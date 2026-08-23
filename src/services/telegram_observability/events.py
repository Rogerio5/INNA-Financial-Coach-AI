"""Compatibilidade temporária para telegram_observability.events."""

import sys

from src.integracoes.telegram.observabilidade import (
    events as _implementation,
)

sys.modules[__name__] = _implementation
