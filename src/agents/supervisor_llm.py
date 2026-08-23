"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.supervisao.supervisor_llm
"""

import sys

from src.plataforma.supervisao import supervisor_llm as _implementation

sys.modules[__name__] = _implementation
