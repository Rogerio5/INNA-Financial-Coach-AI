"""Compatibilidade temporária para src.agents.task_completion_blackboard."""

import sys

from src.plataforma.supervisao.task_completion import (
    blackboard as _implementation,
)

sys.modules[__name__] = _implementation
