"""Compatibilidade temporária para telegram_observability.productive_operations."""

import sys

from src.integracoes.telegram.observabilidade import (
    productive_operations as _implementation,
)

sys.modules[__name__] = _implementation
