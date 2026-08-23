"""Compatibilidade temporaria para src.resilience.runtime."""

import sys

from src.compartilhado.resilience import (
    runtime as _implementation,
)

sys.modules[__name__] = _implementation
