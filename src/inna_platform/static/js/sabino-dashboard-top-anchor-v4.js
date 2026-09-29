
/* ============================================================
   SABINO.AI - DASHBOARD TOP ANCHOR V4

   ONE SHOT ONLY
   ============================================================ */

(function () {

    "use strict";

    if (window.SabinoDashboardTopAnchorV4) {
        return;
    }

    window.SabinoDashboardTopAnchorV4 = true;


    function applyOnce() {

        const topbar =
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
            );


        if (!topbar) {
            return;
        }


        const language =
            document.getElementById(
                "sabinoLanguageSwitcher"
            )
            ||
            document.getElementById(
                "languageButton"
            );


        const profile =
            document.querySelector(
                ".profile"
            );


        /*
         * Só garante a ordem uma única vez.
         */

        if (
            language &&
            language.parentElement !== topbar
        ) {

            if (
                profile &&
                profile.parentElement === topbar
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


        if (
            profile &&
            profile.parentElement !== topbar
        ) {

            topbar.appendChild(
                profile
            );
        }


        topbar.setAttribute(
            "data-sabino-dashboard-anchor-v4",
            "true"
        );


        /*
         * Aplicação única.
         * Nada roda durante scroll.
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
            "transform",
            "none",
            "important"
        );


        [language, profile]
            .filter(Boolean)
            .forEach(
                function (el) {

                    el.style.setProperty(
                        "position",
                        "relative",
                        "important"
                    );

                    el.style.setProperty(
                        "top",
                        "auto",
                        "important"
                    );

                    el.style.setProperty(
                        "right",
                        "auto",
                        "important"
                    );

                    el.style.setProperty(
                        "bottom",
                        "auto",
                        "important"
                    );

                    el.style.setProperty(
                        "left",
                        "auto",
                        "important"
                    );

                    el.style.setProperty(
                        "transform",
                        "none",
                        "important"
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
            applyOnce,
            {
                once: true
            }
        );

    }
    else {

        applyOnce();
    }


    window.addEventListener(
        "load",
        applyOnce,
        {
            once: true
        }
    );

})();
