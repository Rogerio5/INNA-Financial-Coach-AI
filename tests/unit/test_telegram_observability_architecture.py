from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PACKAGE = (
    ROOT
    / "src"
    / "services"
    / "telegram_observability"
)


def test_observability_package_has_no_prometheus_dependency():
    violations = []

    for path in PACKAGE.rglob("*.py"):
        source = path.read_text(
            encoding="utf-8",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

        for node in ast.walk(tree):
            module = None

            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    module = alias.name

                    if module.startswith(
                        "prometheus"
                    ):
                        violations.append(
                            (
                                path.name,
                                node.lineno,
                                module,
                            )
                        )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module
                    or ""
                )

                is_absolute_import = (
                    node.level == 0
                )

                is_external_prometheus = (
                    module == "prometheus"
                    or module.startswith(
                        "prometheus."
                    )
                    or module == "prometheus_client"
                    or module.startswith(
                        "prometheus_client."
                    )
                )

                if (
                    is_absolute_import
                    and is_external_prometheus
                ):
                    violations.append(
                        (
                            path.name,
                            node.lineno,
                            module,
                        )
                    )

    assert violations == []


def test_observability_contracts_have_no_io_calls():
    target = (
        PACKAGE
        / "contracts.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    forbidden_calls = {
        "print",
        "open",
        "connect",
        "requests",
        "urlopen",
    }

    violations = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        name = None

        if isinstance(
            node.func,
            ast.Name,
        ):
            name = node.func.id

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            name = node.func.attr

        if name in forbidden_calls:
            violations.append(
                (
                    node.lineno,
                    name,
                )
            )

    assert violations == []


def test_metric_labels_exclude_high_cardinality_ids():
    target = (
        PACKAGE
        / "contracts.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    forbidden = {
        "chat_id",
        "telegram_user_id",
        "update_id",
        "request_id",
        "receipt_id",
        "session_id",
    }

    tree = ast.parse(
        source,
        filename=str(target),
    )

    class_node = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
        and node.name
        == "TelegramConversationMetricRecord"
    )

    field_names = {
        statement.target.id
        for statement in class_node.body
        if isinstance(
            statement,
            ast.AnnAssign,
        )
        and isinstance(
            statement.target,
            ast.Name,
        )
    }

    assert (
        field_names
        & forbidden
    ) == set()
