"""Pre-voo read-only da base financeira para o Neon."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExistingDocument:
    database_id: int
    nome_logico: str | None
    content_hash: str | None
    versao: int | None
    ativo: bool | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DocumentPreflightDecision:
    nome_logico: str
    content_hash: str
    action: str
    existing_database_id: int | None
    existing_version: int | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_documents(
    planned_documents: Sequence[Mapping[str, Any]],
    existing_by_logical_name: Mapping[str, ExistingDocument],
    existing_by_hash: Mapping[str, Sequence[ExistingDocument]],
) -> tuple[DocumentPreflightDecision, ...]:
    decisions: list[DocumentPreflightDecision] = []

    for document in planned_documents:
        logical_name = str(document["nome_logico"])
        content_hash = str(document["content_hash"])
        planned_version = int(document["versao"])

        logical_match = existing_by_logical_name.get(logical_name)
        hash_matches = tuple(existing_by_hash.get(content_hash, ()))

        if logical_match is not None:
            if logical_match.content_hash == content_hash:
                decisions.append(
                    DocumentPreflightDecision(
                        nome_logico=logical_name,
                        content_hash=content_hash,
                        action="skip_exact_existing",
                        existing_database_id=logical_match.database_id,
                        existing_version=logical_match.versao,
                        reason="Mesmo nome logico e mesmo content hash.",
                    )
                )
                continue

            if (
                logical_match.versao is not None
                and planned_version <= logical_match.versao
            ):
                decisions.append(
                    DocumentPreflightDecision(
                        nome_logico=logical_name,
                        content_hash=content_hash,
                        action="block_version_conflict",
                        existing_database_id=logical_match.database_id,
                        existing_version=logical_match.versao,
                        reason=(
                            "Nome logico existente com hash diferente "
                            "e versao planejada nao superior."
                        ),
                    )
                )
                continue

            decisions.append(
                DocumentPreflightDecision(
                    nome_logico=logical_name,
                    content_hash=content_hash,
                    action="insert_new_version",
                    existing_database_id=logical_match.database_id,
                    existing_version=logical_match.versao,
                    reason="Nome logico existente, novo hash e versao superior.",
                )
            )
            continue

        foreign_hash_matches = tuple(
            match for match in hash_matches if match.nome_logico != logical_name
        )

        if foreign_hash_matches:
            match = foreign_hash_matches[0]

            decisions.append(
                DocumentPreflightDecision(
                    nome_logico=logical_name,
                    content_hash=content_hash,
                    action="block_duplicate_content",
                    existing_database_id=match.database_id,
                    existing_version=match.versao,
                    reason=("Mesmo content hash ja existe com outro nome logico."),
                )
            )
            continue

        decisions.append(
            DocumentPreflightDecision(
                nome_logico=logical_name,
                content_hash=content_hash,
                action="insert_new",
                existing_database_id=None,
                existing_version=None,
                reason="Documento ainda nao existe no banco.",
            )
        )

    return tuple(decisions)


def summarize_decisions(
    decisions: Sequence[DocumentPreflightDecision],
    *,
    planned_chunk_count: int,
    existing_chunk_ids: Sequence[str],
) -> dict[str, Any]:
    action_counts: dict[str, int] = {}

    for decision in decisions:
        action_counts[decision.action] = action_counts.get(decision.action, 0) + 1

    blocking_actions = {
        "block_version_conflict",
        "block_duplicate_content",
    }

    blocking_document_count = sum(
        count for action, count in action_counts.items() if action in blocking_actions
    )

    existing_chunk_count = len(set(existing_chunk_ids))

    return {
        "planned_document_count": len(decisions),
        "planned_chunk_count": planned_chunk_count,
        "action_counts": dict(sorted(action_counts.items())),
        "blocking_document_count": blocking_document_count,
        "existing_chunk_id_count": existing_chunk_count,
        "new_chunk_id_count": planned_chunk_count - existing_chunk_count,
        "preflight_passed": (
            len(decisions) == 16
            and planned_chunk_count == 35
            and blocking_document_count == 0
            and existing_chunk_count == 0
        ),
    }


__all__ = [
    "DocumentPreflightDecision",
    "ExistingDocument",
    "analyze_documents",
    "summarize_decisions",
]
