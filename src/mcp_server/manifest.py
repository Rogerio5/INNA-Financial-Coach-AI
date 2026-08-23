"""Compatibilidade temporaria para src.mcp_server.manifest."""

import sys

from src.integracoes.mcp import (
    manifest as _implementation,
)

sys.modules[__name__] = _implementation
