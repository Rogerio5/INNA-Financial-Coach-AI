from __future__ import annotations

import pytest


def _event():
    from src.observability.planner_metrics import (
        PlannerMetricEvent,
    )

    return PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="gemini",
        cache_hit=False,
        plan_source="gemini",
        plan_valid=True,
        fallback_used=False,
        duration_ms=125.5,
    )


def test_create_table_sql_is_privacy_safe():
    from src.observability.planner_metrics import (
        _build_create_table_sql,
    )

    sql = _build_create_table_sql().lower()

    assert "planner_metric_events_inna" in sql
    assert "created_at" in sql
    assert "planner_mode" in sql
    assert "query_complexity" in sql
    assert "planner_route" in sql
    assert "cache_hit" in sql
    assert "plan_source" in sql
    assert "plan_valid" in sql
    assert "fallback_used" in sql
    assert "duration_ms" in sql

    forbidden = (
        "question",
        "pergunta",
        "prompt",
        "response",
        "resposta",
        "user_id",
        "usuario_id",
        "content",
    )

    for field in forbidden:
        assert field not in sql


def test_create_table_sql_has_required_indexes():
    from src.observability.planner_metrics import (
        _build_create_table_sql,
    )

    sql = _build_create_table_sql().lower()

    assert (
        "idx_planner_metrics_created_at"
        in sql
    )

    assert (
        "idx_planner_metrics_route_created_at"
        in sql
    )

    assert (
        "idx_planner_metrics_complexity_created_at"
        in sql
    )


def test_insert_payload_contains_only_safe_fields():
    from src.observability.planner_metrics import (
        _event_to_insert_payload,
    )

    payload = _event_to_insert_payload(
        _event()
    )

    assert payload == {
        "planner_mode": "adaptive",
        "query_complexity": "complex",
        "planner_route": "gemini",
        "cache_hit": False,
        "plan_source": "gemini",
        "plan_valid": True,
        "fallback_used": False,
        "duration_ms": 125.5,
        "planner_outcome": "success",
    }


def test_persist_event_uses_parameterized_values(
    monkeypatch,
):
    from src.observability import planner_metrics

    execute_calls = []

    class FakeCursor:
        def execute(
            self,
            statement,
            params=None,
        ):
            execute_calls.append(
                (
                    str(statement),
                    params,
                )
            )

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return False

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return False

    monkeypatch.setattr(
        planner_metrics,
        "_connect_postgres",
        lambda: FakeConnection(),
    )

    result = planner_metrics._persist_event(
        _event()
    )

    assert result is True

    insert_calls = [
        call
        for call in execute_calls
        if (
            "insert into"
            in call[0].lower()
        )
    ]

    assert len(insert_calls) == 1

    sql, params = insert_calls[0]

    assert (
        "planner_metric_events_inna"
        in sql.lower()
    )

    assert params is not None

    assert (
        params["planner_route"]
        == "gemini"
    )

    assert (
        params["query_complexity"]
        == "complex"
    )


def test_persist_event_rolls_back_on_failure(
    monkeypatch,
):
    from src.observability import planner_metrics

    state = {
        "rollback": False,
    }

    class FakeCursor:
        def execute(
            self,
            statement,
            params=None,
        ):
            del statement, params

            raise RuntimeError(
                "insert failed"
            )

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return False

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

        def rollback(self):
            state["rollback"] = True

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return False

    monkeypatch.setattr(
        planner_metrics,
        "_connect_postgres",
        lambda: FakeConnection(),
    )

    with pytest.raises(RuntimeError):
        planner_metrics._persist_event(
            _event()
        )

    assert state["rollback"] is True


def test_public_record_stays_fail_open_when_neon_fails(
    monkeypatch,
):
    from src.observability import planner_metrics

    def fail(*args, **kwargs):
        del args, kwargs
        raise RuntimeError(
            "neon unavailable"
        )

    monkeypatch.setattr(
        planner_metrics,
        "_persist_event",
        fail,
    )

    result = (
        planner_metrics.record_planner_metric_event(
            _event()
        )
    )

    assert result is False


def test_repository_does_not_require_user_content():
    event = _event()

    assert not hasattr(
        event,
        "question",
    )

    assert not hasattr(
        event,
        "user_id",
    )

    assert not hasattr(
        event,
        "prompt",
    )

    assert not hasattr(
        event,
        "response",
    )

def test_load_database_url_falls_back_to_dotenv(
    monkeypatch,
    tmp_path,
):
    from src.observability import planner_metrics

    env_path = tmp_path / ".env"

    env_path.write_text(
        (
            "DATABASE_URL="
            "postgresql://example.invalid/test"
            "\n"
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(
        tmp_path
    )

    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    result = (
        planner_metrics._load_database_url()
    )

    assert (
        result
        == "postgresql://example.invalid/test"
    )
