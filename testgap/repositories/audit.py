"""Audit and review history repository for SQLite."""
from typing import List, Optional
from testgap.database import DatabaseManager, default_db
from testgap.schemas import ReviewHistoryInDB, AuditResultInDB
from testgap.utils.timestamps import utc_now_iso


class AuditRepository:
    """Handles persistence of review audit trials and quality audit reports."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or default_db

    def add_review_entry(
        self,
        example_id: int,
        previous_status: Optional[str],
        new_status: str,
        review_note: str = "",
        changed_by: str = "local_ui",
        conn=None
    ) -> ReviewHistoryInDB:
        now = utc_now_iso()
        sql = """
            INSERT INTO review_history (
                example_id, previous_status, new_status, review_note, changed_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (example_id, previous_status, new_status, review_note, changed_by, now)

        if conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            entry_id = cursor.lastrowid
            cursor.execute("SELECT * FROM review_history WHERE id = ?", (entry_id,))
            return ReviewHistoryInDB.model_validate(dict(cursor.fetchone()))
        else:
            with self.db.transaction() as t_conn:
                cursor = t_conn.cursor()
                cursor.execute(sql, params)
                entry_id = cursor.lastrowid
                cursor.execute("SELECT * FROM review_history WHERE id = ?", (entry_id,))
                return ReviewHistoryInDB.model_validate(dict(cursor.fetchone()))

    def get_history_for_example(self, example_id: int) -> List[ReviewHistoryInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM review_history WHERE example_id = ? ORDER BY id DESC",
                (example_id,)
            )
            return [ReviewHistoryInDB.model_validate(dict(r)) for r in cursor.fetchall()]

    def save_audit_result(
        self,
        audit_type: str,
        total_examined: int,
        total_errors: int,
        total_warnings: int,
        report_json: str,
        rules_version: str = "1.0.0"
    ) -> AuditResultInDB:
        now = utc_now_iso()
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_results (
                    audit_date, audit_type, total_examined, total_errors,
                    total_warnings, report_json, rules_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (now, audit_type, total_examined, total_errors, total_warnings, report_json, rules_version)
            )
            audit_id = cursor.lastrowid
            cursor.execute("SELECT * FROM audit_results WHERE id = ?", (audit_id,))
            return AuditResultInDB.model_validate(dict(cursor.fetchone()))

    def get_latest_audit_result(self) -> Optional[AuditResultInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_results ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return AuditResultInDB.model_validate(dict(row)) if row else None

    def get_audit_history(self, limit: int = 10) -> List[AuditResultInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_results ORDER BY id DESC LIMIT ?", (limit,))
            return [AuditResultInDB.model_validate(dict(r)) for r in cursor.fetchall()]
