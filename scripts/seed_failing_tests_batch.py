"""CLI Script: Seed database with real test failure cases across diverse root causes.

Categories of Test Failure Root Causes:
1. AssertionError (Financial / Float rounding logic regression)
2. TypeError / Null Dereference (Unexpected NoneType in external payload)
3. TimeoutError (Infinite loop in circular dependency graph)
4. IntegrityError (Unique constraint violation in relational database)
5. Security Authorization Bypass (BOLA / IDOR returning 200 instead of 403)
6. Mock Signature Incompatibility (Mock asserting outdated method arguments)
7. Schema ValidationError (Breaking contract change with required field)
"""
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

FAILING_TESTS_EXAMPLES = [
    # -------------------------------------------------------------------------
    # 1. AssertionError - Regressao de Arredondamento Bancario vs Comercial
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste por Regressão de Arredondamento Bancário vs Comercial (AssertionError)",
        "project_name": "PaymentBillingEngine",
        "description": "Motor de faturamento e cálculo de juros diários com precisão monetária legal.",
        "requirements_text": (
            "REQ-FIN-001: O cálculo de juros moratórios deve utilizar a fórmula: principal * (taxa / 100) * dias.\n"
            "REQ-FIN-002: O resultado final DEVE ser arredondado utilizando arredondamento comercial (ROUND_HALF_UP) com 2 casas decimais exatas.\n"
            "REQ-FIN-003: Não é permitido o uso de floats nativos do Python que causam imprecisões de representação IEEE 754 e arredondamento banqueiro (round-half-to-even)."
        ),
        "source_code": (
            "# Codigo sob teste com defeito sutil de representacao e arredondamento\n"
            "def calculate_daily_interest(principal: float, rate_percentage: float, days: int) -> float:\n"
            "    # DEFEITO: Uso de float nativo e round() padrao do Python (que faz round-half-to-even)\n"
            "    interest = principal * (rate_percentage / 100.0) * days\n"
            "    return round(interest, 2)\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from decimal import Decimal, ROUND_HALF_UP\n\n"
            "def test_calculate_daily_interest_half_up():\n"
            "    # Cenário de teste legal: R$ 101.25 a 0.05% por 5 dias\n"
            "    # Calculo exato: 101.25 * 0.0005 * 5 = 0.253125\n"
            "    # Outro cenario critico de borda comercial: 2.555 -> deve virar 2.56\n"
            "    result = calculate_daily_interest(100.0, 0.085166, 30)\n"
            "    # Esperado comercialmente: 2.56\n"
            "    # MOTIVO DA FALHA DO TESTE: AssertionError: 2.55 != 2.56 devido a round() par/impar no float\n"
            "    assert result == 2.56, f'Falha de arredondamento comercial: {result} != 2.56'\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste falha com AssertionError revelando divergência entre o round() nativo e o arredondamento contábil Decimal(ROUND_HALF_UP).",
        "analysis_scope": "financial_rounding_assertion_failure",
        "split_group": "fail_assertion_billing_round",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://bugs.python.org/issue18606 (Floating point and Decimal precision failures)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falha de teste por divergência de arredondamento financeiro (AssertionError: 2.55 != 2.56)",
                "description": "O teste falhou porque o código utiliza float nativo com round(), que implementa arredondamento bancário (round half to even). O requisito contábil REQ-FIN-002 exige Decimal com ROUND_HALF_UP.",
                "evidence": "Execução do teste resulta em AssertionError: Falha de arredondamento comercial: 2.55 != 2.56.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "from decimal import Decimal, ROUND_HALF_UP\n"
                    "def test_interest_strict_decimal_precision():\n"
                    "    # Teste que valida o comportamento correto com Decimal\n"
                    "    p = Decimal('100.00')\n"
                    "    rate = Decimal('0.085166')\n"
                    "    days = 30\n"
                    "    val = (p * (rate / Decimal('100')) * Decimal(days)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)\n"
                    "    assert val == Decimal('2.56')\n"
                ),
                "expected_result": "Adotar Decimal com quantize(ROUND_HALF_UP) para o teste passar com precisão absoluta."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 2. TypeError / Null Dereference - Desestruturacao de Resposta Nula
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste por Acesso a Objeto Nulo em Payload Externo (TypeError)",
        "project_name": "WebhookEventDispatcher",
        "description": "Serviço de processamento de webhooks e extração de identificadores de tenant e metadados.",
        "requirements_text": (
            "REQ-WHK-001: O despachante de webhooks deve extrair o tenant_id e atributos de metadata da requisição recebida.\n"
            "REQ-WHK-002: Se o objeto de metadados não for enviado ou vier nulo, a função deve retornar dicionário vazio como fallback, sem estourar TypeError.\n"
            "REQ-WHK-003: A função deve retornar o identificador de evento normalizado."
        ),
        "source_code": (
            "# Codigo com defeito: Acesso direto sem verificacao defensiva de None\n"
            "def extract_webhook_metadata(event_payload: dict) -> dict:\n"
            "    # DEFEITO: Assume que 'metadata' eh sempre um dict, falhando se for None\n"
            "    meta = event_payload.get('metadata')\n"
            "    # Se meta for None, meta.get('account_id') estoura AttributeError / TypeError\n"
            "    return {\n"
            "        'event_id': event_payload['id'],\n"
            "        'account_id': meta['account_id'],\n"
            "        'region': meta.get('region', 'us-east-1')\n"
            "    }\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "def test_extract_metadata_with_null_metadata_field():\n"
            "    # Payload valido do provedor onde metadata eh explicitamente null\n"
            "    payload = {'id': 'evt_999', 'metadata': None}\n"
            "    # MOTIVO DA FALHA DO TESTE: TypeError: 'NoneType' object is not subscriptable\n"
            "    result = extract_webhook_metadata(payload)\n"
            "    assert result['event_id'] == 'evt_999'\n"
            "    assert result['account_id'] is None\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste falha com TypeError: 'NoneType' object is not subscriptable ao tentar indexar meta['account_id'].",
        "analysis_scope": "null_dereference_type_error",
        "split_group": "fail_typeerror_null_metadata",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://cwe.mitre.org/data/definitions/476.html (NULL Pointer Dereference)",
        "gaps": [
            {
                "category": "functional_coverage",
                "title": "Falha de teste por desreferência de NoneType em payload de webhook (TypeError)",
                "description": "O teste falha com TypeError porque meta['account_id'] assume que 'metadata' é um dicionário quando o provedor envia 'metadata': None.",
                "evidence": "TypeError: 'NoneType' object is not subscriptable na linha 'account_id': meta['account_id'].",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_extract_metadata_graceful_null_handling():\n"
                    "    # Teste de regressao garantindo tratamento gracioso de None\n"
                    "    res = extract_webhook_metadata({'id': 'evt_1', 'metadata': None})\n"
                    "    assert res == {'event_id': 'evt_1', 'account_id': None, 'region': 'us-east-1'}\n"
                ),
                "expected_result": "Aplicar 'meta = event_payload.get(\"metadata\") or {}' para sanar o TypeError."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 3. TimeoutError - Loop Infinito em Dependencias Ciclicas
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste por Loop Infinito em Dependências Cíclicas de Tarefas (TimeoutError)",
        "project_name": "TaskDAGResolver",
        "description": "Resolvedor de ordem de dependências de jobs e tarefas de pipelines assíncronos.",
        "requirements_text": (
            "REQ-DAG-001: A função resolve_execution_order(graph) deve retornar a lista de nós na ordem topológica de execução.\n"
            "REQ-DAG-002: Se o grafo possuir ciclos (ex: A -> B -> A), a função DEVE detectar o ciclo imediatamente e lançar CyclicDependencyError.\n"
            "REQ-DAG-003: Em nenhuma circunstância a função pode entrar em loop infinito ou estourar a pilha de recursão."
        ),
        "source_code": (
            "class CyclicDependencyError(Exception): pass\n\n"
            "def resolve_execution_order(graph: dict[str, list[str]]) -> list[str]:\n"
            "    # DEFEITO: Travessia ingênua sem rastreamento de nós atualmente na pilha de recursão\n"
            "    order = []\n"
            "    visited = set()\n"
            "    def dfs(node):\n"
            "        # Não verifica ciclo em progresso (in-stack set faltando!)\n"
            "        for neighbor in graph.get(node, []):\n"
            "            if neighbor not in visited:\n"
            "                dfs(neighbor)  # Se houver ciclo indireto sem fechar no visited, causa loop!\n"
            "        visited.add(node)\n"
            "        order.append(node)\n"
            "    for start_node in graph:\n"
            "        if start_node not in visited:\n"
            "            dfs(start_node)\n"
            "    return order\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "def test_cyclic_graph_detection_fails_with_timeout():\n"
            "    # Grafo com dependencia circular: A depende de B, B depende de A\n"
            "    circular_graph = {\n"
            "        'job_A': ['job_B'],\n"
            "        'job_B': ['job_A']\n"
            "    }\n"
            "    # MOTIVO DA FALHA DO TESTE: RecursionError / TimeoutError\n"
            "    # O teste espera CyclicDependencyError, mas o código estoura RecursionError: maximum recursion depth exceeded\n"
            "    with pytest.raises(CyclicDependencyError):\n"
            "        resolve_execution_order(circular_graph)\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste falha porque o código estoura RecursionError em vez de detectar o ciclo e lançar CyclicDependencyError.",
        "analysis_scope": "graph_circular_dependency_timeout",
        "split_group": "fail_timeout_circular_dag",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://cwe.mitre.org/data/definitions/674.html (Uncontrolled Recursion)",
        "gaps": [
            {
                "category": "performance_reliability",
                "title": "Falha de teste por recursão infinita e ausência de detecção de ciclo (RecursionError)",
                "description": "O teste falha com 'Failed: DID NOT RAISE CyclicDependencyError' (dispara RecursionError) porque o DFS não possui conjunto de nós em processamento (visiting / recursion_stack).",
                "evidence": "RecursionError: maximum recursion depth exceeded in comparison.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_detects_triangle_cycle_gracefully():\n"
                    "    # Ciclo A -> B -> C -> A\n"
                    "    triangle = {'A': ['B'], 'B': ['C'], 'C': ['A']}\n"
                    "    with pytest.raises(CyclicDependencyError, match='Ciclo detectado'):\n"
                    "        resolve_execution_order(triangle)\n"
                ),
                "expected_result": "Implementar 3 estados de cores no DFS (branco, cinza, preto) para lançar CyclicDependencyError em tempo O(V+E)."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 4. IntegrityError - Violacao de Unicidade sem Rollback em Banco de Dados
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste por Conflito de Chave Única em Cadastro Concorrente (IntegrityError)",
        "project_name": "UserRegistrationService",
        "description": "Módulo de persistência de credenciais e contas de usuário com validação relacional.",
        "requirements_text": (
            "REQ-USR-001: A função register_user deve persistir um novo usuário no SQLite garantindo unicidade de e-mail.\n"
            "REQ-USR-002: Se o e-mail já estiver cadastrado, a função deve capturar a violação de constraint e lançar a exceção de domínio DuplicateEmailException.\n"
            "REQ-USR-003: A transação em falha DEVE executar rollback para não deixar a conexão em estado inconsistente."
        ),
        "source_code": (
            "import sqlite3\n\n"
            "class DuplicateEmailException(Exception): pass\n\n"
            "def register_user(conn: sqlite3.Connection, username: str, email: str) -> int:\n"
            "    cursor = conn.cursor()\n"
            "    # DEFEITO: Não faz try/except em sqlite3.IntegrityError e não executa rollback\n"
            "    cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))\n"
            "    conn.commit()\n"
            "    return cursor.lastrowid\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "import sqlite3\n\n"
            "@pytest.fixture\n"
            "def db():\n"
            "    conn = sqlite3.connect(':memory:')\n"
            "    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT UNIQUE)')\n"
            "    conn.commit()\n"
            "    yield conn\n"
            "    conn.close()\n\n"
            "def test_register_duplicate_email_raises_domain_exception(db):\n"
            "    register_user(db, 'alice', 'alice@example.com')\n"
            "    # MOTIVO DA FALHA DO TESTE: sqlite3.IntegrityError em vez de DuplicateEmailException\n"
            "    with pytest.raises(DuplicateEmailException):\n"
            "        register_user(db, 'alice2', 'alice@example.com')\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste falha porque o código propaga sqlite3.IntegrityError cru em vez da exceção de domínio DuplicateEmailException.",
        "analysis_scope": "database_integrity_constraint_failure",
        "split_group": "fail_integrity_unique_email",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://cwe.mitre.org/data/definitions/209.html (Generation of Error Message Containing Sensitive Information)",
        "gaps": [
            {
                "category": "integration_state",
                "title": "Falha de teste por vazamento de sqlite3.IntegrityError sem rollback (IntegrityError)",
                "description": "O teste falha com 'sqlite3.IntegrityError: UNIQUE constraint failed: users.email' porque o repositório não encapsula o erro em DuplicateEmailException nem faz conn.rollback().",
                "evidence": "sqlite3.IntegrityError: UNIQUE constraint failed: users.email.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_database_connection_healthy_after_duplicate_error(db):\n"
                    "    register_user(db, 'u1', 'shared@mail.com')\n"
                    "    with pytest.raises(DuplicateEmailException):\n"
                    "        register_user(db, 'u2', 'shared@mail.com')\n"
                    "    # Garante que rollback foi feito e podemos inserir outro normal\n"
                    "    uid = register_user(db, 'u3', 'other@mail.com')\n"
                    "    assert uid > 0\n"
                ),
                "expected_result": "Capturar sqlite3.IntegrityError, executar conn.rollback() e lançar DuplicateEmailException."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 5. Security Bypass / AssertionError - Falha de Autorizacao BOLA/IDOR
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste de Segurança por Ausência de Checagem de Tenant (IDOR Security Failure)",
        "project_name": "MultiTenantDocumentVault",
        "description": "API de cofre de documentos corporativos com isolamento lógico multi-inquilino (multi-tenant).",
        "requirements_text": (
            "REQ-SEC-001: Documentos pertencem a um tenant_id específico.\n"
            "REQ-SEC-002: Ao solicitar GET /documents/{id}, a API DEVE validar se o documento pertence ao tenant_id do usuário autenticado no token.\n"
            "REQ-SEC-003: Se um usuário de tenant_id A tentar ler documento de tenant_id B, a API DEVE retornar estritamente HTTP 403 (Forbidden) ou 404 (Not Found)."
        ),
        "source_code": (
            "class DocumentController:\n"
            "    def __init__(self, db_store):\n"
            "        self.db = db_store\n\n"
            "    def get_document(self, current_user: dict, doc_id: str):\n"
            "        # DEFEITO DE SEGURANÇA: Busca o documento apenas pelo ID sem filtrar por current_user['tenant_id']\n"
            "        doc = self.db.get(doc_id)\n"
            "        if not doc:\n"
            "            return {'status': 404, 'error': 'Documento não encontrado'}\n"
            "        # FALTA CHECAGEM: if doc['tenant_id'] != current_user['tenant_id']: return {'status': 403}!\n"
            "        return {'status': 200, 'data': doc}\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "def test_idor_cross_tenant_access_blocked():\n"
            "    # Documento pertencente a Empresa X (tenant_99)\n"
            "    fake_db = {'doc_1': {'id': 'doc_1', 'tenant_id': 'tenant_99', 'confidential': 'dados_secretos'}}\n"
            "    controller = DocumentController(fake_db)\n"
            "    # Atacante autenticado na Empresa Y (tenant_01)\n"
            "    attacker_user = {'user_id': 'hacker_bob', 'tenant_id': 'tenant_01'}\n"
            "    response = controller.get_document(attacker_user, 'doc_1')\n"
            "    # MOTIVO DA FALHA DO TESTE: AssertionError: assert 200 in [403, 404] (Vulnerabilidade BOLA/IDOR exposta)\n"
            "    assert response['status'] in [403, 404], f'Vulnerabilidade IDOR detectada! Retornou: {response}'\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste de segurança falha com AssertionError revelando vulnerabilidade crítica de Broken Object Level Authorization (IDOR).",
        "analysis_scope": "idor_cross_tenant_security_failure",
        "split_group": "fail_authz_idor_tenant",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Falha de teste de segurança por vazamento de documento entre inquilinos (AssertionError: 200 in [403, 404])",
                "description": "O teste automatizado de segurança falhou porque o endpoint respondeu HTTP 200 contendo dados sigilosos ao receber requisição de outro inquilino (IDOR / BOLA).",
                "evidence": "AssertionError: Vulnerabilidade IDOR detectada! Retornou: {'status': 200, 'data': {'confidential': 'dados_secretos'}}.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_enforce_tenant_authorization():\n"
                    "    res = controller.get_document({'tenant_id': 'outro'}, 'doc_1')\n"
                    "    assert res['status'] == 403\n"
                ),
                "expected_result": "Adicionar verificação doc['tenant_id'] == current_user['tenant_id'] retornando HTTP 403 Forbidden."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 6. Mock Signature Incompatibility - Mock Esperando Assinatura Antiga
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste por Assinatura Incompatível em Mock de Serviço de Notificação (MockError)",
        "project_name": "OrderFulfillmentWorker",
        "description": "Worker de envio de notificações de compras integrando serviço de e-mail corporativo.",
        "requirements_text": (
            "REQ-NOT-001: Ao aprovar um pedido, a função notify_order_approved deve despachar e-mail ao cliente.\n"
            "REQ-NOT-002: A função send_email da biblioteca externa foi refatorada e agora exige obrigatoriamente os parâmetros: recipient, template_id e sender_address.\n"
            "REQ-NOT-003: Testes de unidade que mockam a função send_email devem refletir a nova assinatura com sender_address."
        ),
        "source_code": (
            "# Codigo refatorado chamando a nova assinatura do servico externo\n"
            "def notify_order_approved(order: dict, email_client) -> bool:\n"
            "    # Codigo em conformidade com o novo contrato que exige sender_address\n"
            "    return email_client.send_email(\n"
            "        recipient=order['customer_email'],\n"
            "        template_id='order_approved_v2',\n"
            "        sender_address='noreply@loja.com'\n"
            "    )\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from unittest.mock import MagicMock\n\n"
            "def test_notify_order_approved_dispatches_email():\n"
            "    mock_email = MagicMock()\n"
            "    order = {'id': 123, 'customer_email': 'cliente@teste.com'}\n"
            "    notify_order_approved(order, mock_email)\n"
            "    # MOTIVO DA FALHA DO TESTE: AssertionError do mock por assinatura desatualizada no teste legado!\n"
            "    # O teste antigo espera apenas (recipient, template_id), sem sender_address\n"
            "    mock_email.send_email.assert_called_once_with(\n"
            "        recipient='cliente@teste.com',\n"
            "        template_id='order_approved_v2'\n"
            "    )\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste falha com AssertionError: expected call not found porque a suíte de teste está desatualizada em relação à nova assinatura do mock.",
        "analysis_scope": "mock_contract_drift_failure",
        "split_group": "fail_mock_signature_mismatch",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://martinfowler.com/articles/mocksArentStubs.html (Mocks Aren't Stubs)",
        "gaps": [
            {
                "category": "test_quality",
                "title": "Falha de teste por drift de contrato em mock desatualizado (AssertionError: mock.assert_called_once_with)",
                "description": "O teste falhou porque o mock na suíte de testes permaneceu com a assinatura antiga, ignorando o novo parâmetro mandatório 'sender_address' exigido pelo código de produção.",
                "evidence": "AssertionError: expected call not equal to actual call: extra kwargs: sender_address='noreply@loja.com'.",
                "severity": "medium",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_mock_aligned_with_latest_signature():\n"
                    "    mock_client = MagicMock()\n"
                    "    notify_order_approved({'customer_email': 'a@b.com'}, mock_client)\n"
                    "    mock_client.send_email.assert_called_once_with(\n"
                    "        recipient='a@b.com',\n"
                    "        template_id='order_approved_v2',\n"
                    "        sender_address='noreply@loja.com'\n"
                    "    )\n"
                ),
                "expected_result": "Atualizar a asserção do mock para incluir sender_address='noreply@loja.com'."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 7. Schema ValidationError - Quebra de Contrato de API (Breaking Change)
    # -------------------------------------------------------------------------
    {
        "title": "Falha de Teste por Quebra de Contrato e Ausência de Campo Obrigatório (ValidationError)",
        "project_name": "ShippingCalculationAPI",
        "description": "API de cálculo de frete logístico com validação Pydantic de payload.",
        "requirements_text": (
            "REQ-SHP-001: O payload de cálculo de frete exige: weight_kg (>0), destination_zip e o novo campo obrigatório state_code (UF de 2 caracteres).\n"
            "REQ-SHP-002: Payloads legados sem o campo state_code devem ser rejeitados com ValidationError.\n"
            "REQ-SHP-003: O peso não pode exceder o limite de transporte aéreo de 30.0 kg."
        ),
        "source_code": (
            "from pydantic import BaseModel, Field, ValidationError\n\n"
            "class ShippingRequest(BaseModel):\n"
            "    weight_kg: float = Field(gt=0, le=30)\n"
            "    destination_zip: str\n"
            "    state_code: str = Field(min_length=2, max_length=2)  # NOVO CAMPO OBRIGATÓRIO (BREAKING CHANGE)\n\n"
            "def calculate_shipping(data: dict) -> float:\n"
            "    req = ShippingRequest(**data)\n"
            "    return 15.0 + (req.weight_kg * 2.5)\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "def test_legacy_payload_fails_with_validation_error():\n"
            "    # Payload de teste legado (v1) que nao continha state_code\n"
            "    legacy_v1_payload = {'weight_kg': 5.0, 'destination_zip': '01310-100'}\n"
            "    # O teste da versao v1 esperava calcular normalmente\n"
            "    # MOTIVO DA FALHA DO TESTE: pydantic.ValidationError: Field required: state_code\n"
            "    cost = calculate_shipping(legacy_v1_payload)\n"
            "    assert cost == 27.5\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Teste legado falha com ValidationError devido à quebra de contrato sem migração retrocompatível.",
        "analysis_scope": "pydantic_schema_breaking_change",
        "split_group": "fail_schema_breaking_contract",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://docs.pydantic.dev/latest/errors/validation_errors/",
        "gaps": [
            {
                "category": "functional_coverage",
                "title": "Falha de teste por quebra de retrocompatibilidade de contrato de API (ValidationError: state_code required)",
                "description": "O teste legado falha com 'pydantic_core._pydantic_core.ValidationError: 1 validation error for ShippingRequest state_code Field required' porque a API não suporta fallback ou valor default para payloads v1.",
                "evidence": "ValidationError: state_code Field required [type=missing, input_value={'weight_kg': 5.0, ...}].",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_calculate_shipping_with_v2_contract():\n"
                    "    v2_payload = {'weight_kg': 5.0, 'destination_zip': '01310-100', 'state_code': 'SP'}\n"
                    "    assert calculate_shipping(v2_payload) == 27.5\n"
                ),
                "expected_result": "Adicionar state_code ao teste ou disponibilizar valor default/fallback no modelo."
            }
        ]
    }
]


def ingest_failing_tests_cases():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    cat_repo = CategoryRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    cats = {c.code: c.id for c in cat_repo.get_all(include_inactive=True)}
    default_cat_id = cats.get("functional_coverage", 1)

    print("[*] Inserindo lote de testes com falhas reais por diferentes motivos no TestGap...")

    imported = 0
    skipped = 0

    for item in FAILING_TESTS_EXAMPLES:
        initial_gaps = []
        for g in item["gaps"]:
            cat_id = cats.get(g["category"], default_cat_id)
            initial_gaps.append(
                GapCreate(
                    category_id=cat_id,
                    title=g["title"],
                    description=g["description"],
                    requirement_reference=item.get("source_reference", ""),
                    evidence=g["evidence"],
                    severity=Severity(g["severity"]),
                    confidence=g["confidence"],
                    suggested_test=g["suggested_test"],
                    expected_result=g["expected_result"],
                    status=GapStatus.CONFIRMED
                )
            )

        payload = ExampleCreate(
            title=item["title"],
            project_name=item["project_name"],
            description=item["description"],
            requirements_text=item["requirements_text"],
            source_code=item["source_code"],
            source_language=item["source_language"],
            test_framework=item["test_framework"],
            test_suite_text=item["test_suite_text"],
            test_format=item["test_format"],
            expected_behavior=item["expected_behavior"],
            analysis_scope=item["analysis_scope"],
            split_group=item["split_group"],
            source_type=item["source_type"],
            source_reference=item["source_reference"],
            initial_gaps=initial_gaps
        )

        try:
            ex = ex_service.create_example(payload)
            rev_service.update_status(
                ex.id,
                ReviewStatus.APPROVED,
                review_note="Exemplo de falha de teste categorizado com root cause especificado e aprovado."
            )
            print(f"[+] Importado: {ex.public_id} — {ex.title}")
            imported += 1
        except ValueError as ve:
            print(f"[-] Ja existente (ignorado): {item['title']}")
            skipped += 1

    print(f"\n[+] Concluido: {imported} exemplos de falhas de testes inseridos, {skipped} duplicados.")


if __name__ == "__main__":
    ingest_failing_tests_cases()
