"""Compatibilidade temporária para telegram_update_jobs.ingress."""

import sys

from src.integracoes.telegram.update_jobs import (
    ingress as _implementation,
)

sys.modules[__name__] = _implementation
