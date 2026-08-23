"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.governanca.execution_governance
"""

import sys

from src.plataforma.governanca import execution_governance as _implementation

sys.modules[__name__] = _implementation
