(function () {

    "use strict";


    if (window.SabinoDashboardArabicPolishV1) {
        return;
    }


    window.SabinoDashboardArabicPolishV1 = true;


    const ARABIC_RE =
        /[\u0600-\u06FF]/;


    const REPLACEMENTS = {

        "Início":
            "الرئيسية",

        "Inicio":
            "الرئيسية",

        "Premium · Ativo":
            "مميز · نشط",

        "Premium · Active":
            "مميز · نشط"

    };


    function normalize(value) {

        return String(value || "")
            .replace(/\s+/g, " ")
            .trim();
    }


    function currentLocale() {

        let locale =
            document.documentElement.lang ||
            "pt-BR";


        try {

            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current === "function"
            ) {

                locale =
                    window.SabinoLocale.current() ||
                    locale;
            }

        }
        catch (_) {
        }


        return String(locale)
            .replace("_", "-")
            .toLowerCase();
    }


    function isArabic() {

        return currentLocale()
            .startsWith("ar");
    }


    function restoreStructureDirection() {

        /*
         * O árabe não vai espelhar a aplicação inteira.
         */

        document.documentElement
            .setAttribute(
                "dir",
                "ltr"
            );


        if (document.body) {

            document.body
                .setAttribute(
                    "dir",
                    "ltr"
                );
        }


        /*
         * Se houver grids, garantir ordem física LTR.
         */

        Array.from(
            document.querySelectorAll(
                "body *"
            )
        )
        .forEach(function (element) {

            const style =
                window.getComputedStyle(
                    element
                );


            if (
                style.display === "grid" &&
                element.children.length >= 3
            ) {

                element.style.setProperty(
                    "direction",
                    "ltr",
                    "important"
                );
            }

        });

    }


    function replacePortugueseLeftovers() {

        const elements =
            Array.from(
                document.querySelectorAll(
                    "span, strong, small, a, button, div"
                )
            );


        elements.forEach(function (element) {

            /*
             * Só alterar folhas.
             */

            if (element.children.length !== 0) {
                return;
            }


            const text =
                normalize(
                    element.textContent
                );


            if (
                Object.prototype
                    .hasOwnProperty
                    .call(
                        REPLACEMENTS,
                        text
                    )
            ) {

                element.textContent =
                    REPLACEMENTS[text];
            }

        });

    }


    function markArabicText() {

        const elements =
            Array.from(
                document.querySelectorAll(
                    "h1, h2, h3, h4, h5, h6, " +
                    "p, span, strong, small, label, a, button, div"
                )
            );


        elements.forEach(function (element) {

            /*
             * Não aplicar RTL a containers.
             * Somente elementos finais de texto.
             */

            if (
                element.children.length !== 0
            ) {
                return;
            }


            const text =
                normalize(
                    element.textContent
                );


            if (!text) {
                return;
            }


            if (
                ARABIC_RE.test(
                    text
                )
            ) {

                element.setAttribute(
                    "data-sabino-arabic-text",
                    "true"
                );


                element.setAttribute(
                    "dir",
                    "rtl"
                );

            }
            else {

                element.removeAttribute(
                    "data-sabino-arabic-text"
                );


                /*
                 * Marcas e nomes técnicos continuam LTR.
                 */

                if (
                    text.includes("Sabino.AI") ||
                    text === "INNA"
                ) {

                    element.setAttribute(
                        "data-sabino-arabic-brand",
                        "true"
                    );

                }

            }

        });

    }


    function fixHeaderOrder() {

        const header =
            document.getElementById(
                "sabinoDashboardHeaderFinal"
            );


        const language =
            document.getElementById(
                "sabinoLanguageSwitcher"
            );


        const user =
            document.querySelector(
                '[data-sabino-dashboard-user-final="true"]'
            );


        if (
            !header ||
            !language ||
            !user
        ) {
            return;
        }


        /*
         * Mesmo padrão do Português:
         *
         * idioma | usuário
         */

        if (
            language.parentElement !== header
        ) {

            header.appendChild(
                language
            );
        }


        if (
            user.parentElement !== header
        ) {

            header.appendChild(
                user
            );
        }


        language.style.setProperty(
            "order",
            "1",
            "important"
        );


        user.style.setProperty(
            "order",
            "2",
            "important"
        );


        header.style.setProperty(
            "direction",
            "ltr",
            "important"
        );

    }


    function applyArabic() {

        if (!isArabic()) {

            document.documentElement
                .classList
                .remove(
                    "sabino-dashboard-arabic"
                );


            return;
        }


        document.documentElement
            .classList
            .add(
                "sabino-dashboard-arabic"
            );


        restoreStructureDirection();

        replacePortugueseLeftovers();

        markArabicText();

        fixHeaderOrder();

    }


    function refresh() {

        [
            0,
            100,
            300,
            700,
            1400
        ]
        .forEach(function (delay) {

            window.setTimeout(
                applyArabic,
                delay
            );

        });

    }


    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            refresh,
            {
                once: true
            }
        );

    }
    else {

        refresh();
    }


    /*
     * Reaplicar depois de cada mudança
     * do seletor de idiomas.
     */

    window.addEventListener(
        "sabino:locale-change",
        refresh
    );


    window.addEventListener(
        "sabino:money-localized",
        refresh
    );

})();
