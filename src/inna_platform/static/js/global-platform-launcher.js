document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        const platforms = [

            {
                id:
                    "financial",

                code:
                    "FI",

                name:
                    "Financeira",

                description:
                    "Educação, Segurança, Reembolso e Planejamento.",

                route:
                    "/plataforma/financeiro",

                status:
                    "active"
            },

            {
                id:
                    "quality",

                code:
                    "QC",

                name:
                    "Qualidade & Confiabilidade",

                description:
                    "Testes, Quality Gate, risco e confiabilidade.",

                route:
                    "/plataforma/qualidade",

                status:
                    "preparation"
            },

            {
                id:
                    "industry",

                code:
                    "I4",

                name:
                    "Indústria 4.0",

                description:
                    "Produção, qualidade, manutenção, IoT e energia.",

                route:
                    "/plataforma/industria-4-0",

                status:
                    "preparation"
            },

            {
                id:
                    "career",

                code:
                    "CA",

                name:
                    "Carreira Inteligente",

                description:
                    "ATS, currículo, vagas, entrevistas e portfólio.",

                route:
                    "/plataforma/carreira",

                status:
                    "preparation"
            }

        ];


        const path =
            window.location.pathname;


        const favoriteKey =
            "sabino_platform_favorites";


        const recentKey =
            "sabino_platform_recent";


        const permissionKey =
            "sabino_platform_permissions";


        function detectCurrentPlatform() {

            if (
                path.startsWith(
                    "/plataforma/financeiro"
                )
            ) {
                return "financial";
            }


            if (
                path.startsWith(
                    "/plataforma/qualidade"
                )
            ) {
                return "quality";
            }


            if (
                path.startsWith(
                    "/plataforma/industria-4-0"
                )
            ) {
                return "industry";
            }


            if (
                path.startsWith(
                    "/plataforma/carreira"
                )
            ) {
                return "career";
            }


            return null;

        }


        const currentPlatform =
            detectCurrentPlatform();


        function safeJson(
            key,
            fallback
        ) {

            try {

                const value =
                    JSON.parse(
                        localStorage.getItem(
                            key
                        )
                    );


                return value ?? fallback;

            }
            catch {

                return fallback;

            }

        }


        let favorites =
            safeJson(
                favoriteKey,
                ["financial"]
            );


        let recents =
            safeJson(
                recentKey,
                []
            );


        /*
         * Somente preparação visual.
         * Segurança real deverá continuar sendo
         * validada no backend via RBAC.
         */

        const storedPermissions =
            safeJson(
                permissionKey,
                null
            );


        function hasPermission(platform) {

            if (
                !Array.isArray(
                    storedPermissions
                )
            ) {
                return true;
            }


            return storedPermissions.includes(
                platform.id
            );

        }


        if (currentPlatform) {

            recents =
                [
                    currentPlatform,
                    ...recents.filter(
                        item =>
                            item !== currentPlatform
                    )
                ]
                    .slice(
                        0,
                        4
                    );


            localStorage.setItem(
                recentKey,
                JSON.stringify(
                    recents
                )
            );

        }


        function currentName() {

            if (!currentPlatform) {
                return "Central";
            }


            return (
                platforms.find(
                    platform =>
                        platform.id ===
                        currentPlatform
                )
                ?.name
                ||
                "Plataforma"
            );

        }


        function toast(message) {

            let element =
                document.getElementById(
                    "sabino-platform-toast"
                );


            if (!element) {

                element =
                    document.createElement(
                        "div"
                    );


                element.id =
                    "sabino-platform-toast";


                element.className =
                    "sabino-platform-toast";


                element.setAttribute(
                    "role",
                    "status"
                );


                document.body.appendChild(
                    element
                );

            }


            element.textContent =
                message;


            element.classList.add(
                "show"
            );


            clearTimeout(
                element._timer
            );


            element._timer =
                setTimeout(
                    () => {

                        element.classList.remove(
                            "show"
                        );

                    },
                    2600
                );

        }


        function platformItem(
            platform,
            recent = false
        ) {

            const current =
                platform.id ===
                currentPlatform;


            const favorite =
                favorites.includes(
                    platform.id
                );


            const permitted =
                hasPermission(
                    platform
                );


            const available =
                platform.status ===
                "active";


            const item =
                document.createElement(
                    "div"
                );


            item.className =
                [
                    "sabino-platform-item",
                    current
                        ? "current"
                        : "",
                    !available ||
                    !permitted
                        ? "disabled"
                        : ""
                ]
                    .filter(Boolean)
                    .join(" ");


            item.dataset.platformId =
                platform.id;


            item.tabIndex =
                available &&
                permitted
                    ? 0
                    : -1;


            item.innerHTML =
                `
                <div class="sabino-platform-icon">
                    ${platform.code}
                </div>

                <div>

                    <strong>
                        ${platform.name}
                    </strong>

                    <small>
                        ${
                            current
                                ? "Plataforma atual"
                                : platform.description
                        }
                    </small>

                </div>

                <div class="sabino-platform-item-actions">

                    <span
                        class="sabino-platform-state ${
                            available
                                ? "active"
                                : "preparation"
                        }"
                    >
                        ${
                            current
                                ? "Atual"
                                : (
                                    available
                                        ? "● Ativa"
                                        : "Preparação"
                                )
                        }
                    </span>

                    ${
                        recent
                            ? ""
                            : `
                            <button
                                type="button"
                                class="sabino-platform-favorite ${
                                    favorite
                                        ? "active"
                                        : ""
                                }"
                                data-platform-favorite="${platform.id}"
                                aria-label="Favoritar ${platform.name}"
                                title="Favoritar"
                            >
                                ${
                                    favorite
                                        ? "★"
                                        : "☆"
                                }
                            </button>
                            `
                    }

                </div>
                `;


            if (
                available &&
                permitted
            ) {

                const openPlatform =
                    () => {

                        if (current) {

                            closeLauncher();

                            return;

                        }


                        window.location.href =
                            platform.route;

                    };


                item.addEventListener(
                    "click",
                    event => {

                        if (
                            event.target.closest(
                                "[data-platform-favorite]"
                            )
                        ) {
                            return;
                        }


                        openPlatform();

                    }
                );


                item.addEventListener(
                    "keydown",
                    event => {

                        if (
                            event.key === "Enter" ||
                            event.key === " "
                        ) {

                            event.preventDefault();

                            openPlatform();

                        }

                    }
                );

            }
            else {

                item.addEventListener(
                    "click",
                    event => {

                        if (
                            event.target.closest(
                                "[data-platform-favorite]"
                            )
                        ) {
                            return;
                        }


                        if (!permitted) {

                            toast(
                                "Esta plataforma não está disponível para o perfil atual."
                            );

                            return;

                        }


                        toast(
                            `${platform.name} está registrada na arquitetura e ainda está em preparação.`
                        );

                    }
                );

            }


            return item;

        }


        function findHost() {

            const selectors = [

                ".inna-central-actions",

                ".finance-top-actions",

                ".ef2-top-actions",

                ".ef2-header-actions",

                ".ef2-actions",

                ".sf-top-actions",

                ".sf-header-actions",

                ".sf-actions",

                ".ef2-header",

                ".sf-header"

            ];


            for (
                const selector
                of selectors
            ) {

                const element =
                    document.querySelector(
                        selector
                    );


                if (element) {
                    return element;
                }

            }


            return null;

        }


        const host =
            findHost();


        const launcher =
            document.createElement(
                "div"
            );


        launcher.className =
            "sabino-platform-launcher-host";


        launcher.innerHTML =
            `
            <button
                type="button"
                class="sabino-platform-launcher-button"
                id="sabino-platform-launcher-button"
                aria-haspopup="dialog"
                aria-expanded="false"
            >

                <span class="launcher-grid-icon">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </span>

                <span class="launcher-button-label">
                    Plataformas
                </span>

                <span class="sabino-platform-launcher-current">
                    ${currentName()}
                </span>

            </button>


            <div
                class="sabino-platform-launcher-panel"
                id="sabino-platform-launcher-panel"
                role="dialog"
                aria-label="Plataformas Sabino.AI"
            >

                <header class="sabino-platform-launcher-header">

                    <div>

                        <small>
                            SABINO.AI
                        </small>

                        <h3>
                            Plataformas
                        </h3>

                        <p>
                            Acesse rapidamente os domínios
                            disponíveis para sua conta.
                        </p>

                    </div>

                    <button
                        type="button"
                        class="sabino-platform-launcher-close"
                        id="sabino-platform-launcher-close"
                        aria-label="Fechar"
                    >
                        ×
                    </button>

                </header>


                <div class="sabino-platform-search">

                    <input
                        type="search"
                        id="sabino-platform-search-input"
                        placeholder="Buscar plataforma..."
                        autocomplete="off"
                    >

                </div>


                <section class="sabino-platform-launcher-section">

                    <header>

                        <strong>
                            Plataformas
                        </strong>

                        <span>
                            4 registradas
                        </span>

                    </header>

                    <div
                        class="sabino-platform-list"
                        id="sabino-platform-list"
                    ></div>

                </section>


                <section class="sabino-platform-launcher-section">

                    <header>

                        <strong>
                            Recentes
                        </strong>

                    </header>

                    <div
                        class="sabino-platform-list"
                        id="sabino-platform-recent-list"
                    ></div>

                </section>


                <footer class="sabino-platform-launcher-footer">

                    <small>
                        Acesso sujeito às permissões da empresa.
                    </small>

                    <a href="/plataforma#platforms">
                        Ver todas →
                    </a>

                </footer>

            </div>
            `;


        if (host) {

            host.insertBefore(
                launcher,
                host.firstChild
            );

        }
        else {

            launcher.classList.add(
                "sabino-platform-launcher-floating"
            );


            document.body.appendChild(
                launcher
            );

        }


        const button =
            document.getElementById(
                "sabino-platform-launcher-button"
            );


        const panel =
            document.getElementById(
                "sabino-platform-launcher-panel"
            );


        const close =
            document.getElementById(
                "sabino-platform-launcher-close"
            );


        const search =
            document.getElementById(
                "sabino-platform-search-input"
            );


        const list =
            document.getElementById(
                "sabino-platform-list"
            );


        const recentList =
            document.getElementById(
                "sabino-platform-recent-list"
            );


        function renderPlatforms(
            query = ""
        ) {

            const normalized =
                query
                    .trim()
                    .toLowerCase();


            const sorted =
                [...platforms]
                    .sort(
                        (a,b) => {

                            const favA =
                                favorites.includes(
                                    a.id
                                )
                                    ? 1
                                    : 0;


                            const favB =
                                favorites.includes(
                                    b.id
                                )
                                    ? 1
                                    : 0;


                            return favB - favA;

                        }
                    );


            const filtered =
                sorted.filter(
                    platform => {

                        if (!normalized) {
                            return true;
                        }


                        return (
                            platform.name
                                .toLowerCase()
                                .includes(
                                    normalized
                                )
                            ||
                            platform.description
                                .toLowerCase()
                                .includes(
                                    normalized
                                )
                        );

                    }
                );


            list.innerHTML =
                "";


            filtered.forEach(
                platform => {

                    list.appendChild(
                        platformItem(
                            platform
                        )
                    );

                }
            );


            bindFavorites();

        }


        function renderRecents() {

            recentList.innerHTML =
                "";


            const recentPlatforms =
                recents
                    .map(
                        id =>
                            platforms.find(
                                platform =>
                                    platform.id === id
                            )
                    )
                    .filter(Boolean);


            if (
                recentPlatforms.length === 0
            ) {

                recentList.innerHTML =
                    `
                    <div class="sabino-platform-recent-empty">
                        As plataformas acessadas recentemente
                        aparecerão aqui.
                    </div>
                    `;


                return;

            }


            recentPlatforms
                .slice(
                    0,
                    3
                )
                .forEach(
                    platform => {

                        recentList.appendChild(
                            platformItem(
                                platform,
                                true
                            )
                        );

                    }
                );

        }


        function bindFavorites() {

            document
                .querySelectorAll(
                    "[data-platform-favorite]"
                )
                .forEach(
                    favoriteButton => {

                        favoriteButton.addEventListener(
                            "click",
                            event => {

                                event.stopPropagation();


                                const platformId =
                                    favoriteButton.dataset
                                        .platformFavorite;


                                if (
                                    favorites.includes(
                                        platformId
                                    )
                                ) {

                                    favorites =
                                        favorites.filter(
                                            id =>
                                                id !==
                                                platformId
                                        );

                                }
                                else {

                                    favorites.push(
                                        platformId
                                    );

                                }


                                localStorage.setItem(
                                    favoriteKey,
                                    JSON.stringify(
                                        favorites
                                    )
                                );


                                renderPlatforms(
                                    search.value
                                );

                            }
                        );

                    }
                );

        }


        function openLauncher() {

            panel.classList.add(
                "open"
            );


            button.setAttribute(
                "aria-expanded",
                "true"
            );


            setTimeout(
                () => {

                    search.focus();

                },
                40
            );

        }


        function closeLauncher() {

            panel.classList.remove(
                "open"
            );


            button.setAttribute(
                "aria-expanded",
                "false"
            );

        }


        button.addEventListener(
            "click",
            event => {

                event.stopPropagation();


                if (
                    panel.classList.contains(
                        "open"
                    )
                ) {

                    closeLauncher();

                }
                else {

                    openLauncher();

                }

            }
        );


        close.addEventListener(
            "click",
            closeLauncher
        );


        search.addEventListener(
            "input",
            () => {

                renderPlatforms(
                    search.value
                );

            }
        );


        document.addEventListener(
            "click",
            event => {

                if (
                    !launcher.contains(
                        event.target
                    )
                ) {

                    closeLauncher();

                }

            }
        );


        document.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Escape"
                ) {

                    closeLauncher();

                }

            }
        );


        renderPlatforms();

        renderRecents();


        console.log(
            "SABINO_GLOBAL_PLATFORM_LAUNCHER_V1=READY"
        );

    }
);
