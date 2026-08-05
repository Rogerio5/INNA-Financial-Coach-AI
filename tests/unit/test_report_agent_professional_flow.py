from __future__ import annotations

from unittest.mock import patch

from src.agent_tools.core import (
    ToolError,
    ToolResult,
    ToolStatus,
)
from src.agents.nodes import (
    report_agent_node,
)
from src.agents.report_flow import (
    executar_fluxo_relatorio,
)


def _base_state():
    return {
        "user_message": ("Quero gerar meu relatório."),
        "user_id": "user-report-flow",
        "language": "pt",
        "currency": "BRL",
        "thread_id": "thread-report-flow",
        "trace_id": "trace-report-flow",
        "intent": "relatorio",
        "route_source": "rule",
        "conversation_history": [],
        "structured_response": {},
        "tool_results": [],
        "errors": [],
        "trace": [],
    }


def _success_result(
    *,
    call_id: str,
    tool_name: str,
    output: dict,
) -> ToolResult:
    return ToolResult(
        call_id=call_id,
        tool_name=tool_name,
        status=ToolStatus.SUCCESS,
        output=output,
        error=None,
        duration_ms=5,
    )


def test_report_flow_requires_trusted_identity():
    state = _base_state()
    state["user_id"] = None

    result = executar_fluxo_relatorio(state)

    assert "identidade autenticada" in result["response"].lower()

    assert "trusted_user_identity_missing" in result["errors"]

    assert "report:missing_user_identity" in result["trace"]


@patch("src.agents.report_flow.executar_ferramenta_inna")
def test_report_flow_prepares_official_report(
    execute_mock,
):
    history_result = _success_result(
        call_id="history-call",
        tool_name=("consultar_historico_financeiro"),
        output={
            "possui_historico": True,
            "total_retornado": 1,
            "diagnosticos": [
                {
                    "data_hora": ("2026-07-22T01:00:00"),
                    "saldo_estimado": 800.0,
                    "comprometimento_renda_percentual": (65.5),
                    "meses_reserva_estimados": 2.4,
                    "score_financeiro": 72,
                    "nivel_risco": "Medio",
                    "moeda": "BRL",
                    "idioma": "pt",
                }
            ],
        },
    )

    preparation_result = _success_result(
        call_id="prepare-call",
        tool_name=("preparar_relatorio_financeiro"),
        output={
            "report_version": "1.0",
            "titulo": ("Relatório Financeiro INNA"),
            "idioma": "pt",
            "possui_diagnostico": True,
            "total_diagnosticos": 1,
            "indicadores_oficiais": {
                "saldo_estimado": 800.0,
                "score_financeiro": 72,
            },
            "historico": [],
            "resumo_executivo": ("Relatório preparado."),
            "recomendacoes": [],
            "proximos_passos": [],
            "financial_values_recalculated": False,
            "ready_for_risk_review": True,
            "ready_for_pdf_rendering": False,
        },
    )

    execute_mock.side_effect = [
        history_result,
        preparation_result,
    ]

    result = executar_fluxo_relatorio(_base_state())

    assert execute_mock.call_count == 2

    assert "aprovado pela revisão de risco" in result["response"].lower()

    report = result["structured_response"]["financial_report"]

    assert report["financial_values_recalculated"] is False

    assert report["ready_for_risk_review"]

    assert report["risk_review_approved"]

    assert report["ready_for_pdf_rendering"]

    assert result["structured_response"]["risk_review"]["approved"]

    assert "risk_reviewer:approved" in result["trace"]

    assert result["tool_results"][0]["ok"] is True

    assert result["tool_results"][1]["ok"] is True

    assert "agent:report_agent" in result["trace"]


@patch("src.agents.report_flow.executar_ferramenta_inna")
def test_report_flow_handles_empty_history(
    execute_mock,
):
    execute_mock.side_effect = [
        _success_result(
            call_id="history-empty",
            tool_name=("consultar_historico_financeiro"),
            output={
                "possui_historico": False,
                "total_retornado": 0,
                "diagnosticos": [],
            },
        ),
        _success_result(
            call_id="prepare-empty",
            tool_name=("preparar_relatorio_financeiro"),
            output={
                "report_version": "1.0",
                "titulo": ("Relatório Financeiro INNA"),
                "idioma": "pt",
                "possui_diagnostico": False,
                "total_diagnosticos": 0,
                "indicadores_oficiais": None,
                "historico": [],
                "resumo_executivo": ("Ainda não existem diagnósticos."),
                "recomendacoes": [],
                "proximos_passos": [],
                "financial_values_recalculated": False,
                "ready_for_risk_review": True,
                "ready_for_pdf_rendering": False,
            },
        ),
    ]

    result = executar_fluxo_relatorio(_base_state())

    assert "ainda não existem diagnósticos" in result["response"].lower()


@patch("src.agents.report_flow.executar_ferramenta_inna")
def test_report_flow_handles_history_failure(
    execute_mock,
):
    execute_mock.return_value = ToolResult(
        call_id="history-error",
        tool_name=("consultar_historico_financeiro"),
        status=ToolStatus.ERROR,
        output=None,
        error=ToolError(
            code="history_query_failed",
            message="Falha controlada.",
            retryable=True,
            details={},
        ),
        duration_ms=4,
    )

    result = executar_fluxo_relatorio(_base_state())

    assert execute_mock.call_count == 1

    assert "não foi possível consultar" in result["response"].lower()

    assert "history_query_failed" in result["errors"]


@patch("src.agents.report_flow.executar_ferramenta_inna")
def test_report_flow_handles_preparation_failure(
    execute_mock,
):
    execute_mock.side_effect = [
        _success_result(
            call_id="history-success",
            tool_name=("consultar_historico_financeiro"),
            output={
                "possui_historico": True,
                "total_retornado": 1,
                "diagnosticos": [
                    {
                        "saldo_estimado": 500.0,
                        "score_financeiro": 65,
                    }
                ],
            },
        ),
        ToolResult(
            call_id="prepare-error",
            tool_name=("preparar_relatorio_financeiro"),
            status=ToolStatus.ERROR,
            output=None,
            error=ToolError(
                code="report_preparation_failed",
                message="Falha controlada.",
                retryable=False,
                details={},
            ),
            duration_ms=3,
        ),
    ]

    result = executar_fluxo_relatorio(_base_state())

    assert "não foi possível preparar" in result["response"].lower()

    assert "report_preparation_failed" in result["errors"]


@patch("src.agents.report_flow.executar_ferramenta_inna")
def test_report_node_uses_professional_flow(
    execute_mock,
):
    execute_mock.side_effect = [
        _success_result(
            call_id="history-node",
            tool_name=("consultar_historico_financeiro"),
            output={
                "possui_historico": False,
                "total_retornado": 0,
                "diagnosticos": [],
            },
        ),
        _success_result(
            call_id="prepare-node",
            tool_name=("preparar_relatorio_financeiro"),
            output={
                "report_version": "1.0",
                "titulo": ("Relatório Financeiro INNA"),
                "idioma": "pt",
                "possui_diagnostico": False,
                "total_diagnosticos": 0,
                "indicadores_oficiais": None,
                "historico": [],
                "resumo_executivo": ("Sem diagnósticos."),
                "recomendacoes": [],
                "proximos_passos": [],
                "financial_values_recalculated": False,
                "ready_for_risk_review": True,
                "ready_for_pdf_rendering": False,
            },
        ),
    ]

    result = report_agent_node(_base_state())

    assert result["structured_response"]["financial_report"]

    assert "Integrar gerar_relatorio_pdf" not in str(result)


@patch("src.agents.report_flow.executar_ferramenta_inna")
def test_report_flow_blocks_pdf_when_risk_review_fails(
    execute_mock,
):
    execute_mock.side_effect = [
        _success_result(
            call_id="history-risk-block",
            tool_name=("consultar_historico_financeiro"),
            output={
                "possui_historico": True,
                "total_retornado": 1,
                "diagnosticos": [
                    {
                        "saldo_estimado": 500.0,
                        "score_financeiro": 65,
                        "nivel_risco": "Medio",
                    }
                ],
            },
        ),
        _success_result(
            call_id="prepare-risk-block",
            tool_name=("preparar_relatorio_financeiro"),
            output={
                "report_version": "1.0",
                "titulo": ("Relatório Financeiro INNA"),
                "idioma": "pt",
                "possui_diagnostico": True,
                "total_diagnosticos": 1,
                "indicadores_oficiais": {
                    "saldo_estimado": 500.0,
                    "score_financeiro": 65,
                    "nivel_risco": "Medio",
                },
                "historico": [],
                "resumo_executivo": ("Resultado garantido para o usuário."),
                "recomendacoes": [],
                "proximos_passos": [],
                "financial_values_recalculated": False,
                "ready_for_risk_review": True,
                "ready_for_pdf_rendering": False,
            },
        ),
    ]

    result = executar_fluxo_relatorio(_base_state())

    report = result["structured_response"]["financial_report"]

    assert not report["risk_review_approved"]

    assert not report["ready_for_pdf_rendering"]

    assert "impedem sua liberação para pdf" in result["response"].lower()

    assert "risk_reviewer:blocked" in result["trace"]
