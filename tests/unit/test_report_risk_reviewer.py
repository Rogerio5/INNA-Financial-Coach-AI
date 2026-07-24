from __future__ import annotations

from src.agents.risk_reviewer import (
    apply_risk_review_to_report,
    review_financial_report,
)


def _valid_report():
    return {
        "report_version": "1.0",
        "titulo": (
            "Relatório Financeiro INNA"
        ),
        "idioma": "pt",
        "possui_diagnostico": True,
        "total_diagnosticos": 1,
        "indicadores_oficiais": {
            "data_hora": (
                "2026-07-22T01:00:00"
            ),
            "saldo_estimado": 800.0,
            "comprometimento_renda_percentual": (
                65.5
            ),
            "meses_reserva_estimados": 2.4,
            "score_financeiro": 72,
            "nivel_risco": "Medio",
            "moeda": "BRL",
            "idioma": "pt",
        },
        "historico": [],
        "resumo_executivo": (
            "Relatório preparado com os "
            "dados financeiros oficiais."
        ),
        "recomendacoes": [
            (
                "Considere fortalecer gradualmente "
                "a reserva financeira."
            )
        ],
        "proximos_passos": [
            (
                "Revise o orçamento novamente "
                "no próximo mês."
            )
        ],
        "financial_values_recalculated": False,
        "ready_for_risk_review": True,
        "ready_for_pdf_rendering": False,
    }


def test_approves_valid_official_report():
    decision = review_financial_report(
        _valid_report()
    )

    assert decision.approved
    assert decision.blocking_findings == 0
    assert (
        decision.reason
        == "risk_review_approved"
    )


def test_blocks_recalculated_financial_values():
    report = _valid_report()

    report[
        "financial_values_recalculated"
    ] = True

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "financial_values_recalculated"
        for item in decision.findings
    )


def test_blocks_missing_official_indicators():
    report = _valid_report()

    report["indicadores_oficiais"] = None

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "official_indicators_missing"
        for item in decision.findings
    )


def test_blocks_score_out_of_range():
    report = _valid_report()

    report[
        "indicadores_oficiais"
    ]["score_financeiro"] = 150

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "financial_score_out_of_range"
        for item in decision.findings
    )


def test_warns_income_commitment_above_100():
    report = _valid_report()

    report[
        "indicadores_oficiais"
    ][
        "comprometimento_renda_percentual"
    ] = 120.0

    decision = review_financial_report(
        report
    )

    assert decision.approved
    assert decision.warning_findings == 1

    assert any(
        item.code
        == "income_commitment_above_100"
        for item in decision.findings
    )


def test_blocks_negative_reserve_months():
    report = _valid_report()

    report[
        "indicadores_oficiais"
    ][
        "meses_reserva_estimados"
    ] = -1.0

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "negative_reserve_months"
        for item in decision.findings
    )


def test_blocks_prohibited_financial_promise():
    report = _valid_report()

    report["recomendacoes"] = [
        (
            "Este investimento oferece "
            "retorno garantido."
        )
    ]

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "prohibited_financial_promise"
        for item in decision.findings
    )


def test_blocks_contradictory_recommendations():
    report = _valid_report()

    report["recomendacoes"] = [
        "Assuma novas dívidas.",
        "Evite novas dívidas.",
    ]

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "contradictory_recommendations"
        for item in decision.findings
    )


def test_blocks_report_without_diagnosis():
    report = _valid_report()

    report["possui_diagnostico"] = False
    report["indicadores_oficiais"] = None
    report["total_diagnosticos"] = 0

    decision = review_financial_report(
        report
    )

    assert not decision.approved

    assert any(
        item.code
        == "no_financial_diagnosis"
        for item in decision.findings
    )


def test_apply_review_releases_pdf_only_when_approved():
    approved = apply_risk_review_to_report(
        _valid_report()
    )

    assert approved[
        "risk_review_approved"
    ]

    assert approved[
        "ready_for_pdf_rendering"
    ]

    invalid_report = _valid_report()

    invalid_report[
        "financial_values_recalculated"
    ] = True

    blocked = apply_risk_review_to_report(
        invalid_report
    )

    assert not blocked[
        "risk_review_approved"
    ]

    assert not blocked[
        "ready_for_pdf_rendering"
    ]


def test_invalid_payload_is_blocked():
    decision = review_financial_report(
        None
    )

    assert not decision.approved

    assert any(
        item.code
        == "invalid_report_payload"
        for item in decision.findings
    )
