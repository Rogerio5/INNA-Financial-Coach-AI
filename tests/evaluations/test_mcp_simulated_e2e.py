from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.mcp_simulated import (
    SimulatedMCPClient,
    build_simulated_mcp_harness,
    error_code,
    output_mapping,
    status_value,
)


@pytest.fixture
def harness():
    instance = build_simulated_mcp_harness()

    try:
        yield instance
    finally:
        instance.close()


def make_client(
    harness,
    *,
    agent_name: str = "supervisor",
) -> SimulatedMCPClient:
    return SimulatedMCPClient(
        harness,
        agent_name=agent_name,
        user_id="user-simulated-001",
        session_id="session-simulated-001",
    )


def test_registry_contains_simulated_tools(
    harness,
) -> None:
    expected_tools = {
        "mcp_health",
        "mcp_rag_search",
        "mcp_financial_calculate",
        "mcp_controlled_error",
        "mcp_timeout",
    }

    registered_tools = {
        definition.name for definition in (harness.registry.list_definitions())
    }

    assert expected_tools <= registered_tools


def test_health_client_server_executor_flow(
    harness,
) -> None:
    result = make_client(harness).call(
        "mcp_health",
        {},
        trace_id="trace-health-001",
    )

    assert status_value(result) == "success"

    output = output_mapping(result)

    assert output["status"] == "ok"
    assert output["service"] == "inna-mcp-simulated"
    assert output["trace_id"] == "trace-health-001"


def test_rag_simulated_e2e_propagates_context(
    harness,
) -> None:
    result = make_client(
        harness,
        agent_name="rag_agent",
    ).call(
        "mcp_rag_search",
        {
            "question": ("Como montar uma reserva financeira?"),
            "top_k": 3,
        },
        trace_id="trace-rag-001",
    )

    assert status_value(result) == "success"

    output = output_mapping(result)

    assert output["evidence_count"] == 2
    assert len(output["sources"]) == 2
    assert output["user_id"] == "user-simulated-001"
    assert output["session_id"] == "session-simulated-001"
    assert output["trace_id"] == "trace-rag-001"


def test_financial_simulated_e2e(
    harness,
) -> None:
    result = make_client(
        harness,
        agent_name="financial_agent",
    ).call(
        "mcp_financial_calculate",
        {
            "monthly_income": 3000,
            "fixed_expenses": 1500,
            "variable_expenses": 600,
            "monthly_debts": 300,
        },
        trace_id="trace-financial-001",
    )

    assert status_value(result) == "success"

    output = output_mapping(result)

    assert output["estimated_balance"] == 600
    assert output["risk_level"] == "low"
    assert output["user_id"] == "user-simulated-001"
    assert output["session_id"] == "session-simulated-001"
    assert output["trace_id"] == "trace-financial-001"


def test_invalid_arguments_are_rejected(
    harness,
) -> None:
    result = make_client(
        harness,
        agent_name="rag_agent",
    ).call(
        "mcp_rag_search",
        {
            "question": "curta",
            "top_k": 100,
        },
    )

    assert status_value(result) != "success"
    assert error_code(result)


def test_permission_denied_for_wrong_agent(
    harness,
) -> None:
    result = make_client(
        harness,
        agent_name="report_agent",
    ).call(
        "mcp_financial_calculate",
        {
            "monthly_income": 3000,
            "fixed_expenses": 1200,
            "variable_expenses": 500,
            "monthly_debts": 200,
        },
    )

    assert status_value(result) != "success"
    assert error_code(result)


def test_unknown_tool_returns_safe_error(
    harness,
) -> None:
    result = make_client(harness).call(
        "mcp_unknown_tool",
        {},
    )

    assert status_value(result) != "success"
    assert error_code(result)


def test_controlled_error_is_safe(
    harness,
) -> None:
    result = make_client(harness).call(
        "mcp_controlled_error",
        {
            "message": "fail safely",
        },
    )

    assert status_value(result) != "success"
    assert error_code(result)

    message = str(
        getattr(
            result.error,
            "message",
            "",
        )
    ).casefold()

    assert "traceback" not in message
    assert "c:\\" not in message


def test_timeout_is_enforced(
    harness,
) -> None:
    result = make_client(harness).call(
        "mcp_timeout",
        {
            "delay_seconds": 0.2,
        },
    )

    assert status_value(result) != "success"
    assert error_code(result)


def test_schema_catalog_exposes_tools(
    harness,
) -> None:
    serialized = json.dumps(
        harness.registry.schema_catalog(),
        ensure_ascii=False,
        default=str,
    )

    for tool_name in (
        "mcp_health",
        "mcp_rag_search",
        "mcp_financial_calculate",
        "mcp_controlled_error",
        "mcp_timeout",
    ):
        assert tool_name in serialized


def test_e2e_report_can_be_generated(
    harness,
    tmp_path: Path,
) -> None:
    client = make_client(harness)

    health = client.call(
        "mcp_health",
        {},
        trace_id="trace-report-health",
    )

    financial = client.call(
        "mcp_financial_calculate",
        {
            "monthly_income": 4000,
            "fixed_expenses": 1800,
            "variable_expenses": 700,
            "monthly_debts": 300,
        },
        trace_id="trace-report-financial",
    )

    report = {
        "offline": True,
        "network_server_started": False,
        "live_rag_called": False,
        "database_called": False,
        "gemini_called": False,
        "results": {
            "health": {
                "status": status_value(health),
                "output": output_mapping(health),
            },
            "financial": {
                "status": status_value(financial),
                "output": output_mapping(financial),
            },
        },
    }

    path = tmp_path / "mcp_simulated_e2e.json"

    path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert loaded["offline"] is True
    assert loaded["network_server_started"] is False
    assert loaded["results"]["health"]["status"] == "success"
    assert loaded["results"]["financial"]["status"] == "success"
