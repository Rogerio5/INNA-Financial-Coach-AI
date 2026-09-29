document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    console.log("SABINO_CONTRACT_V1=LOADED");


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


    /*
     * Sem proposta não existe contrato.
     */

    if (!configuration) {

        window.location.replace(
            "/configurar"
        );

        return;

    }


    function setText(id, value) {

        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                value ?? "-";
        }

    }


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


    /* ======================================================
       DADOS PRINCIPAIS
       ====================================================== */

    const plan =
        configuration
            ?.recommendedPlan
            ?.name || "-";


    const planId =
        configuration
            ?.recommendedPlan
            ?.id || "";


    const monthlyEstimate =
        proposal?.finalEstimate ??
        configuration
            ?.pricing
            ?.estimatedTotal ??
        null;


    const solutionId =
        localStorage.getItem(
            "inna_solution_id"
        ) || "Será gerado na contratação";


    setText(
        "contract-solution-id",
        solutionId
    );


    setText(
        "contract-plan",
        plan
    );


    setText(
        "contract-summary-plan",
        plan
    );


    setText(
        "contract-monthly-price",
        formatBRL(monthlyEstimate)
    );


    setText(
        "contract-count-modules",
        configuration?.modules?.length || 0
    );


    setText(
        "contract-count-channels",
        configuration?.channels?.length || 0
    );


    setText(
        "contract-count-integrations",
        configuration?.integrations?.length || 0
    );


    setText(
        "contract-count-resources",
        configuration?.resources?.length || 0
    );


    /* ======================================================
       PRAZO
       ====================================================== */

    const termInputs =
        Array.from(
            document.querySelectorAll(
                'input[name="contract-term"]'
            )
        );


    const billingInputs =
        Array.from(
            document.querySelectorAll(
                'input[name="billing"]'
            )
        );


    function selectedTerm() {

        return Number(
            document.querySelector(
                'input[name="contract-term"]:checked'
            )?.value || 1
        );

    }


    function selectedBilling() {

        return (
            document.querySelector(
                'input[name="billing"]:checked'
            )?.value || "monthly"
        );

    }


    function termLabel(months) {

        if (months === 1) {
            return "1 mês";
        }

        if (months === 12) {
            return "12 meses / 1 ano";
        }

        if (months === 24) {
            return "24 meses / 2 anos";
        }

        if (months === 36) {
            return "36 meses / 3 anos";
        }

        return `${months} meses`;

    }


    function updateCommercialSummary() {

        const months =
            selectedTerm();


        const billing =
            selectedBilling();


        setText(
            "contract-summary-term",
            termLabel(months)
        );


        setText(
            "contract-summary-billing",
            billing === "annual"
                ? "Anual"
                : "Mensal"
        );


        if (
            monthlyEstimate === null ||
            planId === "enterprise"
        ) {

            setText(
                "contract-period-total",
                "Sob consulta"
            );

        }

        else {

            const total =
                Number(monthlyEstimate) *
                months;


            setText(
                "contract-period-total",
                formatBRL(total)
            );

        }


        document
            .querySelectorAll(
                ".contract-choice"
            )
            .forEach(label => {

                label.classList.toggle(
                    "selected",
                    label.querySelector(
                        "input"
                    )?.checked
                );

            });


        document
            .querySelectorAll(
                ".contract-billing-option"
            )
            .forEach(label => {

                label.classList.toggle(
                    "selected",
                    label.querySelector(
                        "input"
                    )?.checked
                );

            });

    }


    termInputs.forEach(input => {

        input.addEventListener(
            "change",
            updateCommercialSummary
        );

    });


    billingInputs.forEach(input => {

        input.addEventListener(
            "change",
            updateCommercialSummary
        );

    });


    /* ======================================================
       ACEITE
       ====================================================== */

    const confirmButton =
        document.getElementById(
            "contract-confirm"
        );


    const validation =
        document.getElementById(
            "contract-validation"
        );


    function showError(message) {

        if (!validation) {
            return;
        }


        validation.hidden =
            false;


        validation.textContent =
            message;


        validation.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    }


    function validateContract() {

        /* CONTRACT_DOCUMENT_READ_GATE_V1 */

        const requiredDocuments = [
            "contract",
            "proposal",
            "terms",
            "sla",
            "privacy",
            "security",
            "commercial"
        ];


        let documentReads = {};


        try {

            documentReads =
                JSON.parse(
                    localStorage.getItem(
                        "inna_contract_document_reads_v51"
                    ) || "{}"
                );

        }
        catch {

            documentReads = {};

        }


        const unreadDocuments =
            requiredDocuments.filter(
                documentId =>
                    documentReads
                        ?. [documentId]
                        ?.confirmed !== true
            );


        if (unreadDocuments.length > 0) {

            showError(
                `Leia e confirme todos os documentos contratuais antes de continuar. Restam ${unreadDocuments.length} documento(s).`
            );

            return false;

        }


        const company =
            document.getElementById(
                "contract-company"
            )?.value.trim();


        const representative =
            document.getElementById(
                "contract-representative"
            )?.value.trim();


        const role =
            document.getElementById(
                "contract-role"
            )?.value.trim();


        const email =
            document.getElementById(
                "contract-email"
            )?.value.trim();


        if (
            !company ||
            !representative ||
            !role ||
            !email
        ) {

            showError(
                "Preencha empresa, representante autorizado, cargo e e-mail corporativo."
            );

            return false;

        }


        if (
            !document.getElementById(
                "accept-terms"
            )?.checked ||

            !document.getElementById(
                "accept-commercial"
            )?.checked ||

            !document.getElementById(
                "accept-authorized"
            )?.checked
        ) {

            showError(
                "Confirme os três itens de aceite antes de continuar."
            );

            return false;

        }


        const acceptance =
            document.getElementById(
                "contract-accept-text"
            )?.value
                .trim()
                .toUpperCase();


        if (acceptance !== "ACEITO") {

            showError(
                'Digite exatamente "ACEITO" para confirmar a contratação.'
            );

            return false;

        }


        if (
            planId === "enterprise" ||
            monthlyEstimate === null
        ) {

            showError(
                "Esta configuração requer uma proposta Enterprise personalizada antes da formalização do contrato."
            );

            return false;

        }


        validation.hidden =
            true;


        return true;

    }


    function generateContractId() {

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


        return `CTR-${date}-${random}`;

    }


    if (confirmButton) {

        confirmButton.addEventListener(
            "click",
            () => {

                if (!validateContract()) {
                    return;
                }


                const months =
                    selectedTerm();


                const billing =
                    selectedBilling();


                const total =
                    Number(monthlyEstimate) *
                    months;


                const contract = {

                    contractId:
                        generateContractId(),

                    solutionId:
                        localStorage.getItem(
                            "inna_solution_id"
                        ),

                    contractVersion:
                        "1.0-demo",

                    plan: {
                        id:
                            planId,

                        name:
                            plan
                    },

                    term: {
                        months,

                        label:
                            termLabel(months)
                    },

                    billing: {
                        type:
                            billing,

                        label:
                            billing === "annual"
                                ? "Anual"
                                : "Mensal"
                    },

                    pricing: {
                        currency:
                            "BRL",

                        monthlyEstimate:
                            Number(monthlyEstimate),

                        periodEstimate:
                            total,

                        commercialStatus:
                            "demonstrative"
                    },

                    company: {

                        legalName:
                            document.getElementById(
                                "contract-company"
                            ).value.trim(),

                        document:
                            document.getElementById(
                                "contract-company-document"
                            ).value.trim(),

                        representative:
                            document.getElementById(
                                "contract-representative"
                            ).value.trim(),

                        role:
                            document.getElementById(
                                "contract-role"
                            ).value.trim(),

                        email:
                            document.getElementById(
                                "contract-email"
                            ).value.trim()

                    },

                    acceptance: {

                        terms:
                            true,

                        commercial:
                            true,

                        authorized:
                            true,

                        confirmationText:
                            "ACEITO",

                        acceptedAt:
                            new Date()
                                .toISOString()

                    },

                    legalReview: {

                        status:
                            "PENDING_LEGAL_REVIEW",

                        label:
                            "Pendente de validação jurídica",

                        contractVersion:
                            "1.0-demo",

                        productionApproved:
                            false,

                        reviewedBy:
                            null,

                        reviewedAt:
                            null
                    },

                    accepted:
                        true

                };


                localStorage.setItem(
                    "inna_contract",
                    JSON.stringify(contract)
                );


                /*
                 * Uma nova contratação reinicia
                 * a implantação.
                 */

                localStorage.setItem(
                    "inna_implantation_stage",
                    "1"
                );


                localStorage.setItem(
                    "inna_platform_active",
                    "false"
                );


                localStorage.removeItem(
                    "inna_platform_activated_at"
                );


                window.location.href =
                    "/jornada";

            }
        );

    }


    updateCommercialSummary();

});



