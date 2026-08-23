"""Compatibilidade temporária para telegram_conversation_state.repository."""

import sys

from src.integracoes.telegram.conversation_state import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation
