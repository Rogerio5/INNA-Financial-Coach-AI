(function () {

    "use strict";


    if (
        window.SabinoDashboardUserI18n12V1
    ) {
        return;
    }


    window.SabinoDashboardUserI18n12V1 =
        true;


    const DICTIONARY = {

        "pt-BR": {
            user: "Usuário",
            account: "Conta Sabino.AI"
        },

        "en-US": {
            user: "User",
            account: "Sabino.AI Account"
        },

        "en-GB": {
            user: "User",
            account: "Sabino.AI Account"
        },

        "es-ES": {
            user: "Usuario",
            account: "Cuenta Sabino.AI"
        },

        "de-DE": {
            user: "Benutzer",
            account: "Sabino.AI Konto"
        },

        "fr-FR": {
            user: "Utilisateur",
            account: "Compte Sabino.AI"
        },

        "it-IT": {
            user: "Utente",
            account: "Account Sabino.AI"
        },

        "ru-RU": {
            user: "Пользователь",
            account: "Аккаунт Sabino.AI"
        },

        "ar-SA": {
            user: "المستخدم",
            account: "حساب Sabino.AI"
        },

        "ro-RO": {
            user: "Utilizator",
            account: "Cont Sabino.AI"
        },

        "uk-UA": {
            user: "Користувач",
            account: "Обліковий запис Sabino.AI"
        },

        "de-CH": {
            user: "Benutzer",
            account: "Sabino.AI Konto"
        }

    };


    function normalizeLocale(
        value
    ) {

        const raw =
            String(
                value || "pt-BR"
            )
            .replace(
                "_",
                "-"
            )
            .trim();


        const parts =
            raw.split("-");


        if (
            parts.length >= 2
        ) {

            return (
                parts[0].toLowerCase()
                +
                "-"
                +
                parts[1].toUpperCase()
            );

        }


        const fallback = {

            pt: "pt-BR",
            en: "en-US",
            es: "es-ES",
            de: "de-DE",
            fr: "fr-FR",
            it: "it-IT",
            ru: "ru-RU",
            ar: "ar-SA",
            ro: "ro-RO",
            uk: "uk-UA"

        };


        return (
            fallback[
                raw.toLowerCase()
            ]
            ||
            "pt-BR"
        );

    }


    function currentLocale() {

        try {

            if (
                window.SabinoLocale
                &&
                typeof
                    window.SabinoLocale.current
                    ===
                    "function"
            ) {

                return normalizeLocale(
                    window.SabinoLocale.current()
                );

            }

        }
        catch (_) {
        }


        return normalizeLocale(
            document.documentElement.lang
        );

    }


    function normalizeText(
        value
    ) {

        return String(
            value || ""
        )
        .replace(
            /\s+/g,
            " "
        )
        .trim();

    }


    function findUserBlock() {

        return (
            document.querySelector(
                '[data-sabino-dashboard-user-final="true"]'
            )
            ||
            document.querySelector(
                "#sabinoDashboardHeaderFinal [data-sabino-dashboard-user-final]"
            )
            ||
            null
        );

    }


    function applyTranslation() {

        const user =
            findUserBlock();


        if (!user) {
            return false;
        }


        const locale =
            currentLocale();


        const dictionary =
            DICTIONARY[locale]
            ||
            DICTIONARY["pt-BR"];


        const leaves =
            Array.from(
                user.querySelectorAll(
                    "span, strong, div"
                )
            )
            .filter(
                function (
                    element
                ) {

                    return (
                        element.children.length
                        ===
                        0
                    );

                }
            );


        let nameElement =
            user.querySelector(
                '[data-sabino-dashboard-user-name="true"]'
            );


        /*
         * Caso o sistema recrie o nome,
         * localizamos novamente.
         */

        if (!nameElement) {

            nameElement =
                leaves.find(
                    function (
                        element
                    ) {

                        const value =
                            normalizeText(
                                element.textContent
                            );


                        return (
                            value.includes(
                                "@local.test"
                            )
                            ||
                            value.includes(
                                "browser-"
                            )
                            ||
                            value ===
                                "Usuário"
                            ||
                            value ===
                                "User"
                            ||
                            value ===
                                "Usuario"
                            ||
                            value ===
                                "Benutzer"
                            ||
                            value ===
                                "Utilisateur"
                            ||
                            value ===
                                "Utente"
                            ||
                            value ===
                                "Пользователь"
                            ||
                            value ===
                                "المستخدم"
                            ||
                            value ===
                                "Utilizator"
                            ||
                            value ===
                                "Користувач"
                        );

                    }
                );

        }


        if (nameElement) {

            if (
                !nameElement.dataset
                    .sabinoOriginalIdentity
            ) {

                nameElement.dataset
                    .sabinoOriginalIdentity =
                    normalizeText(
                        nameElement.textContent
                    );

            }


            nameElement.textContent =
                dictionary.user;


            nameElement.setAttribute(
                "data-sabino-dashboard-user-name",
                "true"
            );

        }


        /*
         * Segunda linha:
         * Conta Sabino.AI / Sabino.AI Konto etc.
         */

        let accountElement =
            user.querySelector(
                '[data-sabino-dashboard-account-label="true"]'
            );


        if (!accountElement) {

            accountElement =
                leaves.find(
                    function (
                        element
                    ) {

                        if (
                            element ===
                            nameElement
                        ) {
                            return false;
                        }


                        const value =
                            normalizeText(
                                element.textContent
                            );


                        return (
                            value.includes(
                                "Conta Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Sabino.AI Account"
                            )
                            ||
                            value.includes(
                                "Cuenta Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Sabino.AI Konto"
                            )
                            ||
                            value.includes(
                                "Compte Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Account Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Аккаунт Sabino.AI"
                            )
                            ||
                            value.includes(
                                "حساب Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Cont Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Обліковий запис Sabino.AI"
                            )
                        );

                    }
                );

        }


        if (accountElement) {

            accountElement.textContent =
                dictionary.account;


            accountElement.setAttribute(
                "data-sabino-dashboard-account-label",
                "true"
            );

        }


        /*
         * Mesmo tamanho e estrutura usados no Português.
         */

        user.style.setProperty(
            "min-width",
            "145px",
            "important"
        );


        user.style.setProperty(
            "max-width",
            "190px",
            "important"
        );


        user.style.setProperty(
            "overflow",
            "hidden",
            "important"
        );


        return true;

    }


    function refresh() {

        [
            0,
            100,
            300,
            700,
            1400
        ]
        .forEach(
            function (
                delay
            ) {

                window.setTimeout(
                    applyTranslation,
                    delay
                );

            }
        );

    }


    if (
        document.readyState
        ===
        "loading"
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
     * Toda troca entre os 12 idiomas
     * reaplica o mesmo padrão.
     */

    window.addEventListener(
        "sabino:locale-change",
        refresh
    );


    window.addEventListener(
        "sabino:money-localized",
        function () {

            window.setTimeout(
                applyTranslation,
                50
            );

        }
    );


    window.SabinoDashboardUserI18n12 = {

        refresh:
            refresh

    };

})();
