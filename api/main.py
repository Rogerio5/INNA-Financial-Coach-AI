from api.telegram_webhook import router as telegram_router
from fastapi import FastAPI, HTTPException, Query, Response
from api.schemas import DiagnosticoItem, EmailRequest, FeedbackInput, FeedbackItem, FeedbackResponse, FinancialInput, FinancialResponse

from src.financial_engine import build_financial_diagnosis
from src.gemini_client import generate_ai_plan
from src.pdf_report import gerar_relatorio_pdf
from src.email_sender import send_diagnostico_email
from src.repository import (
    get_diagnostico_by_id_db,
    list_diagnosticos_by_nome_db,
    list_diagnosticos_db,
    list_feedbacks_db,
    save_diagnostico_db,
    save_feedback_db,
)




def format_money_br(value) -> str:
    try:
        number = float(str(value).replace(",", "."))
    except Exception:
        number = 0.0

    formatted = f"R$ {number:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


app = FastAPI(
    title="INNA Financial Coach AI API",
    description="API para diagnóstico financeiro com IA Generativa, Gemini e PostgreSQL.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "INNA Financial Coach AI API is running",
    }




@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "INNA Financial Coach AI",
        "message": "API online e pronta para receber requisições."
    }


@app.post("/diagnostico", response_model=FinancialResponse)
def gerar_diagnostico(payload: FinancialInput):
    payload_dict = payload.model_dump()

    diagnosis = build_financial_diagnosis(payload_dict)
    ai_plan = generate_ai_plan(payload_dict, diagnosis)

    response = {
        **diagnosis,
        "nome": payload_dict["nome"],
        "plano_30_dias": ai_plan,
    }

    diagnostico_id = save_diagnostico_db(payload_dict, response)
    response["id"] = diagnostico_id

    return response


@app.post("/feedback", response_model=FeedbackResponse)
def registrar_feedback(payload: FeedbackInput):
    payload_dict = payload.model_dump()

    save_feedback_db(
        nome=payload_dict["nome"],
        util=payload_dict["util"],
        comentario=payload_dict["comentario"],
        score_financeiro=payload_dict["score_financeiro"],
        nivel_risco=payload_dict["nivel_risco"],
    )

    return {
        "status": "success",
        "message": "Feedback registrado com sucesso no PostgreSQL.",
    }


@app.get("/diagnosticos", response_model=list[DiagnosticoItem])
def listar_diagnosticos(limit: int = Query(default=50, ge=1, le=200)):
    return list_diagnosticos_db(limit=limit)


@app.get("/feedbacks", response_model=list[FeedbackItem])
def listar_feedbacks(limit: int = Query(default=50, ge=1, le=200)):
    return list_feedbacks_db(limit=limit)


@app.get("/diagnosticos/{diagnostico_id}/relatorio")
def baixar_relatorio_diagnostico(diagnostico_id: int):
    diagnostico = get_diagnostico_by_id_db(diagnostico_id)

    if diagnostico is None:
        raise HTTPException(
            status_code=404,
            detail="Diagnóstico não encontrado.",
        )

    pdf_bytes = gerar_relatorio_pdf(diagnostico)

    nome = str(diagnostico.get("nome", "usuario"))
    nome_arquivo = nome.strip().lower().replace(" ", "_")
    filename = f"relatorio_inna_{nome_arquivo}_{diagnostico_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@app.get("/diagnosticos/usuario/{nome}", response_model=list[DiagnosticoItem])
def listar_diagnosticos_por_usuario(
    nome: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    return list_diagnosticos_by_nome_db(nome=nome, limit=limit)


app.include_router(telegram_router)


@app.post("/diagnosticos/{diagnostico_id}/enviar-email")
def enviar_diagnostico_por_email(diagnostico_id: int, payload: EmailRequest):
    diagnostico = get_diagnostico_by_id_db(diagnostico_id)

    if not diagnostico:
        raise HTTPException(status_code=404, detail="Diagnóstico não encontrado.")

    if "@" not in payload.email or "." not in payload.email:
        raise HTTPException(status_code=400, detail="E-mail inválido.")

    try:
        pdf_bytes = gerar_relatorio_pdf(diagnostico)

        nome = diagnostico.get("nome", "usuário")
        saldo = (
            diagnostico.get("saldo_estimado")
            or diagnostico.get("saldo_mensal_estimado")
            or diagnostico.get("saldo_mensal")
            or diagnostico.get("saldo")
            or 0
        )
        risco = diagnostico.get("nivel_risco", diagnostico.get("risco", "não informado"))
        saldo_formatado = format_money_br(saldo)

        subject = "Seu diagnóstico financeiro INNA"

        body = f"""Olá, {nome}.

Segue em anexo seu relatório financeiro gerado pela INNA Financial Coach AI.

Resumo do diagnóstico:
- Saldo mensal estimado: {saldo_formatado}
- Nível de risco: {risco}

A INNA ajuda você a entender sua renda, gastos, dívidas, reserva financeira e próximos passos para organizar sua vida financeira.

Você também pode acompanhar seus diagnósticos pelo app web, dashboard e Telegram.

Atenciosamente,
INNA Financial Coach AI
"""

        send_diagnostico_email(
            to_email=payload.email,
            subject=subject,
            body=body,
            pdf_bytes=pdf_bytes,
            filename=f"relatorio-inna-{diagnostico_id}.pdf",
        )

        return {
            "success": True,
            "message": "Relatório enviado por e-mail com sucesso.",
            "email": payload.email,
            "diagnostico_id": diagnostico_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar e-mail: {str(exc)}",
        )
