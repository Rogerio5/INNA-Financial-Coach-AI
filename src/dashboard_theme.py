"""
Tema visual compartilhado dos dashboards administrativos da INNA.

Aplica contraste escuro aos componentes nativos do Streamlit,
incluindo tabelas, JSON, inputs, upload, expanders e botões.
"""

from __future__ import annotations


def apply_admin_dark_theme() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
            --inna-bg: #050d18;
            --inna-bg-secondary: #071525;
            --inna-card: #0a1d32;
            --inna-card-hover: #102a46;
            --inna-border: #28557d;
            --inna-border-soft: #173852;
            --inna-text: #ffffff;
            --inna-muted: #c7d4e2;
            --inna-accent: #38bdf8;
        }

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background-color: var(--inna-bg) !important;
            color: var(--inna-text) !important;
        }

        [data-testid="stHeader"] {
            background-color: rgba(5, 13, 24, 0.96) !important;
        }

        [data-testid="stToolbar"] {
            color: var(--inna-text) !important;
        }

        [data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div {
            background-color: var(--inna-bg-secondary) !important;
            color: var(--inna-text) !important;
        }

        h1,
        h2,
        h3,
        h4,
        h5,
        h6,
        p,
        label,
        strong,
        small,
        li {
            color: var(--inna-text);
        }

        [data-testid="stCaptionContainer"],
        [data-testid="stMarkdownContainer"] small {
            color: var(--inna-muted) !important;
        }

        div[data-testid="stMetric"] {
            background-color: var(--inna-card) !important;
            border: 1px solid var(--inna-border) !important;
            border-radius: 14px !important;
            padding: 14px !important;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricDelta"] {
            color: var(--inna-text) !important;
        }

        div[data-testid="stExpander"] {
            background-color: var(--inna-card) !important;
            border: 1px solid var(--inna-border-soft) !important;
            border-radius: 10px !important;
        }

        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary span {
            color: var(--inna-text) !important;
        }

        div[data-testid="stFileUploader"] {
            background-color: var(--inna-card) !important;
            border: 1px solid var(--inna-border-soft) !important;
            border-radius: 12px !important;
            padding: 10px !important;
        }

        div[data-testid="stFileUploader"] section {
            background-color: var(--inna-bg-secondary) !important;
            border: 1px dashed var(--inna-border) !important;
            color: var(--inna-text) !important;
        }

        div[data-testid="stFileUploader"] section span,
        div[data-testid="stFileUploader"] section small {
            color: var(--inna-muted) !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stDateInput"] input,
        div[data-baseweb="select"] > div {
            background-color: var(--inna-card) !important;
            color: var(--inna-text) !important;
            border-color: var(--inna-border) !important;
        }

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #91a4b8 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: var(--inna-card) !important;
            color: var(--inna-text) !important;
        }

        li[role="option"] {
            background-color: var(--inna-card) !important;
            color: var(--inna-text) !important;
        }

        li[role="option"]:hover {
            background-color: var(--inna-card-hover) !important;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"],
        div[data-testid="stDataEditor"] {
            background-color: var(--inna-bg-secondary) !important;
            border: 1px solid var(--inna-border-soft) !important;
            border-radius: 9px !important;
            overflow: hidden !important;
        }

        div[data-testid="stDataFrame"] > div,
        div[data-testid="stDataEditor"] > div {
            background-color: var(--inna-bg-secondary) !important;
        }

        div[data-testid="stTable"] table {
            background-color: var(--inna-bg-secondary) !important;
            color: var(--inna-text) !important;
        }

        div[data-testid="stTable"] th {
            background-color: #10243a !important;
            color: var(--inna-text) !important;
            border-color: var(--inna-border-soft) !important;
        }

        div[data-testid="stTable"] td {
            background-color: #081726 !important;
            color: var(--inna-text) !important;
            border-color: var(--inna-border-soft) !important;
        }

        div[data-testid="stJson"],
        div[data-testid="stCode"],
        div[data-testid="stCodeBlock"],
        pre {
            background-color: #030914 !important;
            color: var(--inna-text) !important;
            border-color: var(--inna-border-soft) !important;
        }

        div[data-testid="stJson"] *,
        div[data-testid="stCode"] *,
        div[data-testid="stCodeBlock"] *,
        pre *,
        code {
            color: var(--inna-text) !important;
        }

        div[data-testid="stAlertContainer"] {
            color: var(--inna-text) !important;
            border-radius: 9px !important;
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"],
        button[kind="primary"] {
            background-color: var(--inna-card) !important;
            color: var(--inna-text) !important;
            border: 1px solid var(--inna-border) !important;
            border-radius: 9px !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[kind="secondary"]:hover,
        button[kind="primary"]:hover {
            background-color: var(--inna-card-hover) !important;
            color: var(--inna-text) !important;
            border-color: var(--inna-accent) !important;
        }

        .stButton > button p,
        .stDownloadButton > button p {
            color: var(--inna-text) !important;
        }

        hr {
            border-color: var(--inna-border-soft) !important;
        }

        a {
            color: var(--inna-accent) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


__all__ = [
    "apply_admin_dark_theme",
]
