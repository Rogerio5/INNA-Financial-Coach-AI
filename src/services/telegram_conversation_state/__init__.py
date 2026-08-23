"""
Compatibilidade temporária do pacote
src.services.telegram_conversation_state.

Implementação oficial:
src.integracoes.telegram.conversation_state
"""

import sys

from src.integracoes.telegram import (
    conversation_state as _implementation,
)
from src.integracoes.telegram.conversation_state import (
    contracts as _contracts,
)
from src.integracoes.telegram.conversation_state import (
    repository as _repository,
)
from src.integracoes.telegram.conversation_state import (
    runtime as _runtime,
)
from src.integracoes.telegram.conversation_state import (
    store as _store,
)
from src.integracoes.telegram.conversation_state import (
    webhook_bridge as _webhook_bridge,
)

sys.modules[
    __name__ + ".contracts"
] = _contracts

sys.modules[
    __name__ + ".repository"
] = _repository

sys.modules[
    __name__ + ".runtime"
] = _runtime

sys.modules[
    __name__ + ".store"
] = _store

sys.modules[
    __name__ + ".webhook_bridge"
] = _webhook_bridge

sys.modules[__name__] = _implementation
