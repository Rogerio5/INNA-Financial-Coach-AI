"""Compatibilidade temporária para telegram_observability.readiness_probes."""

import sys

from src.integracoes.telegram.observabilidade import (
    readiness_probes as _implementation,
)

sys.modules[__name__] = _implementation
