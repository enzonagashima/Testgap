"""Review workflow service for tracking statuses and transitions."""
from typing import List, Optional
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.audit import AuditRepository
from testgap.schemas import ExampleInDB, ReviewHistoryInDB
from testgap.enums import ReviewStatus


class ReviewService:
    """Manages example review state transitions and audit logging."""

    def __init__(
        self,
        example_repo: Optional[ExampleRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        self.example_repo = example_repo or ExampleRepository()
        self.audit_repo = audit_repo or AuditRepository(self.example_repo.db)

    def update_status(
        self,
        example_id: int,
        new_status: ReviewStatus,
        review_note: str = "",
        changed_by: str = "local_ui"
    ) -> ExampleInDB:
        example = self.example_repo.get_by_id(example_id, include_gaps=False)
        if not example:
            raise ValueError(f"Exemplo {example_id} não encontrado.")

        old_status = example.review_status.value

        # Atomic update and audit trail
        with self.example_repo.db.transaction() as conn:
            # Update example table
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE examples SET review_status = ?, updated_at = datetime('now') WHERE id = ?",
                (new_status.value, example_id)
            )

            # Record review history
            self.audit_repo.add_review_entry(
                example_id=example_id,
                previous_status=old_status,
                new_status=new_status.value,
                review_note=review_note,
                changed_by=changed_by,
                conn=conn
            )

        return self.example_repo.get_by_id(example_id, include_gaps=True)

    def get_review_history(self, example_id: int) -> List[ReviewHistoryInDB]:
        return self.audit_repo.get_history_for_example(example_id)
