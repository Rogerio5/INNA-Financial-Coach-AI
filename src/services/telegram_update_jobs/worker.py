"""Compatibilidade temporária para telegram_update_jobs.worker."""

import sys

from src.integracoes.telegram.update_jobs import (
    worker as _implementation,
)

sys.modules[__name__] = _implementation
