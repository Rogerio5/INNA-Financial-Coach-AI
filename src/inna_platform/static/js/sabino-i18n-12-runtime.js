(function () {

    "use strict";

    if (window.SabinoI18n12Runtime) {
        return;
    }


    /*
     * ========================================================
     * SABINO.AI - I18N COMPLEMENTAR DOS 12 IDIOMAS
     * ========================================================
     *
     * Atua somente sobre textos que ainda ficaram fora
     * do runtime principal.
     *
     * Não converte moeda.
     * Não altera valores numéricos.
     * Não limita navigator.language.
     */


    const SUPPORTED = new Set([
        "pt-BR",
        "en-US",
        "en-GB",
        "es-ES",
        "de-DE",
        "fr-FR",
        "it-IT",
        "ru-RU",
        "ar-SA",
        "ro-RO",
        "uk-UA",
        "de-CH"
    ]);


    const BASE_FALLBACK = {

        pt: "pt-BR",

        en: "en-US",

        es: "es-ES",

        de: "de-DE",

        fr: "fr-FR",

        it: "it-IT",

        ru: "ru-RU",

        ar: "ar-SA",

        ro: "ro-RO",

        uk: "uk-UA"

    };


    const TEXTS = {

        language: {

            "pt-BR": "Idioma",
            "en-US": "Language",
            "en-GB": "Language",
            "es-ES": "Idioma",
            "de-DE": "Sprache",
            "fr-FR": "Langue",
            "it-IT": "Lingua",
            "ru-RU": "Язык",
            "ar-SA": "اللغة",
            "ro-RO": "Limbă",
            "uk-UA": "Мова",
            "de-CH": "Sprache"

        },


        language_currency: {

            "pt-BR":
                "Idioma e moeda da plataforma",

            "en-US":
                "Platform language and currency",

            "en-GB":
                "Platform language and currency",

            "es-ES":
                "Idioma y moneda de la plataforma",

            "de-DE":
                "Sprache und Währung der Plattform",

            "fr-FR":
                "Langue et devise de la plateforme",

            "it-IT":
                "Lingua e valuta della piattaforma",

            "ru-RU":
                "Язык и валюта платформы",

            "ar-SA":
                "لغة المنصة وعملتها",

            "ro-RO":
                "Limba și moneda platformei",

            "uk-UA":
                "Мова та валюта платформи",

            "de-CH":
                "Sprache und Währung der Plattform"

        },


        automatic_browser: {

            "pt-BR":
                "Automático do navegador",

            "en-US":
                "Browser automatic",

            "en-GB":
                "Browser automatic",

            "es-ES":
                "Automático del navegador",

            "de-DE":
                "Automatisch vom Browser",

            "fr-FR":
                "Automatique du navigateur",

            "it-IT":
                "Automatico dal browser",

            "ru-RU":
                "Автоматически по браузеру",

            "ar-SA":
                "تلقائي من المتصفح",

            "ro-RO":
                "Automat din browser",

            "uk-UA":
                "Автоматично з браузера",

            "de-CH":
                "Automatisch vom Browser"

        },


        no_history: {

            "pt-BR":
                "Sem histórico ainda",

            "en-US":
                "No history yet",

            "en-GB":
                "No history yet",

            "es-ES":
                "Aún no hay historial",

            "de-DE":
                "Noch kein Verlauf",

            "fr-FR":
                "Aucun historique pour le moment",

            "it-IT":
                "Nessuna cronologia ancora",

            "ru-RU":
                "Истории пока нет",

            "ar-SA":
                "لا يوجد سجل حتى الآن",

            "ro-RO":
                "Niciun istoric încă",

            "uk-UA":
                "Історії ще немає",

            "de-CH":
                "Noch kein Verlauf"

        },


        no_expenses: {

            "pt-BR":
                "Nenhuma despesa registrada.",

            "en-US":
                "No expenses recorded.",

            "en-GB":
                "No expenses recorded.",

            "es-ES":
                "No hay gastos registrados.",

            "de-DE":
                "Keine Ausgaben erfasst.",

            "fr-FR":
                "Aucune dépense enregistrée.",

            "it-IT":
                "Nessuna spesa registrata.",

            "ru-RU":
                "Расходы не зарегистрированы.",

            "ar-SA":
                "لا توجد مصروفات مسجلة.",

            "ro-RO":
                "Nicio cheltuială înregistrată.",

            "uk-UA":
                "Жодних витрат не зареєстровано.",

            "de-CH":
                "Keine Ausgaben erfasst."

        },


        no_data_yet: {

            "pt-BR":
                "Sem dados ainda",

            "en-US":
                "No data yet",

            "en-GB":
                "No data yet",

            "es-ES":
                "Aún no hay datos",

            "de-DE":
                "Noch keine Daten",

            "fr-FR":
                "Aucune donnée pour le moment",

            "it-IT":
                "Nessun dato ancora",

            "ru-RU":
                "Данных пока нет",

            "ar-SA":
                "لا توجد بيانات حتى الآن",

            "ro-RO":
                "Nu există încă date",

            "uk-UA":
                "Даних поки немає",

            "de-CH":
                "Noch keine Daten"

        },


        no_data_available: {

            "pt-BR":
                "Nenhum dado disponível.",

            "en-US":
                "No data available.",

            "en-GB":
                "No data available.",

            "es-ES":
                "No hay datos disponibles.",

            "de-DE":
                "Keine Daten verfügbar.",

            "fr-FR":
                "Aucune donnée disponible.",

            "it-IT":
                "Nessun dato disponibile.",

            "ru-RU":
                "Нет доступных данных.",

            "ar-SA":
                "لا توجد بيانات متاحة.",

            "ro-RO":
                "Nu există date disponibile.",

            "uk-UA":
                "Немає доступних даних.",

            "de-CH":
                "Keine Daten verfügbar."

        },


        no_data_display: {

            "pt-BR":
                "Sem dados para exibir.",

            "en-US":
                "No data to display.",

            "en-GB":
                "No data to display.",

            "es-ES":
                "No hay datos para mostrar.",

            "de-DE":
                "Keine Daten zum Anzeigen.",

            "fr-FR":
                "Aucune donnée à afficher.",

            "it-IT":
                "Nessun dato da visualizzare.",

            "ru-RU":
                "Нет данных для отображения.",

            "ar-SA":
                "لا توجد بيانات لعرضها.",

            "ro-RO":
                "Nu există date de afișat.",

            "uk-UA":
                "Немає даних для відображення.",

            "de-CH":
                "Keine Daten zum Anzeigen."

        },


        register_expense: {

            "pt-BR":
                "Registre uma despesa para identificar sua maior categoria.",

            "en-US":
                "Record an expense to identify your largest category.",

            "en-GB":
                "Record an expense to identify your largest category.",

            "es-ES":
                "Registra un gasto para identificar tu categoría principal.",

            "de-DE":
                "Erfassen Sie eine Ausgabe, um Ihre größte Kategorie zu erkennen.",

            "fr-FR":
                "Enregistrez une dépense pour identifier votre principale catégorie.",

            "it-IT":
                "Registra una spesa per identificare la tua categoria principale.",

            "ru-RU":
                "Добавьте расход, чтобы определить крупнейшую категорию.",

            "ar-SA":
                "سجّل مصروفًا لتحديد أكبر فئة إنفاق لديك.",

            "ro-RO":
                "Înregistrează o cheltuială pentru a identifica principala categorie.",

            "uk-UA":
                "Додайте витрату, щоб визначити найбільшу категорію.",

            "de-CH":
                "Erfassen Sie eine Ausgabe, um Ihre grösste Kategorie zu erkennen."

        }

    };


    /*
     * Texto português original -> chave interna.
     */

    const SOURCE_TEXT = new Map([

        [
            "Idioma",
            "language"
        ],

        [
            "Idioma e moeda da plataforma",
            "language_currency"
        ],

        [
            "Automático do navegador",
            "automatic_browser"
        ],

        [
            "Sem histórico ainda",
            "no_history"
        ],

        [
            "Nenhuma despesa registrada.",
            "no_expenses"
        ],

        [
            "Nenhuma despesa registrada",
            "no_expenses"
        ],

        [
            "Sem dados ainda",
            "no_data_yet"
        ],

        [
            "Nenhum dado disponível.",
            "no_data_available"
        ],

        [
            "Nenhum dado disponível",
            "no_data_available"
        ],

        [
            "Sem dados para exibir.",
            "no_data_display"
        ],

        [
            "Sem dados para exibir",
            "no_data_display"
        ],

        [
            "Registre uma despesa para identificar sua maior categoria.",
            "register_expense"
        ]

    ]);


    const PT_MONTHS = {

        jan: 0,

        fev: 1,

        mar: 2,

        abr: 3,

        mai: 4,

        jun: 5,

        jul: 6,

        ago: 7,

        set: 8,

        out: 9,

        nov: 10,

        dez: 11

    };


    function normalizeLocale(
        value
    ) {

        if (!value) {
            return null;
        }


        const raw =
            String(
                value
            )
            .trim()
            .replace(
                "_",
                "-"
            );


        if (!raw) {
            return null;
        }


        try {

            const canonical =
                Intl.getCanonicalLocales(
                    raw
                )[0];

            if (canonical) {
                return canonical;
            }

        }
        catch (_) {
            // fallback abaixo
        }


        return raw;

    }


    function activeLocale() {

        let locale = null;


        if (
            window.SabinoLocale &&
            typeof window.SabinoLocale.current ===
                "function"
        ) {

            try {

                locale =
                    window.SabinoLocale.current();

            }
            catch (_) {
                locale = null;
            }

        }


        if (!locale) {

            const source =
                localStorage.getItem(
                    "sabino_language_source"
                );


            if (source === "manual") {

                locale =
                    localStorage.getItem(
                        "sabino_language_manual"
                    );

            }

        }


        if (!locale) {

            locale =
                navigator.language ||
                "pt-BR";

        }


        return normalizeLocale(
            locale
        );

    }


    function supportedLocale() {

        const locale =
            activeLocale();


        if (
            locale &&
            SUPPORTED.has(
                locale
            )
        ) {

            return locale;

        }


        /*
         * Em modo automático:
         * outros idiomas continuam livres.
         *
         * Esta camada complementar NÃO força
         * idioma fora dos 12.
         */

        return null;

    }


    function translation(
        key,
        locale
    ) {

        const group =
            TEXTS[key];

        if (!group) {
            return null;
        }


        return (
            group[locale] ||
            group["pt-BR"] ||
            null
        );

    }


    function normalizeSourceText(
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


    function localizeKnownText(
        value,
        locale
    ) {

        const normalized =
            normalizeSourceText(
                value
            );


        const key =
            SOURCE_TEXT.get(
                normalized
            );


        if (!key) {
            return null;
        }


        return translation(
            key,
            locale
        );

    }


    function parsePortugueseMonth(
        text
    ) {

        const normalized =
            normalizeSourceText(
                text
            );


        /*
         * Exemplo:
         * Abr/26
         */

        const match =
            normalized.match(
                /^([A-Za-zÀ-ÿ]{3})\/(\d{2})$/
            );


        if (!match) {
            return null;
        }


        const key =
            match[1]
            .toLocaleLowerCase(
                "pt-BR"
            );


        if (
            !Object.prototype.hasOwnProperty.call(
                PT_MONTHS,
                key
            )
        ) {
            return null;
        }


        return {

            month:
                PT_MONTHS[key],

            year:
                2000 +
                Number(
                    match[2]
                ),

            shortYear:
                match[2]

        };

    }


    function localizedMonth(
        text,
        locale
    ) {

        const parsed =
            parsePortugueseMonth(
                text
            );


        if (!parsed) {
            return null;
        }


        const date =
            new Date(
                parsed.year,
                parsed.month,
                1
            );


        let month;


        try {

            month =
                new Intl.DateTimeFormat(
                    locale,
                    {
                        month: "short"
                    }
                )
                .format(
                    date
                );

        }
        catch (_) {

            return null;

        }


        month =
            String(
                month
            )
            .trim();


        return (
            month +
            "/" +
            parsed.shortYear
        );

    }


    function shouldIgnoreNode(
        node
    ) {

        const parent =
            node &&
            node.parentElement;


        if (!parent) {
            return true;
        }


        const tag =
            parent.tagName;


        return (
            tag === "SCRIPT" ||
            tag === "STYLE" ||
            tag === "NOSCRIPT" ||
            tag === "TEXTAREA"
        );

    }


    function translateTextNode(
        node,
        locale
    ) {

        if (
            !node ||
            shouldIgnoreNode(
                node
            )
        ) {
            return;
        }


        const original =
            node.nodeValue;


        const normalized =
            normalizeSourceText(
                original
            );


        if (!normalized) {
            return;
        }


        const known =
            localizeKnownText(
                normalized,
                locale
            );


        if (
            known &&
            known !== normalized
        ) {

            node.nodeValue =
                original.replace(
                    normalized,
                    known
                );

            return;
        }


        const month =
            localizedMonth(
                normalized,
                locale
            );


        if (
            month &&
            month !== normalized
        ) {

            node.nodeValue =
                original.replace(
                    normalized,
                    month
                );

        }

    }


    function translateElement(
        root,
        locale
    ) {

        if (!root) {
            return;
        }


        if (
            root.nodeType ===
            Node.TEXT_NODE
        ) {

            translateTextNode(
                root,
                locale
            );

            return;
        }


        if (
            root.nodeType !==
            Node.ELEMENT_NODE &&
            root.nodeType !==
            Node.DOCUMENT_NODE
        ) {
            return;
        }


        const walker =
            document.createTreeWalker(
                root,
                NodeFilter.SHOW_TEXT
            );


        const nodes = [];

        let node;


        while (
            (
                node =
                    walker.nextNode()
            )
        ) {

            nodes.push(
                node
            );

        }


        nodes.forEach(
            function (item) {

                translateTextNode(
                    item,
                    locale
                );

            }
        );

    }


    function charts() {

        if (!window.Chart) {
            return [];
        }


        const result = [];


        /*
         * Chart.js 3/4
         */

        if (
            typeof window.Chart.getChart ===
            "function"
        ) {

            document
                .querySelectorAll(
                    "canvas"
                )
                .forEach(
                    function (canvas) {

                        try {

                            const chart =
                                window.Chart.getChart(
                                    canvas
                                );

                            if (chart) {
                                result.push(
                                    chart
                                );
                            }

                        }
                        catch (_) {
                            // segue
                        }

                    }
                );

        }


        /*
         * Chart.js versões anteriores.
         */

        if (
            !result.length &&
            window.Chart.instances
        ) {

            Object
                .values(
                    window.Chart.instances
                )
                .forEach(
                    function (chart) {

                        if (chart) {
                            result.push(
                                chart
                            );
                        }

                    }
                );

        }


        return [
            ...new Set(
                result
            )
        ];

    }


    function localizeChart(
        chart,
        locale
    ) {

        if (
            !chart ||
            !chart.data ||
            !Array.isArray(
                chart.data.labels
            )
        ) {
            return false;
        }


        let changed =
            false;


        const labels =
            chart.data.labels.map(
                function (label) {

                    if (
                        typeof label !==
                        "string"
                    ) {
                        return label;
                    }


                    const localized =
                        localizedMonth(
                            label,
                            locale
                        );


                    if (
                        localized &&
                        localized !== label
                    ) {

                        changed =
                            true;

                        return localized;

                    }


                    return label;

                }
            );


        if (!changed) {
            return false;
        }


        chart.data.labels =
            labels;


        try {

            chart.update(
                "none"
            );

        }
        catch (_) {

            try {
                chart.update();
            }
            catch (_) {
                // nada
            }

        }


        return true;

    }


    function localizeCharts(
        locale
    ) {

        charts().forEach(
            function (chart) {

                localizeChart(
                    chart,
                    locale
                );

            }
        );

    }


    function translateButton(
        locale
    ) {

        /*
         * Botão novo.
         */

        const panel =
            document.getElementById(
                "sabinoLanguagePanel"
            );


        if (panel) {

            const headerStrong =
                panel.querySelector(
                    ".sabino-lang-panel-header strong"
                );


            if (headerStrong) {

                headerStrong.textContent =
                    translation(
                        "language",
                        locale
                    );

            }


            const headerSubtitle =
                panel.querySelector(
                    ".sabino-lang-panel-header span"
                );


            if (headerSubtitle) {

                headerSubtitle.textContent =
                    translation(
                        "language_currency",
                        locale
                    );

            }


            const auto =
                panel.querySelector(
                    ".sabino-lang-auto"
                );


            if (auto) {

                const first =
                    auto.querySelector(
                        "span:first-child"
                    );


                if (first) {

                    const manual =
                        localStorage.getItem(
                            "sabino_language_source"
                        ) ===
                        "manual";


                    first.textContent =
                        (
                            manual
                                ? ""
                                : "✓ "
                        ) +
                        translation(
                            "automatic_browser",
                            locale
                        );

                }

            }

        }

    }


    function apply() {

        const locale =
            supportedLocale();


        if (!locale) {

            /*
             * Fora dos 12 idiomas:
             * navegador continua livre e
             * este runtime não interfere.
             */

            return;

        }


        translateElement(
            document.body,
            locale
        );


        translateButton(
            locale
        );


        localizeCharts(
            locale
        );

    }


    let observer = null;


    function observe() {

        if (
            observer ||
            !document.body
        ) {
            return;
        }


        observer =
            new MutationObserver(
                function (mutations) {

                    const locale =
                        supportedLocale();


                    if (!locale) {
                        return;
                    }


                    mutations.forEach(
                        function (mutation) {

                            mutation
                                .addedNodes
                                .forEach(
                                    function (node) {

                                        translateElement(
                                            node,
                                            locale
                                        );

                                    }
                                );

                        }
                    );


                    translateButton(
                        locale
                    );

                }
            );


        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );

    }


    function delayedChartPasses() {

        const delays = [
            0,
            200,
            500,
            1000,
            1800,
            3000
        ];


        delays.forEach(
            function (delay) {

                window.setTimeout(
                    function () {

                        const locale =
                            supportedLocale();


                        if (locale) {

                            localizeCharts(
                                locale
                            );

                            translateButton(
                                locale
                            );

                        }

                    },
                    delay
                );

            }
        );

    }


    function start() {

        apply();

        observe();

        delayedChartPasses();

    }


    window.SabinoI18n12Runtime = {

        apply:
            apply,

        locale:
            supportedLocale

    };


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
