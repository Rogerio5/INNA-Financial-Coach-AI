"""Compatibilidade temporaria para src.resilience.policies."""

import sys

from src.compartilhado.resilience import (
    policies as _implementation,
)

sys.modules[__name__] = _implementation
