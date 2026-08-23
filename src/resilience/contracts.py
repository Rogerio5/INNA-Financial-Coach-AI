"""Compatibilidade temporaria para src.resilience.contracts."""

import sys

from src.compartilhado.resilience import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation
