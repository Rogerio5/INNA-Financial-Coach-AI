document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    console.log(
        "SABINO_EDUCATION_V2_FIX=LOADED"
    );


    const platformActive =
        localStorage.getItem(
            "inna_platform_active"
        ) === "true";


    if (!platformActive) {

        window.location.replace(
            "/jornada"
        );

        return;

    }


    function readJson(key) {

        try {

            const raw =
                localStorage.getItem(key);

            return raw
                ? JSON.parse(raw)
                : {};

        }
        catch {

            return {};

        }

    }


    function valueLabel(value, fallback = "-") {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return fallback;
        }


        if (
            typeof value === "string" ||
            typeof value === "number"
        ) {
            return String(value);
        }


        return (
            value.label ||
            value.name ||
            value.value ||
            fallback
        );

    }


    const config =
        readJson(
            "inna_solution_config"
        );


    const integrations =
        Array.isArray(
            config.integrations
        )
            ? config.integrations
            : [];


    const rag =
        valueLabel(
            config.rag,
            "Base configurada"
        );


    const ragElement =
        document.getElementById(
            "ef2-rag"
        );


    if (ragElement) {

        ragElement.textContent =
            `${rag} · sincronizada`;

    }


    const integrationElement =
        document.getElementById(
            "ef2-integrations"
        );


    if (integrationElement) {

        integrationElement.textContent =
            integrations.length
                ? `${integrations.length}/${integrations.length}`
                : "0/0";

    }


    const toast =
        document.getElementById(
            "ef2-toast"
        );


    let toastTimer;


    function showToast(message) {

        if (!toast) {
            return;
        }


        clearTimeout(
            toastTimer
        );


        toast.textContent =
            message;


        toast.classList.add(
            "show"
        );


        toastTimer =
            setTimeout(
                () => {

                    toast.classList.remove(
                        "show"
                    );

                },
                2800
            );

    }


    const messages = {

        inna:
            "A INNA será conectada aos dados reais deste módulo na etapa de integração.",

        report:
            "Relatórios serão alimentados pelos dados reais do módulo.",

        diagnostics:
            "Diagnósticos completos serão conectados ao FastAPI/PostgreSQL."

    };


    document
        .querySelectorAll(
            "[data-ef-action]"
        )
        .forEach(
            element => {

                element.addEventListener(
                    "click",
                    () => {

                        const action =
                            element.dataset.efAction;


                        showToast(
                            messages[action] ||
                            "Recurso preparado para integração."
                        );

                    }
                );

            }
        );


    /* EDUCATION DASHBOARD V3 START */


    /* ======================================================
       IDIOMA
       ====================================================== */

    const LANGUAGE_KEY =
        "sabinoa_ui_language";


    const languageSelect =
        document.getElementById(
            "ef2-language"
        );


    const savedLanguage =
        localStorage.getItem(
            LANGUAGE_KEY
        ) || "pt-BR";


    if (languageSelect) {

        languageSelect.value =
            savedLanguage;


        languageSelect.addEventListener(
            "change",
            () => {

                localStorage.setItem(
                    LANGUAGE_KEY,
                    languageSelect.value
                );


                showToast(
                    languageSelect.value === "pt-BR"
                        ? "Português (Brasil) selecionado."
                        : "Idioma salvo. A tradução completa desta tela será habilitada na etapa de internacionalização."
                );

            }
        );

    }


    /* ======================================================
       FILTRO DE PERIODO
       ====================================================== */

    let activePeriod =
        "30d";


    document
        .querySelectorAll(
            "[data-period]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        document
                            .querySelectorAll(
                                "[data-period]"
                            )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "active"
                                    )
                            );


                        button.classList.add(
                            "active"
                        );


                        activePeriod =
                            button.dataset.period;


                        updateLastRefresh();


                        showToast(
                            activePeriod === "custom"
                                ? "O período personalizado será conectado ao seletor de datas."
                                : `Período alterado para ${button.textContent.trim()}.`
                        );

                    }
                );

            }
        );


    /* ======================================================
       ULTIMA ATUALIZACAO
       ====================================================== */

    function updateLastRefresh() {

        const element =
            document.getElementById(
                "ef3-last-update"
            );


        if (!element) {
            return;
        }


        const now =
            new Date();


        element.textContent =
            `às ${
                now.toLocaleTimeString(
                    "pt-BR",
                    {
                        hour:
                            "2-digit",

                        minute:
                            "2-digit",

                        second:
                            "2-digit"
                    }
                )
            }`;

    }


    updateLastRefresh();


    document
        .getElementById(
            "ef3-refresh"
        )
        ?.addEventListener(
            "click",
            () => {

                updateLastRefresh();


                showToast(
                    "Indicadores atualizados."
                );

            }
        );


    /* ======================================================
       DRILL-DOWN
       ====================================================== */

    const drilldownMessages = {

        risk:
            "Abrindo detalhamento dos usuários por nível de risco.",

        goals:
            "Abrindo detalhamento das metas financeiras.",

        rag:
            "Abrindo detalhamento da base de conhecimento.",

        hitl:
            "Abrindo fila de revisão humana.",

        diagnostics:
            "Abrindo histórico completo de diagnósticos.",

        integrations:
            "Abrindo estado das integrações."

    };


    document
        .querySelectorAll(
            "[data-ef-drilldown]"
        )
        .forEach(
            element => {

                element.addEventListener(
                    "click",
                    () => {

                        const type =
                            element.dataset
                                .efDrilldown;


                        showToast(
                            drilldownMessages[type] ||
                            "Detalhamento preparado para integração."
                        );

                    }
                );

            }
        );


    /* ======================================================
       CARDS OPERACIONAIS COMO DRILL-DOWN
       ====================================================== */

    document
        .querySelectorAll(
            ".ef2-live-card"
        )
        .forEach(
            card => {

                card.tabIndex =
                    0;


                card.addEventListener(
                    "click",
                    () => {

                        const title =
                            card
                                .querySelector(
                                    "small"
                                )
                                ?.textContent
                                ?.trim() ||
                                "indicador";


                        showToast(
                            `Detalhamento de ${title} será aberto nesta área.`
                        );

                    }
                );

            }
        );


    /* ======================================================
       SAUDE
       ====================================================== */

    const healthComponents = {

        api:
            100,

        database:
            100,

        rag:
            100,

        inna:
            98,

        integrations:
            100,

        hitl:
            82,

        errors:
            94

    };


    const healthValues =
        Object.values(
            healthComponents
        );


    const calculatedHealth =
        Math.round(
            healthValues.reduce(
                (sum, value) =>
                    sum + value,
                0
            ) /
            healthValues.length
        );


    document
        .querySelector(
            ".ef2-health-ring strong"
        )
        ?.replaceChildren(
            document.createTextNode(
                `${calculatedHealth}%`
            )
        );


    /* ======================================================
       RELATORIO DEMONSTRATIVO
       ====================================================== */

    document
        .querySelectorAll(
            '[data-ef-action="report"]'
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        const report = [
                            "SABINO.AI - EDUCAÇÃO FINANCEIRA",
                            "",
                            `Período: ${activePeriod}`,
                            `Saúde operacional: ${calculatedHealth}%`,
                            "Usuários atendidos: 84",
                            "Diagnósticos: 342",
                            "Alertas de risco: 18",
                            "Metas financeiras: 126",
                            "Consultas INNA: 519",
                            `RAG: ${rag}`,
                            `Integrações: ${integrations.length}`,
                            "",
                            "Documento demonstrativo."
                        ].join("\n");


                        const blob =
                            new Blob(
                                [report],
                                {
                                    type:
                                        "text/plain;charset=utf-8"
                                }
                            );


                        const url =
                            URL.createObjectURL(
                                blob
                            );


                        const anchor =
                            document.createElement(
                                "a"
                            );


                        anchor.href =
                            url;


                        anchor.download =
                            "educacao-financeira-relatorio-demo.txt";


                        anchor.click();


                        URL.revokeObjectURL(
                            url
                        );


                        showToast(
                            "Relatório demonstrativo gerado."
                        );

                    }
                );

            }
        );


    /* ======================================================
       NOVAS ACOES
       ====================================================== */

    document
        .querySelectorAll(
            '[data-ef-action="health"]'
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        showToast(
                            "Saúde calculada a partir de API, banco, RAG, INNA, integrações, HITL e taxa de erros."
                        );

                    }
                );

            }
        );


    document
        .querySelectorAll(
            '[data-ef-action="inna-recommendations"]'
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        showToast(
                            "A INNA contextual será conectada às recomendações reais na integração do módulo."
                        );

                    }
                );

            }
        );


    /* EDUCATION DASHBOARD V3 END */

    /* EDUCATION MULTIVIEW JS V1 START */

    const educationAllowedViews =
        new Set([
            "overview",
            "operational",
            "analytics",
            "intelligence"
        ]);


    const educationViewLabels = {

        overview:
            "Visão Geral",

        operational:
            "Operacional",

        analytics:
            "Analítica",

        intelligence:
            "Inteligência INNA"

    };


    function setEducationView(
        requestedView,
        updateUrl = true
    ) {

        const view =
            educationAllowedViews.has(
                requestedView
            )
                ? requestedView
                : "overview";


        document
            .querySelectorAll(
                "[data-view-section]"
            )
            .forEach(
                section => {

                    section.hidden =
                        section.dataset.viewSection !== view;

                }
            );


        document
            .querySelectorAll(
                "[data-module-view]"
            )
            .forEach(
                button => {

                    button.classList.toggle(
                        "active",
                        button.dataset.moduleView === view
                    );

                    button.setAttribute(
                        "aria-pressed",
                        button.dataset.moduleView === view
                            ? "true"
                            : "false"
                    );

                }
            );


        const title =
            document.getElementById(
                "education-view-title"
            );


        if (title) {

            title.textContent =
                educationViewLabels[view];

        }


        localStorage.setItem(
            "sabino_education_dashboard_view",
            view
        );


        if (updateUrl) {

            const url =
                new URL(
                    window.location.href
                );


            url.searchParams.set(
                "view",
                view
            );


            window.history.replaceState(
                {
                    moduleView:
                        view
                },
                "",
                url
            );

        }

    }


    document
        .querySelectorAll(
            "[data-module-view]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        setEducationView(
                            button.dataset.moduleView
                        );

                    }
                );

            }
        );


    document
        .querySelectorAll(
            "[data-open-view]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        setEducationView(
                            button.dataset.openView
                        );


                        document
                            .querySelector(
                                ".module-view-controller"
                            )
                            ?.scrollIntoView({
                                behavior:
                                    "smooth",

                                block:
                                    "start"
                            });

                    }
                );

            }
        );


    const educationInitialUrl =
        new URL(
            window.location.href
        );


    const educationUrlView =
        educationInitialUrl.searchParams.get(
            "view"
        );


    const educationSavedView =
        localStorage.getItem(
            "sabino_education_dashboard_view"
        );


    const educationInitialView =
        educationAllowedViews.has(
            educationUrlView
        )
            ? educationUrlView
            : (
                educationAllowedViews.has(
                    educationSavedView
                )
                    ? educationSavedView
                    : "overview"
            );


    setEducationView(
        educationInitialView,
        true
    );


    /* idioma - fallback caso V3 ainda nao esteja aplicado */

    const educationLanguage =
        document.getElementById(
            "ef2-language"
        );


    if (educationLanguage) {

        const educationLanguageKey =
            "sabinoa_ui_language";


        const educationSavedLanguage =
            localStorage.getItem(
                educationLanguageKey
            ) || "pt-BR";


        educationLanguage.value =
            educationSavedLanguage;


        educationLanguage.addEventListener(
            "change",
            () => {

                localStorage.setItem(
                    educationLanguageKey,
                    educationLanguage.value
                );

            }
        );

    }

    /* EDUCATION MULTIVIEW JS V1 END */

    /* EDUCATION INNA INTELLIGENCE JS V1 START */

    const educationIntelMessages = {

        "education-recommendation":
            "A INNA prescritiva será conectada aos dados reais e às políticas de governança do módulo.",

        "education-explainability":
            "A explicação detalhada mostrará evidências, contexto, RAG, confiança e revisão humana.",

        "education-chat":
            "A conversa especializada da INNA receberá o contexto da Educação Financeira na integração."

    };


    document
        .querySelectorAll(
            "[data-inna-intel-action]"
        )
        .forEach(
            element => {

                element.addEventListener(
                    "click",
                    () => {

                        const action =
                            element.dataset
                                .innaIntelAction;


                        if (
                            educationIntelMessages[
                                action
                            ]
                        ) {

                            showToast(
                                educationIntelMessages[
                                    action
                                ]
                            );

                        }

                    }
                );

            }
        );

    /* EDUCATION INNA INTELLIGENCE JS V1 END */
});



