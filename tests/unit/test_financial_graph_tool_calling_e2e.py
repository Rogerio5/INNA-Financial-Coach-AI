from __future__ import annotations

from unittest.mock import patch

from src.agent_tools.core import (
    ToolError,
    ToolResult,
    ToolStatus,
)
from src.agent_tools.financial_tools import (
    FINANCIAL_DIAGNOSIS_TOOL_NAME,
)
from src.agents.graph import (
    executar_nucleo_inna,
)


COMPLETE_FINANCIAL_MESSAGE = (
    "Renda: 4000; Gastos fixos: 2000; Gastos variáveis: 500; Dívidas: 300; Reserva: 0"
)


def _success_result() -> ToolResult:
    return ToolResult(
        call_id="financial-e2e-success",
        tool_name=(FINANCIAL_DIAGNOSIS_TOOL_NAME),
        status=ToolStatus.SUCCESS,
        output={
            "renda_mensal": 4000.0,
            "gastos_fixos": 2000.0,
            "gastos_variaveis": 500.0,
            "dividas_mensais": 300.0,
            "reserva_atual": 0.0,
            "moeda": "BRL",
            "idioma": "pt",
            "gastos_incluem_dividas": False,
            "despesas_totais": 2800.0,
            "saldo_estimado": 1200.0,
            "comprometimento_renda_percentual": 70.0,
            "meses_reserva_estimados": 0.0,
            "score_financeiro": 70,
            "nivel_risco": "Medio",
            "situacao": "saldo_positivo",
            "tem_saldo_positivo": True,
            "parcelas_adicionais_consideradas": 300.0,
            "base_calculo": (
                "As parcelas de dívidas foram acrescentadas separadamente."
            ),
            "versao_regra": ("financial_engine_v1+budget_tool_v1"),
        },
        duration_ms=2.0,
    )


def test_complete_message_reaches_formal_financial_tool():
    captured_calls = []

    def fake_execute(call):
        captured_calls.append(call)
        return _success_result()

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        side_effect=fake_execute,
    ):
        result = executar_nucleo_inna(
            COMPLETE_FINANCIAL_MESSAGE,
            usuario_id="user-e2e",
            idioma="pt",
            moeda="BRL",
        )

    assert result["next_node"] == ("financial_agent")

    assert len(captured_calls) == 1

    call = captured_calls[0]

    assert call.tool_name == (FINANCIAL_DIAGNOSIS_TOOL_NAME)

    assert call.context.requested_by == "financial_agent"

    assert call.arguments == {
        "renda_mensal": 4000.0,
        "gastos_fixos": 2000.0,
        "gastos_variaveis": 500.0,
        "dividas_mensais": 300.0,
        "reserva_atual": 0.0,
        "gastos_incluem_dividas": False,
        "moeda": "BRL",
        "idioma": "pt",
    }

    diagnosis = result["structured_response"]["diagnostico_financeiro"]

    assert diagnosis["saldo_estimado"] == 1200.0

    assert diagnosis["score_financeiro"] == 70

    assert diagnosis["nivel_risco"] == "Medio"

    assert "Score financeiro: 70/100" in result["response"]

    stored_result = result["tool_results"][0]

    assert stored_result["status"] == ("success")

    # Dados financeiros completos não devem ser
    # duplicados no histórico técnico da ferramenta.
    assert "output" not in stored_result
    assert "saldo_estimado" not in stored_result

    assert "tool:calcular_diagnostico_financeiro:success" in result["trace"]

    assert "agent:financial_agent" in result["trace"]

    assert result["trace"][-1].startswith("conversation_summary_node:")


def test_incomplete_message_does_not_execute_tool():
    """
    Renda e gasto agregado não são suficientes para
    dividir gastos fixos e variáveis com segurança.
    """
    with patch("src.agents.nodes.executar_ferramenta_inna") as mock_execute:
        result = executar_nucleo_inna(
            ("Tenho renda de 3000 e gasto 2500 por mês."),
            usuario_id="user-e2e",
            idioma="pt",
            moeda="BRL",
        )

    assert result["next_node"] == ("financial_agent")

    mock_execute.assert_not_called()

    resolution = result["structured_response"]["financial_input_resolution"]

    assert resolution["ready"] is False

    assert "gastos_fixos" in (resolution["missing_fields"])

    assert "gastos_variaveis" in (resolution["missing_fields"])

    assert "financial_input:incomplete" in result["trace"]


def test_financial_timeout_is_handled_safely():
    timeout_result = ToolResult(
        call_id="financial-e2e-timeout",
        tool_name=(FINANCIAL_DIAGNOSIS_TOOL_NAME),
        status=ToolStatus.TIMEOUT,
        output=None,
        error=ToolError(
            code="tool_timeout",
            message=("A ferramenta excedeu o tempo máximo de execução."),
            retryable=True,
            details={
                "timeout_seconds": 2.0,
            },
        ),
        duration_ms=2000.0,
    )

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=timeout_result,
    ):
        result = executar_nucleo_inna(
            COMPLETE_FINANCIAL_MESSAGE,
            usuario_id="user-e2e",
            idioma="pt",
            moeda="BRL",
        )

    assert result["response"] == (
        "Não foi possível calcular o diagnóstico financeiro neste momento."
    )

    stored_result = result["tool_results"][0]

    assert stored_result["status"] == ("timeout")

    assert stored_result["error_code"] == "tool_timeout"

    assert stored_result["retryable"] is True

    assert "tool:calcular_diagnostico_financeiro:timeout" in result["trace"]

    assert "agent:financial_agent:error" in result["trace"]
