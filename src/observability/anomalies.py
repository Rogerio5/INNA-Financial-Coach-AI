"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.anomalies
"""

import sys

from src.plataforma.observabilidade import (
    anomalies as _implementation,
)

sys.modules[__name__] = _implementation
