
(function () {

    "use strict";


    if (window.SabinoCurrency) {
        return;
    }


    const STORAGE_CURRENT =
        "sabino_currency";

    const STORAGE_MANUAL =
        "sabino_currency_manual";

    const STORAGE_SOURCE =
        "sabino_currency_source";

    const FALLBACK_CURRENCY =
        "BRL";


    /*
     * Moeda padrão pela região.
     *
     * Se o locale vier sem região, Intl.Locale.maximize()
     * tenta inferir a região provável.
     */

    const REGION_TO_CURRENCY = {};


    function assign(
        regions,
        currency
    ) {

        regions
            .trim()
            .split(/\s+/)
            .filter(Boolean)
            .forEach(
                function (region) {

                    REGION_TO_CURRENCY[
                        region
                    ] = currency;

                }
            );

    }


    /* EURO */
    assign(
        `
        AD AT AX BE BL CY DE EE ES FI FR GF GP GR
        HR IE IT LT LU LV MC MF MQ MT NL PM PT RE
        SI SK SM TF VA YT BG
        `,
        "EUR"
    );


    /* DOLAR DOS ESTADOS UNIDOS */
    assign(
        `
        US AS BQ EC FM GU IO MH MP PR PW SV TC TL
        UM VG VI
        `,
        "USD"
    );


    assign("BR", "BRL");
    assign("GB GG IM JE", "GBP");
    assign("CA", "CAD");

    assign(
        "AU CC CX HM KI NF NR TV",
        "AUD"
    );

    assign(
        "NZ CK NU PN TK",
        "NZD"
    );

    assign("CH LI", "CHF");

    assign("JP", "JPY");
    assign("CN", "CNY");
    assign("HK", "HKD");
    assign("TW", "TWD");
    assign("KR", "KRW");

    assign("IN", "INR");
    assign("PK", "PKR");
    assign("BD", "BDT");
    assign("LK", "LKR");
    assign("NP", "NPR");
    assign("BT", "BTN");
    assign("MV", "MVR");

    assign("ID", "IDR");
    assign("MY", "MYR");
    assign("SG", "SGD");
    assign("TH", "THB");
    assign("VN", "VND");
    assign("PH", "PHP");
    assign("BN", "BND");
    assign("KH", "KHR");
    assign("LA", "LAK");
    assign("MM", "MMK");
    assign("MN", "MNT");

    assign("KZ", "KZT");
    assign("KG", "KGS");
    assign("TJ", "TJS");
    assign("TM", "TMT");
    assign("UZ", "UZS");

    assign("AF", "AFN");
    assign("IR", "IRR");
    assign("IQ", "IQD");
    assign("IL PS", "ILS");
    assign("JO", "JOD");
    assign("LB", "LBP");
    assign("SY", "SYP");

    assign("SA", "SAR");
    assign("AE", "AED");
    assign("QA", "QAR");
    assign("KW", "KWD");
    assign("BH", "BHD");
    assign("OM", "OMR");
    assign("YE", "YER");

    assign("TR", "TRY");
    assign("RU", "RUB");
    assign("UA", "UAH");

    /*
     * Bielorrússia
     */
    assign("BY", "BYN");

    assign("PL", "PLN");
    assign("CZ", "CZK");
    assign("HU", "HUF");
    assign("RO", "RON");
    assign("RS", "RSD");
    assign("BA", "BAM");
    assign("MK", "MKD");
    assign("AL", "ALL");
    assign("MD", "MDL");
    assign("GE", "GEL");
    assign("AM", "AMD");
    assign("AZ", "AZN");

    assign("IS", "ISK");
    assign("NO SJ BV", "NOK");
    assign("SE", "SEK");
    assign("DK FO GL", "DKK");

    assign("ZA", "ZAR");
    assign("LS", "LSL");
    assign("SZ", "SZL");
    assign("NA", "NAD");
    assign("BW", "BWP");
    assign("ZM", "ZMW");
    assign("ZW", "ZWG");
    assign("MW", "MWK");
    assign("MZ", "MZN");
    assign("AO", "AOA");

    assign("NG", "NGN");
    assign("GH", "GHS");
    assign("KE", "KES");
    assign("UG", "UGX");
    assign("TZ", "TZS");
    assign("RW", "RWF");
    assign("BI", "BIF");
    assign("CD", "CDF");
    assign("ET", "ETB");
    assign("ER", "ERN");
    assign("SD", "SDG");
    assign("SS", "SSP");
    assign("SO", "SOS");
    assign("DJ", "DJF");

    assign("MG", "MGA");
    assign("MU", "MUR");
    assign("SC", "SCR");
    assign("KM", "KMF");
    assign("CV", "CVE");
    assign("GM", "GMD");
    assign("GN", "GNF");
    assign("LR", "LRD");
    assign("SL", "SLE");
    assign("ST", "STN");

    assign(
        "BJ BF CI GW ML NE SN TG",
        "XOF"
    );

    assign(
        "CM CF TD CG GQ GA",
        "XAF"
    );

    assign("MA EH", "MAD");
    assign("DZ", "DZD");
    assign("TN", "TND");
    assign("LY", "LYD");
    assign("EG", "EGP");
    assign("MR", "MRU");

    assign("MX", "MXN");
    assign("GT", "GTQ");
    assign("BZ", "BZD");
    assign("HN", "HNL");
    assign("NI", "NIO");
    assign("CR", "CRC");
    assign("PA", "PAB");
    assign("CU", "CUP");
    assign("DO", "DOP");
    assign("HT", "HTG");
    assign("JM", "JMD");
    assign("TT", "TTD");
    assign("BB", "BBD");
    assign("BS", "BSD");

    assign(
        "AG DM GD KN LC VC",
        "XCD"
    );

    assign("AW", "AWG");

    /*
     * Curaçao / Sint Maarten:
     * Caribbean Guilder.
     */
    assign(
        "CW SX",
        "XCG"
    );

    assign("KY", "KYD");
    assign("BM", "BMD");
    assign("FK", "FKP");
    assign("GY", "GYD");
    assign("SR", "SRD");

    assign("AR", "ARS");
    assign("CL", "CLP");
    assign("CO", "COP");
    assign("PE", "PEN");
    assign("UY", "UYU");
    assign("PY", "PYG");
    assign("BO", "BOB");
    assign("VE", "VES");

    assign("FJ", "FJD");
    assign("PG", "PGK");
    assign("SB", "SBD");
    assign("VU", "VUV");
    assign("WS", "WST");
    assign("TO", "TOP");

    assign(
        "NC PF WF",
        "XPF"
    );


    function localeValue() {

        try {

            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current
                    === "function"
            ) {

                return (
                    window.SabinoLocale.current()
                    ||
                    navigator.language
                    ||
                    "pt-BR"
                );

            }

        }
        catch (_) {
        }


        return (
            localStorage.getItem(
                "sabino_language"
            )
            ||
            navigator.language
            ||
            "pt-BR"
        );

    }


    function normalizeLocale(
        locale
    ) {

        return String(
            locale ||
            "pt-BR"
        )
            .replace(
                /_/g,
                "-"
            )
            .trim();

    }


    function localeRegion(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );


        try {

            const direct =
                new Intl.Locale(
                    normalized
                );

            if (
                direct.region
            ) {

                return direct.region;

            }


            const maximized =
                direct.maximize();

            return (
                maximized.region ||
                null
            );

        }
        catch (_) {

            return null;

        }

    }


    function automaticCurrency() {

        const locale =
            localeValue();

        const normalized =
            String(
                locale ||
                ""
            );

        /*
         * SABINO_LOCALE_CURRENCY_MAP_V3
         *
         * Apenas formatação.
         * Nenhuma conversão cambial.
         */
        const LOCALE_TO_CURRENCY = {

            "af-ZA": "ZAR",

            "ar-AE": "AED",
            "ar-EG": "EGP",
            "ar-MA": "MAD",
            "ar-SA": "SAR",

            "bn-BD": "BDT",

            "cs-CZ": "CZK",
            "da-DK": "DKK",

            "de-AT": "EUR",
            "de-CH": "CHF",
            "de-DE": "EUR",

            "el-GR": "EUR",

            "en-AU": "AUD",
            "en-CA": "CAD",
            "en-GB": "GBP",
            "en-IN": "INR",
            "en-NZ": "NZD",
            "en-US": "USD",

            "es-AR": "ARS",
            "es-CL": "CLP",
            "es-CO": "COP",
            "es-ES": "EUR",
            "es-MX": "MXN",
            "es-PE": "PEN",

            "fa-IR": "IRR",
            "fi-FI": "EUR",

            "fr-BE": "EUR",
            "fr-CA": "CAD",
            "fr-CH": "CHF",
            "fr-FR": "EUR",

            "he-IL": "ILS",
            "hi-IN": "INR",
            "hu-HU": "HUF",

            "id-ID": "IDR",

            "it-CH": "CHF",
            "it-IT": "EUR",

            "ja-JP": "JPY",
            "ko-KR": "KRW",

            "ms-MY": "MYR",

            "nb-NO": "NOK",

            "nl-BE": "EUR",
            "nl-NL": "EUR",

            "pl-PL": "PLN",

            "pt-BR": "BRL",
            "pt-PT": "EUR",

            "ro-RO": "RON",
            "ru-RU": "RUB",

            "sk-SK": "EUR",
            "sv-SE": "SEK",
            "sw-KE": "KES",

            "th-TH": "THB",
            "tr-TR": "TRY",

            "uk-UA": "UAH",
            "ur-PK": "PKR",

            "vi-VN": "VND",

            "zh-CN": "CNY",
            "zh-HK": "HKD",
            "zh-SG": "SGD",
            "zh-TW": "TWD",

            /*
             * Bielorrusso também pode chegar
             * como locale simples "be".
             */
            "be": "BYN",
            "be-BY": "BYN"
        };


        if (
            LOCALE_TO_CURRENCY[
                normalized
            ]
        ) {

            return LOCALE_TO_CURRENCY[
                normalized
            ];

        }


        /*
         * Fallback para locale sem região.
         */
        const language =
            normalized
                .split("-")[0]
                .toLowerCase();


        const LANGUAGE_FALLBACK = {
            pt: "BRL",
            en: "USD",
            es: "EUR",
            fr: "EUR",
            de: "EUR",
            it: "EUR",
            ro: "RON",
            ru: "RUB",
            ar: "SAR",
            be: "BYN"
        };


        if (
            LANGUAGE_FALLBACK[
                language
            ]
        ) {

            return LANGUAGE_FALLBACK[
                language
            ];

        }


        /*
         * Mantém a lógica global existente
         * para qualquer outro locale.
         */
        const region =
            localeRegion(
                locale
            );


        if (
            region &&
            REGION_TO_CURRENCY[
                region
            ]
        ) {

            return REGION_TO_CURRENCY[
                region
            ];

        }


        return FALLBACK_CURRENCY;

    }


    function allCurrencies() {

        try {

            if (
                typeof Intl.supportedValuesOf
                === "function"
            ) {

                return Intl
                    .supportedValuesOf(
                        "currency"
                    )
                    .map(
                        code =>
                            code.toUpperCase()
                    );

            }

        }
        catch (_) {
        }


        /*
         * Fallback para navegadores antigos.
         */
        return `
        AED AFN ALL AMD AOA ARS AUD AWG AZN
        BAM BBD BDT BHD BIF BMD BND BOB BRL BSD BTN BWP BYN BZD
        CAD CDF CHF CLP CNY COP CRC CUP CVE CZK
        DJF DKK DOP DZD
        EGP ERN ETB EUR
        FJD FKP
        GBP GEL GHS GIP GMD GNF GTQ GYD
        HKD HNL HTG HUF
        IDR ILS INR IQD IRR ISK
        JMD JOD JPY
        KES KGS KHR KMF KPW KRW KWD KYD KZT
        LAK LBP LKR LRD LSL LYD
        MAD MDL MGA MKD MMK MNT MOP MRU MUR MVR MWK MXN MYR MZN
        NAD NGN NIO NOK NPR NZD
        OMR
        PAB PEN PGK PHP PKR PLN PYG
        QAR
        RON RSD RUB RWF
        SAR SBD SCR SDG SEK SGD SHP SLE SOS SRD SSP STN SYP SZL
        THB TJS TMT TND TOP TRY TTD TWD TZS
        UAH UGX USD UYU UZS
        VES VND VUV
        WST
        XAF XCD XCG XOF XPF
        YER
        ZAR ZMW ZWG
        `
            .trim()
            .split(/\s+/);

    }


    const CURRENCIES =
        Array.from(
            new Set(
                allCurrencies()
            )
        )
        .sort();


    function isCurrency(
        code
    ) {

        return CURRENCIES.includes(
            String(
                code ||
                ""
            )
            .toUpperCase()
        );

    }


    function manualCurrency() {

        const value =
            localStorage.getItem(
                STORAGE_MANUAL
            );


        if (
            value &&
            isCurrency(
                value
            )
        ) {

            return value.toUpperCase();

        }


        return null;

    }


    function currentCurrency() {

        /*
         * SABINO_LOCALE_MONEY_DISPLAY_V2
         *
         * A moeda exibida segue sempre
         * a localidade ativa.
         *
         * Localidade ativa:
         * 1. idioma escolhido na Sabino.AI
         * 2. caso contrário, navegador
         *
         * Não existe conversão cambial.
         * O valor numérico é preservado.
         */
        return automaticCurrency();

    }


    function currencySymbol(
        currency,
        locale = localeValue()
    ) {

        try {

            const parts =
                new Intl.NumberFormat(
                    locale,
                    {
                        style:
                            "currency",

                        currency:
                            currency,

                        currencyDisplay:
                            "narrowSymbol"
                    }
                )
                .formatToParts(
                    0
                );


            const currencyPart =
                parts.find(
                    part =>
                        part.type ===
                        "currency"
                );


            return (
                currencyPart?.value
                ||
                currency
            );

        }
        catch (_) {

            return currency;

        }

    }


    function currencyName(
        currency,
        locale = localeValue()
    ) {

        try {

            const display =
                new Intl.DisplayNames(
                    [locale],
                    {
                        type:
                            "currency"
                    }
                );


            return (
                display.of(
                    currency
                )
                ||
                currency
            );

        }
        catch (_) {

            return currency;

        }

    }


    function format(
        value,
        options = {}
    ) {

        const locale =
            options.locale
            ||
            localeValue();

        const currency =
            (
                options.currency
                ||
                currentCurrency()
            )
            .toUpperCase();


        let number =
            Number(value);


        if (
            !Number.isFinite(
                number
            )
        ) {

            number =
                0;

        }


        try {

            return new Intl.NumberFormat(
                locale,
                {
                    style:
                        "currency",

                    currency:
                        currency,

                    currencyDisplay:
                        options.currencyDisplay
                        ||
                        "narrowSymbol",

                    minimumFractionDigits:
                        options.minimumFractionDigits,

                    maximumFractionDigits:
                        options.maximumFractionDigits
                }
            )
            .format(
                number
            );

        }
        catch (_) {

            return (
                currency +
                " " +
                number.toFixed(2)
            );

        }

    }


    function dispatchChange(
        currency,
        source
    ) {

        window.dispatchEvent(
            new CustomEvent(
                "sabino:currency-change",
                {
                    detail: {

                        currency:
                            currency,

                        symbol:
                            currencySymbol(
                                currency
                            ),

                        locale:
                            localeValue(),

                        source:
                            source
                    }
                }
            )
        );

    }


    
    // ========================================================
    // SABINO_FX_FRONTEND_V1
    // Display-only FX conversion.
    // Valores persistidos nunca são modificados.
    // ========================================================

    const FX_CONVERT_ENDPOINT =
        "/api/finance/fx/convert";

    const FX_CLIENT_CACHE_TTL_MS =
        5 * 60 * 1000;

    const fxClientCache =
        new Map();

    let fxRenderVersion =
        0;


    async function convertMoney(
        value,
        sourceCurrency = "BRL",
        targetCurrency = currentCurrency()
    ) {

        const numeric =
            Number(value);

        if (
            !Number.isFinite(
                numeric
            )
        ) {

            throw new Error(
                "SABINO_FX_INVALID_VALUE"
            );
        }


        const source =
            String(
                sourceCurrency
                ||
                "BRL"
            )
            .toUpperCase();


        const target =
            String(
                targetCurrency
                ||
                currentCurrency()
            )
            .toUpperCase();


        if (
            source === target
        ) {

            return {
                original: {
                    amount:
                        String(numeric),
                    currency:
                        source
                },

                converted: {
                    amount:
                        String(numeric),
                    currency:
                        target
                },

                exchange: {
                    rate:
                        "1",
                    rate_date:
                        null,
                    provider:
                        "identity",
                    cached:
                        false
                }
            };

        }


        const cacheKey =
            source
            +
            "|"
            +
            target
            +
            "|"
            +
            String(numeric);


        const cached =
            fxClientCache.get(
                cacheKey
            );


        if (
            cached
            &&
            cached.expiresAt
            >
            Date.now()
        ) {

            return cached.payload;

        }


        const params =
            new URLSearchParams(
                {
                    amount:
                        String(numeric),

                    from_currency:
                        source,

                    to_currency:
                        target
                }
            );


        const response =
            await fetch(
                FX_CONVERT_ENDPOINT
                +
                "?"
                +
                params.toString(),
                {
                    method:
                        "GET",

                    headers: {
                        Accept:
                            "application/json"
                    },

                    credentials:
                        "same-origin"
                }
            );


        if (
            !response.ok
        ) {

            throw new Error(
                "SABINO_FX_HTTP_"
                +
                response.status
            );
        }


        const payload =
            await response.json();


        if (
            !payload
            ||
            !payload.converted
            ||
            !payload.converted.currency
        ) {

            throw new Error(
                "SABINO_FX_INVALID_RESPONSE"
            );
        }


        if (
            String(
                payload
                    .converted
                    .currency
            )
            .toUpperCase()
            !==
            target
        ) {

            throw new Error(
                "SABINO_FX_CURRENCY_MISMATCH"
            );
        }


        fxClientCache.set(
            cacheKey,
            {
                expiresAt:
                    Date.now()
                    +
                    FX_CLIENT_CACHE_TTL_MS,

                payload:
                    payload
            }
        );


        return payload;

    }


    function formatAnnotatedMoney() {

        {
            /*
             * SABINO_LOCALE_MONEY_DISPLAY_ANNOTATED_V2
             *
             * IMPORTANTE:
             * 4250 continua sendo 4250.
             *
             * pt-BR -> R$ 4.250,00
             * en-US -> $4,250.00
             * en-GB -> £4,250.00
             * es-ES -> 4.250,00 €
             *
             * Nenhuma taxa de câmbio é aplicada.
             */

            const localeCurrency =
                automaticCurrency();

            const elements =
                Array.from(
                    document.querySelectorAll(
                        "[data-sabino-money]"
                    )
                );


            elements.forEach(
                function (element) {

                    const raw =
                        element.getAttribute(
                            "data-sabino-money"
                        );

                    const value =
                        Number(raw);


                    if (
                        !Number.isFinite(
                            value
                        )
                    ) {
                        return;
                    }


                    const explicitStatic =
                        element.getAttribute(
                            "data-sabino-fx-static-v1"
                        )
                        ===
                        "1";


                    /*
                     * Cards dinâmicos muitas vezes
                     * começam com data-sabino-money="0"
                     * e depois recebem um valor da API.
                     *
                     * Não sobrescrevemos esse valor aqui.
                     * Esses writers serão migrados na
                     * próxima etapa.
                     */
                    if (
                        value === 0
                        &&
                        !explicitStatic
                    ) {

                        const currentText =
                            String(
                                element.textContent
                                ||
                                ""
                            );


                        if (
                            /[1-9]/.test(
                                currentText
                            )
                        ) {

                            element.setAttribute(
                                "data-sabino-money-status",
                                "dynamic-writer-pending"
                            );

                            return;
                        }
                    }


                    element.textContent =
                        format(
                            value,
                            {
                                currency:
                                    localeCurrency
                            }
                        );


                    element.setAttribute(
                        "data-sabino-display-currency",
                        localeCurrency
                    );


                    element.setAttribute(
                        "data-sabino-money-status",
                        "localized"
                    );


                    /*
                     * Remove metadados antigos de FX,
                     * porque não há mais cotação.
                     */
                    element.removeAttribute(
                        "data-sabino-fx-rate"
                    );

                    element.removeAttribute(
                        "data-sabino-fx-rate-date"
                    );

                    element.removeAttribute(
                        "data-sabino-fx-status"
                    );

                }
            );


            window.dispatchEvent(
                new CustomEvent(
                    "sabino:money-localized",
                    {
                        detail: {
                            currency:
                                localeCurrency,

                            count:
                                elements.length
                        }
                    }
                )
            );


            return Promise.resolve(
                elements
            );
        }


        /* SABINO_FX_FRONTEND_V1 */

        const renderVersion =
            ++fxRenderVersion;

        const targetCurrency =
            currentCurrency();

        const elements =
            Array.from(
                document.querySelectorAll(
                    "[data-sabino-money]"
                )
            );


        return Promise.all(
            elements.map(
                async function (element) {

                    const raw =
                        element.getAttribute(
                            "data-sabino-money"
                        );

                    const value =
                        Number(raw);


                    if (
                        !Number.isFinite(value)
                    ) {
                        return;
                    }


                    const sourceCurrency =
                        String(
                            element.getAttribute(
                                "data-sabino-source-currency"
                            )
                            ||
                            "BRL"
                        )
                        .toUpperCase();


                    const explicitStatic =
                        element.getAttribute(
                            "data-sabino-fx-static-v1"
                        )
                        ===
                        "1";


                    /*
                     * Muitos cards começam em zero
                     * e depois são atualizados pelas APIs
                     * específicas da página.
                     *
                     * Se o valor original do atributo é zero,
                     * mas o texto atual contém um valor não-zero,
                     * NÃO sobrescrevemos o dado dinâmico.
                     */
                    if (
                        value === 0
                        &&
                        !explicitStatic
                    ) {

                        const currentText =
                            String(
                                element.textContent
                                ||
                                ""
                            );

                        if (
                            /[1-9]/.test(
                                currentText
                            )
                        ) {

                            element.setAttribute(
                                "data-sabino-fx-status",
                                "dynamic-skip"
                            );

                            return;
                        }


                        if (
                            renderVersion
                            !==
                            fxRenderVersion
                        ) {
                            return;
                        }


                        element.textContent =
                            format(
                                0,
                                {
                                    currency:
                                        targetCurrency
                                }
                            );

                        element.setAttribute(
                            "data-sabino-display-currency",
                            targetCurrency
                        );

                        element.setAttribute(
                            "data-sabino-fx-status",
                            "zero"
                        );

                        return;
                    }


                    if (
                        sourceCurrency
                        ===
                        targetCurrency
                    ) {

                        if (
                            renderVersion
                            !==
                            fxRenderVersion
                        ) {
                            return;
                        }

                        element.textContent =
                            format(
                                value,
                                {
                                    currency:
                                        sourceCurrency
                                }
                            );

                        element.setAttribute(
                            "data-sabino-display-currency",
                            sourceCurrency
                        );

                        element.setAttribute(
                            "data-sabino-fx-status",
                            "identity"
                        );

                        return;
                    }


                    try {

                        const result =
                            await convertMoney(
                                value,
                                sourceCurrency,
                                targetCurrency
                            );


                        if (
                            renderVersion
                            !==
                            fxRenderVersion
                        ) {
                            return;
                        }


                        const converted =
                            Number(
                                result
                                    .converted
                                    .amount
                            );


                        if (
                            !Number.isFinite(
                                converted
                            )
                        ) {
                            throw new Error(
                                "SABINO_FX_INVALID_AMOUNT"
                            );
                        }


                        element.textContent =
                            format(
                                converted,
                                {
                                    currency:
                                        targetCurrency
                                }
                            );


                        element.setAttribute(
                            "data-sabino-display-currency",
                            targetCurrency
                        );

                        element.setAttribute(
                            "data-sabino-source-currency",
                            sourceCurrency
                        );

                        element.setAttribute(
                            "data-sabino-fx-status",
                            "converted"
                        );


                        if (
                            result.exchange
                            &&
                            result.exchange.rate
                        ) {

                            element.setAttribute(
                                "data-sabino-fx-rate",
                                String(
                                    result.exchange.rate
                                )
                            );
                        }


                        if (
                            result.exchange
                            &&
                            result.exchange.rate_date
                        ) {

                            element.setAttribute(
                                "data-sabino-fx-date",
                                String(
                                    result.exchange.rate_date
                                )
                            );
                        }

                    }
                    catch (error) {

                        if (
                            renderVersion
                            !==
                            fxRenderVersion
                        ) {
                            return;
                        }


                        /*
                         * Falhou a cotação:
                         * mostramos a moeda ORIGINAL.
                         * Nunca apenas trocamos o símbolo.
                         */
                        element.textContent =
                            format(
                                value,
                                {
                                    currency:
                                        sourceCurrency
                                }
                            );

                        element.setAttribute(
                            "data-sabino-display-currency",
                            sourceCurrency
                        );

                        element.setAttribute(
                            "data-sabino-fx-status",
                            "error"
                        );


                        console.warn(
                            "SABINO_FX_CONVERSION_FAILED",
                            sourceCurrency,
                            targetCurrency,
                            value,
                            error
                        );

                    }

                }
            )
        ).then(
            function () {

                if (
                    renderVersion
                    !==
                    fxRenderVersion
                ) {
                    return;
                }


                window.dispatchEvent(
                    new CustomEvent(
                        "sabino:fx-rendered",
                        {
                            detail: {
                                currency:
                                    targetCurrency
                            }
                        }
                    )
                );

            }
        );

    }


    function updateButton() {

        const button =
            document.getElementById(
                "sabinoGlobalCurrencyButton"
            );


        if (!button) {
            return;
        }


        const currency =
            currentCurrency();

        const symbol =
            currencySymbol(
                currency
            );


        button.textContent =
            "💱 "
            +
            currency
            +
            " "
            +
            symbol
            +
            " ▾";

    }


    function updateAutomaticButton() {

        const button =
            document.getElementById(
                "sabinoGlobalCurrencyAuto"
            );


        if (!button) {
            return;
        }


        const automatic =
            automaticCurrency();

        const locale =
            localeValue();


        button.textContent =
            (
                manualCurrency()
                    ? "Usar moeda automática: "
                    : "✓ Moeda automática: "
            )
            +
            currencyName(
                automatic,
                locale
            )
            +
            " ("
            +
            automatic
            +
            " / "
            +
            currencySymbol(
                automatic,
                locale
            )
            +
            ")";

    }


    function applyCurrency(
        currency,
        options = {}
    ) {

        const normalized =
            String(
                currency ||
                FALLBACK_CURRENCY
            )
            .toUpperCase();


        if (
            !isCurrency(
                normalized
            )
        ) {

            console.warn(
                "SABINO_CURRENCY_INVALID",
                normalized
            );

            return currentCurrency();

        }


        const source =
            options.source
            ||
            "runtime";


        localStorage.setItem(
            STORAGE_CURRENT,
            normalized
        );

        localStorage.setItem(
            STORAGE_SOURCE,
            source
        );


        if (
            options.manual === true
        ) {

            localStorage.setItem(
                STORAGE_MANUAL,
                normalized
            );

        }


        updateButton();
        updateAutomaticButton();

        void formatAnnotatedMoney();


        dispatchChange(
            normalized,
            source
        );


        console.log(
            "SABINO_GLOBAL_CURRENCY",
            normalized,
            currencySymbol(
                normalized
            ),
            source
        );


        return normalized;

    }


    function clearManualCurrency() {

        localStorage.removeItem(
            STORAGE_MANUAL
        );


        return applyCurrency(
            automaticCurrency(),
            {
                source:
                    "locale",
                manual:
                    false
            }
        );

    }


    function renderCurrencyList(
        query = ""
    ) {

        const list =
            document.getElementById(
                "sabinoGlobalCurrencyList"
            );


        if (!list) {
            return;
        }


        const locale =
            localeValue();

        const active =
            currentCurrency();

        const search =
            String(
                query ||
                ""
            )
            .trim()
            .toLocaleLowerCase();


        list.innerHTML =
            "";


        for (
            const currency
            of CURRENCIES
        ) {

            const symbol =
                currencySymbol(
                    currency,
                    locale
                );

            const name =
                currencyName(
                    currency,
                    locale
                );


            const haystack =
                (
                    currency
                    +
                    " "
                    +
                    symbol
                    +
                    " "
                    +
                    name
                )
                .toLocaleLowerCase();


            if (
                search &&
                !haystack.includes(
                    search
                )
            ) {

                continue;

            }


            const option =
                document.createElement(
                    "button"
                );

            option.type =
                "button";

            option.className =
                "sabino-global-currency-option";

            option.dataset.currency =
                currency;


            if (
                currency ===
                active
            ) {

                option.classList.add(
                    "active"
                );

            }


            const check =
                document.createElement(
                    "span"
                );

            check.className =
                "sabino-currency-check";

            check.textContent =
                currency === active
                    ? "✓"
                    : "";


            const copy =
                document.createElement(
                    "span"
                );

            copy.className =
                "sabino-currency-copy";


            const title =
                document.createElement(
                    "strong"
                );

            title.textContent =
                name;


            const meta =
                document.createElement(
                    "small"
                );

            meta.textContent =
                currency
                +
                " · "
                +
                symbol;


            copy.appendChild(
                title
            );

            copy.appendChild(
                meta
            );


            option.appendChild(
                check
            );

            option.appendChild(
                copy
            );


            option.addEventListener(
                "click",
                function () {

                    applyCurrency(
                        currency,
                        {
                            source:
                                "manual",

                            manual:
                                true
                        }
                    );


                    const panel =
                        document.getElementById(
                            "sabinoGlobalCurrencyPanel"
                        );


                    if (panel) {

                        panel.hidden =
                            true;

                    }


                    const selectorButton =
                        document.getElementById(
                            "sabinoGlobalCurrencyButton"
                        );


                    if (selectorButton) {

                        selectorButton
                            .setAttribute(
                                "aria-expanded",
                                "false"
                            );

                    }

                }
            );


            list.appendChild(
                option
            );

        }

    }


    function createSelector() {

        if (
            document.getElementById(
                "sabinoGlobalCurrency"
            )
        ) {

            return;

        }


        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.id =
            "sabinoGlobalCurrency";

        wrapper.className =
            "sabino-global-currency";


        const button =
            document.createElement(
                "button"
            );

        button.id =
            "sabinoGlobalCurrencyButton";

        button.className =
            "sabino-global-currency-button";

        button.type =
            "button";

        button.setAttribute(
            "aria-haspopup",
            "dialog"
        );

        button.setAttribute(
            "aria-expanded",
            "false"
        );


        const panel =
            document.createElement(
                "div"
            );

        panel.id =
            "sabinoGlobalCurrencyPanel";

        panel.className =
            "sabino-global-currency-panel";

        panel.hidden =
            true;


        const title =
            document.createElement(
                "div"
            );

        title.className =
            "sabino-global-currency-heading";

        title.textContent =
            "MOEDA / CURRENCY";


        const automatic =
            document.createElement(
                "button"
            );

        automatic.id =
            "sabinoGlobalCurrencyAuto";

        automatic.type =
            "button";

        automatic.className =
            "sabino-global-currency-auto";


        const search =
            document.createElement(
                "input"
            );

        search.id =
            "sabinoGlobalCurrencySearch";

        search.type =
            "search";

        search.className =
            "sabino-global-currency-search";

        search.placeholder =
            "Pesquisar moeda / Search currency";

        search.autocomplete =
            "off";


        const list =
            document.createElement(
                "div"
            );

        list.id =
            "sabinoGlobalCurrencyList";

        list.className =
            "sabino-global-currency-list";


        panel.appendChild(
            title
        );

        panel.appendChild(
            automatic
        );

        panel.appendChild(
            search
        );

        panel.appendChild(
            list
        );


        wrapper.appendChild(
            button
        );

        wrapper.appendChild(
            panel
        );


        document.body.appendChild(
            wrapper
        );


        button.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();


                const open =
                    panel.hidden;


                panel.hidden =
                    !open;


                button.setAttribute(
                    "aria-expanded",
                    String(open)
                );


                if (open) {

                    renderCurrencyList(
                        search.value
                    );


                    setTimeout(
                        function () {

                            search.focus();

                        },
                        0
                    );

                }

            }
        );


        automatic.addEventListener(
            "click",
            function () {

                clearManualCurrency();

                panel.hidden =
                    true;

                button.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }
        );


        search.addEventListener(
            "input",
            function () {

                renderCurrencyList(
                    search.value
                );

            }
        );


        document.addEventListener(
            "click",
            function (event) {

                if (
                    !wrapper.contains(
                        event.target
                    )
                ) {

                    panel.hidden =
                        true;

                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }
        );


        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                    "Escape"
                ) {

                    panel.hidden =
                        true;

                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }
        );


        updateButton();
        updateAutomaticButton();

    }


    /*
     * Se o idioma/região mudar:
     *
     * sem moeda manual -> troca moeda automaticamente.
     * com moeda manual -> mantém escolha do usuário.
     */
    window.addEventListener(
        "sabino:locale-change",
        function () {

            if (
                manualCurrency()
            ) {

                updateButton();
                updateAutomaticButton();

                formatAnnotatedMoney();

                return;

            }


            applyCurrency(
                automaticCurrency(),
                {
                    source:
                        "locale",
                    manual:
                        false
                }
            );

        }
    );


    window.addEventListener(
        "storage",
        function (event) {

            if (
                event.key ===
                STORAGE_MANUAL ||
                event.key ===
                STORAGE_CURRENT ||
                event.key ===
                "sabino_language"
            ) {

                updateButton();
                updateAutomaticButton();

            }

        }
    );


    window.SabinoCurrency = {

        all:
            CURRENCIES.slice(),

        current:
            currentCurrency,

        automatic:
            automaticCurrency,

        manual:
            manualCurrency,

        symbol:
            currencySymbol,

        name:
            currencyName,

        format:
            format,

        convert:
            convertMoney,

        refresh:
            formatAnnotatedMoney,

        apply:
            function (
                currency
            ) {

                return applyCurrency(
                    currency,
                    {
                        source:
                            "manual",
                        manual:
                            true
                    }
                );

            },

        useAutomatic:
            clearManualCurrency,

        region:
            function () {

                return localeRegion(
                    localeValue()
                );

            }

    };


    function start() {

        createSelector();


        const manual =
            manualCurrency();


        applyCurrency(
            manual
            ||
            automaticCurrency(),
            {
                source:
                    manual
                        ? "manual"
                        : "locale",

                manual:
                    Boolean(
                        manual
                    )
            }
        );


        console.log(
            "SABINO_GLOBAL_CURRENCY_CORE=READY"
        );


        console.log(
            "SABINO_CURRENCY_COUNT="
            +
            CURRENCIES.length
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
                once:
                    true
            }
        );

    }
    else {

        start();

    }

})();
