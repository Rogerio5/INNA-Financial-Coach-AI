import pytest

from src.observability.phoenix_config import (
    PhoenixConfigurationError,
    load_phoenix_settings,
)


def _configure_valid_environment(monkeypatch):
    monkeypatch.setenv("PHOENIX_ENABLED", "true")
    monkeypatch.setenv("PHOENIX_API_KEY", "secret-test-value")
    monkeypatch.setenv(
        "PHOENIX_COLLECTOR_ENDPOINT",
        "https://example.test/s/workspace",
    )
    monkeypatch.setenv(
        "PHOENIX_PROJECT_NAME",
        "inna-test",
    )
    monkeypatch.setenv(
        "PHOENIX_CAPTURE_CONTENT",
        "false",
    )
    monkeypatch.setenv(
        "PHOENIX_TRACE_SAMPLE_RATE",
        "0.10",
    )


def test_load_phoenix_settings(monkeypatch):
    _configure_valid_environment(monkeypatch)

    settings = load_phoenix_settings()

    assert settings.enabled is True
    assert settings.ready is True
    assert settings.project_name == "inna-test"
    assert settings.capture_content is False
    assert settings.sample_rate == 0.10


@pytest.mark.parametrize(
    "value",
    ["-0.1", "1.1", "invalid"],
)
def test_rejects_invalid_sample_rate(monkeypatch, value):
    _configure_valid_environment(monkeypatch)
    monkeypatch.setenv(
        "PHOENIX_TRACE_SAMPLE_RATE",
        value,
    )

    with pytest.raises(PhoenixConfigurationError):
        load_phoenix_settings()


def test_disabled_configuration_does_not_require_key(monkeypatch):
    monkeypatch.setenv("PHOENIX_ENABLED", "false")
    monkeypatch.delenv("PHOENIX_API_KEY", raising=False)
    monkeypatch.delenv(
        "PHOENIX_COLLECTOR_ENDPOINT",
        raising=False,
    )

    settings = load_phoenix_settings()

    assert settings.enabled is False
    assert settings.ready is False
