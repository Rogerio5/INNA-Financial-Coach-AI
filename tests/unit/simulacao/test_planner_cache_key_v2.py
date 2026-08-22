import src.agentic_rag.planner_cache as planner_cache


def _key(
    *,
    question: str = "Compare Tesouro Selic e CDB.",
    language: str = "pt",
    intent: str = "consulta_rag",
    trusted: bool = False,
) -> str:
    return planner_cache.build_planner_cache_key(
        question=question,
        language=language,
        intent=intent,
        trusted_user_context_available=trusted,
    )


def test_cache_key_uses_v2_namespace():
    key = _key()

    assert key.startswith(
        "inna:planner:v2:"
    )


def test_equivalent_queries_share_key():
    first = _key(
        question=(
            "Compare Tesouro Selic e CDB."
        ),
    )

    second = _key(
        question=(
            "  compare   TESOURO SELIC e CDB.  "
        ),
    )

    assert first == second


def test_language_is_normalized():
    first = _key(
        language="PT",
    )

    second = _key(
        language="pt",
    )

    assert first == second


def test_different_intent_changes_key():
    first = _key(
        intent="consulta_rag",
    )

    second = _key(
        intent="relatorio",
    )

    assert first != second


def test_trusted_context_changes_key():
    anonymous = _key(
        trusted=False,
    )

    trusted = _key(
        trusted=True,
    )

    assert anonymous != trusted


def test_query_is_not_exposed_in_redis_key():
    question = (
        "Minha pergunta financeira privada."
    )

    key = _key(
        question=question,
    )

    assert question not in key
    assert "minha pergunta" not in key.lower()


def test_planner_version_changes_key(
    monkeypatch,
):
    monkeypatch.setattr(
        planner_cache,
        "PLANNER_CACHE_PLANNER_VERSION",
        "planner_v1",
    )

    first = _key()

    monkeypatch.setattr(
        planner_cache,
        "PLANNER_CACHE_PLANNER_VERSION",
        "planner_v2",
    )

    second = _key()

    assert first != second


def test_tools_mapping_changes_key(
    monkeypatch,
):
    original = dict(
        planner_cache.ALLOWED_TOOL_BY_SOURCE
    )

    first = _key()

    changed = dict(original)

    source = next(
        iter(changed)
    )

    changed[source] = (
        changed[source]
        + "_vnext"
    )

    monkeypatch.setattr(
        planner_cache,
        "ALLOWED_TOOL_BY_SOURCE",
        changed,
    )

    second = _key()

    assert first != second
