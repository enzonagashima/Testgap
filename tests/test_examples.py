"""Tests for ExampleRepository and ExampleService."""
import pytest
from testgap.repositories.examples import ExampleRepository
from testgap.services.example_service import ExampleService
from testgap.schemas import ExampleCreate, ExampleUpdate


def test_create_example_generates_public_id(db_manager, sample_example_payload):
    """Test that creating an example automatically generates sequential TG-000001 public_id."""
    service = ExampleService(ExampleRepository(db_manager))
    data = ExampleCreate.model_validate(sample_example_payload)

    ex1 = service.create_example(data)
    assert ex1.public_id == "TG-000001"
    assert ex1.review_status.value == "pending"

    # Second example with different requirements
    payload2 = sample_example_payload.copy()
    payload2["requirements_text"] = "Requisito diferente para evitar duplicata de hash."
    data2 = ExampleCreate.model_validate(payload2)
    ex2 = service.create_example(data2)
    assert ex2.public_id == "TG-000002"


def test_duplicate_content_hash_rejected(db_manager, sample_example_payload):
    """Test that creating an example with identical requirements, code and tests raises ValueError."""
    service = ExampleService(ExampleRepository(db_manager))
    data = ExampleCreate.model_validate(sample_example_payload)
    service.create_example(data)

    # Attempt to insert identical content
    with pytest.raises(ValueError, match="Conteúdo idêntico já cadastrado"):
        service.create_example(data)


def test_update_example_recomputes_hash(db_manager, sample_example_payload):
    """Test that updating content recomputes content_hash correctly."""
    service = ExampleService(ExampleRepository(db_manager))
    data = ExampleCreate.model_validate(sample_example_payload)
    ex = service.create_example(data)
    orig_hash = ex.content_hash

    # Update requirements
    updated = service.update_example(
        ex.id,
        ExampleUpdate(requirements_text="Novos requisitos atualizados")
    )
    assert updated.content_hash != orig_hash
    assert updated.requirements_text == "Novos requisitos atualizados"


def test_duplicate_as_draft(db_manager, sample_example_payload):
    """Test cloning an example as a fresh pending draft with a distinct public_id."""
    service = ExampleService(ExampleRepository(db_manager))
    data = ExampleCreate.model_validate(sample_example_payload)
    original = service.create_example(data)

    clone = service.duplicate_as_draft(original.id)
    assert clone.id != original.id
    assert clone.public_id != original.public_id
    assert clone.public_id == "TG-000002"
    assert clone.review_status.value == "pending"
    assert "Cópia" in clone.title


def test_list_and_search_examples(db_manager, sample_example_payload):
    """Test listing examples with text search and project filtering."""
    service = ExampleService(ExampleRepository(db_manager))
    service.create_example(ExampleCreate.model_validate(sample_example_payload))

    # Search for term
    results, count = service.list_examples(search="Bloqueio")
    assert count == 1
    assert len(results) == 1

    # Search for non-existent term
    results, count = service.list_examples(search="TermoInexistenteXYZ")
    assert count == 0
    assert len(results) == 0
