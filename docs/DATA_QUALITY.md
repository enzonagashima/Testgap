# Diretrizes de Qualidade dos Dados

O processo de auditoria de qualidade do TestGap atua em duas camadas fundamentais:

## Camada 1: Validação Estrutural
Executada de forma síncrona pelo Pydantic v2 e restrições de integridade no SQLite:
- Strings obrigatórias não podem conter apenas espaços em branco.
- Identificadores no formato sequencial `TG-000001`.
- Índices de confiança dentro do intervalo `[0.0, 1.0]`.
- Enumerações válidas para `review_status`, `severity`, `gap_status`, `source_type`.

## Camada 2: Validação Semântica & Heurísticas
Executada pelo `QualityService`:
- **Consistência de Rótulos**: Se `has_gaps = True`, deve haver pelo menos uma lacuna confirmada vinculada.
- **Detecção de Duplicatas Exatas**: Alerta de colisão de `content_hash`.
- **Integridade da Taxonomia**: Detecção de lacunas associadas a categorias inativas.
- **Riqueza de Conteúdo**: Alertas para requisitos com descrição excessivamente curta (< 30 caracteres) ou ausência de código-fonte.
