document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    console.log(
        "SABINO_SECURITY_DASHBOARD_V1=LOADED"
    );


    /* ======================================================
       GATE
       ====================================================== */

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


    /* ======================================================
       HELPERS
       ====================================================== */

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


    const integrationElement =
        document.getElementById(
            "sf-integrations"
        );


    if (integrationElement) {

        integrationElement.textContent =
            integrations.length
                ? `${integrations.length}/${integrations.length}`
                : "0/0";

    }


    /* ======================================================
       IDIOMA
       ====================================================== */

    const LANGUAGE_KEY =
        "sabinoa_ui_language";


    const languageSelect =
        document.getElementById(
            "sf-language"
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
                        : "Idioma salvo. Tradução completa será conectada na etapa de internacionalização."
                );

            }
        );

    }


    /* ======================================================
       TOAST
       ====================================================== */

    const toast =
        document.getElementById(
            "sf-toast"
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


    /* ======================================================
       PERIODO
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
                                ? "Período personalizado preparado para integração."
                                : `Período alterado para ${button.textContent.trim()}.`
                        );

                    }
                );

            }
        );


    /* ======================================================
       UPDATE
       ====================================================== */

    function updateLastRefresh() {

        const element =
            document.getElementById(
                "sf-last-update"
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
            "sf-refresh"
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
       SAUDE EXPLICAVEL
       ====================================================== */

    const healthComponents = {

        monitoring:
            100,

        rules:
            100,

        events:
            99,

        integrations:
            100,

        alerts:
            92,

        hitl:
            89,

        errors:
            98

    };


    const values =
        Object.values(
            healthComponents
        );


    const health =
        Math.round(
            values.reduce(
                (sum, value) =>
                    sum + value,
                0
            )
            /
            values.length
        );


    const healthElement =
        document.getElementById(
            "sf-health"
        );


    if (healthElement) {

        healthElement.textContent =
            `${health}%`;

    }


    /* ======================================================
       RELATORIO DEMO
       ====================================================== */

    function generateReport() {

        const content = [
            "SABINO.AI - SEGURANÇA FINANCEIRA",
            "",
            `Período: ${activePeriod}`,
            `Saúde operacional: ${health}%`,
            "Eventos monitorados: 12.840",
            "Alertas detectados: 184",
            "Alertas ativos: 27",
            "Incidentes críticos: 3",
            "Casos HITL pendentes: 4",
            "Regras ativas: 24",
            `Integrações: ${integrations.length}`,
            "",
            "Documento demonstrativo."
        ].join("\n");


        const blob =
            new Blob(
                [content],
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
            "seguranca-financeira-relatorio-demo.txt";


        anchor.click();


        URL.revokeObjectURL(
            url
        );


        showToast(
            "Relatório demonstrativo gerado."
        );

    }


    /* ======================================================
       ACOES
       ====================================================== */

    const messages = {

        inna:
            "A INNA será conectada aos eventos e alertas reais deste módulo.",

        health:
            "Saúde calculada a partir de monitoramento, regras, eventos, integrações, alertas, HITL e taxa de erros.",

        recommendations:
            "Recomendações reais serão produzidas pela INNA após integração com os dados do módulo.",

        incidents:
            "Abrindo visão detalhada dos incidentes críticos.",

        hitl:
            "Abrindo fila de revisão humana.",

        monitoring:
            "Abrindo estado detalhado do monitoramento.",

        cases:
            "Histórico completo de casos será conectado ao backend.",

        audit:
            "Auditoria será conectada aos logs e eventos reais."

    };


    document
        .querySelectorAll(
            "[data-sf-action]"
        )
        .forEach(
            element => {

                element.addEventListener(
                    "click",
                    () => {

                        const action =
                            element.dataset.sfAction;


                        if (action === "report") {

                            generateReport();

                            return;

                        }


                        showToast(
                            messages[action] ||
                            "Recurso preparado para integração."
                        );

                    }
                );

            }
        );


    /* ======================================================
       DRILL-DOWN NOS CARDS
       ====================================================== */

    document
        .querySelectorAll(
            ".sf-live-card"
        )
        .forEach(
            card => {

                card.tabIndex =
                    0;


                card.addEventListener(
                    "click",
                    () => {

                        const metric =
                            card
                                .querySelector(
                                    "small"
                                )
                                ?.textContent
                                ?.trim() ||
                                "indicador";


                        showToast(
                            `Detalhamento de ${metric} preparado para integração.`
                        );

                    }
                );

            }
        );


    /* SECURITY MULTIVIEW JS V1 START */

    const securityAllowedViews =
        new Set([
            "overview",
            "operational",
            "analytics",
            "intelligence"
        ]);


    const securityViewLabels = {

        overview:
            "Visão Geral",

        operational:
            "Operacional",

        analytics:
            "Analítica",

        intelligence:
            "Inteligência INNA"

    };


    function setSecurityView(
        requestedView,
        updateUrl = true
    ) {

        const view =
            securityAllowedViews.has(
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
                "security-view-title"
            );


        if (title) {

            title.textContent =
                securityViewLabels[view];

        }


        localStorage.setItem(
            "sabino_security_dashboard_view",
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

                        setSecurityView(
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

                        setSecurityView(
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


    const securityInitialUrl =
        new URL(
            window.location.href
        );


    const securityUrlView =
        securityInitialUrl.searchParams.get(
            "view"
        );


    const securitySavedView =
        localStorage.getItem(
            "sabino_security_dashboard_view"
        );


    const securityInitialView =
        securityAllowedViews.has(
            securityUrlView
        )
            ? securityUrlView
            : (
                securityAllowedViews.has(
                    securitySavedView
                )
                    ? securitySavedView
                    : "overview"
            );


    setSecurityView(
        securityInitialView,
        true
    );

    /* SECURITY MULTIVIEW JS V1 END */

    /* SECURITY INNA INTELLIGENCE JS V1 START */

    const securityIntelMessages = {

        "security-recommendation":
            "A INNA prescritiva será conectada aos eventos reais, regras e políticas autorizadas.",

        "security-explainability":
            "A futura trilha mostrará evento, regra, contexto, confiança, análise da INNA e revisão HITL.",

        "security-chat":
            "A conversa especializada receberá o contexto autorizado da Segurança Financeira."

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
                            securityIntelMessages[
                                action
                            ]
                        ) {

                            showToast(
                                securityIntelMessages[
                                    action
                                ]
                            );

                        }

                    }
                );

            }
        );

    /* SECURITY INNA INTELLIGENCE JS V1 END */
});


