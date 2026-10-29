"""Tests for SQLite database configuration, pragmas, transactions, and migrations."""
import sqlite3
import pytest


def test_migrations_applied_and_categories_seeded(db_manager):
    """Test that schema migrations run and seed default categories."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        assert count == 8

        cursor.execute("SELECT version FROM schema_migrations WHERE version = '001_initial'")
        row = cursor.fetchone()
        assert row is not None


def test_foreign_keys_enforced(db_manager):
    """Test that SQLite foreign key constraints are strictly enforced."""
    with pytest.raises(sqlite3.IntegrityError):
        with db_manager.transaction() as conn:
            cursor = conn.cursor()
            # Attempt to insert a gap referencing non-existent example_id 9999
            cursor.execute(
                """
                INSERT INTO gaps (example_id, gap_code, category_id, title, description,
                                  suggested_test, expected_result, created_at, updated_at)
                VALUES (9999, 'GAP-001', 1, 'Fake Gap', 'Desc', 'Test', 'Result', 'now', 'now')
                """
            )


def test_transaction_rollback(db_manager):
    """Test that an exception within transaction() completely rolls back all modifications."""
    with pytest.raises(ValueError):
        with db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO categories (code, name, description, is_active, created_at)
                VALUES ('temp_cat', 'Temp', 'Description', 1, 'now')
                """
            )
            # Intentionally raise an error to trigger rollback
            raise ValueError("Forced error for rollback testing")

    # Verify rollback
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE code = 'temp_cat'")
        assert cursor.fetchone() is None


def test_idempotent_migrations(db_manager):
    """Test that re-running migrations does not fail or duplicate data."""
    # Run again
    db_manager.run_migrations()
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        assert cursor.fetchone()[0] == 8
