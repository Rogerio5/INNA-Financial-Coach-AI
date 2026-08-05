"""Servidor MCP oficial da INNA."""

from src.mcp_server.server import (
    criar_servidor_mcp_inna,
    server as mcp_server,
)

__all__ = [
    "criar_servidor_mcp_inna",
    "mcp_server",
]
