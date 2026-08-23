"""Compatibilidade temporária para telegram_conversation_state.runtime."""

import sys

from src.integracoes.telegram.conversation_state import (
    runtime as _implementation,
)

sys.modules[__name__] = _implementation
