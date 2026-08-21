"""Compatibilidade temporaria para src.resilience.tracing."""

import sys

from src.compartilhado.resilience import (
    tracing as _implementation,
)

sys.modules[__name__] = _implementation
