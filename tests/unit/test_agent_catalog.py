from src.agents.agent_catalog import (
    DEFAULT_AGENT_REGISTRY,
    criar_registro_agentes_inna,
)


def test_default_registry_contains_all_known_identities():
    registry = criar_registro_agentes_inna()

    assert {
        definition.agent_id
        for definition
        in registry.list_definitions()
    } == {
        "financial_agent",
        "report_agent",
        "education_agent",
        "rag_agent",
        "fallback_agent",
        "research_agent",
        "communication_agent",
    }


def test_financial_agent_reuses_team_hierarchy():
    definition = (
        DEFAULT_AGENT_REGISTRY.get(
            "financial_agent"
        )
    )

    assert definition.team == (
        "financial_team"
    )

    assert definition.supervisor == (
        "financial_team_supervisor"
    )


def test_financial_agent_tools_are_derived():
    definition = (
        DEFAULT_AGENT_REGISTRY.get(
            "financial_agent"
        )
    )

    assert definition.allowed_tools == (
        frozenset(
            {
                "calcular_diagnostico_financeiro",
                "consultar_historico_financeiro",
            }
        )
    )


def test_report_agent_tools_are_derived():
    definition = (
        DEFAULT_AGENT_REGISTRY.get(
            "report_agent"
        )
    )

    assert definition.allowed_tools == (
        frozenset(
            {
                "consultar_historico_financeiro",
                "preparar_email_financeiro",
                "preparar_relatorio_financeiro",
            }
        )
    )


def test_research_agent_is_formally_registered():
    definition = (
        DEFAULT_AGENT_REGISTRY.get(
            "research_agent"
        )
    )

    assert definition.kind == "agent"
    assert definition.runtime == "agentic_rag"
    assert definition.team is None
    assert definition.supervisor is None
    assert definition.version == "5.1.0"

    assert definition.allowed_tools == (
        frozenset(
            {
                "buscar_conhecimento_rag",
                "consultar_historico_financeiro",
            }
        )
    )


def test_communication_identity_is_not_hierarchical_agent():
    definition = (
        DEFAULT_AGENT_REGISTRY.get(
            "communication_agent"
        )
    )

    assert (
        definition.kind
        == "service_identity"
    )

    assert definition.runtime == "mcp"
    assert definition.team is None
    assert definition.supervisor is None

    assert definition.allowed_tools == (
        frozenset(
            {
                "preparar_email_financeiro",
                "preparar_mensagem_telegram",
            }
        )
    )


def test_fallback_agent_has_no_tools():
    definition = (
        DEFAULT_AGENT_REGISTRY.get(
            "fallback_agent"
        )
    )

    assert definition.allowed_tools == (
        frozenset()
    )


def test_capability_discovery_finds_rag_agents():
    result = (
        DEFAULT_AGENT_REGISTRY
        .find_by_capability(
            "knowledge_retrieval"
        )
    )

    assert {
        definition.agent_id
        for definition in result
    } == {
        "education_agent",
        "rag_agent",
        "research_agent",
    }


def test_schema_catalog_contains_seven_identities():
    catalog = (
        DEFAULT_AGENT_REGISTRY
        .schema_catalog()
    )

    assert len(catalog) == 7

def test_capability_discovery_excludes_service_identity_by_default():
    result = (
        DEFAULT_AGENT_REGISTRY
        .find_by_capability(
            "email_preparation"
        )
    )

    assert {
        definition.agent_id
        for definition in result
    } == {
        "report_agent",
    }


def test_service_identity_can_be_discovered_explicitly():
    result = (
        DEFAULT_AGENT_REGISTRY
        .find_by_capability(
            "email_preparation",
            kind="service_identity",
        )
    )

    assert {
        definition.agent_id
        for definition in result
    } == {
        "communication_agent",
    }


def test_tool_permission_identities_are_all_registered():
    from src.agent_tools.catalog import (
        criar_registro_ferramentas_inna,
    )

    registered = {
        definition.agent_id
        for definition
        in DEFAULT_AGENT_REGISTRY.list_definitions()
    }

    permitted: set[str] = set()

    for tool in (
        criar_registro_ferramentas_inna()
        .list_definitions()
    ):
        permitted.update(
            agent_id
            for agent_id
            in tool.allowed_agents
            if agent_id != "*"
        )

    assert permitted <= registered

