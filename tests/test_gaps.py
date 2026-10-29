"""Tests for GapRepository, GapService, and CategoryRepository safeguards."""
import pytest
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.gaps import GapRepository
from testgap.repositories.categories import CategoryRepository
from testgap.services.example_service import ExampleService
from testgap.services.gap_service import GapService
from testgap.services.category_service import CategoryService
from testgap.schemas import ExampleCreate, GapCreate, GapUpdate


def test_create_gap_linked_to_example(db_manager, sample_example_payload, sample_gap_payload):
    """Test creating a gap linked to an example."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    gap_service = GapService(GapRepository(db_manager), CategoryRepository(db_manager))

    ex = ex_service.create_example(ExampleCreate.model_validate(sample_example_payload))
    gap = gap_service.add_gap_to_example(ex.id, GapCreate.model_validate(sample_gap_payload))

    assert gap.example_id == ex.id
    assert gap.gap_code == "GAP-001"
    assert gap.title == sample_gap_payload["title"]
    assert gap.category_name == "Cobertura Funcional"


def test_cascade_delete_gaps(db_manager, sample_example_payload, sample_gap_payload):
    """Test that deleting an example automatically cascades to delete all its gaps."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    gap_service = GapService(GapRepository(db_manager), CategoryRepository(db_manager))

    ex = ex_service.create_example(ExampleCreate.model_validate(sample_example_payload))
    gap = gap_service.add_gap_to_example(ex.id, GapCreate.model_validate(sample_gap_payload))

    # Verify gap exists
    assert gap_service.get_gap(gap.id) is not None

    # Delete example
    ex_service.delete_example(ex.id)

    # Verify gap was cascaded
    assert gap_service.get_gap(gap.id) is None


def test_cannot_delete_category_with_active_gaps(db_manager, sample_example_payload, sample_gap_payload):
    """Test that deleting a category linked to existing gaps is rejected."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    gap_service = GapService(GapRepository(db_manager), CategoryRepository(db_manager))
    cat_service = CategoryService(CategoryRepository(db_manager))

    ex = ex_service.create_example(ExampleCreate.model_validate(sample_example_payload))
    gap_service.add_gap_to_example(ex.id, GapCreate.model_validate(sample_gap_payload))

    # Attempt to delete category 1 ('functional_coverage')
    with pytest.raises(ValueError, match="Não é possível excluir a categoria"):
        cat_service.delete_category(1)


def test_gap_update(db_manager, sample_example_payload, sample_gap_payload):
    """Test updating fields on an existing gap."""
    ex_service = ExampleService(ExampleRepository(db_manager))
    gap_service = GapService(GapRepository(db_manager), CategoryRepository(db_manager))

    ex = ex_service.create_example(ExampleCreate.model_validate(sample_example_payload))
    gap = gap_service.add_gap_to_example(ex.id, GapCreate.model_validate(sample_gap_payload))

    updated = gap_service.update_gap(
        gap.id,
        GapUpdate(title="Título da lacuna alterado", confidence=0.85)
    )
    assert updated.title == "Título da lacuna alterado"
    assert updated.confidence == 0.85
