from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "hitl-e2e.yml"

LIVE_TEST_PATH = (
    PROJECT_ROOT / "tests" / "integration" / "test_human_review_e2e_live.py"
)

E2E_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "test_human_review_e2e_resume.py"


def test_hitl_workflow_is_manual_only() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8-sig")

    assert "workflow_dispatch:" in content
    assert "\npull_request:" not in content
    assert "\npush:" not in content

    assert "contents: read" in content

    assert "cancel-in-progress: false" in content


def test_hitl_workflow_uses_protected_secrets() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8-sig")

    assert "secrets.DATABASE_URL" in content

    assert "secrets.INNA_INTERNAL_API_SIGNING_SECRET" in content

    assert "environment:" in content

    assert "name: hitl-e2e" in content

    assert 'RUN_HITL_E2E_TESTS: "1"' in content


def test_hitl_workflow_has_timeout_and_artifact() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8-sig")

    assert "timeout-minutes: 15" in content
    assert "actions/upload-artifact@v4" in content
    assert "if: always()" in content
    assert "retention-days: 7" in content


def test_live_test_is_explicitly_gated() -> None:
    content = LIVE_TEST_PATH.read_text(encoding="utf-8-sig")

    assert "RUN_HITL_E2E_TESTS" in content
    assert "@pytest.mark.skipif(" in content
    assert "timeout=180" in content

    assert "INNA_INTERNAL_API_SIGNING_SECRET" in content

    assert "DATABASE_URL" in content
    assert "_cleanup_test_data(" in content
    assert "finally:" in content


def test_live_test_validates_success_markers() -> None:
    content = LIVE_TEST_PATH.read_text(encoding="utf-8-sig")

    markers = [
        "REAL_LANGGRAPH_INTERRUPT_CREATED",
        "SIGNED_RESOLVE_API_APPROVED",
        "CHECKPOINT_APPROVED_STATE_VALIDATED",
        "DATABASE_APPROVED_STATE_VALIDATED",
        "HUMAN_REVIEW_FULL_E2E_RESUME_VALIDATED",
        "CHECKPOINT_THREAD_DELETED",
        "REVIEW_CLEANUP_ROWS: 1",
    ]

    for marker in markers:
        assert marker in content


def test_e2e_script_accepts_controlled_run_id() -> None:
    content = E2E_SCRIPT_PATH.read_text(encoding="utf-8-sig")

    assert "HITL_E2E_RUN_ID" in content

    assert "def _resolve_run_suffix()" in content
