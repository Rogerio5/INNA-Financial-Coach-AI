"""Compatibilidade temporária para human_review.admin_contracts."""

import sys

from src.plataforma.governanca.human_review import (
    admin_contracts as _implementation,
)

sys.modules[__name__] = _implementation
