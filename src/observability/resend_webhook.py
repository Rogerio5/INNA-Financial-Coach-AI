"""
Compatibilidade temporaria.

Implementacao oficial:
src.integracoes.resend_webhook
"""

import sys

from src.integracoes import (
    resend_webhook as _implementation,
)

sys.modules[__name__] = _implementation
