/* ============================================================
   SABINO DEMO TOP FINAL V3

   ?demo=1:
   cria badge no topo do documento.

   Financeiro real:
   não cria badge.
   ============================================================ */

(function () {

    "use strict";

    if (window.SabinoDemoTopFinalV3) {
        return;
    }

    window.SabinoDemoTopFinalV3 = true;


    const ID =
        "sabinoDemoFixedBadge";


    let scheduled =
        false;


    function normalize(value) {

        return String(value || "")
            .normalize("NFD")
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }


    function isDemo() {

        const params =
            new URLSearchParams(
                window.location.search
            );


        return (
            params.get("demo") === "1"
        );
    }


    function hideOriginal() {

        const nodes =
            Array.from(
                document.querySelectorAll(
                    "div,span,p,strong,small"
                )
            );


        nodes.forEach(
            function (element) {

                if (
                    element.id === ID ||
                    element.closest(
                        "#" + ID
                    )
                ) {

                    return;
                }


                const text =
                    normalize(
                        element.textContent
                    );


                if (
                    text !==
                    "modo demonstracao"
                ) {

                    return;
                }


                let target =
                    element;


                for (
                    let i = 0;
                    i < 4 &&
                    target.parentElement &&
                    target.parentElement !==
                    document.body;
                    i += 1
                ) {

                    const parent =
                        target.parentElement;


                    const parentText =
                        normalize(
                            parent.textContent
                        );


                    const rect =
                        parent.getBoundingClientRect();


                    if (
                        parentText.includes(
                            "modo demonstracao"
                        ) &&
                        rect.width <= 360 &&
                        rect.height <= 140
                    ) {

                        target =
                            parent;

                    }
                    else {

                        break;
                    }
                }


                target.classList.add(
                    "sabino-demo-original-hidden"
                );

            }
        );
    }


    /* ========================================================
       SABINO_DEMO_BADGE_I18N_V5
       Sabino.AI permanece como marca.
       ======================================================== */

    function demoCopy() {

        let locale =
            document.documentElement.lang
            ||
            "pt-BR";


        try {

            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current ===
                    "function"
            ) {

                locale =
                    window.SabinoLocale.current()
                    ||
                    locale;
            }

        }
        catch (_) {}


        const language =
            String(locale)
                .replace("_", "-")
                .split("-")[0]
                .toLowerCase();


        const copies = {

            pt: {
                title:
                    "Modo demonstração",

                subtitle:
                    "Conta Sabino.AI"
            },


            en: {
                title:
                    "Demo mode",

                subtitle:
                    "Sabino.AI Account"
            },


            es: {
                title:
                    "Modo de demostración",

                subtitle:
                    "Cuenta Sabino.AI"
            },


            de: {
                title:
                    "Demomodus",

                subtitle:
                    "Sabino.AI-Konto"
            },


            fr: {
                title:
                    "Mode démonstration",

                subtitle:
                    "Compte Sabino.AI"
            },


            it: {
                title:
                    "Modalità demo",

                subtitle:
                    "Account Sabino.AI"
            },


            ro: {
                title:
                    "Mod demonstrație",

                subtitle:
                    "Cont Sabino.AI"
            },


            ru: {
                title:
                    "Демо-режим",

                subtitle:
                    "Аккаунт Sabino.AI"
            },


            uk: {
                title:
                    "Демонстраційний режим",

                subtitle:
                    "Обліковий запис Sabino.AI"
            },


            ar: {
                title:
                    "وضع العرض التجريبي",

                subtitle:
                    "حساب Sabino.AI"
            }
        };


        return (
            copies[language]
            ||
            copies.pt
        );
    }


    function translateDemoBadge(
        badge
    ) {

        if (!badge) {
            return;
        }


        const copy =
            demoCopy();


        const title =
            badge.querySelector(
                ".sabino-demo-title"
            );


        const subtitle =
            badge.querySelector(
                ".sabino-demo-subtitle"
            );


        if (title) {

            title.textContent =
                copy.title;
        }


        if (subtitle) {

            subtitle.textContent =
                copy.subtitle;
        }


        /*
         * Protege apenas a marca.
         */

        if (subtitle) {

            subtitle.setAttribute(
                "data-sabino-brand-preserved",
                "true"
            );
        }


        badge.setAttribute(
            "data-sabino-demo-i18n-v5",
            "true"
        );
    }



    function ensureBadge() {

        scheduled =
            false;


        if (!isDemo()) {

            const existing =
                document.getElementById(
                    ID
                );


            if (existing) {
                existing.remove();
            }


            return;
        }


        let badge =
            document.getElementById(
                ID
            );


        if (!badge) {

            badge =
                document.createElement(
                    "div"
                );


            badge.id =
                ID;


            badge.innerHTML = `
                <div class="sabino-demo-title">
                    Modo demonstração
                </div>

                <div class="sabino-demo-subtitle">
                    Conta Sabino.AI
                </div>
            `;
        }


        /*
         * Mesmo padrão que funcionou
         * para o idioma:
         *
         * filho direto do HTML.
         */

        if (
            badge.parentElement !==
            document.documentElement
        ) {

            document.documentElement
                .appendChild(
                    badge
                );
        }


        /*
         * Reforço inline contra qualquer
         * runtime concorrente.
         */

        badge.style.setProperty(
            "position",
            "absolute",
            "important"
        );

        badge.style.setProperty(
            "top",
            "10px",
            "important"
        );

        badge.style.setProperty(
            "right",
            "24px",
            "important"
        );

        badge.style.setProperty(
            "left",
            "auto",
            "important"
        );

        badge.style.setProperty(
            "bottom",
            "auto",
            "important"
        );

        badge.style.setProperty(
            "transform",
            "none",
            "important"
        );


        translateDemoBadge(
            badge
        );


        hideOriginal();
    }


    function schedule() {

        if (scheduled) {
            return;
        }


        scheduled =
            true;


        requestAnimationFrame(
            ensureBadge
        );
    }


    function boot() {

        ensureBadge();


        [
            100,
            300,
            700,
            1200,
            2000
        ]
        .forEach(
            function (delay) {

                window.setTimeout(
                    ensureBadge,
                    delay
                );

            }
        );
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            boot,
            {
                once: true
            }
        );

    }
    else {

        boot();
    }


    window.addEventListener(
        "load",
        boot
    );


    /*
     * Atualiza imediatamente ao trocar idioma.
     */

    window.addEventListener(
        "sabino:locale-change",
        ensureBadge
    );


    window.addEventListener(
        "sabino:languagechange",
        ensureBadge
    );


    /*
     * Se algum runtime recriar o badge
     * original após o carregamento,
     * escondemos novamente.
     *
     * NÃO existe listener de scroll.
     */

    const observer =
        new MutationObserver(
            schedule
        );


    function observe() {

        if (!document.body) {
            return;
        }


        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );
    }


    if (document.body) {

        observe();

    }
    else {

        document.addEventListener(
            "DOMContentLoaded",
            observe,
            {
                once: true
            }
        );
    }

})();


/* ============================================================
   SABINO_DEMO_DUPLICATE_CLEANUP_V6

   DEMO:
   mantém somente o badge fixo superior.

   REAL:
   mantém o bloco normal de conta/usuário.
   ============================================================ */

(function () {

    "use strict";


    if (
        window.SabinoDemoDuplicateCleanupV6
    ) {

        return;
    }


    window.SabinoDemoDuplicateCleanupV6 =
        true;


    function isDemo() {

        const params =
            new URLSearchParams(
                window.location.search
            );


        return (
            params.get("demo") === "1"
        );
    }


    function originalAccount() {

        /*
         * Elementos exatos já existentes
         * no Financeiro.
         */

        const name =
            document.getElementById(
                "financeAccountName"
            );


        const plan =
            document.getElementById(
                "financeAccountPlan"
            );


        /*
         * Procuramos apenas o container
         * .account desses elementos.
         *
         * Não sobe por containers genéricos.
         */

        if (name) {

            const account =
                name.closest(
                    ".account"
                );


            if (account) {
                return account;
            }
        }


        if (plan) {

            const account =
                plan.closest(
                    ".account"
                );


            if (account) {
                return account;
            }
        }


        return null;
    }


    function apply() {

        const account =
            originalAccount();


        if (!account) {
            return false;
        }


        if (isDemo()) {

            /*
             * No demo o badge superior
             * #sabinoDemoFixedBadge é o único
             * indicador visual de demonstração.
             */

            account.style.setProperty(
                "display",
                "none",
                "important"
            );


            account.setAttribute(
                "aria-hidden",
                "true"
            );


            account.setAttribute(
                "data-sabino-demo-original-hidden",
                "true"
            );


            return true;
        }


        /*
         * Financeiro REAL:
         * nunca esconder a conta do usuário.
         */

        if (
            account.getAttribute(
                "data-sabino-demo-original-hidden"
            ) === "true"
        ) {

            account.style.removeProperty(
                "display"
            );


            account.removeAttribute(
                "aria-hidden"
            );


            account.removeAttribute(
                "data-sabino-demo-original-hidden"
            );
        }


        return true;
    }


    function boot() {

        apply();


        [
            50,
            150,
            400,
            800,
            1500,
            2500
        ]
        .forEach(
            function (delay) {

                window.setTimeout(
                    apply,
                    delay
                );
            }
        );
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            boot,
            {
                once: true
            }
        );

    }
    else {

        boot();
    }


    window.addEventListener(
        "load",
        boot
    );


    window.addEventListener(
        "sabino:locale-change",
        apply
    );


    window.addEventListener(
        "sabino:languagechange",
        apply
    );

})();
