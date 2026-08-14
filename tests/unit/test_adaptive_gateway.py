from src.agents.adaptive_gateway import decide_adaptive_route


def test_simple_financial_route_is_direct():
    decision = decide_adaptive_route(
        intent="diagnostico_financeiro",
        next_node="financial_agent",
        confidence=0.92,
    )

    assert decision.route_type == "simple"
    assert decision.complexity == "simple"
    assert decision.domain == "financial"
    assert decision.target_supervisor == "financial_team_supervisor"
    assert decision.budget.max_agents == 1
    assert decision.budget.max_a2a_messages == 0


def test_simple_rag_route_uses_knowledge_supervisor():
    decision = decide_adaptive_route(
        intent="consulta_rag",
        next_node="rag_agent",
        confidence=0.89,
    )

    assert decision.route_type == "simple"
    assert decision.domain == "knowledge"
    assert decision.target_supervisor == "knowledge_team_supervisor"


def test_multi_domain_request_is_complex():
    decision = decide_adaptive_route(
        intent="diagnostico_financeiro",
        next_node="financial_agent",
        confidence=0.94,
        multi_domain=True,
    )

    assert decision.route_type == "complex"
    assert decision.complexity == "complex"
    assert decision.budget.max_supervisors == 3
    assert decision.budget.max_a2a_messages == 6
    assert decision.budget.max_handoffs == 3


def test_required_handoff_is_complex():
    decision = decide_adaptive_route(
        intent="consulta_rag",
        next_node="rag_agent",
        confidence=0.90,
        requires_handoff=True,
    )

    assert decision.route_type == "complex"


def test_high_risk_request_is_complex():
    decision = decide_adaptive_route(
        intent="diagnostico_financeiro",
        next_node="financial_agent",
        confidence=0.95,
        risk="high",
    )

    assert decision.route_type == "complex"


def test_critical_risk_escalates():
    decision = decide_adaptive_route(
        intent="diagnostico_financeiro",
        next_node="financial_agent",
        confidence=0.95,
        risk="critical",
    )

    assert decision.route_type == "escalate"
    assert decision.reason == "adaptive_escalation_required"


def test_low_confidence_escalates():
    decision = decide_adaptive_route(
        intent="consulta_rag",
        next_node="rag_agent",
        confidence=0.59,
    )

    assert decision.route_type == "escalate"
    assert decision.target_agent == "fallback_agent"
    assert (
        decision.target_supervisor
        == "support_team_supervisor"
    )


def test_unknown_intent_escalates_to_safe_path():
    decision = decide_adaptive_route(
        intent="desconhecido",
        next_node="fallback_agent",
        confidence=0.40,
    )

    assert decision.route_type == "escalate"
    assert decision.domain == "support"
    assert decision.target_supervisor == "support_team_supervisor"


def test_confidence_is_clamped_to_valid_range():
    decision = decide_adaptive_route(
        intent="consulta_rag",
        next_node="rag_agent",
        confidence=2.0,
    )

    assert decision.confidence == 1.0

def test_explicit_complexity_hint_routes_complex():
    decision = decide_adaptive_route(
        intent="diagnostico_financeiro",
        next_node="financial_agent",
        confidence=0.95,
        complexity_hint="complex",
    )

    assert decision.route_type == "complex"
    assert decision.complexity == "complex"
