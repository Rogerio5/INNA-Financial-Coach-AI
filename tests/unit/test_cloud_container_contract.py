from pathlib import Path

DOCKERFILE = Path("Dockerfile")
DOCKERIGNORE = Path(".dockerignore")


def _dockerfile() -> str:
    return DOCKERFILE.read_text(
        encoding="utf-8-sig"
    )


def _dockerignore() -> str:
    return DOCKERIGNORE.read_text(
        encoding="utf-8-sig"
    )


def test_container_uses_project_python_version():
    source = _dockerfile()

    assert source.startswith(
        "FROM python:3.12.1-slim"
    )


def test_container_runs_fastapi_with_dynamic_port():
    source = _dockerfile()

    assert "api.main:app" in source
    assert "--host 0.0.0.0" in source
    assert "${PORT:-8080}" in source
    assert "EXPOSE 8080" in source

    assert "--reload" not in source


def test_container_runs_as_non_root_user():
    source = _dockerfile()

    assert "useradd" in source
    assert "--uid 10001" in source
    assert "USER inna" in source

    assert (
        source.index("USER inna")
        > source.index("COPY --chown=inna:inna")
    )


def test_container_has_healthcheck():
    source = _dockerfile()

    assert "HEALTHCHECK" in source
    assert "/health" in source
    assert "127.0.0.1" in source


def test_container_uses_requirements_contract():
    source = _dockerfile()

    assert (
        "COPY requirements.txt"
        in source
    )

    assert (
        "-r /app/requirements.txt"
        in source
    )


def test_container_does_not_bake_environment_secrets():
    ignored = _dockerignore()

    required = (
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        ".git",
        ".venv",
    )

    for item in required:
        assert item in ignored


def test_container_excludes_local_runtime_artifacts():
    ignored = _dockerignore()

    required = (
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "artifacts",
        "reports",
        "*.sqlite",
        "*.db",
    )

    for item in required:
        assert item in ignored
