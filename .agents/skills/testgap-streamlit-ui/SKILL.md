---
name: testgap-streamlit-ui
description: >-
  Guides the implementation, components, page layout, and UX standards for the
  Streamlit multi-page interface of TestGap. Use when designing, creating, or
  refining the web UI pages, components, forms, filters, and state management.
---

# TestGap Streamlit UI Architecture & Guidelines

This skill defines the user interface requirements, visual style, component hierarchy, and integration rules for the Streamlit web dashboard in TestGap (Phase 3).

---

## 1. Core Interface Directives

1. **Language & Tone**: All UI strings, button labels, toasts, column headers, and form help text must be in **Brazilian Portuguese (pt-BR)**.
2. **Strict Service Layer Boundary**:
   - Streamlit scripts (`app.py`, `pages/*.py`) must **never** import `sqlite3` directly or execute SQL queries.
   - All data fetching and mutations must call methods on `ExampleService`, `GapService`, `CategoryService`, `ReviewService`, or `QualityService`.
3. **Desktop Ergonomics**: Use `st.set_page_config(layout="wide")` across all pages. Provide crisp technical tables, responsive filter sidebars, and tabbed forms.
4. **No Simulated Data**: When the database is empty, render informative empty-state callouts with quick-start buttons (e.g. "Criar Primeiro Exemplo" or "Importar Dataset") instead of placeholder mock metrics.
5. **Safe Destructive Actions**: Deleting an example or deactivating a category must require explicit user confirmation (e.g. `st.warning` with a confirmation checkbox or modal).

---

## 2. Page Hierarchy & Responsibilities

Refer to [pages_spec.md](./references/pages_spec.md) for detailed form fields and layout specifications.

```text
pages/
├── 1_Dataset.py            # Searchable, filterable, paginated dataset table & actions
├── 2_Adicionar_Exemplo.py  # Structured creation form (Sections A through G)
├── 3_Categorias.py         # Category management, activation toggle, gap count
├── 4_Estatisticas.py       # Metrics breakdown by project, severity, split_group
├── 5_Qualidade_Dados.py    # Quality audit runner & issue breakdown
└── 6_Configuracoes.py      # Database status, backup execution, storage info
app.py                      # Home dashboard, KPI metric cards, recent changes
```

---

## 3. Reusable UI Components (`testgap/ui/components.py`)

Create standard helper functions to guarantee visual consistency:

### Status & Severity Badges
- **Review Status Badges**:
  - `approved` (`Aprovado`): Green pill / badge (`#28a745`)
  - `pending` (`Pendente`): Yellow/Gold pill (`#ffc107`)
  - `needs_revision` (`Requer Revisão`): Orange pill (`#fd7e14`)
  - `rejected` (`Rejeitado`): Red pill (`#dc3545`)
- **Severity Badges**:
  - `critical` (`Crítico`): Dark Red (`#721c24`, bg `#f8d7da`)
  - `high` (`Alto`): Orange (`#856404`, bg `#fff3cd`)
  - `medium` (`Médio`): Blue (`#0c5460`, bg `#d1ecf1`)
  - `low` (`Baixo`): Slate (`#383d41`, bg `#e2e3e5`)
  - `informational` (`Informativo`): Teal (`#155724`, bg `#d4edda`)

### Metric Cards (`render_metric_card`)
Render HTML/CSS cards displaying label, large numeric value, and subtle description.

### Empty State Handler (`render_empty_state`)
When query results are empty, show a clean info box with actionable next steps.

---

## 4. Multi-Page Workflow Patterns

### Dataset Browser (`pages/1_Dataset.py`)
- **Filter Bar**: Text search across `title`, `project_name`, `public_id`; selectboxes for `review_status`, `source_type`, `category`, `severity`, and checkbox for `has_gaps`.
- **Paginated Table**: Default 20 records per page.
- **Action Buttons per Row**:
  - *Ver / Detalhes*: Expands or navigates to details view with tabbed inspection of code and gaps.
  - *Editar*: Pre-fills edit form.
  - *Duplicar como Rascunho*: Clones record, resets `public_id`, sets status to `pending`.
  - *Excluir*: Displays confirmation before invoking `example_service.delete_example()`.

### Example Form Sections (`pages/2_Adicionar_Exemplo.py`)
Organize the form into distinct expanders or tabs:
- **Seção A — Identificação**: `title`, `project_name`, `description`.
- **Seção B — Requisitos**: `requirements_text` (multiline editor).
- **Seção C — Código-Fonte**: `source_language` (default `python`), `source_code`.
- **Seção D — Suíte de Testes**: `test_format` (default `pytest`), `test_framework`, `test_suite_text`.
- **Seção E — Escopo**: `analysis_scope`, `expected_behavior`.
- **Seção F — Lacunas (Gaps)**: Dynamic list editor allowing user to add/remove gaps with fields:
  - `category_id`, `title`, `description`, `requirement_reference`, `evidence`, `severity`, `confidence`, `suggested_test`, `expected_result`, `status`.
- **Seção G — Metadados**: `split_group` (e.g. project slug), `source_type`, `source_reference`.

### Review Transitions (Details View)
Provide direct buttons:
- `Aprovar Exemplo` (changes status to `approved`)
- `Rejeitar Exemplo` (changes status to `rejected`)
- `Solicitar Revisão` (changes status to `needs_revision`)
- Require an optional review note that is saved directly into `review_history`.
