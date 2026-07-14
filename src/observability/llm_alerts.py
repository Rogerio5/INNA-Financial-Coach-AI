"""
Alertas persistentes de FinOps e desempenho de LLM.

Os alertas são determinísticos e não armazenam prompts,
perguntas ou respostas dos usuários.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


NOME_TABELA = "llm_alerts_inna"

ORDEM_SEVERIDADE = {
    "informativa": 1,
    "baixa": 2,
    "media": 3,
    "alta": 4,
    "critica": 5,
}


def _carregar_database_url() -> str:
    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:
        try:
            from dotenv import load_dotenv

            load_dotenv(
                dotenv_path=Path(".env"),
                override=False,
            )

            database_url = os.getenv(
                "DATABASE_URL"
            )
        except Exception:
            database_url = None

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não encontrada."
        )

    return database_url


def _criar_engine():
    from sqlalchemy import create_engine

    return create_engine(
        _carregar_database_url(),
        pool_pre_ping=True,
    )


def inicializar_tabela_llm_alerts() -> dict[str, Any]:
    """
    Cria a tabela de alertas e índices.
    """
    try:
        from sqlalchemy import text

        engine = _criar_engine()

        tabela = text(f"""
            CREATE TABLE IF NOT EXISTS {NOME_TABELA} (
                id BIGSERIAL PRIMARY KEY,
                criado_em TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),
                atualizado_em TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),

                codigo VARCHAR(120) NOT NULL,
                titulo VARCHAR(255) NOT NULL,
                descricao TEXT NOT NULL,

                categoria VARCHAR(80) NOT NULL,
                severidade VARCHAR(30) NOT NULL,

                status VARCHAR(30) NOT NULL
                    DEFAULT 'aberto',

                valor_atual NUMERIC(20, 8),
                valor_limite NUMERIC(20, 8),
                unidade VARCHAR(50),

                modelo VARCHAR(150),
                operacao VARCHAR(120),
                trace_id VARCHAR(255),

                dedupe_key VARCHAR(255) NOT NULL,

                recomendacao TEXT,
                metadados_json JSONB NOT NULL
                    DEFAULT '{{}}'::jsonb,

                resolvido_em TIMESTAMPTZ,
                resolvido_por VARCHAR(255),

                CONSTRAINT uq_llm_alert_dedupe_aberto
                    UNIQUE (dedupe_key, status)
            );
        """)

        indices = [
            text(f"""
                CREATE INDEX IF NOT EXISTS
                idx_{NOME_TABELA}_criado_em
                ON {NOME_TABELA}
                (criado_em DESC);
            """),
            text(f"""
                CREATE INDEX IF NOT EXISTS
                idx_{NOME_TABELA}_status
                ON {NOME_TABELA}
                (status);
            """),
            text(f"""
                CREATE INDEX IF NOT EXISTS
                idx_{NOME_TABELA}_severidade
                ON {NOME_TABELA}
                (severidade);
            """),
        ]

        with engine.begin() as connection:
            connection.execute(tabela)

            for indice in indices:
                connection.execute(indice)

        engine.dispose()

        return {
            "ok": True,
            "tabela": NOME_TABELA,
            "message": (
                "Tabela de alertas LLM inicializada."
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "tabela": NOME_TABELA,
            "message": (
                "Erro ao inicializar alertas: "
                f"{exc}"
            ),
        }


def _criar_alerta(
    *,
    codigo: str,
    titulo: str,
    descricao: str,
    categoria: str,
    severidade: str,
    valor_atual: float,
    valor_limite: float,
    unidade: str,
    recomendacao: str,
    modelo: str | None = None,
    operacao: str | None = None,
    trace_id: str | None = None,
    metadados: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Padroniza um alerta antes da persistência.
    """
    dedupe_partes = [
        codigo,
        modelo or "todos",
        operacao or "todas",
    ]

    return {
        "codigo": codigo,
        "titulo": titulo,
        "descricao": descricao,
        "categoria": categoria,
        "severidade": severidade,
        "ordem_severidade": (
            ORDEM_SEVERIDADE[severidade]
        ),
        "valor_atual": round(
            float(valor_atual),
            8,
        ),
        "valor_limite": round(
            float(valor_limite),
            8,
        ),
        "unidade": unidade,
        "modelo": modelo,
        "operacao": operacao,
        "trace_id": trace_id,
        "dedupe_key": ":".join(
            dedupe_partes
        )[:255],
        "recomendacao": recomendacao,
        "metadados": metadados or {},
    }


def detectar_alertas_llm(
    df: pd.DataFrame | None,
    finops: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Detecta alertas de custo, tokens, falhas e latência.
    """
    alertas: list[dict[str, Any]] = []

    situacao = finops.get(
        "situacao_orcamento",
        {},
    )

    projecao = finops.get(
        "situacao_projecao",
        {},
    )

    config = finops.get(
        "configuracao",
        {},
    )

    if situacao.get("status") in {
        "alerta",
        "critico",
        "excedido",
    }:
        severidade = (
            "critica"
            if situacao.get("status")
            == "excedido"
            else "alta"
            if situacao.get("status")
            == "critico"
            else "media"
        )

        alertas.append(
            _criar_alerta(
                codigo="orcamento_mensal",
                titulo="Uso elevado do orçamento de LLM",
                descricao=(
                    "O consumo acumulado atingiu "
                    f"{situacao.get('percentual_utilizado', 0):.2f}% "
                    "do orçamento mensal."
                ),
                categoria="finops",
                severidade=severidade,
                valor_atual=finops.get(
                    "custo_acumulado_usd",
                    0,
                ),
                valor_limite=config.get(
                    "orcamento_mensal_usd",
                    0,
                ),
                unidade="USD",
                recomendacao=(
                    "Revisar modelos, tamanho dos prompts, "
                    "quantidade de chunks e cache."
                ),
            )
        )

    if projecao.get("status") in {
        "alerta",
        "critico",
        "excedido",
    }:
        alertas.append(
            _criar_alerta(
                codigo="projecao_mensal",
                titulo="Projeção mensal acima do esperado",
                descricao=(
                    "A projeção mensal de consumo está próxima "
                    "ou acima do limite configurado."
                ),
                categoria="finops",
                severidade=(
                    "critica"
                    if projecao.get("status")
                    == "excedido"
                    else "alta"
                ),
                valor_atual=finops.get(
                    "projecao_mensal_usd",
                    0,
                ),
                valor_limite=config.get(
                    "orcamento_mensal_usd",
                    0,
                ),
                unidade="USD",
                recomendacao=(
                    "Avaliar o uso de Gemini Flash-Lite, reduzir "
                    "contexto e reutilizar resultados."
                ),
            )
        )

    if df is None or df.empty:
        return alertas

    base = df.copy()

    duracoes = pd.to_numeric(
        base.get(
            "duracao_ms",
            pd.Series(dtype=float),
        ),
        errors="coerce",
    ).fillna(0)

    tokens = pd.to_numeric(
        base.get(
            "tokens_totais",
            pd.Series(dtype=float),
        ),
        errors="coerce",
    ).fillna(0)

    sucessos = (
        base.get(
            "sucesso",
            pd.Series(
                [True] * len(base)
            ),
        )
        .fillna(False)
        .astype(bool)
    )

    chamadas_lentas = int(
        (duracoes >= 30000).sum()
    )

    if chamadas_lentas > 0:
        maior_duracao = float(
            duracoes.max()
        )

        alertas.append(
            _criar_alerta(
                codigo="chamadas_lentas",
                titulo="Chamadas de LLM com alta latência",
                descricao=(
                    f"Foram detectadas {chamadas_lentas} "
                    "chamada(s) acima de 30 segundos."
                ),
                categoria="performance",
                severidade=(
                    "alta"
                    if maior_duracao >= 120000
                    else "media"
                ),
                valor_atual=maior_duracao,
                valor_limite=30000,
                unidade="ms",
                recomendacao=(
                    "Verificar cold start, tamanho do prompt, "
                    "rede e tempo de resposta do provider."
                ),
            )
        )

    total_falhas = int(
        (~sucessos).sum()
    )

    if total_falhas > 0:
        taxa_falhas = (
            total_falhas
            / len(base)
        ) * 100

        alertas.append(
            _criar_alerta(
                codigo="falhas_llm",
                titulo="Falhas em chamadas de LLM",
                descricao=(
                    f"Foram detectadas {total_falhas} "
                    "falha(s), equivalentes a "
                    f"{taxa_falhas:.2f}% das chamadas."
                ),
                categoria="confiabilidade",
                severidade=(
                    "critica"
                    if taxa_falhas >= 30
                    else "alta"
                ),
                valor_atual=taxa_falhas,
                valor_limite=0,
                unidade="percentual",
                recomendacao=(
                    "Analisar tipo do erro, limites da API, "
                    "credenciais e estratégia de fallback."
                ),
            )
        )

    if len(tokens) > 0:
        media_tokens = float(
            tokens.mean()
        )

        if media_tokens >= 10000:
            alertas.append(
                _criar_alerta(
                    codigo="tokens_elevados",
                    titulo="Média elevada de tokens por chamada",
                    descricao=(
                        "A média de tokens por chamada atingiu "
                        f"{media_tokens:.0f} tokens."
                    ),
                    categoria="eficiencia",
                    severidade="media",
                    valor_atual=media_tokens,
                    valor_limite=10000,
                    unidade="tokens",
                    recomendacao=(
                        "Reduzir histórico, prompt, chunks "
                        "e documentos enviados ao modelo."
                    ),
                )
            )

    return sorted(
        alertas,
        key=lambda item: item[
            "ordem_severidade"
        ],
        reverse=True,
    )


def persistir_alerta_llm(
    alerta: dict[str, Any],
) -> dict[str, Any]:
    """
    Persiste um alerta, evitando duplicação aberta.
    """
    inicializacao = (
        inicializar_tabela_llm_alerts()
    )

    if not inicializacao.get("ok"):
        return inicializacao

    try:
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine = _criar_engine()

        inserir = text(f"""
            INSERT INTO {NOME_TABELA} (
                codigo,
                titulo,
                descricao,
                categoria,
                severidade,
                valor_atual,
                valor_limite,
                unidade,
                modelo,
                operacao,
                trace_id,
                dedupe_key,
                recomendacao,
                metadados_json
            )
            VALUES (
                :codigo,
                :titulo,
                :descricao,
                :categoria,
                :severidade,
                :valor_atual,
                :valor_limite,
                :unidade,
                :modelo,
                :operacao,
                :trace_id,
                :dedupe_key,
                :recomendacao,
                CAST(:metadados_json AS JSONB)
            )
            RETURNING id, criado_em;
        """)

        parametros = {
            **alerta,
            "metadados_json": json.dumps(
                alerta.get(
                    "metadados",
                    {},
                ),
                ensure_ascii=False,
                default=str,
            ),
        }

        parametros.pop(
            "ordem_severidade",
            None,
        )

        parametros.pop(
            "metadados",
            None,
        )

        try:
            with engine.begin() as connection:
                registro = connection.execute(
                    inserir,
                    parametros,
                ).mappings().first()

        except IntegrityError:
            engine.dispose()

            return {
                "ok": True,
                "salvo": False,
                "duplicado": True,
                "message": (
                    "Alerta aberto semelhante já existe."
                ),
            }

        engine.dispose()

        return {
            "ok": True,
            "salvo": True,
            "duplicado": False,
            "id": int(
                registro["id"]
            ),
            "criado_em": registro[
                "criado_em"
            ],
            "message": "Alerta salvo.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "salvo": False,
            "duplicado": False,
            "message": (
                "Erro ao persistir alerta: "
                f"{exc}"
            ),
        }


def avaliar_e_persistir_alertas(
    df: pd.DataFrame | None,
    finops: dict[str, Any],
) -> dict[str, Any]:
    """
    Detecta e persiste todos os alertas atuais.
    """
    detectados = detectar_alertas_llm(
        df,
        finops,
    )

    resultados = [
        persistir_alerta_llm(alerta)
        for alerta in detectados
    ]

    return {
        "ok": all(
            item.get("ok")
            for item in resultados
        ) if resultados else True,
        "alertas_detectados": detectados,
        "resultados_persistencia": resultados,
        "total_detectados": len(detectados),
        "total_salvos": sum(
            1
            for item in resultados
            if item.get("salvo")
        ),
        "total_duplicados": sum(
            1
            for item in resultados
            if item.get("duplicado")
        ),
    }


def resolver_alerta_llm(
    alerta_id: int,
    *,
    resolvido_por: str = "dashboard",
) -> dict[str, Any]:
    """
    Marca um alerta aberto como resolvido.
    """
    inicializacao = (
        inicializar_tabela_llm_alerts()
    )

    if not inicializacao.get("ok"):
        return inicializacao

    try:
        from sqlalchemy import text

        engine = _criar_engine()

        comando = text(f"""
            UPDATE {NOME_TABELA}
            SET
                status = 'resolvido',
                resolvido_em = NOW(),
                resolvido_por = :resolvido_por,
                atualizado_em = NOW()
            WHERE id = :alerta_id
              AND status = 'aberto'
            RETURNING id, resolvido_em;
        """)

        with engine.begin() as connection:
            registro = connection.execute(
                comando,
                {
                    "alerta_id": int(
                        alerta_id
                    ),
                    "resolvido_por": str(
                        resolvido_por
                        or "dashboard"
                    )[:255],
                },
            ).mappings().first()

        engine.dispose()

        if not registro:
            return {
                "ok": True,
                "resolvido": False,
                "message": (
                    "O alerta não existe ou já foi resolvido."
                ),
            }

        return {
            "ok": True,
            "resolvido": True,
            "id": int(
                registro["id"]
            ),
            "resolvido_em": registro[
                "resolvido_em"
            ],
            "message": (
                "Alerta resolvido com sucesso."
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "resolvido": False,
            "message": (
                "Erro ao resolver alerta: "
                f"{exc}"
            ),
        }


def carregar_alertas_llm(
    *,
    limite: int = 500,
    status: str | None = None,
) -> dict[str, Any]:
    """
    Consulta alertas persistidos.
    """
    inicializacao = (
        inicializar_tabela_llm_alerts()
    )

    if not inicializacao.get("ok"):
        return {
            **inicializacao,
            "df": pd.DataFrame(),
        }

    try:
        from sqlalchemy import text

        engine = _criar_engine()

        filtro = ""
        parametros: dict[str, Any] = {
            "limite": max(
                int(limite),
                1,
            ),
        }

        if status:
            filtro = "WHERE status = :status"
            parametros["status"] = status

        consulta = text(f"""
            SELECT *
            FROM {NOME_TABELA}
            {filtro}
            ORDER BY
                CASE severidade
                    WHEN 'critica' THEN 5
                    WHEN 'alta' THEN 4
                    WHEN 'media' THEN 3
                    WHEN 'baixa' THEN 2
                    ELSE 1
                END DESC,
                criado_em DESC
            LIMIT :limite;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(
                consulta,
                connection,
                params=parametros,
            )

        engine.dispose()

        return {
            "ok": True,
            "df": df,
            "total": len(df),
            "message": "Alertas carregados.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "df": pd.DataFrame(),
            "total": 0,
            "message": (
                "Erro ao carregar alertas: "
                f"{exc}"
            ),
        }


__all__ = [
    "resolver_alerta_llm",
    "NOME_TABELA",
    "ORDEM_SEVERIDADE",
    "inicializar_tabela_llm_alerts",
    "detectar_alertas_llm",
    "persistir_alerta_llm",
    "avaliar_e_persistir_alertas",
    "carregar_alertas_llm",
]
