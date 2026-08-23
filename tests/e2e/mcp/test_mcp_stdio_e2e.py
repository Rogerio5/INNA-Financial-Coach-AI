"""Teste E2E local do servidor MCP real via stdio."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)

MCP_MANIFEST_URI = "inna://mcp/manifest"

EXPECTED_MCP_TOOLS = {
    "buscar_conhecimento_rag",
    "calcular_diagnostico_financeiro",
    "preparar_email_financeiro",
    "preparar_mensagem_telegram",
}


@pytest.mark.anyio
async def test_real_mcp_stdio_protocol_e2e(
    tmp_path: Path,
) -> None:
    """Valida cliente e servidor MCP em processos separados."""
    audit_path = (
        tmp_path / "mcp-stdio-e2e.jsonl"
    )

    test_token = (
        "inna-mcp-stdio-e2e-test-token"
    )

    env = os.environ.copy()

    env[
        "INNA_INTERNAL_OPERATIONS_TOKEN"
    ] = test_token

    env[
        "INNA_MCP_CLIENT_TOKEN"
    ] = test_token

    env[
        "INNA_MCP_AUDIT_PATH"
    ] = str(audit_path)

    env[
        "INNA_MCP_DB_AUDIT_ENABLED"
    ] = "false"

    project_root = Path.cwd()

    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "src.mcp_server.server",
        ],
        env=env,
        cwd=str(project_root),
    )

    async with stdio_client(
        params
    ) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=20.0,
        ) as session:
            initialized = (
                await session.initialize()
            )

            assert initialized is not None

            tools_result = (
                await session.list_tools()
            )

            tool_names = {
                tool.name
                for tool in tools_result.tools
            }

            assert tool_names == (
                EXPECTED_MCP_TOOLS
            )

            resources_result = (
                await session.list_resources()
            )

            resource_uris = {
                str(resource.uri)
                for resource
                in resources_result.resources
            }

            assert MCP_MANIFEST_URI in (
                resource_uris
            )

            manifest_result = (
                await session.read_resource(
                    MCP_MANIFEST_URI
                )
            )

            assert len(
                manifest_result.contents
            ) == 1

            manifest_text = getattr(
                manifest_result.contents[0],
                "text",
                None,
            )

            assert manifest_text

            manifest = json.loads(
                manifest_text
            )

            assert (
                manifest[
                    "registry_summary"
                ][
                    "mcp_exposed_tool_count"
                ]
                == 4
            )

            result = await session.call_tool(
                "calcular_diagnostico_financeiro",
                {
                    "renda_mensal": 5000,
                    "gastos_fixos": 2000,
                    "gastos_variaveis": 1000,
                    "dividas_mensais": 300,
                    "reserva_atual": 2000,
                    "gastos_incluem_dividas": False,
                    "moeda": "BRL",
                    "idioma": "pt",
                },
            )

            payload = result.model_dump(
                by_alias=True
            )

            assert (
                payload.get(
                    "isError",
                    False,
                )
                is not True
            )

            structured = (
                payload.get(
                    "structuredContent"
                )
                or payload.get(
                    "structured_content"
                )
            )

            assert isinstance(
                structured,
                dict,
            )

            assert "_mcp" in structured

    assert audit_path.exists()

    events = [
        json.loads(line)
        for line in audit_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    assert len(events) >= 2

    assert any(
        event["event_type"]
        == "resource_read"
        and event["status"]
        == "success"
        for event in events
    )

    assert any(
        event["event_type"]
        == "tool_call"
        and event["status"]
        == "success"
        for event in events
    )

    serialized = json.dumps(
        events,
        ensure_ascii=False,
    )

    assert test_token not in serialized
