# TestGap UI Pages Specification

Detailed specifications for each Streamlit page in the application.

---

## 1. Homepage (`app.py`)

- **Page Title**: `TestGap Dataset — Início`
- **Header**: Visual title with subtitle "Plataforma Local de Curadoria de Datasets para Lacunas de Testes em IA".
- **Execution Mode Indicator**: "Ambiente Local (Windows) — Banco: `data/testgap.db`".
- **KPI Metrics Grid (Top Row)**:
  1. Total de Exemplos (`total_examples`)
  2. Exemplos Aprovados (`approved_count`)
  3. Exemplos Pendentes (`pending_count`)
  4. Exemplos com Lacunas (`with_gaps_count`)
  5. Exemplos sem Lacunas (`without_gaps_count`)
- **Visual Breakdown Charts (Middle Row)**:
  - Distribuição de Lacunas por Categoria (Gráfico de barras)
  - Distribuição por Severidade (Gráfico de pizza/rosca ou barras)
- **Quality Quick-Status Box**:
  - Exibe contagem de erros e avisos da última auditoria executada.
  - Botão "Executar Nova Auditoria" direcionando para a página 5.
- **Recent Activity Table**:
  - Últimos 5 exemplos criados ou atualizados com links para visualização direta.

---

## 2. Dataset Explorer (`pages/1_Dataset.py`)

- **Sidebar Filters**:
  - Campo de busca textual (ID público, título, projeto)
  - Multiselect de Estado de Revisão (`Pendente`, `Aprovado`, `Rejeitado`, `Requer Revisão`)
  - Multiselect de Origem (`human_authored`, `ai_generated`, etc.)
  - Selectbox de Projeto
  - Selectbox de Categoria de Lacuna
  - Selectbox de Severidade
  - Radio/Checkbox de Lacunas: Todos | Com Lacunas | Sem Lacunas
- **Table Columns**:
  - `ID Público` (ex: `TG-000001`)
  - `Título`
  - `Projeto`
  - `Linguagem / Framework`
  - `Qtd. Lacunas`
  - `Status Revisão` (Badge colorido)
  - `Origem`
  - `Atualizado em`
  - `Ações` (Menu ou botões compactos)
- **Detail Modal / Drawer**:
  - Tabs: Requisitos | Código-Fonte | Suíte de Testes | Lacunas Identificadas | Histórico de Revisão.

---

## 3. Cadastro de Exemplo (`pages/2_Adicionar_Exemplo.py`)

- **Seções Estruturadas**:
  - **A. Identificação**: Título (obrigatório), Nome do Projeto (obrigatório), Descrição breve do contexto.
  - **B. Requisitos**: Requisitos funcionais e regras de negócio a serem validadas (obrigatório).
  - **C. Código-Fonte**: Linguagem de programação (select: python, javascript, typescript, java, csharp, etc.), Código-fonte da aplicação (área de texto expansível com destaque sintático).
  - **D. Suíte de Testes**: Formato/Framework de testes (select: pytest, unittest, jest, junit, etc.), Código integral da suíte de testes (obrigatório).
  - **E. Escopo de Análise**: Escopo analisado (ex: "Validação de senhas e bloqueio"), Comportamento esperado sintetizado.
  - **F. Lacunas Identificadas**:
    - Checkbox / Toggle: "Este exemplo contém lacunas de teste? (`has_gaps`)"
    - Construtor interativo de lacunas: Botão "+ Adicionar Lacuna".
    - Cada lacuna possui: Categoria (select das ativas), Título, Descrição detalhada, Requisito referenciado, Evidência na suíte/código, Severidade (Crítico, Alto, Médio, Baixo, Informativo), Confiança (slider 0.0 a 1.0), Teste Proposto (código ou passo a passo), Resultado Esperado.
  - **G. Metadados e Curadoria**:
    - Grupo de separação (`split_group`): ex: `auth_service_v1` (usado para garantir que dados de um mesmo projeto fiquem no mesmo split de treino/teste).
    - Origem dos dados (`source_type`): select.
    - Referência da origem (URL, issue, repositório).
- **Validação ao Salvar**:
  - Executa validação de campos obrigatórios via Pydantic model `ExampleCreate`.
  - Verifica se hash idêntico já existe no banco. Se existir, alerta o usuário antes de salvar.

---

## 4. Gestão de Categorias (`pages/3_Categorias.py`)

- **Tabela de Categorias**:
  - Código estável, Nome em pt-BR, Descrição, Status (Ativa/Inativa), Total de Lacunas Vinculadas.
- **Ações**:
  - Alternar ativação (`is_active = 0/1`).
  - Botão de exclusão protegido: somente permitido se nenhuma lacuna estiver vinculada à categoria.
  - Formulário para cadastrar nova categoria customizada.

---

## 5. Estatísticas e Métricas (`pages/4_Estatisticas.py`)

- **Gráficos e Indicadores**:
  - Lacunas por categoria (gráfico horizontal de barras).
  - Lacunas por severidade (distribuição percentual).
  - Distribuição de exemplos por `split_group` (para auditoria de balanceamento de dataset).
  - Taxa de aprovação de revisões (Aprovados vs Rejeitados vs Pendentes).
  - Contagem de exemplos por linguagem e framework.

---

## 6. Qualidade dos Dados (`pages/5_Qualidade_Dados.py`)

- **Painel de Auditoria**:
  - Botão "Executar Auditoria Completa".
  - Métricas: Total examinado, Quantidade de Erros (bloqueantes de exportação), Quantidade de Avisos.
  - Tabela filtrável de Não-Conformidades:
    - ID do Exemplo
    - Severidade do Problema (`Erro` / `Aviso` / `Info`)
    - Regra Violada
    - Mensagem explicativa
    - Link direto para edição do exemplo afetado.

---

## 7. Configurações e Manutenção (`pages/6_Configuracoes.py`)

- **Informações do Sistema**:
  - Caminho absoluto do banco SQLite ativo.
  - Tamanho do arquivo em disco (KB/MB).
  - Versão do esquema de dados (`1.0.0`).
  - Total de registros nas tabelas.
- **Ações de Manutenção**:
  - Botão "Gerar Cópia de Segurança (Backup)": Salva cópia com timestamp em `data/backups/`.
  - Botão "Executar Otimização SQLite (`VACUUM`)".
  - Logs recentes do sistema.
