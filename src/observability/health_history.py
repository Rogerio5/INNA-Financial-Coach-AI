"""
Persistência histórica do INNA Health Score.

Responsabilidades:
- criar a tabela de snapshots;
- salvar avaliações do Health Score;
- consultar o histórico;
- calcular tendência entre snapshots;
- evitar registros duplicados em intervalos muito curtos.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


NOME_TABELA = "health_score_snapshots_inna"


def _carregar_database_url() -> str:
    """
    Obtém DATABASE_URL do ambiente ou do arquivo .env.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        try:
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=Path(".env"))

            database_url = os.getenv("DATABASE_URL")

        except Exception:
            database_url = None

    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrada.")

    return database_url


def _criar_engine():
    """
    Cria uma engine SQLAlchemy com verificação de conexão.
    """
    from sqlalchemy import create_engine

    return create_engine(
        _carregar_database_url(),
        pool_pre_ping=True,
    )


def inicializar_tabela_health_history() -> dict[str, Any]:
    """
    Cria a tabela e seus índices caso ainda não existam.
    """
    try:
        from sqlalchemy import text

        engine = _criar_engine()

        comando = text(f"""
            CREATE TABLE IF NOT EXISTS {NOME_TABELA} (
                id BIGSERIAL PRIMARY KEY,
                criado_em TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),

                score_global NUMERIC(6, 2) NOT NULL,

                score_tools NUMERIC(6, 2) NOT NULL
                    DEFAULT 0,

                score_rag NUMERIC(6, 2) NOT NULL
                    DEFAULT 0,

                score_memoria NUMERIC(6, 2) NOT NULL
                    DEFAULT 0,

                score_infraestrutura NUMERIC(6, 2) NOT NULL
                    DEFAULT 0,

                score_timeline NUMERIC(6, 2) NOT NULL
                    DEFAULT 0,

                score_performance NUMERIC(6, 2) NOT NULL
                    DEFAULT 0,

                classificacao VARCHAR(50),
                status VARCHAR(50),

                componente_mais_forte VARCHAR(80),
                componente_mais_fraco VARCHAR(80),

                total_anomalias INTEGER NOT NULL
                    DEFAULT 0,

                origem VARCHAR(50) NOT NULL
                    DEFAULT 'manual',

                metricas_json JSONB NOT NULL
                    DEFAULT '{{}}'::jsonb,

                health_json JSONB NOT NULL
                    DEFAULT '{{}}'::jsonb,

                erros_coleta_json JSONB NOT NULL
                    DEFAULT '[]'::jsonb
            );
        """)

        indice_data = text(f"""
            CREATE INDEX IF NOT EXISTS
            idx_{NOME_TABELA}_criado_em
            ON {NOME_TABELA} (criado_em DESC);
        """)

        indice_score = text(f"""
            CREATE INDEX IF NOT EXISTS
            idx_{NOME_TABELA}_score_global
            ON {NOME_TABELA} (score_global);
        """)

        with engine.begin() as connection:
            connection.execute(comando)
            connection.execute(indice_data)
            connection.execute(indice_score)

        engine.dispose()

        return {
            "ok": True,
            "message": ("Tabela de histórico do Health Score inicializada."),
            "tabela": NOME_TABELA,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (f"Erro ao inicializar histórico: {exc}"),
            "tabela": NOME_TABELA,
        }


def _extrair_score_componente(
    health: dict[str, Any],
    nome: str,
) -> float:
    """
    Extrai de forma segura o score de um componente.
    """
    componentes = health.get(
        "componentes",
        {},
    )

    item = componentes.get(
        nome,
        {},
    )

    return round(
        float(
            item.get(
                "score",
                0,
            )
        ),
        2,
    )


def preparar_snapshot(
    resultado: dict[str, Any],
    *,
    origem: str = "manual",
) -> dict[str, Any]:
    """
    Converte a coleta real em um snapshot persistível.
    """
    health = resultado.get(
        "health",
        {},
    )

    anomalias = resultado.get(
        "anomalias",
        {},
    )

    return {
        "score_global": round(
            float(
                health.get(
                    "score_global",
                    0,
                )
            ),
            2,
        ),
        "score_tools": _extrair_score_componente(
            health,
            "tools",
        ),
        "score_rag": _extrair_score_componente(
            health,
            "rag",
        ),
        "score_memoria": _extrair_score_componente(
            health,
            "memoria",
        ),
        "score_infraestrutura": (
            _extrair_score_componente(
                health,
                "infraestrutura",
            )
        ),
        "score_timeline": _extrair_score_componente(
            health,
            "timeline",
        ),
        "score_performance": (
            _extrair_score_componente(
                health,
                "performance",
            )
        ),
        "classificacao": str(
            health.get(
                "classificacao",
                "",
            )
        ),
        "status": str(
            health.get(
                "status",
                "",
            )
        ),
        "componente_mais_forte": str(
            health.get(
                "componente_mais_forte",
                "",
            )
        ),
        "componente_mais_fraco": str(
            health.get(
                "componente_mais_fraco",
                "",
            )
        ),
        "total_anomalias": int(
            anomalias.get(
                "total_anomalias",
                0,
            )
        ),
        "origem": str(origem or "manual")[:50],
        "metricas_json": resultado.get(
            "metricas",
            {},
        ),
        "health_json": health,
        "erros_coleta_json": resultado.get(
            "erros_coleta",
            [],
        ),
    }


def salvar_health_snapshot(
    resultado: dict[str, Any],
    *,
    origem: str = "manual",
    evitar_duplicado_minutos: int = 5,
) -> dict[str, Any]:
    """
    Salva um snapshot.

    Quando configurado, evita salvar outro registro muito
    próximo com o mesmo score global e a mesma origem.
    """
    inicializacao = inicializar_tabela_health_history()

    if not inicializacao.get("ok"):
        return inicializacao

    snapshot = preparar_snapshot(
        resultado,
        origem=origem,
    )

    try:
        from sqlalchemy import text

        engine = _criar_engine()

        consulta_duplicado = text(f"""
            SELECT id, criado_em
            FROM {NOME_TABELA}
            WHERE score_global = :score_global
              AND origem = :origem
              AND criado_em >= (
                    NOW()
                    - (
                        :minutos
                        * INTERVAL '1 minute'
                    )
              )
            ORDER BY criado_em DESC
            LIMIT 1;
        """)

        inserir = text(f"""
            INSERT INTO {NOME_TABELA} (
                score_global,
                score_tools,
                score_rag,
                score_memoria,
                score_infraestrutura,
                score_timeline,
                score_performance,
                classificacao,
                status,
                componente_mais_forte,
                componente_mais_fraco,
                total_anomalias,
                origem,
                metricas_json,
                health_json,
                erros_coleta_json
            )
            VALUES (
                :score_global,
                :score_tools,
                :score_rag,
                :score_memoria,
                :score_infraestrutura,
                :score_timeline,
                :score_performance,
                :classificacao,
                :status,
                :componente_mais_forte,
                :componente_mais_fraco,
                :total_anomalias,
                :origem,
                CAST(:metricas_json AS JSONB),
                CAST(:health_json AS JSONB),
                CAST(:erros_coleta_json AS JSONB)
            )
            RETURNING id, criado_em;
        """)

        parametros = {
            **snapshot,
            "metricas_json": json.dumps(
                snapshot["metricas_json"],
                ensure_ascii=False,
                default=str,
            ),
            "health_json": json.dumps(
                snapshot["health_json"],
                ensure_ascii=False,
                default=str,
            ),
            "erros_coleta_json": json.dumps(
                snapshot["erros_coleta_json"],
                ensure_ascii=False,
                default=str,
            ),
        }

        with engine.begin() as connection:
            duplicado = (
                connection.execute(
                    consulta_duplicado,
                    {
                        "score_global": snapshot["score_global"],
                        "origem": snapshot["origem"],
                        "minutos": max(
                            int(evitar_duplicado_minutos),
                            0,
                        ),
                    },
                )
                .mappings()
                .first()
            )

            if duplicado:
                engine.dispose()

                return {
                    "ok": True,
                    "salvo": False,
                    "duplicado": True,
                    "id": int(duplicado["id"]),
                    "criado_em": duplicado["criado_em"],
                    "message": ("Snapshot semelhante já foi salvo recentemente."),
                }

            registro = (
                connection.execute(
                    inserir,
                    parametros,
                )
                .mappings()
                .first()
            )

        engine.dispose()

        return {
            "ok": True,
            "salvo": True,
            "duplicado": False,
            "id": int(registro["id"]),
            "criado_em": registro["criado_em"],
            "message": ("Snapshot do Health Score salvo."),
        }

    except Exception as exc:
        return {
            "ok": False,
            "salvo": False,
            "duplicado": False,
            "message": (f"Erro ao salvar snapshot: {exc}"),
        }


def carregar_health_history(
    *,
    limite: int = 500,
    dias: int | None = 30,
) -> dict[str, Any]:
    """
    Carrega os snapshots históricos mais recentes.
    """
    inicializacao = inicializar_tabela_health_history()

    if not inicializacao.get("ok"):
        return {
            **inicializacao,
            "df": pd.DataFrame(),
        }

    try:
        from sqlalchemy import text

        engine = _criar_engine()

        filtro_periodo = ""

        parametros: dict[str, Any] = {
            "limite": max(
                int(limite),
                1,
            ),
        }

        if dias is not None:
            filtro_periodo = """
                WHERE criado_em >= (
                    NOW()
                    - (
                        :dias
                        * INTERVAL '1 day'
                    )
                )
            """

            parametros["dias"] = max(
                int(dias),
                1,
            )

        consulta = text(f"""
            SELECT
                id,
                criado_em,
                score_global,
                score_tools,
                score_rag,
                score_memoria,
                score_infraestrutura,
                score_timeline,
                score_performance,
                classificacao,
                status,
                componente_mais_forte,
                componente_mais_fraco,
                total_anomalias,
                origem,
                metricas_json,
                health_json,
                erros_coleta_json
            FROM {NOME_TABELA}
            {filtro_periodo}
            ORDER BY criado_em DESC
            LIMIT :limite;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(
                consulta,
                connection,
                params=parametros,
            )

        engine.dispose()

        if not df.empty:
            df["criado_em"] = pd.to_datetime(
                df["criado_em"],
                utc=True,
                errors="coerce",
            )

            colunas_score = [
                "score_global",
                "score_tools",
                "score_rag",
                "score_memoria",
                "score_infraestrutura",
                "score_timeline",
                "score_performance",
            ]

            for coluna in colunas_score:
                df[coluna] = pd.to_numeric(
                    df[coluna],
                    errors="coerce",
                )

        return {
            "ok": True,
            "message": ("Histórico carregado."),
            "df": df,
            "total": len(df),
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (f"Erro ao carregar histórico: {exc}"),
            "df": pd.DataFrame(),
            "total": 0,
        }


def calcular_tendencia_health(
    df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Compara os dois snapshots mais recentes.
    """
    if df is None or len(df) < 2:
        return {
            "tem_comparacao": False,
            "delta": 0.0,
            "direcao": "estavel",
            "icone": "➖",
            "mensagem": (
                "Ainda não existem snapshots suficientes para calcular tendência."
            ),
        }

    base = df.copy()

    base["criado_em"] = pd.to_datetime(
        base["criado_em"],
        utc=True,
        errors="coerce",
    )

    base = base.sort_values(
        "criado_em",
        ascending=False,
    )

    atual = float(base.iloc[0]["score_global"])

    anterior = float(base.iloc[1]["score_global"])

    delta = round(
        atual - anterior,
        2,
    )

    if delta > 0:
        direcao = "melhora"
        icone = "📈"
        mensagem = (
            f"O Health Score melhorou {delta:.2f} ponto(s) desde o snapshot anterior."
        )

    elif delta < 0:
        direcao = "piora"
        icone = "📉"
        mensagem = (
            f"O Health Score caiu {abs(delta):.2f} ponto(s) desde o snapshot anterior."
        )

    else:
        direcao = "estavel"
        icone = "➖"
        mensagem = "O Health Score permaneceu estável."

    return {
        "tem_comparacao": True,
        "score_atual": round(
            atual,
            2,
        ),
        "score_anterior": round(
            anterior,
            2,
        ),
        "delta": delta,
        "direcao": direcao,
        "icone": icone,
        "mensagem": mensagem,
    }


__all__ = [
    "NOME_TABELA",
    "inicializar_tabela_health_history",
    "preparar_snapshot",
    "salvar_health_snapshot",
    "carregar_health_history",
    "calcular_tendencia_health",
]
