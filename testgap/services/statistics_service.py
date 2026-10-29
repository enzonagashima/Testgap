"""Statistics and KPI aggregation service."""
from typing import Dict, Any, List
from testgap.database import DatabaseManager, default_db
from testgap.repositories.gaps import GapRepository


class StatisticsService:
    """Calculates dataset statistics and KPIs from SQLite."""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or default_db
        self.gap_repo = GapRepository(self.db)

    def get_summary_metrics(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Examples counts
            cursor.execute("SELECT COUNT(*) FROM examples")
            total_examples = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM examples WHERE review_status = 'approved'")
            approved_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM examples WHERE review_status = 'pending'")
            pending_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM examples WHERE review_status = 'rejected'")
            rejected_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM examples WHERE review_status = 'needs_revision'")
            needs_revision_count = cursor.fetchone()[0]

            # Examples with/without gaps
            cursor.execute(
                """
                SELECT COUNT(DISTINCT e.id)
                FROM examples e
                JOIN gaps g ON g.example_id = e.id
                WHERE g.status = 'confirmed'
                """
            )
            with_gaps_count = cursor.fetchone()[0]
            without_gaps_count = total_examples - with_gaps_count

            # Total gaps
            cursor.execute("SELECT COUNT(*) FROM gaps")
            total_gaps = cursor.fetchone()[0]

            # Categories stats
            gaps_by_category = self.gap_repo.get_stats_by_category()

            # Severities stats
            gaps_by_severity = self.gap_repo.get_stats_by_severity()

            # Project stats
            cursor.execute(
                """
                SELECT project_name, COUNT(*) as count
                FROM examples
                GROUP BY project_name
                ORDER BY count DESC
                """
            )
            examples_by_project = {r["project_name"]: r["count"] for r in cursor.fetchall()}

            # Split groups
            cursor.execute(
                """
                SELECT split_group, COUNT(*) as count
                FROM examples
                GROUP BY split_group
                ORDER BY count DESC
                """
            )
            examples_by_split_group = {r["split_group"]: r["count"] for r in cursor.fetchall()}

            # Languages
            cursor.execute(
                """
                SELECT source_language, COUNT(*) as count
                FROM examples
                GROUP BY source_language
                ORDER BY count DESC
                """
            )
            examples_by_language = {r["source_language"]: r["count"] for r in cursor.fetchall()}

            # Recent changes
            cursor.execute(
                """
                SELECT id, public_id, title, project_name, review_status, updated_at
                FROM examples
                ORDER BY id DESC
                LIMIT 5
                """
            )
            recent_examples = [dict(r) for r in cursor.fetchall()]

            return {
                "total_examples": total_examples,
                "approved_count": approved_count,
                "pending_count": pending_count,
                "rejected_count": rejected_count,
                "needs_revision_count": needs_revision_count,
                "with_gaps_count": with_gaps_count,
                "without_gaps_count": without_gaps_count,
                "total_gaps": total_gaps,
                "gaps_by_category": gaps_by_category,
                "gaps_by_severity": gaps_by_severity,
                "examples_by_project": examples_by_project,
                "examples_by_split_group": examples_by_split_group,
                "examples_by_language": examples_by_language,
                "recent_examples": recent_examples,
            }
