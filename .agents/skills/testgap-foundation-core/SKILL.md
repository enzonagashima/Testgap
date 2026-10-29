---
name: testgap-foundation-core
description: >-
  Provides architectural guidelines, database configuration, migration runner,
  Pydantic schemas, and repository/service patterns for the TestGap foundation and
  core data layers. Use when implementing or modifying SQLite persistence,
  models, migrations, repositories, and business services.
---

# TestGap Foundation & Core Data Architecture

This skill governs the persistence, schemas, repositories, and business services of **TestGap** (Phases 1 and 2).

---

## 1. Architectural Principles

1. **Strict 4-Layer Boundary**:
   - `UI Pages` (`pages/*.py`) call `Services`.
   - `Services` (`testgap/services/`) execute business validation, coordination, and call `Repositories`.
   - `Repositories` (`testgap/repositories/`) execute parameterized SQLite queries and map rows to domain objects / Pydantic models.
   - `Schemas & Database` (`testgap/schemas.py`, `testgap/database.py`, `testgap/enums.py`) define immutable invariants, enums, and database connections.
   - **No SQL statements in the UI or Service layers.**
2. **SQLite Configuration & Safety**:
   - Always enforce foreign keys: `PRAGMA foreign_keys = ON;`.
   - Use Write-Ahead Logging for concurrency: `PRAGMA journal_mode = WAL;`.
   - Set busy timeout: `PRAGMA busy_timeout = 5000;`.
   - Never hardcode the database in `/tmp`. Default location: `data/testgap.db`.
   - All multi-table mutations must occur within a transaction (`with db.transaction():`).
3. **Idempotent Migrations**:
   - Maintain a `schema_migrations` table tracking applied migration version scripts.
   - Startup must verify if migrations are pending and apply them sequentially without data loss.

---

## 2. Directory Layout for Core

```text
testgap/
├── config.py                 # App settings, paths, DB path, pagination defaults
├── database.py               # SQLite connection manager, pragmas, transactions
├── enums.py                  # ReviewStatus, Severity, GapStatus, SourceType
├── schemas.py                # Pydantic v2 validation models
│
├── repositories/
│   ├── __init__.py
│   ├── categories.py         # Category CRUD & lookup
│   ├── examples.py           # Example CRUD, search, filter, pagination
│   ├── gaps.py               # Gap CRUD tied to examples
│   └── audit.py              # Review history & audit results persistence
│
├── services/
│   ├── __init__.py
│   ├── example_service.py    # Public ID generation, content_hash, validations
│   ├── gap_service.py        # Gap business rules, status checks
│   ├── review_service.py     # State transitions & review audit logging
│   ├── category_service.py   # Category validation & safeguards
│   └── statistics_service.py # Aggregated metrics calculation
│
└── utils/
    ├── hashing.py            # SHA-256 calculation for content_hash
    └── timestamps.py         # UTC ISO 8601 timestamps
```

---

## 3. SQLite DDL Schema Specifications

Refer to [schema_ddl.md](./references/schema_ddl.md) for complete SQL definitions.

### Key Constraints:
- `examples.public_id`: Unique identifier formatted as `TG-000001` (6 digits zero-padded).
- `examples.content_hash`: SHA-256 of `(requirements_text.strip() + '|' + source_code.strip() + '|' + test_suite_text.strip())`. Recalculated on update.
- `gaps.example_id`: Foreign key with `ON DELETE CASCADE`.
- `categories.code`: Unique string code (e.g. `functional_coverage`). Deletion blocked if referenced by any gap; soft-deactivation via `is_active = 0`.
- `review_history`: Records all transitions of `review_status` with `changed_by` (`local_ui`, `cli`, `import`).

---

## 4. Enums and Schema Models

### Enums (`testgap/enums.py`)
- `ReviewStatus`: `pending`, `approved`, `rejected`, `needs_revision`
- `Severity`: `critical`, `high`, `medium`, `low`, `informational`
- `GapStatus`: `proposed`, `confirmed`, `rejected`, `needs_revision`
- `SourceType`: `human_authored`, `ai_generated`, `mutation_generated`, `public_dataset`, `imported`, `synthetic`

### Pydantic Models (`testgap/schemas.py`)
- `ExampleCreate`: Validates required fields (`title`, `project_name`, `requirements_text`, `test_suite_text`, `analysis_scope`). Rejects whitespace-only text.
- `ExampleUpdate`: Optional fields for updates; triggers `content_hash` recomputation if content fields change.
- `GapCreate`: Validates `title`, `description`, `category_id`, `severity`, `suggested_test`, `expected_result`.
- `CanonicalExample`: Represents the JSONL export and exchange structure as specified in Section 6.1 of `specs.md`.

---

## 5. Repository Pattern Implementation Standard

Repositories must:
1. Receive a database connection or transaction context.
2. Use parameterized queries exclusively (`?` placeholders).
3. Return domain dataclasses or Pydantic models (or typed dictionaries) rather than raw SQLite row tuples.
4. Support pagination (`limit`, `offset`) and indexed search filters.

```python
# Example Repository Pattern snippet
class ExampleRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_by_id(self, example_id: int) -> Optional[ExampleInDB]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM examples WHERE id = ?", (example_id,))
            row = cursor.fetchone()
            return ExampleInDB.model_validate(dict(row)) if row else None
```

---

## 6. Service Layer Coordination Standard

Services orchestrate operations across multiple repositories and enforce domain rules:
- **`ExampleService`**:
  - Generates next sequential `public_id` (`TG-000001`, `TG-000002`).
  - Computes `content_hash` using `testgap/utils/hashing.py`.
  - Checks for exact duplicate `content_hash` before saving.
  - Handles duplicate-draft cloning (clearing `public_id` and setting status to `pending`).
- **`ReviewService`**:
  - Validates state transitions (e.g. cannot approve an example with confirmed fatal structural errors).
  - Inserts record into `review_history` atomically within the same transaction.
