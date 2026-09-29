from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


_EDUCATION_STATE: dict[str, Any] = {

    "module": "education_finance",

    "code": "EF",

    "name": "Educação Financeira",

    "status": "active",

    "active": True,

    "health": 96,

    "active_users": 84,

    "diagnostics": 342,

    "alerts": 18,

    "hitl": 3,

    "rag_queries": 10240,

    "financial_goals": 126,

    "high_risk_users": 3,

    "stale_goals": 8,

    "route":
        "/plataforma/financeiro/modulos/educacao-financeira",

    "source": "local-demo",

    "demo": True,

}


def _utc_now() -> str:

    return (
        datetime
        .now(timezone.utc)
        .isoformat()
    )


def get_education_dashboard() -> dict[str, Any]:
    """
    Dados detalhados utilizados pelo dashboard
    do módulo Educação Financeira.

    Nesta versão, a origem ainda é local/demonstrativa.
    Depois este serviço poderá consultar PostgreSQL,
    eventos, RAG e observabilidade.
    """

    data = deepcopy(
        _EDUCATION_STATE
    )

    data["updated_at"] = _utc_now()

    data["risk"] = {

        "high": 3,

        "medium": 11,

        "low": 70,

    }

    data["recommendations"] = [

        {
            "priority": "high",
            "title":
                "Revisar usuários com risco elevado",
        },

        {
            "priority": "medium",
            "title":
                "Revisar metas financeiras em atraso",
        },

        {
            "priority": "medium",
            "title":
                "Acompanhar diagnósticos pendentes",
        },

    ]

    return data


def get_education_summary() -> dict[str, Any]:
    """
    Contrato resumido enviado à Plataforma Financeira.
    Não envia todos os detalhes do módulo.
    """

    data = get_education_dashboard()

    return {

        "module":
            data["module"],

        "code":
            data["code"],

        "name":
            data["name"],

        "status":
            data["status"],

        "active":
            data["active"],

        "health":
            data["health"],

        "active_users":
            data["active_users"],

        "alerts":
            data["alerts"],

        "hitl":
            data["hitl"],

        "rag_queries":
            data["rag_queries"],

        "critical_items":
            data["high_risk_users"],

        "route":
            data["route"],

        "source":
            data["source"],

        "demo":
            data["demo"],

        "updated_at":
            data["updated_at"],

    }
