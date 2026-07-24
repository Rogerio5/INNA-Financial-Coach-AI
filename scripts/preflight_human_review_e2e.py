from __future__ import annotations

import inspect
import sys
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.agents.graph import (
    consultar_estado_conversa,
    executar_nucleo_inna_persistente,
    retomar_revisao_humana_persistente,
)

from src.agents.persistence import (
    abrir_checkpointer_postgres,
    verificar_conexao_memoria,
)


GRAPH_PATH = Path(
    "src/agents/graph.py"
)

INTERRUPT_PATH = Path(
    "src/agents/human_review_interrupt_node.py"
)


def _assert_signature() -> None:
    execute_signature = inspect.signature(
        executar_nucleo_inna_persistente
    )

    resume_signature = inspect.signature(
        retomar_revisao_humana_persistente
    )

    execute_parameters = (
        execute_signature.parameters
    )

    resume_parameters = (
        resume_signature.parameters
    )

    required_execute = {
        "mensagem",
        "thread_id",
        "human_review_enabled",
    }

    missing_execute = (
        required_execute
        - set(execute_parameters)
    )

    if missing_execute:
        raise RuntimeError(
            "Parâmetros ausentes na execução "
            f"persistente: {sorted(missing_execute)}"
        )

    required_resume = {
        "thread_id",
        "decisao",
    }

    missing_resume = (
        required_resume
        - set(resume_parameters)
    )

    if missing_resume:
        raise RuntimeError(
            "Parâmetros ausentes na retomada: "
            f"{sorted(missing_resume)}"
        )

    print(
        "PERSISTENT_EXECUTION_SIGNATURE:",
        execute_signature,
    )

    print(
        "PERSISTENT_RESUME_SIGNATURE:",
        resume_signature,
    )

    print(
        "HUMAN_REVIEW_SIGNATURES_VALIDATED"
    )


def _assert_source_contract() -> None:
    graph_source = GRAPH_PATH.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    interrupt_source = (
        INTERRUPT_PATH.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )
    )

    graph_required = [
        "human_review_policy",
        "human_review_interrupt",
        "Command(",
        "resume=normalized_decision",
        "abrir_checkpointer_postgres",
        "thread_id=thread_id",
    ]

    interrupt_required = [
        "interrupt(",
        "allowed_actions",
        "review_id",
        "thread_id",
    ]

    missing_graph = [
        item
        for item in graph_required
        if item not in graph_source
    ]

    missing_interrupt = [
        item
        for item in interrupt_required
        if item not in interrupt_source
    ]

    if missing_graph:
        raise RuntimeError(
            "Contrato ausente em graph.py: "
            f"{missing_graph}"
        )

    if missing_interrupt:
        raise RuntimeError(
            "Contrato ausente no nó de interrupt: "
            f"{missing_interrupt}"
        )

    print(
        "HUMAN_REVIEW_GRAPH_SOURCE_VALIDATED"
    )


def _assert_checkpoint_connection() -> None:
    result = verificar_conexao_memoria()

    print(
        "CHECKPOINT_CONNECTION_RESULT:",
        result,
    )

    if not result.get("ok"):
        raise RuntimeError(
            "A memória operacional PostgreSQL "
            "não está disponível."
        )

    with abrir_checkpointer_postgres() as checkpointer:
        checkpointer.setup()

        checkpointer_type = (
            type(checkpointer).__name__
        )

        print(
            "CHECKPOINTER_TYPE:",
            checkpointer_type,
        )

        if (
            "Postgres"
            not in checkpointer_type
        ):
            raise RuntimeError(
                "O checkpointer ativo não parece "
                "ser PostgreSQL."
            )

    print(
        "POSTGRES_CHECKPOINTER_VALIDATED"
    )


def _assert_empty_thread_lookup() -> None:
    thread_id = (
        "preflight-hitl-"
        + uuid4().hex
    )

    result = consultar_estado_conversa(
        thread_id=thread_id
    )

    print(
        "EMPTY_THREAD_ID:",
        thread_id,
    )

    print(
        "EMPTY_THREAD_RESULT_TYPE:",
        type(result).__name__,
    )

    if result not in (
        None,
        {},
    ):
        if isinstance(result, dict):
            values = result.get(
                "values",
                result,
            )

            if values:
                raise RuntimeError(
                    "Um thread aleatório retornou "
                    "estado inesperado."
                )
        else:
            raise RuntimeError(
                "Formato inesperado na consulta "
                "de thread inexistente."
            )

    print(
        "EMPTY_THREAD_LOOKUP_VALIDATED"
    )


def main() -> None:
    _assert_signature()
    _assert_source_contract()
    _assert_checkpoint_connection()
    _assert_empty_thread_lookup()

    print(
        "HUMAN_REVIEW_E2E_PREFLIGHT_VALIDATED"
    )


if __name__ == "__main__":
    main()
