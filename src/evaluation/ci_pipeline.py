"""Compatibilidade temporária para src.evaluation.ci_pipeline."""

from __future__ import annotations

if __name__ == "__main__":
    from src.compartilhado.avaliacao.ci_pipeline import main

    raise SystemExit(main())

import sys

from src.compartilhado.avaliacao import (
    ci_pipeline as _implementation,
)

sys.modules[__name__] = _implementation
