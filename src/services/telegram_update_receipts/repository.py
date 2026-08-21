"""Compatibilidade temporária para telegram_update_receipts.repository."""

import sys

from src.integracoes.telegram.update_receipts import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation
