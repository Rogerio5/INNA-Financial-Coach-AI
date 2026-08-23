"""Compatibilidade temporária para telegram_observability.structured_logging."""

import sys

from src.integracoes.telegram.observabilidade import (
    structured_logging as _implementation,
)

sys.modules[__name__] = _implementation
