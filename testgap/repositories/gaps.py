"""Gap repository for managing individual test gaps in SQLite."""
from typing import List, Optional, Dict
from testgap.database import DatabaseManager, default_db
from testgap.schemas import GapInDB, GapCreate, GapUpdate
from testgap.utils.timestamps import utc_now_iso


class GapRepository:
    """Handles persistence and queries for test gaps."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or default_db

    def get_by_example_id(self, example_id: int) -> List[GapInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT g.*, c.name as category_name, c.code as category_code
                FROM gaps g
                JOIN categories c ON g.category_id = c.id
                WHERE g.example_id = ?
                ORDER BY g.id ASC
                """,
                (example_id,)
            )
            rows = cursor.fetchall()
            return [GapInDB.model_validate(dict(r)) for r in rows]

    def get_by_id(self, gap_id: int) -> Optional[GapInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT g.*, c.name as category_name, c.code as category_code
                FROM gaps g
                JOIN categories c ON g.category_id = c.id
                WHERE g.id = ?
                """,
                (gap_id,)
            )
            row = cursor.fetchone()
            return GapInDB.model_validate(dict(row)) if row else None

    def create(self, example_id: int, gap_code: str, gap: GapCreate, conn=None) -> GapInDB:
        now = utc_now_iso()
        sql = """
            INSERT INTO gaps (
                example_id, gap_code, category_id, title, description,
                requirement_reference, evidence, severity, confidence,
                suggested_test, expected_result, status, review_note,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            example_id, gap_code, gap.category_id, gap.title, gap.description,
            gap.requirement_reference, gap.evidence, gap.severity.value,
            gap.confidence, gap.suggested_test, gap.expected_result,
            gap.status.value, gap.review_note, now, now
        )

        if conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            gap_id = cursor.lastrowid
            cursor.execute(
                """
                SELECT g.*, c.name as category_name, c.code as category_code
                FROM gaps g
                JOIN categories c ON g.category_id = c.id
                WHERE g.id = ?
                """,
                (gap_id,)
            )
            row = cursor.fetchone()
            return GapInDB.model_validate(dict(row))
        else:
            with self.db.transaction() as t_conn:
                cursor = t_conn.cursor()
                cursor.execute(sql, params)
                gap_id = cursor.lastrowid
                cursor.execute(
                    """
                    SELECT g.*, c.name as category_name, c.code as category_code
                    FROM gaps g
                    JOIN categories c ON g.category_id = c.id
                    WHERE g.id = ?
                    """,
                    (gap_id,)
                )
                row = cursor.fetchone()
                return GapInDB.model_validate(dict(row))

    def update(self, gap_id: int, update_data: GapUpdate) -> Optional[GapInDB]:
        fields = []
        params = []
        for key, val in update_data.model_dump(exclude_unset=True).items():
            if val is not None:
                fields.append(f"{key} = ?")
                params.append(val.value if hasattr(val, "value") else val)

        if not fields:
            return self.get_by_id(gap_id)

        now = utc_now_iso()
        fields.append("updated_at = ?")
        params.append(now)
        params.append(gap_id)

        sql = f"UPDATE gaps SET {', '.join(fields)} WHERE id = ?"
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if cursor.rowcount == 0:
                return None
        return self.get_by_id(gap_id)

    def delete(self, gap_id: int) -> bool:
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gaps WHERE id = ?", (gap_id,))
            return cursor.rowcount > 0

    def get_stats_by_category(self) -> Dict[str, int]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.name, COUNT(g.id) as count
                FROM categories c
                LEFT JOIN gaps g ON g.category_id = c.id
                GROUP BY c.id
                ORDER BY count DESC
                """
            )
            return {row["name"]: row["count"] for row in cursor.fetchall()}

    def get_stats_by_severity(self) -> Dict[str, int]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT severity, COUNT(id) as count
                FROM gaps
                GROUP BY severity
                """
            )
            return {row["severity"]: row["count"] for row in cursor.fetchall()}
