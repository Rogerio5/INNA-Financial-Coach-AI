import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import requests

from src.api_client import gerar_diagnostico_api, enviar_feedback_api, baixar_relatorio_pdf_api, buscar_historico_usuario_api, verificar_api_online, enviar_relatorio_email


st.set_page_config(
    page_title="INNA Financial Coach AI",
    page_icon="💰",
    layout="centered",
)


APP_LANG_LABELS = {
    "pt": "🇧🇷 Português Brasil",
    "en_us": "🇺🇸 English US",
    "en_gb": "🇬🇧 English UK",
}

APP_TRANSLATIONS = {
    "pt": {
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnóstico financeiro com IA e plano de ação de 30 dias",
        "notice": "A INNA é uma educadora financeira. Ela não recomenda investimentos nem substitui um profissional certificado.",
        "api_offline": "A API da INNA está offline. Confirme se a API online está ativa.",
        "name": "Seu nome",
        "monthly_income": tr("monthly_income"),
        "fixed_expenses": tr("fixed_expenses"),
        "variable_expenses": tr("variable_expenses"),
        "debts": tr("debts"),
        "savings": tr("savings"),
        "goal": tr("goal"),
        "default_goal": "Organizar minha vida financeira",
        "generate": "Gerar diagnóstico com a INNA",
        "loading": "Chamando a API da INNA e gerando diagnóstico com IA...",
        "saved": "Diagnóstico gerado e salvo via FastAPI com sucesso!",
        "success": "Diagnóstico gerado com sucesso!",
        "diagnosis": "### Diagnóstico",
        "plan": "### Plano de ação de 30 dias",
        "download_pdf": "📄 Baixar relatório em PDF",
        "email_title": "### 📧 Receber relatório por e-mail",
        "email_input": tr("email_input"),
        "email_button": "📧 Enviar relatório por e-mail",
        "email_invalid": "Digite um e-mail válido.",
        "email_success": "Relatório enviado por e-mail com sucesso!",
        "email_error": "Erro ao enviar relatório por e-mail",
        "pdf_error": "Não foi possível baixar o relatório pela API",
        "pdf_unavailable": "Relatório PDF indisponível: diagnóstico ainda não possui ID retornado pela API.",
        "feedback_title": "Feedback",
        "feedback_comment": tr("feedback_comment"),
        "feedback_placeholder": "Exemplo: o plano ficou claro, faltou mais detalhe, gostei da explicação...",
        "feedback_button": "Enviar feedback",
        "feedback_success": "Feedback registrado via FastAPI com sucesso. Obrigado por ajudar a evoluir a INNA!",
        "history_title": "Histórico individual",
        "history_name": tr("history_name"),
        "history_limit": tr("history_limit"),
        "history_button": "Buscar histórico",
        "history_empty": "Nenhum diagnóstico encontrado para esse nome.",
    },
    "en_us": {
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
    },
    "en_gb": {
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
    },
}

app_lang = st.sidebar.selectbox(
    "🌍 Idioma / Language",
    options=list(APP_LANG_LABELS.keys()),
    format_func=lambda key: APP_LANG_LABELS[key],
)

def tr(key: str) -> str:
    return APP_TRANSLATIONS.get(app_lang, APP_TRANSLATIONS["pt"]).get(
        key,
        APP_TRANSLATIONS["pt"].get(key, key),
    )


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

    renda_mensal = st.number_input(
        tr("monthly_income"),
        min_value=0.0,
        value=3000.0,
        step=100.0,
    )

    gastos_fixos = st.number_input(
        tr("fixed_expenses"),
        min_value=0.0,
        value=1400.0,
        step=100.0,
    )

    gastos_variaveis = st.number_input(
        tr("variable_expenses"),
        min_value=0.0,
        value=700.0,
        step=100.0,
    )

    dividas_mensais = st.number_input(
        tr("debts"),
        min_value=0.0,
        value=300.0,
        step=100.0,
    )

    reserva_atual = st.number_input(
        tr("savings"),
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
    payload = {
        "nome": nome,
        "renda_mensal": renda_mensal,
        "gastos_fixos": gastos_fixos,
        "gastos_variaveis": gastos_variaveis,
        "dividas_mensais": dividas_mensais,
        "reserva_atual": reserva_atual,
        "objetivo": objetivo,
    }

    try:
        with st.spinner(tr("loading")):
            response = gerar_diagnostico_api(payload)

        st.session_state.last_payload = payload
        st.session_state.last_response = response

        st.success(tr("saved"))

    except requests.exceptions.ConnectionError:
        st.error(
            "Não foi possível conectar na FastAPI. "
            "Confirme se a API está rodando em http://127.0.0.1:8000."
        )

    except requests.exceptions.Timeout:
        st.error("A API demorou muito para responder. Tente novamente.")

    except requests.exceptions.HTTPError as error:
        st.error(f"Erro HTTP ao chamar a API: {error}")

    except Exception as error:
        st.error(f"Erro inesperado ao gerar diagnóstico: {error}")


if st.session_state.last_response:
    response = st.session_state.last_response

    st.success(tr("success"))

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
                    enviar_relatorio_email(diagnostico_id, email_destino)
                    st.success(tr("email_success"))
                except Exception as error:
                    st.error(f"{tr('email_error')}: {error}")

    else:
        st.warning(tr("pdf_unavailable"))


    st.divider()

    st.write(tr("feedback_title"))
    st.caption("Sua avaliação ajuda a melhorar a INNA e validar o projeto.")

    with st.form("feedback_form"):
        util = st.radio(
            "Essa resposta foi útil?",
            ["Sim", "Não"],
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
            "nivel_risco": response["nivel_risco"],
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
            st.error(f"Erro ao enviar feedback pela API: {error}")


st.divider()

st.write("## 📚 Histórico individual")

st.caption(
    "Consulte diagnósticos anteriores pelo nome do usuário. "
    "Essa área usa a FastAPI para buscar dados salvos no PostgreSQL."
)

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
            st.success(f"{len(historico)} diagnóstico(s) encontrado(s).")

            historico_ordenado = sorted(
                historico,
                key=lambda item: item["id"],
            )

            score_data = {
                item["id"]: item["score_financeiro"]
                for item in historico_ordenado
            }

            st.write("### Evolução do score")
            st.line_chart(score_data)

            st.write("### Diagnósticos encontrados")

            for item in historico:
                with st.expander(
                    f"ID {item['id']} — {item['nome']} — Score {item['score_financeiro']}/100 — Risco {item['nivel_risco']}"
                ):
                    st.write(f"**Saldo estimado:** R$ {item['saldo_estimado']:.2f}")
                    st.write(f"**Comprometimento da renda:** {item['comprometimento_renda_percentual']:.2f}%")
                    st.write(f"**Meses de reserva:** {item['meses_reserva_estimados']:.2f}")
                    st.write(f"**Objetivo:** {item.get('objetivo', '')}")

                    st.write("**Diagnóstico:**")
                    st.write(item["diagnostico"])

                    try:
                        pdf_antigo = baixar_relatorio_pdf_api(item["id"])

                        st.download_button(
                            label=f"📄 Baixar PDF do diagnóstico {item['id']}",
                            data=pdf_antigo,
                            file_name=f"relatorio_inna_{item['nome'].replace(' ', '_').lower()}_{item['id']}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_historico_{item['id']}",
                        )
                    except Exception as error:
                        st.warning(f"Não foi possível gerar PDF do histórico: {error}")

    except Exception as error:
        st.error(f"Erro ao buscar histórico pela API: {error}")
