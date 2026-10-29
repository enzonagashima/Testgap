"""Custom styling and CSS injection for TestGap Streamlit UI."""
import streamlit as st


def apply_custom_styles() -> None:
    """Inject polished technical theme CSS into Streamlit page."""
    st.markdown(
        """
        <style>
        /* General page layout */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }
        
        /* Metric Card styling */
        .tg-metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }
        .tg-metric-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .tg-metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0F172A;
        }
        .tg-metric-desc {
            font-size: 0.8rem;
            color: #94A3B8;
            margin-top: 4px;
        }

        /* Status Pills */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            font-size: 0.78rem;
            font-weight: 600;
            border-radius: 12px;
            text-transform: uppercase;
        }
        .badge-approved { background-color: #DCFCE7; color: #166534; }
        .badge-pending { background-color: #FEF9C3; color: #854D0E; }
        .badge-rejected { background-color: #FEE2E2; color: #991B1B; }
        .badge-needs_revision { background-color: #FFEDD5; color: #9A3412; }

        /* Severity Pills */
        .badge-critical { background-color: #FFE4E6; color: #9F1239; }
        .badge-high { background-color: #FEF3C7; color: #92400E; }
        .badge-medium { background-color: #E0F2FE; color: #075985; }
        .badge-low { background-color: #F1F5F9; color: #334155; }
        .badge-informational { background-color: #ECFDF5; color: #065F46; }

        /* Code & Monospace areas */
        .stCodeBlock {
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
