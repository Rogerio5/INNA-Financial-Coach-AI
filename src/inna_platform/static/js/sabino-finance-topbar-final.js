(function () {

    "use strict";

    const DOCK_ID =
        "sabinoFinanceTopbarFinal";


    function text(el) {

        return String(
            el?.textContent || ""
        )
        .replace(/\s+/g, " ")
        .trim();

    }


    function visible(el) {

        if (!el) return false;

        const s =
            getComputedStyle(el);

        const r =
            el.getBoundingClientRect();

        return (
            s.display !== "none" &&
            s.visibility !== "hidden" &&
            r.width > 0 &&
            r.height > 0
        );

    }


    function language() {

        return document.getElementById(
            "sabinoLanguageSwitcher"
        );

    }


    function containsInna(el) {

        return text(el)
            .toLowerCase()
            .includes(
                "perguntar a inna"
            );

    }


    function hasInitials(el) {

        if (!el) return false;

        const all = [
            el,
            ...el.querySelectorAll("*")
        ];


        return all.some(function (item) {

            if (
                item.children.length !== 0
            ) {
                return false;
            }


            const value =
                text(item);


            if (
                !/^[A-Z]{2}$/.test(value)
            ) {
                return false;
            }


            const r =
                item.getBoundingClientRect();


            return (
                r.width >= 20 &&
                r.width <= 70 &&
                r.height >= 20 &&
                r.height <= 70
            );

        });

    }


    function findUser() {

        const lang =
            language();


        const candidates =
            Array.from(
                document.querySelectorAll(
                    "body *"
                )
            )
            .filter(function (el) {

                if (!visible(el)) {
                    return false;
                }


                if (
                    lang &&
                    el.contains(lang)
                ) {
                    return false;
                }


                if (
                    containsInna(el)
                ) {
                    return false;
                }


                const value =
                    text(el);


                return (
                    value.includes("Premium") &&
                    (
                        value.includes("Ativo") ||
                        value.includes("Active")
                    )
                );

            });


        /*
         * Menor elemento primeiro.
         */

        candidates.sort(
            function (a, b) {

                const ar =
                    a.getBoundingClientRect();

                const br =
                    b.getBoundingClientRect();

                return (
                    ar.width * ar.height
                    -
                    br.width * br.height
                );

            }
        );


        for (
            const candidate
            of candidates
        ) {

            let current =
                candidate;


            for (
                let level = 0;
                level < 7 && current;
                level += 1
            ) {

                const r =
                    current.getBoundingClientRect();


                if (
                    lang &&
                    current.contains(lang)
                ) {
                    break;
                }


                if (
                    containsInna(current)
                ) {
                    break;
                }


                if (
                    r.width >= 90 &&
                    r.width <= 350 &&
                    r.height >= 25 &&
                    r.height <= 100 &&
                    hasInitials(current)
                ) {

                    return current;

                }


                current =
                    current.parentElement;

            }

        }


        return null;

    }


    function dock() {

        let el =
            document.getElementById(
                DOCK_ID
            );


        if (el) {
            return el;
        }


        el =
            document.createElement(
                "div"
            );


        el.id =
            DOCK_ID;


        el.setAttribute(
            "aria-label",
            "Idioma e conta"
        );


        document.body.appendChild(
            el
        );


        return el;

    }


    function resetPosition(el) {

        [
            "top",
            "right",
            "bottom",
            "left"
        ].forEach(
            function (property) {

                el.style.setProperty(
                    property,
                    "auto",
                    "important"
                );

            }
        );


        el.style.setProperty(
            "position",
            "relative",
            "important"
        );


        el.style.setProperty(
            "transform",
            "none",
            "important"
        );


        el.style.setProperty(
            "margin",
            "0",
            "important"
        );

    }


    function apply() {

        const lang =
            language();


        const user =
            findUser();


        if (
            !lang ||
            !user
        ) {

            return false;

        }


        const container =
            dock();


        user.setAttribute(
            "data-sabino-finance-user-final",
            "true"
        );


        /*
         * ORDEM FÍSICA:
         *
         * 1 - idioma
         * 2 - usuário
         */

        container.appendChild(
            lang
        );


        container.appendChild(
            user
        );


        resetPosition(
            lang
        );


        resetPosition(
            user
        );


        lang.style.setProperty(
            "order",
            "1",
            "important"
        );


        user.style.setProperty(
            "order",
            "2",
            "important"
        );


        console.info(
            "SABINO_FINANCE_TOPBAR_FINAL_V1=READY"
        );


        return true;

    }


    function start() {

        apply();

        setTimeout(
            apply,
            250
        );

        setTimeout(
            apply,
            750
        );

        setTimeout(
            apply,
            1500
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            start,
            { once: true }
        );

    }
    else {

        start();

    }

})();

/* SABINO_FINANCE_USER_COMPACT_V1 */

(function () {

    "use strict";


    function normalize(value) {

        return String(value || "")
            .replace(/\s+/g, " ")
            .trim();

    }


    function shortNameFromText(value) {

        const text =
            normalize(value);


        /*
         * Se for e-mail técnico/local,
         * não mostramos no header.
         */

        if (
            text.includes("@local.test")
            ||
            text.includes("browser-")
        ) {

            return "Usuário";

        }


        /*
         * Se for e-mail normal, pega apenas
         * a parte antes do @ e limpa.
         */

        if (
            text.includes("@")
        ) {

            const local =
                text
                .split("@")[0]
                .replace(/[._-]+/g, " ")
                .replace(/\d+/g, " ")
                .replace(/\s+/g, " ")
                .trim();


            if (local) {

                return local
                    .split(" ")
                    .filter(Boolean)
                    .map(
                        word =>
                            word.charAt(0).toUpperCase()
                            +
                            word.slice(1).toLowerCase()
                    )
                    .join(" ");

            }

        }


        return text || "Usuário";

    }


    function compactUser() {

        const user =
            document.querySelector(
                '[data-sabino-finance-user-final="true"]'
            );


        if (!user) {
            return false;
        }


        /*
         * Procura textos visíveis dentro do bloco.
         */

        const elements =
            Array.from(
                user.querySelectorAll(
                    "span, strong, div"
                )
            );


        let primary = null;


        for (
            const el
            of elements
        ) {

            if (
                el.children.length > 0
            ) {
                continue;
            }


            const text =
                normalize(
                    el.textContent
                );


            if (!text) {
                continue;
            }


            /*
             * Não mexer em:
             * avatar
             * Premium
             * Ativo
             */

            if (
                /^[A-Z]{2}$/.test(text)
                ||
                text.includes("Premium")
                ||
                text === "Ativo"
                ||
                text === "Active"
            ) {
                continue;
            }


            if (
                text.includes("@")
                ||
                text.includes("browser-")
            ) {

                primary = el;

                break;

            }

        }


        if (primary) {

            primary.setAttribute(
                "data-sabino-user-name",
                "true"
            );


            primary.setAttribute(
                "title",
                primary.textContent.trim()
            );


            primary.textContent =
                shortNameFromText(
                    primary.textContent
                );

        }


        /*
         * Marcar metadado Premium · Ativo,
         * quando estiver no mesmo elemento.
         */

        for (
            const el
            of elements
        ) {

            const text =
                normalize(
                    el.textContent
                );


            if (
                text.includes("Premium")
                &&
                (
                    text.includes("Ativo")
                    ||
                    text.includes("Active")
                )
            ) {

                el.classList.add(
                    "user-meta"
                );

            }

        }


        return true;

    }


    function run() {

        compactUser();

        setTimeout(
            compactUser,
            200
        );

        setTimeout(
            compactUser,
            700
        );

        setTimeout(
            compactUser,
            1500
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            run,
            { once: true }
        );

    }
    else {

        run();

    }

})();


/* ============================================================
   SABINO_FINANCE_HEADER_LOCALE_PERSIST_V1

   Mantém:
   [ Idioma ] [ Usuário compacto ]

   mesmo depois da troca de idioma.
   ============================================================ */

(function () {

    "use strict";


    function normalize(value) {

        return String(value || "")
            .replace(/\s+/g, " ")
            .trim();

    }


    function currentLocale() {

        try {

            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current === "function"
            ) {

                return String(
                    window.SabinoLocale.current() || "pt-BR"
                );

            }

        }
        catch (_) {
        }


        return (
            document.documentElement.lang
            ||
            "pt-BR"
        );

    }


    function genericUserLabel() {

        const locale =
            currentLocale()
            .toLowerCase();


        if (locale.startsWith("en")) {
            return "User";
        }

        if (locale.startsWith("es")) {
            return "Usuario";
        }

        if (locale.startsWith("de")) {
            return "Benutzer";
        }

        if (locale.startsWith("fr")) {
            return "Utilisateur";
        }

        if (locale.startsWith("it")) {
            return "Utente";
        }

        if (locale.startsWith("ru")) {
            return "Пользователь";
        }

        if (locale.startsWith("ar")) {
            return "المستخدم";
        }

        if (locale.startsWith("ro")) {
            return "Utilizator";
        }

        if (locale.startsWith("uk")) {
            return "Користувач";
        }


        return "Usuário";

    }


    function language() {

        return document.getElementById(
            "sabinoLanguageSwitcher"
        );

    }


    function dock() {

        return document.getElementById(
            "sabinoFinanceTopbarFinal"
        );

    }


    function findUser() {

        /*
         * Primeiro tenta reutilizar o usuário
         * que já foi identificado anteriormente.
         */

        let user =
            document.querySelector(
                '[data-sabino-finance-user-final="true"]'
            );


        if (user) {
            return user;
        }


        /*
         * Caso o sistema de idiomas tenha reconstruído
         * o bloco, localizamos novamente.
         */

        const lang =
            language();


        const candidates =
            Array.from(
                document.querySelectorAll(
                    "body *"
                )
            );


        for (
            const candidate
            of candidates
        ) {

            const text =
                normalize(
                    candidate.textContent
                );


            if (
                !text.includes("Premium")
            ) {
                continue;
            }


            if (
                text.toLowerCase()
                    .includes(
                        "perguntar a inna"
                    )
                ||
                text.toLowerCase()
                    .includes(
                        "ask inna"
                    )
            ) {
                continue;
            }


            if (
                lang &&
                candidate.contains(lang)
            ) {
                continue;
            }


            let current =
                candidate;


            for (
                let level = 0;
                level < 7 &&
                current;
                level += 1
            ) {

                const rect =
                    current
                    .getBoundingClientRect();


                const initials =
                    Array.from(
                        current.querySelectorAll(
                            "*"
                        )
                    )
                    .some(
                        function (element) {

                            if (
                                element.children.length
                                !== 0
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


                if (
                    initials
                    &&
                    rect.width >= 90
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


    function resetPosition(element) {

        if (!element) {
            return;
        }


        element.style.setProperty(
            "position",
            "relative",
            "important"
        );


        [
            "top",
            "right",
            "bottom",
            "left"
        ]
        .forEach(
            function (property) {

                element.style.setProperty(
                    property,
                    "auto",
                    "important"
                );

            }
        );


        element.style.setProperty(
            "transform",
            "none",
            "important"
        );


        element.style.setProperty(
            "margin",
            "0",
            "important"
        );

    }


    function compactUser(user) {

        if (!user) {
            return;
        }


        user.setAttribute(
            "data-sabino-finance-user-final",
            "true"
        );


        user.style.setProperty(
            "min-width",
            "165px",
            "important"
        );


        user.style.setProperty(
            "max-width",
            "205px",
            "important"
        );


        user.style.setProperty(
            "overflow",
            "hidden",
            "important"
        );


        const elements =
            Array.from(
                user.querySelectorAll(
                    "span, strong, div"
                )
            );


        for (
            const element
            of elements
        ) {

            if (
                element.children.length > 0
            ) {
                continue;
            }


            const value =
                normalize(
                    element.textContent
                );


            if (
                value.includes("@local.test")
                ||
                value.includes("browser-")
            ) {

                element.title =
                    value;


                element.textContent =
                    genericUserLabel();


                element.setAttribute(
                    "data-sabino-user-name",
                    "true"
                );


                element.style.setProperty(
                    "max-width",
                    "120px",
                    "important"
                );


                element.style.setProperty(
                    "overflow",
                    "hidden",
                    "important"
                );


                element.style.setProperty(
                    "text-overflow",
                    "ellipsis",
                    "important"
                );


                element.style.setProperty(
                    "white-space",
                    "nowrap",
                    "important"
                );

            }

        }

    }


    function restoreHeader() {

        const container =
            dock();


        const lang =
            language();


        const user =
            findUser();


        if (
            !container
            ||
            !lang
            ||
            !user
        ) {
            return false;
        }


        /*
         * Ordem definitiva:
         *
         * idioma | usuário
         */

        container.appendChild(
            lang
        );


        container.appendChild(
            user
        );


        resetPosition(
            lang
        );


        resetPosition(
            user
        );


        lang.style.setProperty(
            "order",
            "1",
            "important"
        );


        user.style.setProperty(
            "order",
            "2",
            "important"
        );


        compactUser(
            user
        );


        return true;

    }


    function restoreAfterLocaleChange() {

        /*
         * A tradução ocorre em etapas.
         * Reaplicamos depois que os escritores
         * de idioma terminarem.
         */

        window.setTimeout(
            restoreHeader,
            0
        );


        window.setTimeout(
            restoreHeader,
            100
        );


        window.setTimeout(
            restoreHeader,
            350
        );


        window.setTimeout(
            restoreHeader,
            800
        );

    }


    /*
     * Evento oficial do SabinoLocale.
     */

    window.addEventListener(
        "sabino:locale-change",
        restoreAfterLocaleChange
    );


    /*
     * Também reaplica quando o documento recebe
     * atualização de moeda após o locale.
     */

    window.addEventListener(
        "sabino:money-localized",
        function () {

            window.setTimeout(
                restoreHeader,
                50
            );

        }
    );


    /*
     * Primeira aplicação.
     */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            restoreAfterLocaleChange,
            {
                once: true
            }
        );

    }
    else {

        restoreAfterLocaleChange();

    }

})();



/* ============================================================
   SABINO_FINANCE_USER_12_LANGUAGES_V2

   Tradução do usuário compacto para os 12 idiomas manuais.
   ============================================================ */

(function () {

    "use strict";


    const USER_I18N = {

        "pt-BR": {
            user: "Usuário",
            active: "Ativo"
        },

        "en-US": {
            user: "User",
            active: "Active"
        },

        "en-GB": {
            user: "User",
            active: "Active"
        },

        "es-ES": {
            user: "Usuario",
            active: "Activo"
        },

        "de-DE": {
            user: "Benutzer",
            active: "Aktiv"
        },

        "fr-FR": {
            user: "Utilisateur",
            active: "Actif"
        },

        "it-IT": {
            user: "Utente",
            active: "Attivo"
        },

        "ru-RU": {
            user: "Пользователь",
            active: "Активен"
        },

        "ar-SA": {
            user: "المستخدم",
            active: "نشط"
        },

        "ro-RO": {
            user: "Utilizator",
            active: "Activ"
        },

        "uk-UA": {
            user: "Користувач",
            active: "Активний"
        },

        "de-CH": {
            user: "Benutzer",
            active: "Aktiv"
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
                parts[0]
                    .toLowerCase()
                +
                "-"
                +
                parts[1]
                    .toUpperCase()
            );

        }


        const base =
            parts[0]
                .toLowerCase();


        const fallback = {

            pt:
                "pt-BR",

            en:
                "en-US",

            es:
                "es-ES",

            de:
                "de-DE",

            fr:
                "fr-FR",

            it:
                "it-IT",

            ru:
                "ru-RU",

            ar:
                "ar-SA",

            ro:
                "ro-RO",

            uk:
                "uk-UA"

        };


        return (
            fallback[base]
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
            ||
            "pt-BR"
        );

    }


    function dictionary() {

        const locale =
            currentLocale();


        /*
         * de-CH = Schweiz
         * en-GB = English UK
         */

        return (
            USER_I18N[locale]
            ||
            USER_I18N["pt-BR"]
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


    function userBlock() {

        return document
            .querySelector(
                '[data-sabino-finance-user-final="true"]'
            );

    }


    function localizeCompactUser() {

        const user =
            userBlock();


        if (!user) {
            return false;
        }


        const dict =
            dictionary();


        const elements =
            Array.from(
                user.querySelectorAll(
                    "span, strong, div"
                )
            );


        /*
         * NOME DO USUÁRIO
         */

        elements.forEach(
            function (
                element
            ) {

                if (
                    element.children.length > 0
                ) {
                    return;
                }


                const value =
                    normalizeText(
                        element.textContent
                    );


                /*
                 * Nome técnico que não deve
                 * aparecer no cabeçalho.
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
                        "data-sabino-user-name"
                    )
                ) {

                    if (
                        !element.title
                        &&
                        value
                    ) {

                        element.title =
                            value;

                    }


                    element.textContent =
                        dict.user;


                    element.setAttribute(
                        "data-sabino-user-name",
                        "true"
                    );


                    element.style.setProperty(
                        "max-width",
                        "125px",
                        "important"
                    );


                    element.style.setProperty(
                        "overflow",
                        "hidden",
                        "important"
                    );


                    element.style.setProperty(
                        "text-overflow",
                        "ellipsis",
                        "important"
                    );


                    element.style.setProperty(
                        "white-space",
                        "nowrap",
                        "important"
                    );

                }

            }
        );


        /*
         * STATUS
         *
         * Mantemos "Premium" como nome do plano
         * e traduzimos apenas o estado.
         */

        elements.forEach(
            function (
                element
            ) {

                if (
                    element.children.length > 0
                ) {
                    return;
                }


                const value =
                    normalizeText(
                        element.textContent
                    );


                const lower =
                    value.toLowerCase();


                if (
                    lower.includes(
                        "premium"
                    )
                    &&
                    (
                        lower.includes(
                            "ativo"
                        )
                        ||
                        lower.includes(
                            "active"
                        )
                        ||
                        lower.includes(
                            "activo"
                        )
                        ||
                        lower.includes(
                            "aktiv"
                        )
                        ||
                        lower.includes(
                            "actif"
                        )
                        ||
                        lower.includes(
                            "attivo"
                        )
                        ||
                        lower.includes(
                            "актив"
                        )
                        ||
                        lower.includes(
                            "نشط"
                        )
                        ||
                        lower.includes(
                            "activ"
                        )
                    )
                ) {

                    element.textContent =
                        "Premium · "
                        +
                        dict.active;


                    element.setAttribute(
                        "data-sabino-user-status",
                        "true"
                    );

                }


                if (
                    element.hasAttribute(
                        "data-sabino-user-status"
                    )
                ) {

                    element.textContent =
                        "Premium · "
                        +
                        dict.active;

                }

            }
        );


        /*
         * Mantém o bloco compacto.
         */

        user.style.setProperty(
            "min-width",
            "160px",
            "important"
        );


        user.style.setProperty(
            "max-width",
            "205px",
            "important"
        );


        user.style.setProperty(
            "overflow",
            "hidden",
            "important"
        );


        return true;

    }


    function afterLocaleChange() {

        /*
         * A tradução da página ocorre em etapas.
         */

        [
            0,
            80,
            200,
            450,
            900
        ]
        .forEach(
            function (
                delay
            ) {

                window.setTimeout(
                    localizeCompactUser,
                    delay
                );

            }
        );

    }


    window.addEventListener(
        "sabino:locale-change",
        afterLocaleChange
    );


    window.addEventListener(
        "sabino:money-localized",
        function () {

            window.setTimeout(
                localizeCompactUser,
                50
            );

        }
    );


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            afterLocaleChange,
            {
                once: true
            }
        );

    }
    else {

        afterLocaleChange();

    }


    window.SabinoFinanceUserI18n12 = {

        refresh:
            localizeCompactUser,

        locale:
            currentLocale

    };

})();

