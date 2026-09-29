(function () {

    "use strict";


    const HEADER_ID =
        "sabinoFinanceDashboardHeader";


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


    function language() {

        return document
            .getElementById(
                "sabinoLanguageSwitcher"
            );

    }


    function containsINNA(
        element
    ) {

        const text =
            normalize(
                element?.textContent
            )
            .toLowerCase();


        return (
            text.includes(
                "perguntar a inna"
            )
            ||
            text.includes(
                "conversar com a inna"
            )
        );

    }


    function hasAvatarInitials(
        element
    ) {

        if (!element) {
            return false;
        }


        const candidates =
            Array.from(
                element.querySelectorAll(
                    "span, div, strong"
                )
            );


        return candidates.some(
            function (
                candidate
            ) {

                const text =
                    normalize(
                        candidate.textContent
                    );


                if (
                    !/^[A-Z]{2}$/.test(
                        text
                    )
                ) {

                    return false;

                }


                const rect =
                    candidate
                    .getBoundingClientRect();


                return (
                    rect.width >= 25
                    &&
                    rect.width <= 60
                    &&
                    rect.height >= 25
                    &&
                    rect.height <= 60
                );

            }
        );

    }


    function userBlock() {

        /*
         * Procura primeiro o texto mais específico
         * que aparece no usuário do Financeiro:
         *
         * Premium · Ativo
         */

        const all =
            Array.from(
                document.querySelectorAll(
                    "header *, .topbar *, body *"
                )
            );


        const anchors =
            all.filter(
                function (
                    element
                ) {

                    if (
                        !visible(
                            element
                        )
                    ) {
                        return false;
                    }


                    const text =
                        normalize(
                            element.textContent
                        );


                    if (
                        containsINNA(
                            element
                        )
                    ) {
                        return false;
                    }


                    return (
                        (
                            text.includes(
                                "Premium"
                            )
                            &&
                            (
                                text.includes(
                                    "Ativo"
                                )
                                ||
                                text.includes(
                                    "Active"
                                )
                            )
                        )
                        ||
                        text ===
                            "Conta Sabino.AI"
                    );

                }
            );


        /*
         * Menor elemento primeiro.
         */

        anchors.sort(
            function (
                a,
                b
            ) {

                const ar =
                    a.getBoundingClientRect();

                const br =
                    b.getBoundingClientRect();


                return (
                    ar.width *
                    ar.height
                )
                -
                (
                    br.width *
                    br.height
                );

            }
        );


        for (
            const anchor
            of anchors
        ) {

            let current =
                anchor;


            for (
                let level = 0;
                level < 7 &&
                current;
                level += 1
            ) {

                const rect =
                    current
                    .getBoundingClientRect();


                /*
                 * Não permite pegar:
                 * - topbar inteiro
                 * - botão INNA
                 * - seletor de idioma
                 */

                if (
                    !containsINNA(
                        current
                    )
                    &&
                    !current.contains(
                        language()
                    )
                    &&
                    rect.width >= 100
                    &&
                    rect.width <= 310
                    &&
                    rect.height >= 32
                    &&
                    rect.height <= 90
                    &&
                    hasAvatarInitials(
                        current
                    )
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
            document
            .getElementById(
                HEADER_ID
            );


        if (header) {
            return header;
        }


        header =
            document
            .createElement(
                "div"
            );


        header.id =
            HEADER_ID;


        header.setAttribute(
            "aria-label",
            "Idioma e conta do usuário"
        );


        document.body.appendChild(
            header
        );


        return header;

    }


    function apply() {

        const locale =
            language();


        const user =
            userBlock();


        if (
            !locale
            ||
            !user
        ) {

            return false;

        }


        const header =
            ensureHeader();


        /*
         * Marca SOMENTE o bloco real encontrado.
         */

        user.setAttribute(
            "data-sabino-finance-dashboard-user",
            "true"
        );


        /*
         * Ordem física do DOM:
         *
         * idioma
         * usuário
         */

        if (
            locale.parentElement !==
            header
        ) {

            header.appendChild(
                locale
            );

        }


        if (
            user.parentElement !==
            header
        ) {

            header.appendChild(
                user
            );

        }


        /*
         * Reforço da ordem.
         */

        locale.style.setProperty(
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
            "SABINO_FINANCE_HEADER_DASHBOARD_V1=READY"
        );


        return true;

    }


    function start() {

        if (
            apply()
        ) {
            return;
        }


        /*
         * Somente tentativas pontuais.
         * Sem MutationObserver.
         */

        window.setTimeout(
            apply,
            200
        );


        window.setTimeout(
            apply,
            600
        );


        window.setTimeout(
            apply,
            1300
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
