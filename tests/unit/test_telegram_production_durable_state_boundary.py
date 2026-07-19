from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}

LEGACY_COMPATIBILITY_WRAPPER = (
    "_process_telegram_update_with_optional_bridge"
)

LEGACY_PROCESSOR = (
    "_process_legacy_telegram_update"
)


def _ignored(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_DIRECTORIES
        for part in path.parts
    )


def _call_name(
    node: ast.Call,
) -> str | None:
    if isinstance(
        node.func,
        ast.Name,
    ):
        return node.func.id

    if isinstance(
        node.func,
        ast.Attribute,
    ):
        return node.func.attr

    return None


def _build_parent_map(
    tree: ast.AST,
) -> dict[ast.AST, ast.AST]:
    parents = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(
            parent
        ):
            parents[child] = parent

    return parents


def _find_owner(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
):
    current = parents.get(
        node
    )

    while current is not None:
        if isinstance(
            current,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            return current

        current = parents.get(
            current
        )

    return None


def test_production_callers_require_bridge_except_legacy_processor():
    violations = []
    controlled_legacy_calls = []

    for path in ROOT.rglob(
        "*.py"
    ):
        relative = path.relative_to(
            ROOT
        )

        if _ignored(relative):
            continue

        if relative.parts[0] == "tests":
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

        parents = _build_parent_map(
            tree
        )

        for node in ast.walk(tree):
            if not isinstance(
                node,
                ast.Call,
            ):
                continue

            if (
                _call_name(node)
                != "process_telegram_update"
            ):
                continue

            keyword_names = {
                keyword.arg
                for keyword in node.keywords
                if keyword.arg is not None
            }

            bridge_keyword = next(
                (
                    keyword
                    for keyword in node.keywords
                    if keyword.arg
                    == "conversation_bridge"
                ),
                None,
            )

            owner = _find_owner(
                node,
                parents,
            )

            owner_name = (
                owner.name
                if owner is not None
                else "<module>"
            )

            is_controlled_legacy_call = (
                relative.as_posix()
                == "api/telegram_webhook.py"
                and owner_name
                == LEGACY_PROCESSOR
                and bridge_keyword is not None
                and isinstance(
                    bridge_keyword.value,
                    ast.Constant,
                )
                and bridge_keyword.value.value is None
            )

            if is_controlled_legacy_call:
                controlled_legacy_calls.append(
                    (
                        relative.as_posix(),
                        node.lineno,
                        owner_name,
                    )
                )
                continue

            if (
                "conversation_bridge"
                not in keyword_names
            ):
                violations.append(
                    (
                        relative.as_posix(),
                        node.lineno,
                        owner_name,
                    )
                )

    assert violations == []

    assert len(
        controlled_legacy_calls
    ) == 1

    assert controlled_legacy_calls[0][0] == (
        "api/telegram_webhook.py"
    )

    assert controlled_legacy_calls[0][2] == (
        LEGACY_PROCESSOR
    )


def test_legacy_processor_passes_explicit_none_to_main_processor():
    target = (
        ROOT
        / "api"
        / "telegram_webhook.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    legacy_processor = next(
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == LEGACY_PROCESSOR
    )

    calls = [
        node
        for node in ast.walk(
            legacy_processor
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and _call_name(node)
            == "process_telegram_update"
        )
    ]

    assert len(calls) == 1

    bridge_keyword = next(
        (
            keyword
            for keyword in calls[0].keywords
            if keyword.arg
            == "conversation_bridge"
        ),
        None,
    )

    assert bridge_keyword is not None

    assert isinstance(
        bridge_keyword.value,
        ast.Constant,
    )

    assert (
        bridge_keyword.value.value
        is None
    )


def test_optional_wrapper_has_explicit_legacy_and_durable_paths():
    target = (
        ROOT
        / "api"
        / "telegram_webhook.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    wrapper = next(
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name
        == LEGACY_COMPATIBILITY_WRAPPER
    )

    legacy_calls = 0
    durable_calls = 0
    has_explicit_none_branch = False

    for node in ast.walk(
        wrapper
    ):
        if isinstance(
            node,
            ast.If,
        ):
            try:
                condition = ast.unparse(
                    node.test
                )
            except Exception:
                condition = ""

            if (
                condition
                == "conversation_bridge is None"
            ):
                has_explicit_none_branch = True

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        name = _call_name(
            node
        )

        if name == LEGACY_PROCESSOR:
            legacy_calls += 1

        if name == "process_telegram_update":
            keyword_names = {
                keyword.arg
                for keyword in node.keywords
                if keyword.arg is not None
            }

            if (
                "conversation_bridge"
                in keyword_names
            ):
                durable_calls += 1

    assert has_explicit_none_branch is True
    assert legacy_calls == 1
    assert durable_calls == 1


def test_worker_creates_one_bridge_and_forwards_it():
    target = (
        ROOT
        / "src"
        / "channels"
        / "telegram_update_worker.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    loader = next(
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name
        == "load_telegram_processor"
    )

    factory_calls = 0
    bridge_forwarded = False

    for node in ast.walk(loader):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        name = _call_name(
            node
        )

        if name == (
            "create_postgres_telegram_webhook_"
            "conversation_bridge"
        ):
            factory_calls += 1

        if name == "process_telegram_update":
            keyword_names = {
                keyword.arg
                for keyword in node.keywords
                if keyword.arg is not None
            }

            bridge_forwarded = (
                "conversation_bridge"
                in keyword_names
            )

    assert factory_calls == 1
    assert bridge_forwarded is True


def test_worker_does_not_import_or_call_legacy_processor():
    target = (
        ROOT
        / "src"
        / "channels"
        / "telegram_update_worker.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    assert (
        LEGACY_PROCESSOR
        not in source
    )


def test_durable_helpers_do_not_reference_legacy_globals():
    target = (
        ROOT
        / "api"
        / "telegram_webhook.py"
    )

    source = target.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(target),
    )

    durable_helpers = {
        "_load_or_open_durable_telegram_session",
        "_sync_and_save_durable_telegram_session",
        "_delete_durable_telegram_session",
        "_resolve_durable_telegram_language",
    }

    violations = []

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name not in durable_helpers:
            continue

        for child in ast.walk(node):
            if not isinstance(
                child,
                ast.Name,
            ):
                continue

            if child.id in {
                "USER_SESSIONS",
                "USER_LAST_LANG",
            }:
                violations.append(
                    (
                        node.name,
                        child.id,
                        child.lineno,
                    )
                )

    assert violations == []

def test_tests_do_not_call_main_processor_without_bridge():
    violations = []

    for path in (
        ROOT
        / "tests"
    ).rglob(
        "*.py"
    ):
        relative = path.relative_to(
            ROOT
        )

        if _ignored(relative):
            continue

        if path == Path(__file__).resolve():
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

        for node in ast.walk(tree):
            if not isinstance(
                node,
                ast.Call,
            ):
                continue

            if (
                _call_name(node)
                != "process_telegram_update"
            ):
                continue

            keyword_names = {
                keyword.arg
                for keyword in node.keywords
                if keyword.arg is not None
            }

            if (
                "conversation_bridge"
                not in keyword_names
            ):
                violations.append(
                    (
                        relative.as_posix(),
                        node.lineno,
                    )
                )

    assert violations == []

