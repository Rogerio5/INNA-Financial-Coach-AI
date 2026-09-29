(() => {
    "use strict";

    const VERSION =
        "2026.09.08.page.1";

    const PAGE =
        (
            location.pathname
            ||
            "/"
        )
        .replace(
            /[^a-zA-Z0-9]+/g,
            "_"
        )
        .replace(
            /^_+|_+$/g,
            ""
        )
        ||
        "root";


    const SKIP_SELECTOR = [
        "script",
        "style",
        "noscript",
        "svg",
        "path",
        "code",
        "pre",
        "textarea",

        '[translate="no"]',
        "[data-i18n-skip]",
        "[data-sabino-protected]",

        "#languageButton",
        "#languageMenu",

        "[data-user-name]",
        "[data-user-id]",
        "[data-account-id]",

        ".username",
        ".user-name",
        ".user-avatar",
        ".avatar"
    ].join(",");


    const EXACT_PROTECTED =
        new Set([
            "Sabino.AI",
            "INNA",
            "CPF",
            "RS"
        ]);


    function normalizeLocale(value) {

        if (
            window.SabinoI18n &&
            window.SabinoI18n.normalizeLocale
        ) {
            return (
                window.SabinoI18n
                    .normalizeLocale(
                        value
                    )
            );
        }


        const raw =
            String(
                value || "pt-BR"
            )
            .replaceAll(
                "_",
                "-"
            );


        try {

            return new Intl.Locale(
                raw
            ).toString();

        }
        catch {

            return raw;
        }
    }


    function currentLocale() {

        if (
            window.SabinoI18n &&
            window.SabinoI18n.locale
        ) {

            return normalizeLocale(
                window.SabinoI18n.locale
            );
        }


        return normalizeLocale(
            localStorage.getItem(
                "sabino.language.v2"
            )
            ||
            localStorage.getItem(
                "sabino_language"
            )
            ||
            navigator.language
            ||
            "pt-BR"
        );
    }


    /*
       Valores que NÃO devem
       ser enviados para tradução.
    */

    function looksLikeDataValue(
        text
    ) {

        const value =
            String(
                text || ""
            ).trim();


        if (!value) {
            return true;
        }


        if (
            EXACT_PROTECTED.has(
                value
            )
        ) {
            return true;
        }


        /*
           URL / email
        */

        if (
            /https?:\/\//i.test(
                value
            )
            ||
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
                value
            )
        ) {
            return true;
        }


        /*
           Valor financeiro
        */

        if (
            /^(?:R\$|US\$|\$|€|£|¥|CHF|BRL|USD|EUR|GBP)\s*[\d.,]+$/i.test(
                value
            )
        ) {
            return true;
        }


        /*
           Percentual / número / horário
        */

        if (
            /^[+\-]?\d[\d\s.,:/%+\-]*$/.test(
                value
            )
        ) {
            return true;
        }


        /*
           Data simples
        */

        if (
            /^\d{1,4}[\/.-]\d{1,2}[\/.-]\d{1,4}$/.test(
                value
            )
        ) {
            return true;
        }


        /*
           Siglas curtas.
        */

        if (
            /^[A-Z0-9]{1,4}$/.test(
                value
            )
        ) {
            return true;
        }


        return false;
    }


    function canTranslate(
        node
    ) {

        if (
            !node ||
            !node.parentElement
        ) {
            return false;
        }


        const parent =
            node.parentElement;


        if (
            parent.closest(
                SKIP_SELECTOR
            )
        ) {
            return false;
        }


        /*
           Se o elemento já usa o i18n
           explícito global, não duplica.
        */

        if (
            parent.closest(
                "[data-i18n]," +
                "[data-i18n-html]," +
                "[data-i18n-placeholder]"
            )
        ) {
            return false;
        }


        const text =
            String(
                node.nodeValue || ""
            ).trim();


        if (
            text.length < 2
        ) {
            return false;
        }


        if (
            looksLikeDataValue(
                text
            )
        ) {
            return false;
        }


        return true;
    }


    function captureRecords() {

        if (!document.body) {
            return [];
        }


        const walker =
            document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode:
                        node =>
                            canTranslate(
                                node
                            )
                                ?
                                NodeFilter
                                    .FILTER_ACCEPT
                                :
                                NodeFilter
                                    .FILTER_REJECT
                }
            );


        const records = [];

        let node;


        while (
            (
                node =
                    walker.nextNode()
            )
        ) {

            const raw =
                node.nodeValue
                ||
                "";


            const leading =
                raw.match(
                    /^\s*/
                )?.[0]
                ||
                "";


            const trailing =
                raw.match(
                    /\s*$/
                )?.[0]
                ||
                "";


            const base =
                raw.trim();


            records.push({
                node,

                key:
                    `${PAGE}.text.${String(
                        records.length
                    ).padStart(
                        4,
                        "0"
                    )}`,

                base,

                leading,

                trailing
            });
        }


        return records;
    }


    /*
       Captura o português ORIGINAL
       antes de qualquer tradução
       da página.
    */

    const RECORDS =
        captureRecords();


    function restorePortuguese() {

        RECORDS.forEach(
            record => {

                record.node.nodeValue =
                    record.leading
                    +
                    record.base
                    +
                    record.trailing;
            }
        );
    }


    function simpleHash(value) {

        let hash =
            2166136261;


        for (
            let i = 0;
            i < value.length;
            i++
        ) {

            hash ^=
                value.charCodeAt(
                    i
                );


            hash =
                Math.imul(
                    hash,
                    16777619
                );
        }


        return (
            hash >>> 0
        ).toString(
            16
        );
    }


    function textsObject() {

        const result = {};


        RECORDS.forEach(
            record => {

                result[
                    record.key
                ] =
                    record.base;
            }
        );


        return result;
    }


    const BASE_TEXTS =
        textsObject();


    const BASE_HASH =
        simpleHash(
            JSON.stringify(
                BASE_TEXTS
            )
        );


    function cacheKey(
        locale
    ) {

        return (
            `sabino.page.i18n.` +
            `${VERSION}:` +
            `${PAGE}:` +
            `${normalizeLocale(
                locale
            )}:` +
            BASE_HASH
        );
    }


    function readCache(
        locale
    ) {

        try {

            const raw =
                localStorage.getItem(
                    cacheKey(
                        locale
                    )
                );


            if (!raw) {
                return null;
            }


            return JSON.parse(
                raw
            );

        }
        catch {

            return null;
        }
    }


    function writeCache(
        locale,
        dictionary
    ) {

        try {

            localStorage.setItem(
                cacheKey(
                    locale
                ),
                JSON.stringify(
                    dictionary
                )
            );

        }
        catch {

            /*
               Cache não é obrigatório.
            */
        }
    }


    function apply(
        dictionary
    ) {

        RECORDS.forEach(
            record => {

                const translated =
                    dictionary[
                        record.key
                    ];


                if (
                    typeof translated
                    !==
                    "string"
                ) {
                    return;
                }


                record.node.nodeValue =
                    record.leading
                    +
                    translated
                    +
                    record.trailing;
            }
        );
    }


    /*
       API aceita até 150 chaves.
       Trabalhamos com lotes menores.
    */

    function chunks(
        entries,
        size = 80
    ) {

        const result = [];


        for (
            let i = 0;
            i < entries.length;
            i += size
        ) {

            result.push(
                entries.slice(
                    i,
                    i + size
                )
            );
        }


        return result;
    }


    let generation =
        0;


    async function translatePage(
        locale
    ) {

        const myGeneration =
            ++generation;


        const normalized =
            normalizeLocale(
                locale
            );


        if (
            normalized
                .toLowerCase()
            ===
            "pt-br"
            ||
            normalized
                .toLowerCase()
            ===
            "pt"
        ) {

            restorePortuguese();

            return;
        }


        if (
            RECORDS.length ===
            0
        ) {
            return;
        }


        const cached =
            readCache(
                normalized
            );


        if (cached) {

            if (
                myGeneration
                ===
                generation
            ) {

                apply(
                    cached
                );
            }

            return;
        }


        const entries =
            Object.entries(
                BASE_TEXTS
            );


        const dictionary = {};


        for (
            const group
            of
            chunks(
                entries
            )
        ) {

            const texts =
                Object.fromEntries(
                    group
                );


            const response =
                await fetch(
                    "/api/i18n/translate",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                locale:
                                    normalized,

                                texts
                            })
                    }
                );


            if (
                !response.ok
            ) {

                throw new Error(
                    `PAGE_I18N_HTTP_${
                        response.status
                    }`
                );
            }


            const payload =
                await response.json();


            Object.assign(
                dictionary,
                payload.translations
                ||
                {}
            );


            if (
                myGeneration
                !==
                generation
            ) {
                return;
            }
        }


        writeCache(
            normalized,
            dictionary
        );


        if (
            myGeneration
            ===
            generation
        ) {

            apply(
                dictionary
            );
        }
    }


    async function safeTranslate(
        locale
    ) {

        try {

            await translatePage(
                locale
            );

        }
        catch (error) {

            console.warn(
                "[Sabino.PageI18n]",
                error
            );
        }
    }


    window.addEventListener(
        "sabino:languagechange",
        event => {

            safeTranslate(
                event.detail?.locale
                ||
                currentLocale()
            );
        }
    );


    function boot() {

        safeTranslate(
            currentLocale()
        );
    }


    window.SabinoPageI18n = {
        version:
            VERSION,

        page:
            PAGE,

        records:
            RECORDS.length,

        translate:
            safeTranslate,

        restorePortuguese
    };


    if (
        document.readyState
        ===
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

})();
