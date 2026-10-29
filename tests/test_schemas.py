"""Tests for Pydantic v2 schemas and validation constraints."""
import pytest
from pydantic import ValidationError
from testgap.schemas import ExampleCreate, GapCreate, CanonicalExample, CanonicalProject, CanonicalInput, CanonicalOutput, CanonicalMetadata, CanonicalGap
from testgap.enums import ReviewStatus, Severity, GapStatus, SourceType


def test_valid_example_schema(sample_example_payload):
    """Test valid ExampleCreate model validation."""
    model = ExampleCreate.model_validate(sample_example_payload)
    assert model.title == sample_example_payload["title"]
    assert model.requirements_text == sample_example_payload["requirements_text"]


def test_empty_or_whitespace_strings_rejected(sample_example_payload):
    """Test that empty or purely whitespace required fields raise ValidationError."""
    payload = sample_example_payload.copy()
    payload["title"] = "   "
    with pytest.raises(ValidationError):
        ExampleCreate.model_validate(payload)

    payload = sample_example_payload.copy()
    payload["requirements_text"] = "\t\n  "
    with pytest.raises(ValidationError):
        ExampleCreate.model_validate(payload)


def test_gap_confidence_and_severity_validation(sample_gap_payload):
    """Test confidence bounds and severity enum validation."""
    model = GapCreate.model_validate(sample_gap_payload)
    assert model.confidence == 1.0
    assert model.severity == Severity.HIGH

    # Out of bounds confidence
    invalid_payload = sample_gap_payload.copy()
    invalid_payload["confidence"] = 1.5
    with pytest.raises(ValidationError):
        GapCreate.model_validate(invalid_payload)

    invalid_payload["confidence"] = -0.1
    with pytest.raises(ValidationError):
        GapCreate.model_validate(invalid_payload)


def test_canonical_example_validation():
    """Test CanonicalExample structure validation matching JSON schema v1.0.0."""
    canonical = CanonicalExample(
        schema_version="1.0.0",
        example_id="TG-000001",
        project=CanonicalProject(name="AuthService", language="python", framework="pytest"),
        input=CanonicalInput(
            requirements="Bloquear após 5 tentativas.",
            source_code="",
            test_suite="def test_ok(): pass",
            test_format="pytest",
            analysis_scope="auth"
        ),
        expected_output=CanonicalOutput(
            has_gaps=True,
            gaps=[
                CanonicalGap(
                    category="functional_coverage",
                    title="Falta teste de bloqueio",
                    description="Não há teste após 5 erros",
                    requirement_reference="REQ-1",
                    evidence="Sem assert",
                    severity=Severity.HIGH,
                    confidence=1.0,
                    suggested_test="Tentar 5 vezes",
                    expected_result="Bloqueio temporário"
                )
            ]
        ),
        metadata=CanonicalMetadata(
            source_type=SourceType.HUMAN_AUTHORED,
            review_status=ReviewStatus.APPROVED,
            split_group="auth_v1",
            labels_verified=True
        )
    )
    assert canonical.example_id == "TG-000001"
    assert canonical.expected_output.has_gaps is True

    # Bad example_id pattern
    with pytest.raises(ValidationError):
        canonical_bad = canonical.model_copy()
        canonical_bad.example_id = "INVALID_ID"
        CanonicalExample.model_validate(canonical_bad.model_dump())
