document.addEventListener("DOMContentLoaded", () => {

    "use strict";
    /* CONTRACT_GATE_V1 */

    let contractState = null;

    try {

        const storedContract =
            localStorage.getItem(
                "inna_contract"
            );

        contractState =
            storedContract
                ? JSON.parse(storedContract)
                : null;

    }
    catch {

        contractState = null;

    }


    if (
        !contractState ||
        contractState.accepted !== true
    ) {

        window.location.replace(
            "/contrato"
        );

        return;

    }


    console.log("SABINO_JOURNEY_V2=LOADED");


    /* ======================================================
       STORAGE
       ====================================================== */

    function getJson(key) {

        try {

            const value =
                localStorage.getItem(key);

            return value
                ? JSON.parse(value)
                : null;

        }
        catch {

            return null;

        }

    }


    const configuration =
        getJson("inna_solution_config");

    const proposal =
        getJson("inna_final_proposal");


    /* ======================================================
       HELPERS
       ====================================================== */

    function setText(id, value) {

        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                value || "-";
        }

    }


    function labelOf(value) {

        if (
            value &&
            typeof value === "object"
        ) {

            return (
                value.label ||
                value.value ||
                "-"
            );

        }

        return value || "-";

    }


    /* ======================================================
       RESUMO
       ====================================================== */

    setText(
        "journey-plan",
        configuration
            ?.recommendedPlan
            ?.name || "Não definido"
    );


    setText(
        "journey-modules",
        `${configuration?.modules?.length || 0} módulos`
    );


    setText(
        "journey-users",
        labelOf(configuration?.users)
    );


    setText(
        "journey-rag",
        labelOf(configuration?.rag)
    );


    setText(
        "journey-integrations",
        `${configuration?.integrations?.length || 0} integrações`
    );


    setText(
        "journey-channels",
        `${configuration?.channels?.length || 0} canais`
    );


    /* ======================================================
       ID DA SOLUCAO
       ====================================================== */

    let solutionId =
        localStorage.getItem(
            "inna_solution_id"
        );


    if (!solutionId) {

        const now =
            new Date();

        const date =
            [
                now.getFullYear(),
                String(
                    now.getMonth() + 1
                ).padStart(2, "0"),
                String(
                    now.getDate()
                ).padStart(2, "0")
            ].join("");


        const random =
            Math.floor(
                1000 +
                Math.random() * 9000
            );


        solutionId =
            `SOL-${date}-${random}`;


        localStorage.setItem(
            "inna_solution_id",
            solutionId
        );

    }


    setText(
        "journey-solution-id",
        solutionId
    );


    const createdAt =
        proposal?.generatedAt ||
        configuration?.createdAt ||
        new Date().toISOString();


    setText(
        "journey-created-at",
        new Date(
            createdAt
        ).toLocaleString("pt-BR")
    );


    /* ======================================================
       ETAPAS
       ====================================================== */

    const stages = [

        {
            title:
                "Proposta confirmada",

            description:
                "Configuração e proposta registradas.",

            action:
                null,

            progress:
                20
        },

        {
            title:
                "Validação da solução",

            description:
                "Revisão técnica e comercial da configuração selecionada.",

            action:
                "Concluir validação →",

            progress:
                20
        },

        {
            title:
                "Preparação do ambiente",

            description:
                "Provisionamento, políticas, segurança e configuração inicial.",

            action:
                "Concluir preparação →",

            progress:
                40
        },

        {
            title:
                "Onboarding e dados",

            description:
                "Configuração de integrações, documentos e bases de conhecimento.",

            action:
                "Concluir onboarding →",

            progress:
                60
        },

        {
            title:
                "Go Live",

            description:
                "Validação final antes da liberação da plataforma em produção.",

            action:
                "Concluir Go Live e ativar →",

            progress:
                80
        }

    ];


    /*
     * 1 = validação
     * 2 = preparação
     * 3 = onboarding
     * 4 = go live
     * 5 = plataforma ativa
     */

    let currentStage =
        Number(
            localStorage.getItem(
                "inna_implantation_stage"
            ) || "1"
        );


    let platformActive =
        localStorage.getItem(
            "inna_platform_active"
        ) === "true";


    const cards =
        Array.from(
            document.querySelectorAll(
                ".journey-step"
            )
        );


    const actionButton =
        document.getElementById(
            "journey-stage-action"
        );


    /* ======================================================
       RENDER
       ====================================================== */

    function renderJourney() {

        if (platformActive) {

            localStorage.setItem(
                "inna_implantation_stage",
                "5"
            );


            window.location.href =
                "/plataforma";

            return;

        }


        cards.forEach(
            (card, index) => {

                card.classList.remove(
                    "done",
                    "current"
                );


                const number =
                    card.querySelector(
                        ".journey-step-number"
                    );


                const status =
                    card.querySelector(
                        "small"
                    );


                if (index < currentStage) {

                    card.classList.add(
                        "done"
                    );


                    if (number) {
                        number.textContent =
                            "✓";
                    }


                    if (status) {
                        status.textContent =
                            "✓ Concluído";
                    }

                }

                else if (
                    index === currentStage
                ) {

                    card.classList.add(
                        "current"
                    );


                    if (number) {
                        number.textContent =
                            String(
                                index + 1
                            );
                    }


                    if (status) {
                        status.textContent =
                            "Etapa atual";
                    }

                }

                else {

                    if (number) {
                        number.textContent =
                            String(
                                index + 1
                            );
                    }


                    if (status) {
                        status.textContent =
                            "Pendente";
                    }

                }

            }
        );


        const stage =
            stages[currentStage];


        if (stage) {

            setText(
                "journey-stage-title",
                stage.title
            );


            setText(
                "journey-stage-description",
                stage.description
            );


            if (actionButton) {

                actionButton.textContent =
                    stage.action ||
                    "Continuar →";

            }

        }


        const progress =
            stage?.progress || 20;


        const ring =
            document.querySelector(
                ".journey-progress-ring strong"
            );


        if (ring) {
            ring.textContent =
                `${progress}%`;
        }


        const currentLabel =
            document.querySelector(
                ".journey-progress-body div:last-child strong"
            );


        if (currentLabel) {

            currentLabel.textContent =
                stage?.title || "-";

        }


        const nextLabel =
            document.querySelector(
                ".journey-progress-body div:last-child small"
            );


        if (nextLabel) {

            if (
                currentStage < 4
            ) {

                nextLabel.textContent =
                    `Próxima: ${
                        stages[
                            currentStage + 1
                        ].title
                    }`;

            }

            else {

                nextLabel.textContent =
                    "Próxima: ativação da plataforma";

            }

        }

    }


    /* ======================================================
       AVANCAR ETAPA
       ====================================================== */

    if (actionButton) {

        actionButton.addEventListener(
            "click",
            () => {

                /*
                 * Ainda não chegou ao Go Live.
                 */

                if (
                    currentStage < 4
                ) {

                    currentStage += 1;


                    localStorage.setItem(
                        "inna_implantation_stage",
                        String(currentStage)
                    );


                    renderJourney();


                    window.scrollTo({
                        top:
                            document.querySelector(
                                ".journey-steps"
                            )?.offsetTop - 120 || 0,

                        behavior:
                            "smooth"
                    });


                    return;

                }


                /*
                 * GO LIVE CONCLUIDO
                 */

                platformActive =
                    true;


                const activatedAt =
                    new Date()
                        .toISOString();


                localStorage.setItem(
                    "inna_platform_active",
                    "true"
                );


                localStorage.setItem(
                    "inna_implantation_stage",
                    "5"
                );


                localStorage.setItem(
                    "inna_platform_activated_at",
                    activatedAt
                );


                window.location.href =
                    "/plataforma";

            }
        );

    }


    /* ======================================================
       PAINEL DE ACOMPANHAMENTO
       ====================================================== */

    const dashboardButton =
        document.getElementById(
            "journey-dashboard-button"
        );


    if (dashboardButton) {

        dashboardButton.textContent =
            "Acompanhar implantação →";


        dashboardButton.addEventListener(
            "click",
            () => {

                document.querySelector(
                    ".journey-steps"
                )
                ?.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

            }
        );

    }


    renderJourney();

});

