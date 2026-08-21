"""Compatibilidade temporária para human_review.service."""

import sys

from src.plataforma.governanca.human_review import (
    service as _implementation,
)

sys.modules[__name__] = _implementation
