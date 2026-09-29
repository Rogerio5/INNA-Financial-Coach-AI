document.addEventListener("DOMContentLoaded", () => {

    /* ======================================================
       CONFIGURACAO
       ====================================================== */

    let configuration = null;


    try {

        const stored =
            localStorage.getItem(
                "inna_solution_config"
            );


        if (stored) {

            configuration =
                JSON.parse(stored);

        }

    }
    catch (error) {

        console.error(
            "Erro ao carregar configuração:",
            error
        );

    }


    if (!configuration) {

        configuration = {

            modules: [
                "Educação Financeira"
            ],

            channels: [
                "Web App"
            ],

            integrations: [],

            resources: [],

            users: {
                value: "1-10",
                label: "1 a 10 usuários"
            },

            data: {
                value: "0-10",
                label: "Até 10 GB/mês"
            },

            rag: {
                value: "0-5000",
                label: "Até 5.000 documentos"
            },

            ragUpdate: {
                value: "on-demand",
                label: "Sob demanda"
            },

            complexity: {
                score: 0,
                level: "Baixa",

                counts: {
                    modules: 1,
                    channels: 1,
                    integrations: 0,
                    resources: 0
                }
            },

            recommendedPlan: {
                id: "starter",
                name: "Starter"
            },

            pricing: {
                currency: "BRL",
                base: 1490,
                modules: 0,
                channels: 0,
                integrations: 0,
                resources: 0,
                users: 0,
                data: 0,
                rag: 0,
                ragUpdate: 0,
                estimatedTotal: 1490
            }

        };

    }


    /* ======================================================
       NORMALIZACAO
       ====================================================== */

    const modules =
        Array.isArray(configuration.modules)
            ? configuration.modules
            : [];


    const channels =
        Array.isArray(configuration.channels)
            ? configuration.channels
            : [];


    const integrations =
        Array.isArray(configuration.integrations)
            ? configuration.integrations
            : [];


    const resources =
        Array.isArray(configuration.resources)
            ? configuration.resources
            : [];


    function labelOf(value) {

        if (
            value &&
            typeof value === "object"
        ) {

            return (
                value.label ||
                value.value ||
                ""
            );

        }

        return value || "";

    }


    /* ======================================================
       FORMATACAO
       ====================================================== */

    function formatBRL(value) {

        if (
            value === null ||
            value === undefined
        ) {

            return "Sob consulta";

        }


        return new Intl.NumberFormat(
            "pt-BR",
            {
                style: "currency",
                currency: "BRL",
                maximumFractionDigits: 0
            }
        ).format(value);

    }


    function setText(id, value) {

        const element =
            document.getElementById(id);

        if (element) {

            element.textContent =
                value;

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


    /* ======================================================
       LISTAS
       ====================================================== */

    function renderList(
        targetId,
        values
    ) {

        const target =
            document.getElementById(targetId);


        if (!target) {
            return;
        }


        target.innerHTML = "";


        values.forEach(value => {

            const item =
                document.createElement("li");

            item.textContent =
                value;

            target.appendChild(item);

        });

    }


    function renderTags(
        targetId,
        values
    ) {

        const target =
            document.getElementById(targetId);


        if (!target) {
            return;
        }


        target.innerHTML = "";


        values.forEach(value => {

            const tag =
                document.createElement("span");

            tag.textContent =
                value;

            target.appendChild(tag);

        });

    }


    /* ======================================================
       RESUMO
       ====================================================== */

    renderList(
        "proposal-summary-modules",
        modules
    );


    renderTags(
        "proposal-summary-channels",
        channels
    );


    renderTags(
        "proposal-summary-integrations",
        integrations
    );


    renderList(
        "proposal-summary-resources",
        resources
    );


    setText(
        "proposal-module-count",
        `${modules.length} módulos`
    );


    setText(
        "proposal-summary-users",
        labelOf(configuration.users)
    );


    setText(
        "proposal-summary-data",
        labelOf(configuration.data)
    );


    setText(
        "proposal-summary-rag",
        labelOf(configuration.rag)
    );


    setText(
        "proposal-summary-rag-update",
        labelOf(configuration.ragUpdate)
    );


    /* ======================================================
       DIMENSIONAMENTO
       ====================================================== */

    const counts =
        configuration.complexity?.counts || {};


    setText(
        "proposal-count-modules",
        counts.modules ?? modules.length
    );


    setText(
        "proposal-count-channels",
        counts.channels ?? channels.length
    );


    setText(
        "proposal-count-integrations",
        counts.integrations ?? integrations.length
    );


    setText(
        "proposal-count-resources",
        counts.resources ?? resources.length
    );


    setText(
        "proposal-complexity-level",
        configuration.complexity?.level || "-"
    );


    /* ======================================================
       PRECO DA CONFIGURACAO
       ====================================================== */

    const pricing =
        configuration.pricing || {};


    setMoney(
        "proposal-price-base",
        pricing.base ?? 0
    );


    setMoney(
        "proposal-price-modules",
        pricing.modules ?? 0
    );


    setMoney(
        "proposal-price-channels",
        pricing.channels ?? 0
    );


    setMoney(
        "proposal-price-integrations",
        pricing.integrations ?? 0
    );


    setMoney(
        "proposal-price-resources",
        pricing.resources ?? 0
    );


    setMoney(
        "proposal-price-users",
        pricing.users ?? 0
    );


    setMoney(
        "proposal-price-data",
        pricing.data ?? 0
    );


    setMoney(
        "proposal-price-rag",
        pricing.rag ?? 0
    );


    setMoney(
        "proposal-price-rag-update",
        pricing.ragUpdate ?? 0
    );


    /* ======================================================
       PLANO RECOMENDADO
       ====================================================== */

    const recommendedPlan =
        configuration.recommendedPlan?.id ||
        "starter";


    const plans =
        Array.from(
            document.querySelectorAll(
                ".proposal-plan"
            )
        );


    let selectedPlan = null;


    plans.forEach(plan => {

        const planId =
            plan.dataset.plan;


        plan.classList.remove(
            "selected"
        );


        const button =
            plan.querySelector(
                ".proposal-select-plan"
            );


        if (
            button &&
            button.tagName === "BUTTON"
        ) {

            button.textContent =
                "Selecionar plano";

        }


        /*
         * Starter não pode ser utilizado
         * quando a configuração recomendada
         * já exige Business ou Enterprise.
         */

        if (
            planId === "starter" &&
            recommendedPlan !== "starter"
        ) {

            plan.classList.add(
                "incompatible"
            );


            if (
                button &&
                button.tagName === "BUTTON"
            ) {

                button.disabled = true;

                button.textContent =
                    "Não compatível";

            }

        }


        /*
         * Business também não deve ser
         * usado quando a configuração
         * exige Enterprise.
         */

        if (
            planId === "business" &&
            recommendedPlan === "enterprise"
        ) {

            plan.classList.add(
                "incompatible"
            );


            if (
                button &&
                button.tagName === "BUTTON"
            ) {

                button.disabled = true;

                button.textContent =
                    "Requer Enterprise";

            }

        }


        if (
            planId === recommendedPlan
        ) {

            plan.classList.add(
                "selected"
            );

            selectedPlan =
                plan;


            if (
                button &&
                button.tagName === "BUTTON"
            ) {

                button.textContent =
                    "Plano recomendado";

            }

        }

    });


    /*
     * Enterprise utiliza link para especialista.
     */

    if (!selectedPlan) {

        selectedPlan =
            plans.find(
                plan =>
                    plan.dataset.plan ===
                    recommendedPlan
            ) || null;

    }


    setText(
        "proposal-selected-plan",
        configuration.recommendedPlan?.name ||
        recommendedPlan
    );


    /* ======================================================
       PRECO DOS CARDS
       ====================================================== */

    /*
     * O valor principal da configuração
     * calculado no configurador deve aparecer
     * no plano recomendado.
     */

    const estimatedTotal =
        pricing.estimatedTotal;


    if (
        recommendedPlan === "starter"
    ) {

        const starter =
            document.querySelector(
                '[data-plan="starter"]'
            );


        const starterPrice =
            starter?.querySelector(
                ".proposal-price strong"
            );


        if (starterPrice) {

            starterPrice.textContent =
                formatBRL(
                    estimatedTotal ?? 1490
                );

        }

    }


    if (
        recommendedPlan === "business"
    ) {

        const business =
            document.querySelector(
                '[data-plan="business"]'
            );


        const businessPrice =
            business?.querySelector(
                ".proposal-price strong"
            );


        if (businessPrice) {

            businessPrice.textContent =
                formatBRL(
                    estimatedTotal ?? 3490
                );

        }

    }


    /* ======================================================
       EXTRAS OPCIONAIS DA PROPOSTA
       ====================================================== */

    function selectedExtrasTotal() {

        return Array.from(
            document.querySelectorAll(
                '.proposal-extra input:checked'
            )
        )
        .reduce(
            (total, input) =>
                total +
                Number(
                    input.dataset.extraPrice || 0
                ),
            0
        );

    }


    function updateFinalEstimate() {

        /*
         * Enterprise continua sob consulta.
         */

        if (
            recommendedPlan === "enterprise" ||
            estimatedTotal === null
        ) {

            setText(
                "proposal-estimated-total",
                "Sob consulta"
            );

            return;

        }


        const extras =
            selectedExtrasTotal();


        const total =
            Number(
                estimatedTotal || 0
            ) + extras;


        setText(
            "proposal-estimated-total",
            formatBRL(total)
        );

    }


    document.querySelectorAll(
        ".proposal-extra input"
    )
    .forEach(input => {

        input.addEventListener(
            "change",
            updateFinalEstimate
        );

    });


    updateFinalEstimate();


    /* ======================================================
       VALIDADE
       ====================================================== */

    const validity =
        new Date();


    validity.setDate(
        validity.getDate() + 7
    );


    setText(
        "proposal-validity-date",
        validity.toLocaleDateString(
            "pt-BR"
        )
    );


    /* ======================================================
       FINALIZAR
       ====================================================== */

    const finalize =
        document.getElementById(
            "proposal-finalize"
        );


    if (finalize) {

        finalize.addEventListener(
            "click",
            () => {

                const extras =
                    Array.from(
                        document.querySelectorAll(
                            ".proposal-extra input:checked"
                        )
                    )
                    .map(input => ({
                        name:
                            input.dataset.extraName,

                        price:
                            Number(
                                input.dataset.extraPrice || 0
                            )
                    }));


                const proposal = {

                    configuration,

                    plan:
                        recommendedPlan,

                    extras,

                    finalEstimate:
                        estimatedTotal === null
                            ? null
                            : Number(
                                estimatedTotal || 0
                            ) +
                            selectedExtrasTotal(),

                    generatedAt:
                        new Date().toISOString()

                };


                localStorage.setItem(
                    "inna_final_proposal",
                    JSON.stringify(proposal)
                );


                window.location.href = "/contrato";

            }
        );

    }

});


