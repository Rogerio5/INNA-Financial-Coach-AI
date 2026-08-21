"""Compatibilidade temporária para src.agents.shared_blackboard."""

import sys

from src.plataforma.governanca.blackboard import (
    models as _implementation,
)

sys.modules[__name__] = _implementation
