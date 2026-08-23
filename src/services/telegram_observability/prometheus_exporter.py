"""Compatibilidade temporária para telegram_observability.prometheus_exporter."""

import sys

from src.integracoes.telegram.observabilidade import (
    prometheus_exporter as _implementation,
)

sys.modules[__name__] = _implementation
