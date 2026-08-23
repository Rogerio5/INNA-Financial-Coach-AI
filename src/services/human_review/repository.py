"""Compatibilidade temporária para human_review.repository."""

import sys

from src.plataforma.governanca.human_review import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation
