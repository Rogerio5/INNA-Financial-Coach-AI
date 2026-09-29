(() => {

    "use strict";

    // SABINO_MONEY_LOCALE_RUNTIME_V1

    if (window.SabinoMoneyLocaleRuntime) {
        return;
    }


    const tracked =
        new Set();

    const lastRendered =
        new WeakMap();

    const SOURCE_VALUE =
        "data-sabino-locale-money-value";

    const SOURCE_CURRENCY =
        "data-sabino-locale-money-source";

    const DISPLAY_STATUS =
        "data-sabino-locale-money-status";

    const COMPACT =
        "data-sabino-locale-money-compact";


    function locale() {

        /*
         * SABINO_MONEY_SHARED_LOCALE_V2
         *
         * A moeda e a formatação devem usar
         * exatamente o mesmo locale global.
         */
        try {

            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current
                    === "function"
            ) {

                const sharedLocale =
                    window.SabinoLocale.current();

                if (sharedLocale) {
                    return sharedLocale;
                }

            }

        }
        catch (_) {
        }


        return (
            localStorage.getItem(
                "sabino_language"
            )
            ||
            document.documentElement.lang
            ||
            navigator.language
            ||
            "pt-BR"
        );

    }


    function moneyApi() {

        return (
            window.SabinoCurrency
            ||
            null
        );

    }


    function normalizeNumber(
        raw
    ) {

        let text =
            String(
                raw
                ||
                ""
            )
            .replace(
                /[\s\u00A0\u202F]/g,
                ""
            )
            .trim();


        if (!text) {
            return null;
        }


        let sign = 1;


        if (text.startsWith("-")) {

            sign = -1;

            text =
                text.slice(1);

        }
        else if (
            text.startsWith("+")
        ) {

            text =
                text.slice(1);
        }


        if (
            !/^\d[\d.,]*$/.test(
                text
            )
        ) {

            return null;
        }


        const comma =
            text.lastIndexOf(",");

        const dot =
            text.lastIndexOf(".");


        let normalized =
            text;


        if (
            comma >= 0
            &&
            dot >= 0
        ) {

            /*
             * O último separador é tratado
             * como decimal.
             */
            if (comma > dot) {

                normalized =
                    text
                    .replace(
                        /\./g,
                        ""
                    )
                    .replace(
                        ",",
                        "."
                    );

            }
            else {

                normalized =
                    text.replace(
                        /,/g,
                        ""
                    );

            }

        }
        else if (
            comma >= 0
        ) {

            const decimals =
                text.length
                -
                comma
                -
                1;


            if (
                decimals === 1
                ||
                decimals === 2
            ) {

                normalized =
                    text
                    .replace(
                        /\./g,
                        ""
                    )
                    .replace(
                        ",",
                        "."
                    );

            }
            else {

                normalized =
                    text.replace(
                        /,/g,
                        ""
                    );
            }

        }
        else if (
            dot >= 0
        ) {

            const decimals =
                text.length
                -
                dot
                -
                1;


            if (
                decimals === 3
            ) {

                normalized =
                    text.replace(
                        /\./g,
                        ""
                    );
            }

        }


        const number =
            Number(
                normalized
            );


        if (
            !Number.isFinite(
                number
            )
        ) {

            return null;
        }


        return (
            number
            *
            sign
        );

    }


    function parseBRL(
        rawText
    ) {

        let text =
            String(
                rawText
                ||
                ""
            )
            .replace(
                /\u00A0/g,
                " "
            )
            .replace(
                /\u202F/g,
                " "
            )
            .trim();


        if (!text) {
            return null;
        }


        let compact = false;


        if (
            /\s+mil$/i.test(
                text
            )
        ) {

            compact = true;

            text =
                text.replace(
                    /\s+mil$/i,
                    ""
                )
                .trim();
        }


        /*
         * Aceita moeda BRL antes OU depois
         * do valor.
         *
         * R$ 4.250,00
         * R$4,250.00
         * 4.250,00 R$
         * 4 250,00 BRL
         */
        let match =
            text.match(
                /^([+-]?)\s*(?:R\$|BRL)\s*([+-]?)\s*([\d\s.,]+)$/i
            );


        let signA = "";
        let signB = "";
        let numberText = "";


        if (match) {

            signA =
                match[1]
                ||
                "";

            signB =
                match[2]
                ||
                "";

            numberText =
                match[3];

        }
        else {

            match =
                text.match(
                    /^([+-]?)\s*([\d\s.,]+)\s*(?:R\$|BRL)$/i
                );


            if (!match) {
                return null;
            }


            signA =
                match[1]
                ||
                "";

            numberText =
                match[2];
        }


        const sign =
            (
                signA === "-"
                ||
                signB === "-"
            )
            ?
            "-"
            :
            "";


        let value =
            normalizeNumber(
                sign
                +
                numberText
            );


        if (value === null) {
            return null;
        }


        if (compact) {

            value =
                value
                *
                1000;
        }


        return {
            value:
                value,

            compact:
                compact
        };

    }


    function currentCurrency() {

        const api =
            moneyApi();


        if (
            api
            &&
            typeof api.current
                ===
                "function"
        ) {

            try {

                return String(
                    api.current()
                    ||
                    "BRL"
                )
                .toUpperCase();

            }
            catch (_) {
                // segue fallback
            }
        }


        /*
         * Apenas fallback.
         * Normalmente SabinoCurrency.current()
         * estará disponível.
         */
        const activeLocale =
            locale()
            .replace(
                "_",
                "-"
            );


        const region =
            (
                activeLocale
                .split("-")[1]
                ||
                ""
            )
            .toUpperCase();


        const map = {
            BR: "BRL",
            US: "USD",
            GB: "GBP",
            UK: "GBP",
            PT: "EUR",
            ES: "EUR",
            FR: "EUR",
            DE: "EUR",
            IT: "EUR",
            RO: "RON",
            RU: "RUB",
            BY: "BYN"
        };


        return (
            map[region]
            ||
            "BRL"
        );

    }


    function formatValue(
        value,
        compact = false
    ) {

        const api =
            moneyApi();


        if (
            !compact
            &&
            api
            &&
            typeof api.format
                ===
                "function"
        ) {

            /*
             * Sem passar currency.
             * O currency core usa a moeda
             * derivada da localidade ativa.
             */
            return api.format(
                value
            );

        }


        const currency =
            currentCurrency();


        return new Intl.NumberFormat(
            locale(),
            {
                style:
                    "currency",

                currency:
                    currency,

                notation:
                    compact
                    ?
                    "compact"
                    :
                    "standard",

                compactDisplay:
                    "short",

                maximumFractionDigits:
                    compact
                    ?
                    1
                    :
                    undefined
            }
        ).format(
            Number(
                value
            )
        );

    }


    function eligible(
        element
    ) {

        if (
            !element
            ||
            element.nodeType !== 1
        ) {

            return false;
        }


        if (
            [
                "SCRIPT",
                "STYLE",
                "INPUT",
                "TEXTAREA",
                "SELECT",
                "OPTION",
                "NOSCRIPT"
            ].includes(
                element.tagName
            )
        ) {

            return false;
        }


        /*
         * Os valores estáticos marcados
         * explicitamente já são tratados
         * pelo currency core V2.
         */
        if (
            element.getAttribute(
                "data-sabino-fx-static-v1"
            )
            ===
            "1"
        ) {

            return false;
        }


        /*
         * Apenas elementos folha.
         * Evita alterar frases inteiras.
         */
        if (
            element.children.length > 0
        ) {

            return false;
        }


        return true;

    }


    function write(
        element,
        value
    ) {

        const text =
            String(
                value
            );


        lastRendered.set(
            element,
            text
        );


        if (
            element.textContent
            !==
            text
        ) {

            element.textContent =
                text;
        }

    }


    function render(
        element
    ) {

        if (
            !document.documentElement.contains(
                element
            )
        ) {

            tracked.delete(
                element
            );

            return;
        }


        const raw =
            element.getAttribute(
                SOURCE_VALUE
            );


        const value =
            Number(
                raw
            );


        if (
            !Number.isFinite(
                value
            )
        ) {

            tracked.delete(
                element
            );

            return;
        }


        const compact =
            element.getAttribute(
                COMPACT
            )
            ===
            "1";


        write(
            element,
            formatValue(
                value,
                compact
            )
        );


        element.setAttribute(
            SOURCE_CURRENCY,
            "BRL"
        );


        element.setAttribute(
            DISPLAY_STATUS,
            "localized"
        );

    }


    function inspect(
        element
    ) {

        if (
            !eligible(
                element
            )
        ) {

            return;
        }


        const text =
            String(
                element.textContent
                ||
                ""
            )
            .trim();


        if (!text) {
            return;
        }


        /*
         * Ignora alteração feita pelo
         * próprio runtime.
         */
        if (
            lastRendered.get(
                element
            )
            ===
            text
        ) {

            return;
        }


        const parsed =
            parseBRL(
                text
            );


        if (!parsed) {

            /*
             * Se a própria página substituir
             * o dinheiro por outro conteúdo,
             * paramos de controlar o elemento.
             */
            if (
                tracked.has(
                    element
                )
            ) {

                tracked.delete(
                    element
                );

                element.removeAttribute(
                    SOURCE_VALUE
                );

                element.removeAttribute(
                    SOURCE_CURRENCY
                );

                element.removeAttribute(
                    DISPLAY_STATUS
                );

                element.removeAttribute(
                    COMPACT
                );

                lastRendered.delete(
                    element
                );
            }


            return;
        }


        element.setAttribute(
            SOURCE_VALUE,
            String(
                parsed.value
            )
        );


        element.setAttribute(
            SOURCE_CURRENCY,
            "BRL"
        );


        if (
            parsed.compact
        ) {

            element.setAttribute(
                COMPACT,
                "1"
            );

        }
        else {

            element.removeAttribute(
                COMPACT
            );
        }


        tracked.add(
            element
        );


        render(
            element
        );

    }


    function scan(
        root = document.body
    ) {

        if (!root) {
            return;
        }


        if (
            root.nodeType === 3
        ) {

            inspect(
                root.parentElement
            );

            return;
        }


        if (
            root.nodeType !== 1
        ) {

            return;
        }


        inspect(
            root
        );


        root
            .querySelectorAll(
                "span,strong,b,small,div,p,td,th,label"
            )
            .forEach(
                inspect
            );

    }


    function refresh() {

        Array
            .from(
                tracked
            )
            .forEach(
                render
            );

    }


    let queued =
        false;

    const pending =
        new Set();


    function queueScan(
        node
    ) {

        if (!node) {
            return;
        }


        pending.add(
            node
        );


        if (queued) {
            return;
        }


        queued =
            true;


        queueMicrotask(
            function () {

                queued =
                    false;


                const nodes =
                    Array.from(
                        pending
                    );


                pending.clear();


                nodes.forEach(
                    scan
                );

            }
        );

    }


    function start() {

        scan();


        const observer =
            new MutationObserver(
                function (
                    mutations
                ) {

                    mutations.forEach(
                        function (
                            mutation
                        ) {

                            if (
                                mutation.type
                                ===
                                "characterData"
                            ) {

                                queueScan(
                                    mutation
                                        .target
                                        .parentElement
                                );

                            }
                            else if (
                                mutation.type
                                ===
                                "childList"
                            ) {

                                queueScan(
                                    mutation.target
                                );


                                mutation
                                    .addedNodes
                                    .forEach(
                                        queueScan
                                    );
                            }

                        }
                    );

                }
            );


        observer.observe(
            document.body,
            {
                subtree:
                    true,

                childList:
                    true,

                characterData:
                    true
            }
        );


        /*
         * Idioma escolhido na plataforma.
         */
        window.addEventListener(
            "sabino:locale-change",
            function () {

                queueMicrotask(
                    refresh
                );
            }
        );


        /*
         * Currency core atualiza a moeda
         * depois da alteração de locale.
         */
        window.addEventListener(
            "sabino:currency-change",
            function () {

                queueMicrotask(
                    refresh
                );
            }
        );


        window.addEventListener(
            "sabino:money-localized",
            function () {

                queueMicrotask(
                    refresh
                );
            }
        );


        /*
         * Mudança de preferência em outra aba.
         */
        window.addEventListener(
            "storage",
            function (
                event
            ) {

                if (
                    event.key
                    ===
                    "sabino_language"
                    ||
                    event.key
                    ===
                    "sabino_language_manual"
                    ||
                    event.key
                    ===
                    "sabino_language_source"
                ) {

                    queueMicrotask(
                        refresh
                    );
                }

            }
        );


        window
            .SabinoMoneyLocaleRuntime
            .observer =
                observer;


        console.log(
            "SABINO_MONEY_LOCALE_RUNTIME_V1_READY"
        );

    }


    window.SabinoMoneyLocaleRuntime = {

        version:
            "1.0.0",

        scan:
            scan,

        refresh:
            refresh,

        parseBRL:
            parseBRL,

        trackedCount:
            function () {

                return tracked.size;
            },

        status:
            function () {

                return {
                    version:
                        "1.0.0",

                    locale:
                        locale(),

                    currency:
                        currentCurrency(),

                    tracked:
                        tracked.size
                };
            },

        observer:
            null
    };


    if (
        document.readyState
        ===
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