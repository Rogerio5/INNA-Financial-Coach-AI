def build_financial_diagnosis(data: dict) -> dict:
    renda = float(data.get("renda_mensal", 0))
    gastos_fixos = float(data.get("gastos_fixos", 0))
    gastos_variaveis = float(data.get("gastos_variaveis", 0))
    dividas = float(data.get("dividas_mensais", 0))
    reserva = float(data.get("reserva_atual", 0))

    total_gastos = gastos_fixos + gastos_variaveis + dividas
    saldo = renda - total_gastos

    if renda > 0:
        comprometimento = (total_gastos / renda) * 100
    else:
        comprometimento = 0

    if total_gastos > 0:
        meses_reserva = reserva / total_gastos
    else:
        meses_reserva = 0

    score = 100

    if saldo < 0:
        score -= 35
    elif saldo < renda * 0.1:
        score -= 20

    if comprometimento > 90:
        score -= 30
    elif comprometimento > 70:
        score -= 20
    elif comprometimento > 50:
        score -= 10

    if meses_reserva < 1:
        score -= 20
    elif meses_reserva < 3:
        score -= 10

    score = max(0, min(100, int(score)))

    if score >= 75:
        risco = "Baixo"
    elif score >= 50:
        risco = "Médio"
    else:
        risco = "Alto"

    diagnostico = (
        f"Seu saldo estimado mensal é de R$ {saldo:.2f}. "
        f"O comprometimento da renda está em {comprometimento:.1f}%. "
        f"Sua reserva cobre aproximadamente {meses_reserva:.1f} meses dos gastos atuais. "
        f"O nível de risco financeiro foi classificado como {risco}."
    )

    return {
        "saldo_estimado": round(saldo, 2),
        "comprometimento_renda_percentual": round(comprometimento, 2),
        "meses_reserva_estimados": round(meses_reserva, 2),
        "score_financeiro": score,
        "nivel_risco": risco,
        "diagnostico": diagnostico,
    }
