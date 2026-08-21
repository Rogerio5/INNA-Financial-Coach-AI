"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.llm_notifications
"""

import sys

from src.plataforma.observabilidade import (
    llm_notifications as _implementation,
)

sys.modules[__name__] = _implementation
