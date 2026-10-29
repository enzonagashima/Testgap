"""Dataset explorer, search, filter, inspection, and review workflows."""
import streamlit as st
import pandas as pd

from testgap.services.example_service import ExampleService
from testgap.services.category_service import CategoryService
from testgap.services.review_service import ReviewService
from testgap.enums import ReviewStatus
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import (
    render_header, render_status_badge, render_severity_badge, render_empty_state
)

st.set_page_config(page_title="TestGap — Dataset", page_icon="📊", layout="wide")
apply_custom_styles()

example_service = ExampleService()
category_service = CategoryService()
review_service = ReviewService()

render_header("Explorador de Dataset", "Consulte, filtre, revise e gerencie exemplos de teste e suas lacunas")

# Sidebar Filters
with st.sidebar:
    st.header("Filtros do Dataset")
    search_query = st.text_input("🔍 Busca textual", placeholder="Título, ID, requisitos...")

    all_projects = example_service.get_all_projects()
    project_filter = st.selectbox("Projeto", options=["Todos"] + all_projects)

    status_options = ["Todos", "pending", "approved", "rejected", "needs_revision"]
    status_filter = st.selectbox("Estado de Revisão", options=status_options)

    categories = category_service.list_categories(include_inactive=True)
    cat_options = {"Todas": None}
    for c in categories:
        cat_options[f"{c.name} ({c.code})"] = c.id
    cat_filter_label = st.selectbox("Categoria de Lacuna", options=list(cat_options.keys()))
    cat_filter_id = cat_options[cat_filter_label]

    gaps_presence = st.radio("Presença de Lacunas", options=["Todos", "Apenas com Lacunas", "Sem Lacunas"], horizontal=True)

    page_size = st.selectbox("Itens por página", options=[10, 20, 50], index=1)

# Map filters
has_gaps_param = None
if gaps_presence == "Apenas com Lacunas":
    has_gaps_param = True
elif gaps_presence == "Sem Lacunas":
    has_gaps_param = False

# Session state for pagination
if "page_num" not in st.session_state:
    st.session_state.page_num = 1

offset = (st.session_state.page_num - 1) * page_size

examples, total_count = example_service.list_examples(
    search=search_query if search_query else None,
    project=project_filter if project_filter != "Todos" else None,
    review_status=status_filter if status_filter != "Todos" else None,
    category_id=cat_filter_id,
    has_gaps=has_gaps_param,
    limit=page_size,
    offset=offset
)

st.caption(f"Exibindo {len(examples)} de {total_count} exemplos encontrados.")

if not examples:
    render_empty_state("Nenhum registro encontrado", "Tente ajustar os filtros ou a busca textual na barra lateral.")
else:
    # Table Representation
    table_rows = []
    for ex in examples:
        confirmed_count = sum(1 for g in ex.gaps if g.status.value == "confirmed")
        table_rows.append({
            "ID": ex.public_id,
            "Título": ex.title,
            "Projeto": ex.project_name,
            "Linguagem": ex.source_language,
            "Framework": ex.test_framework,
            "Qtd. Lacunas": f"{confirmed_count} confirmada(s)",
            "Status": ex.review_status.value,
            "Split": ex.split_group,
            "Atualizado": ex.updated_at[:16].replace("T", " ")
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Pagination controls
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p1:
        if st.button("⬅️ Página Anterior", disabled=(st.session_state.page_num <= 1)):
            st.session_state.page_num -= 1
            st.rerun()
    with col_p2:
        st.write(f"<center>Página <b>{st.session_state.page_num}</b> de <b>{total_pages}</b></center>", unsafe_allow_html=True)
    with col_p3:
        if st.button("Próxima Página ➡️", disabled=(st.session_state.page_num >= total_pages)):
            st.session_state.page_num += 1
            st.rerun()

    st.divider()

    # Detail & Action Inspector
    st.subheader("🔍 Inspeção e Curadoria de Exemplo")
    selected_public_id = st.selectbox(
        "Selecione um exemplo para inspecionar, revisar ou duplicar:",
        options=[ex.public_id for ex in examples],
        format_func=lambda pid: f"{pid} — {next(e.title for e in examples if e.public_id == pid)}"
    )

    if selected_public_id:
        target = next(e for e in examples if e.public_id == selected_public_id)

        # Status & Metadata summary
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f"**Status de Revisão:**\n{render_status_badge(target.review_status.value)}", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"**Projeto:**\n`{target.project_name}`")
        with col_m3:
            st.markdown(f"**Split Group:**\n`{target.split_group}`")
        with col_m4:
            st.markdown(f"**Origem:**\n`{target.source_type.value}`")

        # Tabs for code and details
        tab_req, tab_src, tab_test, tab_gaps, tab_hist = st.tabs([
            "📋 Requisitos", "💻 Código-Fonte", "🧪 Suíte de Testes",
            f"🎯 Lacunas ({len(target.gaps)})", "📜 Histórico de Revisão"
        ])

        with tab_req:
            st.markdown("#### Requisitos e Regras de Negócio")
            st.text_area("Requisitos", target.requirements_text, height=180, disabled=True, label_visibility="collapsed")
            if target.description:
                st.caption(f"Contexto: {target.description}")

        with tab_src:
            st.markdown(f"#### Código-Fonte ({target.source_language})")
            if target.source_code:
                st.code(target.source_code, language=target.source_language)
            else:
                st.info("Nenhum código-fonte fornecido para este exemplo.")

        with tab_test:
            st.markdown(f"#### Suíte de Testes ({target.test_format} / {target.test_framework})")
            st.code(target.test_suite_text, language="python")

        with tab_gaps:
            st.markdown("#### Lacunas Identificadas")
            if not target.gaps:
                st.info("Nenhuma lacuna registrada para este exemplo (exemplo negativo ou totalmente coberto).")
            else:
                for idx, gap in enumerate(target.gaps, 1):
                    with st.expander(f"{gap.gap_code}: {gap.title} ({gap.severity.value.upper()})", expanded=True):
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"**Categoria:** {gap.category_name}")
                        c2.markdown(f"**Severidade:** {render_severity_badge(gap.severity.value)}", unsafe_allow_html=True)
                        c3.markdown(f"**Confiança:** {gap.confidence * 100:.0f}%")

                        st.markdown(f"**Descrição do Comportamento Não Coberto:**\n{gap.description}")
                        if gap.requirement_reference:
                            st.caption(f"Referência ao Requisito: {gap.requirement_reference}")
                        if gap.evidence:
                            st.markdown(f"**Evidência:** {gap.evidence}")

                        st.markdown("**Caso de Teste Sugerido:**")
                        st.code(gap.suggested_test, language="python")
                        st.markdown(f"**Resultado Esperado:** {gap.expected_result}")

        with tab_hist:
            st.markdown("#### Histórico de Alterações de Revisão")
            hist_records = review_service.get_review_history(target.id)
            if not hist_records:
                st.info("Nenhuma alteração de status registrada no histórico.")
            else:
                hist_data = [
                    {
                        "De": h.previous_status or "—",
                        "Para": h.new_status,
                        "Origem": h.changed_by,
                        "Observação": h.review_note or "—",
                        "Data (UTC)": h.created_at[:19].replace("T", " ")
                    }
                    for h in hist_records
                ]
                st.dataframe(pd.DataFrame(hist_data), use_container_width=True, hide_index=True)

        st.write("")
        st.markdown("#### Ações de Curadoria")

        # Action bar: Review state transitions
        c_act1, c_act2, c_act3, c_act4, c_act5 = st.columns([1.5, 1.2, 1.2, 1.2, 1.2])

        review_note = st.text_input("Nota / Justificativa de revisão (opcional):", key="review_note_input")

        with c_act1:
            if st.button("✅ Aprovar Exemplo", use_container_width=True, type="primary"):
                review_service.update_status(target.id, ReviewStatus.APPROVED, review_note=review_note)
                st.success("Exemplo aprovado com sucesso!")
                st.rerun()

        with c_act2:
            if st.button("⚠️ Solicitar Ajuste", use_container_width=True):
                review_service.update_status(target.id, ReviewStatus.NEEDS_REVISION, review_note=review_note)
                st.warning("Marcado para revisão!")
                st.rerun()

        with c_act3:
            if st.button("❌ Rejeitar", use_container_width=True):
                review_service.update_status(target.id, ReviewStatus.REJECTED, review_note=review_note)
                st.error("Exemplo rejeitado!")
                st.rerun()

        with c_act4:
            if st.button("📋 Duplicar Rascunho", use_container_width=True):
                clone = example_service.duplicate_as_draft(target.id)
                st.success(f"Criado novo rascunho com ID {clone.public_id}!")
                st.rerun()

        with c_act5:
            confirm_del = st.checkbox("Confirmar exclusão", key=f"del_chk_{target.id}")
            if st.button("🗑️ Excluir", disabled=not confirm_del, use_container_width=True):
                example_service.delete_example(target.id)
                st.success("Exemplo excluído permanentemente.")
                st.rerun()
