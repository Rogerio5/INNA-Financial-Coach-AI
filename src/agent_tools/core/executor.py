"""Compatibilidade temporaria para src.agent_tools.core.executor."""

import sys

from src.compartilhado.agent_tools.core import (
    executor as _implementation,
)

sys.modules[__name__] = _implementation
