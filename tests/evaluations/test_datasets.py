from __future__ import annotations

import json
from dataclasses import fields
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from src.evaluation.contracts import (
    ConversationTurn,
    ExpectedToolCall,
    InnaEvaluationCase,
    PrivacyLevel,
)
from src.evaluation.datasets import (
    DATASET_SCHEMA_VERSION,
    DEFAULT_DATASET_NAME,
    DEFAULT_DATASET_VERSION,
    DatasetRegistry,
    EvaluationDataset,
    _canonicalize_fingerprint_value,
    _deserialize_conversation_turn,
    _deserialize_expected_tool,
    _semantic_version_key,
    _serialize_conversation_turn,
    _serialize_expected_tool,
    build_dataset,
    evaluation_case_from_dict,
    evaluation_case_to_dict,
    utc_now,
)

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def expected_tool() -> ExpectedToolCall:
    return ExpectedToolCall(
        name="financial_calculator",
        arguments={
            "income": 3000,
            "fixed_expenses": 1400,
            "variable_expenses": 700,
            "debts": 300,
        },
        required=True,
        allow_additional_arguments=False,
        call_order=0,
        minimum_calls=1,
        maximum_calls=1,
        metadata={
            "domain": "financial",
            "critical": True,
        },
    )


@pytest.fixture
def conversation_tool() -> ExpectedToolCall:
    return ExpectedToolCall(
        name="rag_search",
        arguments={
            "query": "reserva de emergência",
        },
        required=True,
        allow_additional_arguments=True,
        call_order=1,
        minimum_calls=1,
        maximum_calls=2,
        metadata={
            "domain": "rag",
            "critical": False,
        },
    )


@pytest.fixture
def conversation(
    conversation_tool: ExpectedToolCall,
) -> tuple[ConversationTurn, ...]:
    return (
        ConversationTurn(
            role="user",
            content=(
                "Como posso organizar uma reserva "
                "de emergência?"
            ),
            turn_index=0,
            expected_agent="financial_agent",
            expected_team="financial_team",
            expected_intent="reserva_financeira",
            expected_tools=(
                conversation_tool,
            ),
            metadata={
                "channel": "web",
                "synthetic": True,
            },
        ),
        ConversationTurn(
            role="assistant",
            content=(
                "Vamos analisar seu orçamento "
                "de forma educativa."
            ),
            turn_index=1,
            expected_output=(
                "Orientação financeira educativa."
            ),
            metadata={
                "final": True,
            },
        ),
    )


@pytest.fixture
def complete_case(
    expected_tool: ExpectedToolCall,
    conversation: tuple[ConversationTurn, ...],
) -> InnaEvaluationCase:
    return InnaEvaluationCase(
        case_id="financial-diagnosis-001",
        input_text=(
            "Cenário financeiro sintético para "
            "avaliação automatizada."
        ),
        case_version="2.1.0",
        dataset_name="inna-core",
        dataset_version="1.0.0",
        description=(
            "Caso completo para testar o catálogo "
            "de avaliações da INNA."
        ),
        category="financial-diagnosis",
        tags=(
            "financial",
            "routing",
            "tool-calling",
        ),
        conversation=conversation,
        expected_output=(
            "Diagnóstico financeiro educativo."
        ),
        expected_agent="financial_agent",
        expected_team="financial_team",
        expected_intent="diagnostico_financeiro",
        expected_task_status="completed",
        expected_tools=(
            expected_tool,
        ),
        forbidden_tools=(
            "unsafe_investment_tool",
        ),
        expected_terms=(
            "saldo",
            "reserva",
        ),
        forbidden_terms=(
            "lucro garantido",
            "sem risco",
        ),
        expected_structured_keys=(
            "summary",
            "financial.balance",
        ),
        forbidden_structured_keys=(
            "password",
            "api_key",
        ),
        expected_trace_terms=(
            "financial_agent",
            "financial_calculator",
        ),
        forbidden_trace_terms=(
            "unsafe_agent",
        ),
        expected_retrieval_terms=(
            "reserva de emergência",
        ),
        minimum_retrieved_documents=1,
        minimum_completion_score=0.90,
        minimum_answer_score=0.85,
        maximum_latency_ms=5000,
        maximum_estimated_cost=0.01,
        language="pt-BR",
        currency="BRL",
        privacy_level=PrivacyLevel.INTERNAL,
        external_evaluation_allowed=False,
        human_review_expected=False,
        metadata={
            "source": "test-suite",
            "synthetic": True,
        },
    )


@pytest.fixture
def complete_dataset(
    complete_case: InnaEvaluationCase,
) -> EvaluationDataset:
    return EvaluationDataset(
        name="inna-core",
        version="1.0.0",
        cases=(
            complete_case,
        ),
        description=(
            "Dataset principal de avaliações "
            "automatizadas da INNA."
        ),
        owner="INNA LLMOps",
        tags=(
            "financial",
            "production-quality",
        ),
        created_at=datetime(
            2026,
            7,
            25,
            12,
            0,
            tzinfo=UTC,
        ),
        metadata={
            "environment": "test",
        },
    )


def build_case(
    *,
    case_id: str,
    dataset_name: str = "inna-core",
    dataset_version: str = "1.0.0",
    category: str = "general",
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
    external_evaluation_allowed: bool = False,
    human_review_expected: bool | None = None,
) -> InnaEvaluationCase:
    return InnaEvaluationCase(
        case_id=case_id,
        input_text="Conteúdo sintético de avaliação.",
        dataset_name=dataset_name,
        dataset_version=dataset_version,
        category=category,
        privacy_level=privacy_level,
        external_evaluation_allowed=(
            external_evaluation_allowed
        ),
        human_review_expected=(
            human_review_expected
        ),
    )


# ============================================================
# CONSTANTES E HORÁRIO
# ============================================================


def test_dataset_constants() -> None:
    assert DATASET_SCHEMA_VERSION == "1.0.0"
    assert DEFAULT_DATASET_NAME
    assert DEFAULT_DATASET_VERSION == "1.0.0"


def test_utc_now_returns_aware_datetime() -> None:
    current = utc_now()

    assert isinstance(current, datetime)
    assert current.tzinfo is not None
    assert current.utcoffset() is not None


# ============================================================
# SERIALIZAÇÃO DE FERRAMENTAS
# ============================================================


def test_expected_tool_serializes_all_fields(
    expected_tool: ExpectedToolCall,
) -> None:
    payload = _serialize_expected_tool(
        expected_tool
    )

    contract_fields = {
        item.name
        for item in fields(
            ExpectedToolCall
        )
    }

    assert set(payload) == contract_fields
    assert payload["name"] == (
        "financial_calculator"
    )
    assert payload["arguments"]["income"] == 3000
    assert payload["required"] is True
    assert (
        payload["allow_additional_arguments"]
        is False
    )
    assert payload["call_order"] == 0
    assert payload["minimum_calls"] == 1
    assert payload["maximum_calls"] == 1
    assert payload["metadata"] == {
        "domain": "financial",
        "critical": True,
    }


def test_expected_tool_roundtrip(
    expected_tool: ExpectedToolCall,
) -> None:
    restored = _deserialize_expected_tool(
        _serialize_expected_tool(
            expected_tool
        )
    )

    assert restored == expected_tool
    assert dict(restored.metadata) == {
        "domain": "financial",
        "critical": True,
    }


def test_expected_tool_legacy_payload() -> None:
    restored = _deserialize_expected_tool(
        {
            "name": "financial_calculator",
            "arguments": {
                "income": 3000,
            },
        }
    )

    assert restored.name == (
        "financial_calculator"
    )
    assert restored.required is True
    assert (
        restored.allow_additional_arguments
        is True
    )
    assert restored.minimum_calls == 1
    assert restored.maximum_calls is None
    assert restored.call_order is None
    assert dict(restored.metadata) == {}


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    (
        (
            "arguments",
            "invalid",
        ),
        (
            "metadata",
            "invalid",
        ),
    ),
)
def test_expected_tool_rejects_invalid_mappings(
    field_name: str,
    field_value: Any,
) -> None:
    payload = {
        "name": "calculator",
        field_name: field_value,
    }

    with pytest.raises(ValueError):
        _deserialize_expected_tool(payload)


@pytest.mark.parametrize(
    "invalid_value",
    (
        "talvez",
        [],
        {},
    ),
)
def test_expected_tool_rejects_invalid_boolean(
    invalid_value: Any,
) -> None:
    with pytest.raises(
        ValueError,
        match="required",
    ):
        _deserialize_expected_tool(
            {
                "name": "calculator",
                "required": invalid_value,
            }
        )


def test_expected_tool_accepts_legacy_boolean_strings() -> None:
    restored = _deserialize_expected_tool(
        {
            "name": "calculator",
            "required": "true",
            "allow_additional_arguments": "false",
        }
    )

    assert restored.required is True
    assert (
        restored.allow_additional_arguments
        is False
    )


# ============================================================
# SERIALIZAÇÃO DE CONVERSATION TURN
# ============================================================


def test_conversation_turn_serializes_all_fields(
    conversation: tuple[ConversationTurn, ...],
) -> None:
    payload = _serialize_conversation_turn(
        conversation[0]
    )

    contract_fields = {
        item.name
        for item in fields(
            ConversationTurn
        )
    }

    assert set(payload) == contract_fields
    assert payload["role"] == "user"
    assert payload["turn_index"] == 0
    assert len(payload["expected_tools"]) == 1
    assert payload["metadata"]["channel"] == (
        "web"
    )


def test_conversation_turn_roundtrip(
    conversation: tuple[ConversationTurn, ...],
) -> None:
    original = conversation[0]

    restored = _deserialize_conversation_turn(
        _serialize_conversation_turn(
            original
        )
    )

    assert restored == original
    assert restored.expected_tools
    assert dict(
        restored.expected_tools[0].metadata
    ) == {
        "domain": "rag",
        "critical": False,
    }


def test_conversation_turn_legacy_defaults() -> None:
    restored = _deserialize_conversation_turn(
        {
            "role": "user",
            "content": "Mensagem antiga.",
        }
    )

    assert restored.role == "user"
    assert restored.content == "Mensagem antiga."
    assert restored.turn_index == 0
    assert restored.expected_output is None
    assert restored.expected_tools == ()
    assert dict(restored.metadata) == {}


def test_conversation_turn_rejects_invalid_tools() -> None:
    with pytest.raises(
        ValueError,
        match="expected_tools",
    ):
        _deserialize_conversation_turn(
            {
                "role": "user",
                "content": "Teste",
                "expected_tools": "invalid",
            }
        )


def test_conversation_turn_rejects_invalid_tool_entry() -> None:
    with pytest.raises(
        ValueError,
        match=r"expected_tools\[0\]",
    ):
        _deserialize_conversation_turn(
            {
                "role": "user",
                "content": "Teste",
                "expected_tools": [
                    "invalid",
                ],
            }
        )


# ============================================================
# SERIALIZAÇÃO COMPLETA DO CASO
# ============================================================


def test_case_serializes_all_contract_fields(
    complete_case: InnaEvaluationCase,
) -> None:
    payload = evaluation_case_to_dict(
        complete_case
    )

    contract_fields = {
        item.name
        for item in fields(
            InnaEvaluationCase
        )
    }

    assert len(contract_fields) == 34
    assert set(payload) == contract_fields


def test_case_roundtrip_preserves_all_fields(
    complete_case: InnaEvaluationCase,
) -> None:
    payload = evaluation_case_to_dict(
        complete_case
    )

    restored = evaluation_case_from_dict(
        payload
    )

    assert restored == complete_case
    assert restored.description == (
        complete_case.description
    )
    assert restored.tags == complete_case.tags
    assert restored.conversation == (
        complete_case.conversation
    )
    assert restored.expected_output == (
        complete_case.expected_output
    )
    assert restored.minimum_answer_score == (
        0.85
    )
    assert restored.language == "pt-br"
    assert restored.currency == "BRL"
    assert dict(restored.metadata) == {
        "source": "test-suite",
        "synthetic": True,
    }


def test_case_roundtrip_preserves_tool_metadata(
    complete_case: InnaEvaluationCase,
) -> None:
    restored = evaluation_case_from_dict(
        evaluation_case_to_dict(
            complete_case
        )
    )

    assert dict(
        restored.expected_tools[0].metadata
    ) == {
        "domain": "financial",
        "critical": True,
    }

    assert dict(
        restored
        .conversation[0]
        .expected_tools[0]
        .metadata
    ) == {
        "domain": "rag",
        "critical": False,
    }


def test_case_legacy_payload_uses_defaults() -> None:
    restored = evaluation_case_from_dict(
        {
            "case_id": "legacy-case",
            "input_text": "Caso antigo.",
            "dataset_name": "inna-legacy",
            "dataset_version": "1.0.0",
        }
    )

    assert restored.description is None
    assert restored.tags == ()
    assert restored.conversation == ()
    assert restored.expected_output is None
    assert restored.minimum_answer_score == 0.0
    assert restored.language == "pt"
    assert restored.currency == "BRL"
    assert (
        restored.privacy_level
        == PrivacyLevel.CONFIDENTIAL
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    (
        (
            "conversation",
            "invalid",
            "conversation",
        ),
        (
            "expected_tools",
            "invalid",
            "expected_tools",
        ),
        (
            "metadata",
            "invalid",
            "metadata",
        ),
        (
            "external_evaluation_allowed",
            "talvez",
            "external_evaluation_allowed",
        ),
        (
            "minimum_answer_score",
            "invalid",
            "minimum_answer_score",
        ),
        (
            "maximum_latency_ms",
            float("inf"),
            "maximum_latency_ms",
        ),
    ),
)
def test_case_rejects_invalid_fields(
    field_name: str,
    invalid_value: Any,
    message: str,
) -> None:
    payload = {
        "case_id": "invalid-case",
        field_name: invalid_value,
    }

    with pytest.raises(
        ValueError,
        match=message,
    ):
        evaluation_case_from_dict(payload)


def test_case_rejects_invalid_privacy_level() -> None:
    with pytest.raises(
        ValueError,
        match="privacy_level",
    ):
        evaluation_case_from_dict(
            {
                "case_id": "invalid-privacy",
                "privacy_level": "unknown",
            }
        )


def test_case_rejects_invalid_conversation_entry() -> None:
    with pytest.raises(
        ValueError,
        match=r"conversation\[0\]",
    ):
        evaluation_case_from_dict(
            {
                "case_id": "invalid-turn",
                "conversation": [
                    "invalid",
                ],
            }
        )


def test_case_rejects_invalid_tool_entry() -> None:
    with pytest.raises(
        ValueError,
        match=r"expected_tools\[0\]",
    ):
        evaluation_case_from_dict(
            {
                "case_id": "invalid-tool",
                "expected_tools": [
                    "invalid",
                ],
            }
        )


def test_case_rejects_missing_input_and_conversation() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "input_text ou conversation"
        ),
    ):
        evaluation_case_from_dict(
            {
                "case_id": "empty-evaluation-case",
            }
        )



def test_case_boolean_compatibility() -> None:
    restored = evaluation_case_from_dict(
        {
            "case_id": "legacy-bools",
            "input_text": (
                "Caso legado para validar "
                "compatibilidade booleana."
            ),
            "external_evaluation_allowed": "false",
            "human_review_expected": "true",
        }
    )

    assert (
        restored.external_evaluation_allowed
        is False
    )
    assert restored.human_review_expected is True


# ============================================================
# CONSTRUÇÃO E VALIDAÇÃO DO DATASET
# ============================================================


def test_dataset_properties(
    complete_dataset: EvaluationDataset,
) -> None:
    assert len(complete_dataset) == 1
    assert complete_dataset.dataset_id == (
        "inna-core@1.0.0"
    )
    assert complete_dataset.case_ids == (
        "financial-diagnosis-001",
    )
    assert complete_dataset.categories == (
        "financial-diagnosis",
    )
    assert complete_dataset.privacy_levels == (
        PrivacyLevel.INTERNAL,
    )
    assert complete_dataset.owner == (
        "INNA LLMOps"
    )


def test_dataset_iteration(
    complete_dataset: EvaluationDataset,
    complete_case: InnaEvaluationCase,
) -> None:
    assert tuple(complete_dataset) == (
        complete_case,
    )


def test_dataset_contains_case_id(
    complete_dataset: EvaluationDataset,
) -> None:
    assert (
        "financial-diagnosis-001"
        in complete_dataset
    )
    assert "missing-case" not in complete_dataset
    assert 123 not in complete_dataset


def test_dataset_get_case(
    complete_dataset: EvaluationDataset,
    complete_case: InnaEvaluationCase,
) -> None:
    assert complete_dataset.get_case(
        complete_case.case_id
    ) == complete_case


def test_dataset_get_case_raises_key_error(
    complete_dataset: EvaluationDataset,
) -> None:
    with pytest.raises(
        KeyError,
        match="Caso não encontrado",
    ):
        complete_dataset.get_case(
            "missing-case"
        )


def test_dataset_rejects_duplicate_case_ids() -> None:
    case = build_case(
        case_id="duplicate-case",
    )

    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        EvaluationDataset(
            name="inna-core",
            version="1.0.0",
            cases=(
                case,
                case,
            ),
        )


def test_dataset_rejects_case_from_another_dataset() -> None:
    case = build_case(
        case_id="wrong-dataset",
        dataset_name="other-dataset",
    )

    with pytest.raises(
        ValueError,
        match="pertence ao dataset",
    ):
        EvaluationDataset(
            name="inna-core",
            version="1.0.0",
            cases=(
                case,
            ),
        )


def test_dataset_rejects_case_from_another_version() -> None:
    case = build_case(
        case_id="wrong-version",
        dataset_version="2.0.0",
    )

    with pytest.raises(
        ValueError,
        match="usa a versão",
    ):
        EvaluationDataset(
            name="inna-core",
            version="1.0.0",
            cases=(
                case,
            ),
        )


@pytest.mark.parametrize(
    "invalid_name",
    (
        "",
        "INNA CORE",
        "inna/core",
        "@inna",
    ),
)
def test_dataset_rejects_invalid_name(
    invalid_name: str,
) -> None:
    with pytest.raises(ValueError):
        EvaluationDataset(
            name=invalid_name,
            version="1.0.0",
            cases=(),
        )


@pytest.mark.parametrize(
    "invalid_version",
    (
        "",
        "1",
        "1.0",
        "v1.0.0",
        "1.0.x",
    ),
)
def test_dataset_rejects_invalid_version(
    invalid_version: str,
) -> None:
    with pytest.raises(ValueError):
        EvaluationDataset(
            name="inna-core",
            version=invalid_version,
            cases=(),
        )


def test_dataset_rejects_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="timezone",
    ):
        EvaluationDataset(
            name="inna-core",
            version="1.0.0",
            cases=(),
            created_at=datetime(
                2026,
                7,
                25,
            ),
        )


def test_build_dataset_helper(
    complete_case: InnaEvaluationCase,
) -> None:
    dataset = build_dataset(
        name="inna-core",
        version="1.0.0",
        cases=(
            complete_case,
        ),
        tags=(
            "financial",
            "financial",
            "routing",
        ),
        metadata={
            "source": "helper",
        },
    )

    assert isinstance(
        dataset,
        EvaluationDataset,
    )
    assert dataset.tags == (
        "financial",
        "routing",
    )
    assert dict(dataset.metadata) == {
        "source": "helper",
    }


# ============================================================
# FILTROS
# ============================================================


@pytest.fixture
def filter_dataset() -> EvaluationDataset:
    return EvaluationDataset(
        name="inna-core",
        version="1.0.0",
        cases=(
            build_case(
                case_id="financial-public",
                category="financial",
                privacy_level=PrivacyLevel.PUBLIC,
                external_evaluation_allowed=True,
            ),
            build_case(
                case_id="financial-internal",
                category="financial",
                privacy_level=PrivacyLevel.INTERNAL,
            ),
            build_case(
                case_id="rag-review",
                category="rag",
                privacy_level=PrivacyLevel.CONFIDENTIAL,
                human_review_expected=True,
            ),
        ),
    )


def test_select_by_case_id(
    filter_dataset: EvaluationDataset,
) -> None:
    selected = filter_dataset.select(
        case_ids=(
            "financial-public",
        )
    )

    assert tuple(
        case.case_id
        for case in selected
    ) == (
        "financial-public",
    )


def test_select_by_category_case_insensitive(
    filter_dataset: EvaluationDataset,
) -> None:
    selected = filter_dataset.select(
        categories=(
            "FINANCIAL",
        )
    )

    assert len(selected) == 2


def test_select_by_privacy(
    filter_dataset: EvaluationDataset,
) -> None:
    selected = filter_dataset.select(
        privacy_levels=(
            PrivacyLevel.INTERNAL,
        )
    )

    assert len(selected) == 1
    assert selected[0].case_id == (
        "financial-internal"
    )


def test_select_external_only(
    filter_dataset: EvaluationDataset,
) -> None:
    selected = filter_dataset.select(
        external_only=True
    )

    assert len(selected) == 1
    assert selected[0].case_id == (
        "financial-public"
    )


def test_public_cases_alias(
    filter_dataset: EvaluationDataset,
) -> None:
    assert (
        filter_dataset.public_cases()
        == filter_dataset.select(
            external_only=True
        )
    )


def test_select_human_review_only(
    filter_dataset: EvaluationDataset,
) -> None:
    selected = filter_dataset.select(
        human_review_only=True
    )

    assert len(selected) == 1
    assert selected[0].case_id == (
        "rag-review"
    )


def test_select_combines_filters_with_and(
    filter_dataset: EvaluationDataset,
) -> None:
    selected = filter_dataset.select(
        categories=(
            "financial",
        ),
        privacy_levels=(
            PrivacyLevel.PUBLIC,
        ),
        external_only=True,
    )

    assert len(selected) == 1
    assert selected[0].case_id == (
        "financial-public"
    )


# ============================================================
# MANIFESTO E FINGERPRINT
# ============================================================


def test_dataset_manifest(
    filter_dataset: EvaluationDataset,
) -> None:
    manifest = filter_dataset.manifest()

    assert manifest["dataset_id"] == (
        "inna-core@1.0.0"
    )
    assert manifest["case_count"] == 3
    assert manifest["external_case_count"] == 1
    assert (
        manifest["human_review_case_count"]
        == 1
    )
    assert manifest["categories"] == {
        "financial": 2,
        "rag": 1,
    }
    assert manifest["fingerprint"] == (
        filter_dataset.fingerprint
    )


def test_fingerprint_is_stable_after_roundtrip(
    complete_dataset: EvaluationDataset,
) -> None:
    restored = EvaluationDataset.from_json(
        complete_dataset.to_json()
    )

    assert restored.fingerprint == (
        complete_dataset.fingerprint
    )


def test_fingerprint_changes_with_functional_content(
    complete_dataset: EvaluationDataset,
    complete_case: InnaEvaluationCase,
) -> None:
    changed_case = InnaEvaluationCase(
        **{
            **evaluation_case_to_dict(
                complete_case
            ),
            "description": (
                "Descrição funcional alterada."
            ),
            "conversation": (
                complete_case.conversation
            ),
            "expected_tools": (
                complete_case.expected_tools
            ),
            "privacy_level": (
                complete_case.privacy_level
            ),
        }
    )

    changed_dataset = EvaluationDataset(
        name="inna-core",
        version="1.0.0",
        cases=(
            changed_case,
        ),
        created_at=(
            complete_dataset.created_at
        ),
    )

    assert changed_dataset.fingerprint != (
        complete_dataset.fingerprint
    )


def test_fingerprint_treats_integer_and_float_equally() -> None:
    integer_value = (
        _canonicalize_fingerprint_value(
            {
                "maximum_latency_ms": 5000,
            }
        )
    )

    float_value = (
        _canonicalize_fingerprint_value(
            {
                "maximum_latency_ms": 5000.0,
            }
        )
    )

    assert integer_value == float_value


@pytest.mark.parametrize(
    "invalid_number",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_fingerprint_rejects_non_finite_numbers(
    invalid_number: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="NaN ou infinitos",
    ):
        _canonicalize_fingerprint_value(
            {
                "value": invalid_number,
            }
        )


# ============================================================
# JSON E ARQUIVOS
# ============================================================


def test_dataset_to_dict_with_cases(
    complete_dataset: EvaluationDataset,
) -> None:
    payload = complete_dataset.to_dict()

    assert payload["dataset_id"] == (
        "inna-core@1.0.0"
    )
    assert len(payload["cases"]) == 1


def test_dataset_to_dict_without_cases(
    complete_dataset: EvaluationDataset,
) -> None:
    payload = complete_dataset.to_dict(
        include_cases=False
    )

    assert "cases" not in payload


def test_dataset_json_roundtrip(
    complete_dataset: EvaluationDataset,
) -> None:
    serialized = complete_dataset.to_json()

    restored = EvaluationDataset.from_json(
        serialized
    )

    assert restored.dataset_id == (
        complete_dataset.dataset_id
    )
    assert restored.cases == (
        complete_dataset.cases
    )
    assert restored.fingerprint == (
        complete_dataset.fingerprint
    )


def test_dataset_from_json_accepts_bytes(
    complete_dataset: EvaluationDataset,
) -> None:
    serialized = complete_dataset.to_json().encode(
        "utf-8"
    )

    restored = EvaluationDataset.from_json(
        serialized
    )

    assert restored.dataset_id == (
        complete_dataset.dataset_id
    )


def test_dataset_from_json_rejects_non_object_root() -> None:
    with pytest.raises(
        ValueError,
        match="objeto na raiz",
    ):
        EvaluationDataset.from_json(
            '["invalid"]'
        )


def test_dataset_export_and_load(
    complete_dataset: EvaluationDataset,
    tmp_path: Path,
) -> None:
    destination = (
        tmp_path
        / "inna-core-export"
    )

    exported = complete_dataset.export_json(
        destination
    )

    assert exported.is_file()
    assert exported.suffix == ".json"

    loaded = EvaluationDataset.load_json(
        exported
    )

    assert loaded.dataset_id == (
        complete_dataset.dataset_id
    )
    assert loaded.cases == (
        complete_dataset.cases
    )
    assert loaded.fingerprint == (
        complete_dataset.fingerprint
    )


def test_dataset_load_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Dataset não encontrado",
    ):
        EvaluationDataset.load_json(
            tmp_path
            / "missing.json"
        )


def test_external_export_contains_only_allowed_cases(
    filter_dataset: EvaluationDataset,
    tmp_path: Path,
) -> None:
    exported = filter_dataset.export_json(
        tmp_path / "external-dataset.json",
        external_only=True,
    )

    payload = json.loads(
        exported.read_text(
            encoding="utf-8"
        )
    )

    assert payload["external_export"] is True
    assert payload["case_count"] == 1
    assert payload["case_ids"] == [
        "financial-public",
    ]
    assert len(payload["cases"]) == 1
    assert (
        payload["cases"][0]["case_id"]
        == "financial-public"
    )


def test_external_export_excludes_internal_cases(
    filter_dataset: EvaluationDataset,
    tmp_path: Path,
) -> None:
    exported = filter_dataset.export_json(
        tmp_path / "public.json",
        external_only=True,
    )

    rendered = exported.read_text(
        encoding="utf-8"
    )

    assert "financial-internal" not in rendered
    assert "rag-review" not in rendered


# ============================================================
# DATASET REGISTRY
# ============================================================


def test_registry_register_and_get(
    complete_dataset: EvaluationDataset,
) -> None:
    registry = DatasetRegistry()

    registry.register(
        complete_dataset
    )

    assert len(registry) == 1
    assert registry.get(
        "inna-core",
        "1.0.0",
    ) == complete_dataset


def test_registry_rejects_duplicate_registration(
    complete_dataset: EvaluationDataset,
) -> None:
    registry = DatasetRegistry(
        (
            complete_dataset,
        )
    )

    with pytest.raises(
        ValueError,
        match="já registrado",
    ):
        registry.register(
            complete_dataset
        )


def test_registry_can_replace_existing(
    complete_dataset: EvaluationDataset,
) -> None:
    replacement = EvaluationDataset(
        name="inna-core",
        version="1.0.0",
        cases=(
            complete_dataset.cases
        ),
        description="Replacement",
    )

    registry = DatasetRegistry(
        (
            complete_dataset,
        )
    )

    registry.register(
        replacement,
        replace_existing=True,
    )

    assert registry.get(
        "inna-core",
        "1.0.0",
    ) == replacement


def test_registry_unregister(
    complete_dataset: EvaluationDataset,
) -> None:
    registry = DatasetRegistry(
        (
            complete_dataset,
        )
    )

    removed = registry.unregister(
        "inna-core",
        "1.0.0",
    )

    assert removed == complete_dataset
    assert len(registry) == 0


def test_registry_unregister_missing() -> None:
    registry = DatasetRegistry()

    with pytest.raises(
        KeyError,
        match="não registrado",
    ):
        registry.unregister(
            "inna-core",
            "1.0.0",
        )


def test_registry_get_missing() -> None:
    registry = DatasetRegistry()

    with pytest.raises(
        KeyError,
        match="não registrado",
    ):
        registry.get(
            "inna-core",
            "1.0.0",
        )


def test_registry_versions_are_semantically_sorted() -> None:
    datasets = tuple(
        EvaluationDataset(
            name="inna-core",
            version=version,
            cases=(),
        )
        for version in (
            "2.0.0",
            "1.10.0",
            "1.2.0",
            "1.0.0-alpha",
            "1.0.0",
        )
    )

    registry = DatasetRegistry(
        datasets
    )

    assert registry.versions(
        "inna-core"
    ) == (
        "1.0.0-alpha",
        "1.0.0",
        "1.2.0",
        "1.10.0",
        "2.0.0",
    )


def test_registry_latest() -> None:
    registry = DatasetRegistry(
        (
            EvaluationDataset(
                name="inna-core",
                version="1.0.0",
                cases=(),
            ),
            EvaluationDataset(
                name="inna-core",
                version="2.0.0",
                cases=(),
            ),
        )
    )

    assert registry.latest(
        "inna-core"
    ).version == "2.0.0"


def test_registry_latest_missing() -> None:
    registry = DatasetRegistry()

    with pytest.raises(
        KeyError,
        match="Nenhuma versão",
    ):
        registry.latest(
            "inna-core"
        )


def test_registry_all_is_sorted() -> None:
    registry = DatasetRegistry(
        (
            EvaluationDataset(
                name="zeta",
                version="1.0.0",
                cases=(),
            ),
            EvaluationDataset(
                name="alpha",
                version="2.0.0",
                cases=(),
            ),
            EvaluationDataset(
                name="alpha",
                version="1.0.0",
                cases=(),
            ),
        )
    )

    assert tuple(
        dataset.dataset_id
        for dataset in registry.all()
    ) == (
        "alpha@1.0.0",
        "alpha@2.0.0",
        "zeta@1.0.0",
    )


@pytest.mark.parametrize(
    ("left", "right"),
    (
        (
            "1.0.0-alpha",
            "1.0.0",
        ),
        (
            "1.0.0",
            "1.1.0",
        ),
        (
            "1.9.0",
            "1.10.0",
        ),
        (
            "1.10.0",
            "2.0.0",
        ),
    ),
)
def test_semantic_version_key_order(
    left: str,
    right: str,
) -> None:
    assert (
        _semantic_version_key(left)
        < _semantic_version_key(right)
    )