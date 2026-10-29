"""Example business logic and coordination service."""
from typing import List, Optional, Tuple
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.gaps import GapRepository
from testgap.schemas import ExampleInDB, ExampleCreate, ExampleUpdate, GapCreate
from testgap.utils.hashing import compute_content_hash
from testgap.enums import ReviewStatus


class ExampleService:
    """Coordinates example operations, uniqueness, cloning, and hashing."""

    def __init__(
        self,
        example_repo: Optional[ExampleRepository] = None,
        gap_repo: Optional[GapRepository] = None
    ):
        self.example_repo = example_repo or ExampleRepository()
        self.gap_repo = gap_repo or GapRepository()

    def get_example(self, example_id: int) -> Optional[ExampleInDB]:
        return self.example_repo.get_by_id(example_id, include_gaps=True)

    def get_by_public_id(self, public_id: str) -> Optional[ExampleInDB]:
        return self.example_repo.get_by_public_id(public_id, include_gaps=True)

    def create_example(self, example_data: ExampleCreate) -> ExampleInDB:
        # Compute content hash
        c_hash = compute_content_hash(
            example_data.requirements_text,
            example_data.source_code,
            example_data.test_suite_text
        )

        # Check for existing duplicate
        existing = self.example_repo.get_by_content_hash(c_hash)
        if existing:
            raise ValueError(
                f"Conteúdo idêntico já cadastrado no exemplo {existing.public_id} ('{existing.title}')."
            )

        return self.example_repo.create(example_data, content_hash=c_hash)

    def update_example(self, example_id: int, update_data: ExampleUpdate) -> Optional[ExampleInDB]:
        current = self.example_repo.get_by_id(example_id, include_gaps=False)
        if not current:
            raise ValueError(f"Exemplo com ID {example_id} não encontrado.")

        # Determine if content changed to rehash
        req = update_data.requirements_text if update_data.requirements_text is not None else current.requirements_text
        src = update_data.source_code if update_data.source_code is not None else current.source_code
        test = update_data.test_suite_text if update_data.test_suite_text is not None else current.test_suite_text

        new_hash = compute_content_hash(req, src, test)
        if new_hash != current.content_hash:
            # Check if another record has this exact hash
            dup = self.example_repo.get_by_content_hash(new_hash)
            if dup and dup.id != example_id:
                raise ValueError(f"Edição colide com o conteúdo idêntico do exemplo {dup.public_id}.")

        return self.example_repo.update(example_id, update_data, new_content_hash=new_hash)

    def duplicate_as_draft(self, example_id: int) -> ExampleInDB:
        """Clones an example as a fresh pending draft with a new public_id."""
        original = self.example_repo.get_by_id(example_id, include_gaps=True)
        if not original:
            raise ValueError(f"Exemplo com ID {example_id} não encontrado.")

        # Prepare new example payload
        clone_create = ExampleCreate(
            title=f"{original.title} (Cópia)",
            project_name=original.project_name,
            description=original.description,
            requirements_text=original.requirements_text,
            source_code=original.source_code,
            source_language=original.source_language,
            test_framework=original.test_framework,
            test_suite_text=original.test_suite_text,
            test_format=original.test_format,
            expected_behavior=original.expected_behavior,
            analysis_scope=original.analysis_scope,
            split_group=original.split_group,
            source_type=original.source_type,
            source_reference=f"Clonado a partir de {original.public_id}",
            initial_gaps=[
                GapCreate(
                    category_id=g.category_id,
                    title=g.title,
                    description=g.description,
                    requirement_reference=g.requirement_reference,
                    evidence=g.evidence,
                    severity=g.severity,
                    confidence=g.confidence,
                    suggested_test=g.suggested_test,
                    expected_result=g.expected_result,
                    status=g.status,
                    review_note=f"Clonado de {original.public_id}"
                )
                for g in original.gaps
            ]
        )

        # Allow duplication by suffixing a slight tag if needed or unique content
        c_hash = compute_content_hash(
            clone_create.requirements_text + f" (clone {original.public_id})",
            clone_create.source_code,
            clone_create.test_suite_text
        )
        return self.example_repo.create(clone_create, content_hash=c_hash)

    def delete_example(self, example_id: int) -> bool:
        return self.example_repo.delete(example_id)

    def list_examples(self, **kwargs) -> Tuple[List[ExampleInDB], int]:
        return self.example_repo.list_examples(**kwargs)

    def get_all_projects(self) -> List[str]:
        return self.example_repo.get_all_projects()
