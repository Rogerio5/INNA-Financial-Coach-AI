from src.agent_tools.catalog import (
    DEFAULT_FINANCIAL_HISTORY_TOOL_TIMEOUT_SECONDS,
    criar_registro_ferramentas_inna,
)
from src.agent_tools.financial_history_tools import (
    FINANCIAL_HISTORY_TOOL_NAME,
)


DATABASE_STATEMENT_TIMEOUT_SECONDS = 5.0


def test_history_tool_default_timeout_exceeds_database_timeout():
    assert (
        DEFAULT_FINANCIAL_HISTORY_TOOL_TIMEOUT_SECONDS
        > DATABASE_STATEMENT_TIMEOUT_SECONDS
    )

    assert DEFAULT_FINANCIAL_HISTORY_TOOL_TIMEOUT_SECONDS == 15.0


def test_history_tool_uses_configured_timeout(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_FINANCIAL_HISTORY_TOOL_TIMEOUT_SECONDS",
        "15",
    )

    registry = criar_registro_ferramentas_inna()

    definition = registry.get(FINANCIAL_HISTORY_TOOL_NAME)

    assert definition.timeout_seconds == 15.0
