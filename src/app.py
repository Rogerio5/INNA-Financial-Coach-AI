import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st

from src.financial_engine import build_financial_diagnosis
from src.gemini_client import generate_ai_plan
from src.logger import save_interaction
from src.feedback import save_feedback


st.set_page_config(
    page_title="INNA Financial Coach AI",
    page_icon="💰",
    layout="centered",
)

st.title("💰 INNA Financial Coach AI")
st.subheader("Diagnóstico financeiro com IA e plano de ação de 30 dias")

st.info(
    "A INNA é uma educadora financeira. Ela não recomenda investimentos "
    "nem substitui um profissional certificado."
)

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_payload" not in st.session_state:
    st.session_state.last_payload = None

with st.form("financial_form"):
    nome = st.text_input("Seu nome", value="Ronaldo")

    renda_mensal = st.number_input(
        "Renda mensal",
        min_value=0.0,
        value=3000.0,
        step=100.0,
    )

    gastos_fixos = st.number_input(
        "Gastos fixos mensais",
        min_value=0.0,
        value=1400.0,
        step=100.0,
    )

    gastos_variaveis = st.number_input(
        "Gastos variáveis mensais",
        min_value=0.0,
        value=700.0,
        step=100.0,
    )

    dividas_mensais = st.number_input(
        "Dívidas mensais",
        min_value=0.0,
        value=300.0,
        step=100.0,
    )

    reserva_atual = st.number_input(
        "Reserva atual",
        min_value=0.0,
        value=500.0,
        step=100.0,
    )

    objetivo = st.text_area(
        "Qual seu objetivo financeiro?",
        value="Organizar minha vida financeira",
    )

    submitted = st.form_submit_button("Gerar diagnóstico com a INNA")

if submitted:
    payload = {
        "nome": nome,
        "renda_mensal": renda_mensal,
        "gastos_fixos": gastos_fixos,
        "gastos_variaveis": gastos_variaveis,
        "dividas_mensais": dividas_mensais,
        "reserva_atual": reserva_atual,
        "objetivo": objetivo,
    }

    diagnosis = build_financial_diagnosis(payload)
    ai_plan = generate_ai_plan(payload, diagnosis)

    response = {
        **diagnosis,
        "nome": nome,
        "plano_30_dias": ai_plan,
    }

    save_interaction(payload, response)

    st.session_state.last_payload = payload
    st.session_state.last_response = response

if st.session_state.last_response:
    response = st.session_state.last_response

    st.success("Diagnóstico gerado com sucesso!")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Saldo estimado",
        f"R$ {response['saldo_estimado']:.2f}",
    )

    col2.metric(
        "Score financeiro",
        f"{response['score_financeiro']}/100",
    )

    col3.metric(
        "Risco",
        response["nivel_risco"],
    )

    st.write("### Diagnóstico")
    st.write(response["diagnostico"])

    st.write("### Plano de ação de 30 dias")
    st.write(response["plano_30_dias"])

    st.divider()

    st.write("### Feedback")
    st.caption("Sua avaliação ajuda a melhorar a INNA e validar o projeto.")

    with st.form("feedback_form"):
        util = st.radio(
            "Essa resposta foi útil?",
            ["Sim", "Não"],
            horizontal=True,
        )

        comentario = st.text_area(
            "Comentário opcional",
            placeholder="Exemplo: o plano ficou claro, faltou mais detalhe, gostei da explicação...",
        )

        feedback_submitted = st.form_submit_button("Enviar feedback")

    if feedback_submitted:
        save_feedback(
            nome=response["nome"],
            util=util,
            comentario=comentario,
            score_financeiro=response["score_financeiro"],
            nivel_risco=response["nivel_risco"],
        )

        st.success("Feedback registrado com sucesso. Obrigado por ajudar a evoluir a INNA!")
