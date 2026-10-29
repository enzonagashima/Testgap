# Experimentos Futuros de Treinamento

Este documento define os contratos e orientações para a Fase 6 e versões posteriores do TestGap, quando os modelos de IA forem finetunados e avaliados.

## 1. Entrada Esperada pelo Modelo
- **Prompt Estruturado**:
  - Contexto do projeto e linguagem.
  - Requisitos textuais informados.
  - Código-fonte da aplicação (quando fornecido).
  - Suíte de testes automatizados existente.
  - Escopo da análise solicitada.

## 2. Saída Esperada do Modelo
- `has_gaps`: Booleano indicando se foram encontradas lacunas reais.
- `gaps`: Lista de objetos contendo `category`, `title`, `description`, `requirement_reference`, `evidence`, `severity`, `suggested_test`, `expected_result`.

## 3. Avaliação e Métricas
- **Detecção Binária**: Precisão, Recall e F1-Score sobre a predição de `has_gaps`.
- **Classificação de Taxonomia**: Acurácia multirrótulo na identificação da categoria correta da lacuna.
- **Validação de Teste Sugerido**: Avaliação por AST e execução em sandbox para verificar se o teste sugerido é sintaticamente válido.
