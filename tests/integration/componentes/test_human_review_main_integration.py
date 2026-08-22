from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


EXPECTED_HUMAN_REVIEW_PATHS = {
    "/internal/human-reviews/register",
    "/internal/human-reviews/pending",
    "/internal/human-reviews/recover-stale",
    "/internal/human-reviews/{review_id}",
    "/internal/human-reviews/{review_id}/resolve",
}


def test_human_review_routes_are_registered_once(
) -> None:
    schema = app.openapi()
    paths = schema.get(
        "paths",
        {},
    )

    assert EXPECTED_HUMAN_REVIEW_PATHS.issubset(
        paths
    )

    registered_paths = [
        registered_path
        for registered_path in paths
        if registered_path.startswith(
            "/internal/human-reviews"
        )
    ]

    for expected_path in (
        EXPECTED_HUMAN_REVIEW_PATHS
    ):
        assert (
            registered_paths.count(
                expected_path
            )
            == 1
        )


def test_human_review_routes_require_authentication(
) -> None:
    client = TestClient(
        app
    )

    response = client.get(
        "/internal/human-reviews/pending"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": (
            "Requisição interna não autenticada."
        )
    }


def test_human_review_resolve_does_not_accept_reviewer_id(
) -> None:
    schema = app.openapi()

    resolve_operation = schema[
        "paths"
    ][
        (
            "/internal/human-reviews/"
            "{review_id}/resolve"
        )
    ][
        "post"
    ]

    request_schema_reference = (
        resolve_operation[
            "requestBody"
        ][
            "content"
        ][
            "application/json"
        ][
            "schema"
        ][
            "$ref"
        ]
    )

    schema_name = (
        request_schema_reference
        .rsplit(
            "/",
            1,
        )[-1]
    )

    request_schema = schema[
        "components"
    ][
        "schemas"
    ][
        schema_name
    ]

    properties = request_schema.get(
        "properties",
        {},
    )

    assert "reviewer_id" not in properties
    assert "thread_id" in properties
    assert "action" in properties


def test_recover_stale_is_not_captured_as_review_id(
) -> None:
    client = TestClient(
        app
    )

    response = client.post(
        "/internal/human-reviews/recover-stale",
        json={
            "timeout_seconds": 300,
        },
    )

    assert response.status_code == 401
    assert response.status_code != 405
