"""Compatibilidade temporaria para src.agent_tools.report_tools."""

import sys

from src.compartilhado.agent_tools import (
    report_tools as _implementation,
)

sys.modules[__name__] = _implementation
