(function () {

    "use strict";


    if (window.SabinoFinanceUnifiedV1) {
        return;
    }


    window.SabinoFinanceUnifiedV1 = true;


    const LABELS = {

        "pt-BR": {
            user: "Usuário",
            account: "Conta Sabino.AI",
            status: "Premium · Ativo"
        },

        "en-US": {
            user: "User",
            account: "Sabino.AI Account",
            status: "Premium · Active"
        },

        "en-GB": {
            user: "User",
            account: "Sabino.AI Account",
            status: "Premium · Active"
        },

        "es-ES": {
            user: "Usuario",
            account: "Cuenta Sabino.AI",
            status: "Premium · Activo"
        },

        "de-DE": {
            user: "Benutzer",
            account: "Sabino.AI Konto",
            status: "Premium · Aktiv"
        },

        "fr-FR": {
            user: "Utilisateur",
            account: "Compte Sabino.AI",
            status: "Premium · Actif"
        },

        "it-IT": {
            user: "Utente",
            account: "Account Sabino.AI",
            status: "Premium · Attivo"
        },

        "ru-RU": {
            user: "Пользователь",
            account: "Аккаунт Sabino.AI",
            status: "Premium · Активен"
        },

        "ar-SA": {
            user: "المستخدم",
            account: "حساب Sabino.AI",
            status: "مميز · نشط"
        },

        "ro-RO": {
            user: "Utilizator",
            account: "Cont Sabino.AI",
            status: "Premium · Activ"
        },

        "uk-UA": {
            user: "Користувач",
            account: "Обліковий запис Sabino.AI",
            status: "Premium · Активний"
        },

        "de-CH": {
            user: "Benutzer",
            account: "Sabino.AI Konto",
            status: "Premium · Aktiv"
        }

    };


    const USER_NAMES = new Set([
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
    ]);


    const STATUS_WORDS = [
        "Premium · Ativo",
        "Premium · Active",
        "Premium · Activo",
        "Premium · Aktiv",
        "Premium · Actif",
        "Premium · Attivo",
        "Premium · Активен",
        "مميز · نشط",
        "Premium · Activ",
        "Premium · Активний"
    ];


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


    const ARABIC_RE =
        /[\u0600-\u06FF]/;


    function norm(value) {

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


        locale =
            String(locale)
                .replace("_", "-");


        const parts =
            locale.split("-");


        if (parts.length >= 2) {

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
                locale.toLowerCase()
            ]
            ||
            "pt-BR"
        );
    }


    function labels() {

        return (
            LABELS[currentLocale()]
            ||
            LABELS["pt-BR"]
        );
    }


    function hasInitials(element) {

        return Array.from(
            element.querySelectorAll("*")
        )
        .some(function (candidate) {

            if (candidate.children.length !== 0) {
                return false;
            }


            return /^[A-Z]{2}$/.test(
                norm(candidate.textContent)
            );
        });
    }


    function findUser() {

        const marked =
            document.querySelector(
                '[data-sabino-finance-unified-user="true"],' +
                '[data-sabino-finance-user-final="true"],' +
                '[data-sabino-finance-fixed-user="true"]'
            );


        if (marked) {
            return marked;
        }


        const leaves =
            Array.from(
                document.querySelectorAll("body *")
            )
            .filter(function (element) {

                if (element.children.length !== 0) {
                    return false;
                }


                const text =
                    norm(element.textContent);


                return (
                    text.includes("@local.test")
                    ||
                    text.includes("browser-")
                    ||
                    USER_NAMES.has(text)
                    ||
                    STATUS_WORDS.includes(text)
                    ||
                    ACCOUNT_WORDS.includes(text)
                );
            });


        for (const leaf of leaves) {

            let current =
                leaf.parentElement;


            for (
                let level = 0;
                level < 6 && current;
                level += 1
            ) {

                const text =
                    norm(current.textContent);


                if (
                    text.includes("Perguntar a INNA")
                ) {

                    current =
                        current.parentElement;

                    continue;
                }


                const rect =
                    current.getBoundingClientRect();


                if (
                    hasInitials(current)
                    &&
                    rect.width >= 80
                    &&
                    rect.width <= 380
                    &&
                    rect.height >= 25
                    &&
                    rect.height <= 115
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
                "sabinoFinanceUnifiedHeader"
            );


        if (!header) {

            header =
                document.createElement("div");


            header.id =
                "sabinoFinanceUnifiedHeader";


            document.body.appendChild(
                header
            );
        }


        return header;
    }


    function localizeUser(user) {

        const dictionary =
            labels();


        user.setAttribute(
            "data-sabino-finance-unified-user",
            "true"
        );


        const leaves =
            Array.from(
                user.querySelectorAll(
                    "span, strong, small, div"
                )
            )
            .filter(function (element) {

                return (
                    element.children.length === 0
                );
            });


        let name =
            user.querySelector(
                '[data-sabino-finance-user-name="true"]'
            );


        if (!name) {

            name =
                leaves.find(function (element) {

                    const text =
                        norm(element.textContent);


                    return (
                        text.includes("@local.test")
                        ||
                        text.includes("browser-")
                        ||
                        USER_NAMES.has(text)
                    );
                });
        }


        if (name) {

            if (
                !name.dataset
                    .sabinoOriginalIdentity
            ) {

                name.dataset
                    .sabinoOriginalIdentity =
                    norm(name.textContent);
            }


            name.textContent =
                dictionary.user;


            name.setAttribute(
                "data-sabino-finance-user-name",
                "true"
            );
        }


        let subtitle =
            user.querySelector(
                '[data-sabino-finance-user-subtitle="true"]'
            );


        if (!subtitle) {

            subtitle =
                leaves.find(function (element) {

                    const text =
                        norm(element.textContent);


                    return (
                        element !== name
                        &&
                        (
                            STATUS_WORDS.includes(text)
                            ||
                            ACCOUNT_WORDS.includes(text)
                        )
                    );
                });
        }


        if (subtitle) {

            const current =
                norm(subtitle.textContent);


            if (
                STATUS_WORDS.includes(current)
            ) {

                subtitle.textContent =
                    dictionary.status;
            }
            else {

                subtitle.textContent =
                    dictionary.account;
            }


            subtitle.setAttribute(
                "data-sabino-finance-user-subtitle",
                "true"
            );
        }
    }


    function hideLegacyLocale() {

        Array.from(
            document.querySelectorAll(
                "button, a, span, div"
            )
        )
        .forEach(function (element) {

            if (
                element.closest(
                    "#sabinoLanguageSwitcher"
                )
            ) {
                return;
            }


            if (element.children.length > 2) {
                return;
            }


            const text =
                norm(element.textContent);


            if (
                !/^[A-Z]{2}(?:-[A-Z]{2})?\s*[▾▼⌄]?$/.test(
                    text
                )
            ) {
                return;
            }


            const rect =
                element.getBoundingClientRect();


            if (
                rect.top < 110
                &&
                rect.left >
                    window.innerWidth * 0.55
                &&
                rect.width < 130
            ) {

                element.style.setProperty(
                    "display",
                    "none",
                    "important"
                );
            }
        });
    }


    function hideOnlineStatus() {

        Array.from(
            document.querySelectorAll(
                "span, small, div, p"
            )
        )
        .forEach(function (element) {

            if (element.children.length !== 0) {
                return;
            }


            const text =
                norm(element.textContent)
                    .toLowerCase();


            if (
                text === "sabino.ai online"
                ||
                text === "sabino.ai está online"
            ) {

                element.style.setProperty(
                    "display",
                    "none",
                    "important"
                );
            }
        });
    }


    function resetArabicText() {

        document.documentElement
            .classList
            .remove(
                "sabino-finance-arabic"
            );


        document
            .querySelectorAll(
                '[data-sabino-finance-arabic-text="true"]'
            )
            .forEach(function (element) {

                element.removeAttribute(
                    "data-sabino-finance-arabic-text"
                );


                if (
                    element.getAttribute("dir")
                    ===
                    "rtl"
                ) {

                    element.removeAttribute(
                        "dir"
                    );
                }
            });
    }


    function applyArabic() {

        resetArabicText();


        /*
         * Estrutura da aplicação permanece
         * igual ao Português para todos os idiomas.
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


        if (
            currentLocale()
            !==
            "ar-SA"
        ) {

            return;
        }


        document.documentElement
            .classList
            .add(
                "sabino-finance-arabic"
            );


        Array.from(
            document.querySelectorAll(
                "h1, h2, h3, h4, h5, h6, " +
                "p, span, strong, small, label, " +
                "a, button, div"
            )
        )
        .forEach(function (element) {

            if (
                element.children.length !== 0
            ) {
                return;
            }


            const text =
                norm(element.textContent);


            if (!text) {
                return;
            }


            if (
                ARABIC_RE.test(text)
            ) {

                element.setAttribute(
                    "data-sabino-finance-arabic-text",
                    "true"
                );


                element.setAttribute(
                    "dir",
                    "rtl"
                );
            }


            if (
                text === "INNA"
                ||
                text === "Sabino.AI"
            ) {

                element.setAttribute(
                    "data-sabino-finance-ltr-brand",
                    "true"
                );
            }
        });
    }


    function mountHeader() {
        if (document.documentElement.dataset.financeHeader === "flow") return true;

        const language =
            document.getElementById(
                "sabinoLanguageSwitcher"
            );


        /*
         * O idioma deve ser montado mesmo quando
         * não existe usuário na página.
         *
         * Isso é fundamental no modo DEMO.
         */

        if (!language) {

            hideLegacyLocale();

            return false;
        }


        const header =
            ensureHeader();


        /*
         * Garantir que o dock fique diretamente
         * ligado ao body e preso ao viewport.
         */

        if (
            header.parentElement !==
            document.body
        ) {

            document.body.appendChild(
                header
            );
        }


        header.style.setProperty(
            "position",
            "fixed",
            "important"
        );

        header.style.setProperty(
            "top",
            "18px",
            "important"
        );

        header.style.setProperty(
            "right",
            "28px",
            "important"
        );

        header.style.setProperty(
            "z-index",
            "2147483000",
            "important"
        );


        /*
         * Idioma sempre entra primeiro.
         */

        /* LANGUAGE_OWNED_BY_PORTAL_V6 */


        language.style.setProperty(
            "position",
            "relative",
            "important"
        );

        language.style.setProperty(
            "top",
            "auto",
            "important"
        );

        language.style.setProperty(
            "right",
            "auto",
            "important"
        );

        language.style.setProperty(
            "left",
            "auto",
            "important"
        );

        language.style.setProperty(
            "transform",
            "none",
            "important"
        );

        language.style.setProperty(
            "order",
            "1",
            "important"
        );


        /*
         * Usuário é opcional.
         *
         * Financeiro real:
         *     idioma | usuário
         *
         * Financeiro demo sem usuário:
         *     idioma
         */

        const user =
            findUser();


        if (user) {

            if (
                user.parentElement !==
                header
            ) {

                header.appendChild(
                    user
                );
            }


            user.style.setProperty(
                "order",
                "2",
                "important"
            );


            localizeUser(
                user
            );
        }


        return true;
    }


    function apply() {

        mountHeader();

        hideLegacyLocale();

        hideOnlineStatus();

        applyArabic();
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
                apply,
                delay
            );
        });
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


    window.addEventListener(
        "sabino:money-localized",
        function () {

            window.setTimeout(
                refresh,
                50
            );
        }
    );

})();


/* ============================================================
   SABINO_FINANCE_LANGUAGE_PORTAL_V2
   Um único owner para posição do idioma
   ============================================================ */

(function () {

    "use strict";


    if (document.documentElement.dataset.financeHeader === "flow") return;

    if (window.SabinoFinanceLanguagePortalV2) {
        return;
    }

    window.SabinoFinanceLanguagePortalV2 = true;


    const PORTAL_ID =
        "sabinoFinanceLanguagePortal";


    let applying = false;
    let scheduled = false;


    function ensurePortal() {

        let portal =
            document.getElementById(
                PORTAL_ID
            );


        if (!portal) {

            portal =
                document.createElement(
                    "div"
                );


            portal.id =
                PORTAL_ID;


            /*
             * Fica fora do BODY rolável.
             */

            document.documentElement
                .appendChild(
                    portal
                );
        }


        return portal;
    }


    function placeLanguage() {

        scheduled = false;


        if (applying) {
            return;
        }


        applying = true;


        try {

            const language =
                document.getElementById(
                    "sabinoLanguageSwitcher"
                );


            if (!language) {
                return;
            }


            const portal =
                ensurePortal();


            /*
             * Se qualquer outro runtime tentar colocar
             * o idioma dentro do header/main/card,
             * trazemos novamente ao portal.
             */

            if (
                language.parentElement !==
                portal
            ) {

                portal.appendChild(
                    language
                );
            }


            /*
             * O PORTAL é fixo.
             * O botão não precisa ser fixed.
             */

            language.style.setProperty(
                "position",
                "relative",
                "important"
            );

            language.style.setProperty(
                "top",
                "auto",
                "important"
            );

            language.style.setProperty(
                "right",
                "auto",
                "important"
            );

            language.style.setProperty(
                "bottom",
                "auto",
                "important"
            );

            language.style.setProperty(
                "left",
                "auto",
                "important"
            );

            language.style.setProperty(
                "margin",
                "0",
                "important"
            );

            language.style.setProperty(
                "transform",
                "none",
                "important"
            );

            language.style.setProperty(
                "pointer-events",
                "auto",
                "important"
            );

        }
        finally {

            applying = false;
        }
    }


    function schedule() {

        if (scheduled) {
            return;
        }


        scheduled = true;


        requestAnimationFrame(
            placeLanguage
        );
    }


    function boot() {

        placeLanguage();


        [
            50,
            150,
            350,
            700,
            1200,
            2000
        ]
        .forEach(function (delay) {

            window.setTimeout(
                placeLanguage,
                delay
            );

        });
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
        boot
    );


    window.addEventListener(
        "sabino:money-localized",
        boot
    );


    /*
     * Observa somente para impedir que outro runtime
     * roube o seletor de volta.
     */

    const observer =
        new MutationObserver(
            function () {

                const language =
                    document.getElementById(
                        "sabinoLanguageSwitcher"
                    );


                if (!language) {
                    return;
                }


                const portal =
                    document.getElementById(
                        PORTAL_ID
                    );


                if (
                    !portal ||
                    language.parentElement !== portal
                ) {

                    schedule();
                }

            }
        );


    observer.observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );

})();
