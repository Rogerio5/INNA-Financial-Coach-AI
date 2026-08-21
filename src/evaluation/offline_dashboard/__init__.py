"""Compatibilidade temporária para src.evaluation.offline_dashboard."""

import sys

from src.interfaces.avaliacao import (
    offline_dashboard as _implementation,
)
from src.interfaces.avaliacao.offline_dashboard import (
    app as _app,
)
from src.interfaces.avaliacao.offline_dashboard import (
    data as _data,
)

sys.modules[
    "src.evaluation.offline_dashboard.app"
] = _app

sys.modules[
    "src.evaluation.offline_dashboard.data"
] = _data

sys.modules[__name__] = _implementation
