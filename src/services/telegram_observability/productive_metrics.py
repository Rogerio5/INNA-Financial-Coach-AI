"""Compatibilidade temporária para telegram_observability.productive_metrics."""

import sys

from src.integracoes.telegram.observabilidade import (
    productive_metrics as _implementation,
)

sys.modules[__name__] = _implementation
