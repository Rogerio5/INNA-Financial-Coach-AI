"""Testes do contrato MCP com os registries corporativos."""

from __future__ import annotations

import importlib

import pytest

module = importlib.import_module(
    "src.mcp_server.server"
)


def test_all_mcp_bindings_are_registry_consistent():
    for tool_name, principal in (
        module._MCP_TOOL_PRINCIPAL_BINDING.items()
    ):
        assert (
            module._resolve_mcp_principal(
                tool_name
            )
            == principal
        )


def test_mcp_binding_uses_registered_active_principal():
    for principal in (
        module._MCP_TOOL_PRINCIPAL_BINDING.values()
    ):
        assert module._AGENT_REGISTRY.contains(
            principal
        )

        definition = (
            module._AGENT_REGISTRY.get(
                principal
            )
        )

        assert definition.status == "active"


def test_mcp_binding_uses_registered_tool():
    for tool_name in (
        module._MCP_TOOL_PRINCIPAL_BINDING
    ):
        assert module._TOOL_REGISTRY.contains(
            tool_name
        )


def test_unknown_mcp_tool_is_denied():
    with pytest.raises(
        module.MCPToolExecutionError,
        match="não autorizada",
    ):
        module._resolve_mcp_principal(
            "unknown_mcp_tool"
        )


def test_unknown_principal_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setitem(
        module._MCP_TOOL_PRINCIPAL_BINDING,
        "calcular_diagnostico_financeiro",
        "ghost_agent",
    )

    with pytest.raises(
        module.MCPToolExecutionError,
        match="não registrado",
    ):
        module._resolve_mcp_principal(
            "calcular_diagnostico_financeiro"
        )


def test_tool_registry_permission_is_enforced(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setitem(
        module._MCP_TOOL_PRINCIPAL_BINDING,
        "calcular_diagnostico_financeiro",
        "report_agent",
    )

    with pytest.raises(
        module.MCPToolExecutionError,
        match="não autoriza",
    ):
        module._resolve_mcp_principal(
            "calcular_diagnostico_financeiro"
        )


def test_server_factory_validates_registry_contract(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setitem(
        module._MCP_TOOL_PRINCIPAL_BINDING,
        "calcular_diagnostico_financeiro",
        "ghost_agent",
    )

    with pytest.raises(
        module.MCPToolExecutionError,
        match="não registrado",
    ):
        module.criar_servidor_mcp_inna()
