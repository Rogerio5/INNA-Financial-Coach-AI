document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        const LOGO_URL =
            "/static/images/sabino-s-logo.png";


        const processed =
            new WeakSet();


        function installLogo(element) {

            if (!element) {
                return false;
            }


            if (
                processed.has(element) ||
                element.querySelector(
                    ".sabino-official-logo"
                )
            ) {

                return true;

            }


            element.innerHTML = "";


            const image =
                document.createElement(
                    "img"
                );


            image.src =
                LOGO_URL;


            image.alt =
                "Sabino.AI";


            image.className =
                "sabino-official-logo";


            image.loading =
                "eager";


            image.decoding =
                "async";


            element.appendChild(
                image
            );


            element.classList.add(
                "sabino-global-logo-container"
            );


            processed.add(
                element
            );


            return true;

        }


        /*
         * 1. Seletores conhecidos.
         */

        const selectors = [

            ".finance-brand-symbol",

            ".brand-symbol",

            ".brand-mark",

            ".logo-symbol",

            ".logo-mark",

            ".sabino-brand-symbol",

            ".sabino-brand-mark",

            ".sabino-logo-symbol",

            ".sabino-logo-mark",

            ".platform-brand-symbol",

            ".platform-logo-symbol",

            ".inna-brand-symbol",

            "[data-sabino-logo]"

        ];


        document
            .querySelectorAll(
                selectors.join(",")
            )
            .forEach(
                element => {

                    const text =
                        (
                            element.textContent ||
                            ""
                        )
                        .trim()
                        .toUpperCase();


                    if (
                        text === "S" ||
                        element.hasAttribute(
                            "data-sabino-logo"
                        ) ||
                        element.classList.contains(
                            "finance-brand-symbol"
                        )
                    ) {

                        installLogo(
                            element
                        );

                    }

                }
            );


        /*
         * 2. Fallback inteligente:
         * procura o S dentro do bloco que contém Sabino.AI.
         */

        document
            .querySelectorAll(
                "header, nav, .topbar, .navbar, .header"
            )
            .forEach(
                header => {

                    const headerText =
                        (
                            header.textContent ||
                            ""
                        );


                    if (
                        !headerText.includes(
                            "Sabino.AI"
                        )
                    ) {

                        return;

                    }


                    const candidates =
                        header.querySelectorAll(
                            "span, div"
                        );


                    for (
                        const candidate
                        of candidates
                    ) {

                        const text =
                            (
                                candidate.textContent ||
                                ""
                            )
                            .trim();


                        if (
                            text !== "S"
                        ) {

                            continue;

                        }


                        /*
                         * Evita substituir elementos gigantes.
                         */

                        const rect =
                            candidate
                                .getBoundingClientRect();


                        if (
                            rect.width > 0 &&
                            rect.height > 0 &&
                            rect.width <= 130 &&
                            rect.height <= 130
                        ) {

                            installLogo(
                                candidate
                            );

                            break;

                        }

                    }

                }
            );


        console.log(
            "SABINO_GLOBAL_OFFICIAL_LOGO=READY"
        );

    }
);
