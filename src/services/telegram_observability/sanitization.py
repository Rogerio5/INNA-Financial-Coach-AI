"""Compatibilidade temporária para telegram_observability.sanitization."""

import sys

from src.integracoes.telegram.observabilidade import (
    sanitization as _implementation,
)

sys.modules[__name__] = _implementation
