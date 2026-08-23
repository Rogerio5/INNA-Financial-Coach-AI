"""Compatibilidade temporária para src.agents.human_review_interrupt_node."""

import sys

from src.plataforma.governanca.human_review import (
    interrupt_node as _implementation,
)

sys.modules[__name__] = _implementation
