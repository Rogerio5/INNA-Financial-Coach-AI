"""Testes do manifesto corporativo MCP."""

from __future__ import annotations

import json

import pytest

from src.mcp_server.manifest import (
    MCP_MANIFEST_SCHEMA_VERSION,
    MCP_MANIFEST_URI,
)
from src.mcp_server.server import (
    _AGENT_REGISTRY,
    _MCP_TOOL_PRINCIPAL_BINDING,
    _TOOL_REGISTRY,
    SERVER_NAME,
    SERVER_VERSION,
    criar_servidor_mcp_inna,
    obter_manifesto_mcp,
)


def test_manifest_is_derived_from_registries():
    manifest = obter_manifesto_mcp()

    assert (
        manifest["schema_version"]
        == MCP_MANIFEST_SCHEMA_VERSION
    )

    assert manifest["server"] == {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "transport_scope": "internal",
    }

    summary = manifest[
        "registry_summary"
    ]

    assert summary[
        "tool_registry_count"
    ] == len(
        _TOOL_REGISTRY.list_definitions()
    )

    assert summary[
        "mcp_exposed_tool_count"
    ] == len(
        _MCP_TOOL_PRINCIPAL_BINDING
    )

    assert summary[
        "internal_only_tool_count"
    ] == 2


def test_manifest_contains_only_mcp_exposed_tools():
    manifest = obter_manifesto_mcp()

    names = {
        tool["name"]
        for tool in manifest["tools"]
    }

    assert names == set(
        _MCP_TOOL_PRINCIPAL_BINDING
    )

    assert (
        "consultar_historico_financeiro"
        not in names
    )

    assert (
        "preparar_relatorio_financeiro"
        not in names
    )


def test_manifest_metadata_matches_registries():
    manifest = obter_manifesto_mcp()

    for item in manifest["tools"]:
        tool = _TOOL_REGISTRY.get(
            item["name"]
        )

        agent = _AGENT_REGISTRY.get(
            item["principal"]
        )

        assert item["principal_kind"] == (
            agent.kind
        )

        assert item["runtime"] == (
            agent.runtime
        )

        assert item["status"] == (
            agent.status
        )

        assert item["timeout_seconds"] == (
            tool.timeout_seconds
        )

        assert item["idempotent"] == (
            tool.idempotent
        )

        assert item["sensitive_output"] == (
            tool.sensitive_output
        )

        assert item["input_schema"] == (
            tool.input_model.model_json_schema()
        )


@pytest.mark.anyio
async def test_manifest_resource_is_registered():
    server = criar_servidor_mcp_inna()

    resources = await server.list_resources()

    uris = {
        str(resource.uri)
        for resource in resources
    }

    assert MCP_MANIFEST_URI in uris


@pytest.mark.anyio
async def test_manifest_resource_is_readable_json():
    server = criar_servidor_mcp_inna()

    contents = await server.read_resource(
        MCP_MANIFEST_URI
    )

    items = list(contents)

    assert len(items) == 1

    raw_content = items[0].content

    if isinstance(
        raw_content,
        bytes,
    ):
        raw_content = raw_content.decode(
            "utf-8"
        )

    payload = json.loads(
        raw_content
    )

    assert payload[
        "schema_version"
    ] == MCP_MANIFEST_SCHEMA_VERSION

    assert payload[
        "registry_summary"
    ][
        "mcp_exposed_tool_count"
    ] == 4

    assert len(
        payload["tools"]
    ) == 4


def test_manifest_does_not_expose_auth_tokens():
    serialized = json.dumps(
        obter_manifesto_mcp(),
        ensure_ascii=False,
    )

    assert (
        "INNA_INTERNAL_OPERATIONS_TOKEN"
        not in serialized
    )

    assert (
        "INNA_MCP_CLIENT_TOKEN"
        not in serialized
    )
