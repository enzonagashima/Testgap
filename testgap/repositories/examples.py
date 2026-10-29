"""Example repository for managing examples in SQLite."""
from typing import List, Optional, Tuple, Dict, Any
from testgap.database import DatabaseManager, default_db
from testgap.schemas import ExampleInDB, ExampleCreate, ExampleUpdate
from testgap.repositories.gaps import GapRepository
from testgap.utils.timestamps import utc_now_iso


class ExampleRepository:
    """Handles persistence and complex filtering for examples."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or default_db
        self.gap_repo = GapRepository(self.db)

    def get_next_public_id(self) -> str:
        """Generate next sequential public_id like TG-000001."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT public_id FROM examples ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if not row or not row["public_id"]:
                return "TG-000001"
            last_id = row["public_id"]
            try:
                num = int(last_id.replace("TG-", ""))
                return f"TG-{num + 1:06d}"
            except ValueError:
                return "TG-000001"

    def get_by_id(self, example_id: int, include_gaps: bool = True) -> Optional[ExampleInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM examples WHERE id = ?", (example_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            if include_gaps:
                data["gaps"] = self.gap_repo.get_by_example_id(example_id)
            return ExampleInDB.model_validate(data)

    def get_by_public_id(self, public_id: str, include_gaps: bool = True) -> Optional[ExampleInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM examples WHERE public_id = ?", (public_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            if include_gaps:
                data["gaps"] = self.gap_repo.get_by_example_id(data["id"])
            return ExampleInDB.model_validate(data)

    def get_by_content_hash(self, content_hash: str) -> Optional[ExampleInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM examples WHERE content_hash = ? LIMIT 1", (content_hash,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["gaps"] = self.gap_repo.get_by_example_id(data["id"])
            return ExampleInDB.model_validate(data)

    def create(self, example: ExampleCreate, content_hash: str, public_id: Optional[str] = None) -> ExampleInDB:
        now = utc_now_iso()
        pid = public_id or self.get_next_public_id()

        sql = """
            INSERT INTO examples (
                public_id, title, project_name, description, requirements_text,
                source_code, source_language, test_framework, test_suite_text,
                test_format, expected_behavior, analysis_scope, review_status,
                split_group, source_type, source_reference, dataset_version,
                content_hash, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            pid, example.title, example.project_name, example.description,
            example.requirements_text, example.source_code, example.source_language,
            example.test_framework, example.test_suite_text, example.test_format,
            example.expected_behavior, example.analysis_scope, "pending",
            example.split_group, example.source_type.value, example.source_reference,
            "1.0.0", content_hash, now, now
        )

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            example_id = cursor.lastrowid

            # Insert initial gaps if provided
            for idx, gap in enumerate(example.initial_gaps, 1):
                gap_code = f"GAP-{idx:03d}"
                self.gap_repo.create(example_id, gap_code, gap, conn=conn)

        return self.get_by_id(example_id, include_gaps=True)

    def update(self, example_id: int, update_data: ExampleUpdate, new_content_hash: Optional[str] = None) -> Optional[ExampleInDB]:
        fields = []
        params = []
        for key, val in update_data.model_dump(exclude_unset=True).items():
            if val is not None:
                fields.append(f"{key} = ?")
                params.append(val.value if hasattr(val, "value") else val)

        if new_content_hash:
            fields.append("content_hash = ?")
            params.append(new_content_hash)

        if not fields:
            return self.get_by_id(example_id)

        now = utc_now_iso()
        fields.append("updated_at = ?")
        params.append(now)
        params.append(example_id)

        sql = f"UPDATE examples SET {', '.join(fields)} WHERE id = ?"
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if cursor.rowcount == 0:
                return None
        return self.get_by_id(example_id)

    def delete(self, example_id: int) -> bool:
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM examples WHERE id = ?", (example_id,))
            return cursor.rowcount > 0

    def list_examples(
        self,
        search: Optional[str] = None,
        project: Optional[str] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        review_status: Optional[str] = None,
        source_type: Optional[str] = None,
        has_gaps: Optional[bool] = None,
        category_id: Optional[int] = None,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[ExampleInDB], int]:
        """List examples with pagination and multi-field filtering."""
        where_clauses = []
        params: List[Any] = []

        if search and search.strip():
            term = f"%{search.strip()}%"
            where_clauses.append("(e.title LIKE ? OR e.public_id LIKE ? OR e.project_name LIKE ? OR e.requirements_text LIKE ?)")
            params.extend([term, term, term, term])

        if project:
            where_clauses.append("e.project_name = ?")
            params.append(project)

        if language:
            where_clauses.append("e.source_language = ?")
            params.append(language)

        if framework:
            where_clauses.append("e.test_framework = ?")
            params.append(framework)

        if review_status:
            where_clauses.append("e.review_status = ?")
            params.append(review_status)

        if source_type:
            where_clauses.append("e.source_type = ?")
            params.append(source_type)

        if has_gaps is True:
            where_clauses.append("EXISTS (SELECT 1 FROM gaps g WHERE g.example_id = e.id AND g.status = 'confirmed')")
        elif has_gaps is False:
            where_clauses.append("NOT EXISTS (SELECT 1 FROM gaps g WHERE g.example_id = e.id AND g.status = 'confirmed')")

        if category_id:
            where_clauses.append("EXISTS (SELECT 1 FROM gaps g WHERE g.example_id = e.id AND g.category_id = ?)")
            params.append(category_id)

        if severity:
            where_clauses.append("EXISTS (SELECT 1 FROM gaps g WHERE g.example_id = e.id AND g.severity = ?)")
            params.append(severity)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = f"SELECT COUNT(DISTINCT e.id) FROM examples e {where_sql}"
        select_sql = f"""
            SELECT e.*, COUNT(g.id) as gap_count
            FROM examples e
            LEFT JOIN gaps g ON g.example_id = e.id
            {where_sql}
            GROUP BY e.id
            ORDER BY e.id DESC
            LIMIT ? OFFSET ?
        """

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]

            cursor.execute(select_sql, params + [limit, offset])
            rows = cursor.fetchall()
            examples = []
            for row in rows:
                data = dict(row)
                data["gaps"] = self.gap_repo.get_by_example_id(data["id"])
                examples.append(ExampleInDB.model_validate(data))

            return examples, total_count

    def get_all_projects(self) -> List[str]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT project_name FROM examples ORDER BY project_name ASC")
            return [r[0] for r in cursor.fetchall()]
