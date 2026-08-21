"""Compatibilidade temporária para conversation_summary."""

import sys

from src.compartilhado.memoria import (
    conversation_summary as _implementation,
)

sys.modules[__name__] = _implementation
