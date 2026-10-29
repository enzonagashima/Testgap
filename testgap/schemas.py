"""Pydantic v2 schemas and validation models for TestGap."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from testgap.enums import ReviewStatus, Severity, GapStatus, SourceType, AuditIssueSeverity


class CategoryBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=128)
    description: str = Field(..., min_length=5)
    is_active: bool = True

    @field_validator("code", "name", "description")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Field cannot be empty or purely whitespace.")
        return s


class CategoryCreate(CategoryBase):
    pass


class CategoryInDB(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: str


class GapBase(BaseModel):
    category_id: int
    title: str = Field(..., min_length=3, max_length=256)
    description: str = Field(..., min_length=5)
    requirement_reference: str = Field(default="", max_length=128)
    evidence: str = Field(default="")
    severity: Severity = Severity.MEDIUM
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    suggested_test: str = Field(..., min_length=5)
    expected_result: str = Field(..., min_length=3)
    status: GapStatus = GapStatus.CONFIRMED
    review_note: str = Field(default="")

    @field_validator("title", "description", "suggested_test", "expected_result")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Field cannot be empty or purely whitespace.")
        return s


class GapCreate(GapBase):
    gap_code: Optional[str] = None


class GapUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_reference: Optional[str] = None
    evidence: Optional[str] = None
    severity: Optional[Severity] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    suggested_test: Optional[str] = None
    expected_result: Optional[str] = None
    status: Optional[GapStatus] = None
    review_note: Optional[str] = None


class GapInDB(GapBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    example_id: int
    gap_code: str
    created_at: str
    updated_at: str
    category_name: Optional[str] = None
    category_code: Optional[str] = None


class ExampleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=256)
    project_name: str = Field(..., min_length=2, max_length=128)
    description: str = Field(default="")
    requirements_text: str = Field(..., min_length=5)
    source_code: str = Field(default="")
    source_language: str = Field(default="python", max_length=64)
    test_framework: str = Field(default="pytest", max_length=64)
    test_suite_text: str = Field(..., min_length=5)
    test_format: str = Field(default="pytest", max_length=64)
    expected_behavior: str = Field(default="")
    analysis_scope: str = Field(..., min_length=3, max_length=128)
    split_group: str = Field(..., min_length=2, max_length=128)
    source_type: SourceType = SourceType.HUMAN_AUTHORED
    source_reference: str = Field(default="")

    @field_validator("title", "project_name", "requirements_text", "test_suite_text", "analysis_scope", "split_group")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Field cannot be empty or purely whitespace.")
        return s


class ExampleCreate(ExampleBase):
    initial_gaps: List[GapCreate] = Field(default_factory=list)


class ExampleUpdate(BaseModel):
    title: Optional[str] = None
    project_name: Optional[str] = None
    description: Optional[str] = None
    requirements_text: Optional[str] = None
    source_code: Optional[str] = None
    source_language: Optional[str] = None
    test_framework: Optional[str] = None
    test_suite_text: Optional[str] = None
    test_format: Optional[str] = None
    expected_behavior: Optional[str] = None
    analysis_scope: Optional[str] = None
    split_group: Optional[str] = None
    source_type: Optional[SourceType] = None
    source_reference: Optional[str] = None
    review_status: Optional[ReviewStatus] = None


class ExampleInDB(ExampleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    public_id: str
    review_status: ReviewStatus
    dataset_version: str
    content_hash: str
    created_at: str
    updated_at: str
    gaps: List[GapInDB] = Field(default_factory=list)


class ReviewCreate(BaseModel):
    new_status: ReviewStatus
    review_note: str = ""
    changed_by: str = "local_ui"


class ReviewHistoryInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    example_id: int
    previous_status: Optional[str]
    new_status: str
    review_note: str
    changed_by: str
    created_at: str


# Canonical JSONL Schemas (Export / Import Contract)

class CanonicalProject(BaseModel):
    name: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
    framework: str = Field(..., min_length=1)


class CanonicalInput(BaseModel):
    requirements: str = Field(..., min_length=1)
    source_code: str = Field(default="")
    test_suite: str = Field(..., min_length=1)
    test_format: str = Field(..., min_length=1)
    analysis_scope: str = Field(..., min_length=1)


class CanonicalGap(BaseModel):
    category: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    requirement_reference: str = ""
    evidence: str = ""
    severity: Severity
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    suggested_test: str = Field(..., min_length=1)
    expected_result: str = Field(..., min_length=1)


class CanonicalOutput(BaseModel):
    has_gaps: bool
    gaps: List[CanonicalGap] = Field(default_factory=list)


class CanonicalMetadata(BaseModel):
    source_type: SourceType
    review_status: ReviewStatus
    split_group: str = Field(..., min_length=1)
    labels_verified: bool = True


class CanonicalExample(BaseModel):
    schema_version: str = "1.0.0"
    example_id: str = Field(..., pattern=r"^TG-\d{6}$")
    project: CanonicalProject
    input: CanonicalInput
    expected_output: CanonicalOutput
    metadata: CanonicalMetadata


# Audit Schemas

class AuditIssue(BaseModel):
    rule_id: str
    severity: AuditIssueSeverity
    example_id: Optional[str] = None
    gap_id: Optional[str] = None
    message: str
    details: Optional[str] = None


class QualityReport(BaseModel):
    audit_date: str
    audit_type: str
    total_examined: int
    total_errors: int
    total_warnings: int
    total_infos: int
    issues: List[AuditIssue] = Field(default_factory=list)
    rules_version: str = "1.0.0"


class AuditResultInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    audit_date: str
    audit_type: str
    total_examined: int
    total_errors: int
    total_warnings: int
    report_json: str
    rules_version: str
