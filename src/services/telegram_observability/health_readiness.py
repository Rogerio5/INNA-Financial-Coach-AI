"""Compatibilidade temporária para telegram_observability.health_readiness."""

import sys

from src.integracoes.telegram.observabilidade import (
    health_readiness as _implementation,
)

sys.modules[__name__] = _implementation
