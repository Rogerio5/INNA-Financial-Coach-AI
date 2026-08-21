"""Compatibilidade temporária para src.agents.human_review_policy."""

import sys

from src.plataforma.governanca.human_review import (
    policy as _implementation,
)

sys.modules[__name__] = _implementation
