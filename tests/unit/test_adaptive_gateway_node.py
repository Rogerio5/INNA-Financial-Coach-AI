from src.agents.adaptive_gateway_node import (
    adaptive_gateway_node,
)


def test_adaptive_gateway_node_simple_route():
    result = adaptive_gateway_node(
        {
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "confidence": 0.89,
        }
    )

    assert result["adaptive_route_type"] == "simple"
    assert result["adaptive_complexity"] == "simple"
    assert result["adaptive_domain"] == "knowledge"
    assert (
        result["adaptive_target_supervisor"]
        == "knowledge_team_supervisor"
    )
    assert result["adaptive_budget"]["max_agents"] == 1
    assert result["adaptive_budget"]["max_a2a_messages"] == 0


def test_adaptive_gateway_node_multi_domain_route():
    result = adaptive_gateway_node(
        {
            "intent": "diagnostico_financeiro",
            "next_node": "financial_agent",
            "confidence": 0.95,
            "adaptive_multi_domain": True,
        }
    )

    assert result["adaptive_route_type"] == "complex"
    assert result["adaptive_complexity"] == "complex"
    assert result["adaptive_budget"]["max_supervisors"] == 3
    assert result["adaptive_budget"]["max_agents"] == 5


def test_adaptive_gateway_node_handoff_route():
    result = adaptive_gateway_node(
        {
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "confidence": 0.90,
            "handoff_required": True,
        }
    )

    assert result["adaptive_route_type"] == "complex"


def test_adaptive_gateway_node_low_confidence_escalates():
    result = adaptive_gateway_node(
        {
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "confidence": 0.30,
        }
    )

    assert result["adaptive_route_type"] == "escalate"
    assert result["next_node"] == "fallback_agent"
    assert (
        result["adaptive_target_agent"]
        == "fallback_agent"
    )
    assert (
        result["adaptive_target_supervisor"]
        == "support_team_supervisor"
    )


def test_adaptive_gateway_node_critical_risk_escalates():
    result = adaptive_gateway_node(
        {
            "intent": "diagnostico_financeiro",
            "next_node": "financial_agent",
            "confidence": 0.95,
            "adaptive_risk": "critical",
        }
    )

    assert result["adaptive_route_type"] == "escalate"
    assert result["adaptive_risk"] == "critical"


def test_invalid_risk_fails_safe():
    result = adaptive_gateway_node(
        {
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "confidence": 0.95,
            "adaptive_risk": "invalid",
        }
    )

    assert result["adaptive_route_type"] == "escalate"
    assert result["adaptive_risk"] == "critical"

def test_composite_request_is_detected_as_complex():
    result = adaptive_gateway_node(
        {
            "user_message": (
                "Analise minhas finanças e depois "
                "gere um relatório."
            ),
            "intent": "diagnostico_financeiro",
            "next_node": "financial_agent",
            "confidence": 0.97,
            "use_database": True,
            "generate_report": True,
        }
    )

    assert result["adaptive_route_type"] == "complex"
    assert result["adaptive_complexity"] == "complex"
    assert (
        "composite_report_workflow"
        in result["adaptive_complexity_signals"]
    )
