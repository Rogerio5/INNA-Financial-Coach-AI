"""Compatibilidade temporaria para src.resilience.events."""

import sys

from src.compartilhado.resilience import (
    events as _implementation,
)

sys.modules[__name__] = _implementation
