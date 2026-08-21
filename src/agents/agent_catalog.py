"""Compatibilidade temporária para src.agents.agent_catalog."""

import sys

from src.plataforma.registro import (
    agent_catalog as _implementation,
)

sys.modules[__name__] = _implementation
