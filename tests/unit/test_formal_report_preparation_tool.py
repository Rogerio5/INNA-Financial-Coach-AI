from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.agent_tools.catalog import (
    criar_registro_ferramentas_inna,
)
from src.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolPermissionPolicy,
    ToolStatus,
)
from src.agent_tools.report_tools import (
    PREPARE_FINANCIAL_REPORT_TOOL_NAME,
    PrepararRelatorioFinanceiroInput,
    ReportPreparationError,
    executar_preparacao_relatorio_financeiro,
)
from src.agent_tools.runtime import (
    executar_ferramenta_inna,
)


def _trusted_context(
    *,
    requested_by: str = "report_agent",
) -> ToolExecutionContext:
    return ToolExecutionContext(
        requested_by=requested_by,
        user_id="user-report-test",
        session_id="session-report-test",
        trace_id="trace-report-test",
        metadata={
            "intent": "relatorio",
        },
    )


def _official_diagnosis():
    return {
        "data_hora": "2026-07-22T01:00:00",
        "saldo_estimado": 800.0,
        "comprometimento_renda_percentual": 65.5,
        "meses_reserva_estimados": 2.4,
        "score_financeiro": 72,
        "nivel_risco": "Medio",
        "moeda": "BRL",
        "idioma": "pt",
    }


def test_prepares_report_without_recalculating_values():
    payload = PrepararRelatorioFinanceiroInput(
        diagnosticos=[
            _official_diagnosis(),
        ],
        resumo_executivo=(
            "Resumo aprovado para o relatório."
        ),
        recomendacoes=[
            "Fortalecer gradualmente a reserva.",
        ],
        proximos_passos=[
            "Revisar novamente no próximo mês.",
        ],
    )

    result = (
        executar_preparacao_relatorio_financeiro(
            payload,
            _trusted_context(),
        )
    )

    assert result.possui_diagnostico
    assert result.total_diagnosticos == 1

    assert (
        result.indicadores_oficiais
        .saldo_estimado
        == 800.0
    )

    assert (
        result.indicadores_oficiais
        .score_financeiro
        == 72
    )

    assert not (
        result.financial_values_recalculated
    )

    assert result.ready_for_risk_review
    assert not result.ready_for_pdf_rendering


def test_latest_official_diagnosis_is_first_item():
    payload = PrepararRelatorioFinanceiroInput(
        diagnosticos=[
            _official_diagnosis(),
            {
                **_official_diagnosis(),
                "saldo_estimado": 400.0,
                "score_financeiro": 50,
            },
        ],
    )

    result = (
        executar_preparacao_relatorio_financeiro(
            payload,
            _trusted_context(),
        )
    )

    assert (
        result.indicadores_oficiais
        .saldo_estimado
        == 800.0
    )

    assert (
        result.indicadores_oficiais
        .score_financeiro
        == 72
    )


def test_empty_history_returns_safe_report():
    payload = PrepararRelatorioFinanceiroInput(
        diagnosticos=[],
    )

    result = (
        executar_preparacao_relatorio_financeiro(
            payload,
            _trusted_context(),
        )
    )

    assert not result.possui_diagnostico
    assert result.total_diagnosticos == 0
    assert result.indicadores_oficiais is None
    assert "não existem" in (
        result.resumo_executivo.lower()
    )


def test_requires_trusted_user_identity():
    payload = PrepararRelatorioFinanceiroInput(
        diagnosticos=[],
    )

    context = ToolExecutionContext(
        requested_by="report_agent",
        user_id=None,
        session_id="session-report-test",
        trace_id="trace-report-test",
        metadata={},
    )

    with pytest.raises(
        ReportPreparationError,
        match="missing_trusted_user_identity",
    ):
        executar_preparacao_relatorio_financeiro(
            payload,
            context,
        )


def test_rejects_invalid_score():
    with pytest.raises(ValidationError):
        PrepararRelatorioFinanceiroInput(
            diagnosticos=[
                {
                    **_official_diagnosis(),
                    "score_financeiro": 150,
                }
            ],
        )


def test_rejects_unknown_input_fields():
    with pytest.raises(ValidationError):
        PrepararRelatorioFinanceiroInput(
            diagnosticos=[],
            usuario_id="attacker-controlled",
        )


def test_catalog_contains_report_preparation_tool():
    registry = (
        criar_registro_ferramentas_inna()
    )

    definition = registry.get(
        PREPARE_FINANCIAL_REPORT_TOOL_NAME
    )

    assert (
        definition.name
        == PREPARE_FINANCIAL_REPORT_TOOL_NAME
    )

    assert definition.allowed_agents == frozenset({
        "report_agent",
    })

    assert definition.idempotent
    assert definition.sensitive_output


def test_report_agent_executes_tool_successfully():
    result = executar_ferramenta_inna(
        ToolCall(
            tool_name=(
                PREPARE_FINANCIAL_REPORT_TOOL_NAME
            ),
            arguments={
                "diagnosticos": [
                    _official_diagnosis(),
                ],
                "recomendacoes": [
                    "Manter acompanhamento mensal.",
                ],
            },
            context=_trusted_context(),
        )
    )

    assert result.status == ToolStatus.SUCCESS
    assert result.ok

    assert (
        result.output["total_diagnosticos"]
        == 1
    )

    assert not result.output[
        "financial_values_recalculated"
    ]


def test_other_agent_cannot_prepare_report():
    policy = ToolPermissionPolicy()

    result = executar_ferramenta_inna(
        ToolCall(
            tool_name=(
                PREPARE_FINANCIAL_REPORT_TOOL_NAME
            ),
            arguments={
                "diagnosticos": [],
            },
            context=_trusted_context(
                requested_by="rag_agent",
            ),
        ),
        permission_policy=policy,
    )

    assert not result.ok

    assert result.status in {
        ToolStatus.DENIED,
        ToolStatus.ERROR,
    }


def test_public_schema_does_not_expose_identity():
    registry = (
        criar_registro_ferramentas_inna()
    )

    definition = registry.get(
        PREPARE_FINANCIAL_REPORT_TOOL_NAME
    )

    schema = (
        definition.input_model
        .model_json_schema()
    )

    properties = schema.get(
        "properties",
        {},
    )

    assert "user_id" not in properties
    assert "usuario_id" not in properties
    assert "nome" not in properties
