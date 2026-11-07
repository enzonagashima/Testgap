"""CLI Script: Seed database with high-value Security & Authentication test-gap examples.

This batch focuses on OWASP Top 10, RFC 7519 (JWT), RFC 6749 (OAuth2 CSRF),
IDOR / BOLA, and Rate-Limiting bypass scenarios.
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

SECURITY_EXAMPLES = [
    # -------------------------------------------------------------------------
    # Caso 1: RFC 7519 (JWT) - Ataque de Algoritmo 'none' e Tolerância de Expiração
    # -------------------------------------------------------------------------
    {
        "title": "Validação de Token JWT com Proteção contra Ataque de Algoritmo None",
        "project_name": "AuthGateway",
        "description": "Módulo de decodificação e verificação de integridade de tokens JWT para APIs REST.",
        "requirements_text": (
            "REQ-JWT-001: O sistema deve validar a assinatura do token usando exclusivamente o algoritmo HS256 com a chave secreta configurada.\n"
            "REQ-JWT-002: Tokens que utilizem o algoritmo 'none' ou qualquer algoritmo não explicitamente permitido devem ser sumariamente rejeitados com InvalidAlgorithmError.\n"
            "REQ-JWT-003: O token deve conter a claim de expiração 'exp'. Se a data atual for posterior a 'exp' considerando uma tolerância (leeway) máxima de 10 segundos, levantar TokenExpiredError."
        ),
        "source_code": (
            "import hmac\n"
            "import hashlib\n"
            "import base64\n"
            "import json\n"
            "import time\n\n"
            "class InvalidAlgorithmError(Exception): pass\n"
            "class TokenExpiredError(Exception): pass\n"
            "class InvalidSignatureError(Exception): pass\n\n"
            "def decode_and_verify_jwt(token: str, secret_key: str, allowed_algorithms=('HS256',), leeway: int = 10) -> dict:\n"
            "    parts = token.split('.')\n"
            "    if len(parts) != 3:\n"
            "        raise ValueError('Formato de token invalido')\n"
            "    header_raw, payload_raw, signature_raw = parts\n"
            "    header = json.loads(base64.urlsafe_b64decode(header_raw + '===').decode('utf-8'))\n"
            "    payload = json.loads(base64.urlsafe_b64decode(payload_raw + '===').decode('utf-8'))\n"
            "    alg = header.get('alg')\n"
            "    if alg not in allowed_algorithms or alg.lower() == 'none':\n"
            "        raise InvalidAlgorithmError(f'Algoritmo nao permitido: {alg}')\n"
            "    expected_sig = hmac.new(secret_key.encode(), f'{header_raw}.{payload_raw}'.encode(), hashlib.sha256).digest()\n"
            "    actual_sig = base64.urlsafe_b64decode(signature_raw + '===')\n"
            "    if not hmac.compare_digest(expected_sig, actual_sig):\n"
            "        raise InvalidSignatureError('Assinatura invalida')\n"
            "    exp = payload.get('exp')\n"
            "    if exp is None or time.time() > (exp + leeway):\n"
            "        raise TokenExpiredError('Token expirado')\n"
            "    return payload\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "import time\n"
            "import base64\n"
            "import json\n"
            "import hmac\n"
            "import hashlib\n\n"
            "def make_token(header, payload, secret):\n"
            "    h = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')\n"
            "    p = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')\n"
            "    sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), f'{h}.{p}'.encode(), hashlib.sha256).digest()).decode().rstrip('=')\n"
            "    return f'{h}.{p}.{sig}'\n\n"
            "def test_valid_token_success():\n"
            "    token = make_token({'alg': 'HS256'}, {'sub': 'user1', 'exp': time.time() + 3600}, 'secret123')\n"
            "    payload = decode_and_verify_jwt(token, 'secret123')\n"
            "    assert payload['sub'] == 'user1'\n\n"
            "def test_token_expired_one_hour_ago():\n"
            "    token = make_token({'alg': 'HS256'}, {'sub': 'user1', 'exp': time.time() - 3600}, 'secret123')\n"
            "    with pytest.raises(TokenExpiredError):\n"
            "        decode_and_verify_jwt(token, 'secret123')\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Garantir rejeição de alg:none e precisão de expiração no limite do leeway (10s).",
        "analysis_scope": "autenticacao_jwt",
        "split_group": "sec_jwt_auth",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "RFC 7519 / OWASP JWT Cheat Sheet",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Ausência de teste para ataque de algoritmo 'none' (CVE-2015-9235 pattern)",
                "description": "A suíte não testa o cenário onde um invasor manipula o header para alg: 'none' e omite a assinatura para tentar bypass de verificação.",
                "evidence": "Todos os testes usam exclusivamente {'alg': 'HS256'}.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_reject_algorithm_none_bypass():\n"
                    "    h = base64.urlsafe_b64encode(json.dumps({'alg': 'none'}).encode()).decode().rstrip('=')\n"
                    "    p = base64.urlsafe_b64encode(json.dumps({'sub': 'admin', 'exp': time.time() + 100}).encode()).decode().rstrip('=')\n"
                    "    unsigned_token = f'{h}.{p}.'\n"
                    "    with pytest.raises(InvalidAlgorithmError):\n"
                    "        decode_and_verify_jwt(unsigned_token, 'secret123')\n"
                ),
                "expected_result": "Levantar InvalidAlgorithmError sem verificar assinatura ou payload."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste de borda para o limite exato de tolerância de expiração (leeway = 10s)",
                "description": "A suíte testa apenas expiração grotesca (1 hora atrás), mas não valida se a tolerância de 10s é respeitada (ex: token expirado há 9s ainda é aceito, e há 11s é rejeitado).",
                "evidence": "O teste de expiração usa -3600 segundos; nenhum caso valida a janela de 10s.",
                "severity": "medium",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_leeway_boundary_tolerance():\n"
                    "    now = time.time()\n"
                    "    # Expirado há 8s (dentro dos 10s de leeway) -> Deve aceitar\n"
                    "    token_within = make_token({'alg': 'HS256'}, {'sub': 'u1', 'exp': now - 8}, 'secret123')\n"
                    "    assert decode_and_verify_jwt(token_within, 'secret123', leeway=10)['sub'] == 'u1'\n"
                    "    # Expirado há 12s (fora do leeway) -> Deve rejeitar\n"
                    "    token_outside = make_token({'alg': 'HS256'}, {'sub': 'u1', 'exp': now - 12}, 'secret123')\n"
                    "    with pytest.raises(TokenExpiredError):\n"
                    "        decode_and_verify_jwt(token_outside, 'secret123', leeway=10)\n"
                ),
                "expected_result": "Token com exp < now mas dentro do leeway é aceito; ultrapassou o leeway é rejeitado."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # Caso 2: Controle de Acesso em Nível de Objeto (OWASP API1:2023 - BOLA / IDOR)
    # -------------------------------------------------------------------------
    {
        "title": "Autorização Horizontal em API Multi-Tenant (Proteção contra BOLA / IDOR)",
        "project_name": "BillingService",
        "description": "Endpoint de consulta e download de faturas em arquitetura SaaS multi-empresa.",
        "requirements_text": (
            "REQ-AUTHZ-001: Um usuário autenticado pode consultar faturas pertencentes exclusivamente à sua própria organização (tenant_id).\n"
            "REQ-AUTHZ-002: Se um usuário autenticado tentar acessar uma fatura existente pertencente a outra organização, a API deve retornar HTTP 404 (Not Found) ou HTTP 403, sem expor os dados da outra empresa.\n"
            "REQ-AUTHZ-003: Administradores globais (is_superuser=True) podem acessar faturas de qualquer tenant."
        ),
        "source_code": (
            "class AccessDeniedException(Exception): pass\n"
            "class InvoiceNotFoundException(Exception): pass\n\n"
            "class InvoiceService:\n"
            "    def __init__(self, db_session):\n"
            "        self.db = db_session\n\n"
            "    def get_invoice(self, invoice_id: int, current_user) -> dict:\n"
            "        invoice = self.db.find_invoice_by_id(invoice_id)\n"
            "        if not invoice:\n"
            "            raise InvoiceNotFoundException('Fatura inexistente')\n"
            "        if not current_user.is_superuser and invoice['tenant_id'] != current_user.tenant_id:\n"
            "            raise InvoiceNotFoundException('Fatura inexistente')  # Oculta existencia para outro tenant\n"
            "        return invoice\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "class DummyUser:\n"
            "    def __init__(self, user_id, tenant_id, is_superuser=False):\n"
            "        self.user_id = user_id\n"
            "        self.tenant_id = tenant_id\n"
            "        self.is_superuser = is_superuser\n\n"
            "def test_user_can_access_own_invoice(mocker):\n"
            "    mock_db = mocker.Mock()\n"
            "    mock_db.find_invoice_by_id.return_value = {'id': 100, 'tenant_id': 'tenant_A', 'amount': 250.0}\n"
            "    service = InvoiceService(mock_db)\n"
            "    user_a = DummyUser(user_id=1, tenant_id='tenant_A')\n"
            "    inv = service.get_invoice(100, user_a)\n"
            "    assert inv['id'] == 100\n"
            "    assert inv['amount'] == 250.0\n\n"
            "def test_get_nonexistent_invoice_raises_not_found(mocker):\n"
            "    mock_db = mocker.Mock()\n"
            "    mock_db.find_invoice_by_id.return_value = None\n"
            "    service = InvoiceService(mock_db)\n"
            "    user_a = DummyUser(user_id=1, tenant_id='tenant_A')\n"
            "    with pytest.raises(InvoiceNotFoundException):\n"
            "        service.get_invoice(999, user_a)\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Validar rejeição quando usuário A tenta acessar recurso existente do usuário B.",
        "analysis_scope": "autorizacao_idor",
        "split_group": "sec_idor_authz",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "OWASP API Security Top 10 - API1:2023 BOLA",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Falta de teste para acesso não autorizado entre tenants (IDOR / BOLA)",
                "description": "A suíte testa o caminho feliz e fatura inexistente, mas NÃO testa a vulnerabilidade principal: usuário do tenant A tentando acessar fatura válida do tenant B.",
                "evidence": "Nenhum teste instancia dois usuários com tenant_ids distintos.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_prevent_cross_tenant_access_idor(mocker):\n"
                    "    mock_db = mocker.Mock()\n"
                    "    # Fatura existe e pertence à Empresa B\n"
                    "    mock_db.find_invoice_by_id.return_value = {'id': 200, 'tenant_id': 'tenant_B', 'amount': 999.0}\n"
                    "    service = InvoiceService(mock_db)\n"
                    "    user_attacker = DummyUser(user_id=2, tenant_id='tenant_A')  # Usuario da Empresa A\n"
                    "    with pytest.raises(InvoiceNotFoundException):\n"
                    "        service.get_invoice(200, user_attacker)\n"
                ),
                "expected_result": "Bloquear o acesso levantando InvoiceNotFoundException e não revelando dados."
            },
            {
                "category": "functional_coverage",
                "title": "Ausência de teste para privilégio de superusuário",
                "description": "REQ-AUTHZ-003 estabelece que administradores com is_superuser=True têm permissão global de acesso a faturas de qualquer tenant, mas isso não é verificado.",
                "evidence": "DummyUser.is_superuser nunca é configurado como True nos testes existentes.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_superuser_can_access_any_tenant_invoice(mocker):\n"
                    "    mock_db = mocker.Mock()\n"
                    "    mock_db.find_invoice_by_id.return_value = {'id': 300, 'tenant_id': 'tenant_Z', 'amount': 500.0}\n"
                    "    service = InvoiceService(mock_db)\n"
                    "    admin_user = DummyUser(user_id=99, tenant_id='admin_tenant', is_superuser=True)\n"
                    "    inv = service.get_invoice(300, admin_user)\n"
                    "    assert inv['id'] == 300\n"
                ),
                "expected_result": "Superusuário acessa faturas de outros tenants normalmente."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # Caso 3: Rate Limiting com Proteção contra IP Spoofing (X-Forwarded-For)
    # -------------------------------------------------------------------------
    {
        "title": "Rate Limiting de Autenticação com Validação de Headers de Proxy",
        "project_name": "SecurityMiddleware",
        "description": "Middleware de controle de requisições por IP com proteção anti-forjamento de IP.",
        "requirements_text": (
            "REQ-RATE-001: Limitar requisições de login a no máximo 5 tentativas por janela de 60 segundos por IP real.\n"
            "REQ-RATE-002: O IP do cliente deve ser extraído do remote_addr da conexão. O cabeçalho 'X-Forwarded-For' só deve ser confiado se a conexão vier de um proxy reverso confiável configurado.\n"
            "REQ-RATE-003: Tentativas excedentes devem retornar HTTP 429 com o cabeçalho 'Retry-After' informando os segundos restantes."
        ),
        "source_code": (
            "class RateLimitExceeded(Exception):\n"
            "    def __init__(self, retry_after):\n"
            "        self.retry_after = retry_after\n\n"
            "class LoginRateLimiter:\n"
            "    def __init__(self, redis_client, max_attempts=5, window_seconds=60, trusted_proxies=None):\n"
            "        self.redis = redis_client\n"
            "        self.max_attempts = max_attempts\n"
            "        self.window = window_seconds\n"
            "        self.trusted_proxies = set(trusted_proxies or [])\n\n"
            "    def get_real_ip(self, remote_addr: str, headers: dict) -> str:\n"
            "        if remote_addr in self.trusted_proxies and 'X-Forwarded-For' in headers:\n"
            "            # Pega o primeiro IP da cadeia repassada pelo proxy confiavel\n"
            "            return headers['X-Forwarded-For'].split(',')[0].strip()\n"
            "        return remote_addr\n\n"
            "    def check_rate_limit(self, remote_addr: str, headers: dict):\n"
            "        ip = self.get_real_ip(remote_addr, headers)\n"
            "        key = f'ratelimit:login:{ip}'\n"
            "        current = self.redis.incr(key)\n"
            "        if current == 1:\n"
            "            self.redis.expire(key, self.window)\n"
            "        if current > self.max_attempts:\n"
            "            ttl = self.redis.ttl(key)\n"
            "            raise RateLimitExceeded(retry_after=max(1, ttl))\n"
            "        return True\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "class MockRedis:\n"
            "    def __init__(self):\n"
            "        self.data = {}\n"
            "        self.ttls = {}\n"
            "    def incr(self, key):\n"
            "        self.data[key] = self.data.get(key, 0) + 1\n"
            "        return self.data[key]\n"
            "    def expire(self, key, seconds):\n"
            "        self.ttls[key] = seconds\n"
            "    def ttl(self, key):\n"
            "        return self.ttls.get(key, 60)\n\n"
            "def test_allow_five_attempts():\n"
            "    limiter = LoginRateLimiter(MockRedis(), max_attempts=5)\n"
            "    for _ in range(5):\n"
            "        assert limiter.check_rate_limit('192.168.1.100', {}) is True\n\n"
            "def test_block_sixth_attempt():\n"
            "    limiter = LoginRateLimiter(MockRedis(), max_attempts=5)\n"
            "    for _ in range(5):\n"
            "        limiter.check_rate_limit('192.168.1.100', {})\n"
            "    with pytest.raises(RateLimitExceeded):\n"
            "        limiter.check_rate_limit('192.168.1.100', {})\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Bloquear tentativas de spoofing de IP usando X-Forwarded-For falso sem proxy confiável.",
        "analysis_scope": "rate_limiting_anti_spoofing",
        "split_group": "sec_rate_limit",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "OWASP Automated Threat Handbook (OAT-007 Brute Force)",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Ausência de teste para tentativa de bypass de rate-limit via X-Forwarded-For falso",
                "description": "Invasores forjam cabeçalhos X-Forwarded-For para alternar o IP em cada requisição. A suíte não testa se o sistema ignora o cabeçalho quando a conexão não parte de um proxy confiável.",
                "evidence": "Todos os testes passam headers={} vazio, nunca testando a lógica de get_real_ip.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_ignore_spoofed_x_forwarded_for_from_untrusted_source():\n"
                    "    # Servidor sem proxy confiavel (ou atacante direto na porta da aplicacao)\n"
                    "    limiter = LoginRateLimiter(MockRedis(), max_attempts=5, trusted_proxies=['10.0.0.1'])\n"
                    "    untrusted_attacker_ip = '203.0.113.50'\n"
                    "    # Atacante tenta forjar 5 IPs diferentes no header X-Forwarded-For\n"
                    "    for i in range(5):\n"
                    "        headers = {'X-Forwarded-For': f'198.51.100.{i}'}\n"
                    "        limiter.check_rate_limit(untrusted_attacker_ip, headers)\n"
                    "    # A 6a tentativa deve ser bloqueada porque o IP real continua sendo o mesmo\n"
                    "    with pytest.raises(RateLimitExceeded):\n"
                    "        limiter.check_rate_limit(untrusted_attacker_ip, {'X-Forwarded-For': '198.51.100.99'})\n"
                ),
                "expected_result": "O atacante é bloqueado pelo remote_addr, ignorando os IPs forjados no header."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste para valor de Retry-After retornado na exceção",
                "description": "REQ-RATE-003 exige informar o tempo restante na janela de rate limit, mas a suíte não valida o valor de retry_after anexado à exceção RateLimitExceeded.",
                "evidence": "Nenhum assert verifica exc_info.value.retry_after.",
                "severity": "medium",
                "confidence": 0.9,
                "suggested_test": (
                    "def test_retry_after_value_positive():\n"
                    "    limiter = LoginRateLimiter(MockRedis(), max_attempts=1)\n"
                    "    limiter.check_rate_limit('10.1.1.1', {})\n"
                    "    with pytest.raises(RateLimitExceeded) as exc_info:\n"
                    "        limiter.check_rate_limit('10.1.1.1', {})\n"
                    "    assert exc_info.value.retry_after > 0\n"
                ),
                "expected_result": "retry_after contém um número inteiro estritamente positivo representando os segundos restantes."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # Caso 4: OAuth2 / OIDC - Validação de Parâmetro State (Proteção contra CSRF)
    # -------------------------------------------------------------------------
    {
        "title": "Validação de Parâmetro State no Fluxo de Autorização OAuth2 contra CSRF",
        "project_name": "IdentityBroker",
        "description": "Handler de callback de provedores de identidade OAuth2 / OIDC (Google, GitHub, etc).",
        "requirements_text": (
            "REQ-OAUTH-001: Ao receber o callback do provedor, o parâmetro 'state' retornado na URL deve ser idêntico ao 'state' previamente gerado e salvo na sessão do usuário.\n"
            "REQ-OAUTH-002: Se o parâmetro 'state' estiver ausente, vazio ou não coincidir exatamente, rejeitar com CSRFValidationException.\n"
            "REQ-OAUTH-003: Após a validação com sucesso, o 'state' deve ser imediatamente excluído da sessão para impedir ataques de repetição (Replay Attacks)."
        ),
        "source_code": (
            "import secrets\n\n"
            "class CSRFValidationException(Exception): pass\n"
            "class ReplayAttackException(Exception): pass\n\n"
            "class OAuthCallbackHandler:\n"
            "    @staticmethod\n"
            "    def generate_state(session: dict) -> str:\n"
            "        state = secrets.token_urlsafe(32)\n"
            "        session['oauth_state'] = state\n"
            "        return state\n\n"
            "    @staticmethod\n"
            "    def validate_callback(query_params: dict, session: dict) -> str:\n"
            "        incoming_state = query_params.get('state')\n"
            "        saved_state = session.get('oauth_state')\n"
            "        if not incoming_state or not saved_state:\n"
            "            raise CSRFValidationException('Parametro state ausente ou sessao expirada')\n"
            "        if not secrets.compare_digest(incoming_state, saved_state):\n"
            "            raise CSRFValidationException('Possivel ataque CSRF: state divergente')\n"
            "        # Remove state para prevenir replay\n"
            "        del session['oauth_state']\n"
            "        code = query_params.get('code')\n"
            "        if not code:\n"
            "            raise ValueError('Authorization code ausente')\n"
            "        return code\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "def test_oauth_callback_success():\n"
            "    session = {}\n"
            "    state = OAuthCallbackHandler.generate_state(session)\n"
            "    code = OAuthCallbackHandler.validate_callback({'state': state, 'code': 'valid_auth_code_123'}, session)\n"
            "    assert code == 'valid_auth_code_123'\n\n"
            "def test_oauth_callback_mismatched_state():\n"
            "    session = {'oauth_state': 'real_state_xyz'}\n"
            "    with pytest.raises(CSRFValidationException):\n"
            "        OAuthCallbackHandler.validate_callback({'state': 'fake_state_abc', 'code': 'any'}, session)\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Garantir destruição do state pós-uso para evitar Replay Attack e teste de state ausente.",
        "analysis_scope": "oauth2_state_csrf",
        "split_group": "sec_oauth_csrf",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "RFC 6749 Section 10.12 (Cross-Site Request Forgery)",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Ausência de teste de destruição do state pós-uso (Prevenção de Replay Attack)",
                "description": "REQ-OAUTH-003 exige que o state seja consumido e deletado imediatamente da sessão para evitar reutilização. A suíte testa a validação mas não verifica se 'oauth_state' foi removido da sessão após o sucesso.",
                "evidence": "Nenhum teste contém assert 'oauth_state' not in session após chamar validate_callback.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_state_is_deleted_after_single_use():\n"
                    "    session = {'oauth_state': 'one_time_token_123'}\n"
                    "    OAuthCallbackHandler.validate_callback({'state': 'one_time_token_123', 'code': 'c1'}, session)\n"
                    "    # O state precisa ter sido apagado da sessao\n"
                    "    assert 'oauth_state' not in session\n"
                    "    # Uma segunda tentativa com o mesmo state deve falhar imediatamente\n"
                    "    with pytest.raises(CSRFValidationException):\n"
                    "        OAuthCallbackHandler.validate_callback({'state': 'one_time_token_123', 'code': 'c1'}, session)\n"
                ),
                "expected_result": "Sessão não contém mais a chave 'oauth_state', bloqueando chamadas repetidas."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste para parâmetro state nulo ou vazio",
                "description": "A suíte testa apenas state diferente ('fake_state_abc'), mas não valida o comportamento quando o parâmetro não vem na requisição ou é string vazia.",
                "evidence": "Nenhum teste com {'state': None} ou {'state': ''}.",
                "severity": "medium",
                "confidence": 0.9,
                "suggested_test": (
                    "def test_missing_or_empty_state_parameter():\n"
                    "    session = {'oauth_state': 'valid_state_123'}\n"
                    "    with pytest.raises(CSRFValidationException):\n"
                    "        OAuthCallbackHandler.validate_callback({'code': 'c1'}, session)  # sem state\n"
                    "    with pytest.raises(CSRFValidationException):\n"
                    "        OAuthCallbackHandler.validate_callback({'state': '', 'code': 'c1'}, session)\n"
                ),
                "expected_result": "Levantar CSRFValidationException."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # Caso 5: Autenticação de Senhas com Proteção contra Enumeração de Usuários e Timing Attacks
    # -------------------------------------------------------------------------
    {
        "title": "Verificação de Senhas em Tempo Constante e Prevenção de Enumeração de Contas",
        "project_name": "AccountSecurity",
        "description": "Função central de verificação de login com proteção contra timing attacks e enumeração de e-mails.",
        "requirements_text": (
            "REQ-PASS-001: A verificação de senha deve utilizar algoritmo de hash com tempo de resposta constante, prevenindo timing attacks.\n"
            "REQ-PASS-002: Quando o usuário informado não existir no banco, a mensagem de retorno para o cliente deve ser idêntica à de senha incorreta ('Credenciais inválidas') para evitar enumeração de contas.\n"
            "REQ-PASS-003: Para evitar timing attack de enumeração de usuários, o sistema deve executar uma operação de hash 'dummy' com o mesmo custo computacional mesmo quando o usuário for inexistente."
        ),
        "source_code": (
            "import hashlib\n"
            "import hmac\n\n"
            "DUMMY_SALT = b'dummy_salt_fixed_16'\n"
            "DUMMY_HASH = hashlib.pbkdf2_hmac('sha256', b'dummy_password', DUMMY_SALT, 100000)\n\n"
            "class LoginService:\n"
            "    def __init__(self, user_repository):\n"
            "        self.users = user_repository\n\n"
            "    def authenticate(self, username: str, password_attempt: str) -> tuple[bool, str]:\n"
            "        user = self.users.find_by_username(username)\n"
            "        if user is None:\n"
            "            # Executa dummy hash para mitigar timing attack de usuario inexistente\n"
            "            hashlib.pbkdf2_hmac('sha256', password_attempt.encode(), DUMMY_SALT, 100000)\n"
            "            return False, 'Credenciais invalidas'\n"
            "        # Hash do usuario real\n"
            "        computed = hashlib.pbkdf2_hmac('sha256', password_attempt.encode(), user['salt'], 100000)\n"
            "        if not hmac.compare_digest(computed, user['password_hash']):\n"
            "            return False, 'Credenciais invalidas'\n"
            "        return True, 'Login realizado com sucesso'\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "import hashlib\n\n"
            "def make_user(username, password):\n"
            "    salt = b'salt123456789012'\n"
            "    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)\n"
            "    return {'username': username, 'salt': salt, 'password_hash': h}\n\n"
            "def test_correct_password(mocker):\n"
            "    mock_repo = mocker.Mock()\n"
            "    mock_repo.find_by_username.return_value = make_user('alice', 'correct_secret')\n"
            "    service = LoginService(mock_repo)\n"
            "    ok, msg = service.authenticate('alice', 'correct_secret')\n"
            "    assert ok is True\n"
            "    assert msg == 'Login realizado com sucesso'\n\n"
            "def test_wrong_password(mocker):\n"
            "    mock_repo = mocker.Mock()\n"
            "    mock_repo.find_by_username.return_value = make_user('alice', 'correct_secret')\n"
            "    service = LoginService(mock_repo)\n"
            "    ok, msg = service.authenticate('alice', 'wrong_pass')\n"
            "    assert ok is False\n"
            "    assert msg == 'Credenciais invalidas'\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Validar que usuário inexistente retorna mensagem idêntica e executa computação de hash.",
        "analysis_scope": "autenticacao_anti_enumeracao",
        "split_group": "sec_timing_enum",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "OWASP Authentication Cheat Sheet - User Enumeration & Timing",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Falta de teste para prevenção de enumeração com usuário inexistente",
                "description": "A suíte testa apenas senha correta e senha incorreta para um usuário que existe. Nunca valida o retorno quando o usuário NÃO existe no banco de dados.",
                "evidence": "mock_repo.find_by_username.return_value sempre retorna o usuário 'alice'.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_nonexistent_user_returns_identical_generic_message(mocker):\n"
                    "    mock_repo = mocker.Mock()\n"
                    "    mock_repo.find_by_username.return_value = None  # Usuario nao existe\n"
                    "    service = LoginService(mock_repo)\n"
                    "    ok, msg = service.authenticate('ghost_user@domain.com', 'some_password')\n"
                    "    assert ok is False\n"
                    "    # A mensagem deve ser generica para nao revelar existencia da conta\n"
                    "    assert msg == 'Credenciais invalidas'\n"
                ),
                "expected_result": "Retornar False com mensagem 'Credenciais invalidas' idêntica à de senha errada."
            },
            {
                "category": "test_quality",
                "title": "Ausência de assert verificando mitigação de timing attack via dummy hash",
                "description": "REQ-PASS-003 exige que a função execute o hash dummy quando o usuário for nulo para manter tempo de resposta equilibrado. Não há teste garantindo que essa computação ocorre.",
                "evidence": "Nenhum teste monitora se hashlib.pbkdf2_hmac foi invocado no caso de usuário inexistente.",
                "severity": "medium",
                "confidence": 0.85,
                "suggested_test": (
                    "def test_dummy_hash_is_computed_when_user_not_found(mocker):\n"
                    "    mock_repo = mocker.Mock()\n"
                    "    mock_repo.find_by_username.return_value = None\n"
                    "    spy = mocker.spy(hashlib, 'pbkdf2_hmac')\n"
                    "    service = LoginService(mock_repo)\n"
                    "    service.authenticate('nonexistent', 'pass123')\n"
                    "    assert spy.call_count >= 1  # Garante que o custo de hash foi executado\n"
                ),
                "expected_result": "pbkdf2_hmac é chamado mesmo para usuário inexistente."
            }
        ]
    }
]


def ingest_security_batch():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    cat_repo = CategoryRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    cats = {c.code: c.id for c in cat_repo.get_all(include_inactive=True)}
    default_cat_id = cats.get("security_authorization", 3)

    print("[*] Iniciando ingestão do lote de Segurança & Autenticação...")

    imported_count = 0
    skipped_count = 0

    for item in SECURITY_EXAMPLES:
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
                    severity=g["severity"],
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
                review_note="Lote de segurança aprovado com especificações RFC e OWASP."
            )
            print(f"[+] Importado com sucesso: {ex.public_id} — {ex.title}")
            imported_count += 1
        except ValueError as ve:
            print(f"[-] Já cadastrado / Duplicado: {item['title']}")
            skipped_count += 1

    print(f"\n[+] Concluído: {imported_count} exemplos de segurança importados, {skipped_count} duplicados.")


if __name__ == "__main__":
    ingest_security_batch()
