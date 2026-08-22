from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import patch

from src.agent_tools.core import (
    ToolError,
    ToolResult,
    ToolStatus,
)
from src.agent_tools.financial_tools import (
    FINANCIAL_DIAGNOSIS_TOOL_NAME,
)
from src.agents.nodes import (
    financial_agent_node,
)


def _complete_state() -> dict:
    return {
        "user_message": (
            "Quero analisar minhas finanças."
        ),
        "financial_inputs": {
            "renda_mensal": 4000,
            "gastos_fixos": 2000,
            "gastos_variaveis": 500,
            "dividas_mensais": 300,
            "reserva_atual": 0,
        },
        "language": "pt",
        "currency": "BRL",
        "user_id": "user-test",
        "thread_id": "thread-test",
        "trace_id": "trace-test",
        "intent": "diagnostico_financeiro",
        "confidence": 0.90,
        "trace": [],
        "errors": [],
        "tool_results": [],
        "structured_response": {},
    }


def _success_result() -> ToolResult:
    return ToolResult(
        call_id="financial-call-success",
        tool_name=(
            FINANCIAL_DIAGNOSIS_TOOL_NAME
        ),
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
                "As parcelas de dívidas foram "
                "acrescentadas separadamente."
            ),
            "versao_regra": (
                "financial_engine_v1+"
                "budget_tool_v1"
            ),
        },
        duration_ms=2.5,
    )


def test_incomplete_data_does_not_execute_tool():
    state = {
        "financial_inputs": {
            "renda_mensal": 3000,
        },
        "intent": "diagnostico_financeiro",
        "trace": [],
        "errors": [],
        "tool_results": [],
        "structured_response": {},
    }

    with patch(
        "src.agents.nodes."
        "executar_ferramenta_inna"
    ) as mock_execute:
        result = financial_agent_node(
            state
        )

    mock_execute.assert_not_called()

    resolution = result[
        "structured_response"
    ]["financial_input_resolution"]

    assert resolution["ready"] is False

    assert "gastos_fixos" in (
        resolution["missing_fields"]
    )

    assert (
        "financial_input:incomplete"
        in result["trace"]
    )

    assert (
        result["trace"][-1]
        == "agent:financial_agent"
    )


def test_complete_data_executes_formal_tool():
    captured = {}

    def fake_execute(call):
        captured["call"] = call
        return _success_result()

    with patch(
        "src.agents.nodes."
        "executar_ferramenta_inna",
        side_effect=fake_execute,
    ):
        result = financial_agent_node(
            _complete_state()
        )

    call = captured["call"]

    assert call.tool_name == (
        FINANCIAL_DIAGNOSIS_TOOL_NAME
    )

    assert (
        call.context.requested_by
        == "financial_agent"
    )

    assert call.context.user_id == (
        "user-test"
    )

    assert call.context.session_id == (
        "thread-test"
    )

    assert call.arguments[
        "renda_mensal"
    ] == 4000

    assert result["response"].startswith(
        "Diagnóstico financeiro calculado"
    )

    diagnosis = result[
        "structured_response"
    ]["diagnostico_financeiro"]

    assert diagnosis[
        "saldo_estimado"
    ] == 1200.0

    assert diagnosis[
        "score_financeiro"
    ] == 70

    stored_result = result[
        "tool_results"
    ][0]

    assert stored_result["status"] == (
        "success"
    )

    # Evita duplicar dados financeiros sensíveis
    # dentro do histórico técnico da ferramenta.
    assert "output" not in stored_result
    assert "saldo_estimado" not in (
        stored_result
    )

    assert (
        "tool:calcular_diagnostico_financeiro:"
        "success"
        in result["trace"]
    )


def test_financial_tool_error_is_safe():
    failure = ToolResult(
        call_id="financial-call-error",
        tool_name=(
            FINANCIAL_DIAGNOSIS_TOOL_NAME
        ),
        status=ToolStatus.ERROR,
        output=None,
        error=ToolError(
            code="tool_execution_error",
            message=(
                "A ferramenta falhou durante "
                "a execução."
            ),
            retryable=False,
        ),
        duration_ms=3.0,
    )

    with patch(
        "src.agents.nodes."
        "executar_ferramenta_inna",
        return_value=failure,
    ):
        result = financial_agent_node(
            _complete_state()
        )

    assert result["response"] == (
        "Não foi possível calcular o "
        "diagnóstico financeiro neste momento."
    )

    assert result["tool_results"][0][
        "error_code"
    ] == "tool_execution_error"

    assert result["errors"] == [
        (
            "A ferramenta falhou durante "
            "a execução."
        )
    ]

    assert (
        "agent:financial_agent:error"
        in result["trace"]
    )


def test_agent_node_does_not_call_financial_engines_directly():
    source = Path(
        "src/agents/nodes.py"
    ).read_text(
        encoding="utf-8",
    )

    tree = ast.parse(source)

    imported_names: set[str] = set()
    called_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(
                    alias.asname or alias.name
                )

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                called_names.add(
                    node.func.attr
                )

    forbidden = {
        "build_financial_diagnosis",
        "analisar_orcamento",
    }

    assert forbidden.isdisjoint(
        imported_names
    )

    assert forbidden.isdisjoint(
        called_names
    )

    assert (
        "resolver_entrada_financeira"
        in imported_names
    )

    assert (
        "resolver_entrada_financeira"
        in called_names
    )

    assert (
        "executar_ferramenta_inna"
        in called_names
    )
