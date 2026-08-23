"""Compatibilidade temporaria para src.mcp_server."""

from src.integracoes.mcp import (
    criar_servidor_mcp_inna,
)
from src.integracoes.mcp import (
    mcp_server,
)

__all__ = [
    "criar_servidor_mcp_inna",
    "mcp_server",
]
