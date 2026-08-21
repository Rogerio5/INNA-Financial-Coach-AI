"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.research_agent
"""

import sys

from src.compartilhado.rag.agentic import (
    research_agent as _implementation,
)

sys.modules[__name__] = _implementation
