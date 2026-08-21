"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.phoenix.privacy
"""

import sys

from src.compartilhado.observabilidade.phoenix import (
    privacy as _implementation,
)

sys.modules[__name__] = _implementation
