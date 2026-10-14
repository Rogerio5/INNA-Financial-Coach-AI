from fastapi.responses import FileResponse
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="INNA Official Platform",
    version="1.0.0",
)

from src.inna_platform.services.finance.mfa import account_page_gate
app.middleware("http")(account_page_gate)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@app.get("/")
async def home(request: Request):
    from pathlib import Path
    from fastapi.responses import FileResponse

    gateway_path = (
        Path(__file__).resolve().parent
        / "static"
        / "sabino-login-gateway.html"
    )

    return FileResponse(
        str(gateway_path),
        media_type="text/html",
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "inna-official-platform",
    }


@app.get("/modulos")
async def modules_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="modulos.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


@app.get("/configurar")
async def configure_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="configurar.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


@app.get("/modulos/educacao-financeira")
async def financial_education_module(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="educacao-financeira.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


@app.get("/proposta")
async def proposal_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="proposta.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


@app.get("/jornada")
async def journey_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="jornada.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


@app.get("/plataforma")
async def active_platform_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="plataforma.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


@app.get("/contrato")
async def contract_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contrato.html",
        context={
            "platform_name": "Sabino.AI",
            "assistant_name": "INNA",
        },
    )


# ==========================================================
# EDUCATION_FINANCE_DASHBOARD_V2
# ==========================================================

@app.get(
    "/plataforma/modulos/educacao-financeira",
    include_in_schema=False,
)
async def education_finance_dashboard_v2():

    from pathlib import Path
    from fastapi.responses import FileResponse

    file_path = (
        Path(__file__).resolve().parent
        / "templates"
        / "educacao_financeira_dashboard.html"
    )

    return FileResponse(
        file_path
    )



# ==========================================================
# SECURITY_FINANCE_DASHBOARD_V1
# ==========================================================

@app.get(
    "/plataforma/modulos/seguranca-financeira",
    include_in_schema=False,
)
async def security_finance_dashboard_v1():

    from pathlib import Path
    from fastapi.responses import FileResponse

    file_path = (
        Path(__file__).resolve().parent
        / "templates"
        / "seguranca_financeira_dashboard.html"
    )

    return FileResponse(
        file_path
    )




# ==========================================================
# SABINO.AI - FINANCIAL PLATFORM ROUTES
# ==========================================================

from fastapi import Request as SabinoFinancialRequest


@app.get("/plataforma/financeiro")
async def sabino_financial_platform(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="financeiro_dashboard.html",
        context={}
    )

@app.get(
    "/plataforma/financeiro/modulos/educacao-financeira"
)
async def sabino_financial_education(
    request: SabinoFinancialRequest
):
    return templates.TemplateResponse(
        "educacao_financeira_dashboard.html",
        {
            "request": request
        }
    )


@app.get(
    "/plataforma/financeiro/modulos/seguranca-financeira"
)
async def sabino_financial_security(
    request: SabinoFinancialRequest
):
    return templates.TemplateResponse(
        "seguranca_financeira_dashboard.html",
        {
            "request": request
        }
    )


# ==========================================================
# FIM - FINANCIAL PLATFORM ROUTES
# ==========================================================



# ==========================================================
# SABINO.AI - FINANCIAL PLATFORM DASHBOARD API
# Dados demonstrativos.
# Substituir posteriormente por agregacao real dos modulos.
# ==========================================================

@app.get("/api/platform/finance/dashboard-legacy", include_in_schema=False)
async def sabino_finance_dashboard_api():

    return {

        "demo": True,

        "summary": {
            "health": 96,
            "users": 2840,
            "active_modules": 2,
            "alerts": 34,
            "hitl": 7,
            "rag_queries": 18420,
            "data_quality": 98
        },

        "modules": [

            {
                "code": "EF",
                "name": "Educação Financeira",
                "description": "Diagnóstico, metas e orientação financeira.",
                "active": True,
                "status_label": "● Ativo",
                "health": 98,
                "users": 2840,
                "alerts": 7,
                "hitl": 3,
                "rag_queries": 10240,
                "route": "/plataforma/financeiro/modulos/educacao-financeira"
            },

            {
                "code": "SF",
                "name": "Segurança Financeira",
                "description": "Detecção, risco, investigação e proteção.",
                "active": True,
                "status_label": "Atenção",
                "health": 92,
                "users": 2170,
                "alerts": 27,
                "hitl": 4,
                "rag_queries": 8180,
                "route": "/plataforma/financeiro/modulos/seguranca-financeira"
            },

            {
                "code": "RI",
                "name": "Reembolso Inteligente",
                "description": "Automação e análise inteligente de reembolsos.",
                "active": False,
                "status_label": "Preparação",
                "health": None,
                "users": 0,
                "alerts": None,
                "hitl": None,
                "rag_queries": 0,
                "route": None
            },

            {
                "code": "PF",
                "name": "Planejamento Financeiro",
                "description": "Orçamento, metas e projeções financeiras.",
                "active": False,
                "status_label": "Planejado",
                "health": None,
                "users": 0,
                "alerts": None,
                "hitl": None,
                "rag_queries": 0,
                "route": None
            }

        ],

        "priorities": [

            {
                "title": "3 alertas críticos",
                "source": "Segurança Financeira"
            },

            {
                "title": "4 casos aguardando HITL",
                "source": "Segurança Financeira"
            },

            {
                "title": "3 diagnósticos para revisão",
                "source": "Educação Financeira"
            }

        ],

        "operational": {

            "average_latency": "1,2s",
            "error_rate": "0,7%",
            "availability": "99,4%",
            "audit_coverage": "100%",

            "services": [

                {
                    "name": "Educação Financeira",
                    "status": "Saudável",
                    "latency": "840ms",
                    "error_rate": "0,3%"
                },

                {
                    "name": "Segurança Financeira",
                    "status": "Atenção",
                    "latency": "1,4s",
                    "error_rate": "1,1%"
                },

                {
                    "name": "RAG Financeiro",
                    "status": "Saudável",
                    "latency": "920ms",
                    "error_rate": "0,4%"
                },

                {
                    "name": "Auditoria",
                    "status": "Saudável",
                    "latency": "180ms",
                    "error_rate": "0,0%"
                },

                {
                    "name": "HITL",
                    "status": "Saudável",
                    "latency": "310ms",
                    "error_rate": "0,0%"
                }

            ]

        },

        "analytics": {

            "monthly_health": [
                {"label": "Mar", "value": 72},
                {"label": "Abr", "value": 78},
                {"label": "Mai", "value": 83},
                {"label": "Jun", "value": 88},
                {"label": "Jul", "value": 92},
                {"label": "Ago", "value": 96}
            ],

            "inna_usage": [
                {"label": "Seg", "value": 58},
                {"label": "Ter", "value": 71},
                {"label": "Qua", "value": 67},
                {"label": "Qui", "value": 82},
                {"label": "Sex", "value": 91},
                {"label": "Sáb", "value": 54},
                {"label": "Dom", "value": 43}
            ]

        },

        "intelligence": {

            "confidence": 88,

            "diagnostic":
                "Segurança Financeira concentra a maior quantidade de alertas e os incidentes de maior criticidade do domínio.",

            "predictive":
                "Mantido o comportamento atual, a fila de revisão humana tende a crescer antes da normalização dos alertas.",

            "prescriptive":
                "Priorizar os três incidentes críticos, revisar os quatro casos HITL de segurança e depois os diagnósticos pendentes de Educação Financeira.",

            "evidence": [

                {
                    "source": "Segurança Financeira",
                    "evidence": "3 alertas críticos ativos",
                    "impact": "Alto",
                    "confidence": 94
                },

                {
                    "source": "Segurança Financeira",
                    "evidence": "4 casos aguardando HITL",
                    "impact": "Médio",
                    "confidence": 91
                },

                {
                    "source": "Educação Financeira",
                    "evidence": "3 diagnósticos aguardando revisão",
                    "impact": "Médio",
                    "confidence": 86
                },

                {
                    "source": "RAG Financeiro",
                    "evidence": "18.420 consultas consolidadas",
                    "impact": "Contexto",
                    "confidence": 89
                }

            ]

        }

    }


# ==========================================================
# FIM FINANCIAL PLATFORM DASHBOARD API
# ==========================================================





# ==========================================================
# SABINO_FINANCE_CONNECTED_SUMMARY_V1
# MODULOS -> PLATAFORMA FINANCEIRA -> INNA CENTRAL
# ==========================================================

from src.inna_platform.services.finance.education_service import (
    get_education_dashboard,
    get_education_summary,
)

from src.inna_platform.services.finance.security_service import (
    get_security_dashboard,
    get_security_summary,
)

from src.inna_platform.services.finance.finance_aggregator import (
    build_finance_dashboard,
    get_finance_summary,
)


@app.get("/api/finance/education/dashboard")
async def sabino_finance_education_dashboard_api():

    return get_education_dashboard()


@app.get("/api/finance/education/summary")
async def sabino_finance_education_summary_api():

    return get_education_summary()


@app.get("/api/finance/security/dashboard")
async def sabino_finance_security_dashboard_api():

    return get_security_dashboard()


@app.get("/api/finance/security/summary")
async def sabino_finance_security_summary_api():

    return get_security_summary()


@app.get("/api/platform/finance/dashboard")
async def sabino_connected_finance_dashboard_api():

    return build_finance_dashboard()


@app.get("/api/platform/finance/summary")
async def sabino_connected_finance_summary_api():

    return get_finance_summary()


# ==========================================================
# FIM SABINO_FINANCE_CONNECTED_SUMMARY_V1
# ==========================================================
# ============================================================

@app.get(
    "/dashboard",
    include_in_schema=False,
)
async def sabino_dashboard():
    return FileResponse(
        str(
            Path(__file__)
            .resolve()
            .parent
            / "static"
            / "sabino-dashboard.html"
        )
    )
from fastapi.responses import HTMLResponse


# ============================================================
# SABINO_DASHBOARD_ROUTE_V2
# ============================================================

import os as _sabino_os


@app.get(
    "/dashboard",
    include_in_schema=False,
)
async def sabino_dashboard_v2():

    dashboard_file = _sabino_os.path.join(
        _sabino_os.path.dirname(__file__),
        "static",
        "sabino-dashboard.html",
    )

    if not _sabino_os.path.isfile(
        dashboard_file
    ):
        return HTMLResponse(
            content=(
                "<h1>Dashboard não encontrado</h1>"
                f"<p>{dashboard_file}</p>"
            ),
            status_code=404,
        )

    return FileResponse(
        dashboard_file,
        media_type="text/html",
    )


# SABINO_DASHBOARD_FINAL_V3_BEGIN

# Remove qualquer rota /dashboard criada anteriormente.
app.router.routes[:] = [
    route
    for route in app.router.routes
    if getattr(route, "path", None) != "/dashboard"
]


@app.get(
    "/dashboard",
    include_in_schema=False,
)
async def sabino_dashboard_final():

    import os
    from fastapi.responses import FileResponse as SabinoFileResponse

    dashboard_file = os.path.join(
        os.path.dirname(__file__),
        "static",
        "sabino-dashboard.html",
    )

    return SabinoFileResponse(
        dashboard_file,
        media_type="text/html",
    )


# SABINO_DASHBOARD_FINAL_V3_END


# SABINO_MODULOS_FINAL_V2_BEGIN

# Mantém somente a rota final /modulos.
app.router.routes[:] = [
    route
    for route in app.router.routes
    if getattr(route, "path", None) != "/modulos"
]


@app.get(
    "/modulos",
    include_in_schema=False,
)
async def sabino_modulos_final():

    import os
    from fastapi.responses import FileResponse as SabinoFileResponse

    page_file = os.path.join(
        os.path.dirname(__file__),
        "static",
        "sabino-modulos.html",
    )

    return SabinoFileResponse(
        page_file,
        media_type="text/html",
    )


# SABINO_MODULOS_FINAL_V2_END


# ============================================================
# SABINO_GLOBAL_I18N_API_V2

from fastapi import Request as _SabinoI18nRequest


_SABINO_I18N_CACHE_V2: dict[
    str,
    dict[str, str],
] = {}


@app.post(
    "/api/i18n/translate",
    include_in_schema=False,
)
async def sabino_global_i18n_translate(
    request: _SabinoI18nRequest,
):
    """
    Tradução global da interface Sabino.AI.

    Proteções:
    - Sabino.AI nunca é traduzido
    - INNA nunca é traduzido
    - CPF nunca é traduzido
    - API key permanece no servidor
    - payload limitado
    - resposta validada
    """

    import hashlib
    import json
    import os
    import re

    from fastapi import HTTPException


    try:
        payload = await request.json()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON.",
        )


    locale = str(
        payload.get("locale")
        or ""
    ).strip()


    texts = payload.get(
        "texts"
    )


    if not re.fullmatch(
        r"[A-Za-z]{2,3}"
        r"(?:[-_][A-Za-z0-9]{2,8})*",
        locale,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid locale.",
        )


    if not isinstance(
        texts,
        dict,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "texts must be an object."
            ),
        )


    if len(texts) > 150:
        raise HTTPException(
            status_code=413,
            detail=(
                "Too many translation keys."
            ),
        )


    clean_texts: dict[
        str,
        str,
    ] = {}


    total_chars = 0


    for key, value in texts.items():

        if not isinstance(
            key,
            str,
        ):
            continue

        if not isinstance(
            value,
            str,
        ):
            continue

        if len(key) > 120:
            continue

        if len(value) > 3000:
            continue


        total_chars += len(
            value
        )


        clean_texts[key] = (
            value
        )


    if total_chars > 30000:
        raise HTTPException(
            status_code=413,
            detail=(
                "Translation payload too large."
            ),
        )


    normalized_locale = (
        locale.replace(
            "_",
            "-",
        )
    )


    if (
        normalized_locale.lower()
        in {
            "pt",
            "pt-br",
        }
    ):
        return {
            "locale":
                normalized_locale,

            "translations":
                clean_texts,

            "source":
                "native",

            "protected":
                [
                    "Sabino.AI",
                    "INNA",
                    "CPF",
                ],
        }


    # ========================================================
    # PROTEÇÃO DE TOKENS
    # ========================================================

    protected_tokens = {
        "__SABINO_AI_BRAND__":
            "Sabino.AI",

        "__INNA_BRAND__":
            "INNA",

        "__CPF_TOKEN__":
            "CPF",
    }


    def protect_value(
        value: str,
    ) -> str:

        protected = str(
            value
        )


        protected = re.sub(
            r"Sabino\.AI",
            "__SABINO_AI_BRAND__",
            protected,
            flags=re.IGNORECASE,
        )


        protected = re.sub(
            r"\bINNA\b",
            "__INNA_BRAND__",
            protected,
            flags=re.IGNORECASE,
        )


        protected = re.sub(
            r"\bCPF\b",
            "__CPF_TOKEN__",
            protected,
            flags=re.IGNORECASE,
        )


        return protected


    def restore_value(
        value: str,
    ) -> str:

        restored = str(
            value
        )


        for (
            placeholder,
            original,
        ) in protected_tokens.items():

            restored = restored.replace(
                placeholder,
                original,
            )


        return restored


    protected_texts = {
        key:
            protect_value(
                value
            )

        for (
            key,
            value,
        ) in clean_texts.items()
    }


    # ========================================================
    # CACHE
    # ========================================================

    cache_payload = json.dumps(
        clean_texts,
        ensure_ascii=False,
        sort_keys=True,
    )


    cache_key = (
        normalized_locale.lower()
        +
        ":"
        +
        hashlib.sha256(
            cache_payload.encode(
                "utf-8"
            )
        ).hexdigest()
    )


    cached = (
        _SABINO_I18N_CACHE_V2.get(
            cache_key
        )
    )


    if cached is not None:

        return {
            "locale":
                normalized_locale,

            "translations":
                cached,

            "source":
                "cache",

            "protected":
                [
                    "Sabino.AI",
                    "INNA",
                    "CPF",
                ],
        }


    # ========================================================
    # GEMINI
    # ========================================================

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )


    if not api_key:

        raise HTTPException(
            status_code=503,
            detail=(
                "GEMINI_API_KEY "
                "is not configured."
            ),
        )


    model = (
        os.getenv(
            "SABINO_I18N_GEMINI_MODEL"
        )
        or
        os.getenv(
            "GEMINI_MODEL"
        )
        or
        "gemini-2.5-flash"
    )


    prompt = f"""
You are the localization engine for Sabino.AI.

Translate every VALUE of the JSON object below
from Brazilian Portuguese into locale:

{normalized_locale}

STRICT RULES:

1. Return ONLY one valid JSON object.
2. Keep every JSON key EXACTLY unchanged.
3. Translate only JSON values.
4. NEVER modify these placeholders:
   __SABINO_AI_BRAND__
   __INNA_BRAND__
   __CPF_TOKEN__
5. Preserve HTML tags:
   <span>
   <br>
   <strong>
   <b>
   <em>
6. Preserve numbers, symbols, variables and URLs.
7. Do not translate technical identifiers.
8. Use natural professional language suitable
   for a modern SaaS/AI platform.
9. Do not add explanations.
10. Do not add Markdown fences.

JSON:

{json.dumps(
    protected_texts,
    ensure_ascii=False,
)}
"""


    try:

        from google import genai


        client = genai.Client(
            api_key=api_key
        )


        response = (
            client.models
            .generate_content(
                model=model,
                contents=prompt,
            )
        )


        raw = str(
            getattr(
                response,
                "text",
                "",
            )
            or
            ""
        ).strip()


    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=(
                "Translation provider unavailable: "
                +
                type(exc).__name__
            ),
        )


    # ========================================================
    # LIMPA POSSÍVEL FENCE
    # ========================================================

    if raw.startswith(
        "```"
    ):

        raw = re.sub(
            r"^```(?:json)?\s*",
            "",
            raw,
            flags=re.IGNORECASE,
        )


        raw = re.sub(
            r"\s*```$",
            "",
            raw,
        )


    # ========================================================
    # JSON
    # ========================================================

    try:

        translated = (
            json.loads(
                raw
            )
        )

    except Exception:

        raise HTTPException(
            status_code=502,
            detail=(
                "Invalid translation response."
            ),
        )


    if not isinstance(
        translated,
        dict,
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Invalid translation object."
            ),
        )


    final: dict[
        str,
        str,
    ] = {}


    for (
        key,
        original,
    ) in clean_texts.items():

        translated_value = (
            translated.get(
                key
            )
        )


        if not isinstance(
            translated_value,
            str,
        ):

            translated_value = (
                protected_texts[
                    key
                ]
            )


        translated_value = (
            restore_value(
                translated_value
            )
        )


        final[key] = (
            translated_value
        )


    # ========================================================
    # GARANTIA EXTRA
    # ========================================================

    for key, value in final.items():

        value = value.replace(
            "__SABINO_AI_BRAND__",
            "Sabino.AI",
        )

        value = value.replace(
            "__INNA_BRAND__",
            "INNA",
        )

        value = value.replace(
            "__CPF_TOKEN__",
            "CPF",
        )

        final[key] = value


    _SABINO_I18N_CACHE_V2[
        cache_key
    ] = final


    return {
        "locale":
            normalized_locale,

        "translations":
            final,

        "source":
            "gemini",

        "protected":
            [
                "Sabino.AI",
                "INNA",
                "CPF",
            ],
    }


# SABINO_GLOBAL_I18N_API_V2_END



# Authenticated, quoted credit execution replaces the former unbilled proxy.
from src.inna_platform.services.finance.paid_analysis_routes import router as paid_inna_router
app.include_router(paid_inna_router)



# ============================================================
# SABINO_INNA_FULL_PAGE_ROUTE_V1
# ============================================================

@app.get(
    "/inna",
    include_in_schema=False,
)
async def sabino_inna_full_page():

    import os

    from fastapi.responses import (
        FileResponse,
        HTMLResponse,
    )

    page_file = os.path.join(
        os.path.dirname(__file__),
        "static",
        "sabino-inna.html",
    )

    if not os.path.isfile(
        page_file
    ):

        return HTMLResponse(
            content=(
                "<h1>INNA não encontrada</h1>"
            ),
            status_code=404,
        )

    return FileResponse(
        page_file,
        media_type="text/html",
    )


# ============================================================
# SABINO_FINANCEIRO_CENTRAL_ROUTE_V1
# ============================================================

@app.get(
    "/financeiro/legacy",
    include_in_schema=False,
)
async def sabino_financeiro_central_v1():

    import os

    from fastapi.responses import (
        FileResponse,
        HTMLResponse,
    )

    page_file = os.path.join(
        os.path.dirname(__file__),
        "static",
        "sabino-financeiro.html",
    )

    if not os.path.isfile(
        page_file
    ):

        return HTMLResponse(
            content=(
                "<h1>Financeiro não encontrado</h1>"
            ),
            status_code=404,
        )

    return FileResponse(
        page_file,
        media_type="text/html",
    )



# ============================================================
# SABINO.AI - FINANCEIRO
# ============================================================

@app.get("/financeiro", include_in_schema=False)
async def sabino_financeiro_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro.html"
    )

    return FileResponse(arquivo)



# ============================================================
# SABINO.AI - PLANOS FINANCEIRO
# ============================================================

@app.get("/financeiro/planos", include_in_schema=False)
async def financeiro_planos_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    page = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-planos.html"
    )

    return FileResponse(page)



# SABINO_FINANCE_CONTRACT_V44_START

@app.get("/financeiro/contratacao", include_in_schema=False)
async def sabino_financeiro_contratacao_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    page = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-contratacao.html"
    )

    return FileResponse(
        path=str(page),
        media_type="text/html"
    )

# SABINO_FINANCE_CONTRACT_V44_END



# SABINO_FINANCE_SIGNUP_V46_START

@app.get("/financeiro/contratacao/cadastro", include_in_schema=False)
async def sabino_financeiro_contratacao_cadastro_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    page = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-cadastro.html"
    )

    return FileResponse(
        path=str(page),
        media_type="text/html"
    )

# SABINO_FINANCE_SIGNUP_V46_END



# SABINO_FINANCE_FINAL_V47_START

@app.get("/financeiro/contratacao/finalizar", include_in_schema=False)
async def sabino_financeiro_contratacao_finalizar_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    page = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-finalizacao.html"
    )

    return FileResponse(
        path=str(page),
        media_type="text/html"
    )

# SABINO_FINANCE_FINAL_V47_END



# SABINO_FINANCE_SUCCESS_V49_START

@app.get("/financeiro/contratacao/concluida", include_in_schema=False)
async def sabino_financeiro_concluida_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    page = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-concluido.html"
    )

    return FileResponse(
        path=str(page),
        media_type="text/html"
    )

# SABINO_FINANCE_SUCCESS_V49_END



# SABINO_TRANSACTION_CLASSIFIER_TC1_START
# ============================================================
# INNA Transaction Classifier TC1
# ============================================================

from pydantic import BaseModel as _TC1BaseModel


class _TC1TransactionRequest(_TC1BaseModel):
    description: str
    transaction_type: str = "Despesa"
    merchant: str = ""
    amount: float | None = None


@app.post(
    "/api/platform/finance/transactions/classify",
    include_in_schema=True,
    tags=["Finance Intelligence"],
)
async def classify_financial_transaction_tc1(
    payload: _TC1TransactionRequest,
):

    from src.inna_platform.services.finance.transaction_classifier import (
        classify_transaction,
    )

    result = classify_transaction(
        description=payload.description,
        transaction_type=payload.transaction_type,
        merchant=payload.merchant,
        amount=payload.amount,
    )

    return {
        "ok": True,
        "classification": result.to_dict(),
    }


@app.get(
    "/api/platform/finance/transactions/classifier/capabilities",
    include_in_schema=True,
    tags=["Finance Intelligence"],
)
async def transaction_classifier_capabilities_tc1():

    from src.inna_platform.services.finance.transaction_classifier import (
        classifier_capabilities,
    )

    return {
        "ok": True,
        "classifier": classifier_capabilities(),
    }


# SABINO_TRANSACTION_CLASSIFIER_TC1_END


# SABINO_TRANSACTION_CLASSIFIER_TC2_START
# ============================================================
# INNA Transaction Classifier TC2
# Gemini Semantic Embeddings
# ============================================================


@app.post(
    "/api/platform/finance/transactions/classify-intelligent",
    include_in_schema=True,
    tags=["Finance Intelligence"],
)
async def classify_financial_transaction_tc2(
    payload: _TC1TransactionRequest,
):

    from src.inna_platform.services.finance.transaction_semantic_classifier import (
        classify_transaction_intelligent,
    )

    result = classify_transaction_intelligent(
        description=payload.description,
        transaction_type=payload.transaction_type,
        merchant=payload.merchant,
        amount=payload.amount,
    )

    return {
        "ok": True,
        "classification": result.to_dict(),
    }


@app.get(
    "/api/platform/finance/transactions/classifier/semantic-capabilities",
    include_in_schema=True,
    tags=["Finance Intelligence"],
)
async def transaction_semantic_capabilities_tc2():

    from src.inna_platform.services.finance.transaction_semantic_classifier import (
        semantic_classifier_capabilities,
    )

    return {
        "ok": True,
        "classifier": (
            semantic_classifier_capabilities()
        ),
    }


# SABINO_TRANSACTION_CLASSIFIER_TC2_END


# SABINO_TRANSACTION_CLASSIFIER_TC3_START
# ============================================================
# INNA Transaction Classifier TC3
# Supervised User Feedback Foundation
# ============================================================

from fastapi import HTTPException as _TC3HTTPException


class _TC3FeedbackRequest(
    _TC1BaseModel
):
    description: str
    final_category: str
    transaction_type: str = "Despesa"
    merchant: str = ""
    amount: float | None = None


@app.post(
    "/api/platform/finance/transactions/classification-feedback",
    include_in_schema=True,
    tags=["Finance Intelligence"],
)
async def transaction_classification_feedback_tc3(
    payload: _TC3FeedbackRequest,
):

    from src.inna_platform.services.finance.transaction_feedback import (
        record_classification_feedback,
    )

    try:

        event = (
            record_classification_feedback(
                description=(
                    payload.description
                ),
                final_category=(
                    payload.final_category
                ),
                transaction_type=(
                    payload.transaction_type
                ),
                merchant=(
                    payload.merchant
                ),
                amount=(
                    payload.amount
                ),
                source="financeiro_ui",
            )
        )

    except ValueError as exc:

        raise _TC3HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise _TC3HTTPException(
            status_code=503,
            detail=(
                "Não foi possível registrar "
                "o feedback neste momento."
            ),
        ) from exc

    return {
        "ok": True,
        "feedback": event,
        "privacy": {
            "raw_description_stored": False,
            "merchant_stored": False,
            "amount_stored": False,
            "user_identity_stored": False,
        },
    }


@app.get(
    "/api/platform/finance/transactions/classifier/feedback-capabilities",
    include_in_schema=True,
    tags=["Finance Intelligence"],
)
async def transaction_feedback_capabilities_tc3():

    from src.inna_platform.services.finance.transaction_feedback import (
        feedback_capabilities,
    )

    return {
        "ok": True,
        "classifier": (
            feedback_capabilities()
        ),
    }


# SABINO_TRANSACTION_CLASSIFIER_TC3_END

# SABINO_TC4_B3_AUTH_ROUTER
from src.inna_platform.services.finance.finance_auth_routes import (
    router as finance_auth_router,
)

app.include_router(
    finance_auth_router
)

# SABINO_TC4_C_TRANSACTION_ROUTER
from src.inna_platform.services.finance.finance_transaction_routes import (
    router as finance_transaction_router,
)

app.include_router(
    finance_transaction_router
)



# SABINO_REIMBURSEMENT_PHASE_1B2_ROUTER_START

from src.inna_platform.services.finance.reimbursement.routes import (
    router as finance_reimbursement_router,
)

app.include_router(
    finance_reimbursement_router
)

# SABINO_REIMBURSEMENT_PHASE_1B2_ROUTER_END

# SABINO_TC4_D2B_FINANCEIRO_PAGE_GATE
#
# Regra:
#
# /financeiro?demo=1
#     -> demonstração pública
#
# /financeiro
#     -> exige sessão
#     -> exige entitlement "financeiro" ativo
#
# O navegador nunca informa owner_id nem concede entitlement.

from fastapi import (
    Request as SabinoFinanceiroGateRequest,
)

from fastapi.responses import (
    RedirectResponse as SabinoFinanceiroGateRedirect,
)

from src.inna_platform.services.finance.finance_auth_routes import (
    AUTH_COOKIE_NAME as SABINO_FINANCEIRO_AUTH_COOKIE,
)

from src.inna_platform.services.finance.finance_identity import (
    resolve_session_user as sabino_financeiro_resolve_session,
)

from src.inna_platform.services.finance.platform_entitlements import (
    has_active_platform_entitlement as sabino_financeiro_has_entitlement,
)


@app.middleware("http")
async def sabino_tc4_d2b_financeiro_page_gate(
    request: SabinoFinanceiroGateRequest,
    call_next,
):

    # --------------------------------------------------------
    # PAGINAS REAIS PROTEGIDAS DO FINANCEIRO
    # --------------------------------------------------------

    protected_finance_paths = {
        "/financeiro",
        "/financeiro/orcamento",
    "/financeiro/gastos",
    "/financeiro/metas",
    "/financeiro/planejamento",
    "/financeiro/reserva",
    "/financeiro/seguranca",
    "/financeiro/credito",
    "/financeiro/contas",
      "/financeiro/patrimonio",
        "/financeiro/protecao",
        "/financeiro/impostos",
        "/financeiro/relatorios",
        "/financeiro/educacao",
        "/financeiro/central-contas",
        "/financeiro/reembolso",
        "/financeiro/familia",
}

    if request.url.path not in protected_finance_paths:
        return await call_next(request)

    # --------------------------------------------------------
    # DEMONSTRACAO PUBLICA SOMENTE NA PAGINA PRINCIPAL
    # --------------------------------------------------------

    if (
        request.url.path == "/financeiro"
        and request.query_params.get("demo") == "1"
    ):
        return await call_next(request)

    # --------------------------------------------------------
    # FINANCEIRO REAL - SESSAO OBRIGATORIA
    # --------------------------------------------------------

    session_token = (
        request.cookies.get(
            SABINO_FINANCEIRO_AUTH_COOKIE
        )
    )

    if not session_token:

        return SabinoFinanceiroGateRedirect(
            url="/",
            status_code=303,
        )


    user = (
        sabino_financeiro_resolve_session(
            session_token
        )
    )

    if not user:

        return SabinoFinanceiroGateRedirect(
            url="/",
            status_code=303,
        )


    user_id = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    if not user_id:

        return SabinoFinanceiroGateRedirect(
            url="/",
            status_code=303,
        )


    # --------------------------------------------------------
    # CONTRATACAO / ENTITLEMENT
    # --------------------------------------------------------

    has_access = (
        sabino_financeiro_has_entitlement(
            user_id=user_id,
            platform_code="financeiro",
        )
    )

    if not has_access:

        return SabinoFinanceiroGateRedirect(
            url="/financeiro/planos",
            status_code=303,
        )


    # --------------------------------------------------------
    # CLIENTE AUTENTICADO + FINANCEIRO ATIVO
    # --------------------------------------------------------

    return await call_next(
        request
    )


# SABINO_TC4_D2C_ACCESS_STATUS_ROUTER
from src.inna_platform.services.finance.finance_access_routes import (
    router as sabino_finance_access_router,
)

app.include_router(
    sabino_finance_access_router
)


# ============================================================
# SABINO_FINANCEIRO_ORCAMENTO_ROUTE_V1
# ============================================================


# ============================================================
# SABINO_FX_API_V1
# Display-only foreign exchange infrastructure.
# Original financial values remain unchanged.
# ============================================================

@app.get(
    "/api/finance/fx/rate",
    tags=["Finance"],
)
async def sabino_finance_fx_rate(
    from_currency: str = "BRL",
    to_currency: str = "USD",
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.fx_service import (
        FxProviderError,
        FxValidationError,
        rate_payload,
    )

    try:

        return await rate_payload(
            from_currency,
            to_currency,
        )

    except FxValidationError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except FxProviderError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/finance/fx/convert",
    tags=["Finance"],
)
async def sabino_finance_fx_convert(
    amount: str,
    from_currency: str = "BRL",
    to_currency: str = "USD",
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.fx_service import (
        FxProviderError,
        FxValidationError,
        convert_currency,
    )

    try:

        return await convert_currency(
            amount,
            from_currency,
            to_currency,
        )

    except FxValidationError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except FxProviderError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@app.get("/financeiro/orcamento", include_in_schema=False)
async def sabino_financeiro_orcamento_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-orcamento.html"
    )

    return FileResponse(arquivo, headers={"Cache-Control": "no-store"})

# ============================================================
# SABINO_BUDGET_API_V1
# ============================================================

def sabino_budget_api_owner(request):
    from fastapi import HTTPException

    token = request.cookies.get(SABINO_FINANCEIRO_AUTH_COOKIE)

    if not token:
        raise HTTPException(status_code=401, detail="Sessão obrigatória")

    user = sabino_financeiro_resolve_session(token)

    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    user_id = str(user.get("user_id", "")).strip()

    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    if not sabino_financeiro_has_entitlement(
        user_id=user_id,
        platform_code="financeiro",
    ):
        raise HTTPException(status_code=403, detail="Financeiro não contratado")

    return user_id


@app.get("/api/finance/budget/{reference_month}")
async def sabino_budget_get(reference_month: str, request: SabinoFinanceiroGateRequest):
    from src.inna_platform.services.finance.finance_setup_repository import (
        get_finance_budget_period,
        list_finance_budget_limits,
    )

    owner_id = sabino_budget_api_owner(request)

    period = get_finance_budget_period(
        owner_id=owner_id,
        reference_month=reference_month,
    )

    limits = list_finance_budget_limits(
        owner_id=owner_id,
        reference_month=reference_month,
    )

    return {
        "reference_month": reference_month,
        "period": period,
        "limits": limits,
    }
# SABINO_BUDGET_API_POST_V1

@app.post("/api/finance/budget")
async def sabino_budget_save(request: SabinoFinanceiroGateRequest):
    from decimal import Decimal, InvalidOperation
    import re

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        upsert_finance_budget_period,
        upsert_finance_budget_limit,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    reference_month = str(
        payload.get("reference_month", "")
    ).strip()

    if not re.fullmatch(
        r"\d{4}-(0[1-9]|1[0-2])",
        reference_month,
    ):
        raise HTTPException(
            status_code=422,
            detail="Mês de referência inválido",
        )

    try:
        monthly_income = Decimal(
            str(payload.get("monthly_income", 0) or 0)
        ).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise HTTPException(
            status_code=422,
            detail="Receita mensal inválida",
        )

    if monthly_income < 0:
        raise HTTPException(
            status_code=422,
            detail="Receita mensal não pode ser negativa",
        )

    allowed_categories = {
        "Moradia",
        "Alimentacao",
        "Transporte",
        "Saude",
        "Lazer",
        "Outros",
    }

    incoming_limits = payload.get("limits", {}) or {}

    normalized_limits = {}

    for category in allowed_categories:
        try:
            value = Decimal(
                str(incoming_limits.get(category, 0) or 0)
            ).quantize(Decimal("0.01"))
        except InvalidOperation:
            raise HTTPException(
                status_code=422,
                detail=f"Limite inválido: {category}",
            )

        if value < 0:
            raise HTTPException(
                status_code=422,
                detail=f"Limite negativo: {category}",
            )

        normalized_limits[category] = value

    period = upsert_finance_budget_period(
        owner_id=owner_id,
        reference_month=reference_month,
        monthly_income=monthly_income,
    )

    saved_limits = []

    for category, value in normalized_limits.items():
        saved_limits.append(
            upsert_finance_budget_limit(
                owner_id=owner_id,
                reference_month=reference_month,
                category=category,
                monthly_limit=value,
            )
        )

    return {
        "ok": True,
        "reference_month": reference_month,
        "period": period,
        "limits": saved_limits,
    }
# SABINO_EXPENSE_API_V1

@app.post("/api/finance/expenses")
async def sabino_finance_expense_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.transaction_repository import (
        create_financial_transaction,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        transaction = create_financial_transaction(
            owner_id=owner_id,
            amount=payload.get("amount"),
            description=str(payload.get("description", "")).strip(),
            category=str(payload.get("category", "")).strip(),
            transaction_type="Despesa",
            currency="BRL",
            transaction_date=payload.get("transaction_date"),
            merchant=str(payload.get("merchant", "")).strip(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "transaction": transaction,
    }
# SABINO_EXPENSE_SUMMARY_API_V1

@app.get("/api/finance/expenses/summary/{reference_month}")
async def sabino_finance_expense_summary(
    reference_month: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.transaction_repository import (
        summarize_financial_expenses_by_month,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        return summarize_financial_expenses_by_month(
            owner_id=owner_id,
            reference_month=reference_month,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
# SABINO_FINANCEIRO_GASTOS_ROUTE_V1

@app.get("/financeiro/gastos", include_in_schema=False)
async def sabino_financeiro_gastos_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-gastos.html"
    )

    return FileResponse(arquivo, headers={"Cache-Control": "no-store"})
# SABINO_EXPENSE_LIST_API_V1

@app.get("/api/finance/expenses/month/{reference_month}")
async def sabino_finance_expense_list(
    reference_month: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.transaction_repository import (
        list_financial_expenses_by_month,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        items = list_financial_expenses_by_month(
            owner_id=owner_id,
            reference_month=reference_month,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "reference_month": reference_month,
        "count": len(items),
        "items": items,
    }
# SABINO_FINANCE_GOALS_API_V1

@app.get("/api/finance/goals")
async def sabino_finance_goals_list(
    request: SabinoFinanceiroGateRequest,
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_goals,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    scope = str(
        request.query_params.get(
            "scope",
            "personal",
        )
    ).strip().lower()

    try:

        items = list_finance_goals(
            owner_id=owner_id,
            scope=scope,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


    return {
        "scope": scope,
        "items": items,
    }


@app.post("/api/finance/goals")
async def sabino_finance_goals_create(
    request: SabinoFinanceiroGateRequest,
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_goal,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    payload = await request.json()

    if not isinstance(
        payload,
        dict,
    ):

        raise HTTPException(
            status_code=400,
            detail="Payload inválido.",
        )


    try:

        goal = create_finance_goal(
            owner_id=owner_id,
            name=str(
                payload.get(
                    "name",
                    "",
                )
            ).strip(),
            target_amount=payload.get(
                "target_amount"
            ),
            target_date=payload.get(
                "target_date"
            ) or None,
            scope=payload.get(
                "scope",
                "personal",
            ),
            responsible_member_id=
                payload.get(
                    "responsible_member_id"
                ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


    return {
        "ok": True,
        "goal": goal,
    }

# SABINO_FINANCEIRO_METAS_ROUTE_V1

@app.get("/financeiro/metas", include_in_schema=False)
async def sabino_financeiro_metas_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-metas.html"
    )

    return FileResponse(arquivo, headers={"Cache-Control": "no-store"})
# SABINO_GOAL_CONTRIBUTION_API_V1

@app.post("/api/finance/goals/{goal_id}/contributions")
async def sabino_finance_goal_contribution(
    goal_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        add_finance_goal_amount,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        goal = add_finance_goal_amount(
            owner_id=owner_id,
            goal_id=goal_id,
            amount=payload.get("amount"),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "goal": goal,
    }
# SABINO_FINANCEIRO_PLANEJAMENTO_ROUTE_V1

@app.get("/financeiro/planejamento", include_in_schema=False)
async def sabino_financeiro_planejamento_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-planejamento.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )
# SABINO_FINANCE_RESERVE_API_V1

@app.get("/api/finance/reserve")
async def sabino_finance_reserve_get(
    request: SabinoFinanceiroGateRequest,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        get_finance_reserve,
    )

    owner_id = sabino_budget_api_owner(request)

    return {
        "reserve": get_finance_reserve(
            owner_id=owner_id,
        )
    }


@app.post("/api/finance/reserve")
async def sabino_finance_reserve_save(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        get_finance_reserve,
        upsert_finance_reserve,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    current = get_finance_reserve(
        owner_id=owner_id,
    )

    current_amount = (
        current.get("current_amount", 0)
        if current
        else 0
    )

    try:
        reserve = upsert_finance_reserve(
            owner_id=owner_id,
            target_amount=payload.get("target_amount"),
            current_amount=current_amount,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "reserve": reserve,
    }
# SABINO_FINANCEIRO_RESERVA_ROUTE_V1

@app.get("/financeiro/reserva", include_in_schema=False)
async def sabino_financeiro_reserva_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-reserva.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )
# SABINO_RESERVE_CONTRIBUTION_API_V1

@app.post("/api/finance/reserve/contributions")
async def sabino_finance_reserve_contribution(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        add_finance_reserve_amount,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        reserve = add_finance_reserve_amount(
            owner_id=owner_id,
            amount=payload.get("amount"),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "reserve": reserve,
    }

# SABINO_FINANCEIRO_SEGURANCA_ROUTE_V1

@app.get("/financeiro/seguranca", include_in_schema=False)
async def sabino_financeiro_seguranca_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-seguranca.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )
# SABINO_FINANCE_SECURITY_API_V1

@app.get("/api/finance/security")
async def sabino_finance_security_get(
    request: SabinoFinanceiroGateRequest,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        get_finance_security_profile,
    )

    owner_id = sabino_budget_api_owner(request)

    profile = get_finance_security_profile(
        owner_id=owner_id,
    )

    if profile is None:
        profile = {
            "owner_id": owner_id,
            "strong_password": False,
            "two_factor": False,
            "movement_alerts": False,
            "verify_links": False,
            "review_devices": False,
        }

    return {
        "profile": profile,
    }


@app.post("/api/finance/security")
async def sabino_finance_security_save(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        upsert_finance_security_profile,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    fields = (
        "strong_password",
        "two_factor",
        "movement_alerts",
        "verify_links",
        "review_devices",
    )

    for field in fields:
        value = payload.get(field, False)

        if not isinstance(value, bool):
            raise HTTPException(
                status_code=422,
                detail=f"{field} deve ser booleano",
            )

    profile = upsert_finance_security_profile(
        owner_id=owner_id,
        strong_password=payload.get(
            "strong_password",
            False,
        ),
        two_factor=payload.get(
            "two_factor",
            False,
        ),
        movement_alerts=payload.get(
            "movement_alerts",
            False,
        ),
        verify_links=payload.get(
            "verify_links",
            False,
        ),
        review_devices=payload.get(
            "review_devices",
            False,
        ),
    )

    return {
        "ok": True,
        "profile": profile,
    }

# SABINO_FINANCEIRO_CREDITO_ROUTE_V1

@app.get("/financeiro/credito", include_in_schema=False)
async def sabino_financeiro_credito_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-credito.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )
# SABINO_FINANCE_CREDIT_API_V1

@app.get("/api/finance/debts")
async def sabino_finance_debts_get(
    request: SabinoFinanceiroGateRequest,
):
    from datetime import date
    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_debts,
        get_finance_budget_period,
    )

    owner_id = sabino_budget_api_owner(request)

    debts = list_finance_debts(
        owner_id=owner_id,
    )

    reference_month = date.today().strftime("%Y-%m")

    period = get_finance_budget_period(
        owner_id=owner_id,
        reference_month=reference_month,
    )

    income = (
        float(period.get("monthly_income", 0))
        if period
        else 0.0
    )

    total_debt = sum(
        float(item.get("outstanding_balance", 0))
        for item in debts
    )

    monthly_payments = sum(
        float(item.get("monthly_payment", 0))
        for item in debts
    )

    commitment = (
        (monthly_payments / income) * 100
        if income > 0
        else 0.0
    )

    return {
        "items": debts,
        "summary": {
            "reference_month": reference_month,
            "monthly_income": income,
            "total_debt": total_debt,
            "monthly_payments": monthly_payments,
            "commitment": commitment,
            "debt_count": len(debts),
        },
    }


@app.post("/api/finance/debts")
async def sabino_finance_debts_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_debt,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    allowed_types = {
        "Cartão de crédito",
        "Empréstimo",
        "Financiamento",
        "Cheque especial",
        "Parcelamento",
        "Outro",
    }

    debt_type = str(
        payload.get("debt_type", "")
    ).strip()

    if debt_type not in allowed_types:
        raise HTTPException(
            status_code=422,
            detail="Tipo de dívida inválido",
        )

    try:
        debt = create_finance_debt(
            owner_id=owner_id,
            debt_type=debt_type,
            creditor=payload.get("creditor"),
            outstanding_balance=payload.get(
                "outstanding_balance"
            ),
            monthly_payment=payload.get(
                "monthly_payment"
            ),
            installments_remaining=payload.get(
                "installments_remaining"
            ),
            due_date=payload.get("due_date"),
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "debt": debt,
    }

# SABINO_DEBT_CLOSE_API_V1

@app.delete("/api/finance/debts/{debt_id}")
async def sabino_finance_debt_close(
    debt_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        close_finance_debt,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        debt = close_finance_debt(
            owner_id=owner_id,
            debt_id=debt_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "debt": debt,
    }

# SABINO_DEBT_PAYMENT_API_V1

@app.post("/api/finance/debts/{debt_id}/payments")
async def sabino_finance_debt_payment(
    debt_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        register_finance_debt_payment,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        result = register_finance_debt_payment(
            owner_id=owner_id,
            debt_id=debt_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "payment": result["payment"],
        "debt": result["debt"],
        "auto_closed": result["auto_closed"],
    }

# SABINO_DEBT_DUE_DATE_API_V1

@app.patch("/api/finance/debts/{debt_id}/due-date")
async def sabino_finance_debt_due_date(
    debt_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException
    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_debt_due_date,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        debt = update_finance_debt_due_date(
            owner_id=owner_id,
            debt_id=debt_id,
            due_date=payload.get("due_date"),
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "debt": debt,
    }

# SABINO_DEBT_PAYMENT_HISTORY_API_V1

@app.get("/api/finance/debts/{debt_id}/payments")
async def sabino_finance_debt_payment_history(
    debt_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_debt_payments,
    )

    owner_id = sabino_budget_api_owner(request)

    items = list_finance_debt_payments(
        owner_id=owner_id,
        debt_id=debt_id,
    )

    return {
        "items": items,
        "count": len(items),
    }

# SABINO_FINANCEIRO_CONTAS_ROUTE_V1

@app.get("/financeiro/contas", include_in_schema=False)
async def sabino_financeiro_contas_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-contas.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )
# SABINO_FINANCE_BILLS_API_V1

@app.get("/api/finance/bills")
async def sabino_finance_bills_get(
    request: SabinoFinanceiroGateRequest,
):
    from datetime import date, timedelta
    import calendar

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_bills,
    )

    owner_id = sabino_budget_api_owner(request)

    bills = list_finance_bills(
        owner_id=owner_id,
    )

    today = date.today()

    month_start = today.replace(day=1)

    month_end = today.replace(
        day=calendar.monthrange(
            today.year,
            today.month,
        )[1]
    )

    seven_days = today + timedelta(days=7)

    month_items = [
        item
        for item in bills
        if month_start <= item["due_date"] <= month_end
    ]

    pending_items = [
        item
        for item in bills
        if item["due_date"] <= month_end
    ]

    due_soon_items = [
        item
        for item in bills
        if today <= item["due_date"] <= seven_days
    ]

    subscriptions = [
        item
        for item in bills
        if bool(item.get("is_subscription"))
    ]

    total_month = sum(
        float(item.get("amount", 0))
        for item in month_items
    )

    return {
        "items": bills,
        "summary": {
            "reference_month": today.strftime("%Y-%m"),
            "month_total": total_month,
            "pending_count": len(pending_items),
            "due_soon_count": len(due_soon_items),
            "subscription_count": len(subscriptions),
        },
    }


@app.post("/api/finance/bills")
async def sabino_finance_bills_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_bill,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    allowed_categories = {
        "Contas",
        "Assinaturas",
        "Moradia",
        "Educação",
        "Saúde",
        "Seguros",
        "Transporte",
        "Lazer",
        "Outras despesas",
    }

    category = str(
        payload.get("category", "")
    ).strip()

    if category not in allowed_categories:
        raise HTTPException(
            status_code=422,
            detail="Categoria inválida",
        )

    recurrence = str(
        payload.get("recurrence", "none")
    ).strip().lower()

    if recurrence not in {
        "none",
        "monthly",
    }:
        raise HTTPException(
            status_code=422,
            detail="Recorrência inválida",
        )

    is_subscription = payload.get(
        "is_subscription",
        False,
    )

    if not isinstance(is_subscription, bool):
        raise HTTPException(
            status_code=422,
            detail="is_subscription deve ser booleano",
        )

    try:
        bill = create_finance_bill(
            owner_id=owner_id,
            name=payload.get("name"),
            category=category,
            amount=payload.get("amount"),
            due_date=payload.get("due_date"),
            recurrence=recurrence,
            is_subscription=is_subscription,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "bill": bill,
    }

# SABINO_BILL_PAYMENT_API_V1

@app.post("/api/finance/bills/{bill_id}/payments")
async def sabino_finance_bill_payment(
    bill_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        register_finance_bill_payment,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        result = register_finance_bill_payment(
            owner_id=owner_id,
            bill_id=bill_id,
            expected_due_date=payload.get(
                "expected_due_date"
            ),
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "already_paid": result.get(
            "already_paid",
            False,
        ),
        "payment": result.get("payment"),
        "bill": result.get("bill"),
        "transaction": result.get(
            "transaction"
        ),
    }

# SABINO_BILL_PAYMENT_HISTORY_API_V1

@app.get("/api/finance/bills/{bill_id}/payments")
async def sabino_finance_bill_payment_history(
    bill_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_bill_payments,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        items = list_finance_bill_payments(
            owner_id=owner_id,
            bill_id=bill_id,
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    total_paid = sum(
        float(item.get("amount") or 0)
        for item in items
    )

    return {
        "bill_id": bill_id,
        "items": items,
        "summary": {
            "payment_count": len(items),
            "total_paid": total_paid,
        },
    }

# SABINO_FINANCEIRO_PATRIMONIO_ROUTE_V1

@app.get("/financeiro/patrimonio", include_in_schema=False)
async def sabino_financeiro_patrimonio():
    from fastapi.responses import FileResponse

    response = FileResponse(
        "src/inna_platform/static/financeiro-patrimonio.html"
    )

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    return response

# SABINO_FINANCE_ASSETS_API_V1

@app.get("/api/finance/assets")
async def sabino_finance_assets_list(
    request: SabinoFinanceiroGateRequest,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_assets,
    )

    owner_id = sabino_budget_api_owner(request)

    items = list_finance_assets(
        owner_id=owner_id,
    )

    total_assets = sum(
        float(item.get("value") or 0)
        for item in items
    )

    return {
        "items": items,
        "summary": {
            "asset_count": len(items),
            "total_assets": total_assets,
        },
    }


@app.post("/api/finance/assets")
async def sabino_finance_assets_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_asset,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        asset = create_finance_asset(
            owner_id=owner_id,
            name=payload.get("name"),
            asset_type=payload.get("asset_type"),
            value=payload.get("value"),
            institution=payload.get(
                "institution",
                "",
            ),
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "asset": asset,
    }


# SABINO_FINANCE_ASSET_CRUD_API_V2

@app.put("/api/finance/assets/{asset_id}")
async def sabino_finance_assets_update(
    asset_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_asset,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    try:
        asset = update_finance_asset(
            owner_id=owner_id,
            asset_id=asset_id,
            name=payload.get("name"),
            asset_type=payload.get("asset_type"),
            value=payload.get("value"),
            institution=payload.get(
                "institution",
                "",
            ),
        )

    except (ValueError, TypeError) as exc:

        status_code = (
            404
            if str(exc) == "ativo não encontrado"
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "asset": asset,
    }


@app.delete("/api/finance/assets/{asset_id}")
async def sabino_finance_assets_delete(
    asset_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        delete_finance_asset,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        asset = delete_finance_asset(
            owner_id=owner_id,
            asset_id=asset_id,
        )

    except (ValueError, TypeError) as exc:

        status_code = (
            404
            if str(exc) == "ativo não encontrado"
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "deleted": True,
        "asset": asset,
    }


# SABINO_FINANCE_INSURANCE_API_V1

@app.get("/api/finance/insurance")
async def sabino_finance_insurance_list(
    request: SabinoFinanceiroGateRequest,
):
    from datetime import date, timedelta

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_insurance_policies,
    )

    owner_id = sabino_budget_api_owner(request)

    policies = list_finance_insurance_policies(
        owner_id=owner_id,
    )

    total_coverage = sum(
        float(item.get("coverage_amount") or 0)
        for item in policies
    )

    monthly_equivalent_cost = 0.0

    for item in policies:

        premium = float(
            item.get("premium_amount") or 0
        )

        frequency = str(
            item.get("premium_frequency") or ""
        )

        if frequency == "Mensal":
            monthly_equivalent_cost += premium

        elif frequency == "Anual":
            monthly_equivalent_cost += (
                premium / 12
            )

    today = date.today()
    limit_date = today + timedelta(days=30)

    expiring_30_days = 0

    for item in policies:

        end_date = item.get("end_date")

        if (
            end_date
            and today <= end_date <= limit_date
        ):
            expiring_30_days += 1

    return {
        "items": policies,
        "summary": {
            "policy_count": len(policies),
            "total_coverage": total_coverage,
            "monthly_equivalent_cost":
                monthly_equivalent_cost,
            "expiring_30_days":
                expiring_30_days,
        },
    }


@app.post("/api/finance/insurance")
async def sabino_finance_insurance_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_insurance_policy,
        list_finance_assets,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    linked_asset_id = str(
        payload.get("linked_asset_id") or ""
    ).strip()

    # Se houver ativo relacionado, ele precisa
    # pertencer ao mesmo usuário autenticado.
    if linked_asset_id:

        assets = list_finance_assets(
            owner_id=owner_id,
        )

        allowed_asset_ids = {
            str(item.get("asset_id"))
            for item in assets
        }

        if linked_asset_id not in allowed_asset_ids:

            raise HTTPException(
                status_code=422,
                detail=(
                    "ativo relacionado inválido "
                    "para este usuário"
                ),
            )

    try:

        policy = create_finance_insurance_policy(
            owner_id=owner_id,
            name=payload.get("name"),
            insurance_type=
                payload.get("insurance_type"),
            provider=payload.get("provider"),
            coverage_amount=
                payload.get("coverage_amount"),
            premium_amount=
                payload.get("premium_amount"),
            premium_frequency=
                payload.get("premium_frequency"),
            start_date=
                payload.get("start_date") or None,
            end_date=
                payload.get("end_date") or None,
            linked_asset_id=
                linked_asset_id or None,
            insured_item=
                payload.get("insured_item", ""),
        )

    except (ValueError, TypeError) as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "policy": policy,
    }


# SABINO_FINANCEIRO_PROTECAO_ROUTE_V1

@app.get("/financeiro/protecao", include_in_schema=False)
async def sabino_financeiro_protecao_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-protecao.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )


# SABINO_FINANCE_INSURANCE_CRUD_API_V2

@app.put("/api/finance/insurance/{policy_id}")
async def sabino_finance_insurance_update(
    policy_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_insurance_policy,
        list_finance_assets,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    linked_asset_id = str(
        payload.get("linked_asset_id") or ""
    ).strip()

    # Ativo vinculado precisa ser do mesmo proprietário.
    if linked_asset_id:

        assets = list_finance_assets(
            owner_id=owner_id,
        )

        allowed_asset_ids = {
            str(item.get("asset_id"))
            for item in assets
        }

        if linked_asset_id not in allowed_asset_ids:

            raise HTTPException(
                status_code=422,
                detail=(
                    "ativo relacionado inválido "
                    "para este usuário"
                ),
            )

    try:

        policy = update_finance_insurance_policy(
            owner_id=owner_id,
            policy_id=policy_id,
            name=payload.get("name"),
            insurance_type=
                payload.get("insurance_type"),
            provider=
                payload.get("provider"),
            coverage_amount=
                payload.get("coverage_amount"),
            premium_amount=
                payload.get("premium_amount"),
            premium_frequency=
                payload.get("premium_frequency"),
            start_date=
                payload.get("start_date") or None,
            end_date=
                payload.get("end_date") or None,
            linked_asset_id=
                linked_asset_id or None,
            insured_item=
                payload.get("insured_item", ""),
        )

    except (ValueError, TypeError) as exc:

        status_code = (
            404
            if str(exc) == "apólice não encontrada"
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "policy": policy,
    }


@app.post("/api/finance/insurance/{policy_id}/renew")
async def sabino_finance_insurance_renew(
    policy_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from datetime import date
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_insurance_policies,
        renew_finance_insurance_policy,
    )

    owner_id = sabino_budget_api_owner(request)
    payload = await request.json()

    policies = list_finance_insurance_policies(
        owner_id=owner_id,
    )

    current_policy = next(
        (
            item
            for item in policies
            if str(item.get("policy_id")) ==
               str(policy_id)
        ),
        None,
    )

    if not current_policy:

        raise HTTPException(
            status_code=404,
            detail="apólice não encontrada",
        )

    try:

        new_end_date = date.fromisoformat(
            str(
                payload.get("new_end_date") or ""
            )
        )

    except ValueError:

        raise HTTPException(
            status_code=422,
            detail=(
                "nova data de vencimento inválida"
            ),
        )

    current_end_date = (
        current_policy.get("end_date")
    )

    if current_end_date:

        if isinstance(current_end_date, str):
            current_end_date = date.fromisoformat(
                current_end_date[:10]
            )

        if new_end_date <= current_end_date:

            raise HTTPException(
                status_code=422,
                detail=(
                    "a renovação deve possuir "
                    "vencimento posterior ao atual"
                ),
            )

    try:

        policy = renew_finance_insurance_policy(
            owner_id=owner_id,
            policy_id=policy_id,
            new_end_date=new_end_date,
        )

    except (ValueError, TypeError) as exc:

        status_code = (
            404
            if str(exc) == "apólice não encontrada"
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "renewed": True,
        "policy": policy,
    }


@app.post("/api/finance/insurance/{policy_id}/cancel")
async def sabino_finance_insurance_cancel(
    policy_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        cancel_finance_insurance_policy,
    )

    owner_id = sabino_budget_api_owner(request)

    try:

        policy = cancel_finance_insurance_policy(
            owner_id=owner_id,
            policy_id=policy_id,
        )

    except (ValueError, TypeError) as exc:

        status_code = (
            404
            if str(exc) == "apólice não encontrada"
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "cancelled": True,
        "policy": policy,
    }


# SABINO_FINANCE_INSURANCE_HISTORY_API_V1

@app.get("/api/finance/insurance/history")
async def sabino_finance_insurance_history(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_insurance_policy_history,
    )

    owner_id = sabino_budget_api_owner(request)

    try:

        items = list_finance_insurance_policy_history(
            owner_id=owner_id,
        )

    except (ValueError, TypeError) as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "items": items,
        "summary": {
            "cancelled_policy_count": len(items),
        },
    }


# ============================================================
# SABINO_FINANCE_TAX_OBLIGATIONS_API_V1
# ============================================================

@app.get("/api/finance/tax-obligations")
async def sabino_finance_tax_obligations_list(
    request: SabinoFinanceiroGateRequest,
):
    from datetime import date, timedelta
    from decimal import Decimal

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_tax_obligations,
    )

    owner_id = sabino_budget_api_owner(request)

    items = list_finance_tax_obligations(
        owner_id=owner_id,
    )

    today = date.today()
    next_30_days = today + timedelta(days=30)

    pending_count = 0
    paid_count = 0
    due_30_days = 0
    overdue_count = 0

    pending_amount = Decimal("0")
    paid_amount = Decimal("0")

    for item in items:

        amount = Decimal(
            str(item.get("amount") or 0)
        )

        paid = bool(
            item.get("paid")
        )

        due_date = item.get(
            "due_date"
        )

        if paid:

            paid_count += 1
            paid_amount += amount

            continue

        pending_count += 1
        pending_amount += amount

        if not due_date:
            continue

        if isinstance(due_date, str):
            due_date = date.fromisoformat(
                due_date[:10]
            )

        if due_date < today:

            overdue_count += 1

        elif today <= due_date <= next_30_days:

            due_30_days += 1

    return {
        "items": items,
        "summary": {
            "total_count": len(items),
            "pending_count": pending_count,
            "paid_count": paid_count,
            "due_30_days": due_30_days,
            "overdue_count": overdue_count,
            "pending_amount": pending_amount,
            "paid_amount": paid_amount,
        },
    }


@app.post("/api/finance/tax-obligations")
async def sabino_finance_tax_obligations_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_tax_obligation,
    )

    owner_id = sabino_budget_api_owner(request)

    payload = await request.json()

    try:

        obligation = create_finance_tax_obligation(
            owner_id=owner_id,
            name=payload.get("name"),
            obligation_type=
                payload.get("obligation_type"),
            amount=
                payload.get("amount"),
            frequency=
                payload.get("frequency"),
            due_date=
                payload.get("due_date") or None,
            authority_name=
                payload.get("authority_name", ""),
            reference_label=
                payload.get("reference_label", ""),
            document_reference=
                payload.get("document_reference", ""),
            notes=
                payload.get("notes", ""),
        )

    except (ValueError, TypeError) as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "obligation": obligation,
    }


@app.post(
    "/api/finance/tax-obligations/{obligation_id}/pay"
)
async def sabino_finance_tax_obligation_pay(
    obligation_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        mark_finance_tax_obligation_paid,
    )

    from src.inna_platform.services.finance.transaction_repository import (
        create_financial_transaction_idempotent,
    )

    owner_id = sabino_budget_api_owner(request)

    try:

        payload = await request.json()

    except Exception:

        payload = {}

    try:

        obligation = mark_finance_tax_obligation_paid(
            owner_id=owner_id,
            obligation_id=obligation_id,
            paid_at=
                payload.get("paid_at") or None,
        )
        # SABINO_TAX_PAYMENT_EXPENSE_V1

        paid_date = obligation.get("paid_at")

        paid_date_key = (
            str(paid_date)
            .replace("-", "")
            [:8]
            if paid_date
            else "paid"
        )

        expense_transaction = (
            create_financial_transaction_idempotent(
                transaction_id=(
                    f"taxpay_{obligation_id}_{paid_date_key}"
                ),
                owner_id=owner_id,
                transaction_date=paid_date,
                transaction_type="Despesa",
                amount=obligation.get("amount") or 0,
                currency="BRL",
                description=(
                    "Pagamento de obrigação: "
                    f"{obligation.get('name') or 'Obrigação'}"
                ),
                merchant=(
                    obligation.get("authority_name")
                    or obligation.get("name")
                    or "Obrigação"
                ),
                category="Impostos",
                subcategory=(
                    obligation.get("obligation_type")
                    or "Obrigação"
                ),
                classification_strategy="manual",
                classification_confirmed=True,
                source="financeiro_ui",
            )
        )

    except (ValueError, TypeError) as exc:

        status_code = (
            404
            if str(exc) == "obrigação não encontrada"
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "paid": True,
        "obligation": obligation,
        "expense_transaction": expense_transaction,
    }


# SABINO_FINANCEIRO_IMPOSTOS_ROUTE_V1

@app.get(
    "/financeiro/impostos",
    include_in_schema=False,
)
async def sabino_financeiro_impostos_page():

    from pathlib import Path
    from fastapi.responses import FileResponse

    page = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-impostos.html"
    )

    response = FileResponse(page)

    response.headers[
        "Cache-Control"
    ] = "no-store"

    return response


# ============================================================
# SABINO_TAX_EXPENSE_RECONCILE_V1
# ============================================================

@app.post(
    "/api/finance/tax-obligations/reconcile-expenses"
)
async def sabino_finance_tax_reconcile_expenses(
    request: SabinoFinanceiroGateRequest,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_tax_obligations,
    )

    from src.inna_platform.services.finance.transaction_repository import (
        create_financial_transaction_idempotent,
    )

    owner_id = sabino_budget_api_owner(request)

    obligations = list_finance_tax_obligations(
        owner_id=owner_id,
    )

    processed = []

    for obligation in obligations:

        if not bool(
            obligation.get("paid")
        ):
            continue

        paid_date = obligation.get(
            "paid_at"
        )

        if not paid_date:
            continue

        obligation_id = str(
            obligation.get("obligation_id")
            or ""
        ).strip()

        if not obligation_id:
            continue

        paid_date_key = (
            str(paid_date)
            .replace("-", "")
            [:8]
        )

        transaction = (
            create_financial_transaction_idempotent(
                transaction_id=(
                    f"taxpay_{obligation_id}_{paid_date_key}"
                ),
                owner_id=owner_id,
                transaction_date=paid_date,
                transaction_type="Despesa",
                amount=(
                    obligation.get("amount")
                    or 0
                ),
                currency="BRL",
                description=(
                    "Pagamento de obrigação: "
                    f"{obligation.get('name') or 'Obrigação'}"
                ),
                merchant=(
                    obligation.get("authority_name")
                    or obligation.get("name")
                    or "Obrigação"
                ),
                category="Impostos",
                subcategory=(
                    obligation.get("obligation_type")
                    or "Obrigação"
                ),
                classification_strategy="manual",
                classification_confirmed=True,
                source="financeiro_ui",
            )
        )

        processed.append({
            "obligation_id": obligation_id,
            "transaction_id":
                transaction.get("transaction_id"),
        })

    return {
        "ok": True,
        "processed_count": len(processed),
        "items": processed,
    }

# ============================================================
# SABINO_FINANCE_INVESTMENTS_API_V1
# ============================================================

@app.get("/api/finance/investments")
async def sabino_finance_investments_list(
    request: SabinoFinanceiroGateRequest,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        FINANCE_INVESTMENT_TYPES,
        FINANCE_INVESTMENT_LIQUIDITIES,
        list_finance_investments,
        summarize_finance_investments,
    )

    owner_id = sabino_budget_api_owner(request)

    return {
        "items": list_finance_investments(
            owner_id=owner_id,
        ),
        "summary": summarize_finance_investments(
            owner_id=owner_id,
        ),
        "investment_types": sorted(
            FINANCE_INVESTMENT_TYPES
        ),
        "liquidities": sorted(
            FINANCE_INVESTMENT_LIQUIDITIES
        ),
    }


@app.post("/api/finance/investments")
async def sabino_finance_investments_create(
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_investment,
        summarize_finance_investments,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        payload = await request.json()

        investment = create_finance_investment(
            owner_id=owner_id,
            name=payload.get("name"),
            investment_type=payload.get(
                "investment_type"
            ),
            institution=payload.get(
                "institution"
            ),
            invested_amount=payload.get(
                "invested_amount"
            ),
            current_value=payload.get(
                "current_value"
            ),
            liquidity=payload.get(
                "liquidity"
            ),
            objective=payload.get(
                "objective"
            ),
            maturity_date=payload.get(
                "maturity_date"
            ),
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "investment": investment,
        "summary": summarize_finance_investments(
            owner_id=owner_id,
        ),
    }

# ============================================================
# SABINO_FINANCE_INVESTMENTS_CRUD_API_V2
# ============================================================

@app.put("/api/finance/investments/{investment_id}")
async def sabino_finance_investments_update(
    investment_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_investment,
        summarize_finance_investments,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        payload = await request.json()

        investment = update_finance_investment(
            owner_id=owner_id,
            investment_id=investment_id,
            name=payload.get("name"),
            investment_type=payload.get(
                "investment_type"
            ),
            institution=payload.get(
                "institution"
            ),
            invested_amount=payload.get(
                "invested_amount"
            ),
            current_value=payload.get(
                "current_value"
            ),
            liquidity=payload.get(
                "liquidity"
            ),
            objective=payload.get(
                "objective"
            ),
            maturity_date=payload.get(
                "maturity_date"
            ),
        )

    except (ValueError, TypeError) as exc:

        message = str(exc)

        raise HTTPException(
            status_code=(
                404
                if "não encontrado" in message
                else 422
            ),
            detail=message,
        ) from exc

    return {
        "ok": True,
        "investment": investment,
        "summary": summarize_finance_investments(
            owner_id=owner_id,
        ),
    }


@app.delete("/api/finance/investments/{investment_id}")
async def sabino_finance_investments_delete(
    investment_id: str,
    request: SabinoFinanceiroGateRequest,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        delete_finance_investment,
        summarize_finance_investments,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        investment = delete_finance_investment(
            owner_id=owner_id,
            investment_id=investment_id,
        )

    except (ValueError, TypeError) as exc:

        message = str(exc)

        raise HTTPException(
            status_code=(
                404
                if "não encontrado" in message
                else 422
            ),
            detail=message,
        ) from exc

    return {
        "ok": True,
        "investment": investment,
        "summary": summarize_finance_investments(
            owner_id=owner_id,
        ),
    }

# ============================================================
# SABINO_FINANCE_REPORTS_PAGE_V1
# ============================================================
@app.get("/financeiro/relatorios", include_in_schema=False)
async def sabino_financeiro_relatorios_page():
    from pathlib import Path
    from fastapi.responses import FileResponse
    arquivo = Path(__file__).resolve().parent / "static" / "financeiro-relatorios.html"
    return FileResponse(arquivo, headers={"Cache-Control": "no-store"})



# ============================================================
# SABINO_FINANCE_NEW_MODULES_ROUTES_V1
# ============================================================

@app.get("/financeiro/educacao", include_in_schema=False)
async def sabino_financeiro_educacao_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-educacao.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )


@app.get("/financeiro/central-contas", include_in_schema=False)
async def sabino_financeiro_central_contas_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-central-contas.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )


@app.get("/financeiro/reembolso", include_in_schema=False)
async def sabino_financeiro_reembolso_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-reembolso.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )


@app.get("/financeiro/familia", include_in_schema=False)
async def sabino_financeiro_familia_page():
    from pathlib import Path
    from fastapi.responses import FileResponse

    arquivo = (
        Path(__file__).resolve().parent
        / "static"
        / "financeiro-familia.html"
    )

    return FileResponse(
        arquivo,
        headers={"Cache-Control": "no-store"},
    )


# ============================================================
# SABINO_FINANCE_EDUCATION_API_V1
# ============================================================

@app.get("/api/finance/education/progress")
async def sabino_finance_education_progress_get(
    request: Request,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        EDUCATION_TRACK_IDS,
        list_finance_education_progress,
    )

    owner_id = sabino_budget_api_owner(request)

    items = list_finance_education_progress(
        owner_id=owner_id,
    )

    completed_count = sum(
        1
        for item in items
        if bool(item.get("completed"))
    )

    total_tracks = len(
        EDUCATION_TRACK_IDS
    )

    progress_percent = (
        round(
            (
                completed_count
                / total_tracks
            ) * 100
        )
        if total_tracks
        else 0
    )

    return {
        "items": items,
        "summary": {
            "total_tracks": total_tracks,
            "completed_tracks": completed_count,
            "progress_percent": progress_percent,
        },
    }


@app.put(
    "/api/finance/education/progress/{track_id}"
)
async def sabino_finance_education_progress_put(
    track_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        upsert_finance_education_progress,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    try:
        item = upsert_finance_education_progress(
            owner_id=owner_id,
            track_id=track_id,
            quiz_score=payload.get(
                "quiz_score"
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "item": item,
    }

# ============================================================
# SABINO_FINANCE_CENTRAL_ACCOUNTS_API_V1
# ============================================================

@app.get("/api/finance/central-accounts")
async def sabino_finance_central_accounts_get(
    request: Request,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_central_accounts,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    items = list_finance_central_accounts(
        owner_id=owner_id
    )

    total_balance = sum(
        (
            item.get("current_balance") or 0
            for item in items
            if item.get("is_active")
        ),
        0,
    )

    active_count = sum(
        1
        for item in items
        if item.get("is_active")
    )

    return {
        "items": items,
        "summary": {
            "accounts_count": len(items),
            "active_accounts": active_count,
            "total_balance": total_balance,
        },
    }


@app.post(
    "/api/finance/central-accounts",
    status_code=201,
)
async def sabino_finance_central_accounts_post(
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_central_account,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    try:
        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        item = create_finance_central_account(
            owner_id=owner_id,
            institution=payload.get(
                "institution"
            ),
            account_name=payload.get(
                "account_name"
            ),
            account_type=payload.get(
                "account_type"
            ),
            current_balance=payload.get(
                "current_balance",
                0,
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return {
        "item": item
    }

# ============================================================
# SABINO_CENTRAL_ACCOUNT_UPDATE_API_V2
# ============================================================

@app.put("/api/finance/central-accounts/{account_id}")
async def sabino_finance_central_account_update(
    account_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_central_account,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        payload = await request.json()

        item = update_finance_central_account(
            owner_id=owner_id,
            account_id=account_id,
            institution=payload.get("institution"),
            account_name=payload.get("account_name"),
            account_type=payload.get("account_type"),
            current_balance=payload.get("current_balance", 0),
        )

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada.",
        )

    return {"item": item}

# ============================================================
# SABINO_CENTRAL_ACCOUNT_ACTIVE_API_V2
# ============================================================

@app.patch("/api/finance/central-accounts/{account_id}/active")
async def sabino_finance_central_account_active(
    account_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        set_finance_central_account_active,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        payload = await request.json()

        is_active = payload.get("is_active")

        if not isinstance(is_active, bool):
            raise ValueError(
                "is_active deve ser booleano."
            )

        item = set_finance_central_account_active(
            owner_id=owner_id,
            account_id=account_id,
            is_active=is_active,
        )

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada.",
        )

    return {"item": item}

# ============================================================
# SABINO_CENTRAL_ACCOUNT_DELETE_API_V2
# ============================================================

@app.delete("/api/finance/central-accounts/{account_id}")
async def sabino_finance_central_account_delete(
    account_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        delete_finance_central_account,
    )

    owner_id = sabino_budget_api_owner(request)

    deleted = delete_finance_central_account(
        owner_id=owner_id,
        account_id=account_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada.",
        )

    return {
        "deleted": True,
        "id": deleted.get("id"),
    }

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBERS_API_V1
# ============================================================

@app.get("/api/finance/family/members")
async def sabino_finance_family_members_get(
    request: Request,
):
    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_family_members,
    )

    owner_id = sabino_budget_api_owner(request)

    items = list_finance_family_members(
        owner_id=owner_id
    )

    active_items = [
        item
        for item in items
        if item.get("is_active")
    ]

    monthly_contribution = sum(
        (
            item.get("monthly_contribution") or 0
            for item in active_items
        ),
        0,
    )

    return {
        "items": items,
        "summary": {
            "members_count": len(items),
            "active_members": len(active_items),
            "monthly_contribution": monthly_contribution,
        },
    }


@app.post(
    "/api/finance/family/members",
    status_code=201,
)
async def sabino_finance_family_members_post(
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_family_member,
    )

    owner_id = sabino_budget_api_owner(request)

    try:
        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        item = create_finance_family_member(
            owner_id=owner_id,
            member_name=payload.get(
                "member_name"
            ),
            relation=payload.get(
                "relation"
            ),
            monthly_contribution=payload.get(
                "monthly_contribution",
                0,
            ),
            expense_share_percent=payload.get(
                "expense_share_percent",
                0,
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return {
        "item": item
    }

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBER_UPDATE_API_V2
# ============================================================

@app.put("/api/finance/family/members/{member_id}")
async def sabino_finance_family_member_update(
    member_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_family_member,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    try:
        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        item = update_finance_family_member(
            owner_id=owner_id,
            member_id=member_id,
            member_name=payload.get(
                "member_name"
            ),
            relation=payload.get(
                "relation"
            ),
            monthly_contribution=payload.get(
                "monthly_contribution",
                0,
            ),
            expense_share_percent=payload.get(
                "expense_share_percent",
                0,
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Membro não encontrado.",
        )

    return {
        "item": item
    }

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBER_ACTIVE_API_V2
# ============================================================

@app.patch("/api/finance/family/members/{member_id}/active")
async def sabino_finance_family_member_active(
    member_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        set_finance_family_member_active,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    try:
        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        is_active = payload.get(
            "is_active"
        )

        if not isinstance(is_active, bool):
            raise ValueError(
                "is_active deve ser booleano."
            )

        item = set_finance_family_member_active(
            owner_id=owner_id,
            member_id=member_id,
            is_active=is_active,
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Membro não encontrado.",
        )

    return {
        "item": item
    }

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBER_DELETE_API_V2
# ============================================================

@app.delete("/api/finance/family/members/{member_id}")
async def sabino_finance_family_member_delete(
    member_id: str,
    request: Request,
):
    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        delete_finance_family_member,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    deleted = delete_finance_family_member(
        owner_id=owner_id,
        member_id=member_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Membro não encontrado.",
        )

    return {
        "deleted": True,
        "id": deleted.get("id"),
        "member_name": deleted.get("member_name"),
    }


# ============================================================
# SABINO_FINANCE_FAMILY_EXPENSES_API_V1
# ============================================================

@app.get("/api/finance/family/expenses")
async def sabino_finance_family_expenses_get(
    request: Request,
):

    from src.inna_platform.services.finance.finance_setup_repository import (
        list_finance_family_expenses,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    items = list_finance_family_expenses(
        owner_id=owner_id
    )

    active_expenses = [
        item
        for item in items
        if item.get("status") != "cancelled"
    ]

    total_expenses = sum(
        (
            item.get("amount") or 0
            for item in active_expenses
        ),
        0,
    )

    pending_expenses = sum(
        (
            item.get("amount") or 0
            for item in items
            if item.get("status") in {
                "pending",
                "overdue",
            }
        ),
        0,
    )

    paid_expenses = sum(
        (
            item.get("amount") or 0
            for item in items
            if item.get("status") == "paid"
        ),
        0,
    )

    return {
        "items": items,
        "summary": {
            "expenses_count": len(items),
            "total_expenses": total_expenses,
            "pending_expenses": pending_expenses,
            "paid_expenses": paid_expenses,
        },
    }


@app.post(
    "/api/finance/family/expenses",
    status_code=201,
)
async def sabino_finance_family_expenses_post(
    request: Request,
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        create_finance_family_expense,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    try:

        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        item = create_finance_family_expense(
            owner_id=owner_id,
            description=payload.get(
                "description"
            ),
            category=payload.get(
                "category"
            ),
            amount=payload.get(
                "amount",
                0,
            ),
            due_date=payload.get(
                "due_date"
            ),
            responsible_member_id=payload.get(
                "responsible_member_id"
            ),
            recurrence=payload.get(
                "recurrence",
                "once",
            ),
            status=payload.get(
                "status",
                "pending",
            ),
            notes=payload.get(
                "notes"
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return {
        "item": item
    }


@app.put(
    "/api/finance/family/expenses/{expense_id}"
)
async def sabino_finance_family_expense_update(
    expense_id: str,
    request: Request,
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        update_finance_family_expense,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    try:

        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        item = update_finance_family_expense(
            owner_id=owner_id,
            expense_id=expense_id,
            description=payload.get(
                "description"
            ),
            category=payload.get(
                "category"
            ),
            amount=payload.get(
                "amount",
                0,
            ),
            due_date=payload.get(
                "due_date"
            ),
            responsible_member_id=payload.get(
                "responsible_member_id"
            ),
            recurrence=payload.get(
                "recurrence",
                "once",
            ),
            status=payload.get(
                "status",
                "pending",
            ),
            notes=payload.get(
                "notes"
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Despesa familiar não encontrada.",
        )

    return {
        "item": item
    }


@app.patch(
    "/api/finance/family/expenses/{expense_id}/status"
)
async def sabino_finance_family_expense_status(
    expense_id: str,
    request: Request,
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        set_finance_family_expense_status,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    try:

        payload = await request.json()

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload inválido."
            )

        item = set_finance_family_expense_status(
            owner_id=owner_id,
            expense_id=expense_id,
            status=payload.get(
                "status"
            ),
        )

    except (
        ValueError,
        TypeError,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Despesa familiar não encontrada.",
        )

    return {
        "item": item
    }


@app.delete(
    "/api/finance/family/expenses/{expense_id}"
)
async def sabino_finance_family_expense_delete(
    expense_id: str,
    request: Request,
):

    from fastapi import HTTPException

    from src.inna_platform.services.finance.finance_setup_repository import (
        delete_finance_family_expense,
    )

    owner_id = sabino_budget_api_owner(
        request
    )

    deleted = delete_finance_family_expense(
        owner_id=owner_id,
        expense_id=expense_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Despesa familiar não encontrada.",
        )

    return {
        "deleted": True,
        "id": deleted.get("id"),
        "description": deleted.get(
            "description"
        ),
    }


# Subscription navigation uses the same authenticated identity as Financeiro.
from src.inna_platform.services.finance.subscription_navigation import (
    router as subscription_navigation_router,
)

app.include_router(subscription_navigation_router)
from src.inna_platform.services.finance.credit_routes import router as credit_router
app.include_router(credit_router)

from src.inna_platform.services.finance.manual_pix_routes import router as manual_pix_router
app.include_router(manual_pix_router)

from src.inna_platform.services.finance.finance_pilot import router as finance_pilot_router
app.include_router(finance_pilot_router)


from src.inna_platform.services.sabino_onboarding import router as sabino_onboarding_router
app.include_router(sabino_onboarding_router)
