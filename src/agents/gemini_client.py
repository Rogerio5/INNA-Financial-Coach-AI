"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.supervisao.gemini_client
"""

import sys

from src.plataforma.supervisao import gemini_client as _implementation

sys.modules[__name__] = _implementation
