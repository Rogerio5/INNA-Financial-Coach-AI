"""Compatibilidade temporária para src.evaluation.live_payload_provider.

Contrato textual legado:
resolve_gemini_billing_mode()
"""

import sys

from src.compartilhado.avaliacao import (
    live_payload_provider as _implementation,
)

sys.modules[__name__] = _implementation
