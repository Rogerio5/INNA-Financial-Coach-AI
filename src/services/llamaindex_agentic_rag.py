"""Compatibilidade temporaria para o runtime LlamaIndex Agentic RAG.

Implementacao oficial:
src.compartilhado.rag.agentic.llamaindex_runtime
"""

import sys

from src.compartilhado.rag.agentic import (
    llamaindex_runtime as _implementation,
)

sys.modules[__name__] = _implementation
