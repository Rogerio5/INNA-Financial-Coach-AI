"""Compatibilidade temporária para human_review.exceptions."""

import sys

from src.plataforma.governanca.human_review import (
    exceptions as _implementation,
)

sys.modules[__name__] = _implementation
