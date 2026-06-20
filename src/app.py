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

st.title("💰 INNA Financial Coach AI")

if not verificar_api_online():
    st.error(
        "A API da INNA está offline. "
        "Abra outro terminal e rode: python -m uvicorn api.main:app --reload --port 8000"
    )
    st.stop()

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

    try:
        with st.spinner("Chamando a API da INNA e gerando diagnóstico com IA..."):
            response = gerar_diagnostico_api(payload)

        st.session_state.last_payload = payload
        st.session_state.last_response = response

        st.success("Diagnóstico gerado e salvo via FastAPI com sucesso!")

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
    diagnostico_formatado = response["diagnostico"].replace("$", "\\$")
    st.markdown(diagnostico_formatado)

    st.write("### Plano de ação de 30 dias")
    plano_formatado = response["plano_30_dias"].replace("$", "\\$")
    st.markdown(plano_formatado)

    st.divider()

    diagnostico_id = response.get("id")

    if diagnostico_id:
        try:
            pdf_bytes = baixar_relatorio_pdf_api(diagnostico_id)

            st.download_button(
                label="📄 Baixar relatório em PDF",
                data=pdf_bytes,
                file_name=f"relatorio_inna_{response['nome'].replace(' ', '_').lower()}_{diagnostico_id}.pdf",
                mime="application/pdf",
            )

        except Exception as error:
            st.warning(f"Não foi possível baixar o relatório pela API: {error}")

        st.markdown("### 📧 Receber relatório por e-mail")

        email_destino = st.text_input(
            "Digite seu e-mail para receber o relatório PDF:",
            placeholder="seuemail@gmail.com",
            key=f"email_destino_{diagnostico_id}",
        )

        if st.button("📧 Enviar relatório por e-mail", key=f"btn_email_{diagnostico_id}"):
            if not email_destino or "@" not in email_destino or "." not in email_destino:
                st.warning("Digite um e-mail válido.")
            else:
                try:
                    enviar_relatorio_email(diagnostico_id, email_destino)
                    st.success("Relatório enviado por e-mail com sucesso!")
                except Exception as error:
                    st.error(f"Erro ao enviar relatório por e-mail: {error}")

    else:
        st.warning("Relatório PDF indisponível: diagnóstico ainda não possui ID retornado pela API.")


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
        feedback_payload = {
            "nome": response["nome"],
            "util": util,
            "comentario": comentario,
            "score_financeiro": response["score_financeiro"],
            "nivel_risco": response["nivel_risco"],
        }

        try:
            enviar_feedback_api(feedback_payload)
            st.success("Feedback registrado via FastAPI com sucesso. Obrigado por ajudar a evoluir a INNA!")

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
        "Nome para buscar histórico",
        value="Ronaldo",
    )

    limite_historico = st.number_input(
        "Quantidade máxima de registros",
        min_value=1,
        max_value=20,
        value=10,
        step=1,
    )

    buscar_historico = st.form_submit_button("Buscar histórico")

if buscar_historico:
    try:
        historico = buscar_historico_usuario_api(
            nome=nome_historico,
            limit=int(limite_historico),
        )

        if not historico:
            st.warning("Nenhum diagnóstico encontrado para esse nome.")
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
