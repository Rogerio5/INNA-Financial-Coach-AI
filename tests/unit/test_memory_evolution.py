from src.services.memory.evolution import (
    calcular_evolucao_memoria,
    copiar_memoria,
)


def test_copiar_memoria_sem_referencia_compartilhada():
    memoria = {"memoria_json": {"meta": 100}}

    copia = copiar_memoria(memoria)
    copia["memoria_json"]["meta"] = 200

    assert memoria["memoria_json"]["meta"] == 100


def test_calcular_evolucao_financeira():
    antes = {
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "valor_reserva": 1200,
    }

    depois = {
        "renda_mensal": 6500,
        "gastos_mensais": 3200,
        "valor_reserva": 1300,
    }

    resultado = calcular_evolucao_memoria(
        antes,
        depois,
    )

    assert resultado["tem_evolucao"] is True
    assert len(resultado["evolucoes"]) == 3

    mapa = {item["campo"]: item for item in resultado["evolucoes"]}

    assert mapa["renda_mensal"]["diferenca"] == 200.0
    assert mapa["gastos_mensais"]["diferenca"] == -100.0
    assert mapa["valor_reserva"]["diferenca"] == 100.0


def test_sem_evolucao():
    memoria = {
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "valor_reserva": 1200,
    }

    resultado = calcular_evolucao_memoria(
        memoria,
        memoria,
    )

    assert resultado["tem_evolucao"] is False
    assert resultado["evolucoes"] == []
