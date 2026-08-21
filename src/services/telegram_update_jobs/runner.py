"""Compatibilidade temporária para telegram_update_jobs.runner."""

import sys

from src.integracoes.telegram.update_jobs import (
    runner as _implementation,
)

sys.modules[__name__] = _implementation
