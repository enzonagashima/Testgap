"""Category business logic and validation service."""
from typing import List, Optional
from testgap.repositories.categories import CategoryRepository
from testgap.schemas import CategoryInDB, CategoryCreate


class CategoryService:
    """Provides high-level category operations and integrity checks."""

    def __init__(self, repo: Optional[CategoryRepository] = None):
        self.repo = repo or CategoryRepository()

    def list_categories(self, include_inactive: bool = False) -> List[CategoryInDB]:
        return self.repo.get_all(include_inactive=include_inactive)

    def get_category(self, category_id: int) -> Optional[CategoryInDB]:
        return self.repo.get_by_id(category_id)

    def get_category_by_code(self, code: str) -> Optional[CategoryInDB]:
        return self.repo.get_by_code(code)

    def create_category(self, category: CategoryCreate) -> CategoryInDB:
        existing = self.repo.get_by_code(category.code)
        if existing:
            raise ValueError(f"Já existe uma categoria cadastrada com o código '{category.code}'.")
        return self.repo.create(category)

    def toggle_category(self, category_id: int, is_active: bool) -> bool:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Categoria com ID {category_id} não encontrada.")
        return self.repo.toggle_active(category_id, is_active)

    def delete_category(self, category_id: int) -> bool:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Categoria com ID {category_id} não encontrada.")
        return self.repo.delete(category_id)
