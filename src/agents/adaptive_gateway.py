"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.gateway.adaptive_gateway
"""

import sys

from src.plataforma.gateway import adaptive_gateway as _implementation

sys.modules[__name__] = _implementation
