from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from api.main import app

from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    assinar_requisicao_interna,
)

from src.agents.graph import (
    _criar_config_execucao,
    _criar_estado_inicial,
    consultar_estado_conversa,
    criar_grafo_inna,
)

from src.agents.persistence import (
    abrir_checkpointer_postgres,
)

from src.database.connection import (
    cursor_postgres,
)

from src.services.human_review.service import (
    registrar_revisao_pendente,
)


client = TestClient(app)


def _resolve_run_suffix() -> str:
    explicit = (
        str(
            os.getenv(
                "HITL_E2E_RUN_ID",
                "",
            )
        )
        .strip()
        .lower()
    )

    if not explicit:
        return uuid4().hex[:12]

    if not re.fullmatch(
        r"[a-z0-9_-]{6,48}",
        explicit,
    ):
        raise RuntimeError("HITL_E2E_RUN_ID possui formato inválido.")

    return explicit


suffix = _resolve_run_suffix()

thread_id = f"hitl-e2e-thread-{suffix}"

review_id = f"hitl-e2e-review-{suffix}"

request_id = f"hitl-e2e-request-{suffix}"

reviewer_id = "hitl-e2e-admin"

resolve_path = f"/internal/human-reviews/{review_id}/resolve"


def _signed_headers(
    *,
    method: str,
    path: str,
    body: bytes,
) -> dict[str, str]:
    timestamp = int(time.time())

    signature = assinar_requisicao_interna(
        method=method,
        path=path,
        user_id=reviewer_id,
        request_id=request_id,
        timestamp=timestamp,
        body=body,
    )

    return {
        HEADER_USER_ID: reviewer_id,
        HEADER_REQUEST_ID: request_id,
        HEADER_TIMESTAMP: str(timestamp),
        HEADER_SIGNATURE: signature,
        "Content-Type": "application/json",
    }


def _interrupt_value(
    result: dict[str, Any],
) -> dict[str, Any]:
    interrupts = result.get(
        "__interrupt__",
        (),
    )

    if not interrupts:
        raise RuntimeError("O grafo não produziu __interrupt__.")

    first = interrupts[0]

    value = getattr(
        first,
        "value",
        first,
    )

    if not isinstance(value, dict):
        raise RuntimeError("Payload do interrupt possui formato inesperado.")

    return dict(value)


def _cleanup_review() -> None:
    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(
            """
            DELETE FROM public.human_reviews
            WHERE review_id = %s;
            """,
            (review_id,),
        )

        print(
            "REVIEW_CLEANUP_ROWS:",
            cursor.rowcount,
        )


def _cleanup_checkpoint(
    checkpointer: Any,
) -> None:
    delete_thread = getattr(
        checkpointer,
        "delete_thread",
        None,
    )

    if callable(delete_thread):
        delete_thread(thread_id)

        print("CHECKPOINT_THREAD_DELETED")
    else:
        print("CHECKPOINT_DELETE_NOT_SUPPORTED")


def main() -> None:
    config = _criar_config_execucao(
        thread_id=thread_id,
    )

    initial_state = _criar_estado_inicial(
        ("Execução controlada para validar a revisão humana."),
        thread_id=thread_id,
        usuario_id="hitl-e2e-user",
        idioma="pt",
        moeda="BRL",
    )

    review = {
        "review_id": review_id,
        "thread_id": thread_id,
        "status": "requested",
        "requested_by": "e2e_test",
        "reason": ("Revisão humana forçada para teste ponta a ponta."),
        "trigger": "forced_review",
        "risk_level": "medium",
        "payload": {
            "response": ("Resposta controlada aguardando aprovação."),
        },
        "metadata": {
            "test": True,
        },
    }

    initial_state.update(
        {
            "human_review_enabled": True,
            "human_review_force_required": True,
            "human_review_required": True,
            "human_review_current": review,
            "human_review_history": [
                review,
            ],
            "human_review_status": "requested",
            "human_review_count": 1,
            "max_human_reviews": 3,
            "structured_response": {
                "response": ("Resposta controlada aguardando aprovação."),
            },
        }
    )

    with abrir_checkpointer_postgres() as checkpointer:
        checkpointer.setup()

        graph = criar_grafo_inna(checkpointer=checkpointer)

        graph.update_state(
            config,
            initial_state,
            as_node="human_review_policy",
        )

        interrupted = graph.invoke(
            None,
            config=config,
        )

        interrupt_payload = _interrupt_value(interrupted)

        print(
            "INTERRUPT_REVIEW_ID:",
            interrupt_payload.get("review_id"),
        )

        print(
            "INTERRUPT_STATUS:",
            interrupt_payload.get("status"),
        )

        assert interrupt_payload["review_id"] == review_id

        assert interrupt_payload["thread_id"] == thread_id

        assert interrupt_payload["status"] in {
            "requested",
            "waiting",
            "pending",
        }

        print("REAL_LANGGRAPH_INTERRUPT_CREATED")

        registered = registrar_revisao_pendente(interrupt_payload)

        assert registered.record.status == "pending"

        print(
            "DATABASE_REVIEW_REGISTERED:",
            registered.record.status,
        )

        decision_payload = {
            "thread_id": thread_id,
            "action": "approve",
            "comment": ("Aprovação do teste E2E."),
        }

        decision_body = json.dumps(
            decision_payload,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ).encode("utf-8")

        response = client.post(
            resolve_path,
            content=decision_body,
            headers=_signed_headers(
                method="POST",
                path=resolve_path,
                body=decision_body,
            ),
        )

        print(
            "RESOLVE_STATUS_CODE:",
            response.status_code,
        )

        print(
            "RESOLVE_RESPONSE:",
            response.json(),
        )

        assert response.status_code == 200

        resolved = response.json()

        assert resolved["review_id"] == review_id

        assert resolved["thread_id"] == thread_id

        assert resolved["status"] == "approved"

        assert resolved["decision_action"] == "approve"

        assert resolved["reviewer_id"] == reviewer_id

        print("SIGNED_RESOLVE_API_APPROVED")

        checkpoint_state = consultar_estado_conversa(thread_id=thread_id)

        values = checkpoint_state.get(
            "values",
            checkpoint_state,
        )

        assert values["human_review_status"] == "approved"

        assert values["human_review_required"] is False

        assert values["human_review_current"]["review_id"] == review_id

        print("CHECKPOINT_APPROVED_STATE_VALIDATED")

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    status,
                    decision_action,
                    reviewer_id,
                    resume_route,
                    resolved_at
                FROM public.human_reviews
                WHERE review_id = %s;
                """,
                (review_id,),
            )

            database_row = cursor.fetchone()

        assert database_row is not None
        assert database_row["status"] == "approved"

        assert database_row["decision_action"] == "approve"

        assert database_row["reviewer_id"] == reviewer_id

        assert database_row["resolved_at"] is not None

        print("DATABASE_APPROVED_STATE_VALIDATED")

        print("HUMAN_REVIEW_FULL_E2E_RESUME_VALIDATED")

        _cleanup_checkpoint(checkpointer)


if __name__ == "__main__":
    try:
        main()
    finally:
        _cleanup_review()
