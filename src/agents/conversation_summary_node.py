"""Compatibilidade temporária para src.agents.conversation_summary_node."""

import sys

from src.compartilhado.memoria import (
    conversation_summary_node as _implementation,
)

sys.modules[__name__] = _implementation
