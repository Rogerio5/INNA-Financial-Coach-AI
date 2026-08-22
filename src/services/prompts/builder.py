"""Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.llm.prompts.builder
"""

import sys

from src.compartilhado.llm.prompts import (
    builder as _implementation,
)

sys.modules[__name__] = _implementation
