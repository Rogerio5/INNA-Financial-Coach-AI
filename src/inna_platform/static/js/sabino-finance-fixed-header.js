(function () {

    "use strict";


    if (
        window.SabinoFinanceFixedHeaderGlobalV1
    ) {
        return;
    }


    window.SabinoFinanceFixedHeaderGlobalV1 =
        true;


    const USER_LABELS = {

        "pt": "Usuário",
        "en": "User",
        "es": "Usuario",
        "de": "Benutzer",
        "fr": "Utilisateur",
        "it": "Utente",
        "ru": "Пользователь",
        "ar": "المستخدم",
        "ro": "Utilizator",
        "uk": "Користувач"

    };


    const ACTIVE_LABELS = {

        "pt": "Ativo",
        "en": "Active",
        "es": "Activo",
        "de": "Aktiv",
        "fr": "Actif",
        "it": "Attivo",
        "ru": "Активен",
        "ar": "نشط",
        "ro": "Activ",
        "uk": "Активний"

    };


    function normalize(
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


    function visible(
        element
    ) {

        if (!element) {
            return false;
        }


        const style =
            window.getComputedStyle(
                element
            );


        const rect =
            element
            .getBoundingClientRect();


        return (
            style.display !==
                "none"
            &&
            style.visibility !==
                "hidden"
            &&
            rect.width > 0
            &&
            rect.height > 0
        );

    }


    function currentLanguage() {

        let locale =
            document.documentElement.lang
            ||
            "pt-BR";


        try {

            if (
                window.SabinoLocale
                &&
                typeof
                    window.SabinoLocale.current
                    ===
                    "function"
            ) {

                locale =
                    window.SabinoLocale.current()
                    ||
                    locale;

            }

        }
        catch (_) {
        }


        return String(locale)
            .split("-")[0]
            .toLowerCase();

    }


    function languageSwitcher() {

        return document.getElementById(
            "sabinoLanguageSwitcher"
        );

    }


    function containsInna(
        element
    ) {

        const value =
            normalize(
                element?.textContent
            )
            .toLowerCase();


        return (
            value.includes(
                "perguntar a inna"
            )
            ||
            value.includes(
                "ask inna"
            )
            ||
            value.includes(
                "inna >"
            )
        );

    }


    function avatarLeaf(
        element
    ) {

        if (!element) {
            return false;
        }


        const candidates = [
            element,
            ...element.querySelectorAll(
                "*"
            )
        ];


        return candidates.some(
            function (
                candidate
            ) {

                if (
                    candidate.children.length
                    !== 0
                ) {
                    return false;
                }


                const value =
                    normalize(
                        candidate.textContent
                    );


                if (
                    !/^[A-Z]{2}$/.test(
                        value
                    )
                ) {
                    return false;
                }


                const rect =
                    candidate
                    .getBoundingClientRect();


                return (
                    rect.width >= 20
                    &&
                    rect.width <= 70
                    &&
                    rect.height >= 20
                    &&
                    rect.height <= 70
                );

            }
        );

    }


    function existingUser() {

        return (
            document.querySelector(
                '[data-sabino-finance-fixed-user="true"]'
            )
            ||
            document.querySelector(
                '[data-sabino-finance-user-final="true"]'
            )
            ||
            null
        );

    }


    function findUser() {

        const existing =
            existingUser();


        if (existing) {
            return existing;
        }


        const locale =
            languageSwitcher();


        /*
         * Começamos pelos elementos de avatar:
         * TC, SA, RS etc.
         */

        const seeds =
            Array.from(
                document.querySelectorAll(
                    "body *"
                )
            )
            .filter(
                function (
                    element
                ) {

                    if (
                        element.children.length
                        !== 0
                    ) {
                        return false;
                    }


                    if (
                        !visible(
                            element
                        )
                    ) {
                        return false;
                    }


                    const value =
                        normalize(
                            element.textContent
                        );


                    return /^[A-Z]{2}$/.test(
                        value
                    );

                }
            );


        let best =
            null;


        let bestArea =
            Number.POSITIVE_INFINITY;


        seeds.forEach(
            function (
                seed
            ) {

                let current =
                    seed;


                for (
                    let level = 0;
                    level < 7 &&
                    current;
                    level += 1
                ) {

                    if (
                        locale
                        &&
                        current.contains(
                            locale
                        )
                    ) {
                        break;
                    }


                    if (
                        containsInna(
                            current
                        )
                    ) {
                        break;
                    }


                    const rect =
                        current
                        .getBoundingClientRect();


                    const value =
                        normalize(
                            current.textContent
                        );


                    const looksLikeAccount =
                        (
                            value.includes(
                                "Premium"
                            )
                            ||
                            value.includes(
                                "@local.test"
                            )
                            ||
                            value.includes(
                                "browser-"
                            )
                            ||
                            value.includes(
                                "Conta Sabino.AI"
                            )
                            ||
                            value.includes(
                                "Usuário"
                            )
                            ||
                            value.includes(
                                "User"
                            )
                        );


                    if (
                        looksLikeAccount
                        &&
                        avatarLeaf(
                            current
                        )
                        &&
                        rect.width >= 80
                        &&
                        rect.width <= 420
                        &&
                        rect.height >= 25
                        &&
                        rect.height <= 110
                    ) {

                        const area =
                            rect.width
                            *
                            rect.height;


                        if (
                            area <
                            bestArea
                        ) {

                            best =
                                current;


                            bestArea =
                                area;

                        }

                    }


                    current =
                        current.parentElement;

                }

            }
        );


        return best;

    }


    function compactUser(
        user
    ) {

        if (!user) {
            return;
        }


        const language =
            currentLanguage();


        const userLabel =
            USER_LABELS[language]
            ||
            USER_LABELS.pt;


        const activeLabel =
            ACTIVE_LABELS[language]
            ||
            ACTIVE_LABELS.pt;


        const leaves =
            Array.from(
                user.querySelectorAll(
                    "span, strong, div"
                )
            );


        leaves.forEach(
            function (
                element
            ) {

                if (
                    element.children.length
                    !== 0
                ) {
                    return;
                }


                const value =
                    normalize(
                        element.textContent
                    );


                /*
                 * Identidade técnica.
                 */

                if (
                    value.includes(
                        "@local.test"
                    )
                    ||
                    value.includes(
                        "browser-"
                    )
                    ||
                    element.hasAttribute(
                        "data-sabino-finance-user-name"
                    )
                ) {

                    if (
                        !element.dataset
                            .sabinoOriginalIdentity
                    ) {

                        element.dataset
                            .sabinoOriginalIdentity =
                            value;

                    }


                    element.textContent =
                        userLabel;


                    element.setAttribute(
                        "data-sabino-finance-user-name",
                        "true"
                    );

                }


                /*
                 * Premium · status.
                 */

                if (
                    value.includes(
                        "Premium"
                    )
                    &&
                    !element.hasAttribute(
                        "data-sabino-finance-plan"
                    )
                ) {

                    element.setAttribute(
                        "data-sabino-finance-plan",
                        "true"
                    );

                }


                if (
                    element.hasAttribute(
                        "data-sabino-finance-plan"
                    )
                ) {

                    element.textContent =
                        "Premium · "
                        +
                        activeLabel;

                }

            }
        );

    }


    function mountFixedHeader() {

        const locale =
            languageSwitcher();


        const user =
            findUser();


        /*
         * Idioma sempre sai de qualquer
         * container que role.
         */

        if (locale) {

            if (
                locale.parentElement !==
                document.body
            ) {

                document.body.appendChild(
                    locale
                );

            }


            locale.setAttribute(
                "data-sabino-finance-fixed-language",
                "true"
            );

        }


        /*
         * Usuário idem.
         */

        if (user) {

            if (
                user.parentElement !==
                document.body
            ) {

                document.body.appendChild(
                    user
                );

            }


            user.setAttribute(
                "data-sabino-finance-fixed-user",
                "true"
            );


            compactUser(
                user
            );

        }


        /*
         * Ajuste do idioma quando não existir
         * conta visível na página.
         */

        if (locale) {

            if (user) {

                locale.removeAttribute(
                    "data-sabino-finance-fixed-solo"
                );

            }
            else {

                locale.setAttribute(
                    "data-sabino-finance-fixed-solo",
                    "true"
                );

            }

        }


        return Boolean(
            locale
            ||
            user
        );

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
                    mountFixedHeader,
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
     * Troca entre os 12 idiomas.
     */

    window.addEventListener(
        "sabino:locale-change",
        refresh
    );


    window.addEventListener(
        "sabino:money-localized",
        function () {

            window.setTimeout(
                mountFixedHeader,
                50
            );

        }
    );


    window.addEventListener(
        "resize",
        function () {

            window.setTimeout(
                mountFixedHeader,
                50
            );

        }
    );


    window.SabinoFinanceFixedHeader = {

        refresh:
            refresh

    };

})();
