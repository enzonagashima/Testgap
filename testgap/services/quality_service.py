"""Dataset quality audit service implementing 2-layer validation heuristics."""
import json
from typing import List, Dict, Any, Optional
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.categories import CategoryRepository
from testgap.repositories.audit import AuditRepository
from testgap.schemas import AuditIssue, QualityReport, AuditResultInDB, ExampleInDB
from testgap.enums import AuditIssueSeverity, ReviewStatus, GapStatus
from testgap.utils.timestamps import utc_now_iso


class QualityService:
    """Executes automated quality audits and semantic rule validations."""

    def __init__(
        self,
        example_repo: Optional[ExampleRepository] = None,
        cat_repo: Optional[CategoryRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        self.example_repo = example_repo or ExampleRepository()
        self.cat_repo = cat_repo or CategoryRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def run_full_audit(self) -> QualityReport:
        """Execute all quality rules on all registered examples and persist report."""
        examples, _ = self.example_repo.list_examples(limit=100000, offset=0)
        categories = {c.id: c for c in self.cat_repo.get_all(include_inactive=True)}

        issues: List[AuditIssue] = []

        seen_hashes: Dict[str, str] = {}

        for ex in examples:
            # 1. Exact Duplicate Hash Rule
            if ex.content_hash in seen_hashes:
                issues.append(
                    AuditIssue(
                        rule_id="RULE_EXACT_DUPLICATE_HASH",
                        severity=AuditIssueSeverity.ERROR,
                        example_id=ex.public_id,
                        message=f"Conteúdo idêntico ao do exemplo {seen_hashes[ex.content_hash]}.",
                        details="Requisitos, código-fonte e suíte de testes coincidem exatamente."
                    )
                )
            else:
                seen_hashes[ex.content_hash] = ex.public_id

            # 2. Short description warning
            if len(ex.requirements_text.strip()) < 30:
                issues.append(
                    AuditIssue(
                        rule_id="RULE_SHORT_REQUIREMENTS",
                        severity=AuditIssueSeverity.WARNING,
                        example_id=ex.public_id,
                        message="Texto de requisitos muito curto.",
                        details=f"Comprimento atual: {len(ex.requirements_text.strip())} caracteres (mínimo recomendado: 30)."
                    )
                )

            # 3. Missing source code warning
            if not ex.source_code or not ex.source_code.strip():
                issues.append(
                    AuditIssue(
                        rule_id="RULE_MISSING_SOURCE_CODE",
                        severity=AuditIssueSeverity.WARNING,
                        example_id=ex.public_id,
                        message="Código-fonte da aplicação ausente.",
                        details="A análise e curadoria dependem exclusivamente dos requisitos textuais."
                    )
                )

            # 4. Gaps consistency checks
            confirmed_gaps = [g for g in ex.gaps if g.status == GapStatus.CONFIRMED]

            # In approved example, unconfirmed gaps warning
            if ex.review_status == ReviewStatus.APPROVED:
                unconfirmed = [g for g in ex.gaps if g.status != GapStatus.CONFIRMED]
                if unconfirmed:
                    issues.append(
                        AuditIssue(
                            rule_id="RULE_UNCONFIRMED_GAPS_IN_APPROVED",
                            severity=AuditIssueSeverity.WARNING,
                            example_id=ex.public_id,
                            message=f"Exemplo aprovado possui {len(unconfirmed)} lacuna(s) não confirmada(s).",
                            details="Lacunas com status diferente de 'confirmed' não serão exportadas para treinamento."
                        )
                    )

            for g in ex.gaps:
                # 5. Category existence and active status
                cat = categories.get(g.category_id)
                if not cat:
                    issues.append(
                        AuditIssue(
                            rule_id="RULE_INEXISTENT_CATEGORY",
                            severity=AuditIssueSeverity.ERROR,
                            example_id=ex.public_id,
                            gap_id=g.gap_code,
                            message=f"Lacuna aponta para categoria inexistente ID {g.category_id}.",
                            details="Integridade referencial comprometida."
                        )
                    )
                elif not cat.is_active:
                    issues.append(
                        AuditIssue(
                            rule_id="RULE_INACTIVE_CATEGORY",
                            severity=AuditIssueSeverity.WARNING,
                            example_id=ex.public_id,
                            gap_id=g.gap_code,
                            message=f"Lacuna vinculada à categoria inativa '{cat.name}'.",
                            details="Recomenda-se reclassificar ou reativar a categoria."
                        )
                    )

                # 6. Suggested test and expected result
                if not g.suggested_test or len(g.suggested_test.strip()) < 5:
                    issues.append(
                        AuditIssue(
                            rule_id="RULE_MISSING_SUGGESTED_TEST",
                            severity=AuditIssueSeverity.ERROR,
                            example_id=ex.public_id,
                            gap_id=g.gap_code,
                            message="Lacuna confirmada sem teste sugerido claro.",
                            details="O teste sugerido é obrigatório para ensinar o modelo a cobrir a lacuna."
                        )
                    )

                if not g.expected_result or len(g.expected_result.strip()) < 3:
                    issues.append(
                        AuditIssue(
                            rule_id="RULE_MISSING_EXPECTED_RESULT",
                            severity=AuditIssueSeverity.ERROR,
                            example_id=ex.public_id,
                            gap_id=g.gap_code,
                            message="Lacuna sem resultado esperado observável.",
                            details="O modelo necessita de critério de aprovação do teste sugerido."
                        )
                    )

                # 7. Evidence warning
                if not g.evidence or not g.evidence.strip():
                    issues.append(
                        AuditIssue(
                            rule_id="RULE_MISSING_EVIDENCE",
                            severity=AuditIssueSeverity.INFO,
                            example_id=ex.public_id,
                            gap_id=g.gap_code,
                            message="Lacuna sem evidência explícita citada.",
                            details="Evidências facilitam a revisão humana e auditabilidade."
                        )
                    )

        # Aggregate counts
        error_count = sum(1 for i in issues if i.severity == AuditIssueSeverity.ERROR)
        warning_count = sum(1 for i in issues if i.severity == AuditIssueSeverity.WARNING)
        info_count = sum(1 for i in issues if i.severity == AuditIssueSeverity.INFO)

        now = utc_now_iso()
        report = QualityReport(
            audit_date=now,
            audit_type="full",
            total_examined=len(examples),
            total_errors=error_count,
            total_warnings=warning_count,
            total_infos=info_count,
            issues=issues,
            rules_version="1.0.0"
        )

        # Persist in audit_results
        self.audit_repo.save_audit_result(
            audit_type="full",
            total_examined=len(examples),
            total_errors=error_count,
            total_warnings=warning_count,
            report_json=report.model_dump_json(),
            rules_version="1.0.0"
        )

        return report

    def get_latest_report(self) -> Optional[QualityReport]:
        row = self.audit_repo.get_latest_audit_result()
        if not row:
            return None
        return QualityReport.model_validate_json(row.report_json)
