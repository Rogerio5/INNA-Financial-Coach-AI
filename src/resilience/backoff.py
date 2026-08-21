"""Compatibilidade temporaria para src.resilience.backoff."""

import sys

from src.compartilhado.resilience import (
    backoff as _implementation,
)

sys.modules[__name__] = _implementation
