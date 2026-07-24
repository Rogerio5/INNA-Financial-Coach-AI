"""
Inicializa as tabelas do checkpointer LangGraph.
"""

from src.agents.persistence import (
    inicializar_memoria_agentes,
)


def main() -> None:
    resultado = inicializar_memoria_agentes()

    print(resultado["message"])

    if not resultado.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
