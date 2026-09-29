from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .education_service import get_education_summary
from .security_service import get_security_summary


def _utc_now() -> str:

    return (
        datetime
        .now(timezone.utc)
        .isoformat()
    )


def _health_average(
    modules: list[dict[str, Any]]
) -> int:

    values = [

        int(module["health"])

        for module in modules

        if (
            module.get("active")
            and
            isinstance(
                module.get("health"),
                (int, float),
            )
        )

    ]

    if not values:
        return 0

    return round(
        sum(values)
        /
        len(values)
    )


def _sum_metric(
    modules: list[dict[str, Any]],
    field: str,
) -> int:

    return sum(

        int(
            module.get(
                field,
                0,
            )
            or
            0
        )

        for module in modules

        if module.get("active")

    )


def build_finance_dashboard() -> dict[str, Any]:
    """
    Consolida apenas summaries dos módulos.

    A Plataforma Financeira não precisa acessar
    detalhes internos completos de cada dashboard.
    """

    education = (
        get_education_summary()
    )

    security = (
        get_security_summary()
    )

    connected_modules = [

        education,

        security,

    ]

    active_modules = [

        module

        for module
        in connected_modules

        if module.get("active")

    ]

    # Como ainda não temos identificação compartilhada
    # de usuários entre os módulos, NÃO somamos usuários.
    # Nesta fase utilizamos o maior conjunto ativo como
    # estimativa conservadora, evitando dupla contagem.

    users_estimate = max(
        (
            int(
                module.get(
                    "active_users",
                    0,
                )
                or
                0
            )

            for module
            in active_modules
        ),
        default=0,
    )

    summary = {

        "health":
            _health_average(
                active_modules
            ),

        "active_modules":
            len(active_modules),

        "connected_modules":
            len(connected_modules),

        "users":
            users_estimate,

        "alerts":
            _sum_metric(
                active_modules,
                "alerts",
            ),

        "hitl":
            _sum_metric(
                active_modules,
                "hitl",
            ),

        "rag_queries":
            _sum_metric(
                active_modules,
                "rag_queries",
            ),

        "critical_items":
            _sum_metric(
                active_modules,
                "critical_items",
            ),

        "data_quality":
            98,

    }

    priorities = [

        {

            "module":
                "financial_security",

            "severity":
                "critical",

            "count":
                security[
                    "critical_items"
                ],

            "title":
                "Alertas críticos de Segurança Financeira",

        },

        {

            "module":
                "financial_security",

            "severity":
                "high",

            "count":
                security[
                    "hitl"
                ],

            "title":
                "Casos HITL de Segurança Financeira",

        },

        {

            "module":
                "education_finance",

            "severity":
                "medium",

            "count":
                education[
                    "critical_items"
                ],

            "title":
                "Usuários de Educação Financeira com risco elevado",

        },

    ]

    return {

        "platform":
            "finance",

        "name":
            "Plataforma Financeira",

        "manager":
            "Gerente Financeiro",

        "demo":
            any(
                bool(
                    module.get(
                        "demo"
                    )
                )
                for module
                in connected_modules
            ),

        "source":
            "module-summaries",

        "summary":
            summary,

        "modules":
            connected_modules,

        "priorities":
            priorities,

        "aggregation": {

            "health":
                "average_active_modules",

            "alerts":
                "sum",

            "hitl":
                "sum",

            "rag_queries":
                "sum",

            "users":
                "max_active_users_until_identity_dedup",

        },

        "updated_at":
            _utc_now(),

    }


def get_finance_summary() -> dict[str, Any]:
    """
    Resumo da Plataforma Financeira
    preparado para a INNA Central.
    """

    dashboard = (
        build_finance_dashboard()
    )

    return {

        "platform":
            dashboard["platform"],

        "name":
            dashboard["name"],

        "manager":
            dashboard["manager"],

        "status":
            "active",

        "health":
            dashboard[
                "summary"
            ][
                "health"
            ],

        "active_modules":
            dashboard[
                "summary"
            ][
                "active_modules"
            ],

        "alerts":
            dashboard[
                "summary"
            ][
                "alerts"
            ],

        "hitl":
            dashboard[
                "summary"
            ][
                "hitl"
            ],

        "critical_items":
            dashboard[
                "summary"
            ][
                "critical_items"
            ],

        "route":
            "/plataforma/financeiro",

        "demo":
            dashboard["demo"],

        "source":
            dashboard["source"],

        "updated_at":
            dashboard[
                "updated_at"
            ],

    }
