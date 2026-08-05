from __future__ import annotations

import ast
from pathlib import Path


ENV_EXAMPLE = Path(".env.example")

DEPLOY_DOCUMENT = Path("docs/deploy/telegram_operational_readiness.md")

KUBERNETES_EXAMPLE = Path("docs/deploy/kubernetes_telegram_operational_probes.yaml")

ROUTER_PATH = Path("api/telegram_operational_status.py")

MAIN_PATH = Path("api/main.py")


REQUIRED_ENVIRONMENT_NAMES = {
    "INNA_INTERNAL_READY_ENABLED",
    "INNA_INTERNAL_OPERATIONS_TOKEN",
    "INNA_READINESS_CACHE_TTL_SECONDS",
    "INNA_READINESS_CONCURRENT_WAIT_SECONDS",
    "INNA_READINESS_EVALUATION_BUDGET_SECONDS",
}


def test_environment_example_exists():
    assert ENV_EXAMPLE.exists()


def test_environment_example_documents_variables():
    source = ENV_EXAMPLE.read_text(encoding="utf-8")

    for name in REQUIRED_ENVIRONMENT_NAMES:
        assert name in source


def test_environment_example_has_no_real_token():
    source = ENV_EXAMPLE.read_text(encoding="utf-8")

    token_lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip().startswith("INNA_INTERNAL_OPERATIONS_TOKEN=")
    ]

    assert token_lines

    assert all(line == "INNA_INTERNAL_OPERATIONS_TOKEN=" for line in token_lines)


def test_internal_route_is_disabled_by_default():
    source = ENV_EXAMPLE.read_text(encoding="utf-8")

    assert "INNA_INTERNAL_READY_ENABLED=false" in source


def test_deploy_document_exists():
    assert DEPLOY_DOCUMENT.exists()


def test_deploy_document_has_required_routes():
    source = DEPLOY_DOCUMENT.read_text(encoding="utf-8")

    assert "GET /health" in source
    assert "GET /ready" in source
    assert "GET /internal/ready" in source


def test_deploy_document_separates_probes():
    source = DEPLOY_DOCUMENT.read_text(encoding="utf-8")

    assert "livenessProbe" in source
    assert "readinessProbe" in source

    assert (
        "/health como livenessProbe" in source
        or "/health como `livenessProbe`" in source
    )

    assert (
        "/ready como readinessProbe" in source
        or "/ready como `readinessProbe`" in source
    )


def test_kubernetes_example_exists():
    assert KUBERNETES_EXAMPLE.exists()


def test_kubernetes_uses_correct_paths():
    source = KUBERNETES_EXAMPLE.read_text(encoding="utf-8")

    assert "startupProbe:" in source
    assert "livenessProbe:" in source
    assert "readinessProbe:" in source

    assert "path: /health" in source
    assert "path: /ready" in source

    assert "path: /internal/ready" not in source


def test_kubernetes_uses_named_port():
    source = KUBERNETES_EXAMPLE.read_text(encoding="utf-8")

    assert "name: http" in source
    assert "port: http" in source


def test_kubernetes_token_uses_secret_reference():
    source = KUBERNETES_EXAMPLE.read_text(encoding="utf-8")

    assert "secretKeyRef:" in source
    assert "internal-operations-token" in source


def test_internal_route_is_hidden_from_openapi():
    source = ROUTER_PATH.read_text(encoding="utf-8")

    tree = ast.parse(
        source,
        filename=str(ROUTER_PATH),
    )

    internal_route = next(
        node
        for node in ast.walk(tree)
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == "telegram_internal_readiness"
        )
    )

    decorators = "\n".join(
        ast.get_source_segment(
            source,
            decorator,
        )
        or ""
        for decorator in internal_route.decorator_list
    )

    assert "include_in_schema=False" in decorators


def test_main_includes_router_once():
    source = MAIN_PATH.read_text(encoding="utf-8")

    assert source.count("app.include_router(telegram_operational_router)") == 1


def test_deploy_files_have_no_private_values():
    combined = "\n".join(
        [
            ENV_EXAMPLE.read_text(encoding="utf-8"),
            DEPLOY_DOCUMENT.read_text(encoding="utf-8"),
            KUBERNETES_EXAMPLE.read_text(encoding="utf-8"),
        ]
    )

    forbidden = {
        "private-operations-secret",
        "test-operations-token",
        "postgresql://user:password",
        "TELEGRAM_BOT_TOKEN=private",
        "AIzaSy",
    }

    for value in forbidden:
        assert value not in combined
