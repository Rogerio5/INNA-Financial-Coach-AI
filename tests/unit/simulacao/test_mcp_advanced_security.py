"""Testes de segurança e auditoria do MCP."""

from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import pytest

from src.mcp_server.security import (
    MCPAuthenticationError,
    validar_autenticacao_interna,
)

module = importlib.import_module("src.mcp_server.server")


def test_mcp_auth_accepts_matching_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "token-seguro",
    )
    monkeypatch.setenv(
        "INNA_MCP_CLIENT_TOKEN",
        "token-seguro",
    )

    validar_autenticacao_interna()


def test_mcp_auth_rejects_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "token-correto",
    )
    monkeypatch.setenv(
        "INNA_MCP_CLIENT_TOKEN",
        "token-incorreto",
    )

    with pytest.raises(
        MCPAuthenticationError,
        match="não autorizado",
    ):
        validar_autenticacao_interna()


def test_mcp_audit_does_not_store_raw_arguments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    audit_path = tmp_path / "mcp.jsonl"

    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "token-seguro",
    )
    monkeypatch.setenv(
        "INNA_MCP_CLIENT_TOKEN",
        "token-seguro",
    )
    monkeypatch.setenv(
        "INNA_MCP_AUDIT_PATH",
        str(audit_path),
    )
    monkeypatch.setenv(
        "INNA_MCP_DB_AUDIT_ENABLED",
        "false",
    )

    def fake_runtime(call):
        return SimpleNamespace(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=SimpleNamespace(value="success"),
            output={
                "saldo_estimado": 500.0,
            },
            error=None,
            duration_ms=2.5,
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

    event = json.loads(audit_path.read_text(encoding="utf-8").strip())

    assert event["status"] == "success"
    assert event["raw_arguments_stored"] is False
    assert event["raw_output_stored"] is False
    assert len(event["arguments_sha256"]) == 64

    serialized = json.dumps(event)

    assert "3000" not in serialized
    assert "1500" not in serialized
    assert "700" not in serialized


def test_mcp_tool_rejects_unauthenticated_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "token-servidor",
    )
    monkeypatch.delenv(
        "INNA_MCP_CLIENT_TOKEN",
        raising=False,
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
