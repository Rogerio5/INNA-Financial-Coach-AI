from src.agents.complexity_detector import (
    assess_request_complexity,
)


def test_single_rag_capability_is_simple():
    result = assess_request_complexity(
        user_message="Explique reserva de emergencia.",
        intent="consulta_rag",
        use_rag=True,
    )

    assert result.complexity == "simple"
    assert result.signals == ()


def test_simple_financial_diagnosis_is_simple():
    result = assess_request_complexity(
        user_message="Analise meu orçamento.",
        intent="diagnostico_financeiro",
        use_database=True,
    )

    assert result.complexity == "simple"


def test_direct_report_request_is_simple():
    result = assess_request_complexity(
        user_message="Gere meu relatório.",
        intent="relatorio",
        use_database=True,
        generate_report=True,
    )

    assert result.complexity == "simple"


def test_composite_diagnosis_report_is_complex():
    result = assess_request_complexity(
        user_message=(
            "Analise minhas finanças e depois "
            "gere um relatório."
        ),
        intent="diagnostico_financeiro",
        use_database=True,
        generate_report=True,
    )

    assert result.complexity == "complex"
    assert (
        "composite_report_workflow"
        in result.signals
    )


def test_database_and_rag_is_complex():
    result = assess_request_complexity(
        user_message="Compare meu histórico com as orientações.",
        intent="diagnostico_financeiro",
        use_database=True,
        use_rag=True,
    )

    assert result.complexity == "complex"
    assert "database_and_rag" in result.signals


def test_handoff_is_complex():
    result = assess_request_complexity(
        user_message="Continue em outro agente.",
        intent="consulta_rag",
        handoff_required=True,
    )

    assert result.complexity == "complex"
    assert "handoff_required" in result.signals


def test_multi_domain_is_complex():
    result = assess_request_complexity(
        user_message="Analise dados de vários módulos.",
        intent="diagnostico_financeiro",
        multi_domain=True,
    )

    assert result.complexity == "complex"
    assert "multi_domain" in result.signals
