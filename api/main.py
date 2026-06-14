from fastapi import FastAPI
from api.schemas import FinancialInput, FinancialResponse
from src.financial_engine import build_financial_diagnosis
from src.gemini_client import generate_ai_plan
from src.logger import save_interaction

app = FastAPI(
    title="INNA Financial Coach AI",
    description="API de diagnóstico financeiro educativo com IA Generativa.",
    version="0.1.0",
)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "app": "INNA Financial Coach AI",
        "message": "API funcionando com sucesso.",
    }


@app.post("/diagnostico", response_model=FinancialResponse)
def diagnostico(payload: FinancialInput):
    diagnosis = build_financial_diagnosis(payload.model_dump())
    ai_plan = generate_ai_plan(payload.model_dump(), diagnosis)

    response = {
        **diagnosis,
        "nome": payload.nome,
        "diagnostico": diagnosis["diagnostico"],
        "plano_30_dias": ai_plan,
    }

    save_interaction(payload.model_dump(), response)
    return response
