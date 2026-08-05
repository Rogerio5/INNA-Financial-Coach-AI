from src.observability.render_runtime import (
    collect_render_runtime_status,
)


def test_collect_render_runtime_local(
    monkeypatch,
):
    variables = [
        "RENDER",
        "RENDER_SERVICE_ID",
        "RENDER_SERVICE_NAME",
        "RENDER_SERVICE_TYPE",
        "RENDER_REGION",
        "RENDER_EXTERNAL_URL",
        "RENDER_GIT_COMMIT",
        "RENDER_INSTANCE_ID",
        "APP_ENV",
    ]

    for name in variables:
        monkeypatch.delenv(
            name,
            raising=False,
        )

    status = collect_render_runtime_status()

    assert status.running_on_render is False
    assert status.environment == "local"
    assert status.service_name == ("inna-financial-coach-ai")
    assert status.service_type == "local-process"
    assert status.region == "local"
    assert status.external_url_configured is False
    assert status.deploy_commit == ""
    assert status.instance_hash == ""
    assert status.uptime_seconds >= 0
    assert status.status == "local"


def test_collect_render_runtime_production(
    monkeypatch,
):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv(
        "APP_ENV",
        "production",
    )
    monkeypatch.setenv(
        "APP_ENV",
        "production",
    )
    monkeypatch.setenv(
        "RENDER_SERVICE_ID",
        "srv-private-value",
    )
    monkeypatch.setenv(
        "RENDER_SERVICE_NAME",
        "inna-api",
    )
    monkeypatch.setenv(
        "RENDER_SERVICE_TYPE",
        "web",
    )
    monkeypatch.setenv(
        "RENDER_REGION",
        "oregon",
    )
    monkeypatch.setenv(
        "RENDER_EXTERNAL_URL",
        "https://private-example.test",
    )
    monkeypatch.setenv(
        "RENDER_GIT_COMMIT",
        "1234567890abcdef",
    )
    monkeypatch.setenv(
        "RENDER_INSTANCE_ID",
        "instance-private-value",
    )

    status = collect_render_runtime_status()

    assert status.running_on_render is True
    assert status.environment == "production"
    assert status.service_name == "inna-api"
    assert status.service_type == "web"
    assert status.region == "oregon"
    assert status.external_url_configured is True
    assert status.deploy_commit == "1234567890ab"
    assert status.instance_hash
    assert status.instance_hash != "instance-private-value"
    assert status.status == "operational"

    payload = status.to_dict()

    assert "private-example" not in str(payload)
    assert "instance-private-value" not in str(payload)


def test_collect_render_runtime_preserves_staging_environment(
    monkeypatch,
):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv(
        "RENDER_SERVICE_NAME",
        "inna-staging",
    )

    status = collect_render_runtime_status()

    assert status.running_on_render is True
    assert status.environment == "staging"
    assert status.service_name == "inna-staging"
    assert status.status == "operational"
