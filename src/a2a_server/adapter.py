"""Compatibilidade temporaria para src.a2a_server.adapter."""

import sys

from src.integracoes.a2a import (
    adapter as _implementation,
)

sys.modules[__name__] = _implementation
