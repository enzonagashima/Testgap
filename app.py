"""TestGap — Main Entry Point and Executive Dashboard."""
import streamlit as st
import pandas as pd
from pathlib import Path

from testgap.config import DB_PATH
from testgap.database import default_db
from testgap.services.statistics_service import StatisticsService
from testgap.services.quality_service import QualityService
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import render_header, render_metric_card, render_status_badge, render_empty_state

# Page Config
st.set_page_config(
    page_title="TestGap — Início",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

# Ensure migrations on startup
default_db.run_migrations()

# Initialize services
stats_service = StatisticsService()
quality_service = QualityService()

render_header(
    "TestGap Dataset",
    "Plataforma Local de Curadoria e Engenharia de Dados para Lacunas de Testes em IA"
)

# Sidebar System Info
with st.sidebar:
    st.title("TestGap")
    st.caption("Versão 0.1.0 • Ambiente Local Windows")
    st.divider()
    st.markdown(f"**Banco SQLite:**\n`{DB_PATH.name}`")
    st.markdown(f"**Status:** Ativo")
    st.divider()
    st.page_link("app.py", label="Visão Geral", icon="🏠")
    st.page_link("pages/1_Dataset.py", label="Explorador de Dados", icon="📊")
    st.page_link("pages/2_Adicionar_Exemplo.py", label="Cadastrar Exemplo", icon="➕")
    st.page_link("pages/3_Categorias.py", label="Categorias", icon="🏷️")
    st.page_link("pages/4_Estatisticas.py", label="Estatísticas", icon="📈")
    st.page_link("pages/5_Qualidade_Dados.py", label="Auditoria de Qualidade", icon="🛡️")
    st.page_link("pages/6_Configuracoes.py", label="Configurações", icon="⚙️")

# Fetch Real Metrics
stats = stats_service.get_summary_metrics()

if stats["total_examples"] == 0:
    render_empty_state(
        "Nenhum exemplo cadastrado",
        "O banco de dados SQLite está pronto e inicializado, mas não contém registros ainda. "
        "Você pode criar um exemplo manualmente ou gerar dados de demonstração.",
        icon="🚀"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Criar Primeiro Exemplo", type="primary", use_container_width=True):
            st.switch_page("pages/2_Adicionar_Exemplo.py")
    with col2:
        if st.button("🌱 Popular com Dados de Demonstração (Seed)", use_container_width=True):
            from scripts.seed_demo_data import run_seed
            run_seed()
            st.success("Dados de demonstração inseridos com sucesso!")
            st.rerun()
else:
    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    render_metric_card(col1, "Total de Exemplos", stats["total_examples"], "Registros no SQLite")
    render_metric_card(col2, "Aprovados", stats["approved_count"], "Prontos para treino")
    render_metric_card(col3, "Pendentes", stats["pending_count"], "Aguardando revisão")
    render_metric_card(col4, "Com Lacunas", stats["with_gaps_count"], "has_gaps = True")
    render_metric_card(col5, "Total de Lacunas", stats["total_gaps"], "Gaps identificados")

    st.write("")

    # Visual Charts & Breakdown
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Distribuição de Lacunas por Categoria")
        if stats["gaps_by_category"]:
            cat_df = pd.DataFrame(
                list(stats["gaps_by_category"].items()),
                columns=["Categoria", "Lacunas"]
            ).sort_values("Lacunas", ascending=True)
            st.bar_chart(cat_df.set_index("Categoria"), horizontal=True, color="#3B82F6")
        else:
            st.info("Nenhuma lacuna registrada.")

    with col_right:
        st.subheader("Distribuição por Severidade")
        if stats["gaps_by_severity"]:
            sev_df = pd.DataFrame(
                list(stats["gaps_by_severity"].items()),
                columns=["Severidade", "Total"]
            )
            st.bar_chart(sev_df.set_index("Severidade"), color="#F59E0B")
        else:
            st.info("Nenhuma lacuna registrada.")

    st.divider()

    # Bottom Row: Quality Alert Box & Recent Changes
    col_bottom_left, col_bottom_right = st.columns([1, 1])

    with col_bottom_left:
        st.subheader("Status de Qualidade do Dataset")
        latest_audit = quality_service.get_latest_report()
        if latest_audit:
            c1, c2, c3 = st.columns(3)
            c1.metric("Examinados", latest_audit.total_examined)
            c2.metric("Erros", latest_audit.total_errors, delta_color="inverse")
            c3.metric("Avisos", latest_audit.total_warnings, delta_color="inverse")
            st.caption(f"Última auditoria realizada em: {latest_audit.audit_date[:19].replace('T', ' ')} UTC")
        else:
            st.info("Nenhuma auditoria recente executada.")

        if st.button("🛡️ Executar Auditoria Completa Agora"):
            st.switch_page("pages/5_Qualidade_Dados.py")

    with col_bottom_right:
        st.subheader("Últimas Alterações")
        if stats["recent_examples"]:
            recent_rows = []
            for r in stats["recent_examples"]:
                recent_rows.append({
                    "ID": r["public_id"],
                    "Título": r["title"],
                    "Projeto": r["project_name"],
                    "Status": r["review_status"]
                })
            st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum histórico recente.")
