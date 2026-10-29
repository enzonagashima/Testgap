"""Statistics, dataset distributions, and analytical metrics."""
import streamlit as st
import pandas as pd

from testgap.services.statistics_service import StatisticsService
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import render_header, render_metric_card

st.set_page_config(page_title="TestGap — Estatísticas", page_icon="📈", layout="wide")
apply_custom_styles()

stats_service = StatisticsService()
render_header("Estatísticas e Distribuições", "Visualização da distribuição dos dados, balanceamento e progresso da curadoria")

stats = stats_service.get_summary_metrics()

if stats["total_examples"] == 0:
    st.info("Nenhum dado disponível para análise estatística no momento.")
else:
    # Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    render_metric_card(c1, "Total de Registros", stats["total_examples"])
    render_metric_card(c2, "Total de Lacunas", stats["total_gaps"])
    render_metric_card(c3, "Split Groups Únicos", len(stats["examples_by_split_group"]))
    render_metric_card(c4, "Projetos Distintos", len(stats["examples_by_project"]))

    st.divider()

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Lacunas por Categoria")
        if stats["gaps_by_category"]:
            df_cat = pd.DataFrame(
                list(stats["gaps_by_category"].items()),
                columns=["Categoria", "Lacunas"]
            ).sort_values("Lacunas", ascending=True)
            st.bar_chart(df_cat.set_index("Categoria"), horizontal=True, color="#2563EB")

    with col_g2:
        st.subheader("Lacunas por Severidade")
        if stats["gaps_by_severity"]:
            df_sev = pd.DataFrame(
                list(stats["gaps_by_severity"].items()),
                columns=["Severidade", "Total"]
            )
            st.bar_chart(df_sev.set_index("Severidade"), color="#D97706")

    st.divider()

    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.subheader("Balanceamento por Split Group")
        if stats["examples_by_split_group"]:
            df_split = pd.DataFrame(
                list(stats["examples_by_split_group"].items()),
                columns=["Split Group", "Exemplos"]
            )
            st.bar_chart(df_split.set_index("Split Group"), color="#059669")

    with col_g4:
        st.subheader("Status de Revisão")
        rev_data = {
            "Aprovado": stats["approved_count"],
            "Pendente": stats["pending_count"],
            "Rejeitado": stats["rejected_count"],
            "Requer Revisão": stats["needs_revision_count"]
        }
        df_rev = pd.DataFrame(list(rev_data.items()), columns=["Status", "Total"])
        st.bar_chart(df_rev.set_index("Status"), color="#7C3AED")
