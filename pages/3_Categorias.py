"""Taxonomy categories management page."""
import streamlit as st
import pandas as pd

from testgap.services.category_service import CategoryService
from testgap.schemas import CategoryCreate
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import render_header

st.set_page_config(page_title="TestGap — Categorias", page_icon="🏷️", layout="wide")
apply_custom_styles()

cat_service = CategoryService()
render_header("Taxonomia e Categorias", "Gerencie as categorias de lacunas de testes utilizadas na classificação")

categories = cat_service.list_categories(include_inactive=True)

# Table summary
cat_rows = []
for c in categories:
    gap_count = cat_service.repo.count_gaps(c.id)
    cat_rows.append({
        "ID": c.id,
        "Código": c.code,
        "Nome": c.name,
        "Descrição": c.description,
        "Status": "Ativa" if c.is_active else "Inativa",
        "Lacunas Vinculadas": gap_count
    })

df = pd.DataFrame(cat_rows)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("➕ Adicionar Nova Categoria")
    with st.form("new_category_form", clear_on_submit=True):
        new_code = st.text_input("Código Único *", placeholder="Ex: concurrency_races")
        new_name = st.text_input("Nome em Português *", placeholder="Ex: Concorrência e Condições de Corrida")
        new_desc = st.text_area("Descrição do Critério *", placeholder="Descreva quando classificar uma lacuna nesta categoria...")
        submit_cat = st.form_submit_button("Cadastrar Categoria", type="primary", use_container_width=True)

    if submit_cat:
        if not new_code or not new_name or not new_desc:
            st.error("Todos os campos da categoria são obrigatórios.")
        else:
            try:
                cat_service.create_category(CategoryCreate(
                    code=new_code.strip().lower(),
                    name=new_name.strip(),
                    description=new_desc.strip(),
                    is_active=True
                ))
                st.success(f"Categoria '{new_name}' criada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {str(e)}")

with col_right:
    st.subheader("⚙️ Alternar Ativação / Exclusão")
    cat_to_manage = st.selectbox(
        "Selecione uma categoria:",
        options=categories,
        format_func=lambda c: f"{c.name} ({'Ativa' if c.is_active else 'Inativa'})"
    )

    if cat_to_manage:
        gap_count = cat_service.repo.count_gaps(cat_to_manage.id)
        st.write(f"**Lacunas associadas atualmente:** {gap_count}")

        c_act1, c_act2 = st.columns(2)
        with c_act1:
            if cat_to_manage.is_active:
                if st.button("⏸️ Desativar Categoria", use_container_width=True):
                    cat_service.toggle_category(cat_to_manage.id, False)
                    st.warning("Categoria desativada.")
                    st.rerun()
            else:
                if st.button("▶️ Reativar Categoria", use_container_width=True):
                    cat_service.toggle_category(cat_to_manage.id, True)
                    st.success("Categoria reativada!")
                    st.rerun()

        with c_act2:
            confirm_cat_del = st.checkbox("Confirmar exclusão", key="chk_cat_del")
            if st.button("🗑️ Excluir Categoria", disabled=not confirm_cat_del, use_container_width=True):
                try:
                    cat_service.delete_category(cat_to_manage.id)
                    st.success("Categoria excluída com sucesso!")
                    st.rerun()
                except ValueError as ve:
                    st.error(str(ve))
