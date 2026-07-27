from __future__ import annotations

import llmops_dashboard


def test_llmops_dashboard_exposes_main() -> None:
    assert callable(llmops_dashboard.main)
