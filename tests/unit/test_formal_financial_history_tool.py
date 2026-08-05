from __future__ import annotations

from types import SimpleNamespace
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
from src.agent_tools.financial_history_tools import (
    FINANCIAL_HISTORY_TOOL_NAME,
    ConsultarHistoricoFinanceiroInput,
    FinancialHistoryToolExecutionError,
    HistoricoFinanceiroItem,
    executar_consulta_historico_financeiro,
)


def _context(
    *,
    agent: str = "financial_agent",
    user_id: str = "user-context-1",
) -> ToolExecutionContext:
    return ToolExecutionContext(
        requested_by=agent,
        user_id=user_id,
        session_id="session-history-test",
        trace_id="trace-history-test",
    )


def _execute(
    *,
    arguments: dict | None = None,
    agent: str = "financial_agent",
    user_id: str = "user-context-1",
):
    registry = criar_registro_ferramentas_inna()

    call = ToolCall(
        tool_name=(FINANCIAL_HISTORY_TOOL_NAME),
        arguments=(arguments if arguments is not None else {"limite": 5}),
        context=_context(
            agent=agent,
            user_id=user_id,
        ),
    )

    with ToolExecutor(registry=registry) as executor:
        return executor.execute(call)


def _repository_result():
    return {
        "possui_historico": True,
        "total_retornado": 1,
        "diagnosticos": [
            {
                "data_hora": ("2026-07-17T10:30:00"),
                "saldo_estimado": 1200.5,
                ("comprometimento_renda_percentual"): 70.25,
                "meses_reserva_estimados": 2.5,
                "score_financeiro": 70,
                "nivel_risco": "Medio",
                "moeda": "BRL",
                "idioma": "pt",
            }
        ],
    }


def test_input_validates_limit_range():
    with pytest.raises(ValidationError):
        ConsultarHistoricoFinanceiroInput(limite=0)

    with pytest.raises(ValidationError):
        ConsultarHistoricoFinanceiroInput(limite=21)


def test_catalog_registers_history_tool():
    registry = criar_registro_ferramentas_inna()

    definition = registry.get(FINANCIAL_HISTORY_TOOL_NAME)

    assert definition.allowed_agents == (
        frozenset(
            {
                "financial_agent",
                "report_agent",
                "research_agent",
            }
        )
    )

    assert definition.idempotent is True
    assert definition.sensitive_output is True

    assert "read_only" in definition.tags
    assert "user_scoped" in definition.tags


def test_schema_exposes_only_limit():
    catalog = obter_catalogo_schemas_ferramentas()

    definition = next(
        item for item in catalog if item["name"] == FINANCIAL_HISTORY_TOOL_NAME
    )

    properties = definition["input_schema"]["properties"]

    assert set(properties) == {
        "limite",
    }

    assert "usuario_id" not in properties
    assert "user_id" not in properties
    assert "nome" not in properties


def test_executes_with_context_identity():
    with patch(
        "src.agent_tools."
        "financial_history_tools."
        "consultar_historico_financeiro_usuario",
        return_value=_repository_result(),
    ) as repository:
        result = _execute(
            arguments={
                "limite": 3,
            },
            user_id="trusted-user-99",
        )

    assert result.status == (ToolStatus.SUCCESS)

    assert result.ok is True

    repository.assert_called_once_with(
        "trusted-user-99",
        limite=3,
    )

    assert result.output["total_retornado"] == 1

    assert result.output["diagnosticos"][0]["score_financeiro"] == 70


def test_cannot_override_context_identity():
    with patch(
        "src.agent_tools.financial_history_tools.consultar_historico_financeiro_usuario"
    ) as repository:
        result = _execute(
            arguments={
                "limite": 3,
                "usuario_id": ("another-user"),
            },
            user_id="trusted-user",
        )

    assert result.status == (ToolStatus.VALIDATION_ERROR)

    repository.assert_not_called()


def test_rejects_missing_trusted_identity():
    payload = ConsultarHistoricoFinanceiroInput(limite=3)

    context = SimpleNamespace(user_id="   ")

    with pytest.raises(FinancialHistoryToolExecutionError):
        executar_consulta_historico_financeiro(
            payload,
            context,
        )


def test_denies_non_financial_agent():
    result = _execute(agent="rag_agent")

    assert result.status == (ToolStatus.DENIED)

    assert result.error.code == ("tool_permission_denied")


def test_repository_failure_is_safe():
    with patch(
        "src.agent_tools."
        "financial_history_tools."
        "consultar_historico_financeiro_usuario",
        side_effect=RuntimeError("postgresql://user:secret@host"),
    ):
        result = _execute()

    assert result.status == (ToolStatus.ERROR)

    message = result.error.message

    assert "secret" not in message
    assert "postgresql://" not in message


def test_output_rejects_sensitive_fields():
    with pytest.raises(ValidationError):
        HistoricoFinanceiroItem(
            score_financeiro=70,
            nome="Não permitido",
        )
