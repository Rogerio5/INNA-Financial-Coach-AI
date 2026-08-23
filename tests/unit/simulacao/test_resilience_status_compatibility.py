from __future__ import annotations

from src.resilience import (
    FailureKind,
    classify_failure,
)


class FakeStatusError(Exception):
    def __init__(
        self,
        status,
    ) -> None:
        super().__init__(
            "provider detail must not affect classification"
        )
        self.status = status


class FakeCodeError(Exception):
    def __init__(
        self,
        code,
    ) -> None:
        super().__init__(
            "provider detail must not affect classification"
        )
        self.code = code


class FakeResponse:
    def __init__(
        self,
        *,
        status=None,
        status_code=None,
    ) -> None:
        self.status = status
        self.status_code = status_code


class FakeResponseError(Exception):
    def __init__(
        self,
        response,
    ) -> None:
        super().__init__(
            "provider detail must not affect classification"
        )
        self.response = response


def test_direct_numeric_status_429_is_rate_limit():
    assert (
        classify_failure(
            FakeStatusError(429)
        )
        == FailureKind.RATE_LIMIT
    )


def test_direct_numeric_status_503_is_upstream_5xx():
    assert (
        classify_failure(
            FakeStatusError(503)
        )
        == FailureKind.UPSTREAM_5XX
    )


def test_direct_numeric_status_401_is_authentication():
    assert (
        classify_failure(
            FakeStatusError(401)
        )
        == FailureKind.AUTHENTICATION
    )


def test_direct_numeric_status_403_is_authorization():
    assert (
        classify_failure(
            FakeStatusError(403)
        )
        == FailureKind.AUTHORIZATION
    )


def test_direct_numeric_status_400_is_invalid_request():
    assert (
        classify_failure(
            FakeStatusError(400)
        )
        == FailureKind.INVALID_REQUEST
    )


def test_google_code_429_remains_supported():
    assert (
        classify_failure(
            FakeCodeError(429)
        )
        == FailureKind.RATE_LIMIT
    )


def test_google_code_503_remains_supported():
    assert (
        classify_failure(
            FakeCodeError(503)
        )
        == FailureKind.UPSTREAM_5XX
    )


def test_response_status_remains_supported():
    assert (
        classify_failure(
            FakeResponseError(
                FakeResponse(
                    status=429
                )
            )
        )
        == FailureKind.RATE_LIMIT
    )


def test_response_status_code_remains_supported():
    assert (
        classify_failure(
            FakeResponseError(
                FakeResponse(
                    status_code=503
                )
            )
        )
        == FailureKind.UPSTREAM_5XX
    )


def test_textual_status_is_ignored_safely():
    result = classify_failure(
        FakeStatusError(
            "UNAVAILABLE"
        )
    )

    assert (
        result
        == FailureKind.UNKNOWN
    )
