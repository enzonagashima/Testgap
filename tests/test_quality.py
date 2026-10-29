"""Tests for QualityService heuristics and quality audit persistence."""
import pytest
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.categories import CategoryRepository
from testgap.repositories.gaps import GapRepository
from testgap.repositories.audit import AuditRepository
from testgap.services.example_service import ExampleService
from testgap.services.gap_service import GapService
from testgap.services.quality_service import QualityService
from testgap.schemas import ExampleCreate, GapCreate
from testgap.enums import AuditIssueSeverity


def test_quality_audit_detects_short_requirements_and_missing_code(db_manager, sample_example_payload):
    """Test that quality service produces warnings for short requirements and missing source code."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    q_service = QualityService(
        ExampleRepository(db_manager),
        CategoryRepository(db_manager),
        AuditRepository(db_manager)
    )

    payload = sample_example_payload.copy()
    payload["requirements_text"] = "Curto demais."
    payload["source_code"] = ""
    ex_service.create_example(ExampleCreate.model_validate(payload))

    report = q_service.run_full_audit()
    assert report.total_examined == 1
    assert report.total_warnings >= 2

    rule_ids = [issue.rule_id for issue in report.issues]
    assert "RULE_SHORT_REQUIREMENTS" in rule_ids
    assert "RULE_MISSING_SOURCE_CODE" in rule_ids


def test_quality_audit_detects_inactive_category(db_manager, sample_example_payload, sample_gap_payload):
    """Test heuristic that flags gaps referencing deactivated categories."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    gap_service = GapService(GapRepository(db_manager), CategoryRepository(db_manager))
    cat_repo = CategoryRepository(db_manager)
    q_service = QualityService(
        ExampleRepository(db_manager),
        cat_repo,
        AuditRepository(db_manager)
    )

    ex = ex_service.create_example(ExampleCreate.model_validate(sample_example_payload))
    gap = gap_service.add_gap_to_example(ex.id, GapCreate.model_validate(sample_gap_payload))

    # Deactivate category 1
    cat_repo.toggle_active(1, is_active=False)

    report = q_service.run_full_audit()
    rule_ids = [issue.rule_id for issue in report.issues]
    assert "RULE_INACTIVE_CATEGORY" in rule_ids
