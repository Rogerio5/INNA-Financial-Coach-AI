"""Compatibilidade temporária para src.agents.blackboard_permissions."""

import sys

from src.plataforma.governanca.blackboard import (
    permissions as _implementation,
)

sys.modules[__name__] = _implementation
