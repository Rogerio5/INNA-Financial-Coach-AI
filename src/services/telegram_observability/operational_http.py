"""Compatibilidade temporária para telegram_observability.operational_http."""

import sys

from src.integracoes.telegram.observabilidade import (
    operational_http as _implementation,
)

sys.modules[__name__] = _implementation
