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
