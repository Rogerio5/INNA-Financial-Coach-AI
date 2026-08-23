"""Integracao MCP oficial da INNA."""

from src.integracoes.mcp.server import (
    criar_servidor_mcp_inna,
)
from src.integracoes.mcp.server import (
    server as mcp_server,
)

__all__ = [
    "criar_servidor_mcp_inna",
    "mcp_server",
]
