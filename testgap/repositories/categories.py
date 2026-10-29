"""Category repository for managing taxonomy categories in SQLite."""
from typing import List, Optional
from testgap.database import DatabaseManager, default_db
from testgap.schemas import CategoryInDB, CategoryCreate
from testgap.utils.timestamps import utc_now_iso


class CategoryRepository:
    """Handles CRUD operations for taxonomy categories."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or default_db

    def get_all(self, include_inactive: bool = False) -> List[CategoryInDB]:
        query = "SELECT * FROM categories"
        if not include_inactive:
            query += " WHERE is_active = 1"
        query += " ORDER BY id ASC"

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [CategoryInDB.model_validate(dict(r)) for r in rows]

    def get_by_id(self, category_id: int) -> Optional[CategoryInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            return CategoryInDB.model_validate(dict(row)) if row else None

    def get_by_code(self, code: str) -> Optional[CategoryInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE code = ?", (code,))
            row = cursor.fetchone()
            return CategoryInDB.model_validate(dict(row)) if row else None

    def create(self, category: CategoryCreate) -> CategoryInDB:
        now = utc_now_iso()
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO categories (code, name, description, is_active, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (category.code, category.name, category.description, 1 if category.is_active else 0, now)
            )
            cat_id = cursor.lastrowid
            cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
            row = cursor.fetchone()
            return CategoryInDB.model_validate(dict(row))

    def toggle_active(self, category_id: int, is_active: bool) -> bool:
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET is_active = ? WHERE id = ?",
                (1 if is_active else 0, category_id)
            )
            return cursor.rowcount > 0

    def count_gaps(self, category_id: int) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM gaps WHERE category_id = ?", (category_id,))
            return cursor.fetchone()[0]

    def delete(self, category_id: int) -> bool:
        gap_count = self.count_gaps(category_id)
        if gap_count > 0:
            raise ValueError(f"Não é possível excluir a categoria pois há {gap_count} lacunas vinculadas.")
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0
