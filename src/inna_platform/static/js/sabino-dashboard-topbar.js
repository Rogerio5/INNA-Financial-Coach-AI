(function () {

    "use strict";


    if (
        window.SabinoDashboardTopbarV1
    ) {
        return;
    }


    window.SabinoDashboardTopbarV1 =
        true;


    const ACCOUNT_ID =
        "sabinoDashboardUserAccount";


    function firstText(
        ...values
    ) {

        for (
            const value
            of values
        ) {

            if (
                typeof value ===
                "string"
                &&
                value.trim()
            ) {

                return value.trim();

            }

        }

        return "";

    }


    function objectValue(
        value
    ) {

        if (
            typeof value ===
            "string"
        ) {

            return value.trim();

        }


        if (
            value &&
            typeof value ===
            "object"
        ) {

            return firstText(
                value.name,
                value.label,
                value.title,
                value.code
            );

        }


        return "";

    }


    function unwrapUser(
        payload
    ) {

        if (
            !payload ||
            typeof payload !==
            "object"
        ) {

            return {};

        }


        return (
            payload.user
            ||
            payload.current_user
            ||
            payload.profile
            ||
            payload.account
            ||
            payload.data?.user
            ||
            payload.data
            ||
            payload
        );

    }


    function nameFromEmail(
        email
    ) {

        if (!email) {
            return "";
        }


        const local =
            String(email)
            .split("@")[0]
            .replace(
                /[._-]+/g,
                " "
            )
            .replace(
                /\d+/g,
                " "
            )
            .replace(
                /\s+/g,
                " "
            )
            .trim();


        if (!local) {
            return "";
        }


        return local
            .split(" ")
            .filter(Boolean)
            .map(
                word =>
                    word
                        .charAt(0)
                        .toUpperCase()
                    +
                    word
                        .slice(1)
                        .toLowerCase()
            )
            .join(" ");

    }


    function initials(
        name
    ) {

        const parts =
            String(
                name ||
                "Usuário"
            )
            .trim()
            .split(/\s+/)
            .filter(Boolean);


        if (!parts.length) {
            return "US";
        }


        if (
            parts.length === 1
        ) {

            return parts[0]
                .slice(
                    0,
                    2
                )
                .toUpperCase();

        }


        return (
            parts[0][0]
            +
            parts[
                parts.length - 1
            ][0]
        )
        .toUpperCase();

    }


    function normalizedStatus(
        value
    ) {

        const status =
            objectValue(
                value
            );


        if (!status) {
            return "";
        }


        const lower =
            status.toLowerCase();


        if (
            lower === "active"
            ||
            lower === "ativo"
        ) {
            return "Ativo";
        }


        if (
            lower === "inactive"
            ||
            lower === "inativo"
        ) {
            return "Inativo";
        }


        return status;

    }


    function createAccount() {

        let account =
            document.getElementById(
                ACCOUNT_ID
            );


        if (account) {
            return account;
        }


        account =
            document.createElement(
                "a"
            );


        account.id =
            ACCOUNT_ID;


        account.href =
            "/conta";


        account.setAttribute(
            "aria-label",
            "Abrir minha conta"
        );


        account.innerHTML = `
            <span
                class="sabino-dashboard-user-avatar"
                data-sabino-user-avatar
            >
                US
            </span>

            <span
                class="sabino-dashboard-user-content"
            >
                <strong
                    class="sabino-dashboard-user-name"
                    data-sabino-user-name
                >
                    Usuário
                </strong>

                <span
                    class="sabino-dashboard-user-meta"
                    data-sabino-user-meta
                >
                    Conta ativa
                </span>
            </span>

            <span
                class="sabino-dashboard-user-chevron"
                aria-hidden="true"
            >
                ▾
            </span>
        `;


        document.body.appendChild(
            account
        );


        return account;

    }


    function renderUser(
        payload
    ) {

        const user =
            unwrapUser(
                payload
            );


        const email =
            firstText(
                user.email,
                payload?.email,
                user.username,
                payload?.username
            );


        const name =
            firstText(
                user.display_name,
                user.full_name,
                user.name,
                user.nome,
                user.first_name,
                payload?.display_name,
                payload?.full_name,
                payload?.name,
                payload?.nome,
                nameFromEmail(
                    email
                ),
                "Usuário"
            );


        const plan =
            objectValue(
                user.plan
                ||
                user.plan_name
                ||
                user.subscription?.plan
                ||
                payload?.plan
                ||
                payload?.subscription?.plan
            );


        const status =
            normalizedStatus(
                user.status
                ||
                user.subscription_status
                ||
                user.subscription?.status
                ||
                payload?.status
                ||
                payload?.subscription_status
                ||
                payload?.subscription?.status
            );


        let meta =
            "";


        if (
            plan &&
            status
        ) {

            meta =
                `${plan} · ${status}`;

        }
        else if (plan) {

            meta =
                plan;

        }
        else if (status) {

            meta =
                status;

        }
        else {

            meta =
                "Conta ativa";

        }


        const account =
            createAccount();


        const nameElement =
            account.querySelector(
                "[data-sabino-user-name]"
            );


        const metaElement =
            account.querySelector(
                "[data-sabino-user-meta]"
            );


        const avatarElement =
            account.querySelector(
                "[data-sabino-user-avatar]"
            );


        if (nameElement) {

            nameElement.textContent =
                name;

            nameElement.title =
                email || name;

        }


        if (metaElement) {

            metaElement.textContent =
                meta;

        }


        if (avatarElement) {

            avatarElement.textContent =
                initials(
                    name
                );

        }

    }


    async function loadUser() {

        /*
         * Cookie HttpOnly da sessão é enviado
         * automaticamente pelo navegador.
         *
         * Nenhum token é colocado em
         * localStorage/sessionStorage.
         */

        try {

            const response =
                await fetch(
                    "/auth/me",
                    {
                        method:
                            "GET",

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


            if (
                response.status ===
                401
            ) {

                /*
                 * Não inventa identidade.
                 */

                renderUser(
                    {}
                );

                return;

            }


            if (!response.ok) {

                renderUser(
                    {}
                );

                return;

            }


            const payload =
                await response.json();


            renderUser(
                payload
            );

        }
        catch (error) {

            console.debug(
                "SABINO_DASHBOARD_USER_LOAD_ERROR",
                error
            );


            renderUser(
                {}
            );

        }

    }


    function start() {

        createAccount();

        loadUser();

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            start,
            {
                once:
                    true
            }
        );

    }
    else {

        start();

    }

})();
