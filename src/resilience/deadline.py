"""Compatibilidade temporaria para src.resilience.deadline."""

import sys

from src.compartilhado.resilience import (
    deadline as _implementation,
)

sys.modules[__name__] = _implementation
