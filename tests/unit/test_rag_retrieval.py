from src.services.rag.retrieval import (
    inferir_categorias_pergunta,
)


def test_categoria_pix():
    resultado = inferir_categorias_pergunta("Recebi um Pix estranho, devo devolver?")

    assert "pix" in resultado
    assert "seguranca" in resultado


def test_categoria_cartao():
    resultado = inferir_categorias_pergunta("Minha fatura do cartão está alta.")

    assert "cartao_credito" in resultado


def test_categoria_reserva():
    resultado = inferir_categorias_pergunta("Como começar uma reserva financeira?")

    assert "reserva_financeira" in resultado


def test_categoria_geral():
    resultado = inferir_categorias_pergunta("Olá, quero aprender sobre finanças.")

    assert resultado == ["geral"]
