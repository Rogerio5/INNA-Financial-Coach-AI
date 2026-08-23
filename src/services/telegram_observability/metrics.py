"""Compatibilidade temporária para telegram_observability.metrics."""

import sys

from src.integracoes.telegram.observabilidade import (
    metrics as _implementation,
)

sys.modules[__name__] = _implementation
