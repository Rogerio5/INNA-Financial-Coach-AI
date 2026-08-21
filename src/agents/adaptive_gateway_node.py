"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.gateway.adaptive_gateway_node
"""

import sys

from src.plataforma.gateway import adaptive_gateway_node as _implementation

sys.modules[__name__] = _implementation
