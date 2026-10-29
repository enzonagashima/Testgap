"""Dataset export service for curation and AI model training."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import jsonschema

from testgap.config import EXPORT_DIR, SCHEMAS_DIR
from testgap.repositories.examples import ExampleRepository
from testgap.schemas import (
    CanonicalExample, CanonicalProject, CanonicalInput,
    CanonicalOutput, CanonicalGap, CanonicalMetadata, ExampleInDB
)
from testgap.enums import ReviewStatus, GapStatus
from testgap.utils.jsonl import write_jsonl


class ExportService:
    """Handles dataset filtering, canonical conversion, and split partitioning."""

    def __init__(self, example_repo: Optional[ExampleRepository] = None):
        self.example_repo = example_repo or ExampleRepository()
        self.schema_path = SCHEMAS_DIR / "dataset-v1.schema.json"
        self._schema_cache = None

    def _get_json_schema(self) -> Dict[str, Any]:
        if self._schema_cache is None:
            if not self.schema_path.exists():
                raise FileNotFoundError(f"JSON Schema não encontrado em {self.schema_path}")
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self._schema_cache = json.load(f)
        return self._schema_cache

    def to_canonical(self, example: ExampleInDB, exclude_unconfirmed_gaps: bool = True) -> CanonicalExample:
        """Convert database ExampleInDB model to canonical JSONL schema record."""
        # Filter gaps
        if exclude_unconfirmed_gaps:
            active_gaps = [g for g in example.gaps if g.status == GapStatus.CONFIRMED]
        else:
            active_gaps = example.gaps

        canonical_gaps = [
            CanonicalGap(
                category=g.category_code or "functional_coverage",
                title=g.title,
                description=g.description,
                requirement_reference=g.requirement_reference,
                evidence=g.evidence,
                severity=g.severity,
                confidence=g.confidence,
                suggested_test=g.suggested_test,
                expected_result=g.expected_result
            )
            for g in active_gaps
        ]

        has_gaps = len(canonical_gaps) > 0

        return CanonicalExample(
            schema_version="1.0.0",
            example_id=example.public_id,
            project=CanonicalProject(
                name=example.project_name,
                language=example.source_language,
                framework=example.test_framework
            ),
            input=CanonicalInput(
                requirements=example.requirements_text,
                source_code=example.source_code or "",
                test_suite=example.test_suite_text,
                test_format=example.test_format,
                analysis_scope=example.analysis_scope
            ),
            expected_output=CanonicalOutput(
                has_gaps=has_gaps,
                gaps=canonical_gaps
            ),
            metadata=CanonicalMetadata(
                source_type=example.source_type,
                review_status=example.review_status,
                split_group=example.split_group,
                labels_verified=(example.review_status == ReviewStatus.APPROVED)
            )
        )

    def validate_canonical_record(self, record_dict: Dict[str, Any]) -> None:
        """Validate single record against dataset-v1.schema.json using jsonschema."""
        schema = self._get_json_schema()
        jsonschema.validate(instance=record_dict, schema=schema)

    def export_dataset(
        self,
        output_file: Path | str,
        only_approved: bool = True,
        split_group: Optional[str] = None
    ) -> Tuple[int, Path]:
        """Export dataset to a single JSONL file."""
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        examples, _ = self.example_repo.list_examples(
            review_status="approved" if only_approved else None,
            limit=100000,
            offset=0
        )

        if split_group:
            examples = [e for e in examples if e.split_group == split_group]

        records = []
        for ex in examples:
            canonical = self.to_canonical(ex, exclude_unconfirmed_gaps=True)
            record_dict = canonical.model_dump()
            self.validate_canonical_record(record_dict)
            records.append(record_dict)

        count = write_jsonl(out_path, records)
        return count, out_path

    def export_for_training(
        self,
        output_dir: Optional[Path | str] = None,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        only_approved: bool = True
    ) -> Dict[str, Any]:
        """Export dataset partitioned into train, val, test sets strictly grouped by split_group.
        
        Guarantees that no project or split_group leaks across training and testing splits.
        """
        out_dir = Path(output_dir or EXPORT_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)

        examples, _ = self.example_repo.list_examples(
            review_status="approved" if only_approved else None,
            limit=100000,
            offset=0
        )

        # Group examples by split_group
        groups: Dict[str, List[ExampleInDB]] = {}
        for ex in examples:
            groups.setdefault(ex.split_group, []).append(ex)

        sorted_groups = sorted(groups.keys())
        total_groups = len(sorted_groups)

        # Distribute split_groups
        train_count = max(1, int(total_groups * train_ratio)) if total_groups > 1 else total_groups
        val_count = max(1, int(total_groups * val_ratio)) if total_groups > 2 else 0

        train_groups = set(sorted_groups[:train_count])
        val_groups = set(sorted_groups[train_count:train_count + val_count])
        test_groups = set(sorted_groups[train_count + val_count:])

        # Fallback if only 1 group exists
        if not test_groups and total_groups > 1:
            test_groups = val_groups

        splits = {"train": [], "val": [], "test": []}

        for group_name, ex_list in groups.items():
            if group_name in train_groups:
                target = "train"
            elif group_name in val_groups:
                target = "val"
            else:
                target = "test"

            for ex in ex_list:
                canonical = self.to_canonical(ex, exclude_unconfirmed_gaps=True)
                rec = canonical.model_dump()
                self.validate_canonical_record(rec)
                splits[target].append(rec)

        results = {}
        for split_name, recs in splits.items():
            file_path = out_dir / f"{split_name}.jsonl"
            write_jsonl(file_path, recs)
            results[split_name] = {
                "file": str(file_path),
                "count": len(recs),
                "groups": list(train_groups if split_name == "train" else (val_groups if split_name == "val" else test_groups))
            }

        return results
