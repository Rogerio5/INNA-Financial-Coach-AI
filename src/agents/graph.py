"""Compatibilidade temporaria para src.agents.graph.

Implementacao oficial:
src.plataforma.orquestracao.graph
"""

import sys

from src.plataforma.orquestracao import (
    graph as _implementation,
)

sys.modules[__name__] = _implementation
