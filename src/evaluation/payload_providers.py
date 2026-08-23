"""Compatibilidade temporária para src.evaluation.payload_providers."""

import sys

from src.compartilhado.avaliacao import (
    payload_providers as _implementation,
)

sys.modules[__name__] = _implementation
