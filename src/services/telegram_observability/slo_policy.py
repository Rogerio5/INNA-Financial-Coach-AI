"""Compatibilidade temporária para telegram_observability.slo_policy."""

import sys

from src.integracoes.telegram.observabilidade import (
    slo_policy as _implementation,
)

sys.modules[__name__] = _implementation
