"""Compatibilidade temporária para telegram_observability.productive_adapter."""

import sys

from src.integracoes.telegram.observabilidade import (
    productive_adapter as _implementation,
)

sys.modules[__name__] = _implementation
