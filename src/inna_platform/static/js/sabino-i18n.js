(() => {
    "use strict";

    const VERSION =
        "2026.09.08.2";

    const STORAGE_LANGUAGE =
        "sabino.language.v2";

    const LEGACY_STORAGE =
        "sabino_language";

    const CACHE_PREFIX =
        `sabino.i18n.${VERSION}:`;


    /* ======================================================
       MARCAS / TERMOS QUE NUNCA DEVEM SER TRADUZIDOS
       ====================================================== */

    const PROTECTED_EXACT =
        new Set([
            "Sabino.AI",
            "INNA",
            "CPF"
        ]);


    const LEGACY_LOCALE_MAP = {
        pt:      "pt-BR",
        pt_br:   "pt-BR",
        "pt-br": "pt-BR",

        en:      "en-US",
        en_us:   "en-US",
        "en-us": "en-US",

        en_gb:   "en-GB",
        "en-gb": "en-GB",

        es:      "es-ES",
        de:      "de-DE",
        fr:      "fr-FR",
        it:      "it-IT",
        ro:      "ro-RO",
        uk:      "uk-UA",
        ua:      "uk-UA",
        ru:      "ru-RU",
        ar:      "ar-SA",
        sa:      "ar-SA",
        ch:      "de-CH"
    };


    /*
       ISO 639-1:
       lista ampla para o menu global.

       O navegador também pode usar locales
       BCP-47 completos:
       zh-TW, pt-BR, fr-CA, en-AU etc.
    */

    const LANGUAGE_CODES = [
        "aa","ab","ae","af","ak","am","an","ar","as","av","ay","az",
        "ba","be","bg","bh","bi","bm","bn","bo","br","bs",
        "ca","ce","ch","co","cr","cs","cu","cv","cy",
        "da","de","dv","dz",
        "ee","el","en","eo","es","et","eu",
        "fa","ff","fi","fj","fo","fr","fy",
        "ga","gd","gl","gn","gu","gv",
        "ha","he","hi","ho","hr","ht","hu","hy","hz",
        "ia","id","ie","ig","ii","ik","io","is","it","iu",
        "ja","jv",
        "ka","kg","ki","kj","kk","kl","km","kn","ko","kr","ks",
        "ku","kv","kw","ky",
        "la","lb","lg","li","ln","lo","lt","lu","lv",
        "mg","mh","mi","mk","ml","mn","mr","ms","mt","my",
        "na","nb","nd","ne","ng","nl","nn","no","nr","nv","ny",
        "oc","oj","om","or","os",
        "pa","pi","pl","ps","pt",
        "qu",
        "rm","rn","ro","ru","rw",
        "sa","sc","sd","se","sg","si","sk","sl","sm","sn",
        "so","sq","sr","ss","st","su","sv","sw",
        "ta","te","tg","th","ti","tk","tl","tn","to","tr",
        "ts","tt","tw","ty",
        "ug","uk","ur","uz",
        "ve","vi","vo",
        "wa","wo",
        "xh",
        "yi","yo",
        "za","zh","zu"
    ];


    const RTL_LANGUAGES =
        new Set([
            "ar",
            "fa",
            "he",
            "ur",
            "ps",
            "dv",
            "yi",
            "ku"
        ]);


    /* ======================================================
       LOCALE
       ====================================================== */

    function normalizeLocale(value) {

        let raw =
            String(value || "")
                .trim()
                .replaceAll("_", "-");

        if (!raw) {
            return "pt-BR";
        }

        const legacyKey =
            raw
                .toLowerCase()
                .replaceAll("-", "_");

        if (
            LEGACY_LOCALE_MAP[
                legacyKey
            ]
        ) {
            raw =
                LEGACY_LOCALE_MAP[
                    legacyKey
                ];
        }

        try {
            return new Intl.Locale(
                raw
            ).toString();
        }
        catch {
            return raw;
        }
    }


    function baseLanguage(locale) {

        return normalizeLocale(
            locale
        )
            .split("-")[0]
            .toLowerCase();
    }


    function browserLocales() {

        const values = [];

        if (
            Array.isArray(
                navigator.languages
            )
        ) {
            values.push(
                ...navigator.languages
            );
        }

        if (navigator.language) {
            values.push(
                navigator.language
            );
        }

        values.push(
            "pt-BR"
        );

        return [
            ...new Set(
                values
                    .filter(Boolean)
                    .map(
                        normalizeLocale
                    )
            )
        ];
    }


    function detectedLocale() {

        const current =
            localStorage.getItem(
                STORAGE_LANGUAGE
            );

        if (current) {
            return normalizeLocale(
                current
            );
        }


        /*
           Migração transparente
           da preferência antiga.
        */

        const legacy =
            localStorage.getItem(
                LEGACY_STORAGE
            );

        if (legacy) {

            const migrated =
                normalizeLocale(
                    legacy
                );

            localStorage.setItem(
                STORAGE_LANGUAGE,
                migrated
            );

            return migrated;
        }


        return (
            browserLocales()[0]
            ||
            "pt-BR"
        );
    }


    /* ======================================================
       DOCUMENTO
       ====================================================== */

    function updateLanguageCode(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        const label =
            normalized.toUpperCase();


        document
            .querySelectorAll(
                `
                #languageCode,
                [data-language-code],
                .language-code
                `
            )
            .forEach(
                element => {

                    element.textContent =
                        label;
                }
            );
    }


    function setDocumentLocale(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        document.documentElement.lang =
            normalized;

        document.documentElement.dir =
            RTL_LANGUAGES.has(
                baseLanguage(
                    normalized
                )
            )
                ? "rtl"
                : "ltr";


        document.documentElement
            .dataset
            .sabinoLocale =
                normalized;


        updateLanguageCode(
            normalized
        );
    }


    /* ======================================================
       PROTEÇÃO DE MARCA
       ====================================================== */

    function protectStaticBrandNodes() {

        document
            .querySelectorAll(
                "body *"
            )
            .forEach(
                element => {

                    if (
                        element.children.length
                        !==
                        0
                    ) {
                        return;
                    }

                    const value =
                        String(
                            element.textContent
                            ||
                            ""
                        ).trim();

                    if (
                        PROTECTED_EXACT.has(
                            value
                        )
                    ) {

                        element.setAttribute(
                            "translate",
                            "no"
                        );

                        element.dataset
                            .sabinoProtected =
                                "true";
                    }
                }
            );
    }


    function isProtectedElement(
        element
    ) {

        if (!element) {
            return true;
        }

        if (
            element.dataset
                .sabinoProtected
            ===
            "true"
        ) {
            return true;
        }

        if (
            element.closest(
                '[translate="no"]'
            )
        ) {
            return true;
        }

        return false;
    }


    /* ======================================================
       TEXTOS BASE
       ====================================================== */

    function collectBaseTexts() {

        protectStaticBrandNodes();

        const texts = {};


        document
            .querySelectorAll(
                "[data-i18n]"
            )
            .forEach(
                element => {

                    if (
                        isProtectedElement(
                            element
                        )
                    ) {
                        return;
                    }

                    const key =
                        element.dataset.i18n;

                    const value =
                        element
                            .textContent
                            .trim();

                    if (
                        key &&
                        value &&
                        !(key in texts)
                    ) {

                        texts[key] =
                            value;
                    }
                }
            );


        document
            .querySelectorAll(
                "[data-i18n-html]"
            )
            .forEach(
                element => {

                    if (
                        isProtectedElement(
                            element
                        )
                    ) {
                        return;
                    }

                    const key =
                        element
                            .dataset
                            .i18nHtml;

                    const value =
                        element
                            .innerHTML
                            .trim();

                    if (
                        key &&
                        value &&
                        !(key in texts)
                    ) {

                        texts[key] =
                            value;
                    }
                }
            );


        document
            .querySelectorAll(
                "[data-i18n-placeholder]"
            )
            .forEach(
                element => {

                    if (
                        isProtectedElement(
                            element
                        )
                    ) {
                        return;
                    }

                    const key =
                        element
                            .dataset
                            .i18nPlaceholder;

                    const value =
                        element.getAttribute(
                            "placeholder"
                        )
                        ||
                        "";

                    if (
                        key &&
                        value &&
                        !(key in texts)
                    ) {

                        texts[key] =
                            value;
                    }
                }
            );


        return texts;
    }


    const BASE_TEXTS =
        collectBaseTexts();


    /* ======================================================
       HTML TRADUZÍVEL SEGURO
       ====================================================== */

    function allowedHtml(html) {

        const template =
            document.createElement(
                "template"
            );

        template.innerHTML =
            String(
                html || ""
            );


        const allowedTags =
            new Set([
                "SPAN",
                "BR",
                "STRONG",
                "B",
                "EM"
            ]);


        const walk = node => {

            [
                ...node.children
            ].forEach(
                child => {

                    if (
                        !allowedTags.has(
                            child.tagName
                        )
                    ) {

                        child.replaceWith(
                            document
                                .createTextNode(
                                    child
                                        .textContent
                                )
                        );

                        return;
                    }


                    [
                        ...child.attributes
                    ].forEach(
                        attribute => {

                            child.removeAttribute(
                                attribute.name
                            );
                        }
                    );


                    walk(
                        child
                    );
                }
            );
        };


        walk(
            template.content
        );

        return template.innerHTML;
    }


    /* ======================================================
       APLICA TRADUÇÃO
       ====================================================== */

    function applyDictionary(
        locale,
        dictionary
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        setDocumentLocale(
            normalized
        );


        document
            .querySelectorAll(
                "[data-i18n]"
            )
            .forEach(
                element => {

                    if (
                        isProtectedElement(
                            element
                        )
                    ) {
                        return;
                    }

                    const key =
                        element.dataset.i18n;

                    if (
                        key &&
                        dictionary[key]
                        !==
                        undefined
                    ) {

                        element.textContent =
                            dictionary[key];
                    }
                }
            );


        document
            .querySelectorAll(
                "[data-i18n-html]"
            )
            .forEach(
                element => {

                    if (
                        isProtectedElement(
                            element
                        )
                    ) {
                        return;
                    }

                    const key =
                        element
                            .dataset
                            .i18nHtml;

                    if (
                        key &&
                        dictionary[key]
                        !==
                        undefined
                    ) {

                        element.innerHTML =
                            allowedHtml(
                                dictionary[
                                    key
                                ]
                            );
                    }
                }
            );


        document
            .querySelectorAll(
                "[data-i18n-placeholder]"
            )
            .forEach(
                element => {

                    const key =
                        element
                            .dataset
                            .i18nPlaceholder;

                    if (
                        key &&
                        dictionary[key]
                        !==
                        undefined
                    ) {

                        element.setAttribute(
                            "placeholder",
                            dictionary[key]
                        );
                    }
                }
            );


        /*
           Reforça marca depois
           de qualquer alteração.
        */

        protectStaticBrandNodes();

        updateLanguageCode(
            normalized
        );


        window.dispatchEvent(
            new CustomEvent(
                "sabino:languagechange",
                {
                    detail: {
                        locale:
                            normalized,

                        language:
                            baseLanguage(
                                normalized
                            )
                    }
                }
            )
        );
    }


    /* ======================================================
       CACHE
       ====================================================== */

    function readCache(locale) {

        try {

            const raw =
                localStorage.getItem(
                    CACHE_PREFIX +
                    normalizeLocale(
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
                CACHE_PREFIX +
                normalizeLocale(
                    locale
                ),
                JSON.stringify(
                    dictionary
                )
            );
        }
        catch {
            /*
               Cache não pode
               derrubar a plataforma.
            */
        }
    }


    /* ======================================================
       API DE TRADUÇÃO
       ====================================================== */

    async function translate(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );


        /*
           Sem textos marcados:
           apenas sincroniza o locale.
        */

        if (
            Object.keys(
                BASE_TEXTS
            ).length
            ===
            0
        ) {
            return {};
        }


        if (
            normalized
                .toLowerCase()
            ===
            "pt-br"
        ) {
            return BASE_TEXTS;
        }


        const cached =
            readCache(
                normalized
            );

        if (cached) {
            return cached;
        }


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

                            texts:
                                BASE_TEXTS
                        })
                }
            );


        if (!response.ok) {

            throw new Error(
                `I18N_HTTP_${response.status}`
            );
        }


        const payload =
            await response.json();


        const dictionary = {
            ...BASE_TEXTS,
            ...(
                payload.translations
                ||
                {}
            )
        };


        writeCache(
            normalized,
            dictionary
        );


        return dictionary;
    }


    /* ======================================================
       MUDA IDIOMA
       ====================================================== */

    async function setLanguage(
        locale,
        options = {}
    ) {

        const normalized =
            normalizeLocale(
                locale
            );


        if (
            options.manual
            ===
            true
        ) {

            /*
               Nova chave global.
            */

            localStorage.setItem(
                STORAGE_LANGUAGE,
                normalized
            );


            /*
               Mantém compatibilidade
               temporária com módulos
               antigos da Sabino.AI.
            */

            localStorage.setItem(
                LEGACY_STORAGE,
                normalized
            );
        }


        setDocumentLocale(
            normalized
        );


        try {

            const dictionary =
                await translate(
                    normalized
                );

            applyDictionary(
                normalized,
                dictionary
            );
        }
        catch (error) {

            console.warn(
                "[Sabino.I18n]",
                error
            );


            /*
               Se a tradução falhar:
               mantém a aplicação funcional.
            */

            setDocumentLocale(
                normalized
            );
        }
    }


    /* ======================================================
       NOME DO IDIOMA
       ====================================================== */

    function languageName(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        try {

            return new Intl.DisplayNames(
                [normalized],
                {
                    type:
                        "language"
                }
            ).of(
                normalized
            )
            ||
            normalized;
        }
        catch {

            return normalized;
        }
    }


    /* ======================================================
       MENU GLOBAL
       ====================================================== */

    function buildLanguageMenu() {

        const menu =
            document.getElementById(
                "languageMenu"
            );

        if (!menu) {
            return;
        }


        menu.innerHTML = "";


        /*
           Primeiro coloca idiomas/regions
           mais comuns e preferências do
           próprio navegador.

           Depois completa com ISO 639-1.
        */

        const candidates = [
            ...browserLocales(),

            "pt-BR",
            "pt-PT",

            "en-US",
            "en-GB",
            "en-CA",
            "en-AU",

            "es-ES",
            "es-MX",
            "es-AR",

            "fr-FR",
            "fr-CA",

            "de-DE",
            "de-CH",
            "de-AT",

            "it-IT",

            "nl-NL",
            "pl-PL",
            "ro-RO",

            "uk-UA",
            "ru-RU",

            "ar-SA",
            "he-IL",

            "tr-TR",

            "hi-IN",
            "bn-BD",

            "zh-CN",
            "zh-TW",
            "zh-HK",

            "ja-JP",
            "ko-KR",

            "vi-VN",
            "th-TH",
            "id-ID",

            ...LANGUAGE_CODES
        ];


        const unique = [
            ...new Set(
                candidates
                    .filter(Boolean)
                    .map(
                        normalizeLocale
                    )
            )
        ];


        unique.forEach(
            locale => {

                const button =
                    document.createElement(
                        "button"
                    );

                button.type =
                    "button";

                button.className =
                    "language-option";

                button.dataset.lang =
                    locale;


                button.textContent =
                    `${languageName(
                        locale
                    )} · ${locale}`;


                button.addEventListener(
                    "click",
                    async () => {

                        menu.classList.remove(
                            "open"
                        );

                        await setLanguage(
                            locale,
                            {
                                manual:
                                    true
                            }
                        );
                    }
                );


                menu.appendChild(
                    button
                );
            }
        );
    }


    /* ======================================================
       CSS AUXILIAR MENU
       ====================================================== */

    function installMenuStyle() {

        if (
            document.getElementById(
                "sabino-i18n-global-style"
            )
        ) {
            return;
        }


        const style =
            document.createElement(
                "style"
            );

        style.id =
            "sabino-i18n-global-style";

        style.textContent = `
            #languageMenu {
                max-height: min(70vh, 620px);
                overflow-y: auto;
                overscroll-behavior: contain;
            }

            [dir="rtl"] #languageMenu {
                text-align: right;
            }
        `;


        document.head.appendChild(
            style
        );
    }


    /* ======================================================
       API GLOBAL
       ====================================================== */

    function exposeGlobalApi() {

        window.SabinoI18n = {

            version:
                VERSION,

            get locale() {
                return normalizeLocale(
                    document
                        .documentElement
                        .lang
                    ||
                    detectedLocale()
                );
            },

            get language() {
                return baseLanguage(
                    this.locale
                );
            },

            detect:
                detectedLocale,

            browserLocales,

            normalizeLocale,

            baseLanguage,

            setLanguage
        };
    }


    /* ======================================================
       BOOT
       ====================================================== */

    async function boot() {

        installMenuStyle();

        exposeGlobalApi();

        protectStaticBrandNodes();

        buildLanguageMenu();


        const locale =
            detectedLocale();


        setDocumentLocale(
            locale
        );


        await setLanguage(
            locale,
            {
                manual:
                    false
            }
        );
    }


    if (
        document.readyState
        ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            boot,
            {
                once:
                    true
            }
        );
    }
    else {

        boot();
    }

})();
