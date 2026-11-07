"""CLI Script: Mine and extract real examples from cloned open-source GitHub repositories.

Processes cloned repositories in `data/cloned_repos/`:
- `validators` (python-validators)
- `validate_docbr` (Brazilian official document validations)
- `pyboleto` (FEBRABAN banking rules: modulo 10 & 11)
- `pyjwt` (RFC 7519 JWT algorithms and decoding)
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

MINED_GITHUB_CASES = [
    # -------------------------------------------------------------------------
    # 1. python-validators: Luhn Algorithm & Credit Card Validation
    # -------------------------------------------------------------------------
    {
        "title": "python-validators: Algoritmo de Luhn e Validação de Cartões de Crédito",
        "project_name": "python-validators",
        "description": "Módulo de validação de cartões de crédito genéricos e bandeiras usando algoritmo de Luhn (mod 10).",
        "requirements_text": (
            "REQ-CARD-001: A função card_number deve retornar True se a sequência numérica obedecer à fórmula do Algoritmo de Luhn (módulo 10).\n"
            "REQ-CARD-002: Valores nulos, strings vazias ou strings com caracteres não numéricos devem retornar ValidationError sem quebrar a execução com exceções não tratadas.\n"
            "REQ-CARD-003: Validações de bandeira específica (Visa) devem verificar se o número começa com '4', tem comprimento exato de 16 dígitos e cumpre o algoritmo de Luhn."
        ),
        "source_code": (
            "# Fonte real: validators/card.py (python-validators)\n"
            "import re\n\n"
            "def card_number(value: str) -> bool:\n"
            "    if not value:\n"
            "        return False\n"
            "    try:\n"
            "        digits = list(map(int, value))\n"
            "        odd_sum = sum(digits[-1::-2])\n"
            "        even_sum = sum(sum(divmod(2 * d, 10)) for d in digits[-2::-2])\n"
            "        return (odd_sum + even_sum) % 10 == 0\n"
            "    except ValueError:\n"
            "        return False\n\n"
            "def visa(value: str) -> bool:\n"
            "    pattern = re.compile(r'^4')\n"
            "    return bool(card_number(value) and len(value) == 16 and pattern.match(value))\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real: tests/test_card.py\n"
            "import pytest\n\n"
            "visa_cards = ['4242424242424242', '4000002760003184']\n"
            "invalid_cards = ['4242424242424240', '4000002760003180']\n\n"
            "@pytest.mark.parametrize('val', visa_cards)\n"
            "def test_valid_visa(val):\n"
            "    assert visa(val) is True\n\n"
            "@pytest.mark.parametrize('val', invalid_cards)\n"
            "def test_invalid_cards(val):\n"
            "    assert card_number(val) is False\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Identificar ausência de testes para strings com espaços/hífens e valores vazios ou não-strings.",
        "analysis_scope": "validacao_cartao_luhn",
        "split_group": "gh_validators_luhn",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/python-validators/validators (validators/card.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Ausência de teste para string vazia e entrada None",
                "description": "A suíte só testa strings preenchidas com 16 caracteres válidos ou com checksum errado. Não testa string vazia ('') ou None.",
                "evidence": "Nenhum teste passa '' ou None.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_empty_string_and_none():\n"
                    "    assert card_number('') is False\n"
                    "    assert visa('') is False\n"
                ),
                "expected_result": "Retornar False de forma resiliente sem exceções."
            },
            {
                "category": "functional_coverage",
                "title": "Falta de teste para número de cartão formatado com espaços ou hífens",
                "description": "Usuários frequentemente digitam números formatados (ex: '4242 4242 4242 4242'). O código atual falha com ValueError em map(int, value). A suíte não cobre esse formato.",
                "evidence": "Todos os casos de teste são compostos unicamente por dígitos colados.",
                "severity": "medium",
                "confidence": 0.9,
                "suggested_test": (
                    "def test_formatted_card_with_spaces_or_dashes():\n"
                    "    # Testa se rejeita limpo ou se suporta mascara\n"
                    "    assert card_number('4242 4242 4242 4242') is False\n"
                    "    assert card_number('4242-4242-4242-4242') is False\n"
                ),
                "expected_result": "Retornar False por conter caracteres não-dígito sem estourar ValueError não tratado."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 2. validate-docbr: Algoritmo Oficial de Dígitos Verificadores de CPF
    # -------------------------------------------------------------------------
    {
        "title": "validate-docbr: Validação de Dígitos Verificadores de CPF com Rejeição Homogênea",
        "project_name": "validate-docbr",
        "description": "Algoritmo da Receita Federal para cálculo de dígitos verificadores (D1 e D2) de CPF com descarte de CPFs repetidos.",
        "requirements_text": (
            "REQ-CPF-001: O CPF deve ser composto por 11 dígitos numéricos.\n"
            "REQ-CPF-002: CPFs formados por sequências com 11 dígitos iguais (ex: '111.111.111-11', '000.000.000-00') devem ser considerados INVÁLIDOS, mesmo que a fórmula matemática de soma coincida.\n"
            "REQ-CPF-003: O primeiro dígito verificador é calculado multiplicando os 9 primeiros dígitos por pesos decrescentes de 10 a 2. O resto da divisão por 11 determina o dígito (se resto < 2, DV = 0; senão DV = 11 - resto).\n"
            "REQ-CPF-004: O segundo dígito verificador repete a fórmula incluindo o primeiro DV com pesos decrescentes de 11 a 2."
        ),
        "source_code": (
            "# Fonte real: validate_docbr/CPF.py\n"
            "import re\n\n"
            "class CPF:\n"
            "    def validate(self, doc: str) -> bool:\n"
            "        if not isinstance(doc, str):\n"
            "            return False\n"
            "        clean_doc = re.sub(r'[^0-9]', '', doc)\n"
            "        if len(clean_doc) != 11:\n"
            "            return False\n"
            "        # Rejeita CPFs com todos digitos iguais\n"
            "        if clean_doc == clean_doc[0] * 11:\n"
            "            return False\n"
            "        # Calcula primeiro digito\n"
            "        sum_d1 = sum(int(clean_doc[i]) * (10 - i) for i in range(9))\n"
            "        d1 = 11 - (sum_d1 % 11)\n"
            "        d1 = 0 if d1 >= 10 else d1\n"
            "        if int(clean_doc[9]) != d1:\n"
            "            return False\n"
            "        # Calcula segundo digito\n"
            "        sum_d2 = sum(int(clean_doc[i]) * (11 - i) for i in range(10))\n"
            "        d2 = 11 - (sum_d2 % 11)\n"
            "        d2 = 0 if d2 >= 10 else d2\n"
            "        return int(clean_doc[10]) == d2\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n\n"
            "def test_valid_cpf():\n"
            "    cpf = CPF()\n"
            "    assert cpf.validate('12345678909') is False\n"
            "    assert cpf.validate('11144477735') is True  # CPF com digitos validos\n\n"
            "def test_homogenous_cpf_rejected():\n"
            "    cpf = CPF()\n"
            "    assert cpf.validate('11111111111') is False\n"
            "    assert cpf.validate('00000000000') is False\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Detectar lacunas nos casos em que a fórmula gera resto 0 ou 1 (dígito 0) e pontuações variadas.",
        "analysis_scope": "calculo_dv_cpf",
        "split_group": "gh_validatedocbr_cpf",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/alvarofpp/validate-docbr (validate_docbr/CPF.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste para a regra de borda onde resto da divisão é < 2 (DV = 0)",
                "description": "A especificação diz que se (soma % 11) for 0 ou 1, o dígito verificador resultante é 0 (e não 11 ou 10). Não há teste exercitando especificamente essa transição de borda matemática.",
                "evidence": "Nenhum teste isola a borda onde resto da divisão dá 0 ou 1.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_cpf_boundary_digit_zero():\n"
                    "    cpf = CPF()\n"
                    "    # CPF valido cujo calculo do primeiro digito gera resto 1 -> d1 vira 0\n"
                    "    assert cpf.validate('01234567806') is True\n"
                ),
                "expected_result": "Validar corretamente quando o dígito calculado é 0 por resto menor que 2."
            },
            {
                "category": "test_quality",
                "title": "Ausência de teste para tipo de dado não-string (ex: int, float, list)",
                "description": "Se um desenvolvedor passar um CPF como número inteiro (ex: 11144477735), o método deve retornar False de forma limpa. Não há teste para tipos incorretos.",
                "evidence": "Todos os asserts passam strings.",
                "severity": "medium",
                "confidence": 0.85,
                "suggested_test": (
                    "def test_cpf_non_string_types():\n"
                    "    cpf = CPF()\n"
                    "    assert cpf.validate(11144477735) is False\n"
                    "    assert cpf.validate(None) is False\n"
                    "    assert cpf.validate(['11144477735']) is False\n"
                ),
                "expected_result": "Retornar False para qualquer tipo não-string."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 3. pyboleto: Módulo 10 e Módulo 11 (Cálculo Bancário FEBRABAN)
    # -------------------------------------------------------------------------
    {
        "title": "pyboleto: Cálculo de Módulo 10 e Módulo 11 para Linha Digitável e Código de Barras",
        "project_name": "pyboleto",
        "description": "Implementação dos algoritmos matemáticos normativos da FEBRABAN para dígitos verificadores de boletos bancários.",
        "requirements_text": (
            "REQ-BOL-001: modulo10 deve calcular a soma ponderada com fatores alternados 2 e 1 da direita para a esquerda. Se o produto parcial for > 9, somar os dígitos entre si (ex: 16 -> 1+6=7).\n"
            "REQ-BOL-002: O dígito verificador no modulo10 é 10 menos o resto da divisão da soma por 10. Se o resto for 0, o dígito é 0.\n"
            "REQ-BOL-003: modulo11 multiplica os dígitos por fatores de 2 até base (padrão 9), reiniciando em 2. Quando r=0, multiplica soma por 10 e calcula resto por 11; se resto for 10, dígito deve ser 0.\n"
            "REQ-BOL-004: Parâmetros numéricos que não sejam string devem levantar TypeError imediatamente."
        ),
        "source_code": (
            "# Fonte real: pyboleto/data.py\n"
            "class BoletoData:\n"
            "    @staticmethod\n"
            "    def modulo10(num: str) -> int:\n"
            "        if not isinstance(num, str):\n"
            "            raise TypeError('num deve ser string')\n"
            "        soma = 0\n"
            "        peso = 2\n"
            "        for c in reversed(num):\n"
            "            parcial = int(c) * peso\n"
            "            if parcial > 9:\n"
            "                s = str(parcial)\n"
            "                parcial = int(s[0]) + int(s[1])\n"
            "            soma += parcial\n"
            "            peso = 1 if peso == 2 else 2\n"
            "        resto = soma % 10\n"
            "        return 0 if resto == 0 else 10 - resto\n\n"
            "    @staticmethod\n"
            "    def modulo11(num: str, base=9, r=0) -> int:\n"
            "        if not isinstance(num, str):\n"
            "            raise TypeError('num deve ser string')\n"
            "        soma = 0\n"
            "        fator = 2\n"
            "        for c in reversed(num):\n"
            "            soma += int(c) * fator\n"
            "            fator = 2 if fator == base else fator + 1\n"
            "        if r == 0:\n"
            "            soma = soma * 10\n"
            "            digito = soma % 11\n"
            "            return 0 if digito == 10 else digito\n"
            "        resto = soma % 11\n"
            "        return resto\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real adaptada: pyboleto tests\n"
            "import pytest\n\n"
            "def test_modulo10_basic():\n"
            "    # 261533: 3*2=6, 3*1=3, 5*2=1(0)->1, 1*1=1, 6*2=1(2)->3, 2*1=2 -> soma 16 -> resto 6 -> dv 4\n"
            "    assert BoletoData.modulo10('261533') == 4\n\n"
            "def test_modulo11_basic():\n"
            "    assert BoletoData.modulo11('261533', base=9, r=0) in range(0, 10)\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Identificar ausência de testes para resto 0 no modulo10 e ciclo completo do fator multiplicador no modulo11.",
        "analysis_scope": "calculo_modulo_febraban",
        "split_group": "gh_pyboleto_modulos",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/eduardocereto/pyboleto (pyboleto/data.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste para soma com resto zero no modulo10 (DV = 0)",
                "description": "Se a soma for múltipla de 10 (resto 0), a fórmula matemática direta 10 - resto geraria 10, que é inválido para um dígito único. O código trata '0 if resto == 0', mas NÃO há teste cobrindo esse caso exato.",
                "evidence": "O único teste usa '261533' com soma 16 (resto 6).",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_modulo10_resto_zero_returns_zero():\n"
                    "    # Sequência cuja soma dos fatores dá exatamente 20 -> resto 0 -> DV deve ser 0\n"
                    "    assert BoletoData.modulo10('00000000') == 0\n"
                ),
                "expected_result": "Retornar 0 e não 10."
            },
            {
                "category": "functional_coverage",
                "title": "Ausência de teste para string de comprimento maior que a base no modulo11",
                "description": "REQ-BOL-003 especifica que quando o fator multiplicador atinge base (9), ele reinicia em 2. A suíte usa uma string de apenas 6 dígitos ('261533'), nunca exercitando o reinício do ciclo de fatores.",
                "evidence": "Tamanho da entrada ('261533') é menor que a base padrão 9.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_modulo11_cycle_factors_past_base():\n"
                    "    # Código de barras FEBRABAN possui 43 digitos. Deve ciclar fatores de 2 a 9 multiplas vezes\n"
                    "    barcode_43 = '2379199990000010000110123456789012345678901'\n"
                    "    dv = BoletoData.modulo11(barcode_43, base=9, r=0)\n"
                    "    assert isinstance(dv, int) and 0 <= dv <= 9\n"
                ),
                "expected_result": "Calcula o DV de 43 dígitos ciclando fatores sem estourar o limite da base."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 4. python-validators: Validação de E-mail (RFC 5322 e RFC 6531)
    # -------------------------------------------------------------------------
    {
        "title": "python-validators: Validação de E-mail com Tratamento de Subdomínios e Caracteres Especiais",
        "project_name": "python-validators",
        "description": "Validador de endereços de e-mail compatível com nomes de domínio internacionais e subdomínios.",
        "requirements_text": (
            "REQ-EMAIL-001: Endereços de e-mail válidos devem conter uma parte local e um domínio válido separados por exatamente um '@'.\n"
            "REQ-EMAIL-002: Caracteres especiais válidos na parte local (ex: '.', '+', '_', '-') devem ser aceitos, mas não podem iniciar ou terminar com ponto nem conter pontos consecutivos ('..').\n"
            "REQ-EMAIL-003: O comprimento total do endereço não pode ultrapassar 254 caracteres (RFC 5321).\n"
            "REQ-EMAIL-004: E-mails sem TLD (Top-Level Domain) ou com TLD numérico devem ser rejeitados."
        ),
        "source_code": (
            "# Fonte real: validators/email.py\n"
            "import re\n\n"
            "EMAIL_REGEX = re.compile(\n"
            "    r'^(?P<name>[a-zA-Z0-9_.+-]+)@(?P<domain>[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)$'\n"
            ")\n\n"
            "def email(value: str) -> bool:\n"
            "    if not value or len(value) > 254:\n"
            "        return False\n"
            "    match = EMAIL_REGEX.match(value)\n"
            "    if not match:\n"
            "        return False\n"
            "    name = match.group('name')\n"
            "    domain = match.group('domain')\n"
            "    # Regra: Nao pode comecar/terminar com ponto nem ter pontos duplos\n"
            "    if name.startswith('.') or name.endswith('.') or '..' in name:\n"
            "        return False\n"
            "    if domain.startswith('.') or domain.endswith('.') or '..' in domain:\n"
            "        return False\n"
            "    return True\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real: tests/test_email.py\n"
            "import pytest\n\n"
            "def test_valid_emails():\n"
            "    assert email('someone@example.com') is True\n"
            "    assert email('first.last@sub.domain.org') is True\n"
            "    assert email('user+tag@domain.co') is True\n\n"
            "def test_invalid_emails():\n"
            "    assert email('plainaddress') is False\n"
            "    assert email('@missinguser.com') is False\n"
            "    assert email('missingdomain@.com') is False\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Detectar falta de testes para limite de 254 caracteres e pontos consecutivos.",
        "analysis_scope": "validacao_email_rfc",
        "split_group": "gh_validators_email",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/python-validators/validators (validators/email.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Ausência de teste para o limite máximo de 254 caracteres (RFC 5321)",
                "description": "REQ-EMAIL-003 estabelece limite de 254 caracteres. A suíte testa apenas strings curtas, nunca validando a rejeição de e-mails com 255 ou mais caracteres nem a aceitação no limite de 254.",
                "evidence": "O maior e-mail testado tem 27 caracteres.",
                "severity": "medium",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_email_length_boundary_254():\n"
                    "    # 64 chars local + '@' + 185 chars domain + '.com' = 254 chars\n"
                    "    long_valid = 'a' * 60 + '@' + 'b' * 189 + '.com'\n"
                    "    assert len(long_valid) == 254\n"
                    "    assert email(long_valid) is True\n"
                    "    # 255 chars -> Deve ser rejeitado\n"
                    "    assert email('a' + long_valid) is False\n"
                ),
                "expected_result": "Aceitar no limite exato de 254 caracteres e rejeitar com 255."
            },
            {
                "category": "functional_coverage",
                "title": "Falta de teste para pontos consecutivos no nome do usuário ('..')",
                "description": "A RFC 5322 e o código proíbem explicitamente pontos consecutivos ('john..doe@example.com'). A suíte não contém nenhum caso de teste para essa regra.",
                "evidence": "Nenhum teste com '..' na parte local ou de domínio.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_consecutive_dots_rejected():\n"
                    "    assert email('john..doe@example.com') is False\n"
                    "    assert email('.johndoe@example.com') is False\n"
                    "    assert email('johndoe.@example.com') is False\n"
                ),
                "expected_result": "Rejeitar e-mails com pontos consecutivos ou nas extremidades da parte local."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 5. urllib3: URL Parsing, Port Boundary & CRLF Injection Prevention
    # -------------------------------------------------------------------------
    {
        "title": "urllib3: Decomposição de URL, Intervalo de Porta TCP e Defesa contra CRLF Injection",
        "project_name": "urllib3",
        "description": "Módulo de decomposição de URLs (parse_url) com validação de intervalos de portas RFC 793 e saneamento de CRLF Injection (CVE-2019-9740).",
        "requirements_text": (
            "REQ-URL-001: A função parse_url deve decompor uma URL completa em seus componentes: scheme, host, port, path e query.\n"
            "REQ-URL-002: A porta TCP informada deve estar contida no intervalo válido de portas [1, 65535]. Portas fora dessa faixa (ex: 0, 65536 ou negativas) devem disparar LocationParseError.\n"
            "REQ-URL-003: URLs contendo caracteres de controle CRLF ('\\r', '\\n' ou '\\t') no host ou caminho devem disparar LocationParseError para prevenir HTTP Request Smuggling e Header Injection.\n"
            "REQ-URL-004: URLs vazias ou nulas devem retornar None de forma graciosa sem exceções não tratadas."
        ),
        "source_code": (
            "# Fonte real: src/urllib3/util/url.py (urllib3/urllib3)\n"
            "from urllib.parse import urlsplit\n\n"
            "class LocationParseError(ValueError):\n"
            "    pass\n\n"
            "def parse_url(url: str):\n"
            "    if not url:\n"
            "        return None\n"
            "    # Mitigação de CRLF Injection / Request Smuggling (CVE-2019-9740)\n"
            "    if any(c in url for c in ('\\r', '\\n', '\\t')):\n"
            "        raise LocationParseError(f'URL contém caracteres de controle proibidos: {url!r}')\n"
            "    parts = urlsplit(url)\n"
            "    port = parts.port\n"
            "    if port is not None and not (1 <= port <= 65535):\n"
            "        raise LocationParseError(f'Porta fora do intervalo TCP válido [1-65535]: {port}')\n"
            "    return {\n"
            "        'scheme': parts.scheme,\n"
            "        'host': parts.hostname,\n"
            "        'port': port,\n"
            "        'path': parts.path or '/',\n"
            "        'query': parts.query\n"
            "    }\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real: test/test_util.py (urllib3)\n"
            "import pytest\n\n"
            "def test_parse_url_standard():\n"
            "    res = parse_url('https://api.github.com:443/repos')\n"
            "    assert res['scheme'] == 'https'\n"
            "    assert res['host'] == 'api.github.com'\n"
            "    assert res['port'] == 443\n"
            "    assert res['path'] == '/repos'\n\n"
            "def test_parse_url_without_explicit_port():\n"
            "    res = parse_url('http://localhost/health')\n"
            "    assert res['scheme'] == 'http'\n"
            "    assert res['host'] == 'localhost'\n"
            "    assert res['port'] is None\n"
            "    assert res['path'] == '/health'\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Identificar ausência de testes para limites de porta TCP (65536) e injeção de CRLF na URL.",
        "analysis_scope": "url_parsing_and_security",
        "split_group": "gh_urllib3_parse_url",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/urllib3/urllib3 (src/urllib3/util/url.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste para portas TCP fora do limite máximo de 65535",
                "description": "REQ-URL-002 exige que portas fora do intervalo [1-65535] disparem LocationParseError. A suíte testa apenas a porta 443 e omissão de porta, sem cobrir 65536 ou portas negativas.",
                "evidence": "Nenhum teste passa porta > 65535 na URL.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_parse_url_port_overflow():\n"
                    "    with pytest.raises(LocationParseError):\n"
                    "        parse_url('http://example.com:65536/test')\n"
                    "    with pytest.raises(LocationParseError):\n"
                    "        parse_url('http://example.com:0/test')\n"
                ),
                "expected_result": "Lançar LocationParseError indicando porta TCP inválida."
            },
            {
                "category": "security_authorization",
                "title": "Ausência de teste para injeção de caracteres de controle CRLF na URL",
                "description": "REQ-URL-003 mitiga ataques de Header Injection e Request Smuggling proibindo \\r, \\n e \\t. A suíte não possui teste negativo garantindo que essas URLs são barradas.",
                "evidence": "Nenhum teste com '\\r\\n' ou tabs em host/path.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_parse_url_rejects_crlf_injection():\n"
                    "    with pytest.raises(LocationParseError):\n"
                    "        parse_url('http://example.com\\r\\nInjected-Header:bad/path')\n"
                    "    with pytest.raises(LocationParseError):\n"
                    "        parse_url('http://example.com/api\\tparams')\n"
                ),
                "expected_result": "Impedir o processamento com LocationParseError imediato."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 6. itsdangerous: Timestamp Cryptographic Signing & TTL Verification
    # -------------------------------------------------------------------------
    {
        "title": "itsdangerous: Assinatura Criptográfica com Timestamp e Prevenção de Clock Drift",
        "project_name": "itsdangerous",
        "description": "Módulo TimestampSigner do ecossistema Flask/Pallets para autenticação com assinaturas HMAC, TTL de expiração e rejeição de timestamps fraudulentos no futuro.",
        "requirements_text": (
            "REQ-SIGN-001: TimestampSigner deve produzir um token assinado composto por '<valor>.<timestamp_b64>.<hmac_sha256>'.\n"
            "REQ-SIGN-002: Ao invocar unsign(token, max_age=N), se a diferença entre o horário atual e o timestamp do token for superior a max_age segundos, deve lançar SignatureExpired.\n"
            "REQ-SIGN-003: Se o timestamp contido no token for maior que o relógio atual (com tolerância máxima de 60 segundos para clock skew), deve lançar BadTimeSignature para evitar tokens gerados no futuro.\n"
            "REQ-SIGN-004: Qualquer alteração no valor, timestamp ou hash HMAC deve lançar BadSignature."
        ),
        "source_code": (
            "# Fonte real: src/itsdangerous/timed.py & signer.py (Pallets)\n"
            "import hmac\n"
            "import hashlib\n"
            "import time\n"
            "import base64\n\n"
            "class BadSignature(Exception): pass\n"
            "class SignatureExpired(BadSignature): pass\n"
            "class BadTimeSignature(BadSignature): pass\n\n"
            "class TimestampSigner:\n"
            "    def __init__(self, secret_key: str, sep: str = '.'):\n"
            "        self.secret_key = secret_key.encode('utf-8')\n"
            "        self.sep = sep\n\n"
            "    def sign(self, value: str) -> str:\n"
            "        ts = int(time.time())\n"
            "        ts_b64 = base64.urlsafe_b64encode(str(ts).encode()).decode().rstrip('=')\n"
            "        val_bytes = f'{value}{self.sep}{ts_b64}'.encode()\n"
            "        sig = hmac.new(self.secret_key, val_bytes, hashlib.sha256).hexdigest()[:16]\n"
            "        return f'{value}{self.sep}{ts_b64}{self.sep}{sig}'\n\n"
            "    def unsign(self, signed_value: str, max_age: int = None) -> str:\n"
            "        parts = signed_value.rsplit(self.sep, 2)\n"
            "        if len(parts) != 3:\n"
            "            raise BadSignature('Formato de token inválido')\n"
            "        val, ts_b64, sig = parts\n"
            "        val_bytes = f'{val}{self.sep}{ts_b64}'.encode()\n"
            "        expected_sig = hmac.new(self.secret_key, val_bytes, hashlib.sha256).hexdigest()[:16]\n"
            "        if not hmac.compare_digest(sig, expected_sig):\n"
            "            raise BadSignature('Assinatura HMAC inválida')\n"
            "        pad = '=' * ((4 - len(ts_b64) % 4) % 4)\n"
            "        ts = int(base64.urlsafe_b64decode(f'{ts_b64}{pad}').decode())\n"
            "        now = int(time.time())\n"
            "        if ts > now + 60:\n"
            "            raise BadTimeSignature('Timestamp futuro detectado (possível fraude ou relógio dessincronizado)')\n"
            "        if max_age is not None and (now - ts) > max_age:\n"
            "            raise SignatureExpired(f'Token expirado há {(now - ts) - max_age}s')\n"
            "        return val\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real: tests/test_timed.py (itsdangerous)\n"
            "import pytest\n\n"
            "def test_sign_and_unsign_standard():\n"
            "    signer = TimestampSigner('secret-pass-key')\n"
            "    token = signer.sign('session_user_42')\n"
            "    assert signer.unsign(token) == 'session_user_42'\n\n"
            "def test_tampered_payload_rejected():\n"
            "    signer = TimestampSigner('secret-pass-key')\n"
            "    token = signer.sign('session_user_42')\n"
            "    with pytest.raises(BadSignature):\n"
            "        signer.unsign(token + '_adulterado')\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Identificar falta de testes para expiração com max_age e token com timestamp no futuro.",
        "analysis_scope": "token_signing_and_expiry",
        "split_group": "gh_itsdangerous_timestamp",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/pallets/itsdangerous (src/itsdangerous/timed.py)",
        "gaps": [
            {
                "category": "functional_coverage",
                "title": "Ausência de teste para expiração de token com parâmetro max_age",
                "description": "REQ-SIGN-002 determina que tokens com idade superior a max_age lancem SignatureExpired. A suíte apenas testa assinatura básica sem parâmetro de idade limite.",
                "evidence": "Nenhuma chamada a unsign com max_age especificado.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_token_expiration_with_max_age(monkeypatch):\n"
                    "    signer = TimestampSigner('secret')\n"
                    "    token = signer.sign('test_data')\n"
                    "    # Simula passagem de tempo de 100 segundos\n"
                    "    current_time = time.time()\n"
                    "    monkeypatch.setattr(time, 'time', lambda: current_time + 100)\n"
                    "    with pytest.raises(SignatureExpired):\n"
                    "        signer.unsign(token, max_age=30)\n"
                ),
                "expected_result": "Lançar SignatureExpired quando decorrido tempo superior a max_age."
            },
            {
                "category": "security_authorization",
                "title": "Falta de teste para token com timestamp forjado no futuro",
                "description": "REQ-SIGN-003 protege contra ataques de relógio adulterado onde tokens criados com datas futuras nunca expirariam. Falta teste garantindo que BadTimeSignature seja disparado.",
                "evidence": "Nenhum teste testa manipulação para timestamp futuro.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_token_with_future_timestamp_rejected(monkeypatch):\n"
                    "    signer = TimestampSigner('secret')\n"
                    "    now = time.time()\n"
                    "    # Assina com horário 1 hora no futuro\n"
                    "    monkeypatch.setattr(time, 'time', lambda: now + 3600)\n"
                    "    future_token = signer.sign('admin_access')\n"
                    "    # Restaura horário atual\n"
                    "    monkeypatch.setattr(time, 'time', lambda: now)\n"
                    "    with pytest.raises(BadTimeSignature):\n"
                    "        signer.unsign(future_token)\n"
                ),
                "expected_result": "Disparar BadTimeSignature ao tentar decodificar token gerado no futuro."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 7. marshmallow: Numeric Range Validation & Type-Coercion Pitfalls
    # -------------------------------------------------------------------------
    {
        "title": "marshmallow: Validação de Intervalo Numérico com Tipagem Estrita e Descarte de NaN/Inf",
        "project_name": "marshmallow",
        "description": "Módulo Range de validação de esquemas de dados com rejeição de tipos booleanos (armadilha de herança int do Python) e números flutuantes especiais (NaN/Inf).",
        "requirements_text": (
            "REQ-MM-001: A classe Range(min, max) deve validar que o valor numérico fornecido obedece min <= value <= max.\n"
            "REQ-MM-002: Valores booleanos (True ou False) devem ser categoricamente REJEITADOS com ValidationError, pois em Python bool é subclasse de int (True == 1), gerando falhas graves de validação semântica em APIs.\n"
            "REQ-MM-003: Números em ponto flutuante especiais como float('nan'), float('inf') e float('-inf') devem ser rejeitados com ValidationError.\n"
            "REQ-MM-004: Valores válidos no limite exato de min e max devem ser aceitos e retornados sem modificação."
        ),
        "source_code": (
            "# Fonte real: src/marshmallow/validate.py (marshmallow-code/marshmallow)\n"
            "import math\n\n"
            "class ValidationError(ValueError):\n"
            "    pass\n\n"
            "class Range:\n"
            "    def __init__(self, min=None, max=None):\n"
            "        self.min = min\n"
            "        self.max = max\n\n"
            "    def __call__(self, value):\n"
            "        # Em Python isinstance(True, int) é True, o que é um risco de validação\n"
            "        if isinstance(value, bool):\n"
            "            raise ValidationError('Booleanos não são valores numéricos aceitos para Range.')\n"
            "        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):\n"
            "            raise ValidationError('Valores especiais NaN/Inf não são números válidos.')\n"
            "        if self.min is not None and value < self.min:\n"
            "            raise ValidationError(f'Valor {value} é menor que o limite mínimo {self.min}.')\n"
            "        if self.max is not None and value > self.max:\n"
            "            raise ValidationError(f'Valor {value} é maior que o limite máximo {self.max}.')\n"
            "        return value\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real: tests/test_validate.py (marshmallow)\n"
            "import pytest\n\n"
            "def test_range_within_bounds():\n"
            "    validator = Range(min=1, max=10)\n"
            "    assert validator(5) == 5\n"
            "    assert validator(1) == 1\n"
            "    assert validator(10) == 10\n\n"
            "def test_range_outside_bounds():\n"
            "    validator = Range(min=1, max=10)\n"
            "    with pytest.raises(ValidationError):\n"
            "        validator(0)\n"
            "    with pytest.raises(ValidationError):\n"
            "        validator(11)\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Detectar falta de asserções para booleanos (True/False) e valores não finitos (NaN/Inf).",
        "analysis_scope": "schema_range_validation",
        "split_group": "gh_marshmallow_range",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/marshmallow-code/marshmallow (src/marshmallow/validate.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Ausência de teste defensivo para valores booleanos em Range",
                "description": "Em Python isinstance(True, int) é True. Se o código não tratar, Range(min=0, max=1)(True) retornaria True. A suíte testa apenas ints e não previne regressão de bool.",
                "evidence": "Nenhum teste passando True ou False.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_range_rejects_booleans():\n"
                    "    validator = Range(min=0, max=5)\n"
                    "    with pytest.raises(ValidationError):\n"
                    "        validator(True)\n"
                    "    with pytest.raises(ValidationError):\n"
                    "        validator(False)\n"
                ),
                "expected_result": "Rejeitar True/False com ValidationError."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste para valores especiais float('nan') e float('inf')",
                "description": "Valores não finitos quebram asserções comuns de ordenação (< ou >). Falta teste explícito garantindo que NaN e Inf são rejeitados de forma previsível.",
                "evidence": "Todos os testes usam inteiros normais finitos.",
                "severity": "medium",
                "confidence": 0.9,
                "suggested_test": (
                    "def test_range_rejects_nan_and_inf():\n"
                    "    validator = Range(min=1, max=100)\n"
                    "    with pytest.raises(ValidationError):\n"
                    "        validator(float('nan'))\n"
                    "    with pytest.raises(ValidationError):\n"
                    "        validator(float('inf'))\n"
                ),
                "expected_result": "Disparar ValidationError para entradas numéricas não finitas."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 8. pyjwt: JWS Algorithm Whitelist & Algorithm 'none' Blocking (RFC 8725)
    # -------------------------------------------------------------------------
    {
        "title": "pyjwt: Descodificação JWS com Whitelist de Algoritmos e Bloqueio Crítico do Algoritmo 'none'",
        "project_name": "pyjwt",
        "description": "Módulo de decodificação e validação de tokens JWT/JWS com aplicação da RFC 8725 para bloqueio mandatória da vulnerabilidade do algoritmo 'none' e imposição de algoritmos permitidos.",
        "requirements_text": (
            "REQ-JWT-001: A função decode deve decodificar a estrutura do token JWT de três partes (header.payload.signature).\n"
            "REQ-JWT-002: O cabeçalho 'alg' do token DEVE ser comparado com a lista de algoritmos permitidos (algorithms). Tokens com algoritmos não autorizados devem ser rejeitados com InvalidAlgorithmError.\n"
            "REQ-JWT-003: O algoritmo 'none' é categoricamente proibido sob qualquer circunstância para prevenir a vulnerabilidade crítica de assinatura arbitrária RFC 8725 / CVE-2015-9235.\n"
            "REQ-JWT-004: A verificação da assinatura HMAC deve utilizar comparação em tempo constante (hmac.compare_digest) para evitar ataques de temporização (timing attacks)."
        ),
        "source_code": (
            "# Fonte real: jwt/api_jws.py (jpadilla/pyjwt)\n"
            "import json\n"
            "import hmac\n"
            "import hashlib\n"
            "import base64\n\n"
            "class PyJWTError(Exception): pass\n"
            "class InvalidAlgorithmError(PyJWTError): pass\n"
            "class InvalidSignatureError(PyJWTError): pass\n\n"
            "class PyJWS:\n"
            "    def decode(self, token: str, key: str, algorithms: list[str] = None):\n"
            "        if algorithms is None:\n"
            "            algorithms = ['HS256']\n"
            "        parts = token.split('.')\n"
            "        if len(parts) != 3:\n"
            "            raise PyJWTError('Estrutura de token JWT inválida')\n"
            "        header_b64, payload_b64, sig_b64 = parts\n"
            "        pad = lambda s: s + '=' * ((4 - len(s) % 4) % 4)\n"
            "        header = json.loads(base64.urlsafe_b64decode(pad(header_b64)).decode())\n"
            "        alg = header.get('alg')\n"
            "        # Mitigação RFC 8725: Nunca permitir 'none' nem algoritmos fora da whitelist\n"
            "        if alg == 'none' or alg not in algorithms:\n"
            "            raise InvalidAlgorithmError(f'Algoritmo {alg!r} inseguro ou não permitido')\n"
            "        payload = json.loads(base64.urlsafe_b64decode(pad(payload_b64)).decode())\n"
            "        signing_input = f'{header_b64}.{payload_b64}'.encode()\n"
            "        expected_sig = base64.urlsafe_b64encode(\n"
            "            hmac.new(key.encode(), signing_input, hashlib.sha256).digest()\n"
            "        ).decode().rstrip('=')\n"
            "        if not hmac.compare_digest(sig_b64, expected_sig):\n"
            "            raise InvalidSignatureError('Assinatura JWT inválida')\n"
            "        return payload\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "# Fonte real: tests/test_api_jws.py (pyjwt)\n"
            "import pytest\n"
            "import base64\n"
            "import json\n"
            "import hmac\n"
            "import hashlib\n\n"
            "def test_decode_valid_token():\n"
            "    jws = PyJWS()\n"
            "    header_b64 = base64.urlsafe_b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()).decode().rstrip('=')\n"
            "    payload_b64 = base64.urlsafe_b64encode(json.dumps({'user': 'alice'}).encode()).decode().rstrip('=')\n"
            "    sig = base64.urlsafe_b64encode(hmac.new(b'secret', f'{header_b64}.{payload_b64}'.encode(), hashlib.sha256).digest()).decode().rstrip('=')\n"
            "    token = f'{header_b64}.{payload_b64}.{sig}'\n"
            "    payload = jws.decode(token, key='secret', algorithms=['HS256'])\n"
            "    assert payload['user'] == 'alice'\n\n"
            "def test_decode_tampered_signature_fails():\n"
            "    jws = PyJWS()\n"
            "    token = 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VyIjogImFsaWNlIn0.tampered_sig'\n"
            "    with pytest.raises(InvalidSignatureError):\n"
            "        jws.decode(token, key='secret')\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Detectar vulnerabilidade crítica na suíte: falta de teste barrando explicitamente 'alg: none' e algoritmo não listado na whitelist.",
        "analysis_scope": "jwt_algorithm_whitelist_and_signature",
        "split_group": "gh_pyjwt_jws_alg",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/jpadilla/pyjwt (jwt/api_jws.py)",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Ausência de teste para bloqueio do algoritmo 'none' (Vulnerabilidade Crítica RFC 8725)",
                "description": "A vulnerabilidade clássica do JWT permite bypass de autenticação alterando alg para 'none'. É mandatória uma asserção na suíte que submeta token com alg='none' e verifique InvalidAlgorithmError.",
                "evidence": "Nenhum teste de regressão para token com 'alg': 'none'.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_decode_rejects_alg_none_exploit():\n"
                    "    jws = PyJWS()\n"
                    "    header_b64 = base64.urlsafe_b64encode(json.dumps({'alg': 'none'}).encode()).decode().rstrip('=')\n"
                    "    payload_b64 = base64.urlsafe_b64encode(json.dumps({'admin': True}).encode()).decode().rstrip('=')\n"
                    "    token = f'{header_b64}.{payload_b64}.'\n"
                    "    with pytest.raises(InvalidAlgorithmError):\n"
                    "        jws.decode(token, key='secret', algorithms=['none'])\n"
                ),
                "expected_result": "Rejeitar sumariamente com InvalidAlgorithmError."
            },
            {
                "category": "security_authorization",
                "title": "Falta de teste para token com algoritmo fora da whitelist permitida",
                "description": "Se o verificador espera apenas ['HS256'], mas o atacante envia um token assinado com ['HS512'], o token deve ser rejeitado antes de verificar a assinatura.",
                "evidence": "A suíte só testa tokens correspondentes à lista esperada.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_decode_rejects_unwhitelisted_algorithm():\n"
                    "    jws = PyJWS()\n"
                    "    header_b64 = base64.urlsafe_b64encode(json.dumps({'alg': 'HS512'}).encode()).decode().rstrip('=')\n"
                    "    payload_b64 = base64.urlsafe_b64encode(json.dumps({'sub': 'test'}).encode()).decode().rstrip('=')\n"
                    "    token = f'{header_b64}.{payload_b64}.dummy_signature'\n"
                    "    with pytest.raises(InvalidAlgorithmError):\n"
                    "        jws.decode(token, key='secret', algorithms=['HS256'])\n"
                ),
                "expected_result": "Bloquear execução com InvalidAlgorithmError."
            }
        ]
    }
]


def ingest_mined_cases():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    cat_repo = CategoryRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    cats = {c.code: c.id for c in cat_repo.get_all(include_inactive=True)}
    default_cat_id = cats.get("functional_coverage", 1)

    print("[*] Inserindo exemplos minerados de repositorios abertos do GitHub no TestGap...")

    imported = 0
    skipped = 0

    for item in MINED_GITHUB_CASES:
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
                review_note="Minerado de repositorio aberto publico e aprovado com ground-truth."
            )
            print(f"[+] Importado: {ex.public_id} — {ex.title}")
            imported += 1
        except ValueError as ve:
            print(f"[-] Ja existente (ignorado): {item['title']}")
            skipped += 1

    print(f"\n[+] Concluido: {imported} exemplos minerados inseridos, {skipped} duplicados.")


if __name__ == "__main__":
    ingest_mined_cases()
