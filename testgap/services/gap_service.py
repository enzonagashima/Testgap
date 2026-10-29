"""Gap business logic and validation service."""
from typing import List, Optional
from testgap.repositories.gaps import GapRepository
from testgap.repositories.categories import CategoryRepository
from testgap.schemas import GapInDB, GapCreate, GapUpdate


class GapService:
    """Provides high-level gap operations, code generation, and validation."""

    def __init__(
        self,
        gap_repo: Optional[GapRepository] = None,
        cat_repo: Optional[CategoryRepository] = None
    ):
        self.gap_repo = gap_repo or GapRepository()
        self.cat_repo = cat_repo or CategoryRepository(self.gap_repo.db)

    def get_gap(self, gap_id: int) -> Optional[GapInDB]:
        return self.gap_repo.get_by_id(gap_id)

    def list_gaps_for_example(self, example_id: int) -> List[GapInDB]:
        return self.gap_repo.get_by_example_id(example_id)

    def add_gap_to_example(self, example_id: int, gap_data: GapCreate) -> GapInDB:
        # Validate category exists and is active
        category = self.cat_repo.get_by_id(gap_data.category_id)
        if not category:
            raise ValueError(f"Categoria {gap_data.category_id} não encontrada.")
        if not category.is_active:
            raise ValueError(f"A categoria '{category.name}' está inativa.")

        # Determine next gap_code
        existing_gaps = self.gap_repo.get_by_example_id(example_id)
        next_num = len(existing_gaps) + 1
        gap_code = gap_data.gap_code or f"GAP-{next_num:03d}"

        return self.gap_repo.create(example_id, gap_code, gap_data)

    def update_gap(self, gap_id: int, update_data: GapUpdate) -> Optional[GapInDB]:
        if update_data.category_id is not None:
            category = self.cat_repo.get_by_id(update_data.category_id)
            if not category:
                raise ValueError(f"Categoria {update_data.category_id} não encontrada.")
            if not category.is_active:
                raise ValueError(f"A categoria '{category.name}' está inativa.")

        return self.gap_repo.update(gap_id, update_data)

    def delete_gap(self, gap_id: int) -> bool:
        return self.gap_repo.delete(gap_id)
