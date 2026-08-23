"""Compatibilidade temporaria para src.mcp_server.server.

Import normal:
preserva identidade com src.integracoes.mcp.server.

Execucao via:
python -m src.mcp_server.server

delega o entrypoint STDIO ao servidor canonico.
"""

import sys

from src.integracoes.mcp import (
    server as _implementation,
)


if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
