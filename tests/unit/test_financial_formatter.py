from src.services.formatters.financial import (
    calcular_percentual_variacao,
    calcular_valor_semanal,
    formatar_comparacao_monetaria,
    formatar_moeda,
    formatar_percentual,
    formatar_variacao_monetaria,
)


def test_formatar_moeda_brl():
    assert formatar_moeda(
        6300,
        "BRL",
        idioma="pt",
    ) == "R$ 6.300,00"


def test_formatar_moeda_usd():
    assert formatar_moeda(
        6300,
        "USD",
        idioma="en",
    ) == "US$ 6,300.00"


def test_formatar_percentual_pt():
    assert formatar_percentual(
        52.3809,
        idioma="pt",
    ) == "52,4%"


def test_calcular_valor_semanal():
    assert calcular_valor_semanal(1200) == 300.0


def test_calcular_percentual_variacao():
    resultado = calcular_percentual_variacao(
        6300,
        6500,
    )

    assert round(resultado, 2) == 3.17


def test_formatar_variacao_monetaria():
    assert formatar_variacao_monetaria(
        200,
        "BRL",
        idioma="pt",
    ) == "▲ +R$ 200,00"


def test_formatar_comparacao_monetaria():
    resultado = formatar_comparacao_monetaria(
        6300,
        6500,
        "BRL",
        idioma="pt",
    )

    assert "R$ 6.300,00" in resultado
    assert "R$ 6.500,00" in resultado
    assert "+3,17%" in resultado
