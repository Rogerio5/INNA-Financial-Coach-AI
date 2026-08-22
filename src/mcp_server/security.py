"""Compatibilidade temporaria para src.mcp_server.security."""

import sys

from src.integracoes.mcp import (
    security as _implementation,
)

sys.modules[__name__] = _implementation
