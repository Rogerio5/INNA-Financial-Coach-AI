document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        const BRAND_MARKER =
            "SABINO_GLOBAL_BRAND_V2";


        const LOGO =
            "/static/images/sabino-s-logo.png";


        function createBrand() {

            const brand =
                document.createElement(
                    "a"
                );


            brand.href =
                "/plataforma";


            brand.className =
                "sabino-global-brand-v2";


            brand.setAttribute(
                "data-sabino-brand-v2",
                "true"
            );


            brand.innerHTML = `
                <span class="sabino-global-brand-v2__logo">
                    <img
                        src="${LOGO}"
                        alt="Sabino.AI"
                    >
                </span>

                <span class="sabino-global-brand-v2__text">

                    <strong class="sabino-global-brand-v2__name">
                        Sabino.AI
                    </strong>

                    <small class="sabino-global-brand-v2__subtitle">
                        Intelligence Platform
                    </small>

                </span>
            `;


            return brand;

        }


        function normalize(text) {

            return (
                text ||
                ""
            )
            .replace(
                /\s+/g,
                " "
            )
            .trim()
            .toLowerCase();

        }


        function findExistingBrand() {

            const explicitSelectors = [

                ".finance-brand",

                ".sabino-brand",

                ".inna-brand",

                ".platform-brand",

                ".navbar-brand",

                ".topbar-brand",

                ".header-brand",

                "[data-sabino-brand]",

                ".brand"

            ];


            for (
                const selector
                of explicitSelectors
            ) {

                const elements =
                    document.querySelectorAll(
                        selector
                    );


                for (
                    const element
                    of elements
                ) {

                    const text =
                        normalize(
                            element.textContent
                        );


                    if (
                        text.includes(
                            "sabino.ai"
                        )
                    ) {

                        return element;

                    }

                }

            }


            const candidates =
                document.querySelectorAll(
                    "header a, header div, nav a, nav div"
                );


            for (
                const element
                of candidates
            ) {

                const text =
                    normalize(
                        element.textContent
                    );


                if (
                    text.includes(
                        "sabino.ai"
                    ) &&
                    text.length < 80
                ) {

                    return element;

                }

            }


            return null;

        }


        function installBrand() {

            if (
                document.querySelector(
                    "[data-sabino-brand-v2='true']"
                )
            ) {

                return;

            }


            const existing =
                findExistingBrand();


            if (!existing) {

                console.warn(
                    BRAND_MARKER +
                    "=BRAND_NOT_FOUND"
                );

                return;

            }


            const brand =
                createBrand();


            existing.replaceWith(
                brand
            );


            console.log(
                BRAND_MARKER +
                "=INSTALLED"
            );

        }


        installBrand();


        /*
         * Observador:
         * garante a marca mesmo em paginas
         * que montem parte do header depois.
         */

        const observer =
            new MutationObserver(
                () => {

                    if (
                        document.querySelector(
                            "[data-sabino-brand-v2='true']"
                        )
                    ) {

                        return;

                    }


                    installBrand();

                }
            );


        observer.observe(
            document.documentElement,
            {
                childList:
                    true,

                subtree:
                    true
            }
        );


        console.log(
            BRAND_MARKER +
            "=READY"
        );

    }
);
