from src.services.memory.extractor import (
    extrair_memoria_da_mensagem_inna,
    mesclar_memoria_existente,
    normalizar_valor_financeiro,
)


def test_normalizar_valor_brasileiro():
    assert normalizar_valor_financeiro("R$ 6.300,00") == 6300.0


def test_normalizar_valor_inteiro():
    assert normalizar_valor_financeiro("1200") == 1200.0


def test_extrair_renda_gastos_reserva():
    resultado = extrair_memoria_da_mensagem_inna(
        "Agora ganho R$ 6.500, gasto R$ 3.200 e consigo guardar R$ 1.300 por mês."
    )

    assert resultado["tem_memoria"] is True
    assert resultado["dados"]["renda_mensal"] == 6500.0
    assert resultado["dados"]["gastos_mensais"] == 3200.0
    assert resultado["dados"]["valor_reserva"] == 1300.0


def test_mensagem_sem_memoria():
    resultado = extrair_memoria_da_mensagem_inna("Bom dia, tudo bem?")

    assert resultado["tem_memoria"] is False
    assert resultado["dados"] == {}


def test_mesclar_sem_apagar_dados_existentes():
    atual = {
        "nome": "Usuário Demo",
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "valor_reserva": 1200,
        "moeda": "BRL",
    }

    novos = {
        "gastos_mensais": 3200,
    }

    resultado = mesclar_memoria_existente(
        atual,
        novos,
    )

    assert resultado["renda_mensal"] == 6300
    assert resultado["gastos_mensais"] == 3200
    assert resultado["valor_reserva"] == 1200
