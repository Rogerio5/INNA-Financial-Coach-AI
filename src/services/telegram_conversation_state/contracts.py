"""Compatibilidade temporária para telegram_conversation_state.contracts."""

import sys

from src.integracoes.telegram.conversation_state import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation
