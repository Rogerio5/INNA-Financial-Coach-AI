"""Compatibilidade temporária para telegram_observability.productive_readiness_factory."""

import sys

from src.integracoes.telegram.observabilidade import (
    productive_readiness_factory as _implementation,
)

sys.modules[__name__] = _implementation
