"""Compatibilidade temporária para evolution."""

import sys

from src.compartilhado.memoria import (
    evolution as _implementation,
)

sys.modules[__name__] = _implementation
