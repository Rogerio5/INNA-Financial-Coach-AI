"""Compatibilidade temporária para src.agents.a2a_contract."""

import sys

from src.integracoes.a2a import (
    contract as _implementation,
)

sys.modules[__name__] = _implementation
