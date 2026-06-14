from src.config import INNA_MOCK_MODE, GEMINI_API_KEY, GEMINI_MODEL
from src.prompts import SYSTEM_PROMPT, build_plan_prompt


def generate_ai_plan(user_data: dict, diagnosis: dict) -> str:
    if INNA_MOCK_MODE or not GEMINI_API_KEY:
        return generate_mock_plan(diagnosis)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = SYSTEM_PROMPT + "\n\n" + build_plan_prompt(user_data, diagnosis)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        return response.text
    except Exception as exc:
        return (
            "Não consegui gerar o plano com IA neste momento. "
            f"Erro técnico: {exc}. "
            "Use o modo Mock para testes locais."
        )


def generate_mock_plan(diagnosis: dict) -> str:
    risco = diagnosis.get("nivel_risco", "Médio")
    saldo = diagnosis.get("saldo_estimado", 0)
    score = diagnosis.get("score_financeiro", 50)

    return f'''
Plano de ação de 30 dias da INNA

Resumo:
Seu nível de risco financeiro atual é {risco}, com score financeiro de {score}/100.
Seu saldo mensal estimado é de R$ {saldo:.2f}.

Semana 1 — Clareza:
Liste todos os gastos fixos, variáveis e dívidas. Separe o que é essencial do que pode ser reduzido.

Semana 2 — Controle:
Defina um limite de gastos variáveis para os próximos 15 dias. Evite novas dívidas nesse período.

Semana 3 — Reserva:
Separe um pequeno valor para iniciar ou reforçar sua reserva de emergência, mesmo que seja pouco.

Semana 4 — Plano:
Revise o que funcionou, ajuste os gastos e defina uma meta simples para o próximo mês.

Próximo passo:
Continue acompanhando seu saldo, gastos e evolução toda semana.
'''
