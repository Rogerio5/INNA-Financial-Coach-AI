/* ============================================================
   SABINO.AI - GASTOS POR CATEGORIA V2

   DEMO:
   usa dados fictícios SOMENTE em ?demo=1

   REAL:
   só renderiza quando existirem dados reais válidos.
   ============================================================ */

(function () {

    "use strict";


    if (window.SabinoFinanceCategoryV2) {
        return;
    }


    const DEMO_DATA = [

        {
            name: "Transporte",
            value: 1092.00,
            color: "#3b82f6"
        },

        {
            name: "Alimentação",
            value: 624.00,
            color: "#ff9b2f"
        },

        {
            name: "Moradia",
            value: 468.00,
            color: "#20d3a0"
        },

        {
            name: "Lazer",
            value: 374.40,
            color: "#9362df"
        },

        {
            name: "Saúde",
            value: 312.00,
            color: "#ff525f"
        },

        {
            name: "Outros",
            value: 249.60,
            color: "#ffd11f"
        }

    ];


    const COLORS = [
        "#3b82f6",
        "#ff9b2f",
        "#20d3a0",
        "#9362df",
        "#ff525f",
        "#ffd11f",
        "#38bdf8",
        "#a3e635"
    ];


    const CURRENCY_BY_LOCALE = {

        "pt-BR": "BRL",
        "en-US": "USD",
        "en-GB": "GBP",
        "es-ES": "EUR",
        "de-DE": "EUR",
        "fr-FR": "EUR",
        "it-IT": "EUR",
        "ru-RU": "RUB",
        "ar-SA": "SAR",
        "ro-RO": "RON",
        "uk-UA": "UAH",
        "de-CH": "CHF"

    };


    function normalizeText(value) {

        return String(value || "")
            .normalize("NFD")
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .toLowerCase()
            .trim();
    }


    function isDemo() {

        const params =
            new URLSearchParams(
                window.location.search
            );


        return (
            params.get("demo") === "1"
        );
    }


    function normalizeData(raw) {

        if (!Array.isArray(raw)) {
            return [];
        }


        return raw
            .map(function (item, index) {

                const value =
                    Number(
                        item &&
                        item.value
                    );


                if (
                    !Number.isFinite(value) ||
                    value <= 0
                ) {

                    return null;
                }


                return {

                    name:
                        String(
                            item.name ||
                            item.category ||
                            "Categoria"
                        ),

                    value: value,

                    color:
                        item.color ||
                        COLORS[
                            index %
                            COLORS.length
                        ]

                };

            })
            .filter(Boolean);

    }


    /*
     * REAL:
     *
     * Aceitamos APENAS uma fonte explicitamente
     * marcada como dados reais.
     *
     * Não copiamos números fictícios do HTML.
     */

    function getRealData() {

        if (
            Array.isArray(
                window.SABINO_FINANCE_CATEGORY_DATA
            )
        ) {

            return normalizeData(
                window.SABINO_FINANCE_CATEGORY_DATA
            );
        }


        const json =
            document.getElementById(
                "sabinoFinanceCategoryRealData"
            );


        if (json) {

            try {

                return normalizeData(
                    JSON.parse(
                        json.textContent
                    )
                );

            }
            catch (error) {

                console.warn(
                    "[Sabino.AI] Dados reais de categorias inválidos.",
                    error
                );
            }
        }


        return [];
    }


    function findCard() {

        const headings =
            Array.from(
                document.querySelectorAll(
                    "h1,h2,h3,h4"
                )
            );


        const heading =
            headings.find(function (element) {

                return (
                    normalizeText(
                        element.textContent
                    ) ===
                    "gastos por categoria"
                );

            });


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
                normalizeText(
                    node.textContent
                );


            const hasTarget =
                text.includes(
                    "gastos por categoria"
                );


            const hasHighlight =
                text.includes(
                    "maior gasto do mes"
                );


            const containsOtherCard =
                text.includes(
                    "gastos por mes"
                ) ||
                text.includes(
                    "proximos passos"
                );


            if (
                hasTarget &&
                hasHighlight &&
                !containsOtherCard
            ) {

                return node;
            }


            node =
                node.parentElement;
        }


        return (
            heading.parentElement ||
            null
        );
    }


    function resolveLocale() {

        const value =
            String(
                window.SABINO_FINANCE_LOCALE ||
                document.documentElement.lang ||
                "pt-BR"
            );


        return (
            CURRENCY_BY_LOCALE[value]
                ? value
                : "pt-BR"
        );
    }


    function resolveCurrency(locale) {

        return (
            window.SABINO_FINANCE_CURRENCY ||
            CURRENCY_BY_LOCALE[locale] ||
            "BRL"
        );
    }


    function money(value) {

        const locale =
            resolveLocale();


        const currency =
            resolveCurrency(
                locale
            );


        try {

            return new Intl.NumberFormat(
                locale,
                {
                    style: "currency",
                    currency: currency,
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            )
            .format(value);

        }
        catch (_) {

            return Number(value)
                .toFixed(2);

        }
    }


    function escapeHtml(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function gradient(data, total) {

        let current = 0;


        return data
            .map(function (item) {

                const start =
                    current;


                const percentage =
                    (
                        item.value /
                        total
                    ) * 100;


                current +=
                    percentage;


                return (
                    item.color +
                    " " +
                    start.toFixed(3) +
                    "% " +
                    current.toFixed(3) +
                    "%"
                );

            })
            .join(", ");
    }


    function render(data) {

        const card =
            findCard();


        if (!card) {
            return false;
        }


        /*
         * REAL sem valor real:
         * não mostramos gráfico fictício.
         */

        if (
            !isDemo() &&
            data.length === 0
        ) {

            card.hidden = true;

            card.setAttribute(
                "data-sabino-category-state",
                "hidden-no-real-data"
            );


            return true;
        }


        card.hidden = false;

        card.classList.add(
            "sabino-category-host"
        );


        card.setAttribute(
            "data-sabino-category-state",
            isDemo()
                ? "demo"
                : "real"
        );


        const total =
            data.reduce(
                function (sum, item) {

                    return (
                        sum +
                        item.value
                    );

                },
                0
            );


        if (!(total > 0)) {

            if (!isDemo()) {
                card.hidden = true;
            }

            return true;
        }


        const ordered =
            data
                .slice()
                .sort(
                    function (a, b) {

                        return (
                            b.value -
                            a.value
                        );

                    }
                );


        const top =
            ordered[0];


        const rows =
            ordered
                .map(
                    function (item, index) {

                        const percent =
                            (
                                item.value /
                                total
                            ) * 100;


                        return `
                            <div
                                class="sabino-cat-v2-row ${index === 0 ? "is-top" : ""}"
                                title="${escapeHtml(item.name)} • ${escapeHtml(money(item.value))} • ${percent.toFixed(0)}%"
                            >
                                <span
                                    class="sabino-cat-v2-dot"
                                    style="background:${escapeHtml(item.color)}"
                                ></span>

                                <span class="sabino-cat-v2-name">
                                    ${escapeHtml(item.name)}
                                </span>

                                <span class="sabino-cat-v2-value">
                                    ${escapeHtml(money(item.value))}
                                </span>

                                <span class="sabino-cat-v2-percent">
                                    ${percent.toFixed(0)}%
                                </span>
                            </div>
                        `;

                    }
                )
                .join("");


        const topPercent =
            (
                top.value /
                total
            ) * 100;


        const donutGradient =
            gradient(
                data,
                total
            );


        card.innerHTML = `
            <div class="sabino-cat-v2">

                <div class="sabino-cat-v2-head">

                    <h2>
                        Gastos por categoria
                    </h2>

                    <p>
                        Veja onde seu dinheiro está sendo mais usado.
                    </p>

                </div>


                <div class="sabino-cat-v2-main">

                    <div
                        class="sabino-cat-v2-donut"
                        style="background:conic-gradient(${donutGradient})"
                        role="img"
                        aria-label="Distribuição dos gastos por categoria"
                    >

                        <div class="sabino-cat-v2-hole">

                            <span class="sabino-cat-v2-total-label">
                                Total
                            </span>

                            <strong class="sabino-cat-v2-total">
                                ${escapeHtml(money(total))}
                            </strong>

                        </div>

                    </div>


                    <div class="sabino-cat-v2-legend">
                        ${rows}
                    </div>

                </div>


                <div class="sabino-cat-v2-highlight">

                    <div>

                        <span class="sabino-cat-v2-highlight-label">
                            Maior gasto do mês
                        </span>

                        <h3 class="sabino-cat-v2-highlight-title">
                            ${escapeHtml(top.name)}
                        </h3>

                        <div class="sabino-cat-v2-highlight-value">
                            Categoria com maior participação nas despesas.
                        </div>

                    </div>


                    <div class="sabino-cat-v2-highlight-right">

                        <strong class="sabino-cat-v2-highlight-money">
                            ${escapeHtml(money(top.value))}
                        </strong>

                        <span class="sabino-cat-v2-highlight-percent">
                            ${topPercent.toFixed(0)}% do total
                        </span>

                    </div>

                </div>

            </div>
        `;


        return true;
    }


    function refresh() {

        const data =
            isDemo()
                ? normalizeData(DEMO_DATA)
                : getRealData();


        render(data);
    }


    window.SabinoFinanceCategoryV2 = {

        refresh: refresh,

        setRealData:
            function (data) {

                window.SABINO_FINANCE_CATEGORY_DATA =
                    normalizeData(data);


                refresh();
            }

    };


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            refresh,
            {
                once: true
            }
        );

    }
    else {

        refresh();
    }


    window.addEventListener(
        "sabino:locale-change",
        refresh
    );


    window.addEventListener(
        "sabino:finance-data-updated",
        function (event) {

            if (
                event.detail &&
                Array.isArray(
                    event.detail.categories
                )
            ) {

                window.SABINO_FINANCE_CATEGORY_DATA =
                    event.detail.categories;
            }


            refresh();

        }
    );

})();
