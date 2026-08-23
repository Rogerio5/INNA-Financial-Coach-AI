"""Compatibilidade temporaria para src.resilience.circuit_breaker."""

import sys

from src.compartilhado.resilience import (
    circuit_breaker as _implementation,
)

sys.modules[__name__] = _implementation
