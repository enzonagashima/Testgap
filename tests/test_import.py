"""Tests for ImportService with JSONL and CSV."""
import json
import pytest
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.categories import CategoryRepository
from testgap.services.import_service import ImportService


def test_import_valid_jsonl(db_manager, tmp_path):
    """Test preview and import of valid JSONL records."""
    ex_repo = ExampleRepository(db_manager)
    cat_repo = CategoryRepository(db_manager)
    service = ImportService(ex_repo, cat_repo)

    test_file = tmp_path / "valid.jsonl"
    record = {
        "schema_version": "1.0.0",
        "example_id": "TG-000001",
        "project": {"name": "PaymentAPI", "language": "python", "framework": "pytest"},
        "input": {
            "requirements": "Cobrança com cartão de crédito internacional deve verificar taxa cambial.",
            "source_code": "def charge(card, amt): pass",
            "test_suite": "def test_charge(): pass",
            "test_format": "pytest",
            "analysis_scope": "cambio"
        },
        "expected_output": {
            "has_gaps": True,
            "gaps": [
                {
                    "category": "functional_coverage",
                    "title": "Falta teste de conversão cambial",
                    "description": "Nenhum teste aplica taxa de conversão",
                    "requirement_reference": "REQ-FX",
                    "evidence": "Nenhum assert cambial",
                    "severity": "high",
                    "suggested_test": "Cobrar em USD e conferir débito em BRL",
                    "expected_result": "Taxa aplicada corretamente"
                }
            ]
        },
        "metadata": {
            "source_type": "human_authored",
            "review_status": "approved",
            "split_group": "payment_v1",
            "labels_verified": True
        }
    }
    test_file.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

    # Preview
    preview = service.preview_jsonl(test_file)
    assert preview["valid_count"] == 1
    assert preview["error_count"] == 0

    # Import
    result = service.import_jsonl(test_file)
    assert result["imported_count"] == 1
    assert result["skipped_count"] == 0

    # Re-import with skip policy
    re_result = service.import_jsonl(test_file, duplicate_policy="skip")
    assert re_result["imported_count"] == 0
    assert re_result["skipped_count"] == 1


def test_import_invalid_jsonl_diagnostics(db_manager, tmp_path):
    """Test that malformed JSONL produces detailed error reports without raising exceptions."""
    service = ImportService(ExampleRepository(db_manager), CategoryRepository(db_manager))
    bad_file = tmp_path / "corrupt.jsonl"
    bad_file.write_text('{"schema_version": "1.0.0", "missing": "fields"}\n{invalid_json\n', encoding="utf-8")

    preview = service.preview_jsonl(bad_file)
    assert preview["valid_count"] == 0
    assert preview["error_count"] == 2
