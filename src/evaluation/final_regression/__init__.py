"""Compatibilidade temporária para src.evaluation.final_regression."""

import sys

from src.compartilhado.avaliacao import (
    final_regression as _implementation,
)
from src.compartilhado.avaliacao.final_regression import (
    runner as _runner,
)

sys.modules[
    "src.evaluation.final_regression.runner"
] = _runner

sys.modules[__name__] = _implementation
