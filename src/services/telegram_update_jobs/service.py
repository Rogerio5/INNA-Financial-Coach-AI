"""Compatibilidade temporária para telegram_update_jobs.service."""

import sys

from src.integracoes.telegram.update_jobs import (
    service as _implementation,
)

sys.modules[__name__] = _implementation
