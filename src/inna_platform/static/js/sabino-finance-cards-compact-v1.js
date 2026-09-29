/* ============================================================
   SABINO.AI - FINANCE CARDS COMPACT V1
   ============================================================ */

(function () {

    "use strict";


    if (window.SabinoFinanceCardsCompactV1) {
        return;
    }


    window.SabinoFinanceCardsCompactV1 = true;


    function normalize(value) {

        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }


    function findCardFromHeading(
        terms
    ) {

        const headings =
            Array.from(
                document.querySelectorAll(
                    "h1,h2,h3,h4"
                )
            );


        const heading =
            headings.find(
                function (element) {

                    const text =
                        normalize(
                            element.textContent
                        );


                    return terms.some(
                        function (term) {

                            return text.includes(
                                normalize(term)
                            );

                        }
                    );

                }
            );


        if (!heading) {
            return null;
        }


        /*
         * Preferimos somente containers semânticos
         * pequenos/próximos. Nenhum elemento é movido.
         */

        const closest =
            heading.closest(
                "article.panel, article, section.panel, section, .panel, .card"
            );


        if (closest) {
            return closest;
        }


        /*
         * Fallback conservador:
         * subir poucos níveis.
         */

        let node =
            heading.parentElement;


        for (
            let level = 0;
            node &&
            node !== document.body &&
            level < 5;
            level += 1
        ) {

            const rect =
                node.getBoundingClientRect();


            if (
                rect.width > 300 &&
                rect.height > 250
            ) {

                return node;
            }


            node =
                node.parentElement;
        }


        return null;
    }


    function markMonthCard() {

        /*
         * A legenda que já instalamos marca
         * o card mensal com este atributo.
         */

        let card =
            document.querySelector(
                '[data-sabino-month-chart-card-v1="true"]'
            );


        if (!card) {

            card =
                findCardFromHeading([
                    "Gastos por mês",
                    "Gastos por mes",
                    "Expenses by month",
                    "Gastos por mes"
                ]);
        }


        if (!card) {
            return false;
        }


        card.setAttribute(
            "data-sabino-month-card-compact-v1",
            "true"
        );


        return true;
    }


    function markCategoryCard() {

        /*
         * Primeiro tentamos o host exato
         * do componente de categoria.
         */

        const host =
            document.querySelector(
                ".sabino-category-host, .sabino-cat-v2"
            );


        let card =
            null;


        if (host) {

            card =
                host.closest(
                    "article.panel, article, section.panel, section, .panel, .card"
                );
        }


        if (!card) {

            card =
                findCardFromHeading([
                    "Gastos por categoria",
                    "Expenses by category",
                    "Gastos por categoría"
                ]);
        }


        if (!card) {
            return false;
        }


        card.setAttribute(
            "data-sabino-category-card-compact-v1",
            "true"
        );


        return true;
    }


    function apply() {

        markMonthCard();
        markCategoryCard();
    }


    function boot() {

        apply();


        [
            100,
            300,
            700,
            1200
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

})();
