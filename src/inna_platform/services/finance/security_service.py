from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


_SECURITY_STATE: dict[str, Any] = {

    "module": "financial_security",

    "code": "SF",

    "name": "Segurança Financeira",

    "status": "attention",

    "active": True,

    "health": 93,

    "active_users": 2170,

    "security_events": 12840,

    "alerts": 27,

    "critical_alerts": 3,

    "hitl": 4,

    "rag_queries": 8180,

    "rules": 24,

    "coverage": 98,

    "route":
        "/plataforma/financeiro/modulos/seguranca-financeira",

    "source": "local-demo",

    "demo": True,

}


def _utc_now() -> str:

    return (
        datetime
        .now(timezone.utc)
        .isoformat()
    )


def get_security_dashboard() -> dict[str, Any]:
    """
    Dados detalhados utilizados pelo dashboard
    do módulo Segurança Financeira.
    """

    data = deepcopy(
        _SECURITY_STATE
    )

    data["updated_at"] = _utc_now()

    data["operational"] = {

        "detection_latency_ms": 820,

        "coverage": data["coverage"],

        "rules": data["rules"],

    }

    data["recommendations"] = [

        {
            "priority": "critical",
            "title":
                "Revisar alertas críticos",
        },

        {
            "priority": "high",
            "title":
                "Processar casos aguardando HITL",
        },

        {
            "priority": "medium",
            "title":
                "Validar regras de monitoramento",
        },

    ]

    return data


def get_security_summary() -> dict[str, Any]:
    """
    Contrato resumido enviado à Plataforma Financeira.
    """

    data = get_security_dashboard()

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
            data["critical_alerts"],

        "route":
            data["route"],

        "source":
            data["source"],

        "demo":
            data["demo"],

        "updated_at":
            data["updated_at"],

    }
