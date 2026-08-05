from pathlib import Path

from scripts.security.validate_workflow_security import (
    validate_workflow,
)


def _error_rules(path: Path) -> set[str]:
    return {
        finding.rule_id
        for finding in validate_workflow(path)
        if finding.severity == "error"
    }


def test_local_postgres_test_credentials_are_allowed(
    tmp_path: Path,
) -> None:
    workflow = tmp_path / "local-database.yml"
    workflow.write_text(
        """
name: Local Test

on:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: local-test
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/test
    steps:
      - name: Checkout
        uses: actions/checkout@v4
""".lstrip(),
        encoding="utf-8",
    )

    rules = _error_rules(workflow)

    assert "possible-hardcoded-database-secret" not in rules


def test_remote_postgres_credentials_are_blocked(
    tmp_path: Path,
) -> None:
    workflow = tmp_path / "remote-database.yml"
    workflow.write_text(
        """
name: Remote Test

on:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: remote-test
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    env:
      DATABASE_URL: postgresql://user:password@example.com:5432/db
    steps:
      - name: Checkout
        uses: actions/checkout@v4
""".lstrip(),
        encoding="utf-8",
    )

    rules = _error_rules(workflow)

    assert "possible-hardcoded-database-secret" in rules


def test_gemini_api_key_is_blocked(
    tmp_path: Path,
) -> None:
    workflow = tmp_path / "gemini-key.yml"

    synthetic_api_key = "AI" + "za" + ("1" * 35)

    workflow.write_text(
        f"""
name: Gemini Test

on:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: gemini-test
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    env:
      GEMINI_API_KEY: {synthetic_api_key}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
""".lstrip(),
        encoding="utf-8",
    )

    rules = _error_rules(workflow)

    assert "possible-hardcoded-secret" in rules
