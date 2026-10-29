# TestGap Automated Test Matrix

Matrix of essential test cases required to validate compliance with `specs.md`.

| Arquivo de Teste | Caso de Teste | Descrição da Validação |
| :--- | :--- | :--- |
| `test_database.py` | `test_foreign_keys_enforced` | Verifica que inserir gap com `example_id` inexistente levanta erro de integridade referencial. |
| `test_database.py` | `test_transaction_rollback` | Garante que falha no meio de operação atômica desfaz alterações prévias. |
| `test_database.py` | `test_migrations_idempotency` | Executar o migrador 2 vezes consecutivas não duplica tabelas nem corrompe dados. |
| `test_schemas.py` | `test_valid_example_schema` | Valida carga completa compatível com `ExampleCreate`. |
| `test_schemas.py` | `test_whitespace_validation` | Garante que strings compostas unicamente por espaços em branco são rejeitadas. |
| `test_schemas.py` | `test_enum_constraints` | Verifica rejeição de valores fora de `ReviewStatus`, `Severity`, `GapStatus`. |
| `test_examples.py` | `test_create_example_generates_public_id` | Garante formatação sequencial `TG-000001`, `TG-000002`. |
| `test_examples.py` | `test_content_hash_calculation` | Verifica que `content_hash` é recalculado ao editar requisitos ou código. |
| `test_examples.py` | `test_duplicate_hash_detection` | Detecta tentativa de criar exemplo com requisitos e código idênticos a outro já existente. |
| `test_examples.py` | `test_example_pagination_and_search` | Testa busca por termo em título e paginação por limit/offset. |
| `test_gaps.py` | `test_create_gap_linked_to_example` | Cria lacuna e valida persistência de campos e chaves estrangeiras. |
| `test_gaps.py` | `test_cascade_delete_gaps` | Ao excluir um exemplo, todas as lacunas vinculadas são removidas automaticamente. |
| `test_gaps.py` | `test_category_deactivation_safeguard` | Não permite excluir categoria que possui lacunas atreladas. |
| `test_import.py` | `test_import_valid_jsonl` | Lê arquivo JSONL canônico e insere registros no banco. |
| `test_import.py` | `test_import_invalid_jsonl_diagnostics` | Identifica linhas corrompidas e gera relatório de erros sem falhar silenciosamente. |
| `test_import.py` | `test_import_duplicate_policy_skip` | Pula registros duplicados preservando os registros originais. |
| `test_export.py` | `test_export_only_approved_examples` | Garante que registros `pending` ou `rejected` não entram na exportação de treino. |
| `test_export.py` | `test_export_excludes_rejected_gaps` | Garante que lacunas rejeitadas são suprimidas na saída exportada. |
| `test_export.py` | `test_export_split_group_partitioning` | Valida que exemplos do mesmo `split_group` ficam restritos a um único split. |
| `test_quality.py` | `test_has_gaps_inconsistency_rule` | Detecta erro quando `has_gaps=true` mas lista de lacunas está vazia. |
| `test_quality.py` | `test_orphan_category_heuristic` | Alerta quando uma lacuna aponta para uma categoria inativa. |
| `test_quality.py` | `test_audit_persistence` | Grava resultado da auditoria na tabela `audit_results`. |
