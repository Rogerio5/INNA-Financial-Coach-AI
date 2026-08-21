"""Compatibilidade temporária para human_review.admin_queries."""

import sys

from src.plataforma.governanca.human_review import (
    admin_queries as _implementation,
)

sys.modules[__name__] = _implementation
