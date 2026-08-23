"""Compatibilidade temporária para telegram_update_jobs.repository."""

import sys

from src.integracoes.telegram.update_jobs import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation
