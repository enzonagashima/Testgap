# TestGap Canonical JSON Schema Reference

This schema defines the structure of each line in exported `.jsonl` files (`schemas/dataset-v1.schema.json`).

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TestGapDatasetRecordV1",
  "type": "object",
  "required": [
    "schema_version",
    "example_id",
    "project",
    "input",
    "expected_output",
    "metadata"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "enum": ["1.0.0"]
    },
    "example_id": {
      "type": "string",
      "pattern": "^TG-[0-9]{6}$"
    },
    "project": {
      "type": "object",
      "required": ["name", "language", "framework"],
      "properties": {
        "name": { "type": "string", "minLength": 1 },
        "language": { "type": "string", "minLength": 1 },
        "framework": { "type": "string", "minLength": 1 }
      }
    },
    "input": {
      "type": "object",
      "required": ["requirements", "source_code", "test_suite", "test_format", "analysis_scope"],
      "properties": {
        "requirements": { "type": "string", "minLength": 1 },
        "source_code": { "type": "string" },
        "test_suite": { "type": "string", "minLength": 1 },
        "test_format": { "type": "string", "minLength": 1 },
        "analysis_scope": { "type": "string", "minLength": 1 }
      }
    },
    "expected_output": {
      "type": "object",
      "required": ["has_gaps", "gaps"],
      "properties": {
        "has_gaps": { "type": "boolean" },
        "gaps": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "category",
              "title",
              "description",
              "requirement_reference",
              "evidence",
              "severity",
              "suggested_test",
              "expected_result"
            ],
            "properties": {
              "category": { "type": "string", "minLength": 1 },
              "title": { "type": "string", "minLength": 1 },
              "description": { "type": "string", "minLength": 1 },
              "requirement_reference": { "type": "string" },
              "evidence": { "type": "string" },
              "severity": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low", "informational"]
              },
              "confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
              },
              "suggested_test": { "type": "string", "minLength": 1 },
              "expected_result": { "type": "string", "minLength": 1 }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["source_type", "review_status", "split_group", "labels_verified"],
      "properties": {
        "source_type": {
          "type": "string",
          "enum": [
            "human_authored",
            "ai_generated",
            "mutation_generated",
            "public_dataset",
            "imported",
            "synthetic"
          ]
        },
        "review_status": {
          "type": "string",
          "enum": ["pending", "approved", "rejected", "needs_revision"]
        },
        "split_group": { "type": "string", "minLength": 1 },
        "labels_verified": { "type": "boolean" }
      }
    }
  }
}
```
