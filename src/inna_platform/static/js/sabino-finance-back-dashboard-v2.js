
/* ============================================================
   SABINO.AI
   FINANCE BACK DASHBOARD V2

   Demo + Real:
   volta para /dashboard
   ============================================================ */

(function () {

    "use strict";

    if (window.SabinoFinanceBackDashboardV2) {
        return;
    }

    window.SabinoFinanceBackDashboardV2 = true;


    const ID =
        "sabinoFinanceBackDashboardV2";


    /*
     * Unicode por escape para evitar problemas
     * de encoding no PowerShell.
     */

    const LABELS = {

        pt: "Voltar",

        en: "Back",

        es: "Volver",

        de: "Zur\u00fcck",

        fr: "Retour",

        it: "Indietro",

        ro: "\u00cenapoi",

        ru: "\u041d\u0430\u0437\u0430\u0434",

        uk: "\u041d\u0430\u0437\u0430\u0434",

        ar: "\u0627\u0644\u0639\u0648\u062f\u0629"
    };


    function language() {

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


        return String(
            locale
        )
        .replace("_", "-")
        .split("-")[0]
        .toLowerCase();
    }


    function sidebar() {

        return (
            document.querySelector(".sidebar")
            ||
            document.querySelector(".side")
            ||
            document.querySelector("aside")
        );
    }


    function brand(
        target
    ) {

        if (!target) {
            return null;
        }


        return (
            target.querySelector(".brand")
            ||
            target.querySelector(".sidebar-brand")
            ||
            target.querySelector(".logo")
            ||
            target.querySelector("[class*='brand']")
        );
    }


    function translate(
        button
    ) {

        if (!button) {
            return;
        }


        const lang =
            language();


        const label =
            button.querySelector(
                ".sabino-back-label"
            );


        if (label) {

            label.textContent =
                LABELS[lang]
                ||
                LABELS.pt;
        }


        button.setAttribute(
            "aria-label",
            LABELS[lang]
            ||
            LABELS.pt
        );
    }


    function ensure() {

        const targetSidebar =
            sidebar();


        if (!targetSidebar) {
            return false;
        }


        let button =
            document.getElementById(
                ID
            );


        if (!button) {

            button =
                document.createElement(
                    "a"
                );


            button.id =
                ID;


            button.href =
                "/dashboard";


            button.setAttribute(
                "data-sabino-finance-back",
                "true"
            );


            button.innerHTML = [
                '<span class="sabino-back-arrow" aria-hidden="true">',
                '\u2190',
                '</span>',
                '<span class="sabino-back-label">Voltar</span>'
            ].join("");
        }


        /*
         * Demo e real voltam para a central
         * onde esta o card Financeiro.
         */

        button.href =
            "/dashboard";


        const targetBrand =
            brand(
                targetSidebar
            );


        if (targetBrand) {

            if (
                button.parentElement !==
                    targetSidebar
                ||
                button.previousElementSibling !==
                    targetBrand
            ) {

                targetBrand.insertAdjacentElement(
                    "afterend",
                    button
                );
            }

        }
        else if (
            button.parentElement !==
            targetSidebar
        ) {

            targetSidebar.insertBefore(
                button,
                targetSidebar.firstChild
            );
        }


        translate(
            button
        );


        return true;
    }


    function boot() {

        ensure();


        [
            100,
            300,
            700,
            1200
        ]
        .forEach(
            function (delay) {

                window.setTimeout(
                    ensure,
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
        function () {

            translate(
                document.getElementById(
                    ID
                )
            );
        }
    );


    window.addEventListener(
        "sabino:languagechange",
        function () {

            translate(
                document.getElementById(
                    ID
                )
            );
        }
    );

})();
