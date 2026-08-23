"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.llm_alerts
"""

import sys

from src.plataforma.observabilidade import (
    llm_alerts as _implementation,
)

sys.modules[__name__] = _implementation
