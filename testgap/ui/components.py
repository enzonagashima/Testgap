"""Reusable UI components and widgets for TestGap Streamlit pages."""
import streamlit as st
from typing import Any, Optional


def render_header(title: str, subtitle: str = "") -> None:
    """Render standardized page header."""
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sub-header">{subtitle}</div>', unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Return HTML badge for review status."""
    labels = {
        "approved": "Aprovado",
        "pending": "Pendente",
        "rejected": "Rejeitado",
        "needs_revision": "Requer Revisão"
    }
    label = labels.get(status, status)
    return f'<span class="badge badge-{status}">{label}</span>'


def render_severity_badge(severity: str) -> str:
    """Return HTML badge for gap severity."""
    labels = {
        "critical": "Crítico",
        "high": "Alto",
        "medium": "Médio",
        "low": "Baixo",
        "informational": "Informativo"
    }
    label = labels.get(severity, severity)
    return f'<span class="badge badge-{severity}">{label}</span>'


def render_metric_card(col, label: str, value: Any, desc: str = "") -> None:
    """Render metric card inside a streamlit column."""
    with col:
        st.markdown(
            f"""
            <div class="tg-metric-card">
                <div class="tg-metric-label">{label}</div>
                <div class="tg-metric-value">{value}</div>
                {f'<div class="tg-metric-desc">{desc}</div>' if desc else ''}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_empty_state(title: str, message: str, icon: str = "ℹ️") -> None:
    """Render empty state container when no records are available."""
    st.info(f"{icon} **{title}**\n\n{message}")
