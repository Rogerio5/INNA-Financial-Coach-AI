"""
Repositório PostgreSQL da memória persistente da INNA.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Optional

try:
    from database.connection import cursor_postgres
except ImportError:
    from src.database.connection import cursor_postgres


def _normalizar_memoria_json(valor: Any) -> dict:
    if valor is None:
        return {}

    if isinstance(valor, dict):
        return valor

    if isinstance(valor, str):
        try:
            resultado = json.loads(valor)
            return resultado if isinstance(resultado, dict) else {}
        except Exception:
            return {}

    return {}


def _normalizar_tags(valor: Any) -> list[str]:
    if valor is None:
        return []

    if isinstance(valor, list):
        return [str(item).strip() for item in valor if str(item).strip()]

    if isinstance(valor, tuple):
        return [str(item).strip() for item in valor if str(item).strip()]

    if isinstance(valor, str):
        return [item.strip() for item in valor.split(",") if item.strip()]

    return []


def _converter_registro(registro: Any) -> Optional[dict]:
    if not registro:
        return None

    memoria = dict(registro)

    memoria["memoria_json"] = _normalizar_memoria_json(memoria.get("memoria_json"))

    memoria["tags"] = _normalizar_tags(memoria.get("tags"))

    for campo in (
        "renda_mensal",
        "gastos_mensais",
        "valor_reserva",
        "ultimo_score",
        "nivel_confianca",
    ):
        valor = memoria.get(campo)

        if isinstance(valor, Decimal):
            memoria[campo] = float(valor)

    return memoria


def buscar_memoria_usuario(
    usuario_id: str,
    *,
    somente_ativa: bool = True,
) -> dict:
    usuario_id = str(usuario_id or "").strip()

    if not usuario_id:
        return {
            "ok": False,
            "message": "usuario_id não informado.",
            "memoria": None,
        }

    filtro_ativo = "AND COALESCE(ativo, TRUE) = TRUE" if somente_ativa else ""

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute(
                f"""
                SELECT *
                FROM memoria_usuarios_inna
                WHERE usuario_id = %s
                {filtro_ativo}
                ORDER BY atualizado_em DESC NULLS LAST, id DESC
                LIMIT 1;
                """,
                (usuario_id,),
            )

            registro = cursor.fetchone()

        memoria = _converter_registro(registro)

        return {
            "ok": True,
            "message": (
                "Memória encontrada." if memoria else "Nenhuma memória encontrada."
            ),
            "memoria": memoria,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": f"Erro ao buscar memória: {exc}",
            "memoria": None,
        }


def salvar_ou_atualizar_memoria_usuario(
    usuario_id: str,
    dados_memoria: dict,
    *,
    origem: str = "sistema",
) -> dict:
    usuario_id = str(usuario_id or "").strip()

    if not usuario_id:
        return {
            "ok": False,
            "message": "usuario_id não informado.",
        }

    dados_memoria = dados_memoria or {}

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                """
                SELECT *
                FROM memoria_usuarios_inna
                WHERE usuario_id = %s
                ORDER BY atualizado_em DESC NULLS LAST, id DESC
                LIMIT 1;
                """,
                (usuario_id,),
            )

            antes = _converter_registro(cursor.fetchone())

            memoria_json = _normalizar_memoria_json(dados_memoria.get("memoria_json"))

            tags = _normalizar_tags(dados_memoria.get("tags"))

            parametros = {
                "usuario_id": usuario_id,
                "nome": dados_memoria.get("nome"),
                "idioma": dados_memoria.get("idioma") or "pt",
                "moeda": dados_memoria.get("moeda") or "BRL",
                "renda_mensal": dados_memoria.get("renda_mensal"),
                "gastos_mensais": dados_memoria.get("gastos_mensais"),
                "valor_reserva": dados_memoria.get("valor_reserva"),
                "possui_dividas": dados_memoria.get("possui_dividas"),
                "uso_cartao_credito": dados_memoria.get("uso_cartao_credito"),
                "ultimo_score": dados_memoria.get("ultimo_score"),
                "ultimo_risco": dados_memoria.get("ultimo_risco"),
                "ultima_meta": dados_memoria.get("ultima_meta"),
                "resumo_contexto": dados_memoria.get("resumo_contexto"),
                "perfil_financeiro": dados_memoria.get("perfil_financeiro"),
                "objetivo_principal": dados_memoria.get("objetivo_principal"),
                "preferencia_linguagem": (
                    dados_memoria.get("preferencia_linguagem") or "simples"
                ),
                "canal_origem": origem,
                "nivel_confianca": (
                    dados_memoria.get("nivel_confianca")
                    if dados_memoria.get("nivel_confianca") is not None
                    else 1.0
                ),
                "memoria_json": json.dumps(
                    memoria_json,
                    ensure_ascii=False,
                    default=str,
                ),
                "tags": tags,
            }

            cursor.execute(
                """
                INSERT INTO memoria_usuarios_inna (
                    usuario_id,
                    nome,
                    idioma,
                    moeda,
                    renda_mensal,
                    gastos_mensais,
                    valor_reserva,
                    possui_dividas,
                    uso_cartao_credito,
                    ultimo_score,
                    ultimo_risco,
                    ultima_meta,
                    resumo_contexto,
                    perfil_financeiro,
                    objetivo_principal,
                    preferencia_linguagem,
                    canal_origem,
                    nivel_confianca,
                    memoria_json,
                    tags,
                    ativo,
                    atualizado_em
                )
                VALUES (
                    %(usuario_id)s,
                    %(nome)s,
                    %(idioma)s,
                    %(moeda)s,
                    %(renda_mensal)s,
                    %(gastos_mensais)s,
                    %(valor_reserva)s,
                    %(possui_dividas)s,
                    %(uso_cartao_credito)s,
                    %(ultimo_score)s,
                    %(ultimo_risco)s,
                    %(ultima_meta)s,
                    %(resumo_contexto)s,
                    %(perfil_financeiro)s,
                    %(objetivo_principal)s,
                    %(preferencia_linguagem)s,
                    %(canal_origem)s,
                    %(nivel_confianca)s,
                    %(memoria_json)s::jsonb,
                    %(tags)s,
                    TRUE,
                    NOW()
                )
                ON CONFLICT (usuario_id)
                DO UPDATE SET
                    nome = EXCLUDED.nome,
                    idioma = EXCLUDED.idioma,
                    moeda = EXCLUDED.moeda,
                    renda_mensal = EXCLUDED.renda_mensal,
                    gastos_mensais = EXCLUDED.gastos_mensais,
                    valor_reserva = EXCLUDED.valor_reserva,
                    possui_dividas = EXCLUDED.possui_dividas,
                    uso_cartao_credito = EXCLUDED.uso_cartao_credito,
                    ultimo_score = EXCLUDED.ultimo_score,
                    ultimo_risco = EXCLUDED.ultimo_risco,
                    ultima_meta = EXCLUDED.ultima_meta,
                    resumo_contexto = EXCLUDED.resumo_contexto,
                    perfil_financeiro = EXCLUDED.perfil_financeiro,
                    objetivo_principal = EXCLUDED.objetivo_principal,
                    preferencia_linguagem = EXCLUDED.preferencia_linguagem,
                    canal_origem = EXCLUDED.canal_origem,
                    nivel_confianca = EXCLUDED.nivel_confianca,
                    memoria_json = EXCLUDED.memoria_json,
                    tags = EXCLUDED.tags,
                    ativo = TRUE,
                    atualizado_em = NOW()
                RETURNING *;
                """,
                parametros,
            )

            depois = _converter_registro(cursor.fetchone())

            tipo_evento = "memoria_criada" if antes is None else "memoria_atualizada"

            cursor.execute(
                """
                INSERT INTO memoria_eventos_inna (
                    usuario_id,
                    tipo_evento,
                    origem,
                    dados_antes,
                    dados_depois,
                    resumo_evento
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s::jsonb,
                    %s::jsonb,
                    %s
                );
                """,
                (
                    usuario_id,
                    tipo_evento,
                    origem,
                    (
                        json.dumps(
                            antes,
                            ensure_ascii=False,
                            default=str,
                        )
                        if antes
                        else None
                    ),
                    json.dumps(
                        depois,
                        ensure_ascii=False,
                        default=str,
                    ),
                    (
                        dados_memoria.get("resumo_contexto")
                        or "Memória salva ou atualizada."
                    ),
                ),
            )

        return {
            "ok": True,
            "message": (
                f"Memória do usuário {usuario_id} salva/atualizada com sucesso."
            ),
            "tipo_evento": tipo_evento,
            "memoria": depois,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": f"Erro ao salvar memória: {exc}",
        }
