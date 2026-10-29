"""Tests for ExportService and training data partitioning."""
import json
import pytest
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.gaps import GapRepository
from testgap.services.example_service import ExampleService
from testgap.services.gap_service import GapService
from testgap.services.review_service import ReviewService
from testgap.services.export_service import ExportService
from testgap.schemas import ExampleCreate, GapCreate
from testgap.enums import ReviewStatus, GapStatus


def test_export_only_approved_and_excludes_rejected_gaps(db_manager, sample_example_payload, sample_gap_payload, tmp_path):
    """Test that export filters out unapproved examples and rejected gaps."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    gap_service = GapService(GapRepository(db_manager))
    review_service = ReviewService(ExampleRepository(db_manager))
    export_service = ExportService(ExampleRepository(db_manager))

    # Example 1: Approved, with 1 confirmed gap and 1 rejected gap
    ex1 = ex_service.create_example(ExampleCreate.model_validate(sample_example_payload))
    gap1 = gap_service.add_gap_to_example(ex1.id, GapCreate.model_validate(sample_gap_payload))
    
    rejected_gap_payload = sample_gap_payload.copy()
    rejected_gap_payload["title"] = "Lacuna Rejeitada"
    rejected_gap_payload["status"] = GapStatus.REJECTED
    gap2 = gap_service.add_gap_to_example(ex1.id, GapCreate.model_validate(rejected_gap_payload))

    review_service.update_status(ex1.id, ReviewStatus.APPROVED)

    # Example 2: Pending (should be excluded when only_approved=True)
    payload2 = sample_example_payload.copy()
    payload2["title"] = "Exemplo Pendente Não Aprovado"
    payload2["requirements_text"] = "Requisito diferente pendente de revisão."
    ex2 = ex_service.create_example(ExampleCreate.model_validate(payload2))

    # Export
    out_file = tmp_path / "export_approved.jsonl"
    count, _ = export_service.export_dataset(out_file, only_approved=True)

    assert count == 1
    with open(out_file, "r", encoding="utf-8") as f:
        line = json.loads(f.readline())
        assert line["example_id"] == ex1.public_id
        # Must only contain 1 confirmed gap, rejected gap omitted!
        assert len(line["expected_output"]["gaps"]) == 1
        assert line["expected_output"]["gaps"][0]["title"] == gap1.title


def test_export_split_group_partitioning(db_manager, sample_example_payload, tmp_path):
    """Test that partitioning isolates split_groups across train, val, and test without leakage."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    review_service = ReviewService(ExampleRepository(db_manager))
    export_service = ExportService(ExampleRepository(db_manager))

    # Create 3 projects with distinct split_groups
    groups = ["group_alpha", "group_beta", "group_gamma"]
    for idx, grp in enumerate(groups, 1):
        p = sample_example_payload.copy()
        p["title"] = f"Projeto {grp}"
        p["requirements_text"] = f"Requisitos específicos para o grupo {grp} com hash único."
        p["split_group"] = grp
        ex = ex_service.create_example(ExampleCreate.model_validate(p))
        review_service.update_status(ex.id, ReviewStatus.APPROVED)

    results = export_service.export_for_training(output_dir=tmp_path)
    train_groups = set(results["train"]["groups"])
    val_groups = set(results["val"]["groups"])

    # Overlap between train and val must be empty!
    assert len(train_groups.intersection(val_groups)) == 0
