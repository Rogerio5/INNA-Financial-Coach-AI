"""Compatibilidade temporaria para src.agent_tools.catalog."""

import sys

from src.compartilhado.agent_tools import (
    catalog as _implementation,
)

sys.modules[__name__] = _implementation
