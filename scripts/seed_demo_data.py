"""CLI Script: Seed SQLite database with realistic, high-quality test-gap examples."""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.database import default_db
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.categories import CategoryRepository
from testgap.services.example_service import ExampleService
from testgap.services.review_service import ReviewService
from testgap.schemas import ExampleCreate, GapCreate
from testgap.enums import Severity, GapStatus, SourceType, ReviewStatus


def run_seed():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    cat_repo = CategoryRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    cats = {c.code: c.id for c in cat_repo.get_all(include_inactive=True)}

    demo_examples = [
        # Example 1: Authentication & Rate Limiting (Security & Functional Coverage)
        {
            "payload": {
                "title": "Bloqueio Temporário por Tentativas Excessivas de Senha",
                "project_name": "AuthService",
                "description": "Módulo de segurança responsável por autenticação com proteção anti-força bruta.",
                "requirements_text": (
                    "REQ-SEC-001: O sistema deve autenticar usuários com login e senha válidos.\n"
                    "REQ-SEC-002: Após 5 tentativas consecutivas com senha inválida, a conta deve ser "
                    "bloqueada temporariamente por 15 minutos, rejeitando qualquer tentativa subsequente com HTTP 423."
                ),
                "source_code": (
                    "class AuthService:\n"
                    "    def __init__(self, user_repo, max_attempts=5):\n"
                    "        self.user_repo = user_repo\n"
                    "        self.max_attempts = max_attempts\n"
                    "\n"
                    "    def authenticate(self, username, password):\n"
                    "        user = self.user_repo.find_by_username(username)\n"
                    "        if not user or user.is_locked():\n"
                    "            return False, 'Conta temporariamente bloqueada'\n"
                    "        if not user.verify_password(password):\n"
                    "            user.increment_failed_attempts()\n"
                    "            return False, 'Credenciais inválidas'\n"
                    "        user.reset_failed_attempts()\n"
                    "        return True, 'Autenticado com sucesso'\n"
                ),
                "source_language": "python",
                "test_framework": "pytest",
                "test_suite_text": (
                    "import pytest\n"
                    "\n"
                    "def test_authenticate_success(auth_service, valid_user):\n"
                    "    ok, msg = auth_service.authenticate(valid_user.username, 'correct_pass')\n"
                    "    assert ok is True\n"
                    "    assert msg == 'Autenticado com sucesso'\n"
                    "\n"
                    "def test_authenticate_single_invalid_password(auth_service, valid_user):\n"
                    "    ok, msg = auth_service.authenticate(valid_user.username, 'wrong_pass')\n"
                    "    assert ok is False\n"
                    "    assert msg == 'Credenciais inválidas'\n"
                ),
                "test_format": "pytest",
                "expected_behavior": "Bloquear conta após 5 falhas consecutivas.",
                "analysis_scope": "autenticacao_e_seguranca",
                "split_group": "auth_core",
                "source_type": SourceType.HUMAN_AUTHORED,
                "source_reference": "RFC-AUTH-2026",
                "initial_gaps": [
                    GapCreate(
                        category_id=cats.get("security_authorization", 3),
                        title="Ausência de teste para limite de 5 falhas consecutivas e bloqueio",
                        description="A suíte de testes testa apenas 1 tentativa incorreta isolada, mas nunca exercita o acúmulo de 5 tentativas e o consequente bloqueio.",
                        requirement_reference="REQ-SEC-002",
                        evidence="Não há nenhum loop ou sequência de 5 chamadas com senha incorreta nos testes.",
                        severity=Severity.HIGH,
                        confidence=1.0,
                        suggested_test=(
                            "def test_lockout_after_five_failed_attempts(auth_service, valid_user):\n"
                            "    for _ in range(5):\n"
                            "        auth_service.authenticate(valid_user.username, 'wrong_pass')\n"
                            "    ok, msg = auth_service.authenticate(valid_user.username, 'wrong_pass')\n"
                            "    assert ok is False\n"
                            "    assert msg == 'Conta temporariamente bloqueada'\n"
                        ),
                        expected_result="A 6ª tentativa falha com mensagem de bloqueio mesmo com senha correta ou incorreta.",
                        status=GapStatus.CONFIRMED
                    ),
                    GapCreate(
                        category_id=cats.get("boundary_values", 2),
                        title="Falta de teste para a 5ª tentativa exata (limite de borda)",
                        description="Não é verificado se a conta continua acessível na 4ª tentativa e bloqueia exatamente na 5ª.",
                        requirement_reference="REQ-SEC-002",
                        evidence="Ausência de assertions verificando o estado da conta a cada tentativa consecutiva.",
                        severity=Severity.MEDIUM,
                        confidence=0.9,
                        suggested_test=(
                            "def test_boundary_fourth_and_fifth_attempt(auth_service, valid_user):\n"
                            "    for _ in range(4):\n"
                            "        auth_service.authenticate(valid_user.username, 'wrong')\n"
                            "    # 4a tentativa ainda nao bloqueia\n"
                            "    assert not valid_user.is_locked()\n"
                            "    # 5a tentativa aciona o bloqueio\n"
                            "    auth_service.authenticate(valid_user.username, 'wrong')\n"
                            "    assert valid_user.is_locked()\n"
                        ),
                        expected_result="Bloqueio ocorre estritamente na 5ª falha e não antes.",
                        status=GapStatus.CONFIRMED
                    )
                ]
            },
            "status": ReviewStatus.APPROVED
        },

        # Example 2: Financial Calculation & Boundary Values
        {
            "payload": {
                "title": "Cálculo de Desconto Progressivo em Carrinho",
                "project_name": "CheckoutAPI",
                "description": "Calculadora de descontos para pedidos de e-commerce.",
                "requirements_text": (
                    "REQ-DISC-001: Pedidos com valor total a partir de R$ 100,00 até R$ 499,99 recebem 5% de desconto.\n"
                    "REQ-DISC-002: Pedidos a partir de R$ 500,00 recebem 10% de desconto.\n"
                    "REQ-DISC-003: Pedidos com valor negativo ou zero devem levantar InvalidOrderAmountException."
                ),
                "source_code": (
                    "def calculate_discount(total_amount):\n"
                    "    if total_amount <= 0:\n"
                    "        raise ValueError('Invalid order amount')\n"
                    "    if total_amount >= 500.0:\n"
                    "        return total_amount * 0.10\n"
                    "    elif total_amount >= 100.0:\n"
                    "        return total_amount * 0.05\n"
                    "    return 0.0\n"
                ),
                "source_language": "python",
                "test_framework": "pytest",
                "test_suite_text": (
                    "def test_discount_tier_one():\n"
                    "    assert calculate_discount(250.0) == 12.5\n"
                    "\n"
                    "def test_discount_tier_two():\n"
                    "    assert calculate_discount(1000.0) == 100.0\n"
                    "\n"
                    "def test_no_discount():\n"
                    "    assert calculate_discount(50.0) == 0.0\n"
                ),
                "test_format": "pytest",
                "expected_behavior": "Validar bordas em 99.99, 100.00, 499.99, 500.00 e valores <= 0.",
                "analysis_scope": "calculo_descontos",
                "split_group": "checkout_pricing",
                "source_type": SourceType.HUMAN_AUTHORED,
                "source_reference": "DISC-SPEC-V2",
                "initial_gaps": [
                    GapCreate(
                        category_id=cats.get("boundary_values", 2),
                        title="Ausência de testes nos valores de fronteira 99.99 e 100.00",
                        description="A suíte só testa valores centrais (50 e 250), não testando a transição exata em 100.0.",
                        requirement_reference="REQ-DISC-001",
                        evidence="Valores 99.99 e 100.00 não constam nos testes.",
                        severity=Severity.HIGH,
                        confidence=1.0,
                        suggested_test=(
                            "def test_boundary_100():\n"
                            "    assert calculate_discount(99.99) == 0.0\n"
                            "    assert calculate_discount(100.00) == 5.0\n"
                        ),
                        expected_result="99.99 sem desconto; 100.00 com exatamente R$ 5,00 de desconto.",
                        status=GapStatus.CONFIRMED
                    ),
                    GapCreate(
                        category_id=cats.get("functional_coverage", 1),
                        title="Falta de teste para exceção com valores <= 0",
                        description="REQ-DISC-003 exige lançamento de exceção para valores nulos ou negativos, mas não há assert de exceção.",
                        requirement_reference="REQ-DISC-003",
                        evidence="Nenhum pytest.raises encontrado na suíte.",
                        severity=Severity.CRITICAL,
                        confidence=1.0,
                        suggested_test=(
                            "def test_invalid_order_amount_exception():\n"
                            "    with pytest.raises(ValueError):\n"
                            "        calculate_discount(0)\n"
                            "    with pytest.raises(ValueError):\n"
                            "        calculate_discount(-50.0)\n"
                        ),
                        expected_result="Lançamento correto de ValueError para zero e negativos.",
                        status=GapStatus.CONFIRMED
                    )
                ]
            },
            "status": ReviewStatus.APPROVED
        },

        # Example 3: Negative Example without Gaps (Complete Test Coverage)
        {
            "payload": {
                "title": "Conversão de Moeda e Formatação de Casas Decimais",
                "project_name": "CheckoutAPI",
                "description": "Função pura de arredondamento e formatação de valores monetários.",
                "requirements_text": (
                    "REQ-FX-001: Arredondar valores monetários sempre com duas casas decimais pelo método half-to-even.\n"
                    "REQ-FX-002: Rejeitar valores nulos ou NaN com TypeError."
                ),
                "source_code": (
                    "from decimal import Decimal, ROUND_HALF_EVEN\n"
                    "\n"
                    "def format_currency(value):\n"
                    "    if value is None:\n"
                    "        raise TypeError('Value cannot be None')\n"
                    "    d = Decimal(str(value))\n"
                    "    return str(d.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN))\n"
                ),
                "source_language": "python",
                "test_framework": "pytest",
                "test_suite_text": (
                    "import pytest\n"
                    "\n"
                    "def test_format_currency_rounding():\n"
                    "    assert format_currency(10.555) == '10.56'\n"
                    "    assert format_currency(10.554) == '10.55'\n"
                    "    assert format_currency(10.5) == '10.50'\n"
                    "\n"
                    "def test_format_currency_none():\n"
                    "    with pytest.raises(TypeError):\n"
                    "        format_currency(None)\n"
                ),
                "test_format": "pytest",
                "expected_behavior": "Suíte cobre 100% dos requisitos descritos com precisão.",
                "analysis_scope": "formatacao_moeda",
                "split_group": "checkout_pricing",
                "source_type": SourceType.HUMAN_AUTHORED,
                "source_reference": "FX-UNIT-01",
                "initial_gaps": []
            },
            "status": ReviewStatus.APPROVED
        },

        # Example 4: Integration & Database Transaction Rollback
        {
            "payload": {
                "title": "Transferência Bancária entre Contas com Transação Atômica",
                "project_name": "BankingService",
                "description": "Serviço de débito e crédito atômico com garantia ACID.",
                "requirements_text": (
                    "REQ-TX-001: Uma transferência deve debitar a conta de origem e creditar a de destino em uma única transação.\n"
                    "REQ-TX-002: Se a conta de origem tiver saldo insuficiente, abortar sem debitar.\n"
                    "REQ-TX-003: Se ocorrer qualquer falha durante o crédito, a operação de débito deve ser totalmente desfeita (rollback)."
                ),
                "source_code": (
                    "def transfer(db, from_acc, to_acc, amount):\n"
                    "    with db.transaction():\n"
                    "        if from_acc.balance < amount:\n"
                    "            raise InsufficientFundsError()\n"
                    "        from_acc.debit(amount)\n"
                    "        to_acc.credit(amount)\n"
                ),
                "source_language": "python",
                "test_framework": "pytest",
                "test_suite_text": (
                    "def test_transfer_success(db, acc_a, acc_b):\n"
                    "    transfer(db, acc_a, acc_b, 100)\n"
                    "    assert acc_a.balance == 900\n"
                    "    assert acc_b.balance == 600\n"
                    "\n"
                    "def test_transfer_insufficient_funds(db, acc_a, acc_b):\n"
                    "    with pytest.raises(InsufficientFundsError):\n"
                    "        transfer(db, acc_a, acc_b, 5000)\n"
                    "    assert acc_a.balance == 1000\n"
                ),
                "test_format": "pytest",
                "expected_behavior": "Garantir rollback do débito se o crédito falhar.",
                "analysis_scope": "transacoes_bancarias",
                "split_group": "banking_core",
                "source_type": SourceType.HUMAN_AUTHORED,
                "source_reference": "TX-CORE-009",
                "initial_gaps": [
                    GapCreate(
                        category_id=cats.get("integration_state", 4),
                        title="Ausência de teste para rollback do débito em caso de falha no crédito",
                        description="A suíte não simula falha ou exception durante a etapa de creditar a conta destino para verificar se a transação é revertida.",
                        requirement_reference="REQ-TX-003",
                        evidence="Nenhum teste introduz erro simulado ou mock no método credit.",
                        severity=Severity.CRITICAL,
                        confidence=1.0,
                        suggested_test=(
                            "def test_transfer_rollback_on_credit_failure(db, acc_a, acc_b, monkeypatch):\n"
                            "    def fail_credit(amt): raise RuntimeError('DB crash')\n"
                            "    monkeypatch.setattr(acc_b, 'credit', fail_credit)\n"
                            "    with pytest.raises(RuntimeError):\n"
                            "        transfer(db, acc_a, acc_b, 100)\n"
                            "    assert acc_a.balance == 1000  # Saldo deve ser preservado\n"
                        ),
                        expected_result="O saldo da conta de origem permanece inalterado devido ao rollback atômico.",
                        status=GapStatus.CONFIRMED
                    )
                ]
            },
            "status": ReviewStatus.APPROVED
        }
    ]

    for item in demo_examples:
        ex = ex_service.create_example(ExampleCreate.model_validate(item["payload"]))
        rev_service.update_status(ex.id, item["status"], review_note="Seed demonstrativo aprovado.")
        print(f"[+] Criado exemplo {ex.public_id}: '{ex.title}' com status '{item['status'].value}'")


if __name__ == "__main__":
    print("[*] Iniciando geração de dados de demonstração (Seed)...")
    run_seed()
    print("[+] Seed concluído com sucesso!")
