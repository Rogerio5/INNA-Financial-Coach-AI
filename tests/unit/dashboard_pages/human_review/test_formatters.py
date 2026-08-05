from datetime import UTC, datetime

from src.dashboard_pages.human_review.formatters import (
    formatar_acao_hitl,
    formatar_data_hora_hitl,
    formatar_duracao_hitl,
    formatar_percentual_hitl,
    formatar_risco_hitl,
    formatar_status_hitl,
    resumir_texto_hitl,
)


def test_formats_status_risk_and_action() -> None:
    assert formatar_status_hitl("resume_failed") == "Falha na retomada"

    assert formatar_risco_hitl("critical") == "Crítico"

    assert formatar_acao_hitl("approve") == "Aprovar"


def test_formats_datetime() -> None:
    value = datetime(
        2026,
        7,
        24,
        18,
        30,
        tzinfo=UTC,
    )

    result = formatar_data_hora_hitl(value)

    assert "24/07/2026" in result


def test_formats_duration() -> None:
    assert formatar_duracao_hitl(3_661) == "1h 1min 1s"

    assert formatar_duracao_hitl(0) == "0s"


def test_formats_percentage() -> None:
    assert formatar_percentual_hitl(0.875) == "87,5%"


def test_summarizes_long_text() -> None:
    result = resumir_texto_hitl(
        "A" * 200,
        limite=20,
    )

    assert len(result) == 20
    assert result.endswith("…")
