"""Compatibilidade temporária para telegram_conversation_state.store."""

import sys

from src.integracoes.telegram.conversation_state import (
    store as _implementation,
)

sys.modules[__name__] = _implementation
