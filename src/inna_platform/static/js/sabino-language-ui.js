(() => {
    "use strict";

    const STORAGE =
        "sabino.language.v2";

    const LEGACY =
        "sabino_language";


    function normalize(value) {

        const raw =
            String(
                value || "pt-BR"
            )
            .trim()
            .replaceAll("_", "-");

        try {
            return new Intl.Locale(
                raw
            ).toString();
        }
        catch {
            return raw || "pt-BR";
        }
    }


    function currentLocale() {

        if (
            window.SabinoI18n &&
            window.SabinoI18n.locale
        ) {
            return normalize(
                window.SabinoI18n.locale
            );
        }


        return normalize(
            localStorage.getItem(
                STORAGE
            )
            ||
            localStorage.getItem(
                LEGACY
            )
            ||
            navigator.language
            ||
            "pt-BR"
        );
    }


    function findDisplayTarget() {

        const button =
            document.getElementById(
                "languageButton"
            );


        let target =
            document.getElementById(
                "languageCode"
            )
            ||
            document.querySelector(
                "[data-language-code]"
            )
            ||
            document.querySelector(
                ".language-code"
            )
            ||
            document.querySelector(
                "[data-sabino-language-display]"
            );


        if (
            !target &&
            button
        ) {

            const candidates = [
                ...button.querySelectorAll(
                    "span,strong,b,small"
                )
            ];


            target =
                candidates.find(
                    element => {

                        const text =
                            String(
                                element.textContent
                                ||
                                ""
                            ).trim();

                        return (
                            text.length > 0 &&
                            text.length < 40 &&
                            !element.querySelector(
                                "svg"
                            )
                        );
                    }
                );
        }


        if (
            !target &&
            button
        ) {

            target =
                document.createElement(
                    "span"
                );

            button.appendChild(
                target
            );
        }


        return {
            button,
            target
        };
    }


    function update(locale) {

        const normalized =
            normalize(
                locale
            );

        const {
            button,
            target
        } =
            findDisplayTarget();


        /*
           Impede o motor de tradução
           de traduzir o próprio código
           do idioma.
        */

        if (button) {

            button.removeAttribute(
                "data-i18n"
            );

            button.removeAttribute(
                "data-i18n-html"
            );

            button.setAttribute(
                "translate",
                "no"
            );
        }


        if (target) {

            target.removeAttribute(
                "data-i18n"
            );

            target.removeAttribute(
                "data-i18n-html"
            );

            target.setAttribute(
                "translate",
                "no"
            );

            target.dataset
                .sabinoLanguageDisplay =
                    "true";


            target.textContent =
                normalized.toUpperCase();
        }
    }


    window.addEventListener(
        "sabino:languagechange",
        event => {

            update(
                event.detail?.locale
                ||
                currentLocale()
            );
        }
    );


    function boot() {

        update(
            currentLocale()
        );


        /*
           Reforço após tradução
           assíncrona da interface.
        */

        setTimeout(
            () => {
                update(
                    currentLocale()
                );
            },
            250
        );


        setTimeout(
            () => {
                update(
                    currentLocale()
                );
            },
            1000
        );
    }


    if (
        document.readyState
        ===
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

})();
