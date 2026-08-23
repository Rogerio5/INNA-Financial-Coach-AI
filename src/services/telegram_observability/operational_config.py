"""Compatibilidade temporária para telegram_observability.operational_config."""

import sys

from src.integracoes.telegram.observabilidade import (
    operational_config as _implementation,
)

sys.modules[__name__] = _implementation
