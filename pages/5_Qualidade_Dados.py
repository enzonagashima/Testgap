"""Data quality auditing, anomaly detection, and validation engine interface."""
import streamlit as st
import pandas as pd

from testgap.services.quality_service import QualityService
from testgap.ui.styles import apply_custom_styles
from testgap.ui.components import render_header, render_metric_card

st.set_page_config(page_title="TestGap — Qualidade", page_icon="🛡️", layout="wide")
apply_custom_styles()

quality_service = QualityService()
render_header("Auditoria de Qualidade do Dataset", "Verificação em duas camadas (regras estruturais e heurísticas semânticas)")

# Action Bar: Trigger Audit
c_btn, c_info = st.columns([1, 3])
with c_btn:
    if st.button("🛡️ Executar Nova Auditoria", type="primary", use_container_width=True):
        with st.spinner("Auditando registros e regras de qualidade..."):
            quality_service.run_full_audit()
        st.success("Auditoria concluída com sucesso!")
        st.rerun()

latest_report = quality_service.get_latest_report()

if not latest_report:
    st.info("Nenhuma auditoria executada até o momento. Clique no botão acima para iniciar.")
else:
    # Summary KPI
    col1, col2, col3, col4 = st.columns(4)
    render_metric_card(col1, "Total Examinado", latest_report.total_examined, "Exemplos inspecionados")
    render_metric_card(col2, "Erros Bloqueantes", latest_report.total_errors, "Impedem exportação para IA")
    render_metric_card(col3, "Avisos de Atenção", latest_report.total_warnings, "Sugerem revisão manual")
    render_metric_card(col4, "Observações", latest_report.total_infos, "Sugestões de melhoria")

    st.caption(f"Relatório gerado em: {latest_report.audit_date[:19].replace('T', ' ')} UTC • Versão das regras: {latest_report.rules_version}")

    st.divider()

    st.subheader("Não-Conformidades e Alertas Detectados")

    if not latest_report.issues:
        st.success("🎉 Nenhum erro ou aviso encontrado! O dataset obedece 100% às regras de qualidade.")
    else:
        # Filter issues by severity
        sev_filter = st.multiselect(
            "Filtrar por Gravidade:",
            options=["error", "warning", "info"],
            default=["error", "warning"]
        )

        filtered_issues = [i for i in latest_report.issues if i.severity.value in sev_filter]

        issues_data = []
        for issue in filtered_issues:
            issues_data.append({
                "Gravidade": issue.severity.value.upper(),
                "Exemplo": issue.example_id or "Geral",
                "Lacuna": issue.gap_id or "—",
                "Regra": issue.rule_id,
                "Mensagem": issue.message,
                "Detalhes": issue.details or ""
            })

        st.dataframe(pd.DataFrame(issues_data), use_container_width=True, hide_index=True)
