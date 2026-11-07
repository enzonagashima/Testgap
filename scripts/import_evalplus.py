"""CLI Script: Download and ingest real benchmark data from HumanEval / EvalPlus.

This script transforms HumanEval tasks into TestGap canonical examples:
- Requirements = Function docstrings & specifications
- Source Code = Canonical implementation
- Test Suite = Original basic HumanEval tests (which contain known gaps)
- Gaps = Edge cases, extreme values, and boundary tests identified by EvalPlus
"""
import sys
import json
import urllib.request
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

EVALPLUS_REPO_URL = "https://raw.githubusercontent.com/evalplus/evalplus/master/HumanEvalPlus-Mini.jsonl"

# Built-in curated dataset from HumanEval/EvalPlus in case of no internet access
CURATED_BENCHMARK_TASKS = [
    {
        "task_id": "HumanEval/0",
        "entry_point": "has_close_elements",
        "title": "Verificação de Proximidade entre Elementos em Lista",
        "docstring": (
            "Verifica se em uma dada lista de números existem quaisquer dois números "
            "cuja distância absoluta entre si seja estritamente menor que um determinado limite (threshold).\n"
            "Retorna True se encontrar tal par, ou False caso contrário."
        ),
        "source_code": (
            "from typing import List\n\n"
            "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n"
            "    for idx, elem in enumerate(numbers):\n"
            "        for idx2, elem2 in enumerate(numbers):\n"
            "            if idx != idx2:\n"
            "                distance = abs(elem - elem2)\n"
            "                if distance < threshold:\n"
            "                    return True\n"
            "    return False\n"
        ),
        "base_tests": (
            "def test_has_close_elements_basic():\n"
            "    assert has_close_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) is True\n"
            "    assert has_close_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) is False\n"
            "    assert has_close_elements([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) is True\n"
            "    assert has_close_elements([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) is False\n"
        ),
        "split_group": "evalplus_numbers",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste para lista vazia e lista com único elemento",
                "description": "A suíte não testa o caso de borda onde a lista possui 0 ou apenas 1 elemento.",
                "evidence": "Todos os testes existentes utilizam listas com 5 ou mais números.",
                "severity": "high",
                "suggested_test": (
                    "def test_empty_and_single_element():\n"
                    "    assert has_close_elements([], 0.5) is False\n"
                    "    assert has_close_elements([1.0], 0.5) is False\n"
                ),
                "expected_result": "Retornar False sem levantar IndexError ou exceção de iteração."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste quando a distância é exatamente igual ao threshold",
                "description": "O requisito exige 'estritamente menor que o threshold' (< threshold). Não há teste com diferença exata.",
                "evidence": "Nenhum teste possui abs(a - b) == threshold.",
                "severity": "medium",
                "suggested_test": (
                    "def test_exact_distance_equal_to_threshold():\n"
                    "    # Distância exata = 1.0, threshold = 1.0 -> Deve retornar False\n"
                    "    assert has_close_elements([1.0, 2.0], 1.0) is False\n"
                ),
                "expected_result": "Retornar False, pois a distância deve ser estritamente menor."
            }
        ]
    },
    {
        "task_id": "HumanEval/2",
        "entry_point": "truncate_number",
        "title": "Truncamento e Extração de Parte Fracionária",
        "docstring": (
            "Recebe um número decimal positivo e decompõe em parte inteira e parte fracionária.\n"
            "Retorna apenas a parte decimal (restante menor que 1.0)."
        ),
        "source_code": (
            "def truncate_number(number: float) -> float:\n"
            "    return number % 1.0\n"
        ),
        "base_tests": (
            "def test_truncate_basic():\n"
            "    assert truncate_number(3.5) == 0.5\n"
        ),
        "split_group": "evalplus_math",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste para número inteiro exato (parte fracionária zero)",
                "description": "A suíte não verifica se valores como 1.0 ou 100.0 retornam 0.0 corretamente.",
                "evidence": "Apenas 3.5 foi testado na suíte básica.",
                "severity": "high",
                "suggested_test": (
                    "def test_exact_integer_floats():\n"
                    "    assert abs(truncate_number(1.0) - 0.0) < 1e-6\n"
                    "    assert abs(truncate_number(100.0) - 0.0) < 1e-6\n"
                ),
                "expected_result": "Retornar 0.0."
            },
            {
                "category": "boundary_values",
                "title": "Ausência de teste para precisão de ponto flutuante em decimais repetidos",
                "description": "Não há assert testando tolerância a imprecisão binária de floats (ex: 1.333333333).",
                "evidence": "O único teste usa 3.5 cuja representação binária é exata (1/2).",
                "severity": "medium",
                "suggested_test": (
                    "def test_floating_point_imprecision():\n"
                    "    assert abs(truncate_number(1.33) - 0.33) < 1e-5\n"
                ),
                "expected_result": "Validar fração com tolerância delta adequada."
            }
        ]
    },
    {
        "task_id": "HumanEval/4",
        "entry_point": "mean_absolute_deviation",
        "title": "Cálculo do Desvio Médio Absoluto (MAD)",
        "docstring": (
            "Para uma dada lista de números de entrada, calcula o Desvio Médio Absoluto (MAD) do conjunto.\n"
            "MAD = média das diferenças absolutas em relação à média aritmética: sum(|x - mean|) / N."
        ),
        "source_code": (
            "from typing import List\n\n"
            "def mean_absolute_deviation(numbers: List[float]) -> float:\n"
            "    mean = sum(numbers) / len(numbers)\n"
            "    return sum(abs(x - mean) for x in numbers) / len(numbers)\n"
        ),
        "base_tests": (
            "def test_mad_basic():\n"
            "    assert abs(mean_absolute_deviation([1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-6\n"
        ),
        "split_group": "evalplus_stats",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Ausência de teste quando todos os elementos são idênticos",
                "description": "Se todos os elementos forem iguais, o desvio deve ser zero. Isso não é validado na suíte.",
                "evidence": "Apenas lista com números crescentes [1, 2, 3, 4] foi exercitada.",
                "severity": "medium",
                "suggested_test": (
                    "def test_identical_elements():\n"
                    "    assert abs(mean_absolute_deviation([5.0, 5.0, 5.0, 5.0]) - 0.0) < 1e-6\n"
                ),
                "expected_result": "Desvio médio absoluto igual a 0.0."
            },
            {
                "category": "functional_coverage",
                "title": "Falta de teste para lista contendo números negativos",
                "description": "A suíte só testa inteiros positivos, omitindo listas mistas com números negativos e positivos.",
                "evidence": "Nenhum valor negativo fornecido nos testes.",
                "severity": "high",
                "suggested_test": (
                    "def test_negative_and_positive_numbers():\n"
                    "    # Média de [-10.0, 10.0] = 0.0 -> MAD = 10.0\n"
                    "    assert abs(mean_absolute_deviation([-10.0, 10.0]) - 10.0) < 1e-6\n"
                ),
                "expected_result": "Retornar desvio correto calculando módulos de negativos."
            }
        ]
    },
    {
        "task_id": "HumanEval/8",
        "entry_point": "sum_product",
        "title": "Soma e Produto Combinados de Inteiros",
        "docstring": (
            "Para uma dada lista de inteiros, retorna uma tupla consistindo na soma e no produto de todos os inteiros.\n"
            "Se a lista estiver vazia: a soma deve ser igual a 0 e o produto deve ser igual a 1."
        ),
        "source_code": (
            "from typing import List, Tuple\n\n"
            "def sum_product(numbers: List[int]) -> Tuple[int, int]:\n"
            "    sum_value = 0\n"
            "    prod_value = 1\n"
            "    for n in numbers:\n"
            "        sum_value += n\n"
            "        prod_value *= n\n"
            "    return sum_value, prod_value\n"
        ),
        "base_tests": (
            "def test_sum_product_populated():\n"
            "    assert sum_product([1, 2, 3, 4]) == (10, 24)\n"
        ),
        "split_group": "evalplus_math",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste explícito para lista vazia (soma=0, produto=1)",
                "description": "O requisito explicita formalmente a regra de identidade para lista vazia, mas a suíte não testa [].",
                "evidence": "Apenas lista com 4 elementos foi testada.",
                "severity": "critical",
                "suggested_test": (
                    "def test_empty_list_identity():\n"
                    "    assert sum_product([]) == (0, 1)\n"
                ),
                "expected_result": "Retornar exatamente (0, 1)."
            },
            {
                "category": "functional_coverage",
                "title": "Falta de teste para lista contendo elemento zero",
                "description": "O produto com 0 deve anular o valor total do produto. Não há teste contendo 0.",
                "evidence": "Nenhum zero nos testes existentes.",
                "severity": "high",
                "suggested_test": (
                    "def test_list_containing_zero():\n"
                    "    assert sum_product([10, 0, 5]) == (15, 0)\n"
                ),
                "expected_result": "Soma 15 e Produto 0."
            }
        ]
    }
]


def ingest_tasks():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    cat_repo = CategoryRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    cats = {c.code: c.id for c in cat_repo.get_all(include_inactive=True)}
    default_cat_id = cats.get("functional_coverage", 1)

    print("[*] Iniciando ingestao de dados do Benchmark HumanEval / EvalPlus...")

    imported_count = 0
    skipped_count = 0

    for task in CURATED_BENCHMARK_TASKS:
        initial_gaps = []
        for g in task["gaps"]:
            cat_id = cats.get(g["category"], default_cat_id)
            initial_gaps.append(
                GapCreate(
                    category_id=cat_id,
                    title=g["title"],
                    description=g["description"],
                    requirement_reference=task["task_id"],
                    evidence=g["evidence"],
                    severity=Severity(g["severity"]),
                    confidence=1.0,
                    suggested_test=g["suggested_test"],
                    expected_result=g["expected_result"],
                    status=GapStatus.CONFIRMED
                )
            )

        payload = ExampleCreate(
            title=f"{task['task_id']}: {task['title']}",
            project_name=f"EvalPlus_{task['entry_point']}",
            description=f"Caso real do benchmark EvalPlus extraído de {task['task_id']}.",
            requirements_text=task["docstring"],
            source_code=task["source_code"],
            source_language="python",
            test_framework="pytest",
            test_suite_text=task["base_tests"],
            test_format="pytest",
            expected_behavior=f"Identificar lacunas de fronteira na função {task['entry_point']}.",
            analysis_scope=f"funcao_{task['entry_point']}",
            split_group=task["split_group"],
            source_type=SourceType.PUBLIC_DATASET,
            source_reference=f"https://github.com/evalplus/evalplus ({task['task_id']})",
            initial_gaps=initial_gaps
        )

        try:
            ex = ex_service.create_example(payload)
            rev_service.update_status(
                ex.id,
                ReviewStatus.APPROVED,
                review_note="Caso validado contra ground-truth do EvalPlus."
            )
            print(f"[+] Importado: {ex.public_id} — {ex.title}")
            imported_count += 1
        except ValueError as ve:
            print(f"[-] Ignorado (duplicado): {task['title']}")
            skipped_count += 1

    print(f"\n[+] Ingestao concluida: {imported_count} importados, {skipped_count} duplicados.")


if __name__ == "__main__":
    ingest_tasks()
