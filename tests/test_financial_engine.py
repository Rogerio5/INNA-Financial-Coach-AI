from src.financial_engine import build_financial_diagnosis


def test_financial_diagnosis_positive_balance():
    data = {
        "renda_mensal": 4000,
        "gastos_fixos": 1500,
        "gastos_variaveis": 800,
        "dividas_mensais": 200,
        "reserva_atual": 5000,
    }

    result = build_financial_diagnosis(data)

    assert result["saldo_estimado"] == 1500
    assert result["score_financeiro"] > 0
    assert result["nivel_risco"] in ["Baixo", "Médio", "Alto"]


def test_financial_diagnosis_negative_balance():
    data = {
        "renda_mensal": 2000,
        "gastos_fixos": 1500,
        "gastos_variaveis": 800,
        "dividas_mensais": 500,
        "reserva_atual": 0,
    }

    result = build_financial_diagnosis(data)

    assert result["saldo_estimado"] < 0
    assert result["nivel_risco"] == "Alto"
