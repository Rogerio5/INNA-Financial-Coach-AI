(function () {
    "use strict";

    if (window.__SABINO_MODULOS_I18N_V1__) {
        return;
    }

    window.__SABINO_MODULOS_I18N_V1__ = true;

    const catalogCache = new Map();
    const originals = new WeakMap();

    function currentLocale() {
        try {
            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current === "function"
            ) {
                return (
                    window.SabinoLocale.current() ||
                    "pt-BR"
                );
            }
        }
        catch (_) {}

        return (
            localStorage.getItem("sabino_locale") ||
            localStorage.getItem("sabino_language") ||
            navigator.language ||
            "pt-BR"
        );
    }

    function normalizeLocale(value) {
        return String(value || "pt-BR")
            .replace("_", "-");
    }

    async function loadCatalog(locale) {
        locale = normalizeLocale(locale);

        /*
         * pt-BR é o texto fonte da página.
         */
        if (
            locale.toLowerCase() === "pt-br" ||
            locale.toLowerCase() === "pt"
        ) {
            return {};
        }

        if (catalogCache.has(locale)) {
            return catalogCache.get(locale);
        }

        try {
            const response = await fetch(
                "/static/i18n/" +
                encodeURIComponent(locale) +
                ".json",
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "force-cache"
                }
            );

            if (!response.ok) {
                console.warn(
                    "SABINO_MODULOS_I18N_CATALOG_HTTP",
                    locale,
                    response.status
                );

                catalogCache.set(locale, {});
                return {};
            }

            const catalog = await response.json();

            catalogCache.set(
                locale,
                catalog && typeof catalog === "object"
                    ? catalog
                    : {}
            );

            return catalogCache.get(locale);
        }
        catch (error) {
            console.warn(
                "SABINO_MODULOS_I18N_CATALOG_ERROR",
                locale,
                error
            );

            catalogCache.set(locale, {});
            return {};
        }
    }

    function shouldSkip(node) {
        if (!node || !node.parentElement) {
            return true;
        }

        const tag =
            node.parentElement.tagName;

        return (
            tag === "SCRIPT" ||
            tag === "STYLE" ||
            tag === "NOSCRIPT" ||
            tag === "TEXTAREA" ||
            tag === "CODE" ||
            tag === "PRE"
        );
    }

    /*
     * SABINO_MODULOS_NORMALIZED_MATCH_V1
     *
     * Permite que textos do HTML com:
     * - quebra de linha
     * - múltiplos espaços
     * - tabulação
     *
     * encontrem a mesma chave existente no catálogo.
     */
    function normalizeTranslationKey(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim();
    }

    function createTranslationLookup(catalog) {
        const lookup = new Map();

        if (
            !catalog ||
            typeof catalog !== "object"
        ) {
            return lookup;
        }

        Object.keys(catalog).forEach(
            function (key) {

                const normalized =
                    normalizeTranslationKey(key);

                if (normalized) {
                    lookup.set(
                        normalized,
                        catalog[key]
                    );
                }

            }
        );

        return lookup;
    }

    function translateTextNodes(catalog) {
        const lookup =
            createTranslationLookup(catalog);

        const walker =
            document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT
            );

        let translated = 0;
        let node;

        while (
            (node = walker.nextNode())
        ) {
            if (shouldSkip(node)) {
                continue;
            }

            if (!originals.has(node)) {
                originals.set(
                    node,
                    node.nodeValue
                );
            }

            const original =
                originals.get(node);

            const key =
                String(original || "").trim();

            if (!key) {
                continue;
            }

            const prefix =
                String(original).match(/^\s*/)?.[0] || "";

            const suffix =
                String(original).match(/\s*$/)?.[0] || "";

                        const normalizedKey =
                normalizeTranslationKey(key);

            if (
                lookup.has(normalizedKey)
            ) {
                node.nodeValue =
                    prefix +
                    String(
                        lookup.get(
                            normalizedKey
                        )
                    ) +
                    suffix;

                translated++;
            }
            else {
                node.nodeValue =
                    original;
            }
        }

        return translated;
    }

    function translateAttributes(catalog) {
        const attributes = [
            "title",
            "aria-label",
            "placeholder"
        ];

        let translated = 0;

        document
            .querySelectorAll("*")
            .forEach(function (element) {

                attributes.forEach(
                    function (attribute) {

                        if (
                            !element.hasAttribute(attribute)
                        ) {
                            return;
                        }

                        const sourceKey =
                            "sabinoI18nOriginal" +
                            attribute
                                .replace(
                                    /[^a-z0-9]/gi,
                                    ""
                                );

                        if (
                            !element.dataset[sourceKey]
                        ) {
                            element.dataset[sourceKey] =
                                element.getAttribute(
                                    attribute
                                );
                        }

                        const original =
                            element.dataset[sourceKey];

                        if (
                            Object.prototype
                                .hasOwnProperty
                                .call(
                                    catalog,
                                    original
                                )
                        ) {
                            element.setAttribute(
                                attribute,
                                catalog[original]
                            );

                            translated++;
                        }
                        else {
                            element.setAttribute(
                                attribute,
                                original
                            );
                        }

                    }
                );

            });

        return translated;
    }

    async function apply(locale) {
        locale =
            normalizeLocale(
                locale ||
                currentLocale()
            );

        const catalog =
            await loadCatalog(locale);

        /*
         * SABINO_MODULOS_NESTED_CATALOG_V1
         *
         * Os arquivos /static/i18n/*.json possuem metadados
         * no nível raiz e o dicionário real dentro de:
         *
         * catalog.translations
         *
         * Também mantemos compatibilidade com catálogo plano.
         */
        const dictionary =
            catalog &&
            catalog.translations &&
            typeof catalog.translations === "object"
                ? catalog.translations
                : catalog;

        const textCount =
            translateTextNodes(dictionary);

        const attributeCount =
            translateAttributes(dictionary);

        const titleOriginal =
            document.documentElement
                .dataset
                .sabinoModulosOriginalTitle
            ||
            document.title;

        if (
            !document.documentElement
                .dataset
                .sabinoModulosOriginalTitle
        ) {
            document.documentElement
                .dataset
                .sabinoModulosOriginalTitle =
                document.title;
        }

        if (
            Object.prototype
                .hasOwnProperty
                .call(
                    dictionary,
                    titleOriginal
                )
        ) {
            document.title =
                dictionary[titleOriginal];
        }
        else {
            document.title =
                titleOriginal;
        }

        console.log(
            "SABINO_MODULOS_I18N=READY",
            locale,
            "TEXT=" + textCount,
            "ATTR=" + attributeCount
        );
    }

    function start() {
        void apply(currentLocale());

        /*
         * Passes pontuais.
         * V27/V31 ainda criam alguns elementos após o load.
         * Não usamos observer contínuo.
         */
        window.setTimeout(
            function () {
                void apply(currentLocale());
            },
            300
        );

        window.setTimeout(
            function () {
                void apply(currentLocale());
            },
            1600
        );
    }

    window.addEventListener(
        "sabino:locale-change",
        function (event) {
            const locale =
                event &&
                event.detail &&
                event.detail.locale
                    ? event.detail.locale
                    : currentLocale();

            void apply(locale);
        }
    );

    if (
        document.readyState === "loading"
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