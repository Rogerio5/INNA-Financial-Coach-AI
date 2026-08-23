"""Compatibilidade temporária para src.evaluation.mcp_simulated.harness."""

import sys

from src.compartilhado.avaliacao.mcp_simulated import (
    harness as _implementation,
)

sys.modules[__name__] = _implementation
