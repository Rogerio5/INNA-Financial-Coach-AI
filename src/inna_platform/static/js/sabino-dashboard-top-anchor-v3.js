/* ============================================================
   SABINO.AI
   DASHBOARD TOP ANCHOR V3

   Topo direito da página.
   Nenhuma compensação de scroll.
   ============================================================ */

(function () {

    "use strict";


    if (
        window.SabinoDashboardTopAnchorV3
    ) {

        return;
    }


    window.SabinoDashboardTopAnchorV3 =
        true;


    function getTopbar() {

        return (
            document.querySelector(
                ".main > header.topbar"
            )
            ||
            document.querySelector(
                ".main > .topbar"
            )
            ||
            document.querySelector(
                "header.topbar"
            )
        );
    }


    function getLanguage() {

        return (
            document.getElementById(
                "sabinoLanguageSwitcher"
            )
            ||
            document.getElementById(
                "languageButton"
            )
            ||
            document.querySelector(
                ".language"
            )
        );
    }


    function getProfile() {

        return (
            document.querySelector(
                ".topbar .profile"
            )
            ||
            document.querySelector(
                ".profile"
            )
        );
    }


    function apply() {

        const topbar =
            getTopbar();


        if (!topbar) {

            return false;
        }


        const language =
            getLanguage();


        const profile =
            getProfile();


        /*
         * Mantém:
         *
         * [ idioma ] [ usuário ]
         */

        if (language) {

            if (
                language.parentElement !==
                topbar
            ) {

                if (
                    profile &&
                    profile.parentElement ===
                    topbar
                ) {

                    topbar.insertBefore(
                        language,
                        profile
                    );

                }
                else {

                    topbar.appendChild(
                        language
                    );
                }
            }
        }


        if (
            profile &&
            profile.parentElement !==
            topbar
        ) {

            topbar.appendChild(
                profile
            );
        }


        topbar.setAttribute(
            "data-sabino-dashboard-top-anchor-v3",
            "true"
        );


        /*
         * Posição FINAL.
         */

        topbar.style.setProperty(
            "position",
            "absolute",
            "important"
        );


        topbar.style.setProperty(
            "top",
            "18px",
            "important"
        );


        topbar.style.setProperty(
            "right",
            "30px",
            "important"
        );


        topbar.style.setProperty(
            "left",
            "auto",
            "important"
        );


        topbar.style.setProperty(
            "bottom",
            "auto",
            "important"
        );


        topbar.style.setProperty(
            "width",
            "auto",
            "important"
        );


        topbar.style.setProperty(
            "display",
            "flex",
            "important"
        );


        topbar.style.setProperty(
            "align-items",
            "center",
            "important"
        );


        topbar.style.setProperty(
            "justify-content",
            "flex-end",
            "important"
        );


        topbar.style.setProperty(
            "gap",
            "18px",
            "important"
        );


        topbar.style.setProperty(
            "margin",
            "0",
            "important"
        );


        topbar.style.setProperty(
            "transform",
            "none",
            "important"
        );


        /*
         * Idioma.
         */

        if (language) {

            const isSwitcher =
                language.id ===
                "sabinoLanguageSwitcher";


            language.style.setProperty(
                "position",
                isSwitcher
                    ? "relative"
                    : "static",
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
                "bottom",
                "auto",
                "important"
            );


            language.style.setProperty(
                "transform",
                "none",
                "important"
            );
        }


        /*
         * Usuário.
         */

        if (profile) {

            profile.style.setProperty(
                "position",
                "static",
                "important"
            );


            profile.style.setProperty(
                "top",
                "auto",
                "important"
            );


            profile.style.setProperty(
                "right",
                "auto",
                "important"
            );


            profile.style.setProperty(
                "left",
                "auto",
                "important"
            );


            profile.style.setProperty(
                "bottom",
                "auto",
                "important"
            );


            profile.style.setProperty(
                "transform",
                "none",
                "important"
            );
        }


        return true;
    }


    function boot() {

        apply();


        [
            100,
            300,
            700,
            1500,
            3000
        ]
        .forEach(
            function (delay) {

                window.setTimeout(
                    apply,
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
        apply
    );


    window.addEventListener(
        "sabino:languagechange",
        apply
    );


    /*
     * NÃO existe:
     *
     * window.scrollY
     * scroll listener
     */

})();