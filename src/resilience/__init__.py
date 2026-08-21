"""Compatibilidade temporária para src.resilience."""

import importlib
import sys

_CANONICAL = "src.compartilhado.resilience"
_LEGACY = "src.resilience"

_SUBMODULES = (
    "backoff",
    "circuit_breaker",
    "classification",
    "contracts",
    "deadline",
    "events",
    "policies",
    "runtime",
    "tracing",
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
