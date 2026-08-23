"""Compatibilidade temporária para src.agents.team_hierarchy."""

import sys

from src.plataforma.roteamento import (
    team_hierarchy as _implementation,
)

sys.modules[__name__] = _implementation
