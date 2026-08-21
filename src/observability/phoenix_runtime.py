"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.phoenix.runtime
"""

import sys

from src.compartilhado.observabilidade.phoenix import (
    runtime as _implementation,
)

sys.modules[__name__] = _implementation
