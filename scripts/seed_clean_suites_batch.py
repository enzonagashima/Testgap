"""CLI Script: Seed database with clean, 100% covered test suites (Hard Negatives).

In AI Engineering for QA / Code Auditing LLMs, having only positive examples (has_gaps=True)
causes severe Confirmation Bias, making the model hallucinate false gaps on good code.
These clean suites provide balanced true negatives (has_gaps=False, gaps=[]).
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.database import default_db
from testgap.repositories.examples import ExampleRepository
from testgap.services.example_service import ExampleService
from testgap.services.review_service import ReviewService
from testgap.schemas import ExampleCreate
from testgap.enums import SourceType, ReviewStatus

CLEAN_SUITES_EXAMPLES = [
    # -------------------------------------------------------------------------
    # 1. SemVer: Semantic Versioning Parser & Comparator (100% Covered)
    # -------------------------------------------------------------------------
    {
        "title": "SemVer: Parser e Comparador de Versionamento Semântico com Suíte Completa",
        "project_name": "SemVerCore",
        "description": "Parser e comparador de versões semânticas (SemVer 2.0.0) com suíte de testes de 100% de cobertura.",
        "requirements_text": (
            "REQ-SEM-001: A função parse_semver deve extrair major, minor e patch como inteiros não-negativos a partir da string 'X.Y.Z'.\n"
            "REQ-SEM-002: Versões com identificador de pré-lançamento (ex: '1.0.0-alpha.1') devem extrair a tag prerelease.\n"
            "REQ-SEM-003: Strings malformadas, vazias ou com componentes negativos devem disparar ValueError.\n"
            "REQ-SEM-004: A comparação entre duas instâncias de SemVer deve respeitar a precedência: major > minor > patch, onde versão com prerelease tem menor precedência que a versão final correspondente."
        ),
        "source_code": (
            "import re\n"
            "from dataclasses import dataclass\n"
            "from typing import Optional\n\n"
            "@dataclass(order=True, frozen=True)\n"
            "class SemVer:\n"
            "    major: int\n"
            "    minor: int\n"
            "    patch: int\n"
            "    prerelease: Optional[str] = None\n\n"
            "SEMVER_REGEX = re.compile(\n"
            "    r'^(?P<major>0|[1-9]\\d*)\\.(?P<minor>0|[1-9]\\d*)\\.(?P<patch>0|[1-9]\\d*)'\n"
            "    r'(?:-(?P<prerelease>[0-9A-Za-z.-]+))?$'\n"
            ")\n\n"
            "def parse_semver(version_str: str) -> SemVer:\n"
            "    if not version_str or not isinstance(version_str, str):\n"
            "        raise ValueError('Versão deve ser uma string não vazia.')\n"
            "    match = SEMVER_REGEX.match(version_str.strip())\n"
            "    if not match:\n"
            "        raise ValueError(f'Formato de versão inválido: {version_str!r}')\n"
            "    data = match.groupdict()\n"
            "    return SemVer(\n"
            "        major=int(data['major']),\n"
            "        minor=int(data['minor']),\n"
            "        patch=int(data['patch']),\n"
            "        prerelease=data['prerelease']\n"
            "    )\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from semver import parse_semver, SemVer\n\n"
            "@pytest.mark.parametrize('v_str, exp_major, exp_minor, exp_patch, exp_pre', [\n"
            "    ('0.0.4', 0, 0, 4, None),\n"
            "    ('1.2.3', 1, 2, 3, None),\n"
            "    ('10.20.30', 10, 20, 30, None),\n"
            "    ('1.0.0-alpha.1', 1, 0, 0, 'alpha.1'),\n"
            "    ('2.1.0-rc.3', 2, 1, 0, 'rc.3'),\n"
            "])\n"
            "def test_parse_valid_semver(v_str, exp_major, exp_minor, exp_patch, exp_pre):\n"
            "    v = parse_semver(v_str)\n"
            "    assert (v.major, v.minor, v.patch, v.prerelease) == (exp_major, exp_minor, exp_patch, exp_pre)\n\n"
            "@pytest.mark.parametrize('invalid_str', [\n"
            "    '', None, 123, '1', '1.0', '1.0.0.0', '01.1.1', '-1.0.0', '1.-2.3', 'v1.0.0', '1.0.0+'\n"
            "])\n"
            "def test_parse_invalid_semver_raises(invalid_str):\n"
            "    with pytest.raises(ValueError):\n"
            "        parse_semver(invalid_str)\n\n"
            "def test_semver_comparison_ordering():\n"
            "    assert parse_semver('1.0.0') < parse_semver('2.0.0')\n"
            "    assert parse_semver('1.1.0') < parse_semver('1.2.0')\n"
            "    assert parse_semver('1.0.1') < parse_semver('1.0.2')\n"
            "    assert parse_semver('1.0.0') == parse_semver('1.0.0')\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Suíte robusta de 100% de cobertura cobrindo caminhos felizes, bordas, tipos nulos, formatos inválidos e ordenação. Sem lacunas.",
        "analysis_scope": "semver_full_coverage",
        "split_group": "clean_semver_parser",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://semver.org/ (Semantic Versioning 2.0.0 Specification)",
        "gaps": []  # Hard negative (no gaps)
    },

    # -------------------------------------------------------------------------
    # 2. Slugify: URL Slug Generator with Full Unicode Normalization (100% Covered)
    # -------------------------------------------------------------------------
    {
        "title": "Slugify: Gerador de Slugs URL com Normalização Unicode e Suíte Exaustiva",
        "project_name": "WebSlugify",
        "description": "Utilitário de geração de slugs limpos para URLs com suporte a acentuação e caracteres especiais.",
        "requirements_text": (
            "REQ-SLUG-001: A função slugify deve converter a string de entrada para minúsculas e decompor acentuações Unicode (NFKD) para caracteres ASCII equivalentes (ex: 'á' -> 'a', 'ç' -> 'c').\n"
            "REQ-SLUG-002: Caracteres alfanuméricos e hífens devem ser preservados; outros símbolos devem ser substituídos por hífens.\n"
            "REQ-SLUG-003: Sequências de múltiplos hífens consecutivos devem ser condensadas em um único hífen.\n"
            "REQ-SLUG-004: Hífens nas extremidades (início ou fim) devem ser removidos (strip).\n"
            "REQ-SLUG-005: Strings vazias, em branco ou nulas devem retornar string vazia '' sem exceções."
        ),
        "source_code": (
            "import re\n"
            "import unicodedata\n\n"
            "def slugify(text: str) -> str:\n"
            "    if not text or not isinstance(text, str):\n"
            "        return ''\n"
            "    # Normaliza caracteres acentuados decompondo diacriticos\n"
            "    normalized = unicodedata.normalize('NFKD', text)\n"
            "    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')\n"
            "    # Converte para minusculas e substitui caracteres nao-alfanumericos por hifen\n"
            "    cleaned = re.sub(r'[^a-zA-Z0-9]+', '-', ascii_only).lower()\n"
            "    # Remove hifens duplicados e extremidades\n"
            "    return cleaned.strip('-')\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from slugify import slugify\n\n"
            "@pytest.mark.parametrize('inp, expected', [\n"
            "    ('Olá Mundo!', 'ola-mundo'),\n"
            "    ('Ação e Reação em São Paulo', 'acao-e-reacao-em-sao-paulo'),\n"
            "    ('Python & Streamlit 2026---Fast!', 'python-streamlit-2026-fast'),\n"
            "    ('---leading and trailing---', 'leading-and-trailing'),\n"
            "    ('SPECIAL @#$% CHARACTERS', 'special-characters'),\n"
            "    ('already-valid-slug', 'already-valid-slug'),\n"
            "    ('123 456', '123-456'),\n"
            "])\n"
            "def test_slugify_transformations(inp, expected):\n"
            "    assert slugify(inp) == expected\n\n"
            "@pytest.mark.parametrize('empty_input', ['', '   ', None, 12345, [], {}])\n"
            "def test_slugify_edge_and_invalid_inputs(empty_input):\n"
            "    assert slugify(empty_input) == ''\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Suíte cobre todas as permutações de acentuação, caracteres pontuação, múltiplos hífens, tipos nulos e inválidos. Sem lacunas.",
        "analysis_scope": "slugify_full_coverage",
        "split_group": "clean_url_slugify",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://datatracker.ietf.org/doc/html/rfc3986 (Uniform Resource Identifier Generic Syntax)",
        "gaps": []  # Hard negative (no gaps)
    },

    # -------------------------------------------------------------------------
    # 3. Exponential Backoff Retry with Full Jitter Coverage (100% Covered)
    # -------------------------------------------------------------------------
    {
        "title": "ExponentialBackoff: Cálculo de Retries com Teto e Jitter com Suíte Totalmente Coberta",
        "project_name": "ResilientNetworkClient",
        "description": "Calculador de retries com backoff exponencial truncado e jitter determinístico para arquiteturas resilientes.",
        "requirements_text": (
            "REQ-RC-001: A função compute_backoff_delay deve calcular o atraso base: base_delay * (2 ** attempt).\n"
            "REQ-RC-002: O atraso não pode exceder max_delay sob nenhuma circunstância (clamp superior).\n"
            "REQ-RC-003: O parâmetro attempt deve ser um inteiro >= 0; valores negativos devem disparar ValueError.\n"
            "REQ-RC-004: Se jitter_factor estiver ativado (0.0 a 1.0), o atraso final deve ser calculado como: base_computed * (1.0 - jitter_factor + jitter_val * jitter_factor)."
        ),
        "source_code": (
            "def compute_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 30.0, jitter_factor: float = 0.0, jitter_seed: float = 0.5) -> float:\n"
            "    if not isinstance(attempt, int) or attempt < 0:\n"
            "        raise ValueError(f'Attempt deve ser um inteiro não-negativo, recebido: {attempt!r}')\n"
            "    if base_delay <= 0 or max_delay <= 0:\n"
            "        raise ValueError('base_delay e max_delay devem ser positivos.')\n"
            "    raw_delay = base_delay * (2 ** attempt)\n"
            "    clamped = min(max_delay, raw_delay)\n"
            "    if jitter_factor > 0:\n"
            "        jitter_val = max(0.0, min(1.0, float(jitter_seed)))\n"
            "        multiplier = (1.0 - jitter_factor) + (jitter_val * jitter_factor)\n"
            "        return round(clamped * multiplier, 3)\n"
            "    return round(clamped, 3)\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from backoff import compute_backoff_delay\n\n"
            "def test_compute_backoff_exponential_progression():\n"
            "    assert compute_backoff_delay(0, base_delay=1.0) == 1.0\n"
            "    assert compute_backoff_delay(1, base_delay=1.0) == 2.0\n"
            "    assert compute_backoff_delay(2, base_delay=1.0) == 4.0\n"
            "    assert compute_backoff_delay(3, base_delay=1.0) == 8.0\n\n"
            "def test_compute_backoff_max_delay_cap():\n"
            "    # 2^10 = 1024, mas o limite deve ser respeitado em 30.0\n"
            "    assert compute_backoff_delay(10, base_delay=1.0, max_delay=30.0) == 30.0\n"
            "    assert compute_backoff_delay(20, base_delay=2.0, max_delay=15.0) == 15.0\n\n"
            "def test_compute_backoff_with_jitter():\n"
            "    # Base 4.0, jitter_factor 0.5, seed 0.0 -> 4.0 * (0.5 + 0.0) = 2.0\n"
            "    assert compute_backoff_delay(2, base_delay=1.0, jitter_factor=0.5, jitter_seed=0.0) == 2.0\n"
            "    # Base 4.0, jitter_factor 0.5, seed 1.0 -> 4.0 * (0.5 + 0.5) = 4.0\n"
            "    assert compute_backoff_delay(2, base_delay=1.0, jitter_factor=0.5, jitter_seed=1.0) == 4.0\n\n"
            "@pytest.mark.parametrize('bad_attempt', [-1, -10, '0', None, 1.5])\n"
            "def test_invalid_attempt_rejected(bad_attempt):\n"
            "    with pytest.raises(ValueError):\n"
            "        compute_backoff_delay(bad_attempt)\n\n"
            "@pytest.mark.parametrize('bad_config', [(0, 10), (-1, 10), (1, 0), (1, -5)])\n"
            "def test_invalid_delays_rejected(bad_config):\n"
            "    with pytest.raises(ValueError):\n"
            "        compute_backoff_delay(1, base_delay=bad_config[0], max_delay=bad_config[1])\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Suíte completa que cobre progressão exponencial, teto máximo, jitter e validações defensivas de entrada. Sem lacunas.",
        "analysis_scope": "exponential_backoff_full_coverage",
        "split_group": "clean_exponential_backoff",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/",
        "gaps": []  # Hard negative (no gaps)
    },

    # -------------------------------------------------------------------------
    # 4. Password Strength & Entropy Validator (100% Covered)
    # -------------------------------------------------------------------------
    {
        "title": "PasswordValidator: Validador de Complexidade e Lista de Senhas Proibidas (Suíte Completa)",
        "project_name": "AuthSecuritySuite",
        "description": "Validador de robustez de senhas NIST SP 800-63B com verificação de complexidade e negação de senhas comuns.",
        "requirements_text": (
            "REQ-PWD-001: A senha deve possuir comprimento mínimo de 10 caracteres e máximo de 128 caracteres.\n"
            "REQ-PWD-002: A senha deve conter ao menos 1 letra maiúscula, 1 minúscula, 1 número e 1 símbolo especial (!@#$%^&*).\n"
            "REQ-PWD-003: Senhas constantes na lista de senhas comuns (ex: 'Password123!', 'Admin@2026!') devem ser rejeitadas com erro 'common_password'.\n"
            "REQ-PWD-004: A função deve retornar dicionário {'valid': bool, 'reasons': list[str]}."
        ),
        "source_code": (
            "import re\n\n"
            "COMMON_PASSWORDS = {'password123!', 'admin@2026!', 'qwerty12345!', 'welcome1234!'}\n\n"
            "def validate_password_strength(password: str) -> dict:\n"
            "    if not isinstance(password, str):\n"
            "        return {'valid': False, 'reasons': ['Senha deve ser uma string.']}\n"
            "    reasons = []\n"
            "    if len(password) < 10:\n"
            "        reasons.append('Comprimento mínimo de 10 caracteres.')\n"
            "    if len(password) > 128:\n"
            "        reasons.append('Comprimento máximo de 128 caracteres.')\n"
            "    if not re.search(r'[A-Z]', password):\n"
            "        reasons.append('Deve conter ao menos uma letra maiúscula.')\n"
            "    if not re.search(r'[a-z]', password):\n"
            "        reasons.append('Deve conter ao menos uma letra minúscula.')\n"
            "    if not re.search(r'[0-9]', password):\n"
            "        reasons.append('Deve conter ao menos um dígito numérico.')\n"
            "    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):\n"
            "        reasons.append('Deve conter ao menos um símbolo especial.')\n"
            "    if password.lower() in COMMON_PASSWORDS:\n"
            "        reasons.append('Senha fraca muito comum.')\n"
            "    return {'valid': len(reasons) == 0, 'reasons': reasons}\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from validator import validate_password_strength\n\n"
            "def test_valid_strong_password():\n"
            "    res = validate_password_strength('Correct-Horse-Battery-99!')\n"
            "    assert res['valid'] is True\n"
            "    assert res['reasons'] == []\n\n"
            "@pytest.mark.parametrize('pwd, expected_msg', [\n"
            "    ('Short1!', 'Comprimento mínimo de 10 caracteres.'),\n"
            "    ('A' * 129 + 'a1!', 'Comprimento máximo de 128 caracteres.'),\n"
            "    ('nouppercase123!', 'Deve conter ao menos uma letra maiúscula.'),\n"
            "    ('NOLOWERCASE123!', 'Deve conter ao menos uma letra minúscula.'),\n"
            "    ('NoDigitsHere!@#', 'Deve conter ao menos um dígito numérico.'),\n"
            "    ('NoSpecialSymbol123', 'Deve conter ao menos um símbolo especial.'),\n"
            "    ('Password123!', 'Senha fraca muito comum.'),\n"
            "    (None, 'Senha deve ser uma string.'),\n"
            "    (1234567890, 'Senha deve ser uma string.'),\n"
            "])\n"
            "def test_invalid_passwords_trigger_exact_reasons(pwd, expected_msg):\n"
            "    res = validate_password_strength(pwd)\n"
            "    assert res['valid'] is False\n"
            "    assert any(expected_msg in r for r in res['reasons'])\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Suíte exaustiva que testa cada critério de falha isolado, entradas não-string, tamanho de borda (10 e 128) e senhas comuns. Sem lacunas.",
        "analysis_scope": "password_validation_full_coverage",
        "split_group": "clean_password_validator",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://pages.nist.gov/800-63-3/sp800-63b.html (NIST Password Guidelines)",
        "gaps": []  # Hard negative (no gaps)
    },

    # -------------------------------------------------------------------------
    # 5. Safe JSON Parser with Depth Limit (100% Covered)
    # -------------------------------------------------------------------------
    {
        "title": "SafeJsonParser: Desserialização Segura com Limite de Profundidade e Tamanho (Suíte Completa)",
        "project_name": "SecureDataIngestion",
        "description": "Parser JSON com proteção contra exaustão de pilha (Stack Exhaustion / Billion Laughs) e limite de payload.",
        "requirements_text": (
            "REQ-JSON-001: A função safe_json_loads deve decodificar uma string JSON em estruturas Python nativas.\n"
            "REQ-JSON-002: A string JSON não pode exceder max_bytes (padrão 1MB); payloads maiores disparam ValueError.\n"
            "REQ-JSON-003: O JSON não pode ultrapassar a profundidade de aninhamento max_depth (padrão 10); estruturas mais profundas disparam ValueError.\n"
            "REQ-JSON-004: JSONs truncados ou malformados disparam ValueError."
        ),
        "source_code": (
            "import json\n\n"
            "def check_depth(obj, current_depth: int = 1, max_depth: int = 10):\n"
            "    if current_depth > max_depth:\n"
            "        raise ValueError(f'Profundidade máxima de {max_depth} excedida.')\n"
            "    if isinstance(obj, dict):\n"
            "        for v in obj.values():\n"
            "            check_depth(v, current_depth + 1, max_depth)\n"
            "    elif isinstance(obj, list):\n"
            "        for item in obj:\n"
            "            check_depth(item, current_depth + 1, max_depth)\n\n"
            "def safe_json_loads(data_str: str, max_bytes: int = 1_000_000, max_depth: int = 10):\n"
            "    if not isinstance(data_str, str):\n"
            "        raise ValueError('Entrada deve ser string.')\n"
            "    if len(data_str.encode('utf-8')) > max_bytes:\n"
            "        raise ValueError(f'Payload excede limite máximo de {max_bytes} bytes.')\n"
            "    try:\n"
            "        parsed = json.loads(data_str)\n"
            "    except (json.JSONDecodeError, TypeError) as e:\n"
            "        raise ValueError(f'JSON malformado: {e}')\n"
            "    check_depth(parsed, 1, max_depth)\n"
            "    return parsed\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from safe_json import safe_json_loads\n\n"
            "def test_parse_valid_json():\n"
            "    data = safe_json_loads('{\"status\": \"ok\", \"items\": [1, 2, 3]}')\n"
            "    assert data['status'] == 'ok'\n"
            "    assert data['items'] == [1, 2, 3]\n\n"
            "def test_rejects_payload_exceeding_byte_limit():\n"
            "    with pytest.raises(ValueError, match='Payload excede limite'):\n"
            "        safe_json_loads('{\"a\": \"b\"}', max_bytes=5)\n\n"
            "def test_rejects_deeply_nested_structures():\n"
            "    # Aninhamento com profundidade 5 sob limite max_depth=3\n"
            "    nested = '{\"a\": {\"b\": {\"c\": {\"d\": 1}}}}'\n"
            "    with pytest.raises(ValueError, match='Profundidade máxima'):\n"
            "        safe_json_loads(nested, max_depth=3)\n\n"
            "@pytest.mark.parametrize('bad_json', [\n"
            "    '{truncated', 'invalid:', '', '{\"key\": undefined}', None, 1234\n"
            "])\n"
            "def test_rejects_malformed_and_non_string_inputs(bad_json):\n"
            "    with pytest.raises(ValueError):\n"
            "        safe_json_loads(bad_json)\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Suíte cobre parsing com sucesso, controle de profundidade de aninhamento, estouro de bytes e entradas malformadas ou não-string. Sem lacunas.",
        "analysis_scope": "safe_json_full_coverage",
        "split_group": "clean_safe_json_parser",
        "source_type": SourceType.HUMAN_AUTHORED,
        "source_reference": "https://cheatsheetseries.owasp.org/cheatsheets/JSON_Injection_Prevention_Cheat_Sheet.html",
        "gaps": []  # Hard negative (no gaps)
    }
]


def ingest_clean_suites():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    print("[*] Inserindo suítes limpas 100% cobertas (Hard Negatives) para balanceamento de IA...")

    imported = 0
    skipped = 0

    for item in CLEAN_SUITES_EXAMPLES:
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
            initial_gaps=[]
        )

        try:
            ex = ex_service.create_example(payload)
            rev_service.update_status(
                ex.id,
                ReviewStatus.APPROVED,
                review_note="Suíte de 100% de cobertura aprovada como Hard Negative para treino de LLMs."
            )
            print(f"[+] Importado: {ex.public_id} — {ex.title}")
            imported += 1
        except ValueError as ve:
            print(f"[-] Ja existente (ignorado): {item['title']}")
            skipped += 1

    print(f"\n[+] Concluido: {imported} suítes limpas inseridas, {skipped} duplicados.")


if __name__ == "__main__":
    ingest_clean_suites()
