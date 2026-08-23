"""Compatibilidade temporária para telegram_observability.worker_readiness."""

import sys

from src.integracoes.telegram.observabilidade import (
    worker_readiness as _implementation,
)

sys.modules[__name__] = _implementation
