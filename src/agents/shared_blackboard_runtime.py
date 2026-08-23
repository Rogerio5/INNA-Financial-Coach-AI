"""Compatibilidade temporária para src.agents.shared_blackboard_runtime."""

import sys

from src.plataforma.governanca.blackboard import (
    runtime as _implementation,
)

sys.modules[__name__] = _implementation
