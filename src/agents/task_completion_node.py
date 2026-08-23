"""Compatibilidade temporária para src.agents.task_completion_node."""

import sys

from src.plataforma.supervisao.task_completion import (
    node as _implementation,
)

sys.modules[__name__] = _implementation
