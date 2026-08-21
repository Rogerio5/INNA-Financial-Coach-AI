"""Compatibilidade temporária para src.agents.human_review."""

import sys

from src.plataforma.governanca.human_review import (
    lifecycle as _implementation,
)

sys.modules[__name__] = _implementation
