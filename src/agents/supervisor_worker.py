"""
Compatibilidade temporaria do Supervisor Worker.

Implementacao oficial:
src.plataforma.supervisao.supervisor_worker

Comportamentos preservados:

1. import src.agents.supervisor_worker
   -> alias real da implementacao nova

2. python -m src.agents.supervisor_worker
   -> continua executando main()
"""

from __future__ import annotations


if __name__ == "__main__":
    from src.plataforma.supervisao.supervisor_worker import (
        main,
    )

    raise SystemExit(main())

else:
    import sys

    from src.plataforma.supervisao import (
        supervisor_worker as _implementation,
    )

    sys.modules[__name__] = _implementation
