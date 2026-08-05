from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.agent_tools.catalog import (
    criar_registro_ferramentas_inna,
    obter_catalogo_schemas_ferramentas,
)
from src.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolExecutor,
    ToolStatus,
)
from src.agent_tools.financial_tools import (
    CalcularDiagnosticoFinanceiroInput,
    FINANCIAL_DIAGNOSIS_TOOL_NAME,
)


def _context(
    agent: str = "financial_agent",
) -> ToolExecutionContext:
    return ToolExecutionContext(
        requested_by=agent,
        user_id="user-test",
        session_id="session-test",
        trace_id="trace-test",
    )


def _arguments(
    **overrides,
) -> dict:
    values = {
        "renda_mensal": 4000,
        "gastos_fixos": 2000,
        "gastos_variaveis": 500,
        "dividas_mensais": 300,
        "reserva_atual": 0,
        "gastos_incluem_dividas": False,
        "moeda": "BRL",
        "idioma": "pt",
    }

    values.update(overrides)

    return values


def _execute(
    *,
    arguments: dict | None = None,
    agent: str = "financial_agent",
):
    registry = criar_registro_ferramentas_inna()

    call = ToolCall(
        tool_name=(FINANCIAL_DIAGNOSIS_TOOL_NAME),
        arguments=(arguments or _arguments()),
        context=_context(agent),
    )

    with ToolExecutor(registry=registry) as executor:
        return executor.execute(call)


def test_input_rejects_negative_values():
    with pytest.raises(ValidationError):
        CalcularDiagnosticoFinanceiroInput(
            **_arguments(
                renda_mensal=-1,
            )
        )


def test_input_normalizes_currency():
    payload = CalcularDiagnosticoFinanceiroInput(
        **_arguments(
            moeda="brl",
        )
    )

    assert payload.moeda == "BRL"


def test_catalog_registers_financial_tool():
    registry = criar_registro_ferramentas_inna()

    definition = registry.get(FINANCIAL_DIAGNOSIS_TOOL_NAME)

    assert definition.allowed_agents == (
        frozenset(
            {
                "financial_agent",
            }
        )
    )

    assert definition.idempotent is True
    assert definition.sensitive_output is True


def test_schema_catalog_exposes_financial_input():
    catalog = obter_catalogo_schemas_ferramentas()

    definition = next(
        item for item in catalog if item["name"] == FINANCIAL_DIAGNOSIS_TOOL_NAME
    )

    properties = definition["input_schema"]["properties"]

    assert "renda_mensal" in properties
    assert "gastos_fixos" in properties
    assert "gastos_variaveis" in properties
    assert "dividas_mensais" in properties
    assert "reserva_atual" in properties


def test_executes_financial_diagnosis():
    result = _execute()

    assert result.status == ToolStatus.SUCCESS
    assert result.ok is True

    output = result.output

    assert output["despesas_totais"] == 2800.0
    assert output["saldo_estimado"] == 1200.0

    assert output["comprometimento_renda_percentual"] == 70.0

    assert output["score_financeiro"] == 70

    assert output["nivel_risco"] == "Medio"
    assert output["situacao"] == ("saldo_positivo")


def test_does_not_duplicate_included_debts():
    result = _execute(
        arguments=_arguments(
            gastos_variaveis=800,
            gastos_incluem_dividas=True,
        )
    )

    assert result.status == ToolStatus.SUCCESS

    output = result.output

    assert output["despesas_totais"] == 2800.0
    assert output["saldo_estimado"] == 1200.0

    assert output["parcelas_adicionais_consideradas"] == 0.0


def test_denies_non_financial_agent():
    result = _execute(agent="rag_agent")

    assert result.status == ToolStatus.DENIED

    assert result.error.code == "tool_permission_denied"


def test_rejects_invalid_arguments_before_handler():
    registry = criar_registro_ferramentas_inna()

    call = ToolCall(
        tool_name=(FINANCIAL_DIAGNOSIS_TOOL_NAME),
        arguments=_arguments(
            gastos_fixos=-100,
        ),
        context=_context(),
    )

    with (
        patch("src.agent_tools.financial_tools.analisar_orcamento") as mock_budget,
        patch(
            "src.agent_tools.financial_tools.build_financial_diagnosis"
        ) as mock_diagnosis,
        ToolExecutor(registry=registry) as executor,
    ):
        result = executor.execute(call)

    assert result.status == ToolStatus.VALIDATION_ERROR

    mock_budget.assert_not_called()
    mock_diagnosis.assert_not_called()


def test_invariant_failure_becomes_safe_error():
    inconsistent_diagnosis = {
        "saldo_estimado": 999999,
        "comprometimento_renda_percentual": 70,
        "meses_reserva_estimados": 0,
        "score_financeiro": 70,
        "nivel_risco": "Medio",
        "diagnostico": "internal",
    }

    registry = criar_registro_ferramentas_inna()

    call = ToolCall(
        tool_name=(FINANCIAL_DIAGNOSIS_TOOL_NAME),
        arguments=_arguments(),
        context=_context(),
    )

    with (
        patch(
            "src.agent_tools.financial_tools.build_financial_diagnosis",
            return_value=(inconsistent_diagnosis),
        ),
        ToolExecutor(registry=registry) as executor,
    ):
        result = executor.execute(call)

    assert result.status == ToolStatus.ERROR

    assert result.error.code == "tool_execution_error"

    assert "999999" not in result.error.message
