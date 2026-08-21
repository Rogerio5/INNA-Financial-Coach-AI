"""Compatibilidade temporária para src.agent_tools."""

import importlib
import sys

_CANONICAL = "src.compartilhado.agent_tools"
_LEGACY = "src.agent_tools"

_MODULES = (
    "communication_tools",
    "financial_history_tools",
    "financial_tools",
    "rag_tools",
    "report_tools",
    "catalog",
    "runtime",
)

_CORE_MODULES = (
    "contracts",
    "registry",
    "permissions",
    "executor",
)

_implementation = importlib.import_module(
    _CANONICAL
)

_core = importlib.import_module(
    f"{_CANONICAL}.core"
)

sys.modules[
    f"{_LEGACY}.core"
] = _core

for _name in _CORE_MODULES:

    _module = importlib.import_module(
        f"{_CANONICAL}.core.{_name}"
    )

    sys.modules[
        f"{_LEGACY}.core.{_name}"
    ] = _module

for _name in _MODULES:

    _module = importlib.import_module(
        f"{_CANONICAL}.{_name}"
    )

    sys.modules[
        f"{_LEGACY}.{_name}"
    ] = _module

sys.modules[__name__] = _implementation
