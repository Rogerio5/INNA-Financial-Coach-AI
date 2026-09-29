(function () {

    "use strict";

    const DOCK_ID =
        "sabinoFinanceClientDock";

    const FALLBACK_ACCOUNT_ID =
        "sabinoFinanceClientAccount";


    function normalize(value) {

        return String(value || "")
            .replace(/\s+/g, " ")
            .trim();

    }


    function visible(element) {

        if (!element) {
            return false;
        }

        const style =
            window.getComputedStyle(element);

        return (
            style.display !== "none" &&
            style.visibility !== "hidden"
        );

    }


    function languageElement() {

        return document.getElementById(
            "sabinoLanguageSwitcher"
        );

    }


    function containsInna(element) {

        return normalize(
            element?.textContent
        )
        .toLowerCase()
        .includes(
            "perguntar a inna"
        );

    }


    function findExistingAccount() {

        /*
         * Primeiro: seletores comuns e seguros.
         */

        const directSelectors = [
            "[data-user-menu]",
            "[data-account-menu]",
            "[data-profile-menu]",
            ".user-menu",
            ".user-chip",
            ".account-chip",
            ".profile-chip",
            ".topbar-user",
            ".header-user",
            ".user-profile"
        ];


        for (
            const selector
            of directSelectors
        ) {

            const element =
                document.querySelector(
                    selector
                );

            if (
                element &&
                !containsInna(element)
            ) {

                return element;

            }

        }


        /*
         * Segundo: localiza Premium / Ativo e sobe somente
         * até um card pequeno. Não aceita container da INNA.
         */

        const elements =
            Array.from(
                document.querySelectorAll(
                    "header *, .topbar *, body *"
                )
            );


        const meta =
            elements.find(
                function (element) {

                    const text =
                        normalize(
                            element.textContent
                        );


                    if (
                        !text.includes("Premium")
                        &&
                        !text.includes("Conta Sabino.AI")
                        &&
                        !text.includes("Conta ativa")
                    ) {
                        return false;
                    }


                    if (
                        containsInna(
                            element
                        )
                    ) {
                        return false;
                    }


                    return true;

                }
            );


        if (!meta) {
            return null;
        }


        let current =
            meta;


        for (
            let i = 0;
            i < 7 && current;
            i += 1
        ) {

            const rect =
                current
                .getBoundingClientRect();


            const text =
                normalize(
                    current.textContent
                );


            if (
                !containsInna(current)
                &&
                rect.width >= 110
                &&
                rect.width <= 330
                &&
                rect.height >= 30
                &&
                rect.height <= 100
                &&
                (
                    text.includes("Premium")
                    ||
                    text.includes("Conta Sabino.AI")
                    ||
                    text.includes("Conta ativa")
                )
            ) {

                return current;

            }


            current =
                current.parentElement;

        }


        return null;

    }


    function dock() {

        let element =
            document.getElementById(
                DOCK_ID
            );


        if (element) {
            return element;
        }


        element =
            document.createElement(
                "div"
            );


        element.id =
            DOCK_ID;


        element.setAttribute(
            "aria-label",
            "Idioma e usuário"
        );


        document.body.appendChild(
            element
        );


        return element;

    }


    function initials(name) {

        const parts =
            normalize(name)
            .split(" ")
            .filter(Boolean);


        if (!parts.length) {
            return "US";
        }


        if (parts.length === 1) {

            return parts[0]
                .slice(0, 2)
                .toUpperCase();

        }


        return (
            parts[0][0]
            +
            parts[
                parts.length - 1
            ][0]
        ).toUpperCase();

    }


    function createFallbackAccount() {

        let account =
            document.getElementById(
                FALLBACK_ACCOUNT_ID
            );


        if (account) {
            return account;
        }


        account =
            document.createElement(
                "a"
            );


        account.id =
            FALLBACK_ACCOUNT_ID;


        account.href =
            "/conta";


        account.innerHTML = `
            <span
                class="sabino-finance-account-avatar"
                data-account-avatar
            >
                US
            </span>

            <span
                class="sabino-finance-account-copy"
            >
                <strong
                    class="sabino-finance-account-name"
                    data-account-name
                >
                    Usuário
                </strong>

                <span
                    class="sabino-finance-account-meta"
                    data-account-meta
                >
                    Conta Sabino.AI
                </span>
            </span>
        `;


        return account;

    }


    async function hydrateFallback(
        account
    ) {

        try {

            const response =
                await fetch(
                    "/auth/me",
                    {
                        credentials:
                            "same-origin",

                        cache:
                            "no-store",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            if (!response.ok) {
                return;
            }


            const payload =
                await response.json();


            const user =
                payload.user
                ||
                payload.profile
                ||
                payload.account
                ||
                payload.data?.user
                ||
                payload.data
                ||
                payload;


            /*
             * Não usa e-mail técnico como nome.
             */

            const name =
                normalize(
                    user.display_name
                    ||
                    user.full_name
                    ||
                    user.nome
                    ||
                    user.name
                    ||
                    "Usuário"
                );


            const plan =
                normalize(
                    user.plan?.name
                    ||
                    user.plan_name
                    ||
                    user.plan
                    ||
                    ""
                );


            const statusRaw =
                normalize(
                    user.status
                    ||
                    user.subscription_status
                    ||
                    ""
                );


            const status =
                statusRaw.toLowerCase() === "active"
                    ? "Ativo"
                    : statusRaw;


            const nameElement =
                account.querySelector(
                    "[data-account-name]"
                );


            const avatar =
                account.querySelector(
                    "[data-account-avatar]"
                );


            const meta =
                account.querySelector(
                    "[data-account-meta]"
                );


            if (nameElement) {

                nameElement.textContent =
                    name;

            }


            if (avatar) {

                avatar.textContent =
                    initials(name);

            }


            if (meta) {

                if (
                    plan &&
                    status
                ) {

                    meta.textContent =
                        `${plan} · ${status}`;

                }
                else if (plan) {

                    meta.textContent =
                        plan;

                }
                else if (status) {

                    meta.textContent =
                        status;

                }

            }

        }
        catch (error) {

            console.debug(
                "SABINO_FINANCE_ACCOUNT",
                error
            );

        }

    }


    function mount() {

        const language =
            languageElement();


        if (!language) {
            return false;
        }


        const container =
            dock();


        /*
         * Idioma SEMPRE primeiro.
         */

        if (
            language.parentElement !==
            container
        ) {

            container.appendChild(
                language
            );

        }


        language.style.setProperty(
            "order",
            "1",
            "important"
        );


        /*
         * Procura o usuário ORIGINAL.
         */

        let account =
            findExistingAccount();


        if (account) {

            account.setAttribute(
                "data-sabino-finance-account-existing",
                "true"
            );


            if (
                account.parentElement !==
                container
            ) {

                container.appendChild(
                    account
                );

            }


            account.style.setProperty(
                "order",
                "2",
                "important"
            );


            return true;

        }


        /*
         * Somente se realmente não existir usuário na página.
         */

        account =
            createFallbackAccount();


        if (
            account.parentElement !==
            container
        ) {

            container.appendChild(
                account
            );

        }


        hydrateFallback(
            account
        );


        return true;

    }


    function start() {

        if (mount()) {
            return;
        }


        window.setTimeout(
            mount,
            200
        );


        window.setTimeout(
            mount,
            700
        );


        window.setTimeout(
            mount,
            1400
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            start,
            {
                once: true
            }
        );

    }
    else {

        start();

    }

})();
