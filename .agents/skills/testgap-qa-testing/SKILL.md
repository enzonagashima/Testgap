---
name: testgap-qa-testing
description: >-
  Provides procedures, test fixtures, test matrix, seed data generation, and
  verification workflows using pytest on Windows for TestGap. Use when writing,
  running, or debugging automated tests and validating acceptance criteria.
---

# TestGap QA & Automated Testing Procedures

This skill defines the testing architecture, pytest conventions, seed data fixtures, and verification guidelines for **TestGap** (Phase 1 through Phase 5).

---

## 1. Non-Negotiable Testing Rules

1. **Never Invent Test Results**: The agent must never produce mock pytest output or fabricate passing assertions. All reported test results must come from real commands executed in the user's PowerShell environment.
2. **Isolation & In-Memory Fixtures**: Unit and integration tests must run against isolated temporary SQLite databases or `:memory:` databases configured with `PRAGMA foreign_keys = ON;`. Tests must never alter the production `data/testgap.db`.
3. **Reproducibility**: Tests must be deterministic and run in any order without depending on test run sequencing.

---

## 2. Pytest Test Suite Architecture

```text
tests/
├── conftest.py          # Fixtures: temp db, migrated db, sample examples, sample gaps
├── test_database.py     # PRAGMAs, foreign keys, transaction rollback, migrations
├── test_schemas.py      # Pydantic schema validation, enum bounds, invalid payloads
├── test_examples.py     # ExampleRepository & ExampleService CRUD, public_id, hashing
├── test_gaps.py         # GapRepository & GapService, cascading deletes, category FK
├── test_import.py       # JSONL & CSV ingestion, duplicate detection, invalid records
├── test_export.py       # JSONL export, eligibility filter, split_group partition
└── test_quality.py      # QualityService heuristics, consistency rules, audit logging
```

Refer to [test_matrix.md](./references/test_matrix.md) for test case specifications.

---

## 3. Standard Pytest Fixtures (`conftest.py`)

```python
import pytest
import sqlite3
import tempfile
import os
from testgap.database import DatabaseManager

@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a fresh isolated SQLite database path for testing."""
    db_file = tmp_path / "testgap_test.db"
    return str(db_file)

@pytest.fixture
def db_manager(temp_db_path):
    """Provides an initialized DatabaseManager with migrations applied."""
    manager = DatabaseManager(temp_db_path)
    manager.run_migrations()
    return manager

@pytest.fixture
def sample_example_payload():
    """Returns a valid dictionary payload for creating an example."""
    return {
        "title": "Bloqueio de Login por Tentativas Inválidas",
        "project_name": "AuthService",
        "description": "Sistema de controle de acesso",
        "requirements_text": "Após 5 tentativas falhas de login, bloquear usuário por 15 minutos.",
        "source_code": "def authenticate(user, password): ...",
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": "def test_login_ok(): assert authenticate('admin', 'correct') is True",
        "test_format": "pytest",
        "expected_behavior": "Bloquear tentativas após o 5º erro consecutivo.",
        "analysis_scope": "fluxo_autenticacao",
        "split_group": "auth_service_v1",
        "source_type": "human_authored"
    }
```

---

## 4. Execution Commands for Windows PowerShell

Always run tests using the project virtual environment:

```powershell
# 1. Run all tests with verbose output
pytest -v --tb=short

# 2. Run a specific test module
pytest tests/test_database.py -v

# 3. Run with coverage report (if pytest-cov installed)
pytest --cov=testgap tests/

# 4. Run CLI initialization and seed verification
python scripts/init_db.py
python scripts/seed_demo_data.py
python scripts/validate_dataset.py --file data/exports/demo_export.jsonl
```

---

## 5. Seed Demo Data Generator (`scripts/seed_demo_data.py`)

The seed script must populate `data/testgap.db` with realistic, non-trivial records:
- Must cover all 8 categories of the taxonomy.
- Must include both examples with confirmed gaps (`has_gaps = True`) and fully covered examples without gaps (`has_gaps = False`).
- Must include varied programming languages (`python`, `javascript`, `typescript`).
- Must use distinct `split_group` values (`auth_core`, `payment_gateway`, `inventory_api`) to demonstrate split separation.
