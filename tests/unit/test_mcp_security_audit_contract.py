"""Contrato corporativo de segurança e auditoria MCP."""

from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import pytest

from src.mcp_server.manifest import (
    MCP_MANIFEST_URI,
)
from src.mcp_server.security import (
    MCPAuthenticationError,
)

module = importlib.import_module(
    "src.mcp_server.server"
)


def _configure_auth(
    monkeypatch: pytest.MonkeyPatch,
    *,
    token: str,
) -> None:
    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        token,
    )
    monkeypatch.setenv(
        "INNA_MCP_CLIENT_TOKEN",
        token,
    )
    monkeypatch.setenv(
        "INNA_MCP_DB_AUDIT_ENABLED",
        "false",
    )


def _read_events(path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def test_tool_audit_includes_principal_and_server_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
):
    audit_path = tmp_path / "tool.jsonl"

    _configure_auth(
        monkeypatch,
        token="week5-4c-tool-test-token",
    )

    monkeypatch.setenv(
        "INNA_MCP_AUDIT_PATH",
        str(audit_path),
    )

    def fake_runtime(call):
        return SimpleNamespace(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=SimpleNamespace(
                value="success"
            ),
            output={
                "saldo_estimado": 500.0,
            },
            error=None,
            duration_ms=1.5,
        )

    monkeypatch.setattr(
        module,
        "executar_ferramenta_inna",
        fake_runtime,
    )

    module.calcular_diagnostico_financeiro(
        renda_mensal=3000,
        gastos_fixos=1500,
        gastos_variaveis=700,
    )

    events = _read_events(
        audit_path
    )

    assert len(events) == 1

    event = events[0]

    assert event["principal"] == (
        "financial_agent"
    )
    assert event["event_type"] == (
        "tool_call"
    )
    assert event["server"] == (
        module.SERVER_NAME
    )
    assert event["server_version"] == (
        module.SERVER_VERSION
    )
    assert event[
        "raw_arguments_stored"
    ] is False
    assert event[
        "raw_output_stored"
    ] is False


def test_tool_auth_failure_is_audited(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
):
    audit_path = (
        tmp_path / "tool-auth-denied.jsonl"
    )

    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "week5-4c-server-token",
    )
    monkeypatch.delenv(
        "INNA_MCP_CLIENT_TOKEN",
        raising=False,
    )
    monkeypatch.setenv(
        "INNA_MCP_AUDIT_PATH",
        str(audit_path),
    )
    monkeypatch.setenv(
        "INNA_MCP_DB_AUDIT_ENABLED",
        "false",
    )

    with pytest.raises(
        MCPAuthenticationError,
        match="não fornecido",
    ):
        module.calcular_diagnostico_financeiro(
            renda_mensal=3000,
            gastos_fixos=1500,
            gastos_variaveis=700,
        )

    events = _read_events(
        audit_path
    )

    assert len(events) == 1

    event = events[0]

    assert event["status"] == "denied"
    assert event["event_type"] == (
        "tool_call"
    )
    assert event["principal"] is None
    assert event["error_code"] == (
        "mcp_authentication_failed"
    )
    assert event["server_version"] == (
        module.SERVER_VERSION
    )

    serialized = json.dumps(event)

    assert (
        "week5-4c-server-token"
        not in serialized
    )


def test_manifest_resource_rejects_unauthenticated_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
):
    audit_path = (
        tmp_path / "resource-denied.jsonl"
    )

    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "week5-4c-resource-token",
    )
    monkeypatch.delenv(
        "INNA_MCP_CLIENT_TOKEN",
        raising=False,
    )
    monkeypatch.setenv(
        "INNA_MCP_AUDIT_PATH",
        str(audit_path),
    )
    monkeypatch.setenv(
        "INNA_MCP_DB_AUDIT_ENABLED",
        "false",
    )

    with pytest.raises(
        MCPAuthenticationError,
        match="não fornecido",
    ):
        module._obter_manifesto_mcp_resource()

    events = _read_events(
        audit_path
    )

    assert len(events) == 1

    event = events[0]

    assert event["tool_name"] == (
        MCP_MANIFEST_URI
    )
    assert event["event_type"] == (
        "resource_read"
    )
    assert event["status"] == "denied"
    assert event["error_code"] == (
        "mcp_authentication_failed"
    )


def test_manifest_resource_success_is_audited(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
):
    audit_path = (
        tmp_path / "resource-success.jsonl"
    )

    _configure_auth(
        monkeypatch,
        token="week5-4c-resource-test-token",
    )

    monkeypatch.setenv(
        "INNA_MCP_AUDIT_PATH",
        str(audit_path),
    )

    manifest = (
        module._obter_manifesto_mcp_resource()
    )

    assert manifest[
        "schema_version"
    ]

    events = _read_events(
        audit_path
    )

    assert len(events) == 1

    event = events[0]

    assert event["tool_name"] == (
        MCP_MANIFEST_URI
    )
    assert event["event_type"] == (
        "resource_read"
    )
    assert event["status"] == "success"
    assert event["server"] == (
        module.SERVER_NAME
    )
    assert event["server_version"] == (
        module.SERVER_VERSION
    )
    assert event["principal"] is None
