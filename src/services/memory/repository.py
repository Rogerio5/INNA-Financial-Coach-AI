"""Compatibilidade temporária para repository."""

import sys

from src.compartilhado.memoria import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation
