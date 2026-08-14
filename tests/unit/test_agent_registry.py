import pytest

from src.agents.agent_registry import (
    AgentDefinition,
    AgentNotFoundError,
    AgentRegistrationError,
    AgentRegistry,
)


def _definition(
    agent_id: str = "financial_agent",
) -> AgentDefinition:
    return AgentDefinition(
        agent_id=agent_id,
        description="Agente de teste.",
        runtime="langgraph",
        team="financial_team",
        supervisor=(
            "financial_team_supervisor"
        ),
        capabilities=frozenset(
            {
                "financial_diagnosis",
            }
        ),
        allowed_tools=frozenset(
            {
                "calcular_diagnostico_financeiro",
            }
        ),
    )


def test_register_and_get_agent():
    registry = AgentRegistry()

    definition = _definition()

    registry.register(
        definition
    )

    assert registry.get(
        "financial_agent"
    ) == definition


def test_duplicate_registration_is_rejected():
    registry = AgentRegistry()

    registry.register(
        _definition()
    )

    with pytest.raises(
        AgentRegistrationError
    ):
        registry.register(
            _definition()
        )


def test_unknown_agent_is_rejected():
    registry = AgentRegistry()

    with pytest.raises(
        AgentNotFoundError
    ):
        registry.get(
            "unknown_agent"
        )


def test_capability_discovery():
    registry = AgentRegistry()

    registry.register(
        _definition()
    )

    result = registry.find_by_capability(
        "financial_diagnosis"
    )

    assert [
        definition.agent_id
        for definition in result
    ] == [
        "financial_agent",
    ]


def test_service_identity_without_hierarchy_is_valid():
    definition = AgentDefinition(
        agent_id="communication_agent",
        description=(
            "Identidade operacional "
            "de comunicação."
        ),
        kind="service_identity",
        runtime="mcp",
        capabilities=frozenset(
            {
                "email_preparation",
                "telegram_preparation",
            }
        ),
    )

    assert definition.team is None
    assert definition.supervisor is None


def test_service_identity_cannot_claim_team():
    with pytest.raises(
        AgentRegistrationError
    ):
        AgentDefinition(
            agent_id="communication_agent",
            description="Teste.",
            kind="service_identity",
            runtime="mcp",
            team="support_team",
            supervisor=(
                "support_team_supervisor"
            ),
        )


def test_team_requires_supervisor():
    with pytest.raises(
        AgentRegistrationError
    ):
        AgentDefinition(
            agent_id="financial_agent",
            description="Teste.",
            team="financial_team",
        )


def test_schema_catalog_is_serializable_contract():
    registry = AgentRegistry()

    registry.register(
        _definition()
    )

    catalog = registry.schema_catalog()

    assert catalog[0]["agent_id"] == (
        "financial_agent"
    )
    assert catalog[0]["kind"] == "agent"
    assert catalog[0]["status"] == "active"
    assert catalog[0]["runtime"] == "langgraph"
    assert catalog[0]["capabilities"] == [
        "financial_diagnosis",
    ]
