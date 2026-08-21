"""Compatibilidade temporária para human_review.contracts."""

import sys

from src.plataforma.governanca.human_review import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation
