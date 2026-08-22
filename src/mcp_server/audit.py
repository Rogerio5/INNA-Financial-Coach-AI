"""Compatibilidade temporaria para src.mcp_server.audit."""

import sys

from src.integracoes.mcp import (
    audit as _implementation,
)

sys.modules[__name__] = _implementation
