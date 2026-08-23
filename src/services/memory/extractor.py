"""Compatibilidade temporária para extractor."""

import sys

from src.compartilhado.memoria import (
    extractor as _implementation,
)

sys.modules[__name__] = _implementation
