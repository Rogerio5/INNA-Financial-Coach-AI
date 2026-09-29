document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    console.log("SABINO_CONFIGURATOR_V9=LOADED");


    /* ======================================================
       ELEMENTOS
       ====================================================== */

    const options = Array.from(
        document.querySelectorAll(".config-option")
    );

    const users =
        document.getElementById("users-config");

    const data =
        document.getElementById("data-config");

    const rag =
        document.getElementById("rag-config");

    const ragUpdate =
        document.getElementById("rag-update-config");

    const reviewButton =
        document.getElementById("review-config");

    const validationMessage =
        document.getElementById(
            "config-validation-message"
        );


    const modules = [
        "Educação Financeira",
        "Segurança Financeira",
        "Reembolso Inteligente"
    ];


    /* ======================================================
       TODOS OS CARDS DEVEM SER CLICAVEIS
       ====================================================== */

    options.forEach((option) => {

        option.disabled = false;

        option.removeAttribute("disabled");

        option.setAttribute(
            "type",
            "button"
        );

        option.setAttribute(
            "aria-pressed",
            option.classList.contains("selected")
                ? "true"
                : "false"
        );

    });


    /* ======================================================
       COMPLEXIDADE
       ====================================================== */

    const complexityWeights = {

        channels: {
            "Web App": 0.5,
            "WhatsApp": 1,
            "Telegram": 0.5,
            "E-mail": 0.5,
            "Chat online": 1
        },

        integrations: {
            "API REST": 1.5,
            "ERP": 2,
            "CRM": 1.5,
            "SSO / Login": 2,
            "Banco de Dados": 2,
            "MCP / Webhooks": 2.5
        },

        resources: {
            "Observabilidade": 1,
            "Governança & LGPD": 1.5,
            "Dashboards": 1,
            "Automação": 1.5,
            "Alertas": 0.5
        }

    };


    /* ======================================================
       PRECOS DEMONSTRATIVOS
       ====================================================== */

    const prices = {

        channels: {
            "Web App": 80,
            "WhatsApp": 180,
            "Telegram": 80,
            "E-mail": 60,
            "Chat online": 120
        },

        integrations: {
            "API REST": 180,
            "ERP": 320,
            "CRM": 250,
            "SSO / Login": 280,
            "Banco de Dados": 300,
            "MCP / Webhooks": 360
        },

        resources: {
            "Observabilidade": 140,
            "Governança & LGPD": 180,
            "Dashboards": 120,
            "Automação": 200,
            "Alertas": 80
        }

    };


    const plans = {

        starter: {
            name: "Starter",
            base: 1490,
            includedModules: 1,

            credits: {
                channels: 100,
                integrations: 180,
                resources: 140
            }
        },

        business: {
            name: "Business",
            base: 3490,
            includedModules: 3,

            credits: {
                channels: 240,
                integrations: 600,
                resources: 300
            }
        },

        enterprise: {
            name: "Enterprise",
            base: null,
            includedModules: 999,

            credits: {
                channels: 999999,
                integrations: 999999,
                resources: 999999
            }
        }

    };


    /* ======================================================
       HELPERS
       ====================================================== */

    function selectedValues(group) {

        return options
            .filter(
                option =>
                    option.dataset.group === group &&
                    option.classList.contains("selected")
            )
            .map(
                option =>
                    option.dataset.value
            );

    }


    function sum(values, table) {

        return values.reduce(
            (total, value) =>
                total + (table[value] || 0),
            0
        );

    }


    function formatBRL(value) {

        return new Intl.NumberFormat(
            "pt-BR",
            {
                style: "currency",
                currency: "BRL",
                maximumFractionDigits: 0
            }
        ).format(value);

    }


    function setText(id, text) {

        const element =
            document.getElementById(id);

        if (element) {
            element.textContent = text;
        }

    }


    function setMoney(id, value) {

        setText(
            id,
            value === null
                ? "Sob consulta"
                : formatBRL(value)
        );

    }


    function selectedLabel(field) {

        return field
            ?.selectedOptions?.[0]
            ?.textContent
            ?.trim() || "";

    }


    /* ======================================================
       SCORE DE USUARIOS
       ====================================================== */

    function usersScore() {

        return ({
            "1-10": 0,
            "11-50": 1,
            "51-100": 2,
            "101-500": 4,
            "501-1000": 7,
            "1001-5000": 10,
            "5000+": 14
        })[users?.value] || 0;

    }


    /* ======================================================
       PRECO DE USUARIOS
       ====================================================== */

    function usersPrice() {

        return ({
            "1-10": 0,
            "11-50": 150,
            "51-100": 300,
            "101-500": 650,
            "501-1000": 1400,
            "1001-5000": 0,
            "5000+": 0
        })[users?.value] || 0;

    }


    /* ======================================================
       VOLUME DE DADOS
       ====================================================== */

    function dataScore() {

        return ({
            "0-10": 0,
            "11-100": 2,
            "101-500": 4,
            "501-1000": 6,
            "1-5tb": 9,
            "5tb+": 12
        })[data?.value] || 0;

    }


    function dataPrice() {

        return ({
            "0-10": 0,
            "11-100": 200,
            "101-500": 400,
            "501-1000": 800,
            "1-5tb": 0,
            "5tb+": 0
        })[data?.value] || 0;

    }


    /* ======================================================
       BASE RAG
       ====================================================== */

    function ragScore() {

        return ({
            "0-5000": 0,
            "5001-50000": 2,
            "50001-250000": 4,
            "250001-1000000": 7,
            "1000000+": 10
        })[rag?.value] || 0;

    }


    function ragPrice() {

        return ({
            "0-5000": 0,
            "5001-50000": 150,
            "50001-250000": 400,
            "250001-1000000": 900,
            "1000000+": 0
        })[rag?.value] || 0;

    }


    /* ======================================================
       ATUALIZACAO RAG
       ====================================================== */

    function ragUpdateScore() {

        return ({
            "on-demand": 0,
            "weekly": 1,
            "daily": 2,
            "continuous": 4
        })[ragUpdate?.value] || 0;

    }


    function ragUpdatePrice() {

        return ({
            "on-demand": 0,
            "weekly": 100,
            "daily": 250,
            "continuous": 600
        })[ragUpdate?.value] || 0;

    }


    /* ======================================================
       ENTERPRISE
       ====================================================== */

    function requiresEnterprise(integrations) {

        if (
            users?.value === "1001-5000" ||
            users?.value === "5000+"
        ) {
            return true;
        }


        if (
            data?.value === "1-5tb" ||
            data?.value === "5tb+"
        ) {
            return true;
        }


        if (
            rag?.value === "1000000+"
        ) {
            return true;
        }


        if (
            rag?.value === "250001-1000000" &&
            ragUpdate?.value === "continuous"
        ) {
            return true;
        }


        const advanced =
            integrations.includes("SSO / Login") &&
            integrations.includes("MCP / Webhooks");


        if (
            users?.value === "501-1000" &&
            advanced &&
            integrations.length >= 4
        ) {
            return true;
        }


        return false;

    }


    /* ======================================================
       CALCULO DA SOLUCAO
       ====================================================== */

    function calculateSolution() {

        const channels =
            selectedValues("channel");

        const integrations =
            selectedValues("integration");

        const resources =
            selectedValues("resource");


        const score =
            modules.length +

            sum(
                channels,
                complexityWeights.channels
            ) +

            sum(
                integrations,
                complexityWeights.integrations
            ) +

            sum(
                resources,
                complexityWeights.resources
            ) +

            usersScore() +
            dataScore() +
            ragScore() +
            ragUpdateScore();


        const forcedEnterprise =
            requiresEnterprise(
                integrations
            );


        const starterCapacity =
            ["1-10", "11-50"]
                .includes(users?.value) &&

            ["0-10", "11-100"]
                .includes(data?.value) &&

            ["0-5000", "5001-50000"]
                .includes(rag?.value) &&

            (
                !ragUpdate ||
                ["on-demand", "weekly"]
                    .includes(ragUpdate.value)
            );


        let planId;
        let complexity;


        if (
            score <= 11 &&
            starterCapacity &&
            !forcedEnterprise
        ) {

            planId = "starter";

            complexity = {
                id: "low",
                name: "Baixa",
                label: "BAIXA"
            };

        }

        else if (
            score <= 32 &&
            !forcedEnterprise
        ) {

            planId = "business";

            complexity = {
                id: "medium",
                name: "Média",
                label: "MÉDIA"
            };

        }

        else {

            planId = "enterprise";

            complexity = {
                id: "high",
                name: "Alta",
                label: "ALTA"
            };

        }


        return {

            score,
            planId,
            complexity,

            channels,
            integrations,
            resources,

            counts: {
                modules: modules.length,
                channels: channels.length,
                integrations: integrations.length,
                resources: resources.length
            }

        };

    }


    /* ======================================================
       CALCULO DO PRECO
       ====================================================== */

    function calculatePrice(solution) {

        const plan =
            plans[solution.planId];


        if (
            solution.planId === "enterprise"
        ) {

            return {
                base: null,
                modules: 0,
                channels: 0,
                integrations: 0,
                resources: 0,
                users: 0,
                data: 0,
                rag: 0,
                ragUpdate: 0,
                total: null,
                label: "Sob consulta"
            };

        }


        const modulesExtra =
            Math.max(
                0,
                modules.length -
                plan.includedModules
            ) * 250;


        const channelsExtra =
            Math.max(
                0,

                sum(
                    solution.channels,
                    prices.channels
                ) -
                plan.credits.channels
            );


        const integrationsExtra =
            Math.max(
                0,

                sum(
                    solution.integrations,
                    prices.integrations
                ) -
                plan.credits.integrations
            );


        const resourcesExtra =
            Math.max(
                0,

                sum(
                    solution.resources,
                    prices.resources
                ) -
                plan.credits.resources
            );


        const userExtra =
            usersPrice();


        const dataExtra =
            dataPrice();


        const ragExtra =
            ragPrice();


        const updateExtra =
            ragUpdatePrice();


        const total =
            plan.base +
            modulesExtra +
            channelsExtra +
            integrationsExtra +
            resourcesExtra +
            userExtra +
            dataExtra +
            ragExtra +
            updateExtra;


        return {

            base:
                plan.base,

            modules:
                modulesExtra,

            channels:
                channelsExtra,

            integrations:
                integrationsExtra,

            resources:
                resourcesExtra,

            users:
                userExtra,

            data:
                dataExtra,

            rag:
                ragExtra,

            ragUpdate:
                updateExtra,

            total,

            label:
                formatBRL(total) + "/mês"

        };

    }


    /* ======================================================
       TAGS
       ====================================================== */

    function renderTags(id, values) {

        const target =
            document.getElementById(id);

        if (!target) {
            return;
        }


        target.innerHTML = "";


        values.forEach((value) => {

            const tag =
                document.createElement("span");

            tag.className =
                "summary-tag";

            tag.textContent =
                value;

            target.appendChild(tag);

        });

    }


    function renderResources(values) {

        const target =
            document.getElementById(
                "summary-resources"
            );

        if (!target) {
            return;
        }


        target.innerHTML = "";


        values.forEach((value) => {

            const item =
                document.createElement("li");

            item.textContent =
                value;

            target.appendChild(item);

        });

    }


    /* ======================================================
       ATUALIZAR TUDO
       ====================================================== */

    function updateSummary() {

        const solution =
            calculateSolution();

        const price =
            calculatePrice(solution);


        renderTags(
            "summary-channels",
            solution.channels
        );


        renderTags(
            "summary-integrations",
            solution.integrations
        );


        renderResources(
            solution.resources
        );


        setText(
            "summary-users",
            selectedLabel(users)
        );


        setText(
            "summary-data",
            selectedLabel(data)
        );


        setText(
            "summary-rag",
            selectedLabel(rag)
        );


        if (ragUpdate) {

            setText(
                "summary-rag-update",
                selectedLabel(ragUpdate)
            );

        }


        setText(
            "summary-count-modules",
            solution.counts.modules
        );


        setText(
            "summary-count-channels",
            solution.counts.channels
        );


        setText(
            "summary-count-integrations",
            solution.counts.integrations
        );


        setText(
            "summary-count-resources",
            solution.counts.resources
        );


        setText(
            "summary-complexity-level",
            solution.complexity.name
        );


        const badge =
            document.getElementById(
                "summary-complexity-badge"
            );


        if (badge) {

            badge.textContent =
                solution.complexity.label;

            badge.dataset.level =
                solution.complexity.id;

        }


        setText(
            "summary-plan",
            plans[solution.planId].name
        );


        setMoney(
            "summary-price-base",
            price.base
        );


        setMoney(
            "summary-price-modules",
            price.modules
        );


        setMoney(
            "summary-price-channels",
            price.channels
        );


        setMoney(
            "summary-price-integrations",
            price.integrations
        );


        setMoney(
            "summary-price-resources",
            price.resources
        );


        setMoney(
            "summary-price-users",
            price.users
        );


        setMoney(
            "summary-price-data",
            price.data
        );


        setMoney(
            "summary-price-rag",
            price.rag
        );


        setMoney(
            "summary-price-rag-update",
            price.ragUpdate
        );


        setText(
            "summary-estimated-price",
            price.label
        );


        console.log(
            "CONFIG_UPDATE",
            {
                solution,
                price
            }
        );


        return {
            solution,
            price
        };

    }


    /* ======================================================
       CLIQUE NOS CARDS
       ====================================================== */

    options.forEach((option) => {

        option.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                option.classList.toggle(
                    "selected"
                );


                option.setAttribute(
                    "aria-pressed",
                    option.classList.contains(
                        "selected"
                    )
                        ? "true"
                        : "false"
                );


                updateSummary();

            }
        );

    });


    /* ======================================================
       ALTERACAO DOS SELECTS
       ====================================================== */

    [
        users,
        data,
        rag,
        ragUpdate
    ]
    .filter(Boolean)
    .forEach((field) => {

        field.addEventListener(
            "change",
            updateSummary
        );

    });


    /* ======================================================
       VALIDACAO
       ====================================================== */

    function validateConfiguration() {

        const solution =
            calculateSolution();


        if (
            solution.channels.length === 0
        ) {

            if (validationMessage) {

                validationMessage.hidden =
                    false;

                validationMessage.textContent =
                    "Selecione pelo menos um canal de atendimento antes de continuar.";

            }


            return false;

        }


        if (validationMessage) {
            validationMessage.hidden = true;
        }


        return true;

    }


    /* ======================================================
       SALVAR
       ====================================================== */

    function saveConfiguration() {

        const result =
            updateSummary();


        const configuration = {

            modules,

            channels:
                result.solution.channels,

            integrations:
                result.solution.integrations,

            resources:
                result.solution.resources,


            users: {
                value:
                    users?.value || "",

                label:
                    selectedLabel(users)
            },


            data: {
                value:
                    data?.value || "",

                label:
                    selectedLabel(data)
            },


            rag: {
                value:
                    rag?.value || "",

                label:
                    selectedLabel(rag)
            },


            ragUpdate: {
                value:
                    ragUpdate?.value || "",

                label:
                    selectedLabel(ragUpdate)
            },


            complexity: {
                score:
                    result.solution.score,

                level:
                    result.solution
                        .complexity.name,

                counts:
                    result.solution.counts
            },


            recommendedPlan: {
                id:
                    result.solution.planId,

                name:
                    plans[
                        result.solution.planId
                    ].name
            },


            pricing: {
                type:
                    "demonstrative_dynamic_estimate",

                currency:
                    "BRL",

                base:
                    result.price.base,

                modules:
                    result.price.modules,

                channels:
                    result.price.channels,

                integrations:
                    result.price.integrations,

                resources:
                    result.price.resources,

                users:
                    result.price.users,

                data:
                    result.price.data,

                rag:
                    result.price.rag,

                ragUpdate:
                    result.price.ragUpdate,

                estimatedTotal:
                    result.price.total,

                finalPriceDefined:
                    false
            },


            createdAt:
                new Date().toISOString()

        };


        localStorage.setItem(
            "inna_solution_config",
            JSON.stringify(configuration)
        );

    }


    /* ======================================================
       PROPOSTA
       ====================================================== */

    if (reviewButton) {

        reviewButton.addEventListener(
            "click",
            () => {

                if (
                    !validateConfiguration()
                ) {
                    return;
                }


                saveConfiguration();


                window.location.href =
                    "/proposta";

            }
        );

    }


    /* PRIMEIRA EXECUCAO */

    updateSummary();

});
