"""Compatibilidade temporária para src.evaluation.mcp_simulated."""

import sys

from src.compartilhado.avaliacao import (
    mcp_simulated as _implementation,
)
from src.compartilhado.avaliacao.mcp_simulated import (
    harness as _harness,
)

sys.modules[
    "src.evaluation.mcp_simulated.harness"
] = _harness

sys.modules[__name__] = _implementation
