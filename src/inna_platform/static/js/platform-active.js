document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    console.log("SABINO_PLATFORM_ACTIVE_V2=LOADED");


    /* ======================================================
       GATE DA PLATAFORMA
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


    function firstValue(...values) {

        return values.find(
            value =>
                value !== undefined &&
                value !== null &&
                value !== ""
        );

    }


    function labelFrom(value, fallback = "-") {

        if (
            value === undefined ||
            value === null ||
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


        return firstValue(
            value.label,
            value.name,
            value.value,
            fallback
        );

    }


    function setText(id, value) {

        const element =
            document.getElementById(id);

        if (element) {
            element.textContent = value;
        }

    }


    function formatDate(date) {

        if (
            !(date instanceof Date) ||
            Number.isNaN(date.getTime())
        ) {
            return "-";
        }


        return new Intl.DateTimeFormat(
            "pt-BR"
        ).format(date);

    }


    function parseDate(value) {

        if (!value) {
            return null;
        }


        const parsed =
            new Date(value);


        return Number.isNaN(
            parsed.getTime()
        )
            ? null
            : parsed;

    }


    function addDays(date, days) {

        const result =
            new Date(date);

        result.setDate(
            result.getDate() + days
        );

        return result;

    }


    /* ======================================================
       DADOS
       ====================================================== */

    const config =
        readJson(
            "inna_solution_config"
        );


    const proposal =
        readJson(
            "inna_final_proposal"
        );


    const contract =
        readJson(
            "inna_contract"
        );


    const modules =
        Array.isArray(config.modules)
            ? config.modules
            : [];


    const channels =
        Array.isArray(config.channels)
            ? config.channels
            : [];


    const integrations =
        Array.isArray(config.integrations)
            ? config.integrations
            : [];


    const resources =
        Array.isArray(config.resources)
            ? config.resources
            : [];


    const activatedAt =
        parseDate(
            localStorage.getItem(
                "inna_platform_activated_at"
            )
        ) ||
        parseDate(
            contract.acceptedAt
        ) ||
        new Date();


    const nextReview =
        addDays(
            activatedAt,
            30
        );


    const plan =
        firstValue(
            config?.recommendedPlan?.name,
            proposal?.plan?.name,
            proposal?.recommendedPlan,
            contract?.plan,
            "Business"
        );


    const users =
        labelFrom(
            firstValue(
                config.users,
                config.userRange,
                config.capacity?.users
            ),
            "-"
        );


    const rag =
        labelFrom(
            firstValue(
                config.rag,
                config.ragBase,
                config.capacity?.rag
            ),
            "-"
        );


    /* ======================================================
       PREENCHIMENTO
       ====================================================== */

    setText(
        "pa-active-since",
        `Desde ${formatDate(activatedAt)}`
    );


    setText(
        "pa-module-count-top",
        `${modules.length || 0} módulos`
    );


    setText(
        "pa-next-review",
        formatDate(nextReview)
    );


    setText(
        "pa-kpi-modules",
        String(modules.length || 0)
    );


    setText(
        "pa-kpi-users",
        users
    );


    setText(
        "pa-kpi-rag",
        rag
    );


    setText(
        "pa-kpi-integrations",
        String(integrations.length || 0)
    );


    const rangeStart =
        new Date();


    const rangeEnd =
        addDays(
            rangeStart,
            30
        );


    setText(
        "pa-date-range",
        `${formatDate(rangeStart)} → ${formatDate(rangeEnd)}`
    );


    /* ======================================================
       GRAFICO DE MODULOS
       ====================================================== */

    const moduleLegend =
        document.getElementById(
            "pa-module-legend"
        );


    const donut =
        document.getElementById(
            "pa-module-donut"
        );


    const displayModules =
        modules.length
            ? modules.slice(0, 5)
            : [
                "Educação Financeira",
                "Segurança Financeira",
                "Reembolso Inteligente"
            ];


    const palette = [
        "#87c83f",
        "#8264db",
        "#32a9c8",
        "#e3a72f",
        "#4eb989"
    ];


    const weights = [];

    let remaining =
        100;


    displayModules.forEach(
        (module, index) => {

            let value;

            if (
                index ===
                displayModules.length - 1
            ) {

                value =
                    remaining;

            }
            else {

                value =
                    Math.max(
                        12,
                        Math.round(
                            100 /
                            displayModules.length
                        )
                    );

                remaining -=
                    value;

            }


            weights.push(
                Math.max(
                    0,
                    value
                )
            );

        }
    );


    if (weights.length) {

        const total =
            weights.reduce(
                (sum, value) =>
                    sum + value,
                0
            );


        const normalized =
            weights.map(
                value =>
                    Math.round(
                        value /
                        total *
                        100
                    )
            );


        const diff =
            100 -
            normalized.reduce(
                (sum, value) =>
                    sum + value,
                0
            );


        normalized[
            normalized.length - 1
        ] += diff;


        let cursor =
            0;


        const segments =
            normalized.map(
                (value, index) => {

                    const start =
                        cursor;

                    const end =
                        cursor + value;

                    cursor =
                        end;


                    return `${palette[index]} ${start}% ${end}%`;

                }
            );


        if (donut) {

            donut.style.background =
                `conic-gradient(${segments.join(",")})`;

        }


        if (moduleLegend) {

            moduleLegend.innerHTML =
                "";


            displayModules.forEach(
                (module, index) => {

                    const row =
                        document.createElement(
                            "div"
                        );


                    row.innerHTML = `
                        <span
                            class="pa-legend-dot"
                            style="background:${palette[index]}"
                        ></span>

                        <strong>
                            ${escapeHtml(module)}
                        </strong>

                        <em>
                            ${normalized[index]}%
                        </em>
                    `;


                    moduleLegend.appendChild(
                        row
                    );

                }
            );

        }

    }


    function escapeHtml(value) {

        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");

    }


    /* ======================================================
       TOAST / ACOES
       ====================================================== */

    const toast =
        document.getElementById(
            "pa-toast"
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
            "INNA Assistant: integração da conversa será conectada ao backend na próxima etapa.",

        resources:
            "Recursos da plataforma disponíveis nesta central.",

        company:
            "Área da empresa preparada para evolução com conta corporativa.",

        language:
            "A plataforma está preparada para evolução multilíngue.",

        theme:
            "Aparência premium Sabino.AI ativa.",

        account:
            "A área Minha conta será conectada ao sistema de autenticação.",

        customize:
            "Personalização do dashboard será habilitada em uma próxima evolução.",

        support:
            "Central de ajuda preparada para integração.",

        tutorials:
            "Biblioteca de tutoriais será conectada nesta área.",

        docs:
            "Documentação técnica será disponibilizada nesta central.",

        updates:
            "Área de novidades da plataforma preparada.",

        training:
            "Treinamento e onboarding preparados para integração.",

        webinar:
            "Agenda de eventos poderá ser conectada aqui.",

        team:
            "Gestão de usuários e convites será conectada ao backend.",

        integrations:
            "Gerenciamento de integrações preparado para evolução.",

        rag:
            "Gerenciamento da base RAG será integrado ao módulo de conhecimento.",

        automations:
            "Central de automações preparada para evolução.",

        activity:
            "Histórico completo será conectado à trilha de auditoria.",

        status:
            "Monitoramento operacional será conectado à observabilidade."

    };


    document
        .querySelectorAll(
            "[data-platform-action]"
        )
        .forEach(
            element => {

                element.addEventListener(
                    "click",
                    () => {

                        const action =
                            element.dataset
                                .platformAction;


                        if (
                            action ===
                            "dashboard"
                        ) {

                            document
                                .getElementById(
                                    "pa-dashboard"
                                )
                                ?.scrollIntoView({
                                    behavior:
                                        "smooth",
                                    block:
                                        "start"
                                });

                            return;

                        }


                        showToast(
                            messages[action] ||
                            "Recurso preparado para evolução."
                        );

                    }
                );

            }
        );


    /* ======================================================
       INFO DEBUG
       ====================================================== */

    console.log(
        "PLATFORM_PLAN=",
        plan
    );

    console.log(
        "PLATFORM_MODULES=",
        modules.length
    );

    console.log(
        "PLATFORM_CHANNELS=",
        channels.length
    );

    console.log(
        "PLATFORM_INTEGRATIONS=",
        integrations.length
    );

    console.log(
        "PLATFORM_RESOURCES=",
        resources.length
    );

});
