from __future__ import annotations

from pathlib import Path


def test_supervisor_subprocess_uses_safe_decode_policy():
    source = Path(
        "src/agents/supervisor_deadline.py"
    ).read_text(
        encoding="utf-8",
    )

    assert 'encoding="utf-8"' in source
    assert 'errors="replace"' in source


def test_supervisor_deadline_keeps_hard_timeout():
    source = Path(
        "src/agents/supervisor_deadline.py"
    ).read_text(
        encoding="utf-8",
    )

    assert "subprocess.run(" in source
    assert "runtime.total_deadline_ms" in source
    assert "subprocess.TimeoutExpired" in source
