"""Pytest fixtures for TestGap tests."""
import pytest
from testgap.database import DatabaseManager


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a fresh isolated SQLite database file."""
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
        "source_code": "def authenticate(user, password):\n    pass",
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": "def test_login_ok():\n    assert authenticate('admin', 'correct') is True",
        "test_format": "pytest",
        "expected_behavior": "Bloquear tentativas após o 5º erro consecutivo.",
        "analysis_scope": "fluxo_autenticacao",
        "split_group": "auth_service_v1",
        "source_type": "human_authored",
        "source_reference": "REQ-AUTH-001"
    }


@pytest.fixture
def sample_gap_payload():
    """Returns a valid dictionary payload for creating a gap."""
    return {
        "category_id": 1,
        "title": "Ausência de teste para limite de tentativas",
        "description": "A suíte não testa o bloqueio temporário após 5 tentativas incorretas.",
        "requirement_reference": "REQ-AUTH-001",
        "evidence": "Não há assert testando 5 chamadas seguidas de login inválido.",
        "severity": "high",
        "confidence": 1.0,
        "suggested_test": "Executar authenticate 5 vezes com senha errada e verificar bloqueio.",
        "expected_result": "Sistema deve levantar AuthenticationLockedError.",
        "status": "confirmed"
    }
