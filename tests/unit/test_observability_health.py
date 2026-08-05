from src.observability.health import (
    calcular_health_score_global,
    calcular_score_infraestrutura,
    calcular_score_memoria,
    calcular_score_performance,
    calcular_score_rag,
    calcular_score_timeline,
    calcular_score_tools,
    classificar_score,
    limitar_score,
)


def test_limitar_score():
    assert limitar_score(120) == 100.0
    assert limitar_score(-20) == 0.0
    assert limitar_score(85.55) == 85.5


def test_classificar_score():
    assert classificar_score(98)["classificacao"] == "Excelente"

    assert classificar_score(60)["status"] == "critico"


def test_score_tools_saudavel():
    resultado = calcular_score_tools(
        taxa_sucesso=100,
        confianca_media=95,
        percentual_sem_tool=0,
        total_anomalias=0,
    )

    assert resultado["score"] == 100.0


def test_score_infraestrutura():
    resultado = calcular_score_infraestrutura(
        total_componentes=6,
        total_operacionais=6,
    )

    assert resultado["score"] == 100.0


def test_score_rag_completo():
    resultado = calcular_score_rag(
        documentos_ativos=2,
        documentos_com_embeddings=2,
        embeddings_ativos=10,
        embeddings_inativos=0,
    )

    assert resultado["score"] == 100.0


def test_score_memoria_indisponivel():
    resultado = calcular_score_memoria(
        tabela_disponivel=False,
        total_usuarios_com_memoria=0,
    )

    assert resultado["score"] == 0.0


def test_score_timeline_com_cold_start():
    resultado = calcular_score_timeline(
        traces_analisados=10,
        traces_com_falha=0,
        percentual_cold_start=30,
    )

    assert resultado["score"] < 100


def test_score_performance_saudavel():
    resultado = calcular_score_performance(
        p95_tools_ms=500,
        p95_trace_ms=5000,
    )

    assert resultado["score"] == 100.0


def test_health_score_global():
    componentes = {
        "tools": {"score": 100},
        "rag": {"score": 95},
        "memoria": {"score": 100},
        "infraestrutura": {"score": 100},
        "timeline": {"score": 90},
        "performance": {"score": 80},
    }

    resultado = calcular_health_score_global(componentes)

    assert resultado["score_global"] == 95.0

    assert resultado["componente_mais_fraco"] == "performance"

    assert resultado["componente_mais_forte"] in {
        "tools",
        "memoria",
        "infraestrutura",
    }


def test_health_com_componente_ausente():
    resultado = calcular_health_score_global(
        {
            "tools": {
                "score": 100,
            }
        }
    )

    assert resultado["score_global"] == 25.0
