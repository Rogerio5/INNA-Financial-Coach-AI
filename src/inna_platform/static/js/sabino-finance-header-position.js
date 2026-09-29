(function () {

    "use strict";

    const RIGHT_MARGIN = 28;
    const GAP = 18;
    const TOP = 22;


    function norm(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim();
    }


    function visible(el) {

        if (!el) return false;

        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();

        return (
            style.display !== "none" &&
            style.visibility !== "hidden" &&
            rect.width > 0 &&
            rect.height > 0
        );
    }


    function language() {

        return document.getElementById(
            "sabinoLanguageSwitcher"
        );
    }


    function containsInna(el) {

        return norm(
            el?.textContent
        )
        .toLowerCase()
        .includes(
            "perguntar a inna"
        );
    }


    function hasAvatar(el) {

        if (!el) return false;

        return Array.from(
            el.querySelectorAll("*")
        )
        .some(function (candidate) {

            const text = norm(
                candidate.textContent
            );

            if (!/^[A-Z]{2}$/.test(text)) {
                return false;
            }

            const r =
                candidate.getBoundingClientRect();

            return (
                r.width >= 24 &&
                r.width <= 65 &&
                r.height >= 24 &&
                r.height <= 65
            );
        });
    }


    function findUser() {

        const lang = language();

        const seeds = Array.from(
            document.querySelectorAll("body *")
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

            if (containsInna(el)) {
                return false;
            }

            const text =
                norm(el.textContent);

            return (
                text.includes("Premium") &&
                (
                    text.includes("Ativo") ||
                    text.includes("Active")
                )
            );
        });


        let best = null;
        let bestArea = Infinity;


        seeds.forEach(function (seed) {

            let current = seed;

            for (
                let level = 0;
                level < 7 && current;
                level += 1
            ) {

                if (
                    lang &&
                    current.contains(lang)
                ) {
                    break;
                }

                if (containsInna(current)) {
                    break;
                }

                const rect =
                    current.getBoundingClientRect();

                if (
                    rect.width >= 100 &&
                    rect.width <= 340 &&
                    rect.height >= 30 &&
                    rect.height <= 100 &&
                    hasAvatar(current)
                ) {

                    const area =
                        rect.width *
                        rect.height;

                    if (area < bestArea) {

                        best = current;
                        bestArea = area;
                    }
                }

                current =
                    current.parentElement;
            }
        });


        return best;
    }


    function setImportant(
        element,
        property,
        value
    ) {

        element.style.setProperty(
            property,
            value,
            "important"
        );
    }


    function positionHeader() {

        const lang = language();
        const user = findUser();

        if (!lang || !user) {

            console.debug(
                "SABINO_HEADER_POSITION_WAITING"
            );

            return false;
        }


        /* ==========================================
           USUÁRIO = EXTREMO DIREITO
           ========================================== */

        setImportant(
            user,
            "position",
            "fixed"
        );

        setImportant(
            user,
            "top",
            TOP + "px"
        );

        setImportant(
            user,
            "right",
            RIGHT_MARGIN + "px"
        );

        setImportant(
            user,
            "left",
            "auto"
        );

        setImportant(
            user,
            "bottom",
            "auto"
        );

        setImportant(
            user,
            "transform",
            "none"
        );

        setImportant(
            user,
            "margin",
            "0"
        );

        setImportant(
            user,
            "z-index",
            "2147483001"
        );


        /*
         * Mede novamente depois de colocar
         * o usuário no lugar final.
         */

        const userRect =
            user.getBoundingClientRect();


        /* ==========================================
           IDIOMA = IMEDIATAMENTE À ESQUERDA
           ========================================== */

        const languageRight =
            RIGHT_MARGIN +
            userRect.width +
            GAP;


        setImportant(
            lang,
            "position",
            "fixed"
        );

        setImportant(
            lang,
            "top",
            TOP + "px"
        );

        setImportant(
            lang,
            "right",
            languageRight + "px"
        );

        setImportant(
            lang,
            "left",
            "auto"
        );

        setImportant(
            lang,
            "bottom",
            "auto"
        );

        setImportant(
            lang,
            "transform",
            "none"
        );

        setImportant(
            lang,
            "margin",
            "0"
        );

        setImportant(
            lang,
            "z-index",
            "2147483000"
        );


        user.dataset
            .sabinoHeaderFinalUser =
            "true";

        lang.dataset
            .sabinoHeaderFinalLanguage =
            "true";


        console.info(
            "SABINO_FINANCE_HEADER_POSITION_FINAL=READY",
            {
                userWidth:
                    Math.round(
                        userRect.width
                    ),

                languageRight:
                    Math.round(
                        languageRight
                    )
            }
        );


        return true;
    }


    function run() {

        positionHeader();

        setTimeout(
            positionHeader,
            200
        );

        setTimeout(
            positionHeader,
            700
        );

        setTimeout(
            positionHeader,
            1500
        );

        setTimeout(
            positionHeader,
            2500
        );
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            run,
            {
                once: true
            }
        );

    }
    else {

        run();
    }


    let resizeTimer = null;

    window.addEventListener(
        "resize",
        function () {

            clearTimeout(
                resizeTimer
            );

            resizeTimer =
                setTimeout(
                    positionHeader,
                    100
                );
        }
    );

})();
