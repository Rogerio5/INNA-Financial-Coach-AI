"""Compatibilidade temporária para src.agents.task_completion."""

import sys

from src.plataforma.supervisao.task_completion import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation
