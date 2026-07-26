from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from src.evaluation.case_catalog import (
    CONVERSATION_DATASET_NAME,
    CONVERSATION_DATASET_VERSION,
    CORE_DATASET_NAME,
    CORE_DATASET_VERSION,
    SAFETY_DATASET_NAME,
    SAFETY_DATASET_VERSION,
    build_conversation_cases,
    build_conversation_dataset,
    build_core_cases,
    build_core_dataset,
    build_official_registry,
    build_safety_cases,
    build_safety_dataset,
    official_case_count,
    official_datasets,
)
from src.evaluation.contracts import (
    ExpectedToolCall,
    InnaEvaluationCase,
    PrivacyLevel,
)
from src.evaluation.datasets import (
    DatasetRegistry,
    EvaluationDataset,
)

# ============================================================
# CONSTANTES
# ============================================================


def test_catalog_constants() -> None:
    assert CORE_DATASET_NAME == "inna-core"
    assert CORE_DATASET_VERSION == "1.0.0"

    assert SAFETY_DATASET_NAME == "inna-safety"
    assert SAFETY_DATASET_VERSION == "1.0.0"

    assert (
        CONVERSATION_DATASET_NAME
        == "inna-conversation"
    )
    assert (
        CONVERSATION_DATASET_VERSION
        == "1.0.0"
    )


# ============================================================
# CONSTRUÇÃO DOS CASOS
# ============================================================


def test_core_cases_count() -> None:
    cases = build_core_cases()

    assert isinstance(cases, tuple)
    assert len(cases) == 6


def test_safety_cases_count() -> None:
    cases = build_safety_cases()

    assert isinstance(cases, tuple)
    assert len(cases) == 3


def test_conversation_cases_count() -> None:
    cases = build_conversation_cases()

    assert isinstance(cases, tuple)
    assert len(cases) == 2


def test_all_catalog_cases_are_evaluation_cases() -> None:
    all_cases = (
        *build_core_cases(),
        *build_safety_cases(),
        *build_conversation_cases(),
    )

    assert all(
        isinstance(case, InnaEvaluationCase)
        for case in all_cases
    )


def test_official_case_count() -> None:
    assert official_case_count() == 11


def test_all_case_ids_are_unique() -> None:
    all_case_ids = tuple(
        case.case_id
        for dataset in official_datasets()
        for case in dataset
    )

    duplicates = tuple(
        case_id
        for case_id, count in Counter(
            all_case_ids
        ).items()
        if count > 1
    )

    assert len(all_case_ids) == 11
    assert duplicates == ()


def test_case_ids_follow_technical_pattern() -> None:
    all_case_ids = tuple(
        case.case_id
        for dataset in official_datasets()
        for case in dataset
    )

    assert all(
        case_id
        and case_id == case_id.lower()
        and " " not in case_id
        and "/" not in case_id
        for case_id in all_case_ids
    )


# ============================================================
# DATASETS
# ============================================================


def test_build_core_dataset() -> None:
    dataset = build_core_dataset()

    assert isinstance(
        dataset,
        EvaluationDataset,
    )
    assert dataset.dataset_id == (
        "inna-core@1.0.0"
    )
    assert len(dataset) == 6
    assert dataset.metadata[
        "synthetic_only"
    ] is True
    assert dataset.metadata[
        "production_data"
    ] is False


def test_build_safety_dataset() -> None:
    dataset = build_safety_dataset()

    assert isinstance(
        dataset,
        EvaluationDataset,
    )
    assert dataset.dataset_id == (
        "inna-safety@1.0.0"
    )
    assert len(dataset) == 3
    assert dataset.categories == (
        "financial-safety",
    )


def test_build_conversation_dataset() -> None:
    dataset = build_conversation_dataset()

    assert isinstance(
        dataset,
        EvaluationDataset,
    )
    assert dataset.dataset_id == (
        "inna-conversation@1.0.0"
    )
    assert len(dataset) == 2
    assert dataset.categories == (
        "conversation",
        "human-review",
    )


def test_official_datasets_count_and_order() -> None:
    datasets = official_datasets()

    assert isinstance(datasets, tuple)
    assert len(datasets) == 3

    assert tuple(
        dataset.dataset_id
        for dataset in datasets
    ) == (
        "inna-conversation@1.0.0",
        "inna-core@1.0.0",
        "inna-safety@1.0.0",
    )


def test_official_registry() -> None:
    registry = build_official_registry()

    assert isinstance(
        registry,
        DatasetRegistry,
    )
    assert len(registry) == 3

    assert registry.get(
        "inna-core",
        "1.0.0",
    ).dataset_id == "inna-core@1.0.0"

    assert registry.get(
        "inna-safety",
        "1.0.0",
    ).dataset_id == "inna-safety@1.0.0"

    assert registry.get(
        "inna-conversation",
        "1.0.0",
    ).dataset_id == (
        "inna-conversation@1.0.0"
    )


def test_dataset_case_relationships() -> None:
    for dataset in official_datasets():
        for case in dataset:
            assert case.dataset_name == (
                dataset.name
            )
            assert case.dataset_version == (
                dataset.version
            )


def test_all_datasets_have_fingerprints() -> None:
    fingerprints = tuple(
        dataset.fingerprint
        for dataset in official_datasets()
    )

    assert all(
        isinstance(fingerprint, str)
        and len(fingerprint) >= 32
        for fingerprint in fingerprints
    )

    assert len(set(fingerprints)) == 3


def test_catalog_fingerprints_are_stable() -> None:
    first = {
        dataset.dataset_id: dataset.fingerprint
        for dataset in official_datasets()
    }

    second = {
        dataset.dataset_id: dataset.fingerprint
        for dataset in official_datasets()
    }

    assert first == second


# ============================================================
# PRIVACIDADE E DADOS SINTÉTICOS
# ============================================================


def test_all_cases_are_synthetic() -> None:
    for dataset in official_datasets():
        for case in dataset:
            assert (
                case.metadata.get("synthetic")
                is True
            )


def test_no_case_uses_production_data() -> None:
    for dataset in official_datasets():
        assert (
            dataset.metadata[
                "production_data"
            ]
            is False
        )


def test_external_cases_are_public() -> None:
    external_cases = tuple(
        case
        for dataset in official_datasets()
        for case in dataset
        if case.external_evaluation_allowed
    )

    assert len(external_cases) == 10

    for case in external_cases:
        assert (
            case.privacy_level
            == PrivacyLevel.PUBLIC
        )
        assert (
            case.metadata.get(
                "external_safe"
            )
            is True
        )


def test_internal_cases_are_not_external() -> None:
    internal_cases = tuple(
        case
        for dataset in official_datasets()
        for case in dataset
        if not case.external_evaluation_allowed
    )

    assert len(internal_cases) == 1

    internal_case = internal_cases[0]

    assert internal_case.case_id == (
        "human-review-sensitive-guidance-001"
    )
    assert (
        internal_case.privacy_level
        == PrivacyLevel.INTERNAL
    )
    assert (
        internal_case.metadata.get(
            "external_safe"
        )
        is False
    )


def test_public_case_count_by_dataset() -> None:
    counts = {
        dataset.name: len(
            dataset.public_cases()
        )
        for dataset in official_datasets()
    }

    assert counts == {
        "inna-conversation": 1,
        "inna-core": 6,
        "inna-safety": 3,
    }


# ============================================================
# CASOS CORE
# ============================================================


def test_core_case_ids() -> None:
    dataset = build_core_dataset()

    assert dataset.case_ids == (
        "financial-diagnosis-balanced-001",
        "budget-negative-balance-001",
        "emergency-fund-guidance-001",
        "debt-prioritization-001",
        "rag-financial-education-001",
        "routing-support-001",
    )


def test_core_categories() -> None:
    dataset = build_core_dataset()

    assert dataset.categories == (
        "budget",
        "debt",
        "emergency-fund",
        "financial-diagnosis",
        "rag",
        "routing",
    )


@pytest.mark.parametrize(
    "case_id",
    (
        "financial-diagnosis-balanced-001",
        "budget-negative-balance-001",
    ),
)
def test_financial_calculator_cases(
    case_id: str,
) -> None:
    case = build_core_dataset().get_case(
        case_id
    )

    assert case.expected_tools
    assert (
        case.expected_tools[0].name
        == "financial_calculator"
    )
    assert (
        case.expected_tools[0].required
        is True
    )
    assert (
        case.expected_tools[0]
        .metadata["domain"]
        == "financial"
    )


def test_rag_case_uses_formal_rag_tool() -> None:
    case = build_core_dataset().get_case(
        "rag-financial-education-001"
    )

    assert case.expected_tools == (
        case.expected_tools[0],
    )
    assert (
        case.expected_tools[0].name
        == "buscar_conhecimento_rag"
    )
    assert (
        case.minimum_retrieved_documents
        >= 1
    )
    assert case.expected_retrieval_terms


def test_support_case_forbids_financial_tool() -> None:
    case = build_core_dataset().get_case(
        "routing-support-001"
    )

    assert case.expected_agent == (
        "support_agent"
    )
    assert case.expected_team == (
        "support_team"
    )
    assert (
        "financial_calculator"
        in case.forbidden_tools
    )


def test_core_financial_cases_have_safety_terms() -> None:
    dataset = build_core_dataset()

    relevant_cases = tuple(
        case
        for case in dataset
        if case.category
        in {
            "financial-diagnosis",
            "budget",
            "debt",
        }
    )

    assert relevant_cases

    assert all(
        case.forbidden_terms
        for case in relevant_cases
    )


# ============================================================
# CASOS DE SEGURANÇA
# ============================================================


def test_safety_case_ids() -> None:
    dataset = build_safety_dataset()

    assert dataset.case_ids == (
        "safety-guaranteed-profit-001",
        "safety-credit-limit-001",
        "safety-insufficient-data-001",
    )


def test_all_safety_cases_have_forbidden_terms() -> None:
    for case in build_safety_cases():
        assert case.forbidden_terms
        assert case.minimum_answer_score > 0


def test_guaranteed_profit_case() -> None:
    case = build_safety_dataset().get_case(
        "safety-guaranteed-profit-001"
    )

    assert "risco" in case.expected_terms
    assert "lucro garantido" in (
        case.forbidden_terms
    )
    assert "retorno garantido" in (
        case.forbidden_terms
    )
    assert "sem risco" in (
        case.forbidden_terms
    )


def test_credit_limit_safety_case() -> None:
    case = build_safety_dataset().get_case(
        "safety-credit-limit-001"
    )

    assert "risco" in case.expected_terms
    assert "juros" in case.expected_terms
    assert "use todo o limite" in (
        case.forbidden_terms
    )


def test_missing_data_safety_case() -> None:
    case = build_safety_dataset().get_case(
        "safety-insufficient-data-001"
    )

    assert "informações" in (
        case.expected_terms
    )
    assert "objetivo" in (
        case.expected_terms
    )
    assert case.minimum_answer_score == (
        pytest.approx(0.75)
    )


# ============================================================
# CONVERSA E HITL
# ============================================================


def test_conversation_case_has_multiple_turns() -> None:
    case = (
        build_conversation_dataset()
        .get_case(
            "conversation-financial-followup-001"
        )
    )

    assert len(case.conversation) == 3

    assert tuple(
        turn.turn_index
        for turn in case.conversation
    ) == (
        0,
        1,
        2,
    )

    assert tuple(
        turn.role
        for turn in case.conversation
    ) == (
        "user",
        "assistant",
        "user",
    )


def test_conversation_case_preserves_expected_tool() -> None:
    case = (
        build_conversation_dataset()
        .get_case(
            "conversation-financial-followup-001"
        )
    )

    third_turn = case.conversation[2]

    assert third_turn.expected_tools

    tool = third_turn.expected_tools[0]

    assert isinstance(
        tool,
        ExpectedToolCall,
    )
    assert tool.name == (
        "financial_calculator"
    )
    assert tool.call_order == 0


def test_human_review_case() -> None:
    case = (
        build_conversation_dataset()
        .get_case(
            "human-review-sensitive-guidance-001"
        )
    )

    assert case.human_review_expected is True
    assert case.expected_task_status == (
        "pending_review"
    )
    assert (
        case.privacy_level
        == PrivacyLevel.INTERNAL
    )
    assert (
        case.external_evaluation_allowed
        is False
    )
    assert (
        case.metadata["requires_hitl"]
        is True
    )


def test_only_one_case_requires_human_review() -> None:
    cases = tuple(
        case
        for dataset in official_datasets()
        for case in dataset
        if case.human_review_expected is True
    )

    assert len(cases) == 1
    assert cases[0].case_id == (
        "human-review-sensitive-guidance-001"
    )


# ============================================================
# QUALIDADE DOS CONTRATOS
# ============================================================


def test_public_cases_have_non_empty_inputs() -> None:
    for dataset in official_datasets():
        for case in dataset.public_cases():
            assert case.input_text.strip()


def test_cases_have_categories() -> None:
    for dataset in official_datasets():
        for case in dataset:
            assert case.category
            assert case.category != "general"


def test_cases_have_language_and_currency() -> None:
    for dataset in official_datasets():
        for case in dataset:
            assert case.language
            assert case.currency


def test_external_cases_have_expected_agents() -> None:
    for dataset in official_datasets():
        for case in dataset.public_cases():
            assert case.expected_agent
            assert case.expected_team


def test_external_cases_have_completion_threshold() -> None:
    for dataset in official_datasets():
        for case in dataset.public_cases():
            assert (
                case.minimum_completion_score
                > 0
            )


def test_tool_metadata_marks_synthetic_tools() -> None:
    tools = tuple(
        tool
        for dataset in official_datasets()
        for case in dataset
        for tool in case.expected_tools
    )

    assert tools

    for tool in tools:
        assert (
            tool.metadata.get("synthetic")
            is True
        )


# ============================================================
# SERIALIZAÇÃO E EXPORTAÇÃO
# ============================================================


@pytest.mark.parametrize(
    "builder",
    (
        build_core_dataset,
        build_safety_dataset,
        build_conversation_dataset,
    ),
)
def test_catalog_dataset_json_roundtrip(
    builder,
) -> None:
    dataset = builder()

    restored = EvaluationDataset.from_json(
        dataset.to_json()
    )

    assert restored.dataset_id == (
        dataset.dataset_id
    )
    assert restored.cases == dataset.cases
    assert restored.fingerprint == (
        dataset.fingerprint
    )


@pytest.mark.parametrize(
    "builder",
    (
        build_core_dataset,
        build_safety_dataset,
        build_conversation_dataset,
    ),
)
def test_external_export(
    builder,
    tmp_path: Path,
) -> None:
    dataset = builder()

    destination = (
        tmp_path
        / f"{dataset.name}.json"
    )

    exported = dataset.export_json(
        destination,
        external_only=True,
    )

    payload = json.loads(
        exported.read_text(
            encoding="utf-8"
        )
    )

    assert payload["external_export"] is True
    assert payload["case_count"] == len(
        dataset.public_cases()
    )

    for case_payload in payload["cases"]:
        assert (
            case_payload[
                "external_evaluation_allowed"
            ]
            is True
        )


def test_conversation_external_export_excludes_hitl(
    tmp_path: Path,
) -> None:
    dataset = build_conversation_dataset()

    exported = dataset.export_json(
        tmp_path / "conversation.json",
        external_only=True,
    )

    rendered = exported.read_text(
        encoding="utf-8"
    )

    assert (
        "conversation-financial-followup-001"
        in rendered
    )
    assert (
        "human-review-sensitive-guidance-001"
        not in rendered
    )


def test_external_exports_contain_ten_cases(
    tmp_path: Path,
) -> None:
    total_exported = 0

    for dataset in official_datasets():
        exported = dataset.export_json(
            tmp_path
            / f"{dataset.name}.json",
            external_only=True,
        )

        payload = json.loads(
            exported.read_text(
                encoding="utf-8"
            )
        )

        total_exported += int(
            payload["case_count"]
        )

    assert total_exported == 10