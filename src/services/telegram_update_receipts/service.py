"""Compatibilidade temporária para telegram_update_receipts.service."""

import sys

from src.integracoes.telegram.update_receipts import (
    service as _implementation,
)

sys.modules[__name__] = _implementation
