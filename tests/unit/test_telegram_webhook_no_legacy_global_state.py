from __future__ import annotations

import ast
from pathlib import Path

from api import telegram_webhook


ROOT = Path(__file__).resolve().parents[2]


def test_legacy_global_state_attributes_do_not_exist():
    assert not hasattr(
        telegram_webhook,
        "USER_SESSIONS",
    )

    assert not hasattr(
        telegram_webhook,
        "USER_LAST_LANG",
    )


def test_webhook_source_has_no_legacy_global_references():
    target = ROOT / "api" / "telegram_webhook.py"

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    violations = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Name,
        ) and node.id in {
            "USER_SESSIONS",
            "USER_LAST_LANG",
        }:
            violations.append(
                (
                    node.id,
                    node.lineno,
                )
            )

    assert violations == []


def test_private_core_has_no_optional_bridge_branch():
    target = ROOT / "api" / "telegram_webhook.py"

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    core = next(
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == "_process_telegram_update_core"
    )

    conditions = []

    for node in ast.walk(core):
        if not isinstance(
            node,
            ast.If,
        ):
            continue

        try:
            condition = ast.unparse(node.test)
        except Exception:
            condition = ""

        if (
            "conversation_bridge is not None" in condition
            or "conversation_bridge is None" in condition
        ):
            conditions.append(
                (
                    node.lineno,
                    condition,
                )
            )

    # A validação inicial explícita contra None ainda é permitida.
    allowed = [item for item in conditions if item[1] == "conversation_bridge is None"]

    assert len(allowed) == 1
    assert len(conditions) == 1
