import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

HERO_IMAGE = ROOT_DIR / "assets" / "inna_hero.png"
HERO_IMAGE = ROOT_DIR / "assets" / "inna_hero.png"
DASHBOARD_ADMIN_URL = "https://inna-dashboard-streamlit.onrender.com"

INNA_USER_EMAIL = os.getenv("INNA_USER_EMAIL", "usuario@inna.ai")
INNA_USER_PASSWORD = os.getenv("INNA_USER_PASSWORD", "usuario123")
INNA_ADMIN_EMAIL = os.getenv("INNA_ADMIN_EMAIL", "admin@inna.ai")
INNA_ADMIN_PASSWORD = os.getenv("INNA_ADMIN_PASSWORD", "admin123")

import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import requests

from src.api_client import gerar_diagnostico_api, enviar_feedback_api, baixar_relatorio_pdf_api, buscar_historico_usuario_api, verificar_api_online, enviar_relatorio_email


st.set_page_config(
    page_title="INNA Financial Coach AI",
    page_icon="💰",
    layout="wide",
)


def apply_inna_dark_form_fix():
    st.markdown("""
    <style>
    /* ===== INPUTS / TEXTAREA / NUMBER INPUT ===== */
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #0d2747 !important;
        border: 1px solid #c9a84f !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="textarea"] textarea {
        background-color: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #b8c7d9 !important;
        opacity: 1 !important;
    }

    /* ===== NUMBER INPUT BOTÕES + / - ===== */
    button[aria-label="Increment"],
    button[aria-label="Decrement"] {
        background-color: #0b2442 !important;
        color: #ffffff !important;
        border-left: 1px solid #c9a84f !important;
    }

    /* ===== SELECTBOX ===== */
    div[data-baseweb="select"] > div {
        background-color: #0d2747 !important;
        border: 1px solid #c9a84f !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }

    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* ===== BOTÕES ===== */
    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #15365f, #0b2442) !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        padding: 0.65rem 1rem !important;
        opacity: 1 !important;
    }

    .stButton > button p,
    .stFormSubmitButton > button p,
    .stDownloadButton > button p,
    .stButton > button div,
    .stFormSubmitButton > button div,
    .stDownloadButton > button div,
    .stButton > button span,
    .stFormSubmitButton > button span,
    .stDownloadButton > button span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 800 !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #1d4679, #123055) !important;
        border: 1px solid #ffd76a !important;
    }

    .stButton > button:hover p,
    .stFormSubmitButton > button:hover p,
    .stDownloadButton > button:hover p,
    .stButton > button:hover span,
    .stFormSubmitButton > button:hover span,
    .stDownloadButton > button:hover span {
        color: #ffd76a !important;
        -webkit-text-fill-color: #ffd76a !important;
    }

    /* ===== BOTÃO DESABILITADO, MAS LEGÍVEL ===== */
    .stButton > button:disabled,
    .stFormSubmitButton > button:disabled,
    .stDownloadButton > button:disabled {
        background: #31465f !important;
        color: #f5f7fa !important;
        border: 1px solid #8fa3b8 !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }

    .stButton > button:disabled p,
    .stFormSubmitButton > button:disabled p,
    .stDownloadButton > button:disabled p,
    .stButton > button:disabled span,
    .stFormSubmitButton > button:disabled span,
    .stDownloadButton > button:disabled span {
        color: #f5f7fa !important;
        -webkit-text-fill-color: #f5f7fa !important;
        opacity: 1 !important;
        font-weight: 800 !important;
    }
    
.inna-pergunta-proximo-passo {
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #FFFFFF !important;
    margin-top: 14px !important;
    margin-bottom: 8px !important;
    line-height: 1.35 !important;
}


.fonte-inna-top {
    text-align: right !important;
    font-size: 12px !important;
    color: #9ca3af !important;
    font-weight: 700 !important;
    margin-bottom: 8px !important;
    opacity: 0.85 !important;
}

.inna-pergunta-proximo-passo {
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #FFFFFF !important;
    margin-top: 14px !important;
    margin-bottom: 8px !important;
    line-height: 1.35 !important;
}

</style>
    """, unsafe_allow_html=True)


apply_inna_dark_form_fix()




st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #ffffff 0%, #f5f7fb 100%);
}

[data-testid="stSidebar"] {
    background: #f0f4f8;
}

.block-container {
    padding-top: 1.2rem;
    max-width: 1320px;
    padding-left: 3rem;
    padding-right: 3rem;
}

.hero-wrapper {
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 22px 55px rgba(0,0,0,0.22);
    margin-bottom: 35px;
}

.title-main {
    font-size: 38px;
    font-weight: 900;
    color: #071C36;
    margin-top: 10px;
}

.subtitle {
    font-size: 19px;
    color: #42526E;
    margin-bottom: 20px;
}

.info-box {
    background: #EAF4FF;
    color: #113B63;
    border: 1px solid #C7E2FF;
    border-radius: 14px;
    padding: 16px;
    font-size: 15px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 27px;
    font-weight: 850;
    color: #071C36;
    margin-top: 35px;
    margin-bottom: 16px;
}

.text-normal {
    font-size: 16px;
    color: #334155;
    line-height: 1.7;
}

.feature-card {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 24px;
    min-height: 175px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
}

.feature-card h3 {
    color: #071C36;
    font-size: 21px;
    margin-bottom: 10px;
}

.feature-card p {
    color: #526173;
    font-size: 15px;
    line-height: 1.6;
}

.step-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 22px;
    border-left: 5px solid #D4AF37;
    box-shadow: 0 8px 22px rgba(0,0,0,0.06);
    min-height: 180px;
}

.step-card h3 {
    color: #D4AF37;
    font-size: 28px;
    margin-bottom: 6px;
}

.step-card h4 {
    color: #071C36;
    font-size: 20px;
    margin-bottom: 8px;
}

.step-card p {
    color: #526173;
    font-size: 14px;
}

.warning-box {
    background: #FFF8DF;
    color: #5C4300;
    border: 1px solid #F3DA8B;
    border-radius: 16px;
    padding: 18px;
    font-size: 15px;
    margin-top: 25px;
}

.cta-box {
    background: linear-gradient(135deg, #071C36, #0E3A73);
    color: white;
    border-radius: 24px;
    padding: 34px;
    text-align: center;
    margin-top: 35px;
    box-shadow: 0 18px 40px rgba(7, 28, 54, 0.25);
}

.cta-box h2 {
    color: white;
    font-size: 30px;
    margin-bottom: 10px;
}

.cta-box p {
    color: #D8E6F7;
    font-size: 16px;
}

.hero-wrapper img {
    width: 100%;
    border-radius: 24px;
}

.premium-badge {
    display: inline-block;
    background: linear-gradient(135deg, #071C36, #0E3A73);
    color: #F8D98B;
    border: 1px solid #D4AF37;
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 12px;
    box-shadow: 0 8px 20px rgba(7, 28, 54, 0.18);
}

/* ===== INNA FINAL VISUAL POLISH ===== */

.hero-wrapper {
    border-radius: 28px;
    overflow: hidden;
    box-shadow: 0 28px 70px rgba(7, 28, 54, 0.28);
    margin-bottom: 42px;
    border: 1px solid rgba(212, 175, 55, 0.35);
}

.hero-wrapper img {
    width: 100%;
    border-radius: 28px;
    display: block;
}

.title-main {
    font-size: 44px;
    font-weight: 950;
    color: #061A33;
    letter-spacing: -1.2px;
    margin-top: 18px;
    margin-bottom: 6px;
}

.subtitle {
    font-size: 21px;
    color: #34465F;
    margin-bottom: 26px;
}

.info-box {
    background: linear-gradient(135deg, #EAF4FF, #F7FBFF);
    color: #113B63;
    border: 1px solid #BBD9FF;
    border-radius: 18px;
    padding: 20px 24px;
    font-size: 17px;
    margin-bottom: 34px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
}

.section-title {
    font-size: 32px;
    font-weight: 900;
    color: #061A33;
    margin-top: 46px;
    margin-bottom: 22px;
    letter-spacing: -0.6px;
}

.text-normal {
    font-size: 18px;
    color: #28384D;
    line-height: 1.85;
}

.feature-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid #DDE7F3;
    border-radius: 24px;
    padding: 32px;
    min-height: 210px;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.feature-card h3 {
    color: #061A33;
    font-size: 24px;
    font-weight: 850;
    margin-bottom: 16px;
}

.feature-card p {
    color: #42526E;
    font-size: 17px;
    line-height: 1.75;
}

.step-card {
    background: #ffffff;
    border-radius: 24px;
    padding: 32px;
    border-left: 6px solid #D4AF37;
    box-shadow: 0 16px 42px rgba(7, 28, 54, 0.08);
    min-height: 235px;
}

.step-card h3 {
    color: #D4AF37;
    font-size: 34px;
    margin-bottom: 24px;
}

.step-card h4 {
    color: #061A33;
    font-size: 23px;
    margin-bottom: 18px;
}

.step-card p {
    color: #42526E;
    font-size: 16px;
    line-height: 1.65;
}

.warning-box {
    background: linear-gradient(135deg, #FFF8DF, #FFFDF4);
    color: #5C4300;
    border: 1px solid #E9C95F;
    border-radius: 20px;
    padding: 22px 26px;
    font-size: 17px;
    margin-top: 36px;
    box-shadow: 0 10px 26px rgba(212, 175, 55, 0.10);
}

.cta-box {
    background: radial-gradient(circle at top left, #164A86 0%, #071C36 42%, #061426 100%);
    color: white;
    border-radius: 30px;
    padding: 52px 34px;
    text-align: center;
    margin-top: 44px;
    box-shadow: 0 26px 70px rgba(7, 28, 54, 0.32);
    border: 1px solid rgba(212, 175, 55, 0.35);
}

.cta-box h2 {
    color: white;
    font-size: 38px;
    font-weight: 900;
    margin-bottom: 20px;
}

.cta-box p {
    color: #D8E6F7;
    font-size: 19px;
}

.premium-badge {
    display: inline-block;
    background: linear-gradient(135deg, #071C36, #0E3A73);
    color: #F8D98B;
    border: 1px solid #D4AF37;
    border-radius: 999px;
    padding: 10px 18px;
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 16px;
    box-shadow: 0 12px 28px rgba(7, 28, 54, 0.22);
}

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 22px;
    padding: 22px 24px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
}

div[data-testid="stMetricLabel"] {
    font-size: 16px;
    color: #334155;
}

div[data-testid="stMetricValue"] {
    font-size: 36px;
    color: #061A33;
    font-weight: 850;
}

.stButton > button {
    border-radius: 14px;
    height: 48px;
    font-weight: 700;
    border: 1px solid #D8E0EA;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.stButton > button:hover {
    border-color: #D4AF37;
    color: #071C36;
    box-shadow: 0 12px 26px rgba(7, 28, 54, 0.12);
}


.inna-hero-dynamic {
    background: radial-gradient(circle at top left, #123E75 0%, #071C36 42%, #04101F 100%);
    border-radius: 32px;
    padding: 34px;
    margin-bottom: 34px;
    border: 1px solid rgba(212, 175, 55, 0.35);
    box-shadow: 0 28px 70px rgba(7, 28, 54, 0.32);
}

.inna-hero-grid {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 34px;
    align-items: center;
}

.inna-portrait-box {
    border-radius: 28px;
    overflow: hidden;
    background: #061426;
    box-shadow: 0 22px 50px rgba(0,0,0,0.32);
}

.inna-portrait-box img {
    width: 100%;
    display: block;
    border-radius: 28px;
}

.inna-hero-content h1 {
    font-size: 64px;
    line-height: 1;
    margin: 0;
    color: #F7D88A;
    font-weight: 900;
    letter-spacing: -1px;
}

.inna-hero-content h2 {
    font-size: 36px;
    margin: 8px 0 6px 0;
    color: #ffffff;
    font-weight: 700;
}

.inna-hero-subtitle {
    font-size: 22px;
    color: #F7D88A;
    margin-bottom: 24px;
}

.inna-hero-description {
    font-size: 20px;
    color: #E6EEF8;
    line-height: 1.55;
    margin-bottom: 28px;
}

.inna-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.inna-hero-mini-card {
    border: 1px solid rgba(65, 153, 255, 0.42);
    background: rgba(4, 16, 31, 0.62);
    border-radius: 18px;
    padding: 18px;
    min-height: 132px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.18);
}

.inna-hero-mini-card .icon {
    font-size: 34px;
    margin-bottom: 8px;
}

.inna-hero-mini-card h3 {
    color: #ffffff;
    font-size: 18px;
    margin: 0 0 8px 0;
}

.inna-hero-mini-card p {
    color: #C9D7EA;
    font-size: 14px;
    line-height: 1.45;
    margin: 0;
}

@media (max-width: 900px) {
    .inna-hero-grid {
        grid-template-columns: 1fr;
    }

    .inna-hero-content h1 {
        font-size: 46px;
    }

    .inna-hero-content h2 {
        font-size: 28px;
    }

    .inna-feature-grid {
        grid-template-columns: 1fr;
    }
}


/* ===== INNA HERO DINÂMICO FINAL ===== */

.inna-hero-dynamic-final {
    background: radial-gradient(circle at top left, #123E75 0%, #071C36 42%, #04101F 100%);
    border-radius: 32px;
    padding: 34px;
    margin-bottom: 34px;
    border: 1px solid rgba(212, 175, 55, 0.38);
    box-shadow: 0 28px 70px rgba(7, 28, 54, 0.34);
}

.inna-hero-final-grid {
    display: grid;
    grid-template-columns: 0.85fr 1.15fr;
    gap: 34px;
    align-items: center;
}

.inna-hero-photo-card {
    border-radius: 28px;
    overflow: hidden;
    background: #061426;
    border: 1px solid rgba(212, 175, 55, 0.45);
    box-shadow: 0 22px 55px rgba(0,0,0,0.35);
}

.inna-hero-photo-card img {
    width: 100%;
    display: block;
    border-radius: 28px;
}

.inna-hero-text-side h1 {
    font-size: 72px;
    line-height: 0.95;
    margin: 0;
    color: #F7D88A;
    font-weight: 950;
    letter-spacing: -1px;
}

.inna-hero-text-side h2 {
    font-size: 38px;
    margin: 10px 0 8px 0;
    color: #ffffff;
    font-weight: 750;
}

.inna-hero-subtitle-final {
    font-size: 22px;
    color: #F7D88A;
    margin-bottom: 24px;
}

.inna-hero-description-final {
    font-size: 20px;
    color: #E6EEF8;
    line-height: 1.55;
    margin-bottom: 30px;
    max-width: 780px;
}

.inna-hero-cards-final {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.inna-hero-card-final {
    border: 1px solid rgba(65, 153, 255, 0.42);
    background: rgba(4, 16, 31, 0.66);
    border-radius: 20px;
    padding: 20px;
    min-height: 142px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.20);
}

.inna-hero-card-final .icon {
    font-size: 35px;
    margin-bottom: 10px;
}

.inna-hero-card-final h3 {
    color: #ffffff;
    font-size: 19px;
    margin: 0 0 8px 0;
    font-weight: 800;
}

.inna-hero-card-final p {
    color: #C9D7EA;
    font-size: 14px;
    line-height: 1.45;
    margin: 0;
}

@media (max-width: 900px) {
    .inna-hero-final-grid {
        grid-template-columns: 1fr;
    }

    .inna-hero-text-side h1 {
        font-size: 48px;
    }

    .inna-hero-text-side h2 {
        font-size: 28px;
    }

    .inna-hero-cards-final {
        grid-template-columns: 1fr;
    }
}


/* ==========================================
   MENU SUPERIOR RESPONSIVO MULTIIDIOMA
   ========================================== */

div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 58px !important;
    height: auto !important;
    padding: 8px 10px !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    line-height: 1.15 !important;
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: anywhere !important;
    text-align: center !important;
    border-radius: 16px !important;
}

/* Em telas menores, reduz um pouco mais a fonte */
@media (max-width: 1100px) {
    div[data-testid="stHorizontalBlock"] .stButton > button {
        font-size: 12px !important;
        padding: 7px 8px !important;
        min-height: 56px !important;
    }
}

@media (max-width: 800px) {
    div[data-testid="stHorizontalBlock"] .stButton > button {
        font-size: 11px !important;
        min-height: 52px !important;
    }
}

</style>
""", unsafe_allow_html=True)
APP_MENU_OPTIONS_USER = [
    "🏠 Início",
    "🧾 Diagnóstico",
    "📊 Panorama",
    "💬 Conversar",
    "📄 Relatório",
    "📚 Histórico",
    "⭐ Avaliar",
    "ℹ️ Sobre",
]

APP_MENU_OPTIONS_ADMIN = [
    "🏠 Início",
    "🧾 Diagnóstico",
    "📊 Panorama",
    "💬 Conversar",
    "📄 Relatório",
    "📚 Histórico",
    "⭐ Avaliar",
    "🔐 Admin Analytics",
    "ℹ️ Sobre",
]

APP_MENU_OPTIONS = APP_MENU_OPTIONS_USER


APP_LANG_LABELS = {
    "pt": "🇧🇷 Português Brasil",
    "en_us": "🇺🇸 English US",
    "en_gb": "🇬🇧 English UK",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
    "it": "🇮🇹 Italiano",
    "ro": "🇷🇴 Română",
    "uk": "🇺🇦 Українська",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "ch": "🇨🇭 Schweiz",
}

BROWSER_LANG_TO_APP_LANG = {
    "pt": "pt",
    "pt-br": "pt",
    "en": "en_us",
    "en-us": "en_us",
    "en-gb": "en_gb",
    "es": "es",
    "es-es": "es",
    "de": "de",
    "de-de": "de",
    "fr": "fr",
    "fr-fr": "fr",
    "it": "it",
    "it-it": "it",
    "ro": "ro",
    "ro-ro": "ro",
    "uk": "uk",
    "uk-ua": "uk",
    "ru": "ru",
    "ru-ru": "ru",
    "ar": "ar",
    "ar-sa": "ar",
    "de-ch": "ch",
    "fr-ch": "ch",
    "it-ch": "ch",
}

def detect_browser_language() -> str:
    browser_lang = streamlit_js_eval(
        js_expressions="navigator.language || navigator.userLanguage",
        key="browser_language",
    )

    if not browser_lang:
        return "pt"

    browser_lang = str(browser_lang).lower()
    short_lang = browser_lang.split("-")[0]

    return BROWSER_LANG_TO_APP_LANG.get(
        browser_lang,
        BROWSER_LANG_TO_APP_LANG.get(short_lang, "pt"),
    )


APP_TRANSLATIONS = {
    "pt": {
        "currency_notice": "Os valores devem ser informados em {currency}. A INNA não faz conversão cambial automática.",
        "estimated_balance": "Saldo estimado",
        "financial_score": "Score financeiro",
        "risk": "Risco",
        "income_commitment": "Comprometimento da renda",
        "reserve_months": "Meses de reserva",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnóstico financeiro com IA e plano de ação de 30 dias",
        "notice": "A INNA é uma educadora financeira. Ela não recomenda investimentos nem substitui um profissional certificado.",
        "api_offline": "A API da INNA está offline. Confirme se a API online está ativa.",
        "name": "Seu nome",
        "monthly_income": "Renda mensal",
        "fixed_expenses": "Gastos fixos mensais",
        "variable_expenses": "Gastos variáveis mensais",
        "debts": "Dívidas mensais",
        "savings": "Reserva atual",
        "goal": "Qual seu objetivo financeiro?",
        "default_goal": "Organizar minha vida financeira",
        "generate": "Gerar diagnóstico com a INNA",
        "loading": "Chamando a API da INNA e gerando diagnóstico com IA...",
        "saved": "Diagnóstico gerado e salvo via FastAPI com sucesso!",
        "success": "Diagnóstico gerado com sucesso!",
        "diagnosis": "### Diagnóstico",
        "plan": "### Plano de ação de 30 dias",
        "download_pdf": "📄 Baixar relatório em PDF",
        "email_title": "### 📧 Receber relatório por e-mail",
        "email_input": "Digite seu e-mail para receber o relatório PDF:",
        "email_button": "📧 Enviar relatório por e-mail",
        "email_invalid": "Digite um e-mail válido.",
        "email_success": "Relatório enviado por e-mail com sucesso!",
        "email_error": "Erro ao enviar relatório por e-mail",
        "pdf_error": "Não foi possível baixar o relatório pela API",
        "pdf_unavailable": "Relatório PDF indisponível: diagnóstico ainda não possui ID retornado pela API.",
        "feedback_title": "Feedback",
        "feedback_comment": "Comentário opcional",
        "feedback_placeholder": "Exemplo: o plano ficou claro, faltou mais detalhe, gostei da explicação...",
        "feedback_button": "Enviar feedback",
        "feedback_success": "Feedback registrado via FastAPI com sucesso. Obrigado por ajudar a evoluir a INNA!",
        "history_title": "Histórico individual",
        "history_name": "Nome para buscar histórico",
        "history_limit": "Quantidade máxima de registros",
        "history_button": "Buscar histórico",
        "history_empty": "Nenhum diagnóstico encontrado para esse nome.",
        "browser_translate_warning": "Para testar os idiomas corretamente, desative o tradutor automático do navegador.",
        "feedback_help": "Sua avaliação ajuda a melhorar a INNA e validar o projeto.",
        "feedback_question": "Essa resposta foi útil?",
        "yes": "Sim",
        "no": "Não",
        "history_help": "Consulte diagnósticos anteriores pelo nome do usuário. Essa área usa a FastAPI para buscar dados salvos no PostgreSQL.",
    },
    "en_us": {
        "currency_notice": "Enter values in {currency}. INNA does not automatically convert exchange rates.",
        "estimated_balance": "Estimated balance",
        "financial_score": "Financial score",
        "risk": "Risk",
        "income_commitment": "Income commitment",
        "reserve_months": "Savings months",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "AI financial diagnosis and 30-day action plan",
        "notice": "INNA is a financial educator. It does not recommend investments and does not replace a certified professional.",
        "api_offline": "The INNA API is offline. Please check if the online API is active.",
        "name": "Your name",
        "monthly_income": "Monthly income",
        "fixed_expenses": "Monthly fixed expenses",
        "variable_expenses": "Monthly variable expenses",
        "debts": "Monthly debt payments",
        "savings": "Current savings",
        "goal": "What is your financial goal?",
        "default_goal": "Organize my financial life",
        "generate": "Generate diagnosis with INNA",
        "loading": "Calling INNA API and generating AI diagnosis...",
        "saved": "Diagnosis generated and saved through FastAPI successfully!",
        "success": "Diagnosis generated successfully!",
        "diagnosis": "### Diagnosis",
        "plan": "### 30-day action plan",
        "download_pdf": "📄 Download PDF report",
        "email_title": "### 📧 Receive report by email",
        "email_input": "Enter your email to receive the PDF report:",
        "email_button": "📧 Send report by email",
        "email_invalid": "Enter a valid email.",
        "email_success": "Report sent by email successfully!",
        "email_error": "Error sending report by email",
        "pdf_error": "Could not download the report from the API",
        "pdf_unavailable": "PDF report unavailable: the diagnosis does not have an API ID yet.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optional comment",
        "feedback_placeholder": "Example: the plan was clear, I wanted more detail, I liked the explanation...",
        "feedback_button": "Send feedback",
        "feedback_success": "Feedback registered successfully through FastAPI. Thank you for helping INNA improve!",
        "history_title": "Individual history",
        "history_name": "Name to search history",
        "history_limit": "Maximum number of records",
        "history_button": "Search history",
        "history_empty": "No diagnosis found for this name.",
        "browser_translate_warning": "To test languages correctly, disable the browser automatic translator.",
        "feedback_help": "Your feedback helps improve INNA and validate the project.",
        "feedback_question": "Was this answer useful?",
        "yes": "Yes",
        "no": "No",
        "history_help": "Search previous diagnoses by user name. This area uses FastAPI to retrieve data saved in PostgreSQL.",
    },
    "en_gb": {
        "currency_notice": "Enter values in {currency}. INNA does not automatically convert exchange rates.",
        "estimated_balance": "Estimated balance",
        "financial_score": "Financial score",
        "risk": "Risk",
        "income_commitment": "Income commitment",
        "reserve_months": "Savings months",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "AI financial diagnosis and 30-day action plan",
        "notice": "INNA is a financial educator. It does not recommend investments and does not replace a certified professional.",
        "api_offline": "The INNA API is offline. Please check if the online API is active.",
        "name": "Your name",
        "monthly_income": "Monthly income",
        "fixed_expenses": "Monthly fixed expenses",
        "variable_expenses": "Monthly variable expenses",
        "debts": "Monthly debt payments",
        "savings": "Current savings",
        "goal": "What is your financial goal?",
        "default_goal": "Organise my financial life",
        "generate": "Generate diagnosis with INNA",
        "loading": "Calling INNA API and generating AI diagnosis...",
        "saved": "Diagnosis generated and saved through FastAPI successfully!",
        "success": "Diagnosis generated successfully!",
        "diagnosis": "### Diagnosis",
        "plan": "### 30-day action plan",
        "download_pdf": "📄 Download PDF report",
        "email_title": "### 📧 Receive report by email",
        "email_input": "Enter your email to receive the PDF report:",
        "email_button": "📧 Send report by email",
        "email_invalid": "Enter a valid email.",
        "email_success": "Report sent by email successfully!",
        "email_error": "Error sending report by email",
        "pdf_error": "Could not download the report from the API",
        "pdf_unavailable": "PDF report unavailable: the diagnosis does not have an API ID yet.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optional comment",
        "feedback_placeholder": "Example: the plan was clear, I wanted more detail, I liked the explanation...",
        "feedback_button": "Send feedback",
        "feedback_success": "Feedback registered successfully through FastAPI. Thank you for helping INNA improve!",
        "history_title": "Individual history",
        "history_name": "Name to search history",
        "history_limit": "Maximum number of records",
        "history_button": "Search history",
        "history_empty": "No diagnosis found for this name.",
        "browser_translate_warning": "To test languages correctly, disable the browser automatic translator.",
        "feedback_help": "Your feedback helps improve INNA and validate the project.",
        "feedback_question": "Was this answer useful?",
        "yes": "Yes",
        "no": "No",
        "history_help": "Search previous diagnoses by user name. This area uses FastAPI to retrieve data saved in PostgreSQL.",
    },
    "es": {
        "currency_notice": "Ingresa los valores en {currency}. INNA no convierte tipos de cambio automáticamente.",
        "estimated_balance": "Saldo estimado",
        "financial_score": "Puntuación financiera",
        "risk": "Riesgo",
        "income_commitment": "Compromiso de ingresos",
        "reserve_months": "Meses de reserva",
        "history_score": "Puntuación",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnóstico financiero con IA y plan de acción de 30 días",
        "notice": "INNA es una educadora financiera. No recomienda inversiones ni sustituye a un profesional certificado.",
        "api_offline": "La API de INNA está fuera de línea. Verifica si la API online está activa.",
        "name": "Tu nombre",
        "monthly_income": "Ingresos mensuales",
        "fixed_expenses": "Gastos fijos mensuales",
        "variable_expenses": "Gastos variables mensuales",
        "debts": "Deudas mensuales",
        "savings": "Ahorros actuales",
        "goal": "¿Cuál es tu objetivo financiero?",
        "default_goal": "Organizar mi vida financiera",
        "generate": "Generar diagnóstico con INNA",
        "loading": "Llamando a la API de INNA y generando diagnóstico con IA...",
        "saved": "Diagnóstico generado y guardado con éxito vía FastAPI.",
        "success": "Diagnóstico generado con éxito.",
        "diagnosis": "### Diagnóstico",
        "plan": "### Plan de acción de 30 días",
        "download_pdf": "📄 Descargar informe PDF",
        "email_title": "### 📧 Recibir informe por e-mail",
        "email_input": "Introduce tu e-mail para recibir el informe PDF:",
        "email_button": "📧 Enviar informe por e-mail",
        "email_invalid": "Introduce un e-mail válido.",
        "email_success": "Informe enviado por e-mail con éxito.",
        "email_error": "Error al enviar el informe por e-mail",
        "pdf_error": "No fue posible descargar el informe desde la API",
        "pdf_unavailable": "Informe PDF no disponible: el diagnóstico aún no tiene ID de API.",
        "feedback_title": "Comentarios",
        "feedback_comment": "Comentario opcional",
        "feedback_placeholder": "Ejemplo: el plan fue claro, faltó más detalle, me gustó la explicación...",
        "feedback_button": "Enviar comentario",
        "feedback_success": "Comentario registrado con éxito vía FastAPI. ¡Gracias por ayudar a mejorar INNA!",
        "history_title": "Historial individual",
        "history_name": "Nombre para buscar historial",
        "history_limit": "Número máximo de registros",
        "history_button": "Buscar historial",
        "history_empty": "No se encontró ningún diagnóstico para ese nombre.",
        "feedback_help": "Tu evaluación ayuda a mejorar INNA y validar el proyecto.",
        "feedback_question": "¿Esta respuesta fue útil?",
        "yes": "Sí",
        "no": "No",
        "history_help": "Consulta diagnósticos anteriores por nombre de usuario. Esta área usa FastAPI para buscar datos guardados en PostgreSQL.",
    },
    "de": {
        "currency_notice": "Gib die Werte in {currency} ein. INNA führt keine automatische Währungsumrechnung durch.",
        "estimated_balance": "Geschätzter Überschuss",
        "financial_score": "Finanzscore",
        "risk": "Risiko",
        "income_commitment": "Einkommensbindung",
        "reserve_months": "Rücklagenmonate",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Finanzdiagnose mit KI und 30-Tage-Aktionsplan",
        "notice": "INNA ist eine Finanzpädagogin. Sie empfiehlt keine Investitionen und ersetzt keine zertifizierte Fachperson.",
        "api_offline": "Die INNA-API ist offline. Prüfe, ob die Online-API aktiv ist.",
        "name": "Dein Name",
        "monthly_income": "Monatliches Einkommen",
        "fixed_expenses": "Monatliche Fixkosten",
        "variable_expenses": "Monatliche variable Ausgaben",
        "debts": "Monatliche Schulden/Raten",
        "savings": "Aktuelle Rücklage",
        "goal": "Was ist dein finanzielles Ziel?",
        "default_goal": "Mein Finanzleben organisieren",
        "generate": "Diagnose mit INNA erstellen",
        "loading": "INNA-API wird aufgerufen und KI-Diagnose wird erstellt...",
        "saved": "Diagnose erfolgreich über FastAPI erstellt und gespeichert.",
        "success": "Diagnose erfolgreich erstellt.",
        "diagnosis": "### Diagnose",
        "plan": "### 30-Tage-Aktionsplan",
        "download_pdf": "📄 PDF-Bericht herunterladen",
        "email_title": "### 📧 Bericht per E-Mail erhalten",
        "email_input": "Gib deine E-Mail ein, um den PDF-Bericht zu erhalten:",
        "email_button": "📧 Bericht per E-Mail senden",
        "email_invalid": "Gib eine gültige E-Mail ein.",
        "email_success": "Bericht erfolgreich per E-Mail gesendet.",
        "email_error": "Fehler beim Senden des Berichts per E-Mail",
        "pdf_error": "Bericht konnte nicht von der API heruntergeladen werden",
        "pdf_unavailable": "PDF-Bericht nicht verfügbar: Die Diagnose hat noch keine API-ID.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optionaler Kommentar",
        "feedback_placeholder": "Beispiel: Der Plan war klar, ich wollte mehr Details, mir gefiel die Erklärung...",
        "feedback_button": "Feedback senden",
        "feedback_success": "Feedback erfolgreich über FastAPI registriert. Danke, dass du INNA verbesserst!",
        "history_title": "Individueller Verlauf",
        "history_name": "Name für Verlaufssuche",
        "history_limit": "Maximale Anzahl von Einträgen",
        "history_button": "Verlauf suchen",
        "history_empty": "Keine Diagnose für diesen Namen gefunden.",
        "browser_translate_warning": "Um die Sprachen korrekt zu testen, deaktiviere den automatischen Browser-Übersetzer.",
        "feedback_help": "Deine Bewertung hilft, INNA zu verbessern und das Projekt zu validieren.",
        "feedback_question": "War diese Antwort hilfreich?",
        "yes": "Ja",
        "no": "Nein",
        "history_help": "Suche frühere Diagnosen nach Benutzername. Dieser Bereich nutzt FastAPI, um gespeicherte Daten aus PostgreSQL abzurufen.",
    },
    "fr": {
        "currency_notice": "Saisissez les valeurs en {currency}. INNA ne convertit pas automatiquement les devises.",
        "estimated_balance": "Solde estimé",
        "financial_score": "Score financier",
        "risk": "Risque",
        "income_commitment": "Engagement du revenu",
        "reserve_months": "Mois d’épargne",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnostic financier avec IA et plan d’action de 30 jours",
        "notice": "INNA est une éducatrice financière. Elle ne recommande pas d’investissements et ne remplace pas un professionnel certifié.",
        "api_offline": "L’API INNA est hors ligne. Vérifiez si l’API en ligne est active.",
        "name": "Votre nom",
        "monthly_income": "Revenu mensuel",
        "fixed_expenses": "Dépenses fixes mensuelles",
        "variable_expenses": "Dépenses variables mensuelles",
        "debts": "Dettes mensuelles",
        "savings": "Épargne actuelle",
        "goal": "Quel est votre objectif financier ?",
        "default_goal": "Organiser ma vie financière",
        "generate": "Générer le diagnostic avec INNA",
        "loading": "Appel de l’API INNA et génération du diagnostic IA...",
        "saved": "Diagnostic généré et enregistré avec succès via FastAPI.",
        "success": "Diagnostic généré avec succès.",
        "diagnosis": "### Diagnostic",
        "plan": "### Plan d’action de 30 jours",
        "download_pdf": "📄 Télécharger le rapport PDF",
        "email_title": "### 📧 Recevoir le rapport par e-mail",
        "email_input": "Entrez votre e-mail pour recevoir le rapport PDF :",
        "email_button": "📧 Envoyer le rapport par e-mail",
        "email_invalid": "Entrez un e-mail valide.",
        "email_success": "Rapport envoyé par e-mail avec succès.",
        "email_error": "Erreur lors de l’envoi du rapport par e-mail",
        "pdf_error": "Impossible de télécharger le rapport depuis l’API",
        "pdf_unavailable": "Rapport PDF indisponible : le diagnostic n’a pas encore d’ID API.",
        "feedback_title": "Retour",
        "feedback_comment": "Commentaire optionnel",
        "feedback_placeholder": "Exemple : le plan était clair, je voulais plus de détails, j’ai aimé l’explication...",
        "feedback_button": "Envoyer le retour",
        "feedback_success": "Retour enregistré avec succès via FastAPI. Merci d’aider INNA à s’améliorer !",
        "history_title": "Historique individuel",
        "history_name": "Nom pour rechercher l’historique",
        "history_limit": "Nombre maximum d’enregistrements",
        "history_button": "Rechercher l’historique",
        "history_empty": "Aucun diagnostic trouvé pour ce nom.",
        "feedback_help": "Votre avis aide à améliorer INNA et à valider le projet.",
        "feedback_question": "Cette réponse était-elle utile ?",
        "yes": "Oui",
        "no": "Non",
        "history_help": "Consultez les diagnostics précédents par nom d’utilisateur. Cette zone utilise FastAPI pour récupérer les données enregistrées dans PostgreSQL.",
    },
    "it": {
        "currency_notice": "Inserisci i valori in {currency}. INNA non converte automaticamente i tassi di cambio.",
        "estimated_balance": "Saldo stimato",
        "financial_score": "Punteggio finanziario",
        "risk": "Rischio",
        "income_commitment": "Impegno del reddito",
        "reserve_months": "Mesi di riserva",
        "history_score": "Punteggio",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnosi finanziaria con IA e piano d’azione di 30 giorni",
        "notice": "INNA è un’educatrice finanziaria. Non raccomanda investimenti e non sostituisce un professionista certificato.",
        "api_offline": "L’API INNA è offline. Controlla se l’API online è attiva.",
        "name": "Il tuo nome",
        "monthly_income": "Reddito mensile",
        "fixed_expenses": "Spese fisse mensili",
        "variable_expenses": "Spese variabili mensili",
        "debts": "Debiti mensili",
        "savings": "Risparmi attuali",
        "goal": "Qual è il tuo obiettivo finanziario?",
        "default_goal": "Organizzare la mia vita finanziaria",
        "generate": "Genera diagnosi con INNA",
        "loading": "Chiamata all’API INNA e generazione della diagnosi IA...",
        "saved": "Diagnosi generata e salvata con successo tramite FastAPI.",
        "success": "Diagnosi generata con successo.",
        "diagnosis": "### Diagnosi",
        "plan": "### Piano d’azione di 30 giorni",
        "download_pdf": "📄 Scarica rapporto PDF",
        "email_title": "### 📧 Ricevi il rapporto via e-mail",
        "email_input": "Inserisci la tua e-mail per ricevere il rapporto PDF:",
        "email_button": "📧 Invia rapporto via e-mail",
        "email_invalid": "Inserisci una e-mail valida.",
        "email_success": "Rapporto inviato via e-mail con successo.",
        "email_error": "Errore durante l’invio del rapporto via e-mail",
        "pdf_error": "Impossibile scaricare il rapporto dall’API",
        "pdf_unavailable": "Rapporto PDF non disponibile: la diagnosi non ha ancora un ID API.",
        "feedback_title": "Feedback",
        "feedback_comment": "Commento opzionale",
        "feedback_placeholder": "Esempio: il piano era chiaro, volevo più dettagli, mi è piaciuta la spiegazione...",
        "feedback_button": "Invia feedback",
        "feedback_success": "Feedback registrato con successo tramite FastAPI. Grazie per aiutare INNA a migliorare!",
        "history_title": "Cronologia individuale",
        "history_name": "Nome per cercare la cronologia",
        "history_limit": "Numero massimo di record",
        "history_button": "Cerca cronologia",
        "history_empty": "Nessuna diagnosi trovata per questo nome.",
        "feedback_help": "La tua valutazione aiuta a migliorare INNA e a validare il progetto.",
        "feedback_question": "Questa risposta è stata utile?",
        "yes": "Sì",
        "no": "No",
        "history_help": "Consulta le diagnosi precedenti per nome utente. Quest’area usa FastAPI per cercare dati salvati in PostgreSQL.",
    },
    "ro": {
        "currency_notice": "Introduceți valorile în {currency}. INNA nu face conversie valutară automată.",
        "estimated_balance": "Sold estimat",
        "financial_score": "Scor financiar",
        "risk": "Risc",
        "income_commitment": "Grad de angajare a venitului",
        "reserve_months": "Luni de rezervă",
        "history_score": "Scor",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnostic financiar cu IA și plan de acțiune pe 30 de zile",
        "notice": "INNA este o educatoare financiară. Nu recomandă investiții și nu înlocuiește un profesionist certificat.",
        "api_offline": "API-ul INNA este offline. Verifică dacă API-ul online este activ.",
        "name": "Numele tău",
        "monthly_income": "Venit lunar",
        "fixed_expenses": "Cheltuieli fixe lunare",
        "variable_expenses": "Cheltuieli variabile lunare",
        "debts": "Datorii lunare",
        "savings": "Economii actuale",
        "goal": "Care este obiectivul tău financiar?",
        "default_goal": "Să îmi organizez viața financiară",
        "generate": "Generează diagnosticul cu INNA",
        "loading": "Se apelează API-ul INNA și se generează diagnosticul cu IA...",
        "saved": "Diagnostic generat și salvat cu succes prin FastAPI.",
        "success": "Diagnostic generat cu succes.",
        "diagnosis": "### Diagnostic",
        "plan": "### Plan de acțiune pe 30 de zile",
        "download_pdf": "📄 Descarcă raportul PDF",
        "email_title": "### 📧 Primește raportul prin e-mail",
        "email_input": "Introdu e-mailul pentru a primi raportul PDF:",
        "email_button": "📧 Trimite raportul prin e-mail",
        "email_invalid": "Introdu un e-mail valid.",
        "email_success": "Raport trimis cu succes prin e-mail.",
        "email_error": "Eroare la trimiterea raportului prin e-mail",
        "pdf_error": "Nu s-a putut descărca raportul din API",
        "pdf_unavailable": "Raport PDF indisponibil: diagnosticul nu are încă ID API.",
        "feedback_title": "Feedback",
        "feedback_comment": "Comentariu opțional",
        "feedback_placeholder": "Exemplu: planul a fost clar, am vrut mai multe detalii, mi-a plăcut explicația...",
        "feedback_button": "Trimite feedback",
        "feedback_success": "Feedback înregistrat cu succes prin FastAPI. Mulțumim că ajuți INNA să evolueze!",
        "history_title": "Istoric individual",
        "history_name": "Nume pentru căutarea istoricului",
        "history_limit": "Număr maxim de înregistrări",
        "history_button": "Caută istoricul",
        "history_empty": "Nu a fost găsit niciun diagnostic pentru acest nume.",
        "feedback_help": "Evaluarea ta ajută la îmbunătățirea INNA și la validarea proiectului.",
        "feedback_question": "A fost util acest răspuns?",
        "yes": "Da",
        "no": "Nu",
        "history_help": "Consultă diagnosticele anterioare după numele utilizatorului. Această zonă folosește FastAPI pentru datele salvate în PostgreSQL.",
    },
    "uk": {
        "currency_notice": "Вводьте значення у валюті {currency}. INNA не виконує автоматичну конвертацію валют.",
        "estimated_balance": "Орієнтовний баланс",
        "financial_score": "Фінансовий бал",
        "risk": "Ризик",
        "income_commitment": "Навантаження на дохід",
        "reserve_months": "Місяці резерву",
        "history_score": "Бал",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Фінансова діагностика з ШІ та план дій на 30 днів",
        "notice": "INNA — фінансова освітня помічниця. Вона не рекомендує інвестиції та не замінює сертифікованого фахівця.",
        "api_offline": "API INNA не в мережі. Перевірте, чи активний онлайн API.",
        "name": "Ваше ім’я",
        "monthly_income": "Місячний дохід",
        "fixed_expenses": "Щомісячні фіксовані витрати",
        "variable_expenses": "Щомісячні змінні витрати",
        "debts": "Щомісячні борги",
        "savings": "Поточні заощадження",
        "goal": "Яка ваша фінансова мета?",
        "default_goal": "Організувати моє фінансове життя",
        "generate": "Створити діагностику з INNA",
        "loading": "Виклик API INNA та створення діагностики з ШІ...",
        "saved": "Діагностику успішно створено та збережено через FastAPI.",
        "success": "Діагностику успішно створено.",
        "diagnosis": "### Діагностика",
        "plan": "### План дій на 30 днів",
        "download_pdf": "📄 Завантажити PDF-звіт",
        "email_title": "### 📧 Отримати звіт електронною поштою",
        "email_input": "Введіть e-mail, щоб отримати PDF-звіт:",
        "email_button": "📧 Надіслати звіт e-mail",
        "email_invalid": "Введіть дійсний e-mail.",
        "email_success": "Звіт успішно надіслано електронною поштою.",
        "email_error": "Помилка надсилання звіту електронною поштою",
        "pdf_error": "Не вдалося завантажити звіт з API",
        "pdf_unavailable": "PDF-звіт недоступний: діагностика ще не має API ID.",
        "feedback_title": "Відгук",
        "feedback_comment": "Необов’язковий коментар",
        "feedback_placeholder": "Приклад: план був зрозумілим, хотілося більше деталей, сподобалося пояснення...",
        "feedback_button": "Надіслати відгук",
        "feedback_success": "Відгук успішно збережено через FastAPI. Дякуємо, що допомагаєте INNA розвиватися!",
        "history_title": "Індивідуальна історія",
        "history_name": "Ім’я для пошуку історії",
        "history_limit": "Максимальна кількість записів",
        "history_button": "Шукати історію",
        "history_empty": "Діагностику для цього імені не знайдено.",
        "feedback_help": "Ваш відгук допомагає покращити INNA та перевірити проєкт.",
        "feedback_question": "Ця відповідь була корисною?",
        "yes": "Так",
        "no": "Ні",
        "history_help": "Перегляньте попередні діагностики за ім’ям користувача. Цей розділ використовує FastAPI для пошуку даних у PostgreSQL.",
    },
    "ru": {
        "currency_notice": "Введите значения в валюте {currency}. INNA не выполняет автоматическую конвертацию валют.",
        "estimated_balance": "Оценочный баланс",
        "financial_score": "Финансовый балл",
        "risk": "Риск",
        "income_commitment": "Нагрузка на доход",
        "reserve_months": "Месяцы резерва",
        "history_score": "Балл",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Финансовая диагностика с ИИ и план действий на 30 дней",
        "notice": "INNA — финансовый образовательный помощник. Она не рекомендует инвестиции и не заменяет сертифицированного специалиста.",
        "api_offline": "API INNA не в сети. Проверьте, активен ли онлайн API.",
        "name": "Ваше имя",
        "monthly_income": "Ежемесячный доход",
        "fixed_expenses": "Ежемесячные фиксированные расходы",
        "variable_expenses": "Ежемесячные переменные расходы",
        "debts": "Ежемесячные долги",
        "savings": "Текущие сбережения",
        "goal": "Какая у вас финансовая цель?",
        "default_goal": "Организовать мою финансовую жизнь",
        "generate": "Создать диагностику с INNA",
        "loading": "Вызов API INNA и создание диагностики с ИИ...",
        "saved": "Диагностика успешно создана и сохранена через FastAPI.",
        "success": "Диагностика успешно создана.",
        "diagnosis": "### Диагностика",
        "plan": "### План действий на 30 дней",
        "download_pdf": "📄 Скачать PDF-отчёт",
        "email_title": "### 📧 Получить отчёт по e-mail",
        "email_input": "Введите e-mail, чтобы получить PDF-отчёт:",
        "email_button": "📧 Отправить отчёт по e-mail",
        "email_invalid": "Введите корректный e-mail.",
        "email_success": "Отчёт успешно отправлен по e-mail.",
        "email_error": "Ошибка отправки отчёта по e-mail",
        "pdf_error": "Не удалось скачать отчёт из API",
        "pdf_unavailable": "PDF-отчёт недоступен: у диагностики ещё нет API ID.",
        "feedback_title": "Обратная связь",
        "feedback_comment": "Необязательный комментарий",
        "feedback_placeholder": "Пример: план был понятным, хотелось больше деталей, понравилось объяснение...",
        "feedback_button": "Отправить отзыв",
        "feedback_success": "Отзыв успешно сохранён через FastAPI. Спасибо, что помогаете INNA развиваться!",
        "history_title": "Индивидуальная история",
        "history_name": "Имя для поиска истории",
        "history_limit": "Максимальное количество записей",
        "history_button": "Искать историю",
        "history_empty": "Диагностика для этого имени не найдена.",
        "feedback_help": "Ваш отзыв помогает улучшить INNA и подтвердить проект.",
        "feedback_question": "Был ли этот ответ полезен?",
        "yes": "Да",
        "no": "Нет",
        "history_help": "Просмотрите предыдущие диагностики по имени пользователя. Этот раздел использует FastAPI для поиска данных в PostgreSQL.",
    },
    "ar": {
        "currency_notice": "أدخل القيم بعملة {currency}. لا تقوم INNA بتحويل العملات تلقائيًا.",
        "estimated_balance": "الرصيد التقديري",
        "financial_score": "الدرجة المالية",
        "risk": "المخاطر",
        "income_commitment": "نسبة الالتزام من الدخل",
        "reserve_months": "أشهر الاحتياطي",
        "history_score": "الدرجة",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "تشخيص مالي بالذكاء الاصطناعي وخطة عمل لمدة 30 يومًا",
        "notice": "INNA هي أداة تعليم مالي. لا تقدم توصيات استثمارية ولا تستبدل المتخصص المالي المعتمد.",
        "api_offline": "واجهة API الخاصة بـ INNA غير متصلة. تحقق من أن الواجهة تعمل عبر الإنترنت.",
        "name": "اسمك",
        "monthly_income": "الدخل الشهري",
        "fixed_expenses": "المصاريف الثابتة الشهرية",
        "variable_expenses": "المصاريف المتغيرة الشهرية",
        "debts": "الديون الشهرية",
        "savings": "المدخرات الحالية",
        "goal": "ما هو هدفك المالي؟",
        "default_goal": "تنظيم حياتي المالية",
        "generate": "إنشاء التشخيص باستخدام INNA",
        "loading": "يتم الاتصال بواجهة INNA وإنشاء التشخيص بالذكاء الاصطناعي...",
        "saved": "تم إنشاء التشخيص وحفظه بنجاح عبر FastAPI.",
        "success": "تم إنشاء التشخيص بنجاح.",
        "diagnosis": "### التشخيص",
        "plan": "### خطة عمل لمدة 30 يومًا",
        "download_pdf": "📄 تنزيل تقرير PDF",
        "email_title": "### 📧 استلام التقرير عبر البريد الإلكتروني",
        "email_input": "أدخل بريدك الإلكتروني لاستلام تقرير PDF:",
        "email_button": "📧 إرسال التقرير عبر البريد الإلكتروني",
        "email_invalid": "أدخل بريدًا إلكترونيًا صالحًا.",
        "email_success": "تم إرسال التقرير عبر البريد الإلكتروني بنجاح.",
        "email_error": "خطأ في إرسال التقرير عبر البريد الإلكتروني",
        "pdf_error": "تعذر تنزيل التقرير من API",
        "pdf_unavailable": "تقرير PDF غير متاح: التشخيص لا يحتوي على معرف API بعد.",
        "feedback_title": "ملاحظات",
        "feedback_comment": "تعليق اختياري",
        "feedback_placeholder": "مثال: كانت الخطة واضحة، أريد تفاصيل أكثر، أعجبتني الشرح...",
        "feedback_button": "إرسال الملاحظات",
        "feedback_success": "تم تسجيل الملاحظات بنجاح عبر FastAPI. شكرًا لمساعدتك في تطوير INNA!",
        "history_title": "السجل الفردي",
        "history_name": "الاسم للبحث في السجل",
        "history_limit": "الحد الأقصى لعدد السجلات",
        "history_button": "البحث في السجل",
        "history_empty": "لم يتم العثور على تشخيص لهذا الاسم.",
        "feedback_help": "تساعد ملاحظاتك في تحسين INNA والتحقق من المشروع.",
        "feedback_question": "هل كانت هذه الإجابة مفيدة؟",
        "yes": "نعم",
        "no": "لا",
        "history_help": "ابحث عن التشخيصات السابقة حسب اسم المستخدم. يستخدم هذا القسم FastAPI لجلب البيانات المحفوظة في PostgreSQL.",
    },
    "ch": {
        "currency_notice": "Gib die Werte in {currency} ein. INNA führt keine automatische Währungsumrechnung durch.",
        "estimated_balance": "Geschätzter Überschuss",
        "financial_score": "Finanzscore",
        "risk": "Risiko",
        "income_commitment": "Einkommensbindung",
        "reserve_months": "Rücklagenmonate",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Finanzdiagnose mit KI und 30-Tage-Aktionsplan",
        "notice": "INNA ist eine Finanzpädagogin. Sie empfiehlt keine Investitionen und ersetzt keine zertifizierte Fachperson.",
        "api_offline": "Die INNA-API ist offline. Prüfe, ob die Online-API aktiv ist.",
        "name": "Dein Name",
        "monthly_income": "Monatliches Einkommen",
        "fixed_expenses": "Monatliche Fixkosten",
        "variable_expenses": "Monatliche variable Ausgaben",
        "debts": "Monatliche Schulden/Raten",
        "savings": "Aktuelle Rücklage",
        "goal": "Was ist dein finanzielles Ziel?",
        "default_goal": "Mein Finanzleben organisieren",
        "generate": "Diagnose mit INNA erstellen",
        "loading": "INNA-API wird aufgerufen und KI-Diagnose wird erstellt...",
        "saved": "Diagnose erfolgreich über FastAPI erstellt und gespeichert.",
        "success": "Diagnose erfolgreich erstellt.",
        "diagnosis": "### Diagnose",
        "plan": "### 30-Tage-Aktionsplan",
        "download_pdf": "📄 PDF-Bericht herunterladen",
        "email_title": "### 📧 Bericht per E-Mail erhalten",
        "email_input": "Gib deine E-Mail ein, um den PDF-Bericht zu erhalten:",
        "email_button": "📧 Bericht per E-Mail senden",
        "email_invalid": "Gib eine gültige E-Mail ein.",
        "email_success": "Bericht erfolgreich per E-Mail gesendet.",
        "email_error": "Fehler beim Senden des Berichts per E-Mail",
        "pdf_error": "Bericht konnte nicht von der API heruntergeladen werden",
        "pdf_unavailable": "PDF-Bericht nicht verfügbar: Die Diagnose hat noch keine API-ID.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optionaler Kommentar",
        "feedback_placeholder": "Beispiel: Der Plan war klar, ich wollte mehr Details, mir gefiel die Erklärung...",
        "feedback_button": "Feedback senden",
        "feedback_success": "Feedback erfolgreich über FastAPI registriert. Danke, dass du INNA verbesserst!",
        "history_title": "Individueller Verlauf",
        "history_name": "Name für Verlaufssuche",
        "history_limit": "Maximale Anzahl von Einträgen",
        "history_button": "Verlauf suchen",
        "history_empty": "Keine Diagnose für diesen Namen gefunden.",
        "browser_translate_warning": "Um die Sprachen korrekt zu testen, deaktiviere den automatischen Browser-Übersetzer.",
        "feedback_help": "Deine Bewertung hilft, INNA zu verbessern und das Projekt zu validieren.",
        "feedback_question": "War diese Antwort hilfreich?",
        "yes": "Ja",
        "no": "Nein",
        "history_help": "Suche frühere Diagnosen nach Benutzername. Dieser Bereich nutzt FastAPI, um gespeicherte Daten aus PostgreSQL abzurufen.",
    },
}

detected_lang = detect_browser_language()

if "app_lang" not in st.session_state:
    st.session_state.app_lang = detected_lang

CURRENCY_BY_LANG = {
    "pt": {"moeda": "BRL", "simbolo": "R$"},
    "en_us": {"moeda": "USD", "simbolo": "$"},
    "en_gb": {"moeda": "GBP", "simbolo": "£"},
    "es": {"moeda": "EUR", "simbolo": "€"},
    "de": {"moeda": "EUR", "simbolo": "€"},
    "fr": {"moeda": "EUR", "simbolo": "€"},
    "it": {"moeda": "EUR", "simbolo": "€"},
    "ro": {"moeda": "RON", "simbolo": "lei"},
    "uk": {"moeda": "UAH", "simbolo": "₴"},
    "ru": {"moeda": "RUB", "simbolo": "₽"},
    "ar": {"moeda": "SAR", "simbolo": "ر.س"},
    "ch": {"moeda": "CHF", "simbolo": "CHF"},
}
app_lang = st.sidebar.selectbox(
    "🌍 Idioma / Language",
    options=list(APP_LANG_LABELS.keys()),
    index=list(APP_LANG_LABELS.keys()).index(st.session_state.app_lang),
    format_func=lambda key: APP_LANG_LABELS[key],
    key="app_lang_sidebar_hidden",
)


# Atualiza idioma e moeda após mudança no seletor superior
st.session_state.app_lang = app_lang
current_currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

# =============================
# TEMA VISUAL DA INNA
# =============================

THEMES_INNA = {
    "Branco brilhante": {
        "bg": "#F8FBFF",
        "sidebar": "#EEF4FB",
        "surface": "#FFFFFF",
        "surface_2": "#EEF6FF",
        "text": "#071C36",
        "muted": "#42526E",
        "accent": "#D4AF37",
        "primary": "#0E3A73",
        "border": "#D5E3F5",
        "hero_bg": "linear-gradient(135deg, #FFFFFF 0%, #F1F7FF 100%)",
        "hero_text": "#071C36",
        "hero_subtext": "#34465F",
        "card_bg": "#FFFFFF",
        "card_text": "#071C36",
    },
    "Escuro preto": {
        "bg": "#05070D",
        "sidebar": "#090D16",
        "surface": "#0D1320",
        "surface_2": "#111827",
        "text": "#F8FAFC",
        "muted": "#B8C2D1",
        "accent": "#E0B64A",
        "primary": "#111827",
        "border": "#26344D",
        "hero_bg": "linear-gradient(135deg, #05070D 0%, #0D1320 55%, #111827 100%)",
        "hero_text": "#FFFFFF",
        "hero_subtext": "#D8E2F0",
        "card_bg": "#0D1320",
        "card_text": "#FFFFFF",
    },
    "Escuro azul": {
        "bg": "#07111F",
        "sidebar": "#0A1729",
        "surface": "#0B1F3A",
        "surface_2": "#102A4C",
        "text": "#F8FAFC",
        "muted": "#C5D3E8",
        "accent": "#F2C86B",
        "primary": "#0B2D5C",
        "border": "#24476F",
        "hero_bg": "linear-gradient(135deg, #0B2D5C 0%, #071C36 55%, #04101F 100%)",
        "hero_text": "#F6D889",
        "hero_subtext": "#E5EDF8",
        "card_bg": "#0F2545",
        "card_text": "#FFFFFF",
    },
}
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Escuro azul"

if "theme_selector_top" in st.session_state:
    st.session_state.theme_name = st.session_state.theme_selector_top

theme = THEMES_INNA[st.session_state.theme_name]
st.markdown(f"""
<style>
.stApp {{
    background: {theme["bg"]} !important;
    color: {theme["text"]} !important;
}}

[data-testid="stAppViewContainer"] {{
    background: {theme["bg"]} !important;
}}

[data-testid="stSidebar"] {{
    background: {theme["sidebar"]} !important;
    border-right: 1px solid {theme["border"]} !important;
}}

.block-container {{
    color: {theme["text"]} !important;
}}

h1, h2, h3, h4, h5, h6, p, span, label {{
    color: {theme["text"]};
}}

.premium-badge {{
    background: {theme["primary"]} !important;
    color: #F8D98B !important;
    border: 1px solid {theme["accent"]} !important;
}}

.info-box {{
    background: {theme["surface_2"]} !important;
    color: {theme["text"]} !important;
    border: 1px solid {theme["border"]} !important;
}}

.feature-card, .step-card {{
    background: {theme["surface"]} !important;
    border: 1px solid {theme["border"]} !important;
}}

.feature-card h3, .step-card h4, .section-title, .title-main {{
    color: {theme["text"]} !important;
}}

.feature-card p, .step-card p, .text-normal, .subtitle {{
    color: {theme["muted"]} !important;
}}

div[data-testid="stMetric"] {{
    background: {theme["surface"]} !important;
    border: 1px solid {theme["border"]} !important;
}}

div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{
    color: {theme["text"]} !important;
}}

.stButton > button {{
    background: {theme["surface"]} !important;
    color: {theme["text"]} !important;
    border: 1px solid {theme["border"]} !important;
}}

.stButton > button:hover {{
    border-color: {theme["accent"]} !important;
    color: {theme["accent"]} !important;
}}

div[data-baseweb="select"] > div {{
    background: {theme["surface"]} !important;
    color: {theme["text"]} !important;
    border: 1px solid {theme["border"]} !important;
}}
</style>
""", unsafe_allow_html=True)





MENU_TEXTS_INNA = {
    "pt": {
        "🏠 Início": "🏠 Início",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "💬 Conversar": "💬 Conversar",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Relatório",
        "📚 Histórico": "📚 Histórico",
        "⭐ Avaliar": "⭐ Avaliar",
        "ℹ️ Sobre": "ℹ️ Sobre",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "en_us": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosis",
        "📊 Panorama": "📊 Overview",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Report",
        "📚 Histórico": "📚 History",
        "⭐ Avaliar": "⭐ Rate",
        "ℹ️ Sobre": "ℹ️ About",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "en_gb": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosis",
        "📊 Panorama": "📊 Overview",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Report",
        "📚 Histórico": "📚 History",
        "⭐ Avaliar": "⭐ Rate",
        "ℹ️ Sobre": "ℹ️ About",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "es": {
        "🏠 Início": "🏠 Inicio",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Informe",
        "📚 Histórico": "📚 Historial",
        "⭐ Avaliar": "⭐ Evaluar",
        "ℹ️ Sobre": "ℹ️ Acerca de",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "de": {
        "🏠 Início": "🏠 Start",
        "🧾 Diagnóstico": "🧾 Diagnose",
        "📊 Panorama": "📊 Übersicht",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Bericht",
        "📚 Histórico": "📚 Verlauf",
        "⭐ Avaliar": "⭐ Bewerten",
        "ℹ️ Sobre": "ℹ️ Über",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "fr": {
        "🏠 Início": "🏠 Accueil",
        "🧾 Diagnóstico": "🧾 Diagnostic",
        "📊 Panorama": "📊 Aperçu",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Rapport",
        "📚 Histórico": "📚 Historique",
        "⭐ Avaliar": "⭐ Évaluer",
        "ℹ️ Sobre": "ℹ️ À propos",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "it": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosi",
        "📊 Panorama": "📊 Panoramica",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Report",
        "📚 Histórico": "📚 Cronologia",
        "⭐ Avaliar": "⭐ Valuta",
        "ℹ️ Sobre": "ℹ️ Info",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "ro": {
        "🏠 Início": "🏠 Acasă",
        "🧾 Diagnóstico": "🧾 Diagnostic",
        "📊 Panorama": "📊 Prezentare",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Raport",
        "📚 Histórico": "📚 Istoric",
        "⭐ Avaliar": "⭐ Evaluează",
        "ℹ️ Sobre": "ℹ️ Despre",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "uk": {
        "🏠 Início": "🏠 Головна",
        "🧾 Diagnóstico": "🧾 Діагностика",
        "📊 Panorama": "📊 Огляд",
        "💬 Conversar": "💬 Чат",
        "💬 Chat": "💬 Чат",
        "📄 Relatório": "📄 Звіт",
        "📚 Histórico": "📚 Історія",
        "⭐ Avaliar": "⭐ Оцінити",
        "ℹ️ Sobre": "ℹ️ Про INNA",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "ru": {
        "🏠 Início": "🏠 Главная",
        "🧾 Diagnóstico": "🧾 Диагностика",
        "📊 Panorama": "📊 Обзор",
        "💬 Conversar": "💬 Чат",
        "💬 Chat": "💬 Чат",
        "📄 Relatório": "📄 Отчёт",
        "📚 Histórico": "📚 История",
        "⭐ Avaliar": "⭐ Оценить",
        "ℹ️ Sobre": "ℹ️ О INNA",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "ar": {
        "🏠 Início": "🏠 الرئيسية",
        "🧾 Diagnóstico": "🧾 التشخيص",
        "📊 Panorama": "📊 نظرة عامة",
        "💬 Conversar": "💬 الدردشة",
        "💬 Chat": "💬 الدردشة",
        "📄 Relatório": "📄 التقرير",
        "📚 Histórico": "📚 السجل",
        "⭐ Avaliar": "⭐ التقييم",
        "ℹ️ Sobre": "ℹ️ حول INNA",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
    "ch": {
        "🏠 Início": "🏠 Start",
        "🧾 Diagnóstico": "🧾 Diagnose",
        "📊 Panorama": "📊 Übersicht",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Bericht",
        "📚 Histórico": "📚 Verlauf",
        "⭐ Avaliar": "⭐ Bewerten",
        "ℹ️ Sobre": "ℹ️ Über",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
    },
}

def menu_t(menu_item: str) -> str:
    lang = app_lang if app_lang in MENU_TEXTS_INNA else "pt"
    return MENU_TEXTS_INNA.get(lang, MENU_TEXTS_INNA["pt"]).get(menu_item, menu_item)



# ==========================================
# MENU MULTILÍNGUE SEGURO DA INNA
# ==========================================
MENU_TEXTS_INNA_SAFE = {
    "pt": {
        "🏠 Início": "🏠 Início",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "💬 Conversar": "💬 Conversar",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Relatório",
        "📚 Histórico": "📚 Histórico",
        "⭐ Avaliar": "⭐ Avaliar",
        "ℹ️ Sobre": "ℹ️ Sobre",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Entrar",
        "🚪 Sair": "🚪 Sair",
    },
    "en_us": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosis",
        "📊 Panorama": "📊 Overview",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Report",
        "📚 Histórico": "📚 History",
        "⭐ Avaliar": "⭐ Rate",
        "ℹ️ Sobre": "ℹ️ About",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Sign in",
        "🚪 Sair": "🚪 Sign out",
    },
    "en_gb": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosis",
        "📊 Panorama": "📊 Overview",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Report",
        "📚 Histórico": "📚 History",
        "⭐ Avaliar": "⭐ Rate",
        "ℹ️ Sobre": "ℹ️ About",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Sign in",
        "🚪 Sair": "🚪 Sign out",
    },
    "es": {
        "🏠 Início": "🏠 Inicio",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Informe",
        "📚 Histórico": "📚 Historial",
        "⭐ Avaliar": "⭐ Evaluar",
        "ℹ️ Sobre": "ℹ️ Acerca de",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Entrar",
        "🚪 Sair": "🚪 Salir",
    },
    "fr": {
        "🏠 Início": "🏠 Accueil",
        "🧾 Diagnóstico": "🧾 Diagnostic",
        "📊 Panorama": "📊 Aperçu",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Rapport",
        "📚 Histórico": "📚 Historique",
        "⭐ Avaliar": "⭐ Évaluer",
        "ℹ️ Sobre": "ℹ️ À propos",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Se connecter",
        "🚪 Sair": "🚪 Se déconnecter",
    },
    "de": {
        "🏠 Início": "🏠 Start",
        "🧾 Diagnóstico": "🧾 Diagnose",
        "📊 Panorama": "📊 Übersicht",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Bericht",
        "📚 Histórico": "📚 Verlauf",
        "⭐ Avaliar": "⭐ Bewerten",
        "ℹ️ Sobre": "ℹ️ Über",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Anmelden",
        "🚪 Sair": "🚪 Abmelden",
    },
    "it": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosi",
        "📊 Panorama": "📊 Panoramica",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Report",
        "📚 Histórico": "📚 Cronologia",
        "⭐ Avaliar": "⭐ Valuta",
        "ℹ️ Sobre": "ℹ️ Info",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Accedi",
        "🚪 Sair": "🚪 Esci",
    },
    "ro": {
        "🏠 Início": "🏠 Acasă",
        "🧾 Diagnóstico": "🧾 Diagnostic",
        "📊 Panorama": "📊 Prezentare",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Raport",
        "📚 Histórico": "📚 Istoric",
        "⭐ Avaliar": "⭐ Evaluează",
        "ℹ️ Sobre": "ℹ️ Despre",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Intră",
        "🚪 Sair": "🚪 Ieși",
    },
    "uk": {
        "🏠 Início": "🏠 Головна",
        "🧾 Diagnóstico": "🧾 Діагностика",
        "📊 Panorama": "📊 Огляд",
        "💬 Conversar": "💬 Чат",
        "💬 Chat": "💬 Чат",
        "📄 Relatório": "📄 Звіт",
        "📚 Histórico": "📚 Історія",
        "⭐ Avaliar": "⭐ Оцінити",
        "ℹ️ Sobre": "ℹ️ Про INNA",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Увійти",
        "🚪 Sair": "🚪 Вийти",
    },
    "ru": {
        "🏠 Início": "🏠 Главная",
        "🧾 Diagnóstico": "🧾 Диагностика",
        "📊 Panorama": "📊 Обзор",
        "💬 Conversar": "💬 Чат",
        "💬 Chat": "💬 Чат",
        "📄 Relatório": "📄 Отчёт",
        "📚 Histórico": "📚 История",
        "⭐ Avaliar": "⭐ Оценить",
        "ℹ️ Sobre": "ℹ️ О INNA",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Войти",
        "🚪 Sair": "🚪 Выйти",
    },
    "ar": {
        "🏠 Início": "🏠 الرئيسية",
        "🧾 Diagnóstico": "🧾 التشخيص",
        "📊 Panorama": "📊 نظرة عامة",
        "💬 Conversar": "💬 الدردشة",
        "💬 Chat": "💬 الدردشة",
        "📄 Relatório": "📄 التقرير",
        "📚 Histórico": "📚 السجل",
        "⭐ Avaliar": "⭐ التقييم",
        "ℹ️ Sobre": "ℹ️ حول INNA",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 تسجيل الدخول",
        "🚪 Sair": "🚪 خروج",
    },
    "ch": {
        "🏠 Início": "🏠 Start",
        "🧾 Diagnóstico": "🧾 Diagnose",
        "📊 Panorama": "📊 Übersicht",
        "💬 Conversar": "💬 Chat",
        "💬 Chat": "💬 Chat",
        "📄 Relatório": "📄 Bericht",
        "📚 Histórico": "📚 Verlauf",
        "⭐ Avaliar": "⭐ Bewerten",
        "ℹ️ Sobre": "ℹ️ Über",
        "🔐 Admin Analytics": "🔐 Admin",
        "🔑 Entrar": "🔑 Anmelden",
        "🚪 Sair": "🚪 Abmelden",
    },
}

def menu_t(menu_item: str) -> str:
    lang = app_lang if app_lang in MENU_TEXTS_INNA_SAFE else "pt"
    return MENU_TEXTS_INNA_SAFE.get(lang, MENU_TEXTS_INNA_SAFE["pt"]).get(menu_item, menu_item)

def top_menu_t(menu_item: str) -> str:
    return menu_t(menu_item)



# ==========================================
# MENU MULTILÍNGUE FINAL DA INNA
# ==========================================
MENU_LABELS_FINAL = {
    "pt": {
        "🏠 Início": "🏠 Início",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "🧾 Novo diagnóstico": "🧾 Novo diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "📊 Meu panorama financeiro": "📊 Meu panorama financeiro",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Conversar",
        "💬 Conversar com a Inna": "💬 Conversar com a Inna",
        "📄 Relatório": "📄 Relatório",
        "📄 Meu relatório": "📄 Meu relatório",
        "📚 Histórico": "📚 Histórico",
        "📚 Meu histórico": "📚 Meu histórico",
        "⭐ Avaliar": "⭐ Avaliar",
        "⭐ Avaliar a Inna": "⭐ Avaliar a Inna",
        "ℹ️ Sobre": "ℹ️ Sobre",
        "ℹ️ Sobre a INNA": "ℹ️ Sobre a INNA",
        "🔑 Entrar": "🔑 Entrar",
        "🚪 Sair": "🚪 Sair",
    },
    "en_us": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosis",
        "🧾 Novo diagnóstico": "🧾 New diagnosis",
        "📊 Panorama": "📊 Overview",
        "📊 Meu panorama financeiro": "📊 My overview",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Chat with Inna",
        "📄 Relatório": "📄 Report",
        "📄 Meu relatório": "📄 My report",
        "📚 Histórico": "📚 History",
        "📚 Meu histórico": "📚 My history",
        "⭐ Avaliar": "⭐ Rate",
        "⭐ Avaliar a Inna": "⭐ Rate Inna",
        "ℹ️ Sobre": "ℹ️ About",
        "ℹ️ Sobre a INNA": "ℹ️ About INNA",
        "🔑 Entrar": "🔑 Sign in",
        "🚪 Sair": "🚪 Sign out",
    },
    "en_gb": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosis",
        "🧾 Novo diagnóstico": "🧾 New diagnosis",
        "📊 Panorama": "📊 Overview",
        "📊 Meu panorama financeiro": "📊 My overview",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Chat with Inna",
        "📄 Relatório": "📄 Report",
        "📄 Meu relatório": "📄 My report",
        "📚 Histórico": "📚 History",
        "📚 Meu histórico": "📚 My history",
        "⭐ Avaliar": "⭐ Rate",
        "⭐ Avaliar a Inna": "⭐ Rate Inna",
        "ℹ️ Sobre": "ℹ️ About",
        "ℹ️ Sobre a INNA": "ℹ️ About INNA",
        "🔑 Entrar": "🔑 Sign in",
        "🚪 Sair": "🚪 Sign out",
    },
    "es": {
        "🏠 Início": "🏠 Inicio",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "🧾 Novo diagnóstico": "🧾 Nuevo diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "📊 Meu panorama financeiro": "📊 Mi panorama",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Hablar con Inna",
        "📄 Relatório": "📄 Informe",
        "📄 Meu relatório": "📄 Mi informe",
        "📚 Histórico": "📚 Historial",
        "📚 Meu histórico": "📚 Mi historial",
        "⭐ Avaliar": "⭐ Evaluar",
        "⭐ Avaliar a Inna": "⭐ Evaluar Inna",
        "ℹ️ Sobre": "ℹ️ Acerca de",
        "ℹ️ Sobre a INNA": "ℹ️ Sobre INNA",
        "🔑 Entrar": "🔑 Entrar",
        "🚪 Sair": "🚪 Salir",
    },
    "fr": {
        "🏠 Início": "🏠 Accueil",
        "🧾 Diagnóstico": "🧾 Diagnostic",
        "🧾 Novo diagnóstico": "🧾 Nouveau diagnostic",
        "📊 Panorama": "📊 Aperçu",
        "📊 Meu panorama financeiro": "📊 Mon aperçu",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Parler avec Inna",
        "📄 Relatório": "📄 Rapport",
        "📄 Meu relatório": "📄 Mon rapport",
        "📚 Histórico": "📚 Historique",
        "📚 Meu histórico": "📚 Mon historique",
        "⭐ Avaliar": "⭐ Évaluer",
        "⭐ Avaliar a Inna": "⭐ Évaluer Inna",
        "ℹ️ Sobre": "ℹ️ À propos",
        "ℹ️ Sobre a INNA": "ℹ️ À propos d’INNA",
        "🔑 Entrar": "🔑 Se connecter",
        "🚪 Sair": "🚪 Se déconnecter",
    },
    "de": {
        "🏠 Início": "🏠 Start",
        "🧾 Diagnóstico": "🧾 Diagnose",
        "🧾 Novo diagnóstico": "🧾 Neue Diagnose",
        "📊 Panorama": "📊 Übersicht",
        "📊 Meu panorama financeiro": "📊 Meine Übersicht",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Mit Inna chatten",
        "📄 Relatório": "📄 Bericht",
        "📄 Meu relatório": "📄 Mein Bericht",
        "📚 Histórico": "📚 Verlauf",
        "📚 Meu histórico": "📚 Mein Verlauf",
        "⭐ Avaliar": "⭐ Bewerten",
        "⭐ Avaliar a Inna": "⭐ Inna bewerten",
        "ℹ️ Sobre": "ℹ️ Über",
        "ℹ️ Sobre a INNA": "ℹ️ Über INNA",
        "🔑 Entrar": "🔑 Anmelden",
        "🚪 Sair": "🚪 Abmelden",
    },
    "it": {
        "🏠 Início": "🏠 Home",
        "🧾 Diagnóstico": "🧾 Diagnosi",
        "🧾 Novo diagnóstico": "🧾 Nuova diagnosi",
        "📊 Panorama": "📊 Panoramica",
        "📊 Meu panorama financeiro": "📊 La mia panoramica",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Parla con Inna",
        "📄 Relatório": "📄 Report",
        "📄 Meu relatório": "📄 Il mio report",
        "📚 Histórico": "📚 Cronologia",
        "📚 Meu histórico": "📚 La mia cronologia",
        "⭐ Avaliar": "⭐ Valuta",
        "⭐ Avaliar a Inna": "⭐ Valuta Inna",
        "ℹ️ Sobre": "ℹ️ Info",
        "ℹ️ Sobre a INNA": "ℹ️ Info INNA",
        "🔑 Entrar": "🔑 Accedi",
        "🚪 Sair": "🚪 Esci",
    },
    "ro": {
        "🏠 Início": "🏠 Acasă",
        "🧾 Diagnóstico": "🧾 Diagnostic",
        "🧾 Novo diagnóstico": "🧾 Diagnostic nou",
        "📊 Panorama": "📊 Prezentare",
        "📊 Meu panorama financeiro": "📊 Prezentarea mea",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Vorbește cu Inna",
        "📄 Relatório": "📄 Raport",
        "📄 Meu relatório": "📄 Raportul meu",
        "📚 Histórico": "📚 Istoric",
        "📚 Meu histórico": "📚 Istoricul meu",
        "⭐ Avaliar": "⭐ Evaluează",
        "⭐ Avaliar a Inna": "⭐ Evaluează Inna",
        "ℹ️ Sobre": "ℹ️ Despre",
        "ℹ️ Sobre a INNA": "ℹ️ Despre INNA",
        "🔑 Entrar": "🔑 Intră",
        "🚪 Sair": "🚪 Ieși",
    },
    "uk": {
        "🏠 Início": "🏠 Головна",
        "🧾 Diagnóstico": "🧾 Діагностика",
        "🧾 Novo diagnóstico": "🧾 Нова діагностика",
        "📊 Panorama": "📊 Огляд",
        "📊 Meu panorama financeiro": "📊 Мій огляд",
        "💬 Chat": "💬 Чат",
        "💬 Conversar": "💬 Чат",
        "💬 Conversar com a Inna": "💬 Чат з Inna",
        "📄 Relatório": "📄 Звіт",
        "📄 Meu relatório": "📄 Мій звіт",
        "📚 Histórico": "📚 Історія",
        "📚 Meu histórico": "📚 Моя історія",
        "⭐ Avaliar": "⭐ Оцінити",
        "⭐ Avaliar a Inna": "⭐ Оцінити Inna",
        "ℹ️ Sobre": "ℹ️ Про INNA",
        "ℹ️ Sobre a INNA": "ℹ️ Про INNA",
        "🔑 Entrar": "🔑 Увійти",
        "🚪 Sair": "🚪 Вийти",
    },
    "ru": {
        "🏠 Início": "🏠 Главная",
        "🧾 Diagnóstico": "🧾 Диагностика",
        "🧾 Novo diagnóstico": "🧾 Новая диагностика",
        "📊 Panorama": "📊 Обзор",
        "📊 Meu panorama financeiro": "📊 Мой обзор",
        "💬 Chat": "💬 Чат",
        "💬 Conversar": "💬 Чат",
        "💬 Conversar com a Inna": "💬 Чат с Inna",
        "📄 Relatório": "📄 Отчёт",
        "📄 Meu relatório": "📄 Мой отчёт",
        "📚 Histórico": "📚 История",
        "📚 Meu histórico": "📚 Моя история",
        "⭐ Avaliar": "⭐ Оценить",
        "⭐ Avaliar a Inna": "⭐ Оценить Inna",
        "ℹ️ Sobre": "ℹ️ О INNA",
        "ℹ️ Sobre a INNA": "ℹ️ О INNA",
        "🔑 Entrar": "🔑 Войти",
        "🚪 Sair": "🚪 Выйти",
    },
    "ar": {
        "🏠 Início": "🏠 الرئيسية",
        "🧾 Diagnóstico": "🧾 التشخيص",
        "🧾 Novo diagnóstico": "🧾 تشخيص جديد",
        "📊 Panorama": "📊 نظرة عامة",
        "📊 Meu panorama financeiro": "📊 نظرتي المالية",
        "💬 Chat": "💬 الدردشة",
        "💬 Conversar": "💬 الدردشة",
        "💬 Conversar com a Inna": "💬 تحدث مع Inna",
        "📄 Relatório": "📄 التقرير",
        "📄 Meu relatório": "📄 تقريري",
        "📚 Histórico": "📚 السجل",
        "📚 Meu histórico": "📚 سجلي",
        "⭐ Avaliar": "⭐ التقييم",
        "⭐ Avaliar a Inna": "⭐ تقييم Inna",
        "ℹ️ Sobre": "ℹ️ حول INNA",
        "ℹ️ Sobre a INNA": "ℹ️ حول INNA",
        "🔑 Entrar": "🔑 تسجيل الدخول",
        "🚪 Sair": "🚪 خروج",
    },
    "ch": {
        "🏠 Início": "🏠 Start",
        "🧾 Diagnóstico": "🧾 Diagnose",
        "🧾 Novo diagnóstico": "🧾 Neue Diagnose",
        "📊 Panorama": "📊 Übersicht",
        "📊 Meu panorama financeiro": "📊 Meine Übersicht",
        "💬 Chat": "💬 Chat",
        "💬 Conversar": "💬 Chat",
        "💬 Conversar com a Inna": "💬 Mit Inna chatten",
        "📄 Relatório": "📄 Bericht",
        "📄 Meu relatório": "📄 Mein Bericht",
        "📚 Histórico": "📚 Verlauf",
        "📚 Meu histórico": "📚 Mein Verlauf",
        "⭐ Avaliar": "⭐ Bewerten",
        "⭐ Avaliar a Inna": "⭐ Inna bewerten",
        "ℹ️ Sobre": "ℹ️ Über INNA",
        "ℹ️ Sobre a INNA": "ℹ️ Über INNA",
        "🔑 Entrar": "🔑 Anmelden",
        "🚪 Sair": "🚪 Abmelden",
    },
}

def menu_label_final(menu_item: str) -> str:
    lang = st.session_state.get("app_lang", app_lang)
    return MENU_LABELS_FINAL.get(lang, MENU_LABELS_FINAL["pt"]).get(menu_item, menu_item)

def menu_t(menu_item: str) -> str:
    return menu_label_final(menu_item)

def top_menu_t(menu_item: str) -> str:
    return menu_label_final(menu_item)


GLOBAL_UI_TEXTS_INNA = {
    "pt": {
        "menu": "Menu",
        "public_access": "Acesso público",
        "login_needed": "Faça login para usar diagnóstico, relatório, histórico e área admin.",
        "login_button": "🔑 Entrar",
        "connected": "Status: conectado",
        "user": "Usuário",
        "profile": "Perfil",
        "logout_success": "Você saiu da INNA.",
        "browser_warning": "Para testar os idiomas corretamente, desative o tradutor automático do navegador.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Área administrativa para gestor, administrador ou avaliador acompanhar métricas da plataforma.",
        "admin_warning": "Este painel é destinado ao administrador da INNA. Ele não deve aparecer para o usuário comum/trabalhador.",
        "admin_open": "Open dashboard in new tab",
        "about_title": "ℹ️ Sobre a INNA Financial Coach AI",
        "about_text": "A INNA é uma educadora financeira com IA Generativa, criada para transformar dados simples em diagnóstico financeiro, plano de ação, relatório PDF e indicadores reais.",
        "about_resources": "Recursos do projeto",
        "about_success": "Projeto pronto para portfólio, hackathons e evolução para assistente bancário.",
    },
    "en_us": {
        "menu": "Menu",
        "public_access": "Public access",
        "login_needed": "Sign in to use diagnosis, report, history and admin area.",
        "login_button": "🔑 Sign in",
        "connected": "Status: connected",
        "user": "User",
        "profile": "Profile",
        "logout_success": "You have signed out of INNA.",
        "browser_warning": "To test languages correctly, disable the browser automatic translator.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Administrative area for managers, administrators or reviewers to monitor platform metrics.",
        "admin_warning": "This dashboard is intended for INNA administrators. It should not appear for regular users/workers.",
        "admin_open": "Open dashboard in new tab",
        "about_title": "ℹ️ About INNA Financial Coach AI",
        "about_text": "INNA is a financial educator powered by Generative AI, created to turn simple data into financial diagnosis, action plans, PDF reports and real indicators.",
        "about_resources": "Project resources",
        "about_success": "Project ready for portfolio, hackathons and evolution into a banking assistant.",
    },
    "en_gb": {
        "menu": "Menu",
        "public_access": "Public access",
        "login_needed": "Sign in to use diagnosis, report, history and admin area.",
        "login_button": "🔑 Sign in",
        "connected": "Status: connected",
        "user": "User",
        "profile": "Profile",
        "logout_success": "You have signed out of INNA.",
        "browser_warning": "To test languages correctly, disable the browser automatic translator.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Administrative area for managers, administrators or reviewers to monitor platform metrics.",
        "admin_warning": "This dashboard is intended for INNA administrators. It should not appear for regular users/workers.",
        "admin_open": "Open dashboard in new tab",
        "about_title": "ℹ️ About INNA Financial Coach AI",
        "about_text": "INNA is a financial educator powered by Generative AI, created to turn simple data into financial diagnosis, action plans, PDF reports and real indicators.",
        "about_resources": "Project resources",
        "about_success": "Project ready for portfolio, hackathons and evolution into a banking assistant.",
    },
    "es": {
        "menu": "Menú",
        "public_access": "Acceso público",
        "login_needed": "Inicia sesión para usar diagnóstico, informe, historial y área administrativa.",
        "login_button": "🔑 Entrar",
        "connected": "Estado: conectado",
        "user": "Usuario",
        "profile": "Perfil",
        "logout_success": "Has salido de INNA.",
        "browser_warning": "Para probar los idiomas correctamente, desactiva el traductor automático del navegador.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Área administrativa para gestores, administradores o evaluadores monitorear métricas de la plataforma.",
        "admin_warning": "Este panel está destinado al administrador de INNA. No debe aparecer para el usuario común/trabajador.",
        "admin_open": "Abrir dashboard en una nueva pestaña",
        "about_title": "ℹ️ Sobre INNA Financial Coach AI",
        "about_text": "INNA es una educadora financiera con IA Generativa, creada para transformar datos simples en diagnóstico financiero, plan de acción, informe PDF e indicadores reales.",
        "about_resources": "Recursos del proyecto",
        "about_success": "Proyecto listo para portafolio, hackathons y evolución hacia asistente bancario.",
    },
    "de": {
        "menu": "Menü",
        "public_access": "Öffentlicher Zugriff",
        "login_needed": "Melden Sie sich an, um Diagnose, Bericht, Verlauf und Adminbereich zu nutzen.",
        "login_button": "🔑 Anmelden",
        "connected": "Status: verbunden",
        "user": "Benutzer",
        "profile": "Profil",
        "logout_success": "Sie haben sich von INNA abgemeldet.",
        "browser_warning": "Um Sprachen korrekt zu testen, deaktivieren Sie den automatischen Browser-Übersetzer.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Administrativer Bereich für Manager, Administratoren oder Prüfer zur Überwachung der Plattformmetriken.",
        "admin_warning": "Dieses Dashboard ist für INNA-Administratoren bestimmt und sollte normalen Benutzern/Arbeitern nicht angezeigt werden.",
        "admin_open": "Dashboard in neuem Tab öffnen",
        "about_title": "ℹ️ Über INNA Financial Coach AI",
        "about_text": "INNA ist eine Finanzpädagogin mit generativer KI, die einfache Daten in Finanzdiagnosen, Aktionspläne, PDF-Berichte und echte Kennzahlen verwandelt.",
        "about_resources": "Projektressourcen",
        "about_success": "Projekt bereit für Portfolio, Hackathons und Weiterentwicklung zum Banking-Assistenten.",
    },
    "fr": {
        "menu": "Menu",
        "public_access": "Accès public",
        "login_needed": "Connectez-vous pour utiliser le diagnostic, le rapport, l’historique et l’espace admin.",
        "login_button": "🔑 Se connecter",
        "connected": "Statut : connecté",
        "user": "Utilisateur",
        "profile": "Profil",
        "logout_success": "Vous vous êtes déconnecté d’INNA.",
        "browser_warning": "Pour tester correctement les langues, désactivez le traducteur automatique du navigateur.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Espace administratif pour les gestionnaires, administrateurs ou évaluateurs afin de suivre les métriques de la plateforme.",
        "admin_warning": "Ce tableau de bord est destiné à l’administrateur d’INNA. Il ne doit pas apparaître pour l’utilisateur/travailleur standard.",
        "admin_open": "Ouvrir le dashboard dans un nouvel onglet",
        "about_title": "ℹ️ À propos d’INNA Financial Coach AI",
        "about_text": "INNA est une éducatrice financière avec IA générative, créée pour transformer des données simples en diagnostic financier, plan d’action, rapport PDF et indicateurs réels.",
        "about_resources": "Ressources du projet",
        "about_success": "Projet prêt pour portfolio, hackathons et évolution vers un assistant bancaire.",
    },
    "it": {
        "menu": "Menu",
        "public_access": "Accesso pubblico",
        "login_needed": "Accedi per usare diagnosi, report, storico e area admin.",
        "login_button": "🔑 Accedi",
        "connected": "Stato: connesso",
        "user": "Utente",
        "profile": "Profilo",
        "logout_success": "Sei uscito da INNA.",
        "browser_warning": "Per testare correttamente le lingue, disattiva il traduttore automatico del browser.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Area amministrativa per manager, amministratori o valutatori per monitorare le metriche della piattaforma.",
        "admin_warning": "Questo pannello è destinato agli amministratori di INNA. Non deve apparire all’utente comune/lavoratore.",
        "admin_open": "Apri dashboard in una nuova scheda",
        "about_title": "ℹ️ Informazioni su INNA Financial Coach AI",
        "about_text": "INNA è un’educatrice finanziaria con IA generativa, creata per trasformare dati semplici in diagnosi finanziaria, piano d’azione, report PDF e indicatori reali.",
        "about_resources": "Risorse del progetto",
        "about_success": "Progetto pronto per portfolio, hackathon ed evoluzione verso assistente bancario.",
    },
    "ro": {
        "menu": "Meniu",
        "public_access": "Acces public",
        "login_needed": "Autentifică-te pentru diagnostic, raport, istoric și zona admin.",
        "login_button": "🔑 Intră",
        "connected": "Status: conectat",
        "user": "Utilizator",
        "profile": "Profil",
        "logout_success": "Ai ieșit din INNA.",
        "browser_warning": "Pentru a testa corect limbile, dezactivează traducătorul automat al browserului.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Zonă administrativă pentru manageri, administratori sau evaluatori pentru monitorizarea metricilor platformei.",
        "admin_warning": "Acest panou este destinat administratorului INNA. Nu trebuie să apară pentru utilizatorul obișnuit/lucrător.",
        "admin_open": "Deschide dashboardul într-o filă nouă",
        "about_title": "ℹ️ Despre INNA Financial Coach AI",
        "about_text": "INNA este o educatoare financiară cu IA generativă, creată pentru a transforma date simple în diagnostic financiar, plan de acțiune, raport PDF și indicatori reali.",
        "about_resources": "Resursele proiectului",
        "about_success": "Proiect pregătit pentru portofoliu, hackathoane și evoluție către asistent bancar.",
    },
    "ru": {
        "menu": "Меню",
        "public_access": "Публичный доступ",
        "login_needed": "Войдите, чтобы использовать диагностику, отчёт, историю и административную область.",
        "login_button": "🔑 Войти",
        "connected": "Статус: подключено",
        "user": "Пользователь",
        "profile": "Профиль",
        "logout_success": "Вы вышли из INNA.",
        "browser_warning": "Для корректной проверки языков отключите автоматический переводчик браузера.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Административная область для менеджера, администратора или проверяющего для отслеживания метрик платформы.",
        "admin_warning": "Эта панель предназначена для администратора INNA. Она не должна отображаться обычному пользователю/работнику.",
        "admin_open": "Открыть dashboard в новой вкладке",
        "about_title": "ℹ️ О INNA Financial Coach AI",
        "about_text": "INNA — финансовый помощник с генеративным ИИ, созданный для превращения простых данных в финансовую диагностику, план действий, PDF-отчёт и реальные показатели.",
        "about_resources": "Ресурсы проекта",
        "about_success": "Проект готов для портфолио, хакатонов и развития в банковского ассистента.",
    },
    "uk": {
        "menu": "Меню",
        "public_access": "Публічний доступ",
        "login_needed": "Увійдіть, щоб використовувати діагностику, звіт, історію та адміністративну область.",
        "login_button": "🔑 Увійти",
        "connected": "Статус: підключено",
        "user": "Користувач",
        "profile": "Профіль",
        "logout_success": "Ви вийшли з INNA.",
        "browser_warning": "Для коректної перевірки мов вимкніть автоматичний перекладач браузера.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Адміністративна область для менеджера, адміністратора або оцінювача для відстеження метрик платформи.",
        "admin_warning": "Ця панель призначена для адміністратора INNA. Вона не повинна відображатися звичайному користувачу/працівнику.",
        "admin_open": "Відкрити dashboard у новій вкладці",
        "about_title": "ℹ️ Про INNA Financial Coach AI",
        "about_text": "INNA — фінансова помічниця з генеративним ШІ, створена для перетворення простих даних у фінансову діагностику, план дій, PDF-звіт і реальні показники.",
        "about_resources": "Ресурси проєкту",
        "about_success": "Проєкт готовий для портфоліо, хакатонів і розвитку в банківського асистента.",
    },
    "ar": {
        "menu": "القائمة",
        "public_access": "وصول عام",
        "login_needed": "سجّل الدخول لاستخدام التشخيص والتقرير والسجل ومنطقة الإدارة.",
        "login_button": "🔑 تسجيل الدخول",
        "connected": "الحالة: متصل",
        "user": "المستخدم",
        "profile": "الملف الشخصي",
        "logout_success": "لقد خرجت من INNA.",
        "browser_warning": "لاختبار اللغات بشكل صحيح، عطّل الترجمة التلقائية في المتصفح.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "منطقة إدارية للمدير أو المسؤول أو المقيّم لمتابعة مؤشرات المنصة.",
        "admin_warning": "هذه اللوحة مخصصة لمسؤول INNA ولا يجب أن تظهر للمستخدم العادي/العامل.",
        "admin_open": "فتح لوحة البيانات في تبويب جديد",
        "about_title": "ℹ️ حول INNA Financial Coach AI",
        "about_text": "INNA هي أداة تعليم مالي بالذكاء الاصطناعي التوليدي، صُممت لتحويل البيانات البسيطة إلى تشخيص مالي وخطة عمل وتقرير PDF ومؤشرات حقيقية.",
        "about_resources": "موارد المشروع",
        "about_success": "المشروع جاهز للملف المهني والهاكاثونات والتطوير كمساعد مصرفي.",
    },
    "ch": {
        "menu": "Menü",
        "public_access": "Öffentlicher Zugriff",
        "login_needed": "Melden Sie sich an, um Diagnose, Bericht, Verlauf und Adminbereich zu nutzen.",
        "login_button": "🔑 Anmelden",
        "connected": "Status: verbunden",
        "user": "Benutzer",
        "profile": "Profil",
        "logout_success": "Sie haben sich von INNA abgemeldet.",
        "browser_warning": "Um Sprachen korrekt zu testen, deaktivieren Sie den automatischen Browser-Übersetzer.",
        "admin_title": "🔐 Admin Analytics — INNA",
        "admin_caption": "Administrativer Bereich zur Überwachung der Plattformmetriken.",
        "admin_warning": "Dieses Dashboard ist für INNA-Administratoren bestimmt und sollte normalen Benutzern nicht angezeigt werden.",
        "admin_open": "Dashboard in neuem Tab öffnen",
        "about_title": "ℹ️ Über INNA Financial Coach AI",
        "about_text": "INNA ist eine Finanzpädagogin mit generativer KI, die einfache Daten in Finanzdiagnosen, Aktionspläne, PDF-Berichte und echte Kennzahlen verwandelt.",
        "about_resources": "Projektressourcen",
        "about_success": "Projekt bereit für Portfolio, Hackathons und Weiterentwicklung zum Banking-Assistenten.",
    },
}

MENU_LABELS_INNA = {
    "pt": {
        "🏠 Início": "🏠 Início",
        "🔑 Entrar": "🔑 Entrar",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "💬 Conversar": "💬 Conversar",
        "📄 Relatório": "📄 Relatório",
        "📚 Histórico": "📚 Histórico",
        "⭐ Avaliar": "⭐ Avaliar",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Sobre",
        "🚪 Sair": "🚪 Sair",
    },
    "en_us": {
        "🏠 Início": "🏠 Home",
        "🔑 Entrar": "🔑 Sign in",
        "🧾 Diagnóstico": "🧾 New diagnosis",
        "📊 Panorama": "📊 My financial overview",
        "💬 Conversar": "💬 Chat with Inna",
        "📄 Relatório": "📄 My report",
        "📚 Histórico": "📚 My history",
        "⭐ Avaliar": "⭐ Rate Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ About INNA",
        "🚪 Sair": "🚪 Sign out",
    },
    "en_gb": {
        "🏠 Início": "🏠 Home",
        "🔑 Entrar": "🔑 Sign in",
        "🧾 Diagnóstico": "🧾 New diagnosis",
        "📊 Panorama": "📊 My financial overview",
        "💬 Conversar": "💬 Chat with Inna",
        "📄 Relatório": "📄 My report",
        "📚 Histórico": "📚 My history",
        "⭐ Avaliar": "⭐ Rate Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ About INNA",
        "🚪 Sair": "🚪 Sign out",
    },
    "es": {
        "🏠 Início": "🏠 Inicio",
        "🔑 Entrar": "🔑 Entrar",
        "🧾 Diagnóstico": "🧾 Nuevo diagnóstico",
        "📊 Panorama": "📊 Mi panorama financiero",
        "💬 Conversar": "💬 Conversar con Inna",
        "📄 Relatório": "📄 Mi informe",
        "📚 Histórico": "📚 Mi historial",
        "⭐ Avaliar": "⭐ Evaluar a Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Sobre INNA",
        "🚪 Sair": "🚪 Salir",
    },
}

for lang_code in ["de", "fr", "it", "ro", "ru", "uk", "ar", "ch"]:
    MENU_LABELS_INNA[lang_code] = MENU_LABELS_INNA["en_us"]

def ui_t(key: str) -> str:
    lang = app_lang if app_lang in GLOBAL_UI_TEXTS_INNA else "pt"
    return GLOBAL_UI_TEXTS_INNA.get(lang, GLOBAL_UI_TEXTS_INNA["pt"]).get(
        key,
        GLOBAL_UI_TEXTS_INNA["pt"].get(key, key),
    )

def menu_t(key: str) -> str:
    lang = app_lang if app_lang in MENU_LABELS_INNA else "pt"
    return MENU_LABELS_INNA.get(lang, MENU_LABELS_INNA["pt"]).get(key, key)

# MENU_LABELS_INNA_COMPLETO
MENU_LABELS_INNA = {
    "pt": {
        "🏠 Início": "🏠 Início",
        "🔑 Entrar": "🔑 Entrar",
        "🧾 Diagnóstico": "🧾 Diagnóstico",
        "📊 Panorama": "📊 Panorama",
        "💬 Conversar": "💬 Conversar",
        "📄 Relatório": "📄 Relatório",
        "📚 Histórico": "📚 Histórico",
        "⭐ Avaliar": "⭐ Avaliar",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Sobre",
        "🚪 Sair": "🚪 Sair",
    },
    "en_us": {
        "🏠 Início": "🏠 Home",
        "🔑 Entrar": "🔑 Sign in",
        "🧾 Diagnóstico": "🧾 New diagnosis",
        "📊 Panorama": "📊 My financial overview",
        "💬 Conversar": "💬 Chat with Inna",
        "📄 Relatório": "📄 My report",
        "📚 Histórico": "📚 My history",
        "⭐ Avaliar": "⭐ Rate Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ About INNA",
        "🚪 Sair": "🚪 Sign out",
    },
    "en_gb": {
        "🏠 Início": "🏠 Home",
        "🔑 Entrar": "🔑 Sign in",
        "🧾 Diagnóstico": "🧾 New diagnosis",
        "📊 Panorama": "📊 My financial overview",
        "💬 Conversar": "💬 Chat with Inna",
        "📄 Relatório": "📄 My report",
        "📚 Histórico": "📚 My history",
        "⭐ Avaliar": "⭐ Rate Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ About INNA",
        "🚪 Sair": "🚪 Sign out",
    },
    "es": {
        "🏠 Início": "🏠 Inicio",
        "🔑 Entrar": "🔑 Entrar",
        "🧾 Diagnóstico": "🧾 Nuevo diagnóstico",
        "📊 Panorama": "📊 Mi panorama financiero",
        "💬 Conversar": "💬 Conversar con Inna",
        "📄 Relatório": "📄 Mi informe",
        "📚 Histórico": "📚 Mi historial",
        "⭐ Avaliar": "⭐ Evaluar a Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Sobre INNA",
        "🚪 Sair": "🚪 Salir",
    },
    "de": {
        "🏠 Início": "🏠 Startseite",
        "🔑 Entrar": "🔑 Anmelden",
        "🧾 Diagnóstico": "🧾 Neue Diagnose",
        "📊 Panorama": "📊 Meine Finanzübersicht",
        "💬 Conversar": "💬 Mit Inna sprechen",
        "📄 Relatório": "📄 Mein Bericht",
        "📚 Histórico": "📚 Mein Verlauf",
        "⭐ Avaliar": "⭐ Inna bewerten",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Über INNA",
        "🚪 Sair": "🚪 Abmelden",
    },
    "fr": {
        "🏠 Início": "🏠 Accueil",
        "🔑 Entrar": "🔑 Se connecter",
        "🧾 Diagnóstico": "🧾 Nouveau diagnostic",
        "📊 Panorama": "📊 Mon panorama financier",
        "💬 Conversar": "💬 Parler avec Inna",
        "📄 Relatório": "📄 Mon rapport",
        "📚 Histórico": "📚 Mon historique",
        "⭐ Avaliar": "⭐ Évaluer Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ À propos d’INNA",
        "🚪 Sair": "🚪 Se déconnecter",
    },
    "it": {
        "🏠 Início": "🏠 Inizio",
        "🔑 Entrar": "🔑 Accedi",
        "🧾 Diagnóstico": "🧾 Nuova diagnosi",
        "📊 Panorama": "📊 Il mio panorama finanziario",
        "💬 Conversar": "💬 Parlare con Inna",
        "📄 Relatório": "📄 Il mio report",
        "📚 Histórico": "📚 Il mio storico",
        "⭐ Avaliar": "⭐ Valuta Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Informazioni su INNA",
        "🚪 Sair": "🚪 Esci",
    },
    "ro": {
        "🏠 Início": "🏠 Acasă",
        "🔑 Entrar": "🔑 Intră",
        "🧾 Diagnóstico": "🧾 Diagnostic nou",
        "📊 Panorama": "📊 Panorama mea financiară",
        "💬 Conversar": "💬 Vorbește cu Inna",
        "📄 Relatório": "📄 Raportul meu",
        "📚 Histórico": "📚 Istoricul meu",
        "⭐ Avaliar": "⭐ Evaluează Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Despre INNA",
        "🚪 Sair": "🚪 Ieșire",
    },
    "ru": {
        "🏠 Início": "🏠 Главная",
        "🔑 Entrar": "🔑 Войти",
        "🧾 Diagnóstico": "🧾 Новая диагностика",
        "📊 Panorama": "📊 Мой финансовый обзор",
        "💬 Conversar": "💬 Поговорить с Inna",
        "📄 Relatório": "📄 Мой отчёт",
        "📚 Histórico": "📚 Моя история",
        "⭐ Avaliar": "⭐ Оценить Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ О INNA",
        "🚪 Sair": "🚪 Выйти",
    },
    "uk": {
        "🏠 Início": "🏠 Головна",
        "🔑 Entrar": "🔑 Увійти",
        "🧾 Diagnóstico": "🧾 Нова діагностика",
        "📊 Panorama": "📊 Мій фінансовий огляд",
        "💬 Conversar": "💬 Поговорити з Inna",
        "📄 Relatório": "📄 Мій звіт",
        "📚 Histórico": "📚 Моя історія",
        "⭐ Avaliar": "⭐ Оцінити Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Про INNA",
        "🚪 Sair": "🚪 Вийти",
    },
    "ar": {
        "🏠 Início": "🏠 الرئيسية",
        "🔑 Entrar": "🔑 تسجيل الدخول",
        "🧾 Diagnóstico": "🧾 تشخيص جديد",
        "📊 Panorama": "📊 نظرتي المالية",
        "💬 Conversar": "💬 التحدث مع Inna",
        "📄 Relatório": "📄 تقريري",
        "📚 Histórico": "📚 سجلي",
        "⭐ Avaliar": "⭐ تقييم Inna",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ حول INNA",
        "🚪 Sair": "🚪 تسجيل الخروج",
    },
    "ch": {
        "🏠 Início": "🏠 Startseite",
        "🔑 Entrar": "🔑 Anmelden",
        "🧾 Diagnóstico": "🧾 Neue Diagnose",
        "📊 Panorama": "📊 Meine Finanzübersicht",
        "💬 Conversar": "💬 Mit Inna sprechen",
        "📄 Relatório": "📄 Mein Bericht",
        "📚 Histórico": "📚 Mein Verlauf",
        "⭐ Avaliar": "⭐ Inna bewerten",
        "🔐 Admin Analytics": "🔐 Admin Analytics",
        "ℹ️ Sobre": "ℹ️ Über INNA",
        "🚪 Sair": "🚪 Abmelden",
    },
}

def menu_t(key: str) -> str:
    lang = app_lang if app_lang in MENU_LABELS_INNA else "pt"
    return MENU_LABELS_INNA.get(lang, MENU_LABELS_INNA["pt"]).get(key, key)
def translate_risk_app(risk: str) -> str:
    risk = str(risk or "").strip()

    risk_map = {
        "Baixo": {
            "pt": "Baixo",
            "en_us": "Low",
            "en_gb": "Low",
            "es": "Bajo",
            "fr": "Faible",
            "de": "Niedrig",
            "ch": "Niedrig",
            "it": "Basso",
            "ro": "Scăzut",
            "uk": "Низький",
            "ru": "Низкий",
            "ar": "منخفض",
        },
        "Medio": {
            "pt": "Médio",
            "en_us": "Medium",
            "en_gb": "Medium",
            "es": "Medio",
            "fr": "Moyen",
            "de": "Mittel",
            "ch": "Mittel",
            "it": "Medio",
            "ro": "Mediu",
            "uk": "Середній",
            "ru": "Средний",
            "ar": "متوسط",
        },
        "Médio": {
            "pt": "Médio",
            "en_us": "Medium",
            "en_gb": "Medium",
            "es": "Medio",
            "fr": "Moyen",
            "de": "Mittel",
            "ch": "Mittel",
            "it": "Medio",
            "ro": "Mediu",
            "uk": "Середній",
            "ru": "Средний",
            "ar": "متوسط",
        },
        "Alto": {
            "pt": "Alto",
            "en_us": "High",
            "en_gb": "High",
            "es": "Alto",
            "fr": "Élevé",
            "de": "Hoch",
            "ch": "Hoch",
            "it": "Alto",
            "ro": "Ridicat",
            "uk": "Високий",
            "ru": "Высокий",
            "ar": "مرتفع",
        },
    }

    return risk_map.get(risk, {}).get(app_lang, risk)


def label_with_currency(key: str) -> str:
    currency = current_currency_info.get("moeda", "")
    symbol = current_currency_info.get("simbolo", "")

    if symbol and symbol != currency:
        return f"{tr(key)} ({currency} / {symbol})"

    return f"{tr(key)} ({currency})"


def format_currency_app(value, symbol: str, currency: str) -> str:
    try:
        value = float(value)
    except Exception:
        value = 0.0

    # Brasil e padrão europeu: 3.500,00
    if currency in ["BRL", "EUR", "RON"]:
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        if currency == "RON":
            return f"{formatted} {symbol}".strip()
        return f"{symbol} {formatted}".strip()

    # Suíça: 3'500.00
    if currency == "CHF":
        formatted = f"{value:,.2f}".replace(",", "'")
        return f"{symbol} {formatted}".strip()

    # Ucrânia e Rússia: 3 500,00
    if currency in ["UAH", "RUB"]:
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", " ").replace(".", ",")
        return f"{symbol} {formatted}".strip()

    # Inglês, dólar, libra, rial e demais: 3,500.00
    formatted = f"{value:,.2f}"

    if symbol:
        return f"{symbol} {formatted}".strip()

    return f"{currency} {formatted}".strip()


def tr(key: str) -> str:
    return APP_TRANSLATIONS.get(app_lang, APP_TRANSLATIONS["pt"]).get(
        key,
        APP_TRANSLATIONS["pt"].get(key, key),
    )

current_currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

st.sidebar.title("💰 INNA")
st.sidebar.caption("Educadora Financeira Inteligente")

if "app_menu_selected" not in st.session_state:
    st.session_state.app_menu_selected = "🏠 Início"


# =============================
# TOPO PRINCIPAL DA INNA
# =============================

st.markdown("""
<div class="inna-top-title">💰 INNA Financial Coach AI</div>
<div class="inna-top-subtitle">Educadora Financeira Inteligente • Web App • IA • Diagnóstico financeiro</div>
<div class="inna-top-divider"></div>
""", unsafe_allow_html=True)

# Linha superior: idioma, tema e login/sair
top_lang_col, top_theme_col, top_login_col = st.columns([1.4, 1.1, 1])

with top_lang_col:
    app_lang = st.selectbox(
        "🌍 Idioma / Language",
        options=list(APP_LANG_LABELS.keys()),
        index=list(APP_LANG_LABELS.keys()).index(st.session_state.app_lang),
        format_func=lambda key: APP_LANG_LABELS[key],
        key="app_lang_top",
    )
    

# Atualiza idioma e moeda após mudança no seletor superior
st.session_state.app_lang = app_lang
current_currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

with top_theme_col:
    st.session_state.theme_name = st.selectbox(
        "🎨 Tema",
        list(THEMES_INNA.keys()),
        index=list(THEMES_INNA.keys()).index(st.session_state.theme_name),
        key="theme_selector_top",
    )
    theme = THEMES_INNA[st.session_state.theme_name]

with top_login_col:
    st.write("")
    if st.session_state.get("logado"):
        if st.button("🚪 Sair", use_container_width=True, key="btn_top_sair"):
            st.session_state.logado = False
            st.session_state.usuario = None
            st.session_state.perfil_usuario = None
            st.session_state.app_menu_selected = "🏠 Início"
            st.session_state.show_login_page = False
            st.rerun()
    else:
        if st.button(ui_t("login_button") if "ui_t" in globals() else "🔑 Entrar", use_container_width=True, key="btn_top_entrar"):
            st.session_state.show_login_page = True
            st.rerun()


# Labels curtos para o menu superior
def top_menu_t(menu_item: str) -> str:
    top_labels = {
        "pt": {
            "🏠 Início": "🏠 Início",
            "🧾 Diagnóstico": "🧾 Diagnóstico",
            "📊 Panorama": "📊 Panorama",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Relatório",
            "📚 Histórico": "📚 Histórico",
            "⭐ Avaliar": "⭐ Avaliar",
            "ℹ️ Sobre": "ℹ️ Sobre",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "en_us": {
            "🏠 Início": "🏠 Home",
            "🧾 Diagnóstico": "🧾 Diagnosis",
            "📊 Panorama": "📊 Overview",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Report",
            "📚 Histórico": "📚 History",
            "⭐ Avaliar": "⭐ Rate",
            "ℹ️ Sobre": "ℹ️ About",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "en_gb": {
            "🏠 Início": "🏠 Home",
            "🧾 Diagnóstico": "🧾 Diagnosis",
            "📊 Panorama": "📊 Overview",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Report",
            "📚 Histórico": "📚 History",
            "⭐ Avaliar": "⭐ Rate",
            "ℹ️ Sobre": "ℹ️ About",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "es": {
            "🏠 Início": "🏠 Inicio",
            "🧾 Diagnóstico": "🧾 Diagnóstico",
            "📊 Panorama": "📊 Panorama",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Informe",
            "📚 Histórico": "📚 Historial",
            "⭐ Avaliar": "⭐ Evaluar",
            "ℹ️ Sobre": "ℹ️ Sobre",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "fr": {
            "🏠 Início": "🏠 Accueil",
            "🧾 Diagnóstico": "🧾 Diagnostic",
            "📊 Panorama": "📊 Aperçu",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Rapport",
            "📚 Histórico": "📚 Historique",
            "⭐ Avaliar": "⭐ Évaluer",
            "ℹ️ Sobre": "ℹ️ À propos",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "de": {
            "🏠 Início": "🏠 Start",
            "🧾 Diagnóstico": "🧾 Diagnose",
            "📊 Panorama": "📊 Übersicht",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Bericht",
            "📚 Histórico": "📚 Verlauf",
            "⭐ Avaliar": "⭐ Bewerten",
            "ℹ️ Sobre": "ℹ️ Über",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "it": {
            "🏠 Início": "🏠 Home",
            "🧾 Diagnóstico": "🧾 Diagnosi",
            "📊 Panorama": "📊 Panoramica",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Report",
            "📚 Histórico": "📚 Storico",
            "⭐ Avaliar": "⭐ Valuta",
            "ℹ️ Sobre": "ℹ️ Info",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "ro": {
            "🏠 Início": "🏠 Acasă",
            "🧾 Diagnóstico": "🧾 Diagnostic",
            "📊 Panorama": "📊 Prezentare",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Raport",
            "📚 Histórico": "📚 Istoric",
            "⭐ Avaliar": "⭐ Evaluare",
            "ℹ️ Sobre": "ℹ️ Despre",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "uk": {
            "🏠 Início": "🏠 Головна",
            "🧾 Diagnóstico": "🧾 Діагноз",
            "📊 Panorama": "📊 Огляд",
            "💬 Conversar": "💬 Чат",
            "📄 Relatório": "📄 Звіт",
            "📚 Histórico": "📚 Історія",
            "⭐ Avaliar": "⭐ Оцінка",
            "ℹ️ Sobre": "ℹ️ Про",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "ru": {
            "🏠 Início": "🏠 Главная",
            "🧾 Diagnóstico": "🧾 Диагноз",
            "📊 Panorama": "📊 Обзор",
            "💬 Conversar": "💬 Чат",
            "📄 Relatório": "📄 Отчёт",
            "📚 Histórico": "📚 История",
            "⭐ Avaliar": "⭐ Оценка",
            "ℹ️ Sobre": "ℹ️ О INNA",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "ar": {
            "🏠 Início": "🏠 الرئيسية",
            "🧾 Diagnóstico": "🧾 التشخيص",
            "📊 Panorama": "📊 نظرة",
            "💬 Conversar": "💬 دردشة",
            "📄 Relatório": "📄 تقرير",
            "📚 Histórico": "📚 السجل",
            "⭐ Avaliar": "⭐ تقييم",
            "ℹ️ Sobre": "ℹ️ حول",
            "🔐 Admin Analytics": "🔐 Admin",
        },
        "ch": {
            "🏠 Início": "🏠 Start",
            "🧾 Diagnóstico": "🧾 Diagnose",
            "📊 Panorama": "📊 Übersicht",
            "💬 Conversar": "💬 Chat",
            "📄 Relatório": "📄 Bericht",
            "📚 Histórico": "📚 Verlauf",
            "⭐ Avaliar": "⭐ Bewerten",
            "ℹ️ Sobre": "ℹ️ Über",
            "🔐 Admin Analytics": "🔐 Admin",
        },
    }

    lang = st.session_state.get("app_lang", app_lang)
    return top_labels.get(lang, top_labels["pt"]).get(menu_item, menu_t(menu_item))


# Linha do menu principal
menu_options_top = [
    "🏠 Início",
    "🧾 Diagnóstico",
    "📊 Panorama",
    "💬 Conversar",
    "📄 Relatório",
    "📚 Histórico",
    "⭐ Avaliar",
    "ℹ️ Sobre",
]

if st.session_state.get("perfil_usuario") == "admin":
    menu_options_top.insert(-1, "🔐 Admin Analytics")

    if "🔐 Admin Analytics" not in APP_MENU_OPTIONS:
        APP_MENU_OPTIONS.append("🔐 Admin Analytics")

menu_cols = st.columns(len(menu_options_top))

for index_menu, menu_item in enumerate(menu_options_top):
    with menu_cols[index_menu]:
        label_menu = top_menu_t(menu_item)
        if st.button(label_menu, use_container_width=True, key=f"top_menu_{index_menu}_{menu_item}"):
            st.session_state.app_menu_selected = menu_item
            st.rerun()

st.markdown("<div class='inna-top-divider'></div>", unsafe_allow_html=True)
app_menu = st.sidebar.radio(
    ui_t("menu") if "ui_t" in globals() else "Menu",
    APP_MENU_OPTIONS,
    index=APP_MENU_OPTIONS.index(st.session_state.app_menu_selected)
    if st.session_state.app_menu_selected in APP_MENU_OPTIONS
    else 0,
    key="app_menu_radio",
    format_func=menu_t,
)

st.session_state.app_menu_selected = app_menu


st.sidebar.divider()

if st.session_state.get("logado"):
    st.sidebar.success(ui_t("connected"))
    st.sidebar.caption(f"{ui_t('user')}: {st.session_state.get('usuario')}")
    st.sidebar.caption(f"{ui_t('profile')}: {st.session_state.get('perfil_usuario')}")
else:
    st.sidebar.info(ui_t("public_access"))
    st.sidebar.caption(ui_t("login_needed"))

    if st.sidebar.button(ui_t("login_button"), use_container_width=True, key="btn_sidebar_login_publico"):
        st.session_state.app_menu_selected = "🔑 Entrar"
        st.rerun()

st.sidebar.divider()

st.sidebar.caption(ui_t("browser_warning"))




HOME_TEXTS_INNA = {
    "pt": {
        "badge": "✨ AI Financial Assistant • Educação financeira inteligente",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Assistente virtual de educação financeira com IA",
        "intro": "A INNA ajuda pessoas a entenderem renda, gastos, dívidas, reserva financeira e próximos passos de forma simples, educativa e personalizada.",
        "what_title": "O que é a INNA?",
        "what_text": "A INNA Financial Coach AI é uma educadora financeira inteligente que transforma dados básicos do usuário em uma visão clara da situação atual. A plataforma pode gerar diagnóstico financeiro, plano de ação de 30 dias, relatório em PDF, envio por e-mail, histórico individual, registros analíticos para dashboard e atendimento multicanal via Web e Telegram.",
        "features_title": "Principais recursos",
        "how_title": "Como funciona",
        "quick_title": "Visão rápida do diagnóstico",
        "feature_1_title": "📋 Diagnóstico financeiro",
        "feature_1_text": "Analisa renda, gastos, dívidas e reserva financeira para gerar uma visão clara da situação atual.",
        "feature_2_title": "🧠 IA Generativa",
        "feature_2_text": "Gera explicações simples e um plano de ação personalizado para os próximos 30 dias.",
        "feature_3_title": "📄 Relatório PDF + E-mail",
        "feature_3_text": "Permite baixar o relatório financeiro ou receber o diagnóstico diretamente por e-mail.",
        "feature_4_title": "🌐 Multicanal e multilíngue",
        "feature_4_text": "Funciona via Web App, Telegram, API e Dashboard, com suporte a diferentes idiomas e moedas.",
        "step_1_title": "Preencha",
        "step_1_text": "Informe renda, gastos, dívidas e reserva financeira.",
        "step_2_title": "Receba análise",
        "step_2_text": "A INNA calcula os principais indicadores financeiros.",
        "step_3_title": "Veja o plano",
        "step_3_text": "A IA gera uma orientação educativa personalizada.",
        "step_4_title": "Baixe ou envie",
        "step_4_text": "Exporte em PDF ou receba o relatório por e-mail.",
        "income": "Renda mensal",
        "expenses": "Gastos fixos",
        "debts": "Dívidas",
        "reserve": "Reserva",
        "warning": "Aviso importante: a INNA é uma ferramenta educativa. Ela não substitui consultoria financeira, contábil, jurídica ou bancária profissional.",
        "cta_title": "Comece seu diagnóstico financeiro agora",
        "cta_text": "Organize sua vida financeira com uma assistente virtual inteligente, simples e personalizada.",
        "btn_start": "🧾 Começar novo diagnóstico",
        "btn_report": "📄 Gerar relatório",
        "btn_about": "ℹ️ Ver sobre o projeto",
    },
    "en_us": {
        "badge": "✨ AI Financial Assistant • Smart financial education",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "AI-powered financial education virtual assistant",
        "intro": "INNA helps people understand income, expenses, debt, emergency savings and next steps in a simple, educational and personalized way.",
        "what_title": "What is INNA?",
        "what_text": "INNA Financial Coach AI is an intelligent financial educator that turns basic user data into a clear view of the current financial situation. The platform can generate a financial diagnosis, a 30-day action plan, PDF report, email delivery, individual history, analytics records and multichannel support via Web and Telegram.",
        "features_title": "Main features",
        "how_title": "How it works",
        "quick_title": "Quick diagnosis overview",
        "feature_1_title": "📋 Financial diagnosis",
        "feature_1_text": "Analyzes income, expenses, debt and emergency savings to generate a clear view of the current situation.",
        "feature_2_title": "🧠 Generative AI",
        "feature_2_text": "Generates simple explanations and a personalized action plan for the next 30 days.",
        "feature_3_title": "📄 PDF report + Email",
        "feature_3_text": "Allows users to download the financial report or receive the diagnosis directly by email.",
        "feature_4_title": "🌐 Multichannel and multilingual",
        "feature_4_text": "Works through Web App, Telegram, API and Dashboard, with support for different languages and currencies.",
        "step_1_title": "Fill in",
        "step_1_text": "Enter income, expenses, debt and emergency savings.",
        "step_2_title": "Receive analysis",
        "step_2_text": "INNA calculates the main financial indicators.",
        "step_3_title": "See the plan",
        "step_3_text": "AI generates personalized educational guidance.",
        "step_4_title": "Download or send",
        "step_4_text": "Export as PDF or receive the report by email.",
        "income": "Monthly income",
        "expenses": "Fixed expenses",
        "debts": "Debt",
        "reserve": "Savings",
        "warning": "Important notice: INNA is an educational tool. It does not replace professional financial, accounting, legal or banking advice.",
        "cta_title": "Start your financial diagnosis now",
        "cta_text": "Organize your financial life with an intelligent, simple and personalized virtual assistant.",
        "btn_start": "🧾 Start new diagnosis",
        "btn_report": "📄 Generate report",
        "btn_about": "ℹ️ See project",
    },
    "es": {
        "badge": "✨ Asistente financiero con IA • Educación financiera inteligente",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Asistente virtual de educación financiera con IA",
        "intro": "INNA ayuda a las personas a entender ingresos, gastos, deudas, reserva financiera y próximos pasos de forma simple, educativa y personalizada.",
        "what_title": "¿Qué es INNA?",
        "what_text": "INNA Financial Coach AI es una educadora financiera inteligente que transforma datos básicos del usuario en una visión clara de la situación actual. La plataforma puede generar diagnóstico financiero, plan de acción de 30 días, informe PDF, envío por e-mail, historial individual, registros analíticos y atención multicanal vía Web y Telegram.",
        "features_title": "Principales recursos",
        "how_title": "Cómo funciona",
        "quick_title": "Vista rápida del diagnóstico",
        "feature_1_title": "📋 Diagnóstico financiero",
        "feature_1_text": "Analiza ingresos, gastos, deudas y reserva financiera para generar una visión clara de la situación actual.",
        "feature_2_title": "🧠 IA Generativa",
        "feature_2_text": "Genera explicaciones simples y un plan de acción personalizado para los próximos 30 días.",
        "feature_3_title": "📄 Informe PDF + E-mail",
        "feature_3_text": "Permite descargar el informe financiero o recibir el diagnóstico directamente por e-mail.",
        "feature_4_title": "🌐 Multicanal y multilingüe",
        "feature_4_text": "Funciona vía Web App, Telegram, API y Dashboard, con soporte para diferentes idiomas y monedas.",
        "step_1_title": "Completa",
        "step_1_text": "Informa ingresos, gastos, deudas y reserva financiera.",
        "step_2_title": "Recibe análisis",
        "step_2_text": "INNA calcula los principales indicadores financieros.",
        "step_3_title": "Mira el plan",
        "step_3_text": "La IA genera una orientación educativa personalizada.",
        "step_4_title": "Descarga o envía",
        "step_4_text": "Exporta en PDF o recibe el informe por e-mail.",
        "income": "Ingreso mensual",
        "expenses": "Gastos fijos",
        "debts": "Deudas",
        "reserve": "Reserva",
        "warning": "Aviso importante: INNA es una herramienta educativa. No sustituye consultoría financiera, contable, jurídica o bancaria profesional.",
        "cta_title": "Comienza tu diagnóstico financiero ahora",
        "cta_text": "Organiza tu vida financiera con una asistente virtual inteligente, simple y personalizada.",
        "btn_start": "🧾 Comenzar nuevo diagnóstico",
        "btn_report": "📄 Generar informe",
        "btn_about": "ℹ️ Ver proyecto",
    },
    "de": {
        "badge": "✨ KI-Finanzassistent • Intelligente Finanzbildung",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Virtuelle Assistentin für Finanzbildung mit KI",
        "intro": "INNA hilft Menschen, Einkommen, Ausgaben, Schulden, Rücklagen und nächste Schritte einfach, lehrreich und personalisiert zu verstehen.",
        "what_title": "Was ist INNA?",
        "what_text": "INNA Financial Coach AI ist eine intelligente Finanzpädagogin, die grundlegende Benutzerdaten in eine klare Sicht auf die aktuelle finanzielle Situation verwandelt.",
        "features_title": "Hauptfunktionen",
        "how_title": "So funktioniert es",
        "quick_title": "Schnellübersicht der Diagnose",
        "feature_1_title": "📋 Finanzdiagnose",
        "feature_1_text": "Analysiert Einkommen, Ausgaben, Schulden und Rücklagen, um eine klare Sicht auf die aktuelle Situation zu erzeugen.",
        "feature_2_title": "🧠 Generative KI",
        "feature_2_text": "Erstellt einfache Erklärungen und einen personalisierten Aktionsplan für die nächsten 30 Tage.",
        "feature_3_title": "📄 PDF-Bericht + E-Mail",
        "feature_3_text": "Ermöglicht das Herunterladen des Finanzberichts oder den direkten Erhalt der Diagnose per E-Mail.",
        "feature_4_title": "🌐 Multikanal und mehrsprachig",
        "feature_4_text": "Funktioniert über Web App, Telegram, API und Dashboard mit Unterstützung für verschiedene Sprachen und Währungen.",
        "step_1_title": "Ausfüllen",
        "step_1_text": "Einkommen, Ausgaben, Schulden und Rücklagen eingeben.",
        "step_2_title": "Analyse erhalten",
        "step_2_text": "INNA berechnet die wichtigsten Finanzindikatoren.",
        "step_3_title": "Plan ansehen",
        "step_3_text": "Die KI erstellt eine personalisierte Bildungsorientierung.",
        "step_4_title": "Herunterladen oder senden",
        "step_4_text": "Als PDF exportieren oder Bericht per E-Mail erhalten.",
        "income": "Monatliches Einkommen",
        "expenses": "Fixkosten",
        "debts": "Schulden",
        "reserve": "Rücklage",
        "warning": "Wichtiger Hinweis: INNA ist ein Bildungstool. Sie ersetzt keine professionelle Finanz-, Steuer-, Rechts- oder Bankberatung.",
        "cta_title": "Starte jetzt deine Finanzdiagnose",
        "cta_text": "Organisiere dein Finanzleben mit einer intelligenten, einfachen und personalisierten virtuellen Assistentin.",
        "btn_start": "🧾 Neue Diagnose starten",
        "btn_report": "📄 Bericht erstellen",
        "btn_about": "ℹ️ Projekt ansehen",
    },
    "fr": {
        "badge": "✨ Assistante financière IA • Éducation financière intelligente",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Assistante virtuelle d’éducation financière avec IA",
        "intro": "INNA aide les personnes à comprendre revenus, dépenses, dettes, épargne de précaution et prochaines étapes de manière simple, éducative et personnalisée.",
        "what_title": "Qu’est-ce qu’INNA ?",
        "what_text": "INNA Financial Coach AI est une éducatrice financière intelligente qui transforme des données simples en une vision claire de la situation financière actuelle.",
        "features_title": "Fonctionnalités principales",
        "how_title": "Comment ça fonctionne",
        "quick_title": "Aperçu rapide du diagnostic",
        "feature_1_title": "📋 Diagnostic financier",
        "feature_1_text": "Analyse les revenus, dépenses, dettes et l’épargne afin de générer une vision claire de la situation actuelle.",
        "feature_2_title": "🧠 IA générative",
        "feature_2_text": "Génère des explications simples et un plan d’action personnalisé pour les 30 prochains jours.",
        "feature_3_title": "📄 Rapport PDF + E-mail",
        "feature_3_text": "Permet de télécharger le rapport financier ou de recevoir le diagnostic directement par e-mail.",
        "feature_4_title": "🌐 Multicanal et multilingue",
        "feature_4_text": "Fonctionne via Web App, Telegram, API et Dashboard, avec prise en charge de plusieurs langues et devises.",
        "step_1_title": "Remplir",
        "step_1_text": "Indiquez revenus, dépenses, dettes et épargne.",
        "step_2_title": "Recevoir l’analyse",
        "step_2_text": "INNA calcule les principaux indicateurs financiers.",
        "step_3_title": "Voir le plan",
        "step_3_text": "L’IA génère une orientation éducative personnalisée.",
        "step_4_title": "Télécharger ou envoyer",
        "step_4_text": "Exportez en PDF ou recevez le rapport par e-mail.",
        "income": "Revenu mensuel",
        "expenses": "Dépenses fixes",
        "debts": "Dettes",
        "reserve": "Épargne",
        "warning": "Avis important : INNA est un outil éducatif. Elle ne remplace pas un conseil financier, comptable, juridique ou bancaire professionnel.",
        "cta_title": "Commencez votre diagnostic financier maintenant",
        "cta_text": "Organisez votre vie financière avec une assistante virtuelle intelligente, simple et personnalisée.",
        "btn_start": "🧾 Commencer un nouveau diagnostic",
        "btn_report": "📄 Générer le rapport",
        "btn_about": "ℹ️ Voir le projet",
    },
    "it": {
        "badge": "✨ Assistente finanziaria IA • Educazione finanziaria intelligente",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Assistente virtuale di educazione finanziaria con IA",
        "intro": "INNA aiuta le persone a comprendere reddito, spese, debiti, riserva finanziaria e prossimi passi in modo semplice, educativo e personalizzato.",
        "what_title": "Che cos’è INNA?",
        "what_text": "INNA Financial Coach AI è un’educatrice finanziaria intelligente che trasforma dati semplici in una visione chiara della situazione finanziaria attuale.",
        "features_title": "Funzionalità principali",
        "how_title": "Come funziona",
        "quick_title": "Panoramica rapida della diagnosi",
        "feature_1_title": "📋 Diagnosi finanziaria",
        "feature_1_text": "Analizza reddito, spese, debiti e riserva per generare una visione chiara della situazione attuale.",
        "feature_2_title": "🧠 IA Generativa",
        "feature_2_text": "Genera spiegazioni semplici e un piano d’azione personalizzato per i prossimi 30 giorni.",
        "feature_3_title": "📄 Report PDF + E-mail",
        "feature_3_text": "Permette di scaricare il report finanziario o ricevere la diagnosi direttamente via e-mail.",
        "feature_4_title": "🌐 Multicanale e multilingue",
        "feature_4_text": "Funziona via Web App, Telegram, API e Dashboard, con supporto a diverse lingue e valute.",
        "step_1_title": "Compila",
        "step_1_text": "Inserisci reddito, spese, debiti e riserva finanziaria.",
        "step_2_title": "Ricevi analisi",
        "step_2_text": "INNA calcola i principali indicatori finanziari.",
        "step_3_title": "Vedi il piano",
        "step_3_text": "L’IA genera un orientamento educativo personalizzato.",
        "step_4_title": "Scarica o invia",
        "step_4_text": "Esporta in PDF o ricevi il report via e-mail.",
        "income": "Reddito mensile",
        "expenses": "Spese fisse",
        "debts": "Debiti",
        "reserve": "Riserva",
        "warning": "Avviso importante: INNA è uno strumento educativo. Non sostituisce consulenza finanziaria, contabile, legale o bancaria professionale.",
        "cta_title": "Inizia ora la tua diagnosi finanziaria",
        "cta_text": "Organizza la tua vita finanziaria con un’assistente virtuale intelligente, semplice e personalizzata.",
        "btn_start": "🧾 Inizia nuova diagnosi",
        "btn_report": "📄 Genera report",
        "btn_about": "ℹ️ Vedi progetto",
    },
    "ro": {
        "badge": "✨ Asistent financiar IA • Educație financiară inteligentă",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Asistent virtual de educație financiară cu IA",
        "intro": "INNA ajută oamenii să înțeleagă veniturile, cheltuielile, datoriile, rezerva financiară și pașii următori într-un mod simplu, educativ și personalizat.",
        "what_title": "Ce este INNA?",
        "what_text": "INNA Financial Coach AI este o educatoare financiară inteligentă care transformă date simple într-o imagine clară a situației financiare actuale.",
        "features_title": "Funcții principale",
        "how_title": "Cum funcționează",
        "quick_title": "Prezentare rapidă a diagnosticului",
        "feature_1_title": "📋 Diagnostic financiar",
        "feature_1_text": "Analizează veniturile, cheltuielile, datoriile și rezerva pentru a genera o imagine clară a situației actuale.",
        "feature_2_title": "🧠 IA generativă",
        "feature_2_text": "Generează explicații simple și un plan de acțiune personalizat pentru următoarele 30 de zile.",
        "feature_3_title": "📄 Raport PDF + E-mail",
        "feature_3_text": "Permite descărcarea raportului financiar sau primirea diagnosticului direct prin e-mail.",
        "feature_4_title": "🌐 Multicanal și multilingv",
        "feature_4_text": "Funcționează prin Web App, Telegram, API și Dashboard, cu suport pentru diferite limbi și monede.",
        "step_1_title": "Completează",
        "step_1_text": "Introdu veniturile, cheltuielile, datoriile și rezerva financiară.",
        "step_2_title": "Primește analiza",
        "step_2_text": "INNA calculează principalii indicatori financiari.",
        "step_3_title": "Vezi planul",
        "step_3_text": "IA generează o orientare educativă personalizată.",
        "step_4_title": "Descarcă sau trimite",
        "step_4_text": "Exportă în PDF sau primește raportul prin e-mail.",
        "income": "Venit lunar",
        "expenses": "Cheltuieli fixe",
        "debts": "Datorii",
        "reserve": "Rezervă",
        "warning": "Notă importantă: INNA este un instrument educativ. Nu înlocuiește consultanța financiară, contabilă, juridică sau bancară profesională.",
        "cta_title": "Începe acum diagnosticul financiar",
        "cta_text": "Organizează-ți viața financiară cu un asistent virtual inteligent, simplu și personalizat.",
        "btn_start": "🧾 Începe diagnostic nou",
        "btn_report": "📄 Generează raport",
        "btn_about": "ℹ️ Vezi proiectul",
    },
    "uk": {
        "badge": "✨ Фінансовий асистент ШІ • Розумна фінансова освіта",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Віртуальна асистентка фінансової освіти з ШІ",
        "intro": "INNA допомагає людям зрозуміти доходи, витрати, борги, фінансовий резерв і наступні кроки просто, освітньо та персоналізовано.",
        "what_title": "Що таке INNA?",
        "what_text": "INNA Financial Coach AI — це інтелектуальна фінансова освітня асистентка, яка перетворює базові дані користувача на зрозумілу картину поточної фінансової ситуації.",
        "features_title": "Основні можливості",
        "how_title": "Як це працює",
        "quick_title": "Швидкий огляд діагностики",
        "feature_1_title": "📋 Фінансова діагностика",
        "feature_1_text": "Аналізує доходи, витрати, борги та резерв, щоб створити зрозумілу картину поточної ситуації.",
        "feature_2_title": "🧠 Генеративний ШІ",
        "feature_2_text": "Створює прості пояснення та персоналізований план дій на наступні 30 днів.",
        "feature_3_title": "📄 PDF-звіт + E-mail",
        "feature_3_text": "Дозволяє завантажити фінансовий звіт або отримати діагностику безпосередньо на e-mail.",
        "feature_4_title": "🌐 Мультиканальний і багатомовний",
        "feature_4_text": "Працює через Web App, Telegram, API і Dashboard з підтримкою різних мов і валют.",
        "step_1_title": "Заповніть",
        "step_1_text": "Вкажіть доходи, витрати, борги та фінансовий резерв.",
        "step_2_title": "Отримайте аналіз",
        "step_2_text": "INNA розраховує основні фінансові показники.",
        "step_3_title": "Перегляньте план",
        "step_3_text": "ШІ створює персоналізовану освітню рекомендацію.",
        "step_4_title": "Завантажте або надішліть",
        "step_4_text": "Експортуйте у PDF або отримайте звіт на e-mail.",
        "income": "Місячний дохід",
        "expenses": "Фіксовані витрати",
        "debts": "Борги",
        "reserve": "Резерв",
        "warning": "Важливе повідомлення: INNA є освітнім інструментом. Вона не замінює професійну фінансову, бухгалтерську, юридичну чи банківську консультацію.",
        "cta_title": "Почніть фінансову діагностику зараз",
        "cta_text": "Організуйте своє фінансове життя з розумною, простою та персоналізованою віртуальною асистенткою.",
        "btn_start": "🧾 Почати нову діагностику",
        "btn_report": "📄 Створити звіт",
        "btn_about": "ℹ️ Переглянути проєкт",
    },
    "ru": {
        "badge": "✨ Финансовый ИИ-ассистент • Умное финансовое обучение",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Виртуальный ассистент финансового образования с ИИ",
        "intro": "INNA помогает людям понять доходы, расходы, долги, финансовый резерв и следующие шаги простым, образовательным и персонализированным способом.",
        "what_title": "Что такое INNA?",
        "what_text": "INNA Financial Coach AI — это интеллектуальный финансовый образовательный ассистент, который превращает базовые данные пользователя в понятную картину текущей финансовой ситуации.",
        "features_title": "Основные функции",
        "how_title": "Как это работает",
        "quick_title": "Краткий обзор диагностики",
        "feature_1_title": "📋 Финансовая диагностика",
        "feature_1_text": "Анализирует доходы, расходы, долги и резерв, чтобы показать понятную картину текущей ситуации.",
        "feature_2_title": "🧠 Генеративный ИИ",
        "feature_2_text": "Создаёт простые объяснения и персонализированный план действий на следующие 30 дней.",
        "feature_3_title": "📄 PDF-отчёт + E-mail",
        "feature_3_text": "Позволяет скачать финансовый отчёт или получить диагностику напрямую по e-mail.",
        "feature_4_title": "🌐 Мультиканальный и многоязычный",
        "feature_4_text": "Работает через Web App, Telegram, API и Dashboard с поддержкой разных языков и валют.",
        "step_1_title": "Заполните",
        "step_1_text": "Введите доходы, расходы, долги и финансовый резерв.",
        "step_2_title": "Получите анализ",
        "step_2_text": "INNA рассчитывает основные финансовые показатели.",
        "step_3_title": "Посмотрите план",
        "step_3_text": "ИИ создаёт персонализированную образовательную рекомендацию.",
        "step_4_title": "Скачайте или отправьте",
        "step_4_text": "Экспортируйте в PDF или получите отчёт по e-mail.",
        "income": "Ежемесячный доход",
        "expenses": "Фиксированные расходы",
        "debts": "Долги",
        "reserve": "Резерв",
        "warning": "Важное уведомление: INNA является образовательным инструментом. Она не заменяет профессиональную финансовую, бухгалтерскую, юридическую или банковскую консультацию.",
        "cta_title": "Начните финансовую диагностику сейчас",
        "cta_text": "Организуйте свою финансовую жизнь с умным, простым и персонализированным виртуальным ассистентом.",
        "btn_start": "🧾 Начать новую диагностику",
        "btn_report": "📄 Создать отчёт",
        "btn_about": "ℹ️ Посмотреть проект",
    },
    "ar": {
        "badge": "✨ مساعد مالي بالذكاء الاصطناعي • تعليم مالي ذكي",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "مساعد افتراضي للتعليم المالي بالذكاء الاصطناعي",
        "intro": "تساعد INNA الأشخاص على فهم الدخل والمصروفات والديون والاحتياطي المالي والخطوات التالية بطريقة بسيطة وتعليمية وشخصية.",
        "what_title": "ما هي INNA؟",
        "what_text": "INNA Financial Coach AI هي أداة تعليم مالي ذكية تحول بيانات المستخدم الأساسية إلى رؤية واضحة للوضع المالي الحالي.",
        "features_title": "المزايا الرئيسية",
        "how_title": "كيف تعمل",
        "quick_title": "نظرة سريعة على التشخيص",
        "feature_1_title": "📋 تشخيص مالي",
        "feature_1_text": "تحلل الدخل والمصروفات والديون والاحتياطي المالي لتكوين رؤية واضحة للوضع الحالي.",
        "feature_2_title": "🧠 ذكاء اصطناعي توليدي",
        "feature_2_text": "ينشئ تفسيرات بسيطة وخطة عمل شخصية للأيام الثلاثين القادمة.",
        "feature_3_title": "📄 تقرير PDF + بريد إلكتروني",
        "feature_3_text": "يسمح بتنزيل التقرير المالي أو استلام التشخيص مباشرة عبر البريد الإلكتروني.",
        "feature_4_title": "🌐 متعدد القنوات واللغات",
        "feature_4_text": "يعمل عبر Web App وTelegram وAPI وDashboard مع دعم لغات وعملات مختلفة.",
        "step_1_title": "املأ البيانات",
        "step_1_text": "أدخل الدخل والمصروفات والديون والاحتياطي المالي.",
        "step_2_title": "استلم التحليل",
        "step_2_text": "تحسب INNA المؤشرات المالية الرئيسية.",
        "step_3_title": "راجع الخطة",
        "step_3_text": "ينشئ الذكاء الاصطناعي توجيهاً تعليمياً مخصصاً.",
        "step_4_title": "نزّل أو أرسل",
        "step_4_text": "صدّر بصيغة PDF أو استلم التقرير عبر البريد الإلكتروني.",
        "income": "الدخل الشهري",
        "expenses": "المصاريف الثابتة",
        "debts": "الديون",
        "reserve": "الاحتياطي",
        "warning": "تنبيه مهم: INNA أداة تعليمية. لا تستبدل الاستشارة المالية أو المحاسبية أو القانونية أو المصرفية المهنية.",
        "cta_title": "ابدأ تشخيصك المالي الآن",
        "cta_text": "نظّم حياتك المالية مع مساعد افتراضي ذكي وبسيط وشخصي.",
        "btn_start": "🧾 بدء تشخيص جديد",
        "btn_report": "📄 إنشاء التقرير",
        "btn_about": "ℹ️ عرض المشروع",
    },
    "ch": {
        "badge": "✨ KI-Finanzassistent • Intelligente Finanzbildung",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Virtuelle Assistentin für Finanzbildung mit KI",
        "intro": "INNA hilft Menschen, Einkommen, Ausgaben, Schulden, Rücklagen und nächste Schritte einfach, lehrreich und personalisiert zu verstehen.",
        "what_title": "Was ist INNA?",
        "what_text": "INNA Financial Coach AI ist eine intelligente Finanzpädagogin, die grundlegende Benutzerdaten in eine klare Sicht auf die aktuelle finanzielle Situation verwandelt.",
        "features_title": "Hauptfunktionen",
        "how_title": "So funktioniert es",
        "quick_title": "Schnellübersicht der Diagnose",
        "feature_1_title": "📋 Finanzdiagnose",
        "feature_1_text": "Analysiert Einkommen, Ausgaben, Schulden und Rücklagen, um eine klare Sicht auf die aktuelle Situation zu erzeugen.",
        "feature_2_title": "🧠 Generative KI",
        "feature_2_text": "Erstellt einfache Erklärungen und einen personalisierten Aktionsplan für die nächsten 30 Tage.",
        "feature_3_title": "📄 PDF-Bericht + E-Mail",
        "feature_3_text": "Ermöglicht das Herunterladen des Finanzberichts oder den direkten Erhalt der Diagnose per E-Mail.",
        "feature_4_title": "🌐 Multikanal und mehrsprachig",
        "feature_4_text": "Funktioniert über Web App, Telegram, API und Dashboard mit Unterstützung für verschiedene Sprachen und Währungen.",
        "step_1_title": "Ausfüllen",
        "step_1_text": "Einkommen, Ausgaben, Schulden und Rücklagen eingeben.",
        "step_2_title": "Analyse erhalten",
        "step_2_text": "INNA berechnet die wichtigsten Finanzindikatoren.",
        "step_3_title": "Plan ansehen",
        "step_3_text": "Die KI erstellt eine personalisierte Bildungsorientierung.",
        "step_4_title": "Herunterladen oder senden",
        "step_4_text": "Als PDF exportieren oder Bericht per E-Mail erhalten.",
        "income": "Monatliches Einkommen",
        "expenses": "Fixkosten",
        "debts": "Schulden",
        "reserve": "Rücklage",
        "warning": "Wichtiger Hinweis: INNA ist ein Bildungstool. Sie ersetzt keine professionelle Finanz-, Steuer-, Rechts- oder Bankberatung.",
        "cta_title": "Starte jetzt deine Finanzdiagnose",
        "cta_text": "Organisiere dein Finanzleben mit einer intelligenten, einfachen und personalisierten virtuellen Assistentin.",
        "btn_start": "🧾 Neue Diagnose starten",
        "btn_report": "📄 Bericht erstellen",
        "btn_about": "ℹ️ Projekt ansehen",
    },
}

HOME_TEXTS_INNA["en_gb"] = HOME_TEXTS_INNA["en_us"].copy()

def home_t(key: str) -> str:
    lang = app_lang if app_lang in HOME_TEXTS_INNA else "pt"
    return HOME_TEXTS_INNA.get(lang, HOME_TEXTS_INNA["pt"]).get(
        key,
        HOME_TEXTS_INNA["pt"].get(key, key),
    )


# ==========================================
# TEXTOS SEGUROS DA TELA DE LOGIN
# Fica antes de tela_login_inna_inline para evitar NameError
# ==========================================
LOGIN_TEXTS_SAFE_INNA = {
    "pt": {
        "title": "🔑 Entrar na INNA",
        "caption": "Acesse sua conta para usar diagnóstico, relatório, histórico e recursos personalizados.",
        "brand": "💰 Inna",
        "subtitle": "Educadora Financeira Inteligente",
        "email": "E-mail",
        "password": "Senha",
        "button": "🔑 Entrar",
        "success_user": "Login realizado com sucesso.",
        "success_admin": "Login administrativo realizado com sucesso.",
        "error": "E-mail ou senha inválidos.",
    },
    "en_us": {
        "title": "🔑 Sign in to INNA",
        "caption": "Access your account to use diagnosis, reports, history and personalized resources.",
        "brand": "💰 Inna",
        "subtitle": "Intelligent Financial Educator",
        "email": "Email",
        "password": "Password",
        "button": "🔑 Sign in",
        "success_user": "Signed in successfully.",
        "success_admin": "Admin signed in successfully.",
        "error": "Invalid email or password.",
    },
    "en_gb": {
        "title": "🔑 Sign in to INNA",
        "caption": "Access your account to use diagnosis, reports, history and personalised resources.",
        "brand": "💰 Inna",
        "subtitle": "Intelligent Financial Educator",
        "email": "Email",
        "password": "Password",
        "button": "🔑 Sign in",
        "success_user": "Signed in successfully.",
        "success_admin": "Admin signed in successfully.",
        "error": "Invalid email or password.",
    },
    "es": {
        "title": "🔑 Entrar en INNA",
        "caption": "Accede a tu cuenta para usar diagnóstico, informes, historial y recursos personalizados.",
        "brand": "💰 Inna",
        "subtitle": "Educadora Financiera Inteligente",
        "email": "E-mail",
        "password": "Contraseña",
        "button": "🔑 Entrar",
        "success_user": "Inicio de sesión realizado con éxito.",
        "success_admin": "Inicio administrativo realizado con éxito.",
        "error": "E-mail o contraseña inválidos.",
    },
    "fr": {
        "title": "🔑 Connexion à INNA",
        "caption": "Accédez à votre compte pour utiliser le diagnostic, les rapports, l’historique et les ressources personnalisées.",
        "brand": "💰 Inna",
        "subtitle": "Éducatrice financière intelligente",
        "email": "E-mail",
        "password": "Mot de passe",
        "button": "🔑 Se connecter",
        "success_user": "Connexion réussie.",
        "success_admin": "Connexion administrateur réussie.",
        "error": "E-mail ou mot de passe invalide.",
    },
    "de": {
        "title": "🔑 Bei INNA anmelden",
        "caption": "Melden Sie sich an, um Diagnose, Berichte, Verlauf und personalisierte Ressourcen zu nutzen.",
        "brand": "💰 Inna",
        "subtitle": "Intelligente Finanzpädagogin",
        "email": "E-mail",
        "password": "Passwort",
        "button": "🔑 Anmelden",
        "success_user": "Anmeldung erfolgreich.",
        "success_admin": "Admin-Anmeldung erfolgreich.",
        "error": "Ungültige E-mail oder ungültiges Passwort.",
    },
    "it": {
        "title": "🔑 Accedi a INNA",
        "caption": "Accedi al tuo account per usare diagnosi, report, cronologia e risorse personalizzate.",
        "brand": "💰 Inna",
        "subtitle": "Educatrice finanziaria intelligente",
        "email": "E-mail",
        "password": "Password",
        "button": "🔑 Accedi",
        "success_user": "Accesso effettuato con successo.",
        "success_admin": "Accesso amministrativo effettuato con successo.",
        "error": "E-mail o password non validi.",
    },
    "ro": {
        "title": "🔑 Intră în INNA",
        "caption": "Accesează contul pentru diagnostic, rapoarte, istoric și resurse personalizate.",
        "brand": "💰 Inna",
        "subtitle": "Educatoare financiară inteligentă",
        "email": "E-mail",
        "password": "Parolă",
        "button": "🔑 Intră",
        "success_user": "Autentificare reușită.",
        "success_admin": "Autentificare administrativă reușită.",
        "error": "E-mail sau parolă invalidă.",
    },
    "uk": {
        "title": "🔑 Увійти в INNA",
        "caption": "Увійдіть, щоб використовувати діагностику, звіти, історію та персоналізовані ресурси.",
        "brand": "💰 Inna",
        "subtitle": "Інтелектуальна фінансова освітня асистентка",
        "email": "E-mail",
        "password": "Пароль",
        "button": "🔑 Увійти",
        "success_user": "Вхід виконано успішно.",
        "success_admin": "Адміністративний вхід виконано успішно.",
        "error": "Невірний e-mail або пароль.",
    },
    "ru": {
        "title": "🔑 Войти в INNA",
        "caption": "Войдите в аккаунт, чтобы использовать диагностику, отчёты, историю и персонализированные ресурсы.",
        "brand": "💰 Inna",
        "subtitle": "Интеллектуальный финансовый образовательный ассистент",
        "email": "E-mail",
        "password": "Пароль",
        "button": "🔑 Войти",
        "success_user": "Вход выполнен успешно.",
        "success_admin": "Административный вход выполнен успешно.",
        "error": "Неверный e-mail или пароль.",
    },
    "ar": {
        "title": "🔑 تسجيل الدخول إلى INNA",
        "caption": "ادخل إلى حسابك لاستخدام التشخيص والتقارير والسجل والموارد الشخصية.",
        "brand": "💰 Inna",
        "subtitle": "مساعدة تعليم مالي ذكية",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "button": "🔑 تسجيل الدخول",
        "success_user": "تم تسجيل الدخول بنجاح.",
        "success_admin": "تم تسجيل دخول المسؤول بنجاح.",
        "error": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
    },
    "ch": {
        "title": "🔑 Bei INNA anmelden",
        "caption": "Melden Sie sich an, um Diagnose, Berichte, Verlauf und personalisierte Ressourcen zu nutzen.",
        "brand": "💰 Inna",
        "subtitle": "Intelligente Finanzpädagogin",
        "email": "E-mail",
        "password": "Passwort",
        "button": "🔑 Anmelden",
        "success_user": "Anmeldung erfolgreich.",
        "success_admin": "Admin-Anmeldung erfolgreich.",
        "error": "Ungültige E-mail oder ungültiges Passwort.",
    },
}

def login_t(key: str) -> str:
    lang = st.session_state.get("app_lang", app_lang)
    return LOGIN_TEXTS_SAFE_INNA.get(lang, LOGIN_TEXTS_SAFE_INNA["pt"]).get(
        key,
        LOGIN_TEXTS_SAFE_INNA["pt"].get(key, key),
    )


def tela_login_inna_inline(destino_apos_login="📊 Panorama"):
    st.warning(login_t("caption"))

    col_login1, col_login2, col_login3 = st.columns([1, 1.2, 1])

    with col_login2:
        st.markdown(f"### {login_t('title')}")
        st.caption(login_t("caption"))

        email_login = st.text_input(login_t("email"), key=f"login_email_inline_{destino_apos_login}")
        senha_login = st.text_input(login_t("password"), type="password", key=f"login_senha_inline_{destino_apos_login}")

        with st.expander(login_t("demo")):
            st.info(
                f"Usuário comum: {INNA_USER_EMAIL} | Senha: {INNA_USER_PASSWORD}\n\n"
                f"Administrador: {INNA_ADMIN_EMAIL} | Senha: {INNA_ADMIN_PASSWORD}"
            )

        if st.button(login_t("button"), use_container_width=True, key=f"btn_login_inline_{destino_apos_login}"):
            if email_login == INNA_USER_EMAIL and senha_login == INNA_USER_PASSWORD:
                st.session_state.logado = True
                st.session_state.show_login_page = False
                st.session_state.usuario = email_login
                st.session_state.perfil_usuario = "usuario"
                st.session_state.app_menu_selected = destino_apos_login
                st.success(login_t("success_user"))
                st.rerun()

            elif email_login == INNA_ADMIN_EMAIL and senha_login == INNA_ADMIN_PASSWORD:
                st.session_state.logado = True
                st.session_state.show_login_page = False
                st.session_state.usuario = email_login
                st.session_state.perfil_usuario = "admin"
                st.session_state.app_menu_selected = destino_apos_login
                st.success(login_t("success_admin"))
                st.rerun()

            else:
                st.error(login_t("error"))
PAGINAS_PUBLICAS_INNA = ["🏠 Início", "🔑 Entrar", "ℹ️ Sobre"]


# Abre a tela de login quando o botão Entrar do topo for clicado
if st.session_state.get("show_login_page") and not st.session_state.get("logado"):
    tela_login_inna_inline(destino_apos_login="📊 Panorama")
    st.stop()




if not st.session_state.get("logado") and app_menu not in PAGINAS_PUBLICAS_INNA:
    tela_login_inna_inline(destino_apos_login=app_menu)
    st.stop()

# =============================
# AJUSTE VISUAL DOS CONTAINERS/CARDS
# =============================

st.markdown(f"""
<style>

/* Remove aparência cinza fraca dos containers com borda */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {theme["card_bg"]} !important;
    border: 1px solid rgba(212, 175, 55, 0.32) !important;
    border-radius: 22px !important;
    box-shadow: 0 14px 34px rgba(7, 28, 54, 0.12) !important;
    padding: 18px !important;
}}

/* Texto dentro dos containers */
div[data-testid="stVerticalBlockBorderWrapper"] h1,
div[data-testid="stVerticalBlockBorderWrapper"] h2,
div[data-testid="stVerticalBlockBorderWrapper"] h3,
div[data-testid="stVerticalBlockBorderWrapper"] p,
div[data-testid="stVerticalBlockBorderWrapper"] span {{
    color: {theme["card_text"]} !important;
}}

/* Cards menores dentro do hero */
div[data-testid="stVerticalBlockBorderWrapper"] p {{
    color: {theme["hero_subtext"]} !important;
    line-height: 1.6 !important;
}}

/* Título Inna */
div[data-testid="stVerticalBlockBorderWrapper"] h1 {{
    color: {theme["hero_text"]} !important;
    font-size: 56px !important;
    font-weight: 950 !important;
    letter-spacing: -1px !important;
}}

/* Financial Coach AI */
div[data-testid="stVerticalBlockBorderWrapper"] h2 {{
    color: {theme["hero_text"]} !important;
    font-size: 32px !important;
    font-weight: 850 !important;
}}

/* Subtítulo */
div[data-testid="stVerticalBlockBorderWrapper"] h3 {{
    color: {theme["accent"]} !important;
    font-weight: 800 !important;
}}

</style>
""", unsafe_allow_html=True)

# =============================
# MENU SUPERIOR / SIDEBAR OCULTA
# =============================

st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 1500px !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-top: 1.2rem !important;
}

.inna-top-title {
    font-size: 28px;
    font-weight: 900;
    color: #071C36;
    margin-bottom: 4px;
}

.inna-top-subtitle {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 10px;
}

.inna-top-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 12px 0 18px 0;
}

div[data-testid="stHorizontalBlock"] button {
    min-height: 40px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# AJUSTE FINAL DO CTA DA LANDING PAGE
# =============================

st.markdown(f"""
<style>

/* CTA final da landing page */
.cta-box {{
    background: {theme["hero_bg"]} !important;
    border: 1px solid {theme["accent"]} !important;
    border-radius: 26px !important;
    padding: 42px 30px !important;
    text-align: center !important;
    box-shadow: 0 20px 50px rgba(7, 28, 54, 0.18) !important;
    margin-top: 32px !important;
}}

/* Título do CTA */
.cta-box h2 {{
    color: {theme["hero_text"]} !important;
    font-size: 34px !important;
    font-weight: 950 !important;
    margin-bottom: 14px !important;
}}

/* Texto do CTA */
.cta-box p {{
    color: {theme["hero_subtext"]} !important;
    font-size: 17px !important;
    font-weight: 500 !important;
}}

/* Ajuste específico para Branco brilhante */
body:not(.dark) .cta-box {{
    background: linear-gradient(135deg, #FFFFFF 0%, #EEF6FF 100%) !important;
}}

/* Botões finais */
.stButton > button {{
    min-height: 44px !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
}}

</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>

/* ===== TOPO / TÍTULO ===== */
.inna-top-title {{
    font-size: 28px !important;
    font-weight: 900 !important;
    color: {theme["hero_text"]} !important;
    margin-bottom: 6px !important;
}}

.inna-top-subtitle {{
    font-size: 14px !important;
    color: {theme["hero_subtext"]} !important;
    margin-bottom: 10px !important;
}}

.inna-top-divider {{
    height: 1px !important;
    background: linear-gradient(90deg, transparent, {theme["accent"]}, transparent) !important;
    margin: 12px 0 18px 0 !important;
}}

/* ===== MENU SUPERIOR ===== */
div[data-testid="stHorizontalBlock"] .stButton > button {{
    min-height: 58px !important;
    border-radius: 18px !important;
    border: 1px solid {theme["border"]} !important;
    background: {theme["surface"]} !important;
    color: {theme["text"]} !important;
    font-weight: 700 !important;
    font-size: 0.98rem !important;
    padding: 0.55rem 0.75rem !important;
    white-space: nowrap !important;
    line-height: 1.15 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    text-align: center !important;
}}

div[data-testid="stHorizontalBlock"] .stButton > button p {{
    white-space: nowrap !important;
    margin: 0 !important;
    line-height: 1.15 !important;
}}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
    border: 1px solid {theme["accent"]} !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.12) !important;
}}

/* ===== CONTAINERS / CARDS ===== */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {theme["card_bg"]} !important;
    border: 1px solid rgba(212, 175, 55, 0.35) !important;
    border-radius: 20px !important;
    box-shadow: 0 12px 30px rgba(0,0,0,0.10) !important;
    padding: 16px !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] h1,
div[data-testid="stVerticalBlockBorderWrapper"] h2,
div[data-testid="stVerticalBlockBorderWrapper"] h3,
div[data-testid="stVerticalBlockBorderWrapper"] h4,
div[data-testid="stVerticalBlockBorderWrapper"] strong {{
    color: {theme["hero_text"]} !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] p,
div[data-testid="stVerticalBlockBorderWrapper"] span,
div[data-testid="stVerticalBlockBorderWrapper"] li {{
    color: {theme["hero_subtext"]} !important;
}}

/* ===== MÉTRICAS ===== */
div[data-testid="metric-container"] {{
    background: {theme["card_bg"]} !important;
    border: 1px solid {theme["border"]} !important;
    border-radius: 16px !important;
    padding: 12px !important;
}}

/* ===== CTA FINAL ===== */
.cta-box {{
    background: {theme["hero_bg"]} !important;
    border: 1px solid {theme["accent"]} !important;
    border-radius: 24px !important;
    padding: 34px 26px !important;
    text-align: center !important;
    box-shadow: 0 18px 40px rgba(0,0,0,0.18) !important;
    margin-top: 28px !important;
}}

.cta-box h2 {{
    color: {theme["hero_text"]} !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    margin-bottom: 10px !important;
}}

.cta-box p {{
    color: {theme["hero_subtext"]} !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    margin-bottom: 0 !important;
}}

/* ===== BOTÕES FINAIS ===== */
.stButton > button {{
    border-radius: 14px !important;
    font-weight: 800 !important;
}}

</style>
""", unsafe_allow_html=True)

# ==========================================
# AJUSTE FINAL DA LANDING PAGE
# warning + cta + ações finais
# ==========================================
st.markdown(f"""
<style>

/* ===== AVISO IMPORTANTE ===== */
.warning-box {{
    background: {theme["card_bg"]} !important;
    border: 1px solid {theme["accent"]} !important;
    border-radius: 20px !important;
    padding: 18px 20px !important;
    margin-top: 18px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.10) !important;
    color: {theme["text"]} !important;
}}

.warning-box strong {{
    color: {theme["accent"]} !important;
    font-weight: 900 !important;
}}

.warning-box,
.warning-box p,
.warning-box span {{
    color: {theme["text"]} !important;
    font-size: 15px !important;
    line-height: 1.55 !important;
}}

/* ===== CTA FINAL ===== */
.cta-box {{
    background: {theme["card_bg"]} !important;
    border: 1px solid {theme["accent"]} !important;
    border-radius: 24px !important;
    padding: 36px 26px !important;
    margin-top: 22px !important;
    margin-bottom: 18px !important;
    text-align: center !important;
    box-shadow: 0 14px 32px rgba(0,0,0,0.14) !important;
}}

.cta-box h2 {{
    color: {theme["hero_text"]} !important;
    font-size: 34px !important;
    font-weight: 950 !important;
    margin: 0 0 12px 0 !important;
    line-height: 1.2 !important;
}}

.cta-box p {{
    color: {theme["hero_subtext"]} !important;
    font-size: 17px !important;
    font-weight: 500 !important;
    margin: 0 !important;
    line-height: 1.55 !important;
}}

/* ===== CONTAINERS DOS BOTÕES FINAIS ===== */
.final-action-wrap {{
    background: {theme["card_bg"]} !important;
    border: 1px solid rgba(212, 175, 55, 0.35) !important;
    border-radius: 20px !important;
    padding: 14px !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.08) !important;
    margin-top: 6px !important;
}}

.final-action-wrap .stButton > button {{
    width: 100% !important;
    min-height: 56px !important;
    border-radius: 16px !important;
    border: 1px solid {theme["border"]} !important;
    background: {theme["surface"]} !important;
    color: {theme["text"]} !important;
    font-weight: 800 !important;
    font-size: 16px !important;
}}

.final-action-wrap .stButton > button:hover {{
    border: 1px solid {theme["accent"]} !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.10) !important;
}}

/* ===== PEQUENO REFORÇO DE CONTRASTE NOS TEMAS ESCUROS ===== */
section[data-testid="stSidebar"] + div .cta-box h2,
section[data-testid="stSidebar"] + div .warning-box strong {{
    opacity: 1 !important;
}}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CTA E AVISO FINAL - FUNDO ESCURO + BORDA DOURADA
# ==========================================
st.markdown("""
<style>

/* Aviso importante */
.warning-box {
    background: linear-gradient(135deg, #07192F 0%, #03101E 100%) !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 22px !important;
    padding: 18px 22px !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.18) !important;
}

.warning-box strong {
    color: #FFFFFF !important;
    font-weight: 900 !important;
}

.warning-box,
.warning-box p,
.warning-box span {
    color: #FFFFFF !important;
    font-size: 15px !important;
    line-height: 1.55 !important;
}

/* CTA final */
.cta-box {
    background: linear-gradient(135deg, #07192F 0%, #03101E 100%) !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 28px !important;
    padding: 42px 28px !important;
    margin-top: 24px !important;
    margin-bottom: 18px !important;
    text-align: center !important;
    box-shadow: 0 16px 36px rgba(0,0,0,0.22) !important;
}

.cta-box h2,
.cta-box .cta-title {
    color: #FFFFFF !important;
    font-size: 38px !important;
    font-weight: 950 !important;
    line-height: 1.2 !important;
    margin-bottom: 14px !important;
}

.cta-box p,
.cta-box .cta-subtitle {
    color: #D8E3F2 !important;
    font-size: 18px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}

/* Remove aparência apagada de headings dentro do CTA */
.cta-box a {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CTA FINAL DEFINITIVO - ESCURO + DOURADO
# ==========================================
st.markdown("""
<style>

/* Força o CTA final a NÃO ficar branco */
.cta-box {
    background: linear-gradient(135deg, #07192F 0%, #03101E 100%) !important;
    border: 1.5px solid #D4AF37 !important;
    border-radius: 28px !important;
    padding: 42px 28px !important;
    margin-top: 24px !important;
    margin-bottom: 18px !important;
    text-align: center !important;
    box-shadow: 0 18px 42px rgba(0,0,0,0.28) !important;
}

/* Título do CTA */
.cta-box h2,
.cta-box .cta-title {
    color: #FFFFFF !important;
    font-size: 38px !important;
    font-weight: 950 !important;
    line-height: 1.2 !important;
    margin-bottom: 14px !important;
    opacity: 1 !important;
}

/* Destaque dourado dentro do título */
.cta-box .cta-highlight {
    color: #F6D889 !important;
}

/* Subtítulo do CTA */
.cta-box p,
.cta-box .cta-subtitle {
    color: #D8E3F2 !important;
    font-size: 18px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    margin: 0 !important;
    opacity: 1 !important;
}

/* Remove ícone/link de heading do Streamlit caso apareça */
.cta-box a {
    display: none !important;
}

/* Aviso importante no mesmo padrão */
.warning-box {
    background: linear-gradient(135deg, #07192F 0%, #03101E 100%) !important;
    border: 1.5px solid #D4AF37 !important;
    border-radius: 22px !important;
    padding: 18px 22px !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.18) !important;
}

.warning-box strong {
    color: #F6D889 !important;
    font-weight: 900 !important;
}

.warning-box,
.warning-box p,
.warning-box span {
    color: #FFFFFF !important;
    font-size: 15px !important;
    line-height: 1.55 !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# PADRÃO FINAL: AVISO + CTA COMO CARD PREMIUM
# ==========================================
st.markdown("""
<style>

/* Aviso importante e CTA final no mesmo padrão */
.warning-box,
.cta-box {
    background: linear-gradient(135deg, #164A86 0%, #071C36 48%, #03101E 100%) !important;
    border: 1.5px solid #D4AF37 !important;
    border-radius: 30px !important;
    padding: 42px 32px !important;
    margin-top: 26px !important;
    margin-bottom: 22px !important;
    text-align: center !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.26) !important;
}

/* Texto do aviso */
.warning-box {
    color: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    line-height: 1.6 !important;
}

/* Destaque do aviso */
.warning-box strong {
    color: #F6D889 !important;
    font-weight: 950 !important;
}

/* Título do CTA */
.cta-box h2,
.cta-box .cta-title {
    color: #F6D889 !important;
    font-size: 40px !important;
    font-weight: 950 !important;
    line-height: 1.2 !important;
    margin-bottom: 26px !important;
    opacity: 1 !important;
}

/* Texto do CTA */
.cta-box p,
.cta-box .cta-subtitle {
    color: #FFFFFF !important;
    font-size: 21px !important;
    font-weight: 500 !important;
    line-height: 1.65 !important;
    margin: 0 !important;
    opacity: 1 !important;
}

/* Remove ícone/link de heading do Streamlit dentro do CTA */
.cta-box a,
.warning-box a {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# FORÇA FINAL DO CTA - CORREÇÃO DEFINITIVA
# ==========================================
st.markdown("""
<style>

/* CTA final definitivo */
.cta-box {
    background: linear-gradient(135deg, #164A86 0%, #071C36 45%, #03101E 100%) !important;
    border: 2px solid #D4AF37 !important;
    border-radius: 30px !important;
    padding: 46px 32px !important;
    margin-top: 28px !important;
    margin-bottom: 22px !important;
    text-align: center !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.28) !important;
}

/* Remove qualquer fundo claro dentro do CTA */
.cta-box * {
    background: transparent !important;
}

/* Título do CTA */
.cta-box h2,
.cta-box .cta-title,
.cta-box div.cta-title {
    color: #F6D889 !important;
    font-size: 40px !important;
    font-weight: 950 !important;
    line-height: 1.2 !important;
    margin-bottom: 22px !important;
    opacity: 1 !important;
}

/* Subtítulo do CTA */
.cta-box p,
.cta-box .cta-subtitle,
.cta-box div.cta-subtitle {
    color: #FFFFFF !important;
    font-size: 21px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    opacity: 1 !important;
}

/* Evita ícone de link do markdown */
.cta-box a {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CTA FINAL PREMIUM - CLASSE EXCLUSIVA
# ==========================================
st.markdown("""
<style>

.final-cta-premium {
    background: linear-gradient(135deg, #164A86 0%, #071C36 45%, #03101E 100%) !important;
    border: 2px solid #D4AF37 !important;
    border-radius: 30px !important;
    padding: 46px 32px !important;
    margin-top: 28px !important;
    margin-bottom: 22px !important;
    text-align: center !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.30) !important;
}

.final-cta-premium,
.final-cta-premium * {
    background-color: transparent !important;
}

.final-cta-title {
    color: #F6D889 !important;
    font-size: 40px !important;
    font-weight: 950 !important;
    line-height: 1.2 !important;
    margin-bottom: 22px !important;
    opacity: 1 !important;
}

.final-cta-subtitle {
    color: #FFFFFF !important;
    font-size: 21px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    opacity: 1 !important;
}

.final-cta-premium a {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# FINAL DA LANDING POR TEMA
# Aviso + CTA final separados por tema
# ==========================================

landing_theme_name = st.session_state.get("theme_name", "Escuro azul")

if landing_theme_name == "Branco brilhante":
    landing_warning_bg = "linear-gradient(135deg, #FFFFFF 0%, #F7FBFF 100%)"
    landing_warning_text = "#071C36"
    landing_warning_strong = "#071C36"
    landing_warning_border = "#D4AF37"

    landing_cta_bg = "linear-gradient(135deg, #FFFFFF 0%, #EEF6FF 100%)"
    landing_cta_title = "#071C36"
    landing_cta_subtitle = "#334155"
    landing_cta_border = "#D4AF37"

elif landing_theme_name in ["Escuro preto", "Preto dourado", "Preto vermelho"]:
    landing_warning_bg = "linear-gradient(135deg, #101010 0%, #050505 100%)"
    landing_warning_text = "#FFFFFF"
    landing_warning_strong = "#F6D889"
    landing_warning_border = "#D4AF37"

    landing_cta_bg = "linear-gradient(135deg, #141414 0%, #050505 100%)"
    landing_cta_title = "#F6D889"
    landing_cta_subtitle = "#FFFFFF"
    landing_cta_border = "#D4AF37"

else:
    landing_warning_bg = "linear-gradient(135deg, #164A86 0%, #071C36 48%, #03101E 100%)"
    landing_warning_text = "#FFFFFF"
    landing_warning_strong = "#F6D889"
    landing_warning_border = "#D4AF37"

    landing_cta_bg = "linear-gradient(135deg, #164A86 0%, #071C36 45%, #03101E 100%)"
    landing_cta_title = "#F6D889"
    landing_cta_subtitle = "#FFFFFF"
    landing_cta_border = "#D4AF37"


st.markdown(f"""
<style>

/* ===== AVISO IMPORTANTE POR TEMA ===== */
.warning-box {{
    background: {landing_warning_bg} !important;
    border: 2px solid {landing_warning_border} !important;
    border-radius: 24px !important;
    padding: 20px 24px !important;
    margin-top: 20px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 14px 34px rgba(0,0,0,0.16) !important;
    color: {landing_warning_text} !important;
    text-align: left !important;
}}

.warning-box,
.warning-box p,
.warning-box span,
.warning-box div {{
    color: {landing_warning_text} !important;
    background: transparent !important;
    opacity: 1 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}}

.warning-box strong {{
    color: {landing_warning_strong} !important;
    background: transparent !important;
    opacity: 1 !important;
    font-weight: 950 !important;
}}

/* ===== CTA FINAL POR TEMA ===== */
.final-cta-premium {{
    background: {landing_cta_bg} !important;
    border: 2px solid {landing_cta_border} !important;
    border-radius: 30px !important;
    padding: 46px 32px !important;
    margin-top: 28px !important;
    margin-bottom: 24px !important;
    text-align: center !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.24) !important;
}}

.final-cta-premium,
.final-cta-premium * {{
    background: transparent !important;
    background-color: transparent !important;
    opacity: 1 !important;
}}

.final-cta-title {{
    color: {landing_cta_title} !important;
    font-size: 40px !important;
    font-weight: 950 !important;
    line-height: 1.2 !important;
    margin-bottom: 18px !important;
}}

.final-cta-subtitle {{
    color: {landing_cta_subtitle} !important;
    font-size: 21px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}}

.final-cta-premium a,
.warning-box a {{
    display: none !important;
}}

</style>
""", unsafe_allow_html=True)

# ==========================================
# LANDING PAGE MAIS COMPACTA
# ==========================================
st.markdown("""
<style>

/* Área geral mais compacta */
.block-container {
    max-width: 1220px !important;
    padding-top: 0.4rem !important;
    padding-bottom: 1rem !important;
}

/* Reduz espaço vertical entre blocos do Streamlit */
div[data-testid="stVerticalBlock"] {
    gap: 0.75rem !important;
}

/* Reduz espaço entre colunas */
div[data-testid="stHorizontalBlock"] {
    gap: 0.9rem !important;
}

/* Topo mais enxuto */
.inna-top-title {
    margin-bottom: 0px !important;
    font-size: 24px !important;
}

.inna-top-subtitle {
    margin-bottom: 4px !important;
    font-size: 12px !important;
}

.inna-top-divider {
    margin: 8px 0 10px 0 !important;
}

/* Linha de idioma, tema e login mais compacta */
div[data-testid="stSelectbox"] {
    margin-bottom: 0px !important;
}

/* Menu superior menor */
.stButton > button {
    min-height: 38px !important;
    padding: 0.35rem 0.55rem !important;
    font-size: 0.9rem !important;
}

/* Badge mais próximo da imagem */
.premium-badge {
    margin-top: 4px !important;
    margin-bottom: 8px !important;
    padding: 7px 14px !important;
    font-size: 12px !important;
}

/* Imagem da Inna mais ajustada */
div[data-testid="stImage"] img {
    border-radius: 18px !important;
    max-height: 520px !important;
    object-fit: cover !important;
}

/* Cards do hero mais compactos */
div[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 12px !important;
    border-radius: 18px !important;
}

/* Títulos do hero menores */
div[data-testid="stVerticalBlockBorderWrapper"] h1 {
    font-size: 42px !important;
    margin-bottom: 0px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] h2 {
    font-size: 22px !important;
    margin-top: 0px !important;
    margin-bottom: 4px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] h3 {
    font-size: 18px !important;
    margin-bottom: 4px !important;
}

/* Texto dos cards mais compacto */
div[data-testid="stVerticalBlockBorderWrapper"] p {
    font-size: 13px !important;
    line-height: 1.35 !important;
    margin-bottom: 4px !important;
}

/* Info box menor */
.info-box {
    padding: 12px 16px !important;
    margin-top: 12px !important;
    margin-bottom: 16px !important;
}

/* Seções mais próximas */
.section-title,
h2, h3 {
    margin-top: 14px !important;
    margin-bottom: 8px !important;
}

/* Cards de recursos e passos menores */
.feature-card,
.step-card,
.metric-card {
    padding: 14px !important;
    min-height: auto !important;
    border-radius: 16px !important;
}

/* CTA e aviso menores */
.warning-box,
.final-cta-premium {
    margin-top: 16px !important;
    margin-bottom: 16px !important;
    padding: 28px 24px !important;
}

.final-cta-title {
    font-size: 32px !important;
    margin-bottom: 12px !important;
}

.final-cta-subtitle {
    font-size: 17px !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# REDUZIR ESPAÇO ENTRE MENU SUPERIOR E HERO
# ==========================================
st.markdown("""
<style>

/* Reduz espaço geral do topo */
.block-container {
    padding-top: 0.2rem !important;
}

/* Reduz espaços verticais internos do Streamlit */
div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

/* Reduz espaço depois do menu superior */
.inna-top-divider {
    margin: 6px 0 6px 0 !important;
}

/* Menu superior mais compacto */
div[data-testid="stHorizontalBlock"] {
    gap: 0.55rem !important;
}

/* Botões do menu com menos altura */
div[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 44px !important;
    padding: 0.35rem 0.55rem !important;
}

/* Badge mais perto do menu e da imagem */
.premium-badge {
    margin-top: 0px !important;
    margin-bottom: 6px !important;
}

/* Remove espaço vazio antes do hero da INNA */
.premium-badge + div {
    margin-top: 0px !important;
}

/* Reduz margem dos containers logo abaixo do menu */
div[data-testid="stVerticalBlock"] > div {
    margin-top: 0px !important;
}

/* Ajusta a área da imagem e card da Inna para subir */
div[data-testid="stImage"] {
    margin-top: 0px !important;
}

</style>
""", unsafe_allow_html=True)
if app_menu == "🏠 Início":

    # HERO PRINCIPAL DA INNA SEM HTML GRANDE
    # Foto à esquerda, textos/cards à direita, sem aparecer código na tela

    st.markdown(
        f'<div class="premium-badge">{home_t("badge")}</div>',
        unsafe_allow_html=True
    )

    hero_col_img, hero_col_text = st.columns([0.9, 1.25], vertical_alignment="center")

    with hero_col_img:
        if HERO_IMAGE.exists():
            st.image(str(HERO_IMAGE), use_container_width=True)
        else:
            st.warning("Imagem não encontrada em assets/inna_hero.png")

    with hero_col_text:
        with st.container(border=True):
            st.markdown("# Inna")
            st.markdown("## Financial Coach AI")
            st.markdown(f"### {home_t('subtitle')}")
            st.write(home_t("intro"))

            card_1, card_2 = st.columns(2)

            with card_1:
                with st.container(border=True):
                    st.markdown("### 📋 " + home_t("feature_1_title").replace("📋 ", ""))
                    st.write(home_t("feature_1_text"))

                with st.container(border=True):
                    st.markdown("### 📄 " + home_t("feature_3_title").replace("📄 ", ""))
                    st.write(home_t("feature_3_text"))

            with card_2:
                with st.container(border=True):
                    st.markdown("### 🧠 " + home_t("feature_2_title").replace("🧠 ", ""))
                    st.write(home_t("feature_2_text"))

                with st.container(border=True):
                    st.markdown("### 🌐 " + home_t("feature_4_title").replace("🌐 ", ""))
                    st.write(home_t("feature_4_text"))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
        {home_t("intro")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{home_t("what_title")}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="text-normal">
        {home_t("what_text")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{home_t("features_title")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{home_t("feature_1_title")}</h3>
            <p>{home_t("feature_1_text")}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="feature-card">
            <h3>{home_t("feature_3_title")}</h3>
            <p>{home_t("feature_3_text")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{home_t("feature_2_title")}</h3>
            <p>{home_t("feature_2_text")}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="feature-card">
            <h3>{home_t("feature_4_title")}</h3>
            <p>{home_t("feature_4_text")}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{home_t("how_title")}</div>', unsafe_allow_html=True)

    col_step1, col_step2, col_step3, col_step4 = st.columns(4)

    with col_step1:
        st.markdown(f"""
        <div class="step-card">
            <h3>1</h3>
            <h4>{home_t("step_1_title")}</h4>
            <p>{home_t("step_1_text")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_step2:
        st.markdown(f"""
        <div class="step-card">
            <h3>2</h3>
            <h4>{home_t("step_2_title")}</h4>
            <p>{home_t("step_2_text")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_step3:
        st.markdown(f"""
        <div class="step-card">
            <h3>3</h3>
            <h4>{home_t("step_3_title")}</h4>
            <p>{home_t("step_3_text")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_step4:
        st.markdown(f"""
        <div class="step-card">
            <h3>4</h3>
            <h4>{home_t("step_4_title")}</h4>
            <p>{home_t("step_4_text")}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{home_t("quick_title")}</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            home_t("income"),
            format_currency_app(3500, current_currency_info["simbolo"], current_currency_info["moeda"]),
            "+12%"
        )
    with m2:
        st.metric(
            home_t("expenses"),
            format_currency_app(2150, current_currency_info["simbolo"], current_currency_info["moeda"]),
            "-5%"
        )
    with m3:
        st.metric(
            home_t("debts"),
            format_currency_app(780, current_currency_info["simbolo"], current_currency_info["moeda"]),
            "-10%"
        )
    with m4:
        st.metric(
            home_t("reserve"),
            format_currency_app(1200, current_currency_info["simbolo"], current_currency_info["moeda"]),
            "+18%"
        )

    st.markdown(f"""
    <div class="warning-box">
        <strong>{home_t("warning")}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="final-cta-premium">
        <div class="final-cta-title">{home_t("cta_title")}</div>
        <div class="final-cta-subtitle">{home_t("cta_text")}</div>
    </div>
    """, unsafe_allow_html=True)

    col_start1, col_start2, col_start3 = st.columns(3)

    if col_start1.button(home_t("btn_start"), use_container_width=True):
        st.session_state.app_menu_selected = "🧾 Diagnóstico" if st.session_state.get("logado") else "🔑 Entrar"
        st.rerun()

    if col_start2.button(home_t("btn_report"), use_container_width=True):
        st.session_state.app_menu_selected = "📄 Relatório" if st.session_state.get("logado") else "🔑 Entrar"
        st.rerun()

    if col_start3.button(home_t("btn_about"), use_container_width=True):
        st.session_state.app_menu_selected = "ℹ️ Sobre"
        st.rerun()

    st.stop()



CHAT_TEXTS_INNA = {
    "pt": {
        "title": "💬 Conversar",
        "caption": "Canal de conversa educativa para dúvidas financeiras simples.",
        "info": "Chat educativo conectado ao RAG local da INNA. As respostas usam a base de conhecimento financeira e exibem fontes quando disponíveis.",
        "input_label": "Digite uma pergunta ou anotação financeira:",
        "placeholder": "Exemplo: Ganho 3000, gasto 2500 e consigo guardar 100",
        "button": "Enviar pergunta para a Inna",
        "empty": "Digite uma pergunta antes de enviar.",
        "demo_answer": "Ainda estou em modo demonstração. Em breve, vou responder usando IA e o contexto do seu diagnóstico financeiro.",
    },
    "en_us": {
        "title": "💬 Chat with Inna",
        "caption": "Educational conversation channel for simple financial questions.",
        "info": "This is where the INNA chat will be. The next step is to connect this screen to AI so it can answer questions based on the user's latest financial diagnosis.",
        "input_label": "Type a financial question:",
        "placeholder": "Example: How can I improve my financial score?",
        "button": "Send question to Inna",
        "empty": "Type a question before sending.",
        "demo_answer": "I am still in demo mode. Soon, I will answer using AI and the context of your financial diagnosis.",
    },
    "en_gb": {
        "title": "💬 Chat with Inna",
        "caption": "Educational conversation channel for simple financial questions.",
        "info": "This is where the INNA chat will be. The next step is to connect this screen to AI so it can answer questions based on the user's latest financial diagnosis.",
        "input_label": "Type a financial question:",
        "placeholder": "Example: How can I improve my financial score?",
        "button": "Send question to Inna",
        "empty": "Type a question before sending.",
        "demo_answer": "I am still in demo mode. Soon, I will answer using AI and the context of your financial diagnosis.",
    },
    "es": {
        "title": "💬 Conversar con Inna",
        "caption": "Canal educativo para dudas financieras simples.",
        "info": "Aquí estará el chat de INNA. El próximo paso es conectar esta pantalla a la IA para responder preguntas con base en el último diagnóstico financiero del usuario.",
        "input_label": "Escribe una duda financiera:",
        "placeholder": "Ejemplo: ¿Cómo puedo mejorar mi puntuación financiera?",
        "button": "Enviar pregunta a Inna",
        "empty": "Escribe una pregunta antes de enviar.",
        "demo_answer": "Todavía estoy en modo demostración. Pronto responderé usando IA y el contexto de tu diagnóstico financiero.",
    },
    "de": {
        "title": "💬 Mit Inna sprechen",
        "caption": "Bildungskanal für einfache Finanzfragen.",
        "info": "Hier wird der INNA-Chat angezeigt. Der nächste Schritt ist, diese Seite mit KI zu verbinden, um Fragen auf Basis der letzten Finanzdiagnose des Nutzers zu beantworten.",
        "input_label": "Geben Sie eine Finanzfrage ein:",
        "placeholder": "Beispiel: Wie kann ich meinen Finanzscore verbessern?",
        "button": "Frage an Inna senden",
        "empty": "Geben Sie vor dem Senden eine Frage ein.",
        "demo_answer": "Ich bin noch im Demonstrationsmodus. Bald werde ich mit KI und dem Kontext Ihrer Finanzdiagnose antworten.",
    },
    "fr": {
        "title": "💬 Parler avec Inna",
        "caption": "Canal éducatif pour les questions financières simples.",
        "info": "C’est ici que le chat INNA sera affiché. La prochaine étape consiste à connecter cette page à l’IA pour répondre aux questions à partir du dernier diagnostic financier de l’utilisateur.",
        "input_label": "Écrivez une question financière :",
        "placeholder": "Exemple : Comment améliorer mon score financier ?",
        "button": "Envoyer la question à Inna",
        "empty": "Écrivez une question avant d’envoyer.",
        "demo_answer": "Je suis encore en mode démonstration. Bientôt, je répondrai avec l’IA et le contexte de votre diagnostic financier.",
    },
    "it": {
        "title": "💬 Parlare con Inna",
        "caption": "Canale educativo per semplici domande finanziarie.",
        "info": "Qui sarà disponibile la chat di INNA. Il prossimo passo è collegare questa schermata all’IA per rispondere alle domande in base all’ultima diagnosi finanziaria dell’utente.",
        "input_label": "Scrivi una domanda finanziaria:",
        "placeholder": "Esempio: Come posso migliorare il mio punteggio finanziario?",
        "button": "Invia domanda a Inna",
        "empty": "Scrivi una domanda prima di inviare.",
        "demo_answer": "Sono ancora in modalità dimostrativa. Presto risponderò usando l’IA e il contesto della tua diagnosi finanziaria.",
    },
    "ro": {
        "title": "💬 Vorbește cu Inna",
        "caption": "Canal educativ pentru întrebări financiare simple.",
        "info": "Aici va fi chatul INNA. Următorul pas este conectarea acestei pagini la IA pentru a răspunde la întrebări pe baza ultimului diagnostic financiar al utilizatorului.",
        "input_label": "Scrie o întrebare financiară:",
        "placeholder": "Exemplu: Cum îmi pot îmbunătăți scorul financiar?",
        "button": "Trimite întrebarea către Inna",
        "empty": "Scrie o întrebare înainte de trimitere.",
        "demo_answer": "Sunt încă în modul demonstrație. În curând voi răspunde folosind IA și contextul diagnosticului tău financiar.",
    },
    "ru": {
        "title": "💬 Поговорить с Inna",
        "caption": "Образовательный канал для простых финансовых вопросов.",
        "info": "Здесь будет чат INNA. Следующий шаг — подключить эту страницу к ИИ, чтобы отвечать на вопросы на основе последней финансовой диагностики пользователя.",
        "input_label": "Введите финансовый вопрос:",
        "placeholder": "Пример: Как я могу улучшить свой финансовый рейтинг?",
        "button": "Отправить вопрос Inna",
        "empty": "Введите вопрос перед отправкой.",
        "demo_answer": "Я пока работаю в демонстрационном режиме. Скоро я смогу отвечать с помощью ИИ и контекста вашей финансовой диагностики.",
    },
    "uk": {
        "title": "💬 Поговорити з Inna",
        "caption": "Освітній канал для простих фінансових питань.",
        "info": "Тут буде чат INNA. Наступний крок — підключити цю сторінку до ШІ, щоб відповідати на питання на основі останньої фінансової діагностики користувача.",
        "input_label": "Введіть фінансове питання:",
        "placeholder": "Приклад: Як я можу покращити свій фінансовий рейтинг?",
        "button": "Надіслати питання Inna",
        "empty": "Введіть питання перед надсиланням.",
        "demo_answer": "Я ще працюю в демонстраційному режимі. Незабаром я відповідатиму за допомогою ШІ та контексту вашої фінансової діагностики.",
    },
    "ar": {
        "title": "💬 التحدث مع Inna",
        "caption": "قناة تعليمية للأسئلة المالية البسيطة.",
        "info": "هنا ستكون محادثة INNA. الخطوة التالية هي ربط هذه الشاشة بالذكاء الاصطناعي للإجابة على الأسئلة بناءً على آخر تشخيص مالي للمستخدم.",
        "input_label": "اكتب سؤالًا ماليًا:",
        "placeholder": "مثال: كيف يمكنني تحسين درجتي المالية؟",
        "button": "إرسال السؤال إلى Inna",
        "empty": "اكتب سؤالًا قبل الإرسال.",
        "demo_answer": "ما زلت في وضع العرض التجريبي. قريبًا سأجيب باستخدام الذكاء الاصطناعي وسياق تشخيصك المالي.",
    },
    "ch": {
        "title": "💬 Mit Inna sprechen",
        "caption": "Bildungskanal für einfache Finanzfragen.",
        "info": "Hier wird der INNA-Chat angezeigt. Der nächste Schritt ist, diese Seite mit KI zu verbinden, um Fragen auf Basis der letzten Finanzdiagnose des Nutzers zu beantworten.",
        "input_label": "Geben Sie eine Finanzfrage ein:",
        "placeholder": "Beispiel: Wie kann ich meinen Finanzscore verbessern?",
        "button": "Frage an Inna senden",
        "empty": "Geben Sie vor dem Senden eine Frage ein.",
        "demo_answer": "Ich bin noch im Demonstrationsmodus. Bald werde ich mit KI und dem Kontext Ihrer Finanzdiagnose antworten.",
    },
}


def formatar_mensagem_chat_inna(texto: str) -> str:
    texto = str(texto or "")

    # Remove aviso repetido no chat
    texto = texto.replace(
        "Essa orientação é educativa e não substitui consultoria financeira profissional.",
        ""
    )

    # Linguagem mais simples e orientativa
    texto = texto.replace(
        "A INNA sugere este caminho para melhorar sua reserva financeira:",
        "Vamos por partes. Vou te orientar de um jeito simples:"
    )

    texto = texto.replace(
        "Vamos por partes. O melhor caminho para melhorar sua reserva é:",
        "Vamos por partes. Vou te orientar de um jeito simples:"
    )

    texto = texto.replace(
        "Melhor caminho para melhorar sua reserva financeira:",
        "Vou te mostrar um caminho simples para começar:"
    )

    texto = texto.replace(
        "Quer que eu te mostre o melhor caminho agora?",
        "<div class='inna-pergunta-proximo-passo'>Quer que eu monte uma meta simples para esta semana?</div>"
    )

    texto = texto.replace(
        "Quer que eu monte uma meta simples para esta semana?",
        "<div class='inna-pergunta-proximo-passo'>Quer que eu monte uma meta simples para esta semana?</div>"
    )

    # Corrige R$ para o Streamlit/Markdown não interpretar o símbolo $
    texto = texto.replace("R$", "R&#36;")
    texto = texto.replace(r"R\$", "R&#36;")

    return f"<div class='inna-chat-texto-simples'>{texto}</div>"


def chat_t(key: str) -> str:
    lang = app_lang if app_lang in CHAT_TEXTS_INNA else "pt"
    return CHAT_TEXTS_INNA.get(lang, CHAT_TEXTS_INNA["pt"]).get(
        key,
        CHAT_TEXTS_INNA["pt"].get(key, key),
    )
if app_menu == "💬 Conversar":
    st.title(chat_t("title"))
    st.caption(chat_t("caption"))

    st.info("Chat educativo conectado ao RAG local da INNA. Faça uma pergunta e continue conversando na mesma página.")

    if "inna_chat_history" not in st.session_state:
        st.session_state.inna_chat_history = [
            {
                "role": "assistant",
                "content": "Olá! Sou a Inna, sua educadora financeira inteligente. Como posso ajudar?",
                "source": None,
            }
        ]

    if st.button("🧹 Limpar conversa", use_container_width=True):
        st.session_state.inna_chat_history = [
            {
                "role": "assistant",
                "content": "Olá! Sou a Inna, sua educadora financeira inteligente. Como posso ajudar?",
                "source": None,
            }
        ]
        st.rerun()

    st.write("### 💡 Perguntas rápidas")
    st.caption("Escolha uma pergunta para começar a conversa com a INNA de forma mais fácil.")

    quick_questions = [
        "Como melhorar minha reserva?",
        "Como reduzir minhas dívidas?",
        "Como organizar meus gastos?",
        "Como sair das dívidas?",
        "Como criar um plano de 30 dias?",
    ]

    quick_cols = st.columns(2)

    for index_question, question in enumerate(quick_questions):
        with quick_cols[index_question % 2]:
            if st.button(question, use_container_width=True, key=f"quick_question_{index_question}"):
                st.session_state.quick_chat_question_inna = question
                st.rerun()

    st.divider()

    for message in st.session_state.inna_chat_history:
        with st.chat_message(message["role"]):
            if message.get("source"):
                st.markdown(
                    f"<div class='fonte-inna-top'>{message['source']}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(formatar_mensagem_chat_inna(message["content"]), unsafe_allow_html=True)

    pergunta_rapida_pendente = st.session_state.pop("quick_chat_question_inna", "")

    if st.session_state.pop("limpar_chat_input_inna", False):
        st.session_state["chat_question_input_inna"] = ""

    ultima_msg_inna = ""
    for msg in reversed(st.session_state.inna_chat_history):
        if msg.get("role") == "assistant":
            ultima_msg_inna = msg.get("content", "")
            break

    if "Quer que eu" in ultima_msg_inna:
        col_sim, col_nao, col_cancelar = st.columns(3)

        with col_sim:
            if st.button("✅ Sim, me mostre", use_container_width=True):
                st.session_state.quick_chat_question_inna = "sim"
                st.rerun()

        with col_nao:
            if st.button("❌ Não agora", use_container_width=True):
                st.session_state.quick_chat_question_inna = "não"
                st.rerun()

        with col_cancelar:
            if st.button("🚫 Cancelar", use_container_width=True):
                st.session_state.quick_chat_question_inna = "cancelar"
                st.rerun()

    pergunta_demo = st.text_input(
        chat_t("input_label"),
        value=pergunta_rapida_pendente,
        placeholder=chat_t("placeholder"),
        key="chat_question_input_inna",
    )

    texto_digitado_chat = str(pergunta_demo or "").lower()

    parece_anotacao_financeira = (
        any(char.isdigit() for char in texto_digitado_chat)
        and (
            "ganho" in texto_digitado_chat
            or "salario" in texto_digitado_chat
            or "salário" in texto_digitado_chat
            or "gasto" in texto_digitado_chat
            or "guardar" in texto_digitado_chat
            or "sobra" in texto_digitado_chat
        )
    )

    if parece_anotacao_financeira:
        texto_botao_chat = "Enviar anotação para a Inna"
    else:
        texto_botao_chat = "Enviar pergunta para a Inna"

    enviar_chat = st.button(texto_botao_chat, use_container_width=True)

    if enviar_chat or pergunta_rapida_pendente:
        if pergunta_demo.strip():
            pergunta_usuario = pergunta_demo.strip()

            continuacoes_curtas = {
                "sim",
                "s",
                "quero",
                "sim quero",
                "quero sim",
                "pode",
                "pode mostrar",
                "me mostre",
                "me mostra",
                "mostre",
                "como faço isso",
                "como faco isso",
                "continue",
                "pode continuar",
                "vamos",
                "ok",
                "claro",
            }

            ultima_resposta_inna = ""

            for msg in reversed(st.session_state.inna_chat_history):
                if msg.get("role") == "assistant":
                    ultima_resposta_inna = msg.get("content", "")
                    break

            pergunta_para_rag = pergunta_usuario

            texto_anotacao = pergunta_usuario.lower()

            palavras_anotacao_financeira = [
                "ganho",
                "recebo",
                "salario",
                "salário",
                "pagamento",
                "renda",
                "entra",
                "cai",
                "meu dinheiro",
                "aposentadoria",
                "beneficio",
                "benefício",
                "pensão",
                "pensao",
                "bico",
                "extra",

                "gasto",
                "gastos",
                "conta",
                "contas",
                "pago",
                "pagando",
                "despesa",
                "despesas",
                "mercado",
                "aluguel",
                "luz",
                "agua",
                "água",
                "internet",
                "telefone",
                "transporte",
                "remedio",
                "remédio",
                "parcela",
                "parcelas",
                "divida",
                "dívida",

                "guardo",
                "guardar",
                "juntar",
                "junto",
                "separo",
                "separar",
                "sobra",
                "sobrou",
                "resta",
                "fica",
                "consigo",
                "posso",
                "da pra",
                "dá pra",
                "da para",
                "dá para",
                "livre",
            ]

            parece_anotacao_financeira = (
                any(char.isdigit() for char in texto_anotacao)
                and any(palavra in texto_anotacao for palavra in palavras_anotacao_financeira)
            )

            if parece_anotacao_financeira:
                pergunta_para_rag = (
                    "ANOTACAO_FINANCEIRA_DO_USUARIO\n"
                    "O usuário informou dados financeiros em texto livre. "
                    "Não trate como pergunta genérica. "
                    "Extraia o valor que ele consegue guardar, se existir, "
                    "e oriente de forma simples, prática e educativa.\n\n"
                    f"Texto do usuário:\n{pergunta_usuario}"
                )

            elif pergunta_usuario.lower().strip("?!. ") in continuacoes_curtas and ultima_resposta_inna:
                pergunta_para_rag = (
                    "O usuário quer continuar a conversa com base na última resposta da INNA. "
                    "Não reinicie o assunto. Entregue um próximo passo prático e curto.\n\n"
                    f"Última resposta da INNA:\n{ultima_resposta_inna}\n\n"
                    f"Resposta curta do usuário:\n{pergunta_usuario}"
                )

            st.session_state.inna_chat_history.append({
                "role": "user",
                "content": pergunta_usuario,
                "source": None,
            })

            try:
                api_base_url = globals().get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

                rag_payload = {
                    "pergunta": pergunta_para_rag,
                    "idioma": st.session_state.get("app_lang", "pt"),
                    "top_k": 3,
                }

                with st.spinner("A Inna está analisando..."):
                    rag_response = requests.post(
                        f"{api_base_url}/rag/ask",
                        json=rag_payload,
                        timeout=30,
                    )

                if rag_response.status_code == 200:
                    rag_data = rag_response.json()

                    resposta_rag = rag_data.get("resposta") or "Não encontrei uma resposta suficiente na base da INNA."
                    fontes_rag = rag_data.get("fontes", [])

                    fonte_resumida = None

                    if fontes_rag:
                        fonte_principal = fontes_rag[0]
                        fonte_resumida = "📚 Fonte usada pela INNA"

                    st.session_state.inna_chat_history.append({
                        "role": "assistant",
                        "content": resposta_rag,
                        "source": fonte_resumida,
                    })

                    st.session_state.limpar_chat_input_inna = True
                    st.rerun()

                else:
                    st.error(
                        f"Não foi possível consultar o RAG da INNA. "
                        f"Status: {rag_response.status_code}"
                    )

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar na FastAPI. Confirme se a API está rodando em http://127.0.0.1:8000.")

            except requests.exceptions.Timeout:
                st.error("A API demorou muito para responder. Tente novamente.")

            except Exception as exc:
                st.error(f"Erro inesperado ao consultar o RAG da INNA: {exc}")

        else:
            st.warning(chat_t("empty"))

    st.stop()


if app_menu in ["🔐 Admin", "🔐 Admin Analytics", "Admin", "Admin Analytics"]:
    st.title("🔐 Admin Analytics — INNA")
    st.caption("Dashboard administrativo integrado ao painel principal da INNA.")

    st.markdown(
        """
<div style="
    background: linear-gradient(135deg, #0b1f3a, #102f57);
    border: 1px solid #d4af37;
    border-radius: 18px;
    padding: 22px 26px;
    margin: 18px 0 22px 0;
    color: #ffffff;
">
    <h3 style="color:#ffd77a; margin-top:0;">🔐 Área administrativa da INNA</h3>
    <p style="font-size:16px; line-height:1.6; margin-bottom:10px;">
        Este painel é destinado ao administrador da INNA e não deve aparecer para o usuário comum.
    </p>
    <p style="font-size:15px; line-height:1.6; margin-bottom:0;">
        Aqui você acompanha diagnósticos, eventos multicanal, idiomas, moedas, feedbacks,
        relatórios PDF, envio por e-mail, Telegram e evolução de uso da plataforma.
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    col_admin1, col_admin2, col_admin3 = st.columns(3)
    col_admin1.metric("Área", "Analytics")
    col_admin2.metric("Canais", "Web + PDF + E-mail + Telegram")
    col_admin3.metric("Banco", "Neon PostgreSQL")

    st.markdown(
        f"""
<a href="{DASHBOARD_ADMIN_URL}" target="_blank" style="
    display:block;
    text-align:center;
    background:#d4af37;
    color:#0b1f3a;
    font-weight:800;
    text-decoration:none;
    padding:14px 18px;
    border-radius:14px;
    margin:18px 0 24px 0;
    border:1px solid #ffe08a;
">
    🚀 Abrir Dashboard Analytics em nova aba
</a>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.write("### 📊 Dashboard Analytics integrado")

    components.iframe(
        DASHBOARD_ADMIN_URL,
        height=950,
        scrolling=True,
    )

    st.stop()


LOGIN_TEXTS_INNA = {
    "pt": {
        "title": "🔑 Entrar na INNA",
        "caption": "Acesse sua conta para usar diagnóstico, relatório, histórico e recursos personalizados.",
        "brand": "💰 Inna",
        "subtitle": "Educadora Financeira Inteligente",
        "email": "E-mail",
        "password": "Senha",
        "demo": "Ver credenciais demo",
        "user_demo": "Usuário comum",
        "admin_demo": "Administrador",
        "button": "Entrar",
        "success_user": "Login realizado com sucesso.",
        "success_admin": "Login de administrador realizado com sucesso.",
        "error": "E-mail ou senha inválidos.",
    },
    "en_us": {
        "title": "🔑 Sign in to INNA",
        "caption": "Access your account to use diagnosis, reports, history and personalized features.",
        "brand": "💰 Inna",
        "subtitle": "Intelligent Financial Educator",
        "email": "Email",
        "password": "Password",
        "demo": "Show demo credentials",
        "user_demo": "Regular user",
        "admin_demo": "Administrator",
        "button": "Sign in",
        "success_user": "Login successful.",
        "success_admin": "Administrator login successful.",
        "error": "Invalid email or password.",
    },
    "en_gb": {
        "title": "🔑 Sign in to INNA",
        "caption": "Access your account to use diagnosis, reports, history and personalised features.",
        "brand": "💰 Inna",
        "subtitle": "Intelligent Financial Educator",
        "email": "Email",
        "password": "Password",
        "demo": "Show demo credentials",
        "user_demo": "Regular user",
        "admin_demo": "Administrator",
        "button": "Sign in",
        "success_user": "Login successful.",
        "success_admin": "Administrator login successful.",
        "error": "Invalid email or password.",
    },
    "es": {
        "title": "🔑 Entrar en INNA",
        "caption": "Accede a tu cuenta para usar diagnóstico, informes, historial y recursos personalizados.",
        "brand": "💰 Inna",
        "subtitle": "Educadora Financiera Inteligente",
        "email": "E-mail",
        "password": "Contraseña",
        "demo": "Ver credenciales demo",
        "user_demo": "Usuario común",
        "admin_demo": "Administrador",
        "button": "Entrar",
        "success_user": "Inicio de sesión realizado con éxito.",
        "success_admin": "Inicio de sesión de administrador realizado con éxito.",
        "error": "E-mail o contraseña inválidos.",
    },
    "de": {
        "title": "🔑 Bei INNA anmelden",
        "caption": "Melden Sie sich an, um Diagnose, Berichte, Verlauf und personalisierte Funktionen zu nutzen.",
        "brand": "💰 Inna",
        "subtitle": "Intelligente Finanzpädagogin",
        "email": "E-Mail",
        "password": "Passwort",
        "demo": "Demo-Zugangsdaten anzeigen",
        "user_demo": "Normaler Benutzer",
        "admin_demo": "Administrator",
        "button": "Anmelden",
        "success_user": "Anmeldung erfolgreich.",
        "success_admin": "Administrator-Anmeldung erfolgreich.",
        "error": "Ungültige E-Mail oder ungültiges Passwort.",
    },
    "fr": {
        "title": "🔑 Se connecter à INNA",
        "caption": "Accédez à votre compte pour utiliser le diagnostic, les rapports, l’historique et les fonctionnalités personnalisées.",
        "brand": "💰 Inna",
        "subtitle": "Éducatrice Financière Intelligente",
        "email": "E-mail",
        "password": "Mot de passe",
        "demo": "Voir les identifiants de démonstration",
        "user_demo": "Utilisateur standard",
        "admin_demo": "Administrateur",
        "button": "Se connecter",
        "success_user": "Connexion réussie.",
        "success_admin": "Connexion administrateur réussie.",
        "error": "E-mail ou mot de passe invalide.",
    },
    "it": {
        "title": "🔑 Accedi a INNA",
        "caption": "Accedi al tuo account per usare diagnosi, report, storico e funzioni personalizzate.",
        "brand": "💰 Inna",
        "subtitle": "Educatrice Finanziaria Intelligente",
        "email": "E-mail",
        "password": "Password",
        "demo": "Mostra credenziali demo",
        "user_demo": "Utente comune",
        "admin_demo": "Amministratore",
        "button": "Accedi",
        "success_user": "Accesso effettuato con successo.",
        "success_admin": "Accesso amministratore effettuato con successo.",
        "error": "E-mail o password non validi.",
    },
    "ro": {
        "title": "🔑 Intră în INNA",
        "caption": "Accesează contul pentru diagnostic, rapoarte, istoric și funcții personalizate.",
        "brand": "💰 Inna",
        "subtitle": "Educatoare Financiară Inteligentă",
        "email": "E-mail",
        "password": "Parolă",
        "demo": "Vezi credențialele demo",
        "user_demo": "Utilizator obișnuit",
        "admin_demo": "Administrator",
        "button": "Intră",
        "success_user": "Autentificare realizată cu succes.",
        "success_admin": "Autentificare administrator realizată cu succes.",
        "error": "E-mail sau parolă invalidă.",
    },
    "ru": {
        "title": "🔑 Войти в INNA",
        "caption": "Войдите в аккаунт, чтобы использовать диагностику, отчёты, историю и персонализированные функции.",
        "brand": "💰 Inna",
        "subtitle": "Интеллектуальный финансовый помощник",
        "email": "E-mail",
        "password": "Пароль",
        "demo": "Показать демо-доступы",
        "user_demo": "Обычный пользователь",
        "admin_demo": "Администратор",
        "button": "Войти",
        "success_user": "Вход выполнен успешно.",
        "success_admin": "Вход администратора выполнен успешно.",
        "error": "Неверный e-mail или пароль.",
    },
    "uk": {
        "title": "🔑 Увійти в INNA",
        "caption": "Увійдіть в акаунт, щоб використовувати діагностику, звіти, історію та персоналізовані функції.",
        "brand": "💰 Inna",
        "subtitle": "Інтелектуальна фінансова помічниця",
        "email": "E-mail",
        "password": "Пароль",
        "demo": "Показати демо-доступи",
        "user_demo": "Звичайний користувач",
        "admin_demo": "Адміністратор",
        "button": "Увійти",
        "success_user": "Вхід виконано успішно.",
        "success_admin": "Вхід адміністратора виконано успішно.",
        "error": "Невірний e-mail або пароль.",
    },
    "ar": {
        "title": "🔑 تسجيل الدخول إلى INNA",
        "caption": "ادخل إلى حسابك لاستخدام التشخيص والتقارير والسجل والميزات المخصصة.",
        "brand": "💰 Inna",
        "subtitle": "معلّمة مالية ذكية",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "demo": "عرض بيانات الدخول التجريبية",
        "user_demo": "مستخدم عادي",
        "admin_demo": "مدير",
        "button": "تسجيل الدخول",
        "success_user": "تم تسجيل الدخول بنجاح.",
        "success_admin": "تم تسجيل دخول المدير بنجاح.",
        "error": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
    },
    "ch": {
        "title": "🔑 Bei INNA anmelden",
        "caption": "Melden Sie sich an, um Diagnose, Berichte, Verlauf und personalisierte Funktionen zu nutzen.",
        "brand": "💰 Inna",
        "subtitle": "Intelligente Finanzpädagogin",
        "email": "E-Mail",
        "password": "Passwort",
        "demo": "Demo-Zugangsdaten anzeigen",
        "user_demo": "Normaler Benutzer",
        "admin_demo": "Administrator",
        "button": "Anmelden",
        "success_user": "Anmeldung erfolgreich.",
        "success_admin": "Administrator-Anmeldung erfolgreich.",
        "error": "Ungültige E-Mail oder ungültiges Passwort.",
    },
}

def login_t(key: str) -> str:
    lang = app_lang if app_lang in LOGIN_TEXTS_INNA else "pt"
    return LOGIN_TEXTS_INNA.get(lang, LOGIN_TEXTS_INNA["pt"]).get(
        key,
        LOGIN_TEXTS_INNA["pt"].get(key, key),
    )
if app_menu == "🔑 Entrar":
    st.title(login_t("title"))
    st.caption(login_t("caption"))

    col_login1, col_login2, col_login3 = st.columns([1, 1.3, 1])

    with col_login2:
        st.markdown(f"### {login_t('brand')}")
        st.markdown(f"#### {login_t('subtitle')}")

        email_login = st.text_input(login_t("email"), key="login_email")
        senha_login = st.text_input(login_t("password"), type="password", key="login_senha")

        with st.expander(login_t("demo")):
            st.info(
                f"{login_t('user_demo')}: {INNA_USER_EMAIL} | {login_t('password')}: {INNA_USER_PASSWORD}\n\n"
                f"{login_t('admin_demo')}: {INNA_ADMIN_EMAIL} | {login_t('password')}: {INNA_ADMIN_PASSWORD}"
            )

        if st.button(login_t("button"), use_container_width=True):
            if email_login == INNA_USER_EMAIL and senha_login == INNA_USER_PASSWORD:
                st.session_state.logado = True
                st.session_state.show_login_page = False
                st.session_state.usuario = email_login
                st.session_state.perfil_usuario = "usuario"
                st.session_state.app_menu_selected = "📊 Panorama"
                st.success(login_t("success_user"))
                st.rerun()

            elif email_login == INNA_ADMIN_EMAIL and senha_login == INNA_ADMIN_PASSWORD:
                st.session_state.logado = True
                st.session_state.show_login_page = False
                st.session_state.usuario = email_login
                st.session_state.perfil_usuario = "admin"
                st.session_state.app_menu_selected = "🔐 Admin Analytics"
                st.success(login_t("success_admin"))
                st.rerun()

            else:
                st.error(login_t("error"))

    st.stop()


if app_menu == "🚪 Sair":
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.perfil_usuario = None
    st.session_state.app_menu_selected = "🏠 Início"
    st.success(ui_t("logout_success"))
    st.rerun()
if app_menu == "ℹ️ Sobre":
    st.title(ui_t("about_title"))
    st.write(ui_t("about_text"))

    st.write("### " + ui_t("about_resources"))
    st.markdown(
        """
- Streamlit Web App.
- FastAPI Backend.
- PostgreSQL/Neon Database.
- Generative AI.
- Financial PDF report.
- E-mail delivery.
- Telegram integration.
- Administrative dashboard.
- Multichannel event tracking.
- Multilingual and multicurrency support.
        """
    )

    st.success(ui_t("about_success"))
    st.stop()



INTERNAL_PAGE_TEXTS_INNA = {
    "pt": {
        "current_page": "Página atual",
        "new_diagnosis_title": "🧾 Novo diagnóstico financeiro",
        "overview_title": "📊 Panorama",
        "report_title": "📄 Relatório",
        "history_title_page": "📚 Histórico",
        "feedback_title_page": "⭐ Avaliar",
        "chat_title_page": "💬 Conversar",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Nenhum diagnóstico gerado ainda. Primeiro vá em **🧾 Novo diagnóstico**.",
        "api_connection_error": "Não foi possível conectar na FastAPI. Confirme se a API está rodando em http://127.0.0.1:8000.",
        "api_timeout": "A API demorou muito para responder. Tente novamente.",
        "unexpected_error": "Erro inesperado ao gerar diagnóstico",
        "diagnosis_opening": "Diagnóstico gerado. Abrindo a página de resultado financeiro...",
        "report_pdf_section": "### 📄 Relatório em PDF",
        "back_to_result": "📊 Voltar para resultado",
        "send_feedback": "💬 Enviar feedback",
        "new_diagnosis_btn": "🧾 Diagnóstico",
        "see_history": "📚 Ver histórico",
        "history_found": "diagnóstico(s) encontrado(s).",
        "score_evolution": "### Evolução do score",
        "diagnoses_found": "### Diagnósticos encontrados",
        "old_pdf": "📄 Baixar PDF do diagnóstico",
        "history_pdf_error": "Não foi possível gerar PDF do histórico",
        "history_search_error": "Erro ao buscar histórico pela API",
        "feedback_connection_error": "Não foi possível conectar na FastAPI para enviar o feedback. Confirme se a API está rodando.",
        "feedback_error": "Erro ao enviar feedback pela API",
        "chat_demo_info": "Aqui ficará o chat da INNA. A próxima etapa é conectar esta tela à IA para responder dúvidas com base no último diagnóstico financeiro do usuário.",
        "chat_question": "Digite uma dúvida financeira:",
        "chat_placeholder": "Exemplo: Como posso organizar minha reserva financeira?",
        "chat_button": "Enviar pergunta para a Inna",
        "chat_empty": "Digite uma pergunta antes de enviar.",
        "chat_demo_answer": "Ainda estou em modo demonstração. Em breve, vou responder usando IA e o contexto do seu diagnóstico financeiro.",
    },
    "en_us": {
        "current_page": "Current page",
        "new_diagnosis_title": "🧾 New financial diagnosis",
        "overview_title": "📊 My financial overview",
        "report_title": "📄 My report",
        "history_title_page": "📚 My history",
        "feedback_title_page": "⭐ Rate Inna",
        "chat_title_page": "💬 Chat with Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "No diagnosis has been generated yet. First go to **🧾 New diagnosis**.",
        "api_connection_error": "Could not connect to FastAPI. Check if the API is running at http://127.0.0.1:8000.",
        "api_timeout": "The API took too long to respond. Please try again.",
        "unexpected_error": "Unexpected error while generating diagnosis",
        "diagnosis_opening": "Diagnosis generated. Opening the financial result page...",
        "report_pdf_section": "### 📄 PDF report",
        "back_to_result": "📊 Back to result",
        "send_feedback": "💬 Send feedback",
        "new_diagnosis_btn": "🧾 New diagnosis",
        "see_history": "📚 View history",
        "history_found": "diagnosis record(s) found.",
        "score_evolution": "### Score evolution",
        "diagnoses_found": "### Diagnoses found",
        "old_pdf": "📄 Download PDF for diagnosis",
        "history_pdf_error": "Could not generate PDF from history",
        "history_search_error": "Error searching history through API",
        "feedback_connection_error": "Could not connect to FastAPI to send feedback. Check if the API is running.",
        "feedback_error": "Error sending feedback through API",
        "chat_demo_info": "This is where the INNA chat will be. The next step is to connect this screen to AI so it can answer questions based on the user's latest financial diagnosis.",
        "chat_question": "Type a financial question:",
        "chat_placeholder": "Example: How can I improve my financial score?",
        "chat_button": "Send question to Inna",
        "chat_empty": "Type a question before sending.",
        "chat_demo_answer": "I am still in demo mode. Soon, I will answer using AI and the context of your financial diagnosis.",
    },
    "en_gb": {
        "current_page": "Current page",
        "new_diagnosis_title": "🧾 New financial diagnosis",
        "overview_title": "📊 My financial overview",
        "report_title": "📄 My report",
        "history_title_page": "📚 My history",
        "feedback_title_page": "⭐ Rate Inna",
        "chat_title_page": "💬 Chat with Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "No diagnosis has been generated yet. First go to **🧾 New diagnosis**.",
        "api_connection_error": "Could not connect to FastAPI. Check if the API is running at http://127.0.0.1:8000.",
        "api_timeout": "The API took too long to respond. Please try again.",
        "unexpected_error": "Unexpected error while generating diagnosis",
        "diagnosis_opening": "Diagnosis generated. Opening the financial result page...",
        "report_pdf_section": "### 📄 PDF report",
        "back_to_result": "📊 Back to result",
        "send_feedback": "💬 Send feedback",
        "new_diagnosis_btn": "🧾 New diagnosis",
        "see_history": "📚 View history",
        "history_found": "diagnosis record(s) found.",
        "score_evolution": "### Score evolution",
        "diagnoses_found": "### Diagnoses found",
        "old_pdf": "📄 Download PDF for diagnosis",
        "history_pdf_error": "Could not generate PDF from history",
        "history_search_error": "Error searching history through API",
        "feedback_connection_error": "Could not connect to FastAPI to send feedback. Check if the API is running.",
        "feedback_error": "Error sending feedback through API",
        "chat_demo_info": "This is where the INNA chat will be. The next step is to connect this screen to AI so it can answer questions based on the user's latest financial diagnosis.",
        "chat_question": "Type a financial question:",
        "chat_placeholder": "Example: How can I improve my financial score?",
        "chat_button": "Send question to Inna",
        "chat_empty": "Type a question before sending.",
        "chat_demo_answer": "I am still in demo mode. Soon, I will answer using AI and the context of your financial diagnosis.",
    },
    "es": {
        "current_page": "Página actual",
        "new_diagnosis_title": "🧾 Nuevo diagnóstico financiero",
        "overview_title": "📊 Mi panorama financiero",
        "report_title": "📄 Mi informe",
        "history_title_page": "📚 Mi historial",
        "feedback_title_page": "⭐ Evaluar a Inna",
        "chat_title_page": "💬 Conversar con Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Aún no se ha generado ningún diagnóstico. Primero ve a **🧾 Nuevo diagnóstico**.",
        "api_connection_error": "No fue posible conectar con FastAPI. Verifica si la API está activa en http://127.0.0.1:8000.",
        "api_timeout": "La API tardó demasiado en responder. Inténtalo nuevamente.",
        "unexpected_error": "Error inesperado al generar diagnóstico",
        "diagnosis_opening": "Diagnóstico generado. Abriendo la página de resultado financiero...",
        "report_pdf_section": "### 📄 Informe PDF",
        "back_to_result": "📊 Volver al resultado",
        "send_feedback": "💬 Enviar comentario",
        "new_diagnosis_btn": "🧾 Nuevo diagnóstico",
        "see_history": "📚 Ver historial",
        "history_found": "diagnóstico(s) encontrado(s).",
        "score_evolution": "### Evolución del score",
        "diagnoses_found": "### Diagnósticos encontrados",
        "old_pdf": "📄 Descargar PDF del diagnóstico",
        "history_pdf_error": "No fue posible generar PDF del historial",
        "history_search_error": "Error al buscar historial por la API",
        "feedback_connection_error": "No fue posible conectar con FastAPI para enviar el feedback. Verifica si la API está activa.",
        "feedback_error": "Error al enviar feedback por la API",
        "chat_demo_info": "Aquí estará el chat de INNA. El próximo paso es conectar esta pantalla a la IA para responder preguntas con base en el último diagnóstico financiero del usuario.",
        "chat_question": "Escribe una duda financiera:",
        "chat_placeholder": "Ejemplo: ¿Cómo puedo mejorar mi puntuación financiera?",
        "chat_button": "Enviar pregunta a Inna",
        "chat_empty": "Escribe una pregunta antes de enviar.",
        "chat_demo_answer": "Todavía estoy en modo demostración. Pronto responderé usando IA y el contexto de tu diagnóstico financiero.",
    },
    "de": {
        "current_page": "Aktuelle Seite",
        "new_diagnosis_title": "🧾 Neue Finanzdiagnose",
        "overview_title": "📊 Mein Finanzüberblick",
        "report_title": "📄 Mein Bericht",
        "history_title_page": "📚 Mein Verlauf",
        "feedback_title_page": "⭐ Inna bewerten",
        "chat_title_page": "💬 Mit Inna sprechen",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Es wurde noch keine Diagnose erstellt. Gehen Sie zuerst zu **🧾 Neue Diagnose**.",
        "api_connection_error": "Verbindung zur FastAPI nicht möglich. Prüfen Sie, ob die API unter http://127.0.0.1:8000 läuft.",
        "api_timeout": "Die API hat zu lange gebraucht. Versuchen Sie es erneut.",
        "unexpected_error": "Unerwarteter Fehler beim Erstellen der Diagnose",
        "diagnosis_opening": "Diagnose erstellt. Finanzübersicht wird geöffnet...",
        "report_pdf_section": "### 📄 PDF-Bericht",
        "back_to_result": "📊 Zurück zum Ergebnis",
        "send_feedback": "💬 Feedback senden",
        "new_diagnosis_btn": "🧾 Neue Diagnose",
        "see_history": "📚 Verlauf ansehen",
        "history_found": "Diagnose(n) gefunden.",
        "score_evolution": "### Score-Entwicklung",
        "diagnoses_found": "### Gefundene Diagnosen",
        "old_pdf": "📄 PDF der Diagnose herunterladen",
        "history_pdf_error": "PDF aus dem Verlauf konnte nicht erstellt werden",
        "history_search_error": "Fehler beim Suchen des Verlaufs über die API",
        "feedback_connection_error": "Verbindung zur FastAPI zum Senden des Feedbacks nicht möglich.",
        "feedback_error": "Fehler beim Senden des Feedbacks über die API",
        "chat_demo_info": "Hier wird der INNA-Chat angezeigt. Der nächste Schritt ist, diese Seite mit KI zu verbinden.",
        "chat_question": "Geben Sie eine Finanzfrage ein:",
        "chat_placeholder": "Beispiel: Wie kann ich meinen Finanzscore verbessern?",
        "chat_button": "Frage an Inna senden",
        "chat_empty": "Geben Sie vor dem Senden eine Frage ein.",
        "chat_demo_answer": "Ich bin noch im Demonstrationsmodus. Bald werde ich mit KI und Ihrer Finanzdiagnose antworten.",
    },
    "fr": {
        "current_page": "Page actuelle",
        "new_diagnosis_title": "🧾 Nouveau diagnostic financier",
        "overview_title": "📊 Mon panorama financier",
        "report_title": "📄 Mon rapport",
        "history_title_page": "📚 Mon historique",
        "feedback_title_page": "⭐ Évaluer Inna",
        "chat_title_page": "💬 Parler avec Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Aucun diagnostic n’a encore été généré. Allez d’abord dans **🧾 Nouveau diagnostic**.",
        "api_connection_error": "Impossible de se connecter à FastAPI. Vérifiez si l’API fonctionne sur http://127.0.0.1:8000.",
        "api_timeout": "L’API a mis trop de temps à répondre. Réessayez.",
        "unexpected_error": "Erreur inattendue lors de la génération du diagnostic",
        "diagnosis_opening": "Diagnostic généré. Ouverture de la page de résultat financier...",
        "report_pdf_section": "### 📄 Rapport PDF",
        "back_to_result": "📊 Retour au résultat",
        "send_feedback": "💬 Envoyer un retour",
        "new_diagnosis_btn": "🧾 Nouveau diagnostic",
        "see_history": "📚 Voir l’historique",
        "history_found": "diagnostic(s) trouvé(s).",
        "score_evolution": "### Évolution du score",
        "diagnoses_found": "### Diagnostics trouvés",
        "old_pdf": "📄 Télécharger le PDF du diagnostic",
        "history_pdf_error": "Impossible de générer le PDF de l’historique",
        "history_search_error": "Erreur lors de la recherche de l’historique via l’API",
        "feedback_connection_error": "Impossible de se connecter à FastAPI pour envoyer le feedback.",
        "feedback_error": "Erreur lors de l’envoi du feedback via l’API",
        "chat_demo_info": "C’est ici que le chat INNA sera affiché. La prochaine étape consiste à connecter cette page à l’IA.",
        "chat_question": "Écrivez une question financière :",
        "chat_placeholder": "Exemple : Comment améliorer mon score financier ?",
        "chat_button": "Envoyer la question à Inna",
        "chat_empty": "Écrivez une question avant d’envoyer.",
        "chat_demo_answer": "Je suis encore en mode démonstration. Bientôt, je répondrai avec l’IA et votre diagnostic financier.",
    },
    "it": {
        "current_page": "Pagina attuale",
        "new_diagnosis_title": "🧾 Nuova diagnosi finanziaria",
        "overview_title": "📊 Il mio panorama finanziario",
        "report_title": "📄 Il mio report",
        "history_title_page": "📚 Il mio storico",
        "feedback_title_page": "⭐ Valuta Inna",
        "chat_title_page": "💬 Parlare con Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Non è stata ancora generata alcuna diagnosi. Vai prima su **🧾 Nuova diagnosi**.",
        "api_connection_error": "Impossibile connettersi a FastAPI. Verifica che l’API sia attiva su http://127.0.0.1:8000.",
        "api_timeout": "L’API ha impiegato troppo tempo a rispondere. Riprova.",
        "unexpected_error": "Errore imprevisto durante la generazione della diagnosi",
        "diagnosis_opening": "Diagnosi generata. Apertura della pagina del risultato finanziario...",
        "report_pdf_section": "### 📄 Report PDF",
        "back_to_result": "📊 Torna al risultato",
        "send_feedback": "💬 Invia feedback",
        "new_diagnosis_btn": "🧾 Nuova diagnosi",
        "see_history": "📚 Vedi storico",
        "history_found": "diagnosi trovata/e.",
        "score_evolution": "### Evoluzione del punteggio",
        "diagnoses_found": "### Diagnosi trovate",
        "old_pdf": "📄 Scarica PDF della diagnosi",
        "history_pdf_error": "Impossibile generare PDF dallo storico",
        "history_search_error": "Errore nella ricerca dello storico tramite API",
        "feedback_connection_error": "Impossibile connettersi a FastAPI per inviare il feedback.",
        "feedback_error": "Errore durante l’invio del feedback tramite API",
        "chat_demo_info": "Qui sarà disponibile la chat di INNA. Il prossimo passo è collegare questa schermata all’IA.",
        "chat_question": "Scrivi una domanda finanziaria:",
        "chat_placeholder": "Esempio: Come posso migliorare il mio punteggio finanziario?",
        "chat_button": "Invia domanda a Inna",
        "chat_empty": "Scrivi una domanda prima di inviare.",
        "chat_demo_answer": "Sono ancora in modalità dimostrativa. Presto risponderò usando IA e la tua diagnosi finanziaria.",
    },
    "ro": {
        "current_page": "Pagina curentă",
        "new_diagnosis_title": "🧾 Diagnostic financiar nou",
        "overview_title": "📊 Panorama mea financiară",
        "report_title": "📄 Raportul meu",
        "history_title_page": "📚 Istoricul meu",
        "feedback_title_page": "⭐ Evaluează Inna",
        "chat_title_page": "💬 Vorbește cu Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Nu a fost generat încă niciun diagnostic. Mai întâi mergi la **🧾 Diagnostic nou**.",
        "api_connection_error": "Nu s-a putut conecta la FastAPI. Verifică dacă API-ul rulează pe http://127.0.0.1:8000.",
        "api_timeout": "API-ul a răspuns prea greu. Încearcă din nou.",
        "unexpected_error": "Eroare neașteptată la generarea diagnosticului",
        "diagnosis_opening": "Diagnostic generat. Se deschide pagina rezultatului financiar...",
        "report_pdf_section": "### 📄 Raport PDF",
        "back_to_result": "📊 Înapoi la rezultat",
        "send_feedback": "💬 Trimite feedback",
        "new_diagnosis_btn": "🧾 Diagnostic nou",
        "see_history": "📚 Vezi istoricul",
        "history_found": "diagnostic(e) găsite.",
        "score_evolution": "### Evoluția scorului",
        "diagnoses_found": "### Diagnostice găsite",
        "old_pdf": "📄 Descarcă PDF-ul diagnosticului",
        "history_pdf_error": "Nu s-a putut genera PDF din istoric",
        "history_search_error": "Eroare la căutarea istoricului prin API",
        "feedback_connection_error": "Nu s-a putut conecta la FastAPI pentru trimiterea feedbackului.",
        "feedback_error": "Eroare la trimiterea feedbackului prin API",
        "chat_demo_info": "Aici va fi chatul INNA. Următorul pas este conectarea acestei pagini la IA.",
        "chat_question": "Scrie o întrebare financiară:",
        "chat_placeholder": "Exemplu: Cum îmi pot îmbunătăți scorul financiar?",
        "chat_button": "Trimite întrebarea către Inna",
        "chat_empty": "Scrie o întrebare înainte de trimitere.",
        "chat_demo_answer": "Sunt încă în modul demonstrație. În curând voi răspunde folosind IA și diagnosticul tău financiar.",
    },
    "ru": {
        "current_page": "Текущая страница",
        "new_diagnosis_title": "🧾 Новая финансовая диагностика",
        "overview_title": "📊 Мой финансовый обзор",
        "report_title": "📄 Мой отчёт",
        "history_title_page": "📚 Моя история",
        "feedback_title_page": "⭐ Оценить Inna",
        "chat_title_page": "💬 Поговорить с Inna",
        "admin_title_page": "🔐 Admin Analytics — INNA",
        "no_diagnosis": "Диагностика ещё не создана. Сначала перейдите в **🧾 Новая диагностика**.",
        "api_connection_error": "Не удалось подключиться к FastAPI. Проверьте, работает ли API на http://127.0.0.1:8000.",
        "api_timeout": "API слишком долго отвечает. Попробуйте снова.",
        "unexpected_error": "Неожиданная ошибка при создании диагностики",
        "diagnosis_opening": "Диагностика создана. Открывается страница финансового результата...",
        "report_pdf_section": "### 📄 PDF-отчёт",
        "back_to_result": "📊 Вернуться к результату",
        "send_feedback": "💬 Отправить отзыв",
        "new_diagnosis_btn": "🧾 Новая диагностика",
        "see_history": "📚 Посмотреть историю",
        "history_found": "диагностик(а) найдено.",
        "score_evolution": "### Динамика score",
        "diagnoses_found": "### Найденные диагностики",
        "old_pdf": "📄 Скачать PDF диагностики",
        "history_pdf_error": "Не удалось создать PDF из истории",
        "history_search_error": "Ошибка при поиске истории через API",
        "feedback_connection_error": "Не удалось подключиться к FastAPI для отправки отзыва.",
        "feedback_error": "Ошибка при отправке отзыва через API",
        "chat_demo_info": "Здесь будет чат INNA. Следующий шаг — подключить эту страницу к ИИ.",
        "chat_question": "Введите финансовый вопрос:",
        "chat_placeholder": "Пример: Как улучшить мой финансовый рейтинг?",
        "chat_button": "Отправить вопрос Inna",
        "chat_empty": "Введите вопрос перед отправкой.",
        "chat_demo_answer": "Я пока работаю в демо-режиме. Скоро я буду отвечать с помощью ИИ и вашей финансовой диагностики.",
    },
}

for lang_code in ["uk", "ar", "ch"]:
    INTERNAL_PAGE_TEXTS_INNA[lang_code] = INTERNAL_PAGE_TEXTS_INNA.get(lang_code, INTERNAL_PAGE_TEXTS_INNA["en_us"]) if lang_code in INTERNAL_PAGE_TEXTS_INNA else INTERNAL_PAGE_TEXTS_INNA["en_us"]

def page_t(key: str) -> str:
    lang = app_lang if app_lang in INTERNAL_PAGE_TEXTS_INNA else "pt"
    return INTERNAL_PAGE_TEXTS_INNA.get(lang, INTERNAL_PAGE_TEXTS_INNA["pt"]).get(
        key,
        INTERNAL_PAGE_TEXTS_INNA["pt"].get(key, key),
    )
st.caption(f"{page_t('current_page')}: {menu_t(app_menu) if 'menu_t' in globals() else app_menu}")


if app_menu == "📊 Panorama":
    st.title(page_t("overview_title"))

    response = st.session_state.get("last_response")

    if not response:
        st.warning(page_t("no_diagnosis"))
        st.stop()

    st.success(tr("success"))

    col1, col2, col3 = st.columns(3)

    col1.metric("Score", f"{float(response.get('score_financeiro', 0)):.1f}/100")
    col2.metric("Risco", response.get("nivel_risco", "não informado"))
    col3.metric(
        "Saldo estimado",
        format_currency_app(
            response.get("saldo_estimado", 0),
            response.get("simbolo_moeda", current_currency_info["simbolo"]),
            response.get("moeda", current_currency_info["moeda"]),
        ),
    )

    st.divider()

    st.write(tr("diagnosis"))
    diagnostico_formatado = response["diagnostico"].replace("$", "\\$")
    st.markdown(diagnostico_formatado)

    st.write(tr("plan"))
    plano_formatado = response["plano_30_dias"].replace("$", "\\$")
    st.markdown(plano_formatado)

    st.divider()

    col_nav1, col_nav2 = st.columns(2)

    if col_nav1.button("📄 Abrir relatório PDF e e-mail"):
        st.session_state.app_menu_selected = "📄 Relatório"
        st.rerun()

    if col_nav2.button("💬 Enviar feedback"):
        st.session_state.app_menu_selected = "⭐ Avaliar"
        st.rerun()

    st.stop()


if app_menu == "📄 Relatório":
    st.title(page_t("report_title"))

    response = st.session_state.get("last_response")

    if not response:
        st.warning(page_t("no_diagnosis"))
        st.stop()

    diagnostico_id = response.get("id")

    if not diagnostico_id:
        st.warning(tr("pdf_unavailable"))
        st.stop()

    st.write(page_t("report_pdf_section"))

    try:
        pdf_bytes = baixar_relatorio_pdf_api(diagnostico_id)

        st.download_button(
            label=tr("download_pdf"),
            data=pdf_bytes,
            file_name=f"relatorio_inna_{response['nome'].replace(' ', '_').lower()}_{diagnostico_id}.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.warning(f"{tr('pdf_error')}: {error}")

    st.divider()

    st.markdown(tr("email_title"))

    email_destino = st.text_input(
        tr("email_input"),
        placeholder="seuemail@gmail.com",
        key=f"email_destino_menu_{diagnostico_id}",
    )

    if st.button(tr("email_button"), key=f"btn_email_menu_{diagnostico_id}"):
        if not email_destino or "@" not in email_destino or "." not in email_destino:
            st.warning(tr("email_invalid"))
        else:
            try:
                currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

                enviar_relatorio_email(
                    diagnostico_id,
                    email_destino,
                    idioma=app_lang,
                    moeda=currency_info["moeda"],
                    simbolo_moeda=currency_info["simbolo"],
                )

                st.success(tr("email_success"))

            except Exception as error:
                st.error(f"{tr('email_error')}: {error}")

    st.divider()

    col_rel1, col_rel2 = st.columns(2)

    if col_rel1.button(page_t("back_to_result")):
        st.session_state.app_menu_selected = "📊 Panorama"
        st.rerun()

    if col_rel2.button(page_t("send_feedback")):
        st.session_state.app_menu_selected = "⭐ Avaliar"
        st.rerun()

    st.stop()


if app_menu == "⭐ Avaliar":
    st.title(page_t("feedback_title_page"))

    response = st.session_state.get("last_response")

    if not response:
        st.warning(page_t("no_diagnosis"))
        st.stop()

    st.caption(tr("feedback_help"))

    with st.form("feedback_form_menu"):
        util = st.radio(
            tr("feedback_question"),
            [tr("yes"), tr("no")],
            horizontal=True,
            key="feedback_util_menu",
        )

        comentario = st.text_area(
            tr("feedback_comment"),
            placeholder=tr("feedback_placeholder"),
            key="feedback_comentario_menu",
        )

        feedback_submitted = st.form_submit_button(tr("feedback_button"))

    if feedback_submitted:
        feedback_payload = {
            "nome": response["nome"],
            "util": util,
            "comentario": comentario,
            "score_financeiro": response["score_financeiro"],
            "nivel_risco": translate_risk_app(response["nivel_risco"]),
        }

        try:
            enviar_feedback_api(feedback_payload)
            st.success(tr("feedback_success"))
        except requests.exceptions.ConnectionError:
            st.error(
                "Não foi possível conectar na FastAPI para enviar o feedback. "
                "Confirme se a API está rodando."
            )
        except Exception as error:
            st.error(f"{page_t('feedback_error')}: {error}")

    st.divider()

    col_fb1, col_fb2 = st.columns(2)

    if col_fb1.button(page_t("new_diagnosis_btn")):
        st.session_state.last_response = None
        st.session_state.last_payload = None
        st.session_state.app_menu_selected = "🏠 Início"
        st.rerun()

    if col_fb2.button(page_t("see_history")):
        st.session_state.app_menu_selected = "📚 Histórico"
        st.rerun()

    st.stop()


if app_menu == "📚 Histórico":
    st.title("📚 Meu histórico individual")
    st.caption(tr("history_help"))

    with st.form("historico_form_menu"):
        nome_busca = st.text_input(
            tr("history_name"),
            value=(st.session_state.get("last_payload") or {}).get("nome", ""),
            key="historico_nome_menu",
        )

        limite = st.number_input(
            tr("history_limit"),
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            key="historico_limite_menu",
        )

        buscar_historico = st.form_submit_button(tr("history_button"))

    if buscar_historico:
        try:
            historico = buscar_historico_usuario_api(nome_busca, int(limite))

            if not historico:
                st.info(tr("history_empty"))
            else:
                for item in historico:
                    with st.expander(f"Diagnóstico {item['id']} — {item['nome']}"):
                        st.write(f"**Score:** {item.get('score_financeiro')}")
                        st.write(f"**Risco:** {item.get('nivel_risco')}")
                        st.write(f"**Moeda:** {item.get('moeda')} {item.get('simbolo_moeda')}")

                        st.write(f"**{tr('diagnosis')}:**")
                        st.write(item["diagnostico"])

                        try:
                            pdf_antigo = baixar_relatorio_pdf_api(item["id"])

                            st.download_button(
                                label=f"{page_t('old_pdf')} {item['id']}",
                                data=pdf_antigo,
                                file_name=f"relatorio_inna_{item['nome'].replace(' ', '_').lower()}_{item['id']}.pdf",
                                mime="application/pdf",
                                key=f"download_pdf_historico_menu_{item['id']}",
                            )
                        except Exception as error:
                            st.warning(f"{page_t('history_pdf_error')}: {error}")

        except Exception as error:
            st.error(f"{page_t('history_search_error')}: {error}")

    st.stop()


st.title(tr("title"))

if not verificar_api_online():
    st.error(tr("api_offline"))
    st.stop()

st.subheader(tr("subtitle"))

st.info(tr("notice"))

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_payload" not in st.session_state:
    st.session_state.last_payload = None


with st.form("financial_form"):
    nome = st.text_input(tr("name"), value="Ronaldo")

    st.caption(
        tr("currency_notice").format(
            currency=f"{current_currency_info['moeda']} / {current_currency_info['simbolo']}"
            if current_currency_info["simbolo"] != current_currency_info["moeda"]
            else current_currency_info["moeda"]
        )
    )

    renda_mensal = st.number_input(
        label_with_currency("monthly_income"),
        min_value=0.0,
        value=3000.0,
        step=100.0,
    )

    gastos_fixos = st.number_input(
        label_with_currency("fixed_expenses"),
        min_value=0.0,
        value=1400.0,
        step=100.0,
    )

    gastos_variaveis = st.number_input(
        label_with_currency("variable_expenses"),
        min_value=0.0,
        value=700.0,
        step=100.0,
    )

    dividas_mensais = st.number_input(
        label_with_currency("debts"),
        min_value=0.0,
        value=300.0,
        step=100.0,
    )

    reserva_atual = st.number_input(
        label_with_currency("savings"),
        min_value=0.0,
        value=500.0,
        step=100.0,
    )

    objetivo = st.text_area(
        tr("goal"),
        value=tr("default_goal"),
    )

    submitted = st.form_submit_button(tr("generate"))


if submitted:
    currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

    payload = {
        "nome": nome,
        "renda_mensal": renda_mensal,
        "gastos_fixos": gastos_fixos,
        "gastos_variaveis": gastos_variaveis,
        "dividas_mensais": dividas_mensais,
        "reserva_atual": reserva_atual,
        "objetivo": objetivo,
        "idioma": app_lang,
        "moeda": currency_info["moeda"],
        "simbolo_moeda": currency_info["simbolo"],
    }

    try:
        with st.spinner(tr("loading")):
            response = gerar_diagnostico_api(payload)

        # Garante que moeda e símbolo apareçam na interface,
        # mesmo quando a API não devolver esses campos no response.
        response.setdefault("moeda", payload.get("moeda", current_currency_info["moeda"]))
        response.setdefault("simbolo_moeda", payload.get("simbolo_moeda", current_currency_info["simbolo"]))

        st.session_state.last_payload = payload
        st.session_state.last_response = response
        st.session_state.app_menu_selected = "📊 Panorama"

        st.success(tr("saved"))
        st.info(page_t("diagnosis_opening"))
        st.rerun()

    except requests.exceptions.ConnectionError:
        st.error(
            "Não foi possível conectar na FastAPI. "
            "Confirme se a API está rodando em http://127.0.0.1:8000."
        )

    except requests.exceptions.Timeout:
        st.error(page_t("api_timeout"))

    except requests.exceptions.HTTPError as error:
        st.error(f"Erro HTTP ao chamar a API: {error}")

    except Exception as error:
        st.error(f"{page_t('unexpected_error')}: {error}")


if st.session_state.last_response:
    response = st.session_state.last_response

    st.success(tr("success"))

    col1, col2, col3 = st.columns(3)

    col1.metric(
        tr("estimated_balance"),
        format_currency_app(
            response["saldo_estimado"],
            response.get("simbolo_moeda", current_currency_info["simbolo"]),
            response.get("moeda", current_currency_info["moeda"]),
        ),
    )

    col2.metric(
        tr("financial_score"),
        f"{response['score_financeiro']}/100",
    )

    col3.metric(
        tr("risk"),
        translate_risk_app(response["nivel_risco"]),
    )

    st.write(tr("diagnosis"))
    diagnostico_formatado = response["diagnostico"].replace("$", "\\$")
    st.markdown(diagnostico_formatado)

    st.write(tr("plan"))
    plano_formatado = response["plano_30_dias"].replace("$", "\\$")
    st.markdown(plano_formatado)

    st.divider()

    diagnostico_id = response.get("id")

    if diagnostico_id:
        try:
            pdf_bytes = baixar_relatorio_pdf_api(diagnostico_id)

            st.download_button(
                label=tr("download_pdf"),
                data=pdf_bytes,
                file_name=f"relatorio_inna_{response['nome'].replace(' ', '_').lower()}_{diagnostico_id}.pdf",
                mime="application/pdf",
            )

        except Exception as error:
            st.warning(f"{tr('pdf_error')}: {error}")

        st.markdown(tr("email_title"))

        email_destino = st.text_input(
            tr("email_input"),
            placeholder="seuemail@gmail.com",
            key=f"email_destino_{diagnostico_id}",
        )

        if st.button(tr("email_button"), key=f"btn_email_{diagnostico_id}"):
            if not email_destino or "@" not in email_destino or "." not in email_destino:
                st.warning(tr("email_invalid"))
            else:
                try:
                    currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])
                    enviar_relatorio_email(
                        diagnostico_id,
                        email_destino,
                        idioma=app_lang,
                        moeda=currency_info["moeda"],
                        simbolo_moeda=currency_info["simbolo"],
                    )
                    st.success(tr("email_success"))
                except Exception as error:
                    st.error(f"{tr('email_error')}: {error}")

    else:
        st.warning(tr("pdf_unavailable"))


    st.divider()

    st.write(tr("feedback_title"))
    st.caption(tr("feedback_help"))

    with st.form("feedback_form"):
        util = st.radio(
            tr("feedback_question"),
            [tr("yes"), tr("no")],
            horizontal=True,
        )

        comentario = st.text_area(
            tr("feedback_comment"),
            placeholder=tr("feedback_placeholder"),
        )

        feedback_submitted = st.form_submit_button(tr("feedback_button"))

    if feedback_submitted:
        feedback_payload = {
            "nome": response["nome"],
            "util": util,
            "comentario": comentario,
            "score_financeiro": response["score_financeiro"],
            "nivel_risco": translate_risk_app(response["nivel_risco"]),
        }

        try:
            enviar_feedback_api(feedback_payload)
            st.success(tr("feedback_success"))

        except requests.exceptions.ConnectionError:
            st.error(
                "Não foi possível conectar na FastAPI para enviar o feedback. "
                "Confirme se a API está rodando."
            )

        except Exception as error:
            st.error(f"{page_t('feedback_error')}: {error}")


st.divider()

st.write("## 📚 " + tr("history_title").replace("### ", ""))

st.caption(tr("history_help"))

with st.form("historico_form"):
    nome_historico = st.text_input(
        tr("history_name"),
        value="Ronaldo",
    )

    limite_historico = st.number_input(
        tr("history_limit"),
        min_value=1,
        max_value=20,
        value=10,
        step=1,
    )

    buscar_historico = st.form_submit_button(tr("history_button"))

if buscar_historico:
    try:
        historico = buscar_historico_usuario_api(
            nome=nome_historico,
            limit=int(limite_historico),
        )

        if not historico:
            st.warning(tr("history_empty"))
        else:
            st.success(f"{len(historico)} {page_t('history_found')}")

            historico_ordenado = sorted(
                historico,
                key=lambda item: item["id"],
            )

            score_data = {
                item["id"]: item["score_financeiro"]
                for item in historico_ordenado
            }

            st.write(page_t("score_evolution"))
            st.line_chart(score_data)

            st.write(page_t("diagnoses_found"))

            for item in historico:
                with st.expander(
                    f"ID {item['id']} — {item['nome']} — {tr('history_score')} {item['score_financeiro']}/100 — {tr('risk')} {translate_risk_app(item['nivel_risco'])}"
                ):
                    st.write(
                        f"**{tr('estimated_balance')}:** "
                        f"{format_currency_app(item['saldo_estimado'], item.get('simbolo_moeda', current_currency_info['simbolo']), item.get('moeda', current_currency_info['moeda']))}"
                    )
                    st.write(f"**{tr('income_commitment')}:** {item['comprometimento_renda_percentual']:.2f}%")
                    st.write(f"**{tr('reserve_months')}:** {item['meses_reserva_estimados']:.2f}")
                    st.write(f"**{tr('goal')}:** {item.get('objetivo', '')}")

                    st.write(f"**{tr('diagnosis')}:**")
                    st.write(item["diagnostico"])

                    try:
                        pdf_antigo = baixar_relatorio_pdf_api(item["id"])

                        st.download_button(
                            label=f"{page_t('old_pdf')} {item['id']}",
                            data=pdf_antigo,
                            file_name=f"relatorio_inna_{item['nome'].replace(' ', '_').lower()}_{item['id']}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_historico_{item['id']}",
                        )
                    except Exception as error:
                        st.warning(f"{page_t('history_pdf_error')}: {error}")

    except Exception as error:
        st.error(f"{page_t('history_search_error')}: {error}")
























































