from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

import pytest

from src.evaluation.case_catalog import (
    build_conversation_dataset,
    build_core_dataset,
)
from src.evaluation.contracts import (
    ConversationTurn,
    InnaEvaluationCase,
    PrivacyLevel,
)
from src.evaluation.deepeval_integration import (
    DEEPEVAL_ENABLED_ENV,
    DEEPEVAL_EXTERNAL_ONLY_ENV,
    DEEPEVAL_LIVE_ENV,
    DeepEvalAvailability,
    DeepEvalCasePayload,
    DeepEvalConfigurationError,
    DeepEvalConversion,
    DeepEvalPrivacyError,
    DeepEvalSettings,
    DeepEvalUnavailableError,
    _normalize_text_sequence,
    _optional_text,
    _parse_environment_bool,
    _render_conversation_turn,
    _supported_constructor_arguments,
    build_deepeval_payload,
    convert_case_to_deepeval,
    create_llm_test_case,
    deepeval_availability,
    ensure_external_case_allowed,
    render_case_input,
    render_conversation_context,
    require_deepeval,
)

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def public_case() -> InnaEvaluationCase:
    return build_core_dataset().get_case(
        "financial-diagnosis-balanced-001"
    )


@pytest.fixture
def conversation_case() -> InnaEvaluationCase:
    return (
        build_conversation_dataset()
        .get_case(
            "conversation-financial-followup-001"
        )
    )


@pytest.fixture
def internal_case() -> InnaEvaluationCase:
    return (
        build_conversation_dataset()
        .get_case(
            "human-review-sensitive-guidance-001"
        )
    )


@pytest.fixture
def actual_output() -> str:
    return (
        "O orçamento apresenta saldo mensal positivo. "
        "Uma parte desse saldo pode ser direcionada "
        "gradualmente para a reserva de emergência."
    )


def build_external_case(
    *,
    case_id: str = "external-case",
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC,
    external_evaluation_allowed: bool = True,
    synthetic: bool = True,
    external_safe: bool = True,
) -> InnaEvaluationCase:
    return InnaEvaluationCase(
        case_id=case_id,
        input_text="Cenário sintético de avaliação.",
        dataset_name="inna-test",
        dataset_version="1.0.0",
        privacy_level=privacy_level,
        external_evaluation_allowed=(
            external_evaluation_allowed
        ),
        metadata={
            "synthetic": synthetic,
            "external_safe": external_safe,
        },
    )


# ============================================================
# CONSTANTES
# ============================================================


def test_deepeval_environment_constants() -> None:
    assert DEEPEVAL_ENABLED_ENV == (
        "INNA_DEEPEVAL_ENABLED"
    )
    assert DEEPEVAL_LIVE_ENV == (
        "INNA_DEEPEVAL_LIVE"
    )
    assert DEEPEVAL_EXTERNAL_ONLY_ENV == (
        "INNA_DEEPEVAL_EXTERNAL_ONLY"
    )


# ============================================================
# CONFIGURAÇÕES E FEATURE FLAGS
# ============================================================


def test_settings_defaults_are_secure() -> None:
    settings = DeepEvalSettings()

    assert settings.enabled is False
    assert settings.live_enabled is False
    assert settings.external_only is True


def test_settings_from_empty_environment() -> None:
    settings = (
        DeepEvalSettings.from_environment({})
    )

    assert settings == DeepEvalSettings(
        enabled=False,
        live_enabled=False,
        external_only=True,
    )


@pytest.mark.parametrize(
    "value",
    (
        "1",
        "true",
        "TRUE",
        "yes",
        "sim",
        "on",
        "enabled",
        "  true  ",
    ),
)
def test_parse_environment_bool_true_values(
    value: str,
) -> None:
    assert (
        _parse_environment_bool(
            value,
            default=False,
            variable_name="TEST_FLAG",
        )
        is True
    )


@pytest.mark.parametrize(
    "value",
    (
        "0",
        "false",
        "FALSE",
        "no",
        "nao",
        "não",
        "off",
        "disabled",
        "",
        "  false  ",
    ),
)
def test_parse_environment_bool_false_values(
    value: str,
) -> None:
    assert (
        _parse_environment_bool(
            value,
            default=True,
            variable_name="TEST_FLAG",
        )
        is False
    )


@pytest.mark.parametrize(
    ("default", "expected"),
    (
        (
            False,
            False,
        ),
        (
            True,
            True,
        ),
    ),
)
def test_parse_environment_bool_none_uses_default(
    default: bool,
    expected: bool,
) -> None:
    assert (
        _parse_environment_bool(
            None,
            default=default,
            variable_name="TEST_FLAG",
        )
        is expected
    )


@pytest.mark.parametrize(
    "invalid_value",
    (
        "talvez",
        "2",
        "live",
        "verdadeiro",
        "null",
    ),
)
def test_parse_environment_bool_rejects_invalid_values(
    invalid_value: str,
) -> None:
    with pytest.raises(
        DeepEvalConfigurationError,
        match="TEST_FLAG",
    ):
        _parse_environment_bool(
            invalid_value,
            default=False,
            variable_name="TEST_FLAG",
        )


def test_settings_from_environment_enabled() -> None:
    settings = (
        DeepEvalSettings.from_environment(
            {
                DEEPEVAL_ENABLED_ENV: "true",
                DEEPEVAL_LIVE_ENV: "false",
                DEEPEVAL_EXTERNAL_ONLY_ENV: "true",
            }
        )
    )

    assert settings.enabled is True
    assert settings.live_enabled is False
    assert settings.external_only is True


def test_settings_can_disable_external_only() -> None:
    settings = (
        DeepEvalSettings.from_environment(
            {
                DEEPEVAL_EXTERNAL_ONLY_ENV: "false",
            }
        )
    )

    assert settings.external_only is False


def test_require_enabled_blocks_disabled_settings() -> None:
    settings = DeepEvalSettings(
        enabled=False
    )

    with pytest.raises(
        DeepEvalConfigurationError,
        match=DEEPEVAL_ENABLED_ENV,
    ):
        settings.require_enabled()


def test_require_enabled_accepts_enabled_settings() -> None:
    settings = DeepEvalSettings(
        enabled=True
    )

    settings.require_enabled()


def test_require_live_blocks_when_integration_disabled() -> None:
    settings = DeepEvalSettings(
        enabled=False,
        live_enabled=True,
    )

    with pytest.raises(
        DeepEvalConfigurationError,
        match=DEEPEVAL_ENABLED_ENV,
    ):
        settings.require_live_enabled()


def test_require_live_blocks_when_live_disabled() -> None:
    settings = DeepEvalSettings(
        enabled=True,
        live_enabled=False,
    )

    with pytest.raises(
        DeepEvalConfigurationError,
        match=DEEPEVAL_LIVE_ENV,
    ):
        settings.require_live_enabled()


def test_require_live_accepts_both_flags() -> None:
    settings = DeepEvalSettings(
        enabled=True,
        live_enabled=True,
    )

    settings.require_live_enabled()


# ============================================================
# DISPONIBILIDADE
# ============================================================


def test_availability_ready_property() -> None:
    availability = DeepEvalAvailability(
        installed=True,
        package_version="4.1.3",
        llm_test_case_available=True,
        evaluate_available=True,
    )

    assert availability.ready is True


@pytest.mark.parametrize(
    "availability",
    (
        DeepEvalAvailability(
            installed=False,
            package_version=None,
            llm_test_case_available=False,
            evaluate_available=False,
        ),
        DeepEvalAvailability(
            installed=True,
            package_version="4.1.3",
            llm_test_case_available=False,
            evaluate_available=True,
        ),
        DeepEvalAvailability(
            installed=True,
            package_version="4.1.3",
            llm_test_case_available=True,
            evaluate_available=False,
        ),
        DeepEvalAvailability(
            installed=True,
            package_version="4.1.3",
            llm_test_case_available=True,
            evaluate_available=True,
            error="erro",
        ),
    ),
)
def test_availability_not_ready(
    availability: DeepEvalAvailability,
) -> None:
    assert availability.ready is False


def test_real_deepeval_availability() -> None:
    availability = deepeval_availability()

    assert availability.installed is True
    assert availability.package_version == "4.1.3"
    assert (
        availability.llm_test_case_available
        is True
    )
    assert availability.evaluate_available is True
    assert availability.ready is True
    assert availability.error is None


def test_require_deepeval_returns_availability() -> None:
    availability = require_deepeval()

    assert availability.ready is True
    assert availability.package_version == "4.1.3"


def test_require_deepeval_blocks_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unavailable = DeepEvalAvailability(
        installed=False,
        package_version=None,
        llm_test_case_available=False,
        evaluate_available=False,
        error="Pacote ausente.",
    )

    monkeypatch.setattr(
        (
            "src.evaluation.deepeval_integration."
            "deepeval_availability"
        ),
        lambda: unavailable,
    )

    with pytest.raises(
        DeepEvalUnavailableError,
        match="Pacote ausente",
    ):
        require_deepeval()


# ============================================================
# NORMALIZAÇÃO
# ============================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (
            None,
            None,
        ),
        (
            "",
            None,
        ),
        (
            "   ",
            None,
        ),
        (
            " texto ",
            "texto",
        ),
        (
            123,
            "123",
        ),
    ),
)
def test_optional_text(
    value: Any,
    expected: str | None,
) -> None:
    assert _optional_text(value) == expected


def test_normalize_text_sequence() -> None:
    normalized = _normalize_text_sequence(
        (
            " primeiro ",
            "segundo",
            "",
            "primeiro",
            "segundo ",
        )
    )

    assert normalized == (
        "primeiro",
        "segundo",
    )


def test_normalize_text_sequence_none() -> None:
    assert (
        _normalize_text_sequence(None)
        == ()
    )


@pytest.mark.parametrize(
    "invalid_value",
    (
        "texto",
        b"bytes",
        bytearray(b"value"),
    ),
)
def test_normalize_text_sequence_rejects_single_string(
    invalid_value: Any,
) -> None:
    with pytest.raises(
        ValueError,
        match="sequência de textos",
    ):
        _normalize_text_sequence(
            invalid_value
        )


# ============================================================
# PAYLOAD
# ============================================================


def test_payload_normalizes_values() -> None:
    payload = DeepEvalCasePayload(
        case_id="  case-001  ",
        input_text="  Entrada  ",
        actual_output="  Resposta  ",
        expected_output="  Esperada  ",
        context=(
            " contexto ",
            "contexto",
        ),
        retrieval_context=(
            " documento ",
        ),
        metadata={
            "source": "test",
        },
    )

    assert payload.case_id == "case-001"
    assert payload.input_text == "Entrada"
    assert payload.actual_output == "Resposta"
    assert payload.expected_output == "Esperada"
    assert payload.context == (
        "contexto",
    )
    assert payload.retrieval_context == (
        "documento",
    )
    assert isinstance(
        payload.metadata,
        MappingProxyType,
    )


@pytest.mark.parametrize(
    ("field_name", "field_value", "message"),
    (
        (
            "case_id",
            " ",
            "case_id",
        ),
        (
            "input_text",
            " ",
            "input_text",
        ),
        (
            "actual_output",
            " ",
            "actual_output",
        ),
    ),
)
def test_payload_rejects_empty_required_fields(
    field_name: str,
    field_value: str,
    message: str,
) -> None:
    values = {
        "case_id": "case-001",
        "input_text": "Entrada",
        "actual_output": "Resposta",
    }

    values[field_name] = field_value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        DeepEvalCasePayload(**values)


def test_payload_metadata_is_immutable() -> None:
    original_metadata = {
        "source": "test",
    }

    payload = DeepEvalCasePayload(
        case_id="case-001",
        input_text="Entrada",
        actual_output="Resposta",
        metadata=original_metadata,
    )

    original_metadata["source"] = "changed"

    assert payload.metadata["source"] == "test"

    with pytest.raises(TypeError):
        payload.metadata["source"] = "invalid"


# ============================================================
# CONVERSAS
# ============================================================


def test_render_conversation_turn() -> None:
    turn = ConversationTurn(
        role="user",
        content="Preciso organizar meu orçamento.",
        turn_index=2,
    )

    assert _render_conversation_turn(turn) == (
        "[2] user: Preciso organizar meu orçamento."
    )


def test_render_conversation_context(
    conversation_case: InnaEvaluationCase,
) -> None:
    context = render_conversation_context(
        conversation_case
    )

    assert len(context) == 3
    assert context[0].startswith(
        "[0] user:"
    )
    assert context[1].startswith(
        "[1] assistant:"
    )
    assert context[2].startswith(
        "[2] user:"
    )


def test_render_case_input_prefers_input_text(
    conversation_case: InnaEvaluationCase,
) -> None:
    rendered = render_case_input(
        conversation_case
    )

    assert rendered == (
        conversation_case.input_text
    )


def test_render_case_input_uses_conversation_when_empty() -> None:
    case = InnaEvaluationCase(
        case_id="conversation-only",
        input_text="",
        conversation=(
            ConversationTurn(
                role="user",
                content="Mensagem inicial.",
                turn_index=0,
            ),
            ConversationTurn(
                role="assistant",
                content="Resposta inicial.",
                turn_index=1,
            ),
        ),
    )

    rendered = render_case_input(case)

    assert rendered == (
        "[0] user: Mensagem inicial.\n"
        "[1] assistant: Resposta inicial."
    )


# ============================================================
# POLÍTICA DE PRIVACIDADE
# ============================================================


def test_external_public_case_is_allowed(
    public_case: InnaEvaluationCase,
) -> None:
    ensure_external_case_allowed(
        public_case
    )


def test_external_policy_rejects_flag_disabled() -> None:
    case = build_external_case(
        external_evaluation_allowed=False
    )

    with pytest.raises(
        DeepEvalPrivacyError,
        match="não está autorizado",
    ):
        ensure_external_case_allowed(case)


@pytest.mark.parametrize(
    "privacy_level",
    (
        PrivacyLevel.INTERNAL,
        PrivacyLevel.CONFIDENTIAL,
    ),
)
def test_external_policy_rejects_non_public_privacy(
    privacy_level: PrivacyLevel,
) -> None:
    case = build_external_case(
        privacy_level=privacy_level
    )

    with pytest.raises(
        DeepEvalPrivacyError,
        match="privacidade público",
    ):
        ensure_external_case_allowed(case)


def test_restricted_case_cannot_enable_external_evaluation() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "RESTRICTED não podem permitir "
            "avaliação externa"
        ),
    ):
        build_external_case(
            privacy_level=PrivacyLevel.RESTRICTED,
            external_evaluation_allowed=True,
        )


def test_restricted_case_is_blocked_by_deepeval_policy() -> None:
    case = build_external_case(
        privacy_level=PrivacyLevel.RESTRICTED,
        external_evaluation_allowed=False,
    )

    with pytest.raises(
        DeepEvalPrivacyError,
        match="não está autorizado",
    ):
        ensure_external_case_allowed(case)


def test_external_policy_rejects_non_synthetic() -> None:
    case = build_external_case(
        synthetic=False
    )

    with pytest.raises(
        DeepEvalPrivacyError,
        match="marcado como sintético",
    ):
        ensure_external_case_allowed(case)


def test_external_policy_rejects_not_external_safe() -> None:
    case = build_external_case(
        external_safe=False
    )

    with pytest.raises(
        DeepEvalPrivacyError,
        match="external_safe",
    ):
        ensure_external_case_allowed(case)


def test_internal_hitl_case_is_blocked(
    internal_case: InnaEvaluationCase,
) -> None:
    with pytest.raises(
        DeepEvalPrivacyError,
        match="não está autorizado",
    ):
        ensure_external_case_allowed(
            internal_case
        )


# ============================================================
# CONSTRUÇÃO DO PAYLOAD DEEPEVAL
# ============================================================


def test_build_local_payload(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    payload = build_deepeval_payload(
        public_case,
        actual_output=actual_output,
        context=(
            "Contexto adicional.",
        ),
        retrieval_context=(
            "Documento recuperado.",
        ),
        metadata={
            "execution_mode": "dry-run",
        },
        external_run=False,
    )

    assert payload.case_id == (
        public_case.case_id
    )
    assert payload.input_text == (
        public_case.input_text
    )
    assert payload.actual_output == (
        actual_output
    )
    assert payload.context == (
        "Contexto adicional.",
    )
    assert payload.retrieval_context == (
        "Documento recuperado.",
    )
    assert payload.metadata[
        "execution_mode"
    ] == "dry-run"
    assert payload.metadata[
        "dataset_name"
    ] == public_case.dataset_name


def test_build_conversation_payload_combines_context(
    conversation_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    payload = build_deepeval_payload(
        conversation_case,
        actual_output=actual_output,
        context=(
            "Contexto adicional.",
        ),
    )

    assert len(payload.context) == 4
    assert payload.context[-1] == (
        "Contexto adicional."
    )


def test_build_payload_removes_duplicate_context(
    conversation_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    conversation_context = (
        render_conversation_context(
            conversation_case
        )
    )

    payload = build_deepeval_payload(
        conversation_case,
        actual_output=actual_output,
        context=(
            conversation_context[0],
            "Novo contexto.",
            conversation_context[0],
        ),
    )

    assert payload.context.count(
        conversation_context[0]
    ) == 1


def test_build_external_payload(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    payload = build_deepeval_payload(
        public_case,
        actual_output=actual_output,
        metadata={
            "execution_mode": "external-test",
        },
        external_run=True,
    )

    assert payload.case_id == (
        public_case.case_id
    )
    assert payload.metadata[
        "synthetic"
    ] is True
    assert payload.metadata[
        "privacy_level"
    ] == "public"


def test_build_external_payload_blocks_internal_case(
    internal_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    with pytest.raises(
        DeepEvalPrivacyError,
    ):
        build_deepeval_payload(
            internal_case,
            actual_output=actual_output,
            external_run=True,
        )


# ============================================================
# COMPATIBILIDADE COM CONSTRUTORES
# ============================================================


def test_supported_constructor_arguments_filters_values() -> None:
    class Constructor:
        def __init__(
            self,
            input: str,
            actual_output: str,
        ) -> None:
            self.input = input
            self.actual_output = actual_output

    values = {
        "input": "Entrada",
        "actual_output": "Resposta",
        "expected_output": "Esperada",
        "context": [],
    }

    filtered = (
        _supported_constructor_arguments(
            Constructor,
            values,
        )
    )

    assert filtered == {
        "input": "Entrada",
        "actual_output": "Resposta",
    }


def test_supported_constructor_arguments_with_kwargs() -> None:
    class Constructor:
        def __init__(
            self,
            input: str,
            **kwargs: Any,
        ) -> None:
            self.input = input
            self.kwargs = kwargs

    values = {
        "input": "Entrada",
        "actual_output": "Resposta",
        "expected_output": "Esperada",
    }

    filtered = (
        _supported_constructor_arguments(
            Constructor,
            values,
        )
    )

    assert filtered == values


# ============================================================
# CRIAÇÃO REAL DO LLMTestCase
# ============================================================


def test_create_real_llm_test_case(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    payload = build_deepeval_payload(
        public_case,
        actual_output=actual_output,
        retrieval_context=(
            "Documento financeiro sintético.",
        ),
    )

    test_case = create_llm_test_case(
        payload
    )

    assert test_case.input == (
        public_case.input_text
    )
    assert test_case.actual_output == (
        actual_output
    )
    assert test_case.retrieval_context == [
        "Documento financeiro sintético."
    ]


def test_convert_case_to_deepeval(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    conversion = convert_case_to_deepeval(
        public_case,
        actual_output=actual_output,
        retrieval_context=(
            "Documento sintético.",
        ),
        metadata={
            "runner": "pytest",
        },
    )

    assert isinstance(
        conversion,
        DeepEvalConversion,
    )
    assert conversion.case_id == (
        public_case.case_id
    )
    assert conversion.deepeval_version == (
        "4.1.3"
    )
    assert conversion.external_run is False
    assert conversion.payload.metadata[
        "runner"
    ] == "pytest"
    assert conversion.llm_test_case.input


def test_convert_public_case_for_external_run(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    conversion = convert_case_to_deepeval(
        public_case,
        actual_output=actual_output,
        external_run=True,
    )

    assert conversion.external_run is True


def test_convert_internal_case_for_external_run_is_blocked(
    internal_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    with pytest.raises(
        DeepEvalPrivacyError,
    ):
        convert_case_to_deepeval(
            internal_case,
            actual_output=actual_output,
            external_run=True,
        )


def test_conversion_does_not_execute_metrics(
    public_case: InnaEvaluationCase,
    actual_output: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden_evaluate(
        *args: Any,
        **kwargs: Any,
    ) -> None:
        nonlocal called
        called = True

        raise AssertionError(
            "deepeval.evaluate não deveria ser chamado."
        )

    monkeypatch.setattr(
        "deepeval.evaluate",
        forbidden_evaluate,
    )

    conversion = convert_case_to_deepeval(
        public_case,
        actual_output=actual_output,
    )

    assert conversion.llm_test_case is not None
    assert called is False


# ============================================================
# SEGURANÇA DE METADADOS
# ============================================================


def test_payload_metadata_does_not_share_mutable_reference(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    metadata = {
        "execution_id": "run-001",
    }

    payload = build_deepeval_payload(
        public_case,
        actual_output=actual_output,
        metadata=metadata,
    )

    metadata["execution_id"] = "changed"

    assert payload.metadata[
        "execution_id"
    ] == "run-001"


def test_external_payload_metadata_is_mapping(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    payload = build_deepeval_payload(
        public_case,
        actual_output=actual_output,
        external_run=True,
    )

    assert isinstance(
        payload.metadata,
        Mapping,
    )


def test_external_payload_does_not_include_complete_case_metadata(
    public_case: InnaEvaluationCase,
    actual_output: str,
) -> None:
    payload = build_deepeval_payload(
        public_case,
        actual_output=actual_output,
        external_run=True,
    )

    allowed_keys = {
        "case_id",
        "dataset_name",
        "dataset_version",
        "case_version",
        "category",
        "language",
        "currency",
        "privacy_level",
        "synthetic",
    }

    assert set(payload.metadata).issuperset(
        allowed_keys
    )

    assert "external_safe" not in (
        payload.metadata
    )