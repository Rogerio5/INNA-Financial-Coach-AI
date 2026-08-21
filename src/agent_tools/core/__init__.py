"""Compatibilidade temporária para src.agent_tools.core."""

import importlib
import sys

_CANONICAL = "src.compartilhado.agent_tools.core"
_LEGACY = "src.agent_tools.core"

_SUBMODULES = (
    "contracts",
    "registry",
    "permissions",
    "executor",
)

_implementation = importlib.import_module(
    _CANONICAL
)

for _name in _SUBMODULES:

    _module = importlib.import_module(
        f"{_CANONICAL}.{_name}"
    )

    sys.modules[
        f"{_LEGACY}.{_name}"
    ] = _module

sys.modules[__name__] = _implementation
