document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        const storageKey =
            "sabino_financial_platform_view";


        const endpoint =
            "/api/platform/finance/dashboard";


        const allowedViews = [
            "overview",
            "operational",
            "analytics",
            "intelligence"
        ];


        const toast =
            document.getElementById(
                "finance-toast"
            );


        const fallbackData = {

            summary: {

                health: 96,
                active_modules: 2,
                users: 2840,
                alerts: 34,
                hitl: 7,
                rag_queries: 18420

            }

        };


        function formatNumber(value) {

            return new Intl.NumberFormat(
                "pt-BR"
            ).format(
                value ?? 0
            );

        }


        function setText(
            id,
            value
        ) {

            const element =
                document.getElementById(
                    id
                );


            if (element) {

                element.textContent =
                    value;

            }

        }


        function notify(message) {

            if (!toast) {
                return;
            }


            toast.textContent =
                message;


            toast.classList.add(
                "show"
            );


            clearTimeout(
                toast._timer
            );


            toast._timer =
                setTimeout(
                    () => {

                        toast.classList.remove(
                            "show"
                        );

                    },
                    2600
                );

        }


        function renderSummary(data) {

            const summary =
                data?.summary
                ??
                fallbackData.summary;


            setText(
                "kpi-health",
                `${summary.health ?? 96}%`
            );


            setText(
                "kpi-modules",
                summary.active_modules ?? 2
            );


            setText(
                "kpi-users",
                formatNumber(
                    summary.users ?? 2840
                )
            );


            setText(
                "kpi-alerts",
                summary.alerts ?? 34
            );


            setText(
                "kpi-hitl",
                summary.hitl ?? 7
            );


            setText(
                "kpi-rag",
                formatNumber(
                    summary.rag_queries ?? 18420
                )
            );

        }


        function setView(
            requested,
            updateUrl = true
        ) {

            const view =
                allowedViews.includes(
                    requested
                )
                    ? requested
                    : "overview";


            document
                .querySelectorAll(
                    "[data-finance-view]"
                )
                .forEach(
                    button => {

                        button.classList.toggle(
                            "active",
                            button.dataset.financeView === view
                        );

                    }
                );


            document
                .querySelectorAll(
                    "[data-finance-panel]"
                )
                .forEach(
                    panel => {

                        panel.classList.toggle(
                            "active",
                            panel.dataset.financePanel === view
                        );

                    }
                );


            localStorage.setItem(
                storageKey,
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


                history.replaceState(
                    {},
                    "",
                    url
                );

            }

        }


        async function loadData(
            showToast = false
        ) {

            try {

                const response =
                    await fetch(
                        endpoint,
                        {
                            cache:
                                "no-store"
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        `HTTP ${response.status}`
                    );

                }


                const data =
                    await response.json();


                renderSummary(
                    data
                );


                setText(
                    "finance-source",
                    data.demo
                        ? "API demonstrativa"
                        : "Dados operacionais"
                );


                setText(
                    "finance-sync",
                    new Date()
                        .toLocaleTimeString(
                            "pt-BR"
                        )
                );


                if (showToast) {

                    notify(
                        "Plataforma Financeira sincronizada."
                    );

                }

            }
            catch (error) {

                console.warn(
                    "FINANCE_API_FALLBACK",
                    error
                );


                renderSummary(
                    fallbackData
                );


                setText(
                    "finance-source",
                    "Dados demonstrativos locais"
                );


                setText(
                    "finance-sync",
                    new Date()
                        .toLocaleTimeString(
                            "pt-BR"
                        )
                );


                if (showToast) {

                    notify(
                        "Dashboard atualizado com dados demonstrativos."
                    );

                }

            }

        }


        document
            .querySelectorAll(
                "[data-finance-view]"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            setView(
                                button.dataset.financeView
                            );

                        }
                    );

                }
            );


        document
            .querySelectorAll(
                "[data-finance-view-target]"
            )
            .forEach(
                element => {

                    element.addEventListener(
                        "click",
                        () => {

                            setView(
                                element.dataset.financeViewTarget
                            );


                            window.scrollTo(
                                {
                                    top:
                                        0,

                                    behavior:
                                        "smooth"
                                }
                            );

                        }
                    );

                }
            );


        document
            .querySelectorAll(
                "[data-finance-toast]"
            )
            .forEach(
                element => {

                    element.addEventListener(
                        "click",
                        () => {

                            notify(
                                element.dataset.financeToast
                            );

                        }
                    );

                }
            );


        document
            .querySelectorAll(
                ".finance-recommendations button"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            setView(
                                "intelligence"
                            );

                            notify(
                                "Recomendação aberta na Inteligência INNA."
                            );

                        }
                    );

                }
            );


        document
            .getElementById(
                "finance-open-inna"
            )
            ?.addEventListener(
                "click",
                () => {

                    setView(
                        "intelligence"
                    );


                    notify(
                        "Inteligência INNA aberta para a Plataforma Financeira."
                    );

                }
            );


        document
            .getElementById(
                "finance-refresh"
            )
            ?.addEventListener(
                "click",
                () => {

                    loadData(
                        true
                    );

                }
            );


        const params =
            new URLSearchParams(
                window.location.search
            );


        const requested =
            params.get(
                "view"
            )
            ||
            localStorage.getItem(
                storageKey
            )
            ||
            "overview";


        setView(
            requested,
            false
        );


        loadData();


        console.log(
            "SABINO_FINANCIAL_PLATFORM_V4=READY"
        );

    }
);
