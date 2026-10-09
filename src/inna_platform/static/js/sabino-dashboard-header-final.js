(function () {

    "use strict";

    let accountName = "";
    fetch("/auth/profile", {credentials: "same-origin", cache: "no-store"})
        .then(response => response.ok ? response.json() : null)
        .then(data => {
            accountName = data && data.user ? data.user.name || data.user.email : "";
            refresh();
        })
        .catch(() => {});


    if (
        window.SabinoDashboardHeaderFinalV2
    ) {
        return;
    }


    window.SabinoDashboardHeaderFinalV2 =
        true;


    const LABELS = {

        "pt-BR": [
            "Usuário",
            "Conta Sabino.AI"
        ],

        "en-US": [
            "User",
            "Sabino.AI Account"
        ],

        "en-GB": [
            "User",
            "Sabino.AI Account"
        ],

        "es-ES": [
            "Usuario",
            "Cuenta Sabino.AI"
        ],

        "de-DE": [
            "Benutzer",
            "Sabino.AI Konto"
        ],

        "fr-FR": [
            "Utilisateur",
            "Compte Sabino.AI"
        ],

        "it-IT": [
            "Utente",
            "Account Sabino.AI"
        ],

        "ru-RU": [
            "Пользователь",
            "Аккаунт Sabino.AI"
        ],

        "ar-SA": [
            "المستخدم",
            "حساب Sabino.AI"
        ],

        "ro-RO": [
            "Utilizator",
            "Cont Sabino.AI"
        ],

        "uk-UA": [
            "Користувач",
            "Обліковий запис Sabino.AI"
        ],

        "de-CH": [
            "Benutzer",
            "Sabino.AI Konto"
        ]

    };


    const ACCOUNT_WORDS = [

        "Conta Sabino.AI",
        "Sabino.AI Account",
        "Cuenta Sabino.AI",
        "Sabino.AI Konto",
        "Compte Sabino.AI",
        "Account Sabino.AI",
        "Аккаунт Sabino.AI",
        "حساب Sabino.AI",
        "Cont Sabino.AI",
        "Обліковий запис Sabino.AI"

    ];


    function norm(
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


    function currentLocale() {

        let value =
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

                value =
                    window.SabinoLocale.current()
                    ||
                    value;

            }

        }
        catch (_) {
        }


        value =
            String(value)
            .replace(
                "_",
                "-"
            );


        const parts =
            value.split("-");


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


        const base =
            parts[0].toLowerCase();


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
            fallback[base]
            ||
            "pt-BR"
        );

    }


    function hasInitials(
        element
    ) {

        return Array.from(
            element.querySelectorAll(
                "*"
            )
        )
        .some(
            function (
                node
            ) {

                return (
                    node.children.length
                    ===
                    0
                    &&
                    /^[A-Z]{2}$/.test(
                        norm(
                            node.textContent
                        )
                    )
                );

            }
        );

    }


    function findUser() {

        const marked =
            document.querySelector(
                '[data-sabino-dashboard-user-final="true"]'
            );


        if (marked) {
            return marked;
        }


        const leaves =
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
                        !==
                        0
                    ) {
                        return false;
                    }


                    const text =
                        norm(
                            element.textContent
                        );


                    return (
                        text.includes(
                            "@local.test"
                        )
                        ||
                        text.includes(
                            "browser-"
                        )
                        ||
                        ACCOUNT_WORDS.includes(
                            text
                        )
                    );

                }
            );


        for (
            const leaf
            of leaves
        ) {

            let current =
                leaf.parentElement;


            for (
                let level = 0;
                level < 6 &&
                current;
                level += 1
            ) {

                const rect =
                    current
                    .getBoundingClientRect();


                if (
                    hasInitials(
                        current
                    )
                    &&
                    rect.width >= 80
                    &&
                    rect.width <= 380
                    &&
                    rect.height >= 25
                    &&
                    rect.height <= 110
                ) {

                    return current;

                }


                current =
                    current.parentElement;

            }

        }


        return null;

    }


    function ensureHeader() {

        let header =
            document.getElementById(
                "sabinoDashboardHeaderFinal"
            );


        if (!header) {

            header =
                document.createElement(
                    "div"
                );


            header.id =
                "sabinoDashboardHeaderFinal";


            document.body.appendChild(
                header
            );

        }


        return header;

    }


    function hideLegacySelector() {

        Array.from(
            document.querySelectorAll(
                "button, a, div, span"
            )
        )
        .forEach(
            function (
                element
            ) {

                if (
                    element.closest(
                        "#sabinoLanguageSwitcher"
                    )
                ) {
                    return;
                }


                if (
                    element.children.length
                    >
                    2
                ) {
                    return;
                }


                const text =
                    norm(
                        element.textContent
                    );


                if (
                    !/^[A-Z]{2}(?:-[A-Z]{2})?\s*[▾▼⌄]?$/.test(
                        text
                    )
                ) {
                    return;
                }


                const rect =
                    element
                    .getBoundingClientRect();


                if (
                    rect.top < 100
                    &&
                    rect.left >
                        window.innerWidth
                        *
                        0.55
                    &&
                    rect.width < 130
                ) {

                    element.style.setProperty(
                        "display",
                        "none",
                        "important"
                    );

                }

            }
        );

    }


    function localizeUser(
        user
    ) {

        const dict =
            LABELS[
                currentLocale()
            ]
            ||
            LABELS["pt-BR"];


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


        let name =
            user.querySelector(
                '[data-sabino-dashboard-user-name="true"]'
            );


        if (!name) {

            name =
                leaves.find(
                    function (
                        element
                    ) {

                        const text =
                            norm(
                                element.textContent
                            );


                        return (
                            text.includes(
                                "@local.test"
                            )
                            ||
                            text.includes(
                                "browser-"
                            )
                            ||
                            [
                                "Usuário",
                                "User",
                                "Usuario",
                                "Benutzer",
                                "Utilisateur",
                                "Utente",
                                "Пользователь",
                                "المستخدم",
                                "Utilizator",
                                "Користувач"
                            ]
                            .includes(
                                text
                            )
                        );

                    }
                );

        }


        if (name) {

            if (
                !name.dataset
                    .sabinoOriginalIdentity
            ) {

                name.dataset
                    .sabinoOriginalIdentity =
                    norm(
                        name.textContent
                    );

            }


            name.textContent =
                accountName || dict[0];

            name.setAttribute("translate", "no");
            name.style.maxWidth = "170px";
            name.style.overflow = "hidden";
            name.style.textOverflow = "ellipsis";
            name.style.whiteSpace = "nowrap";
            name.title = accountName || dict[0];


            name.setAttribute(
                "data-sabino-dashboard-user-name",
                "true"
            );

        }


        let account =
            user.querySelector(
                '[data-sabino-dashboard-account-label="true"]'
            );


        if (!account) {

            account =
                leaves.find(
                    function (
                        element
                    ) {

                        return ACCOUNT_WORDS.includes(
                            norm(
                                element.textContent
                            )
                        );

                    }
                );

        }


        if (account) {

            account.textContent =
                dict[1];


            account.setAttribute(
                "data-sabino-dashboard-account-label",
                "true"
            );

        }


        user.setAttribute(
            "data-sabino-dashboard-user-final",
            "true"
        );

    }


    function apply() {

        const language =
            document.getElementById(
                "sabinoLanguageSwitcher"
            );


        const user =
            findUser();


        if (
            !language
            ||
            !user
        ) {

            hideLegacySelector();

            return false;

        }


        const header =
            ensureHeader();


        header.appendChild(
            language
        );


        header.appendChild(
            user
        );

        // The legacy anchor also runs on load; keep this child in the flex row.
        user.style.setProperty("position", "relative", "important");
        user.style.setProperty("inset", "auto", "important");


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


        localizeUser(
            user
        );


        hideLegacySelector();


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
                    apply,
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


    window.addEventListener(
        "sabino:locale-change",
        refresh
    );

    window.addEventListener("load", refresh, { once: true });


    window.addEventListener(
        "sabino:money-localized",
        function () {

            window.setTimeout(
                apply,
                50
            );

        }
    );

})();
