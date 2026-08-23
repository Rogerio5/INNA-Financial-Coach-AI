"""Compatibilidade temporaria para src.agent_tools.runtime."""

import sys

from src.compartilhado.agent_tools import (
    runtime as _implementation,
)

sys.modules[__name__] = _implementation
