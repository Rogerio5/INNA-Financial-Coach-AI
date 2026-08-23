"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.phoenix.config
"""

import sys

from src.compartilhado.observabilidade.phoenix import (
    config as _implementation,
)

sys.modules[__name__] = _implementation
