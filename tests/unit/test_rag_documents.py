import pytest

from src.services.rag.documents import (
    gerar_nome_arquivo_salvo,
    normalizar_nome_arquivo,
    validar_extensao_documento,
)


def test_normalizar_nome_arquivo():
    resultado = normalizar_nome_arquivo(
        "Guia Árvore Financeira.md"
    )

    assert resultado == "Guia_Arvore_Financeira.md"


def test_validar_extensao_md():
    assert validar_extensao_documento(
        "guia.md"
    ) == ".md"


def test_validar_extensao_txt():
    assert validar_extensao_documento(
        "guia.txt"
    ) == ".txt"


def test_rejeitar_extensao_nao_permitida():
    with pytest.raises(ValueError):
        validar_extensao_documento(
            "arquivo.pdf"
        )


def test_nome_com_timestamp():
    resultado = gerar_nome_arquivo_salvo(
        "Guia Financeiro.md",
        usar_timestamp=True,
    )

    assert resultado.endswith(
        "_Guia_Financeiro.md"
    )


def test_nome_sem_timestamp():
    resultado = gerar_nome_arquivo_salvo(
        "Guia Financeiro.md",
        usar_timestamp=False,
    )

    assert resultado == "Guia_Financeiro.md"
