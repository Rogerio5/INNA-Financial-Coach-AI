"""Compatibilidade temporária para src.agents.human_review_policy_node."""

import sys

from src.plataforma.governanca.human_review import (
    policy_node as _implementation,
)

sys.modules[__name__] = _implementation
