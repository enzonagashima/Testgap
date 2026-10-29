# Diretrizes de Desenvolvimento — TestGap

Este arquivo define regras obrigatórias e contextuais para qualquer agente de IA operando neste repositório, com base nas especificações de `specs.md`.

---

## 1. Regras Operacionais Mandatórias

1. **Ambiente Local Windows**:
   - Todo comando de terminal deve ser executado no Windows usando PowerShell.
   - Usar barras invertidas em caminhos de terminal ou aspas duplas apropriadas.
2. **Nunca Inventar Resultados**:
   - Nunca inventar ou simular saídas de testes automatizados, treinamento de IA ou métricas de auditoria.
   - Executar os comandos reais (`pytest`, `python scripts/...`) e reportar a saída literal.
3. **Arquitetura Estrita em 4 Camadas**:
   - `UI (Streamlit)` ➔ `Serviços` ➔ `Repositórios` ➔ `Esquemas / SQLite`.
   - **Nenhum comando SQL ou acesso direto a `sqlite3` é permitido dentro dos arquivos da UI (`app.py`, `pages/*.py`).**
4. **Persistência Segura**:
   - Banco de dados em `data/testgap.db`.
   - Sempre habilitar chaves estrangeiras (`PRAGMA foreign_keys = ON;`) e modo WAL (`PRAGMA journal_mode = WAL;`).
   - Usar transações atômicas para alterações multitable.
   - Nunca apagar ou sobrescrever o banco de dados durante inicializações normais.
5. **Padrão de Idiomas**:
   - Identificadores técnicos, nomes de arquivos, tabelas, colunas e código em **Inglês**.
   - Interface com usuário, mensagens, labels, badges e documentação em **Português Brasileiro (pt-BR)**.
6. **Skills Disponíveis**:
   - Consulte e utilize as skills em `.agents/skills/` para cada fase de desenvolvimento:
     - `testgap-orchestrator`: Coordenação de fases e relatório final de entrega.
     - `testgap-foundation-core`: Configuração SQLite, migrações, modelos Pydantic e repositórios.
     - `testgap-streamlit-ui`: Layout e componentes das páginas Streamlit.
     - `testgap-quality-audit`: Regras de validação semântica e auditoria de qualidade.
     - `testgap-import-export`: Pipelines JSONL/CSV e particionamento para treino.
     - `testgap-qa-testing`: Testes automatizados com pytest e matriz de testes.
