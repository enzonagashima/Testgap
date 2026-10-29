# Esquema Canônico do Dataset — Versão 1.0.0

Este documento define o formato de intercâmbio de dados utilizado nas exportações e ingestões para treinamento de modelos de IA.

## Formato de Arquivo
- **Extensão**: `.jsonl` (JSON Lines).
- **Codificação**: UTF-8 estrito.
- **Validação**: Validação contra `schemas/dataset-v1.schema.json`.

## Campos Principais

```json
{
  "schema_version": "1.0.0",
  "example_id": "TG-000001",
  "project": {
    "name": "AuthService",
    "language": "python",
    "framework": "pytest"
  },
  "input": {
    "requirements": "Requisitos em texto...",
    "source_code": "Código-fonte opcional...",
    "test_suite": "Suíte original de testes...",
    "test_format": "pytest",
    "analysis_scope": "autenticacao"
  },
  "expected_output": {
    "has_gaps": true,
    "gaps": [
      {
        "category": "security_authorization",
        "title": "Falta de teste para limite de tentativas",
        "description": "Explicação detalhada...",
        "requirement_reference": "REQ-001",
        "evidence": "Não há teste com 5 falhas seguidas",
        "severity": "high",
        "suggested_test": "Código do teste sugerido...",
        "expected_result": "Resultado esperado..."
      }
    ]
  },
  "metadata": {
    "source_type": "human_authored",
    "review_status": "approved",
    "split_group": "auth_core",
    "labels_verified": true
  }
}
```
