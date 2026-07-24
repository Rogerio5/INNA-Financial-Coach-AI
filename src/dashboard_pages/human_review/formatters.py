from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


STATUS_LABELS = {
    "pending": "Pendente",
    "processing": "Em processamento",
    "approved": "Aprovada",
    "corrected": "Corrigida",
    "rejected": "Rejeitada",
    "cancelled": "Cancelada",
    "resume_failed": "Falha na retomada",
}

RISK_LABELS = {
    "": "Não informado",
    "low": "Baixo",
    "medium": "Médio",
    "high": "Alto",
    "critical": "Crítico",
}

ACTION_LABELS = {
    "approve": "Aprovar",
    "correct": "Corrigir",
    "reject": "Rejeitar",
    "cancel": "Cancelar",
}


def formatar_status_hitl(
    status: str,
) -> str:
    normalized = str(
        status or ""
    ).strip().lower()

    return STATUS_LABELS.get(
        normalized,
        normalized.replace(
            "_",
            " ",
        ).title()
        or "Não informado",
    )


def formatar_risco_hitl(
    risk_level: str,
) -> str:
    normalized = str(
        risk_level or ""
    ).strip().lower()

    return RISK_LABELS.get(
        normalized,
        normalized.replace(
            "_",
            " ",
        ).title()
        or "Não informado",
    )


def formatar_acao_hitl(
    action: str,
) -> str:
    normalized = str(
        action or ""
    ).strip().lower()

    return ACTION_LABELS.get(
        normalized,
        normalized.replace(
            "_",
            " ",
        ).title()
        or "Não informado",
    )


def formatar_data_hora_hitl(
    value: datetime | str | None,
    *,
    fallback: str = "—",
) -> str:
    if value in (
        None,
        "",
    ):
        return fallback

    parsed: datetime

    if isinstance(
        value,
        datetime,
    ):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError:
            return fallback

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=UTC
        )

    return parsed.astimezone().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def formatar_duracao_hitl(
    seconds: float | int | None,
    *,
    fallback: str = "—",
) -> str:
    if seconds is None:
        return fallback

    try:
        total_seconds = max(
            0,
            int(round(float(seconds))),
        )
    except (
        TypeError,
        ValueError,
    ):
        return fallback

    days, remainder = divmod(
        total_seconds,
        86_400,
    )

    hours, remainder = divmod(
        remainder,
        3_600,
    )

    minutes, seconds_part = divmod(
        remainder,
        60,
    )

    parts: list[str] = []

    if days:
        parts.append(
            f"{days}d"
        )

    if hours:
        parts.append(
            f"{hours}h"
        )

    if minutes:
        parts.append(
            f"{minutes}min"
        )

    if (
        seconds_part
        or not parts
    ):
        parts.append(
            f"{seconds_part}s"
        )

    return " ".join(parts)


def formatar_percentual_hitl(
    value: float | int | None,
    *,
    casas_decimais: int = 1,
) -> str:
    if value is None:
        return "—"

    try:
        percentage = float(
            value
        ) * 100
    except (
        TypeError,
        ValueError,
    ):
        return "—"

    return (
        f"{percentage:.{casas_decimais}f}%"
        .replace(
            ".",
            ",",
        )
    )


def resumir_texto_hitl(
    value: Any,
    *,
    limite: int = 100,
) -> str:
    text = " ".join(
        str(value or "").split()
    )

    if not text:
        return "—"

    if len(text) <= limite:
        return text

    return (
        text[: max(1, limite - 1)].rstrip()
        + "…"
    )


def formatar_identidade_hitl(
    value: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    return normalized or "Não atribuído"


__all__ = [
    "ACTION_LABELS",
    "RISK_LABELS",
    "STATUS_LABELS",
    "formatar_acao_hitl",
    "formatar_data_hora_hitl",
    "formatar_duracao_hitl",
    "formatar_identidade_hitl",
    "formatar_percentual_hitl",
    "formatar_risco_hitl",
    "formatar_status_hitl",
    "resumir_texto_hitl",
]
