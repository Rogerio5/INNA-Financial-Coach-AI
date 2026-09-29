/* ============================================================
   SABINO.AI - MONTH CHART LEGEND V1
   ============================================================ */

(function () {

    "use strict";

    if (window.SabinoMonthChartLegendV1) {
        return;
    }

    window.SabinoMonthChartLegendV1 = true;


    function normalize(value) {

        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }


    function findCard() {

        const headings =
            Array.from(
                document.querySelectorAll(
                    "h1,h2,h3,h4"
                )
            );


        const heading =
            headings.find(
                function (element) {

                    return (
                        normalize(
                            element.textContent
                        )
                        .includes(
                            "gastos por mes"
                        )
                    );

                }
            );


        if (!heading) {
            return null;
        }


        let node =
            heading.parentElement;


        while (
            node &&
            node !== document.body
        ) {

            const text =
                normalize(
                    node.textContent
                );


            const rect =
                node.getBoundingClientRect();


            if (
                text.includes(
                    "gastos por mes"
                ) &&
                text.includes(
                    "ultimos 6 meses"
                ) &&
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


    function legendText() {

        const lang =
            String(
                document.documentElement.lang ||
                "pt-BR"
            )
            .toLowerCase();


        const map = {

            "pt":
                "Maior gasto do período",

            "en":
                "Highest spending in period",

            "es":
                "Mayor gasto del período",

            "de":
                "Höchste Ausgabe im Zeitraum",

            "fr":
                "Dépense la plus élevée",

            "it":
                "Spesa più alta del periodo",

            "ru":
                "Наибольший расход за период",

            "ar":
                "أعلى إنفاق في الفترة",

            "ro":
                "Cea mai mare cheltuială",

            "uk":
                "Найбільша витрата за період"
        };


        const prefix =
            lang.split("-")[0];


        return (
            map[prefix] ||
            map.pt
        );
    }


    function mount() {

        const card =
            findCard();


        if (!card) {
            return false;
        }


        card.setAttribute(
            "data-sabino-month-chart-card-v1",
            "true"
        );


        let legend =
            card.querySelector(
                ".sabino-month-legend-v1"
            );


        if (!legend) {

            legend =
                document.createElement(
                    "div"
                );


            legend.className =
                "sabino-month-legend-v1";


            legend.innerHTML = `
                <span class="sabino-month-legend-v1-dot"></span>
                <span class="sabino-month-legend-v1-text"></span>
            `;


            card.appendChild(
                legend
            );
        }


        const text =
            legend.querySelector(
                ".sabino-month-legend-v1-text"
            );


        if (text) {

            text.textContent =
                legendText();
        }


        return true;
    }


    function boot() {

        mount();


        [
            100,
            300,
            700,
            1200
        ]
        .forEach(
            function (delay) {

                window.setTimeout(
                    mount,
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
        mount
    );

})();
