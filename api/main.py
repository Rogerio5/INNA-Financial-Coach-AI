from fastapi import FastAPI

from api.schemas import (
    FeedbackInput,
    FeedbackResponse,
    FinancialInput,
    FinancialResponse,
)
from src.financial_engine import build_financial_diagnosis
from src.gemini_client import generate_ai_plan
from src.repository import save_diagnostico_db, save_feedback_db


app = FastAPI(
    title="INNA Financial Coach AI API",
    description="API para diagnóstico financeiro com IA Generativa, Gemini e PostgreSQL.",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "INNA Financial Coach AI API is running",
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

    save_diagnostico_db(payload_dict, response)

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
