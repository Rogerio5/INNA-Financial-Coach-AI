"""Compatibilidade temporaria para src.a2a_server.security."""

import sys

from src.integracoes.a2a import (
    security as _implementation,
)

sys.modules[__name__] = _implementation
