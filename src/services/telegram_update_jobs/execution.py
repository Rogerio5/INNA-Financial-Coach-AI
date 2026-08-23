"""Compatibilidade temporária para telegram_update_jobs.execution."""

import sys

from src.integracoes.telegram.update_jobs import (
    execution as _implementation,
)

sys.modules[__name__] = _implementation
