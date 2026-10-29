"""Registration page for adding new testgap examples with interactive gap builder."""
import streamlit as st

from testgap.services.example_service import ExampleService
from testgap.services.category_service import CategoryService
from testgap.schemas import ExampleCreate, GapCreate
from testgap.enums import Severity, GapStatus, SourceType
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import render_header

st.set_page_config(page_title="TestGap — Cadastrar Exemplo", page_icon="➕", layout="wide")
apply_custom_styles()

example_service = ExampleService()
category_service = CategoryService()

render_header("Cadastrar Novo Exemplo", "Preencha as seções técnicas para adicionar um registro ao dataset")

# Available Categories
categories = category_service.list_categories(include_inactive=False)
cat_dict = {f"{c.name} ({c.code})": c.id for c in categories}

# Session state for dynamic gaps list
if "form_gaps" not in st.session_state:
    st.session_state.form_gaps = []

with st.form("create_example_form", clear_on_submit=False):
    st.subheader("Seção A — Identificação do Exemplo")
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        title = st.text_input("Título do Exemplo *", placeholder="Ex: Validação de bloqueio por tentativas de login")
    with col_a2:
        project_name = st.text_input("Nome do Projeto / Aplicação *", placeholder="Ex: AuthService")

    description = st.text_area("Descrição / Contexto Geral", placeholder="Explicar brevemente o cenário arquitetural...")

    st.divider()

    st.subheader("Seção B — Requisitos de Software")
    requirements_text = st.text_area(
        "Requisitos Funcionais e Regras de Negócio *",
        placeholder="Descreva os requisitos que deveriam ser exercitados pelos testes...",
        height=140
    )

    st.divider()

    st.subheader("Seção C — Código-Fonte da Aplicação (Opcional)")
    col_c1, col_c2 = st.columns([1, 3])
    with col_c1:
        source_language = st.selectbox("Linguagem", options=["python", "javascript", "typescript", "java", "csharp", "go"])
    with col_c2:
        source_code = st.text_area(
            "Código-Fonte (se disponível)",
            placeholder="def authenticate(username, password):\n    ...",
            height=140
        )

    st.divider()

    st.subheader("Seção D — Suíte de Testes Existente")
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        test_format = st.selectbox("Formato da Suíte", options=["pytest", "unittest", "jest", "junit", "other"])
    with col_d2:
        test_framework = st.text_input("Framework de Testes", value="pytest")

    test_suite_text = st.text_area(
        "Código Integral da Suíte de Testes *",
        placeholder="def test_login_ok():\n    assert authenticate('user', 'pass') is True",
        height=160
    )

    st.divider()

    st.subheader("Seção E — Escopo e Comportamento Esperado")
    col_e1, col_e2 = st.columns([1, 1])
    with col_e1:
        analysis_scope = st.text_input("Escopo da Análise *", placeholder="Ex: autenticacao_e_bloqueio")
    with col_e2:
        expected_behavior = st.text_input("Comportamento Esperado Sintetizado", placeholder="Ex: Bloquear após 5 falhas")

    st.divider()

    st.subheader("Seção F — Metadados e Particionamento")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        split_group = st.text_input("Grupo de Separação (Split Group) *", placeholder="Ex: auth_service_v1", help="Usado para particionamento de treino sem data leakage")
    with col_f2:
        source_type = st.selectbox("Origem dos Dados", options=[st.value for st in SourceType])
    with col_f3:
        source_reference = st.text_input("Referência da Origem", placeholder="Ex: Issue #42 ou PR #108")

    st.divider()
    submitted = st.form_submit_button("💾 Salvar Exemplo Base", type="primary", use_container_width=True)

if submitted:
    if not title or not project_name or not requirements_text or not test_suite_text or not analysis_scope or not split_group:
        st.error("Por favor, preencha todos os campos obrigatórios marcados com asterisco (*).")
    else:
        try:
            ex_data = ExampleCreate(
                title=title,
                project_name=project_name,
                description=description or "",
                requirements_text=requirements_text,
                source_code=source_code or "",
                source_language=source_language,
                test_framework=test_framework,
                test_suite_text=test_suite_text,
                test_format=test_format,
                expected_behavior=expected_behavior or "",
                analysis_scope=analysis_scope,
                split_group=split_group,
                source_type=SourceType(source_type),
                source_reference=source_reference or "",
                initial_gaps=[]
            )
            created = example_service.create_example(ex_data)
            st.success(f"Exemplo cadastrado com sucesso com ID público: {created.public_id}!")
            st.info("Você já pode visualizar e adicionar lacunas detalhadas a este exemplo na página do Explorador de Dataset.")
        except ValueError as ve:
            st.error(f"Erro ao salvar: {str(ve)}")
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")
