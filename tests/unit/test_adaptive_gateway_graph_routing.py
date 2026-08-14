from src.agents.adaptive_gateway_node import (
    select_adaptive_gateway_route,
)


def test_simple_route_bypasses_team_hierarchy():
    route = select_adaptive_gateway_route(
        {
            "adaptive_route_type": "simple",
        }
    )

    assert route == "execution_governance"


def test_complex_route_uses_team_hierarchy():
    route = select_adaptive_gateway_route(
        {
            "adaptive_route_type": "complex",
        }
    )

    assert route == "team_router"


def test_escalate_route_fails_safe():
    route = select_adaptive_gateway_route(
        {
            "adaptive_route_type": "escalate",
        }
    )

    assert route == "execution_governance"


def test_unknown_adaptive_route_fails_safe():
    route = select_adaptive_gateway_route(
        {
            "adaptive_route_type": "unexpected",
        }
    )

    assert route == "execution_governance"


def test_missing_adaptive_route_fails_safe():
    route = select_adaptive_gateway_route({})

    assert route == "execution_governance"
