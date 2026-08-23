"""Compatibilidade temporária para src.evaluation.agentic_benchmark."""

import importlib
import sys

_CANONICAL_PACKAGE = (
    "src.compartilhado.avaliacao.agentic_benchmark"
)

_LEGACY_PACKAGE = (
    "src.evaluation.agentic_benchmark"
)

_SUBMODULES = (
    "adapter",
    "benchmark_runner",
    "contracts",
    "dataset_loader",
    "framework_payloads",
    "offline_evaluator",
    "quality_gate",
    "result_contracts",
)

_implementation = importlib.import_module(
    _CANONICAL_PACKAGE
)

for _name in _SUBMODULES:

    _module = importlib.import_module(
        f"{_CANONICAL_PACKAGE}.{_name}"
    )

    sys.modules[
        f"{_LEGACY_PACKAGE}.{_name}"
    ] = _module

sys.modules[__name__] = _implementation
