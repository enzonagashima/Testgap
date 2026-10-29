"""Data ingestion service for JSONL and CSV datasets."""
import csv
import io
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import ValidationError

from testgap.repositories.examples import ExampleRepository
from testgap.repositories.categories import CategoryRepository
from testgap.schemas import CanonicalExample, ExampleCreate, GapCreate
from testgap.utils.jsonl import read_jsonl
from testgap.utils.hashing import compute_content_hash
from testgap.enums import Severity, GapStatus, SourceType


class ImportService:
    """Manages dataset import preview, validation diagnostics, and safe persistence."""

    def __init__(
        self,
        example_repo: Optional[ExampleRepository] = None,
        cat_repo: Optional[CategoryRepository] = None
    ):
        self.example_repo = example_repo or ExampleRepository()
        self.cat_repo = cat_repo or CategoryRepository(self.example_repo.db)

    def preview_jsonl(self, file_path: Path | str) -> Dict[str, Any]:
        """Scan a JSONL file and return diagnostics without inserting into DB."""
        valid_records = []
        errors = []
        duplicates = 0

        # Load category mapping code -> id
        cats = {c.code: c.id for c in self.cat_repo.get_all(include_inactive=True)}

        for line_num, record in read_jsonl(file_path):
            if "_raw_error" in record:
                errors.append({
                    "line": line_num,
                    "error": f"JSON inválido: {record['_raw_error']}"
                })
                continue

            try:
                canonical = CanonicalExample.model_validate(record)
                c_hash = compute_content_hash(
                    canonical.input.requirements,
                    canonical.input.source_code,
                    canonical.input.test_suite
                )

                # Check if hash already in database
                is_duplicate = self.example_repo.get_by_content_hash(c_hash) is not None
                if is_duplicate:
                    duplicates += 1

                valid_records.append({
                    "line": line_num,
                    "example_id": canonical.example_id,
                    "title": canonical.project.name,
                    "is_duplicate": is_duplicate,
                    "gaps_count": len(canonical.expected_output.gaps)
                })
            except ValidationError as ve:
                errors.append({
                    "line": line_num,
                    "error": f"Erro de validação: {str(ve).splitlines()[0]}"
                })
            except Exception as e:
                errors.append({
                    "line": line_num,
                    "error": f"Erro na linha: {str(e)}"
                })

        return {
            "total_lines": len(valid_records) + len(errors),
            "valid_count": len(valid_records),
            "error_count": len(errors),
            "duplicate_count": duplicates,
            "preview": valid_records[:20],
            "errors": errors[:50]
        }

    def import_jsonl(
        self,
        file_path: Path | str,
        duplicate_policy: str = "skip"  # 'skip' | 'error'
    ) -> Dict[str, Any]:
        """Import validated records from a JSONL file into SQLite."""
        cats = {c.code: c.id for c in self.cat_repo.get_all(include_inactive=True)}
        default_cat_id = cats.get("functional_coverage", 1)

        imported_count = 0
        skipped_count = 0
        errors = []

        for line_num, record in read_jsonl(file_path):
            if "_raw_error" in record:
                errors.append({"line": line_num, "error": f"JSON inválido: {record['_raw_error']}"})
                continue

            try:
                canonical = CanonicalExample.model_validate(record)
                c_hash = compute_content_hash(
                    canonical.input.requirements,
                    canonical.input.source_code,
                    canonical.input.test_suite
                )

                existing = self.example_repo.get_by_content_hash(c_hash)
                if existing:
                    if duplicate_policy == "skip":
                        skipped_count += 1
                        continue
                    elif duplicate_policy == "error":
                        raise ValueError(f"Linha {line_num}: Exemplo duplicado detectado ({existing.public_id}).")

                # Prepare initial gaps
                initial_gaps = []
                for g in canonical.expected_output.gaps:
                    cat_id = cats.get(g.category, default_cat_id)
                    initial_gaps.append(
                        GapCreate(
                            category_id=cat_id,
                            title=g.title,
                            description=g.description,
                            requirement_reference=g.requirement_reference or "",
                            evidence=g.evidence or "",
                            severity=g.severity,
                            confidence=g.confidence if g.confidence is not None else 1.0,
                            suggested_test=g.suggested_test,
                            expected_result=g.expected_result,
                            status=GapStatus.CONFIRMED
                        )
                    )

                example_create = ExampleCreate(
                    title=f"Importado: {canonical.project.name} - {canonical.input.analysis_scope}",
                    project_name=canonical.project.name,
                    description=f"Importado do arquivo {Path(file_path).name}",
                    requirements_text=canonical.input.requirements,
                    source_code=canonical.input.source_code or "",
                    source_language=canonical.project.language,
                    test_framework=canonical.project.framework,
                    test_suite_text=canonical.input.test_suite,
                    test_format=canonical.input.test_format,
                    expected_behavior="",
                    analysis_scope=canonical.input.analysis_scope,
                    split_group=canonical.metadata.split_group,
                    source_type=canonical.metadata.source_type,
                    source_reference=f"Importação {canonical.example_id}",
                    initial_gaps=initial_gaps
                )

                self.example_repo.create(example_create, content_hash=c_hash)
                imported_count += 1

            except Exception as e:
                errors.append({"line": line_num, "error": str(e)})

        return {
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "error_count": len(errors),
            "errors": errors
        }

    def import_csv(
        self,
        file_content_or_path: str | Path,
        duplicate_policy: str = "skip"
    ) -> Dict[str, Any]:
        """Parse and import tabular CSV format."""
        cats = {c.code: c.id for c in self.cat_repo.get_all(include_inactive=True)}
        default_cat_id = cats.get("functional_coverage", 1)

        if isinstance(file_content_or_path, (str, Path)) and Path(file_content_or_path).exists():
            f = open(file_content_or_path, "r", encoding="utf-8")
            reader = csv.DictReader(f)
        else:
            reader = csv.DictReader(io.StringIO(str(file_content_or_path)))

        rows = list(reader)
        # Group by title or project
        groups: Dict[str, List[Dict[str, str]]] = {}
        for row in rows:
            key = row.get("title", "").strip() or row.get("project_name", "Projeto Padrão")
            groups.setdefault(key, []).append(row)

        imported = 0
        skipped = 0
        for title, group_rows in groups.items():
            first = group_rows[0]
            req = first.get("requirements_text", first.get("requirements", "")).strip()
            test = first.get("test_suite_text", first.get("test_suite", "")).strip()
            src = first.get("source_code", "").strip()

            if not req or not test:
                continue

            c_hash = compute_content_hash(req, src, test)
            if self.example_repo.get_by_content_hash(c_hash):
                if duplicate_policy == "skip":
                    skipped += 1
                    continue

            # Build gaps
            gaps = []
            for r in group_rows:
                gap_title = r.get("gap_title", "").strip()
                if gap_title:
                    cat_code = r.get("category", "functional_coverage").strip()
                    gaps.append(
                        GapCreate(
                            category_id=cats.get(cat_code, default_cat_id),
                            title=gap_title,
                            description=r.get("gap_description", "Lacuna sem descrição").strip(),
                            requirement_reference=r.get("requirement_reference", "").strip(),
                            severity=Severity(r.get("severity", "medium").lower()),
                            suggested_test=r.get("suggested_test", "Adicionar caso de teste").strip(),
                            expected_result=r.get("expected_result", "Comportamento esperado validado").strip()
                        )
                    )

            ex = ExampleCreate(
                title=title,
                project_name=first.get("project_name", "Projeto Importado").strip(),
                description=first.get("description", "").strip(),
                requirements_text=req,
                source_code=src,
                source_language=first.get("source_language", "python").strip(),
                test_framework=first.get("test_framework", "pytest").strip(),
                test_suite_text=test,
                test_format=first.get("test_format", "pytest").strip(),
                analysis_scope=first.get("analysis_scope", "geral").strip(),
                split_group=first.get("split_group", "import_csv").strip(),
                source_type=SourceType.IMPORTED,
                initial_gaps=gaps
            )
            self.example_repo.create(ex, content_hash=c_hash)
            imported += 1

        return {"imported_count": imported, "skipped_count": skipped}
