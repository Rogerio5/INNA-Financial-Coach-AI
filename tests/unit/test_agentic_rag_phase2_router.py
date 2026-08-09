"""
Testes da Fase 2 da Semana 4:
Router Agent seguro e governado.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from src.agent_tools.financial_history_tools import (
    criar_definicao_consultar_historico_financeiro,
)
from src.agent_tools.rag_tools import (
    criar_definicao_buscar_conhecimento_rag,
)
from src.agentic_rag import (
    MissingTrustedUserContextError,
    ResearchRoutingError,
    ResearchSource,
    ResearchSourceRouter,
    ResearchSubquery,
    build_tool_call,
    create_research_plan,
    execute_routed_tool,
    route_research_plan,
    route_to_audit_payload,
)


def _knowledge_step() -> ResearchSubquery:
    return ResearchSubquery(
        step_id="step_01_knowledge",
        question=("Como criar uma reserva de emergência?"),
        source=(ResearchSource.KNOWLEDGE_BASE),
        tool_name="buscar_conhecimento_rag",
        priority=100,
        required=True,
        top_k=5,
    )


def _history_step() -> ResearchSubquery:
    return ResearchSubquery(
        step_id="step_02_history",
        question=("Compare meu histórico financeiro."),
        source=(ResearchSource.FINANCIAL_HISTORY),
        tool_name=("consultar_historico_financeiro"),
        priority=90,
        required=True,
        max_results=8,
    )


def test_routes_knowledge_base_with_exact_arguments():
    route = ResearchSourceRouter().route(
        _knowledge_step(),
        language="pt",
    )

    assert route.source == ResearchSource.KNOWLEDGE_BASE
    assert route.tool_name == "buscar_conhecimento_rag"
    assert route.arguments == {
        "pergunta": ("Como criar uma reserva de emergência?"),
        "idioma": "pt",
        "top_k": 5,
    }
    assert route.requires_trusted_user is False
    assert route.sensitive_output is False
    assert route.read_only is True
    assert route.idempotent is True
    assert route.requested_by == "research_agent"


def test_routes_history_without_identity_argument():
    route = ResearchSourceRouter().route(
        _history_step(),
        language="pt",
    )

    assert route.arguments == {
        "limite": 8,
    }
    assert "user_id" not in route.arguments
    assert "usuario_id" not in route.arguments
    assert route.requires_trusted_user is True
    assert route.sensitive_output is True


def test_routes_complete_research_plan():
    plan = create_research_plan(
        "Compare reserva de emergência e "
        "pagamento de dívidas, explique os "
        "riscos e crie um plano completo."
    )

    routes = route_research_plan(plan)

    assert len(routes) == len(plan.subqueries)
    assert all(route.read_only for route in routes)
    assert all(route.requested_by == "research_agent" for route in routes)


def test_router_rejects_tool_source_mismatch():
    invalid_step = ResearchSubquery.model_construct(
        step_id="step_01_invalid",
        question=("Consultar conhecimento financeiro."),
        source=(ResearchSource.KNOWLEDGE_BASE),
        tool_name=("consultar_historico_financeiro"),
        priority=50,
        required=True,
        top_k=4,
        max_results=5,
    )

    with pytest.raises(
        ResearchRoutingError,
        match="não corresponde",
    ):
        ResearchSourceRouter().route(
            invalid_step,
            language="pt",
        )


def test_router_rejects_unknown_source():
    invalid_step = ResearchSubquery.model_construct(
        step_id="step_01_external",
        question=("Pesquisar uma fonte externa."),
        source="external_web",
        tool_name="web_search",
        priority=50,
        required=True,
        top_k=4,
        max_results=5,
    )

    with pytest.raises(
        ResearchRoutingError,
        match="não autorizada",
    ):
        ResearchSourceRouter().route(
            invalid_step,
            language="pt",
        )


def test_router_rejects_invalid_language():
    with pytest.raises(
        ResearchRoutingError,
        match="idioma",
    ):
        ResearchSourceRouter().route(
            _knowledge_step(),
            language="../../secret",
        )


def test_history_call_requires_trusted_user():
    route = ResearchSourceRouter().route(
        _history_step(),
        language="pt",
    )

    with pytest.raises(
        MissingTrustedUserContextError,
        match="contexto confiável",
    ):
        build_tool_call(
            route,
            user_id=None,
            session_id="session-1",
            trace_id="trace-1",
        )


def test_knowledge_call_does_not_require_user():
    route = ResearchSourceRouter().route(
        _knowledge_step(),
        language="pt",
    )

    call = build_tool_call(
        route,
        user_id=None,
        session_id="session-1",
        trace_id="trace-1",
    )

    assert call.tool_name == "buscar_conhecimento_rag"
    assert call.context.user_id is None
    assert call.context.requested_by == "research_agent"
    assert call.context.trace_id == "trace-1"


def test_history_identity_stays_only_in_context():
    route = ResearchSourceRouter().route(
        _history_step(),
        language="pt",
    )

    call = build_tool_call(
        route,
        user_id="trusted-user-123",
        session_id="session-123",
        trace_id="trace-123",
    )

    assert call.context.user_id == "trusted-user-123"
    assert call.context.session_id == "session-123"
    assert call.arguments == {
        "limite": 8,
    }
    assert "trusted-user-123" not in repr(call.arguments)


def test_route_contract_rejects_identity_argument():
    route = ResearchSourceRouter().route(
        _history_step(),
        language="pt",
    )

    route_data = route.model_dump(mode="python")
    route_data["arguments"] = {
        "limite": 8,
        "user_id": "forbidden",
    }

    with pytest.raises(
        ValidationError,
        match="Argumentos não permitidos",
    ):
        type(route).model_validate(route_data)


def test_audit_payload_does_not_expose_question():
    route = ResearchSourceRouter().route(
        _knowledge_step(),
        language="pt",
    )

    audit = route_to_audit_payload(route)
    serialized = repr(audit)

    assert "Como criar uma reserva" not in serialized
    assert "arguments_sha256" in audit
    assert audit["argument_names"] == [
        "idioma",
        "pergunta",
        "top_k",
    ]
    assert "arguments" not in audit


def test_execute_routed_tool_uses_formal_call():
    route = ResearchSourceRouter().route(
        _knowledge_step(),
        language="pt",
    )

    captured: dict[str, Any] = {}
    sentinel = object()

    def fake_executor(call):
        captured["call"] = call
        return sentinel

    result = execute_routed_tool(
        route,
        user_id=None,
        session_id="session-test",
        trace_id="trace-test",
        executor=fake_executor,
    )

    assert result is sentinel
    assert captured["call"].tool_name == "buscar_conhecimento_rag"
    assert captured["call"].context.requested_by == "research_agent"


def test_research_agent_has_formal_permissions():
    rag_definition = criar_definicao_buscar_conhecimento_rag()
    history_definition = criar_definicao_consultar_historico_financeiro()

    assert "research_agent" in rag_definition.allowed_agents
    assert "research_agent" in history_definition.allowed_agents


def test_trace_id_is_required():
    route = ResearchSourceRouter().route(
        _knowledge_step(),
        language="pt",
    )

    with pytest.raises(
        ResearchRoutingError,
        match="trace_id",
    ):
        build_tool_call(
            route,
            user_id=None,
            session_id="session-1",
            trace_id="",
        )
