"""Formatting utilities for LLM Fine-Tuning datasets (ChatML, Alpaca, CoT)."""
import json
from typing import Dict, Any, List

SYSTEM_PROMPT = (
    "Você é o TestGap AI, um auditor sênior de QA e engenharia de software.\n"
    "Sua função é confrontar os requisitos de software e regras de negócio com o código-fonte da aplicação "
    "e a suíte de testes existente para identificar pontos cegos, casos de borda não testados, "
    "vulnerabilidades de segurança, regressões e falhas de cobertura.\n"
    "Se a suíte for robusta e cobrir 100% dos requisitos e cenários de borda sem lacunas, determine 'has_gaps': false e 'gaps': [].\n"
    "Caso contrário, determine 'has_gaps': true e liste minuciosamente cada lacuna com sua categoria taxonômica, "
    "severidade, evidência factual e código do teste sugerido."
)


def build_user_prompt(canonical_record: Dict[str, Any]) -> str:
    """Build standardized user instruction prompt with project context and code."""
    inp = canonical_record["input"]
    proj = canonical_record["project"]

    source_code = inp.get("source_code") or "Nenhum código fornecido (análise funcional de especificação / caixa-preta)."

    prompt = (
        f"### Contexto do Projeto\n"
        f"- Projeto: {proj['name']}\n"
        f"- Linguagem: {proj['language']}\n"
        f"- Framework de Teste: {proj['framework']}\n"
        f"- Escopo da Análise: {inp['analysis_scope']}\n\n"
        f"### Requisitos de Software e Regras de Negócio:\n"
        f"{inp['requirements']}\n\n"
        f"### Código-Fonte da Aplicação:\n"
        f"```{proj['language']}\n"
        f"{source_code}\n"
        f"```\n\n"
        f"### Suíte de Testes Atual:\n"
        f"```{proj['language']}\n"
        f"{inp['test_suite']}\n"
        f"```\n\n"
        f"Audite a suíte de testes acima em relação aos requisitos e código fornecidos. "
        f"Determine se há lacunas de teste e apresente o relatório de auditoria em JSON estruturado."
    )
    return prompt


def build_assistant_response(canonical_record: Dict[str, Any], include_thought: bool = True) -> str:
    """Build assistant response with optional Chain-of-Thought reasoning preceding JSON."""
    out = canonical_record["expected_output"]
    has_gaps = out["has_gaps"]
    gaps = out.get("gaps", [])

    if not include_thought:
        return json.dumps(out, ensure_ascii=False, indent=2)

    # Chain-of-Thought synthesis
    if not has_gaps:
        thought = (
            "Análise Concluída: A suíte de testes é completa e robusta. Todos os requisitos, "
            "valores-limite de borda, tratamentos de erro e tipos inválidos foram exaustivamente cobertos. "
            "Nenhuma lacuna de teste identificada."
        )
    else:
        gap_summaries = [f"- [{g['severity'].upper()}] {g['title']} ({g['category']})" for g in gaps]
        thought = (
            f"Análise Concluída: Foram detectadas {len(gaps)} lacuna(s) crítica(s) de teste na suíte:\n"
            + "\n".join(gap_summaries) + "\n"
            + "Recomenda-se a inclusão dos testes complementares sugeridos para prevenir regressões e vulnerabilidades."
        )

    response_payload = {
        "analysis_thought": thought,
        "has_gaps": has_gaps,
        "gaps_count": len(gaps),
        "gaps": gaps
    }
    return json.dumps(response_payload, ensure_ascii=False, indent=2)


def to_chatml_record(canonical_record: Dict[str, Any], include_thought: bool = True) -> Dict[str, Any]:
    """Convert canonical record to OpenAI / Hugging Face ChatML 'messages' format.
    
    Compatible with TRL SFTTrainer, Unsloth, Llama-Factory and OpenAI Fine-Tuning API.
    """
    user_content = build_user_prompt(canonical_record)
    assistant_content = build_assistant_response(canonical_record, include_thought=include_thought)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ],
        "metadata": {
            "example_id": canonical_record["example_id"],
            "split_group": canonical_record["metadata"]["split_group"],
            "has_gaps": canonical_record["expected_output"]["has_gaps"],
            "language": canonical_record["project"]["language"]
        }
    }


def to_alpaca_record(canonical_record: Dict[str, Any], include_thought: bool = True) -> Dict[str, Any]:
    """Convert canonical record to Alpaca instruction format (instruction, input, output)."""
    user_content = build_user_prompt(canonical_record)
    assistant_content = build_assistant_response(canonical_record, include_thought=include_thought)

    return {
        "instruction": SYSTEM_PROMPT,
        "input": user_content,
        "output": assistant_content,
        "metadata": {
            "example_id": canonical_record["example_id"],
            "split_group": canonical_record["metadata"]["split_group"]
        }
    }
