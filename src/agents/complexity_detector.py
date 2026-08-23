"""Compatibilidade temporária para src.agents.complexity_detector."""

import sys

from src.plataforma.gateway import (
    complexity_detector as _implementation,
)

sys.modules[__name__] = _implementation
