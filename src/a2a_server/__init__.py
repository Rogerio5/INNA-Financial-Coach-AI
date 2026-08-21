"""Compatibilidade temporária para src.a2a_server."""

import importlib
import sys

_CANONICAL = "src.integracoes.a2a"
_LEGACY = "src.a2a_server"

_SUBMODULES = (
    "adapter",
    "security",
    "server",
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
