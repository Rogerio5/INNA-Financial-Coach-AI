"""Compatibilidade temporaria para src.a2a_server.server."""

import sys

from src.integracoes.a2a import (
    server as _implementation,
)

sys.modules[__name__] = _implementation
