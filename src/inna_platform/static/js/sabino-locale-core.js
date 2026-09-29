
(function () {

    "use strict";

    if (window.SabinoLocale) {
        return;
    }

    const STORAGE_LANGUAGE =
        "sabino_language";

    const STORAGE_MANUAL =
        "sabino_language_manual";

    const STORAGE_SOURCE =
        "sabino_language_source";

    const FALLBACK_LOCALE =
        "pt-BR";


    /*
     * ISO 639-1.
     *
     * O seletor não fica limitado aos 12 idiomas antigos.
     * Os nomes são renderizados pelo próprio Intl do navegador.
     */

    const BASE_LANGUAGE_CODES = `
aa ab ae af ak am an ar as av ay az
ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv cy
da de dv dz ee el en eo es et eu
fa ff fi fj fo fr fy
ga gd gl gn gu gv
ha he hi ho hr ht hu hy hz
ia id ie ig ii ik io is it iu
ja jv
ka kg ki kj kk kl km kn ko kr ks ku kv kw ky
la lb lg li ln lo lt lu lv
mg mh mi mk ml mn mr ms mt my
na nb nd ne ng nl nn no nr nv ny
oc oj om or os
pa pi pl ps pt
qu
rm rn ro ru rw
sa sc sd se sg si sk sl sm sn so sq sr ss st su sv sw
ta te tg th ti tk tl tn to tr ts tt tw ty
ug uk ur uz
ve vi vo
wa wo
xh
yi yo
za zh zu
`
        .trim()
        .split(/\s+/);


    /*
     * Variantes regionais importantes.
     * Elas ficam acima do idioma-base no seletor.
     */

    const REGIONAL_LOCALES = [

        "pt-BR",
        "pt-PT",

        "en-US",
        "en-GB",
        "en-CA",
        "en-AU",
        "en-NZ",
        "en-IN",

        "es-ES",
        "es-MX",
        "es-AR",
        "es-CO",
        "es-CL",
        "es-PE",

        "fr-FR",
        "fr-CA",
        "fr-BE",
        "fr-CH",

        "de-DE",
        "de-AT",
        "de-CH",

        "it-IT",
        "it-CH",

        "nl-NL",
        "nl-BE",

        "ro-RO",
        "pl-PL",
        "cs-CZ",
        "sk-SK",
        "hu-HU",

        "sv-SE",
        "nb-NO",
        "da-DK",
        "fi-FI",

        "ru-RU",
        "uk-UA",

        "tr-TR",
        "el-GR",

        "ar-SA",
        "ar-AE",
        "ar-EG",
        "ar-MA",

        "he-IL",
        "fa-IR",

        "hi-IN",
        "bn-BD",
        "ur-PK",

        "zh-CN",
        "zh-TW",
        "zh-HK",
        "zh-SG",

        "ja-JP",
        "ko-KR",

        "th-TH",
        "vi-VN",

        "id-ID",
        "ms-MY",

        "sw-KE",

        "af-ZA"
    ];



    /*
     * SABINO_SELECTOR_3_LANGUAGES_V1
     *
     * O núcleo continua podendo reconhecer outros locales
     * automaticamente pelo navegador.
     *
     * O seletor manual da Sabino.AI mostra apenas:
     * pt-BR, en-US e es-ES.
     */
    const SELECTOR_LOCALES = [
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
    ];

const SIMPLE_SELECTOR_LABELS = {
        "pt-BR": "Português Brasil",
        "en-US": "English US",
        "en-GB": "English UK",
        "es-ES": "Español",
        "de-DE": "Deutsch",
        "fr-FR": "Français",
        "it-IT": "Italiano",
        "ru-RU": "Русский",
        "ar-SA": "العربية",
        "ro-RO": "Română",
        "uk-UA": "Українська",
        "de-CH": "Schweiz"
    };

    const RTL_LANGUAGES =
        new Set([
            "ar",
            "fa",
            "he",
            "ur",
            "ps",
            "dv",
            "yi"
        ]);


    const ALL_LOCALES =
        Array.from(
            new Set([
                ...REGIONAL_LOCALES,
                ...BASE_LANGUAGE_CODES
            ])
        );


    function normalizeLocale(
        locale
    ) {

        if (!locale) {
            return FALLBACK_LOCALE;
        }

        let raw =
            String(locale)
                .trim()
                .replace(
                    /_/g,
                    "-"
                );

        if (!raw) {
            return FALLBACK_LOCALE;
        }

        const parts =
            raw.split("-");

        const language =
            parts[0].toLowerCase();

        if (parts.length === 1) {
            return language;
        }

        const normalized = [
            language
        ];

        for (
            let index = 1;
            index < parts.length;
            index += 1
        ) {

            const part =
                parts[index];

            if (part.length === 2) {

                normalized.push(
                    part.toUpperCase()
                );

            }
            else if (
                part.length === 4
            ) {

                normalized.push(
                    part.charAt(0).toUpperCase()
                    +
                    part.slice(1).toLowerCase()
                );

            }
            else {

                normalized.push(
                    part
                );

            }

        }

        return normalized.join("-");

    }


    function languageBase(
        locale
    ) {

        return normalizeLocale(
            locale
        )
        .split("-")[0];

    }


    function isKnownLanguage(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        const base =
            languageBase(
                normalized
            );

        return (
            ALL_LOCALES.includes(
                normalized
            ) ||
            BASE_LANGUAGE_CODES.includes(
                base
            )
        );

    }


    function browserCandidates() {

        const result = [];

        if (
            Array.isArray(
                navigator.languages
            )
        ) {

            result.push(
                ...navigator.languages
            );

        }

        if (
            navigator.language
        ) {

            result.push(
                navigator.language
            );

        }

        return Array.from(
            new Set(
                result
                    .filter(Boolean)
                    .map(normalizeLocale)
            )
        );

    }


    /*
     * SABINO_BROWSER_LOCALE_RESOLVER_V1
     *
     * Exemplos:
     * be -> be-BY
     * pt -> pt-BR
     * en -> en-US
     * zh-Hant -> zh-TW
     *
     * Se o navegador já informar região,
     * ela é preservada.
     */
    function resolveBrowserLocale(
        candidate
    ) {

        const normalized =
            normalizeLocale(
                candidate
            );


        if (
            !isKnownLanguage(
                normalized
            )
        ) {
            return null;
        }


        try {

            if (
                typeof Intl.Locale
                ===
                "function"
            ) {

                const parsed =
                    new Intl.Locale(
                        normalized
                    );


                /*
                 * O navegador já informou
                 * país/região. Preservamos.
                 */
                if (parsed.region) {

                    return normalized;

                }


                /*
                 * Sem região:
                 * Intl.Locale infere a região
                 * mais provável para o idioma.
                 */
                const maximized =
                    parsed.maximize();


                if (maximized.region) {

                    return normalizeLocale(
                        languageBase(
                            normalized
                        )
                        +
                        "-"
                        +
                        maximized.region
                    );

                }

            }

        }
        catch (_) {
        }


        return normalized;

    }


    function detectBrowserLocale() {

        /*
         * SABINO_BROWSER_ANY_LOCALE_V3
         *
         * O navegador pode usar qualquer locale reconhecido
         * pelo núcleo da Sabino.AI.
         *
         * SELECTOR_LOCALES limita apenas o seletor manual.
         */

        const candidates =
            browserCandidates();


        for (
            const candidate
            of candidates
        ) {

            const resolved =
                resolveBrowserLocale(
                    candidate
                );


            if (resolved) {

                return resolved;

            }

        }


        return FALLBACK_LOCALE;

    }


    function manualLocale() {

        const source =
            localStorage.getItem(
                STORAGE_SOURCE
            );


        if (source !== "manual") {

            return null;

        }


        const value =
            normalizeLocale(
                localStorage.getItem(
                    STORAGE_MANUAL
                ) || ""
            );


        if (
            !SELECTOR_LOCALES.includes(
                value
            )
        ) {

            return null;

        }


        return value;

    }


    function currentLocale() {

        /*
         * SABINO_PAGE_BROWSER_FORCE_V1
         *
         * Páginas públicas, como login, podem solicitar
         * exclusivamente o locale do navegador sem apagar
         * a preferência manual do usuário.
         */

        if (
            window.SABINO_FORCE_BROWSER_LOCALE ===
            true
        ) {

            return detectBrowserLocale();

        }


        return (
            manualLocale() ||
            detectBrowserLocale()
        );

    }


    function setDirection(
        locale
    ) {

        const base =
            languageBase(locale);

        document.documentElement.lang =
            locale;

        document.documentElement.dir =
            RTL_LANGUAGES.has(base)
                ? "rtl"
                : "ltr";

    }


    function legacyCandidates(
        locale
    ) {

        const normalized =
            normalizeLocale(locale);

        const base =
            languageBase(normalized);

        const underscore =
            normalized.replace(
                /-/g,
                "_"
            );

        const candidates = [
            normalized,
            underscore,
            base
        ];

        if (normalized === "pt-BR") {
            candidates.push(
                "pt",
                "pt_br"
            );
        }

        if (normalized === "pt-PT") {
            candidates.push(
                "pt"
            );
        }

        if (normalized === "en-US") {
            candidates.push(
                "en",
                "en_us"
            );
        }

        if (normalized === "en-GB") {
            candidates.push(
                "en",
                "en_gb"
            );
        }

        if (normalized.startsWith("es-")) {
            candidates.push(
                "es",
                "es_es"
            );
        }

        if (normalized.startsWith("fr-")) {
            candidates.push(
                "fr",
                "fr_fr"
            );
        }

        if (normalized.startsWith("de-")) {
            candidates.push(
                "de",
                "de_de"
            );
        }

        if (normalized.startsWith("it-")) {
            candidates.push(
                "it",
                "it_it"
            );
        }

        if (normalized.startsWith("ro-")) {
            candidates.push(
                "ro",
                "ro_ro"
            );
        }

        if (normalized.startsWith("ru-")) {
            candidates.push(
                "ru",
                "ru_ru"
            );
        }

        if (normalized.startsWith("uk-")) {
            candidates.push(
                "uk",
                "uk_ua",
                "ua"
            );
        }

        if (normalized.startsWith("ar-")) {
            candidates.push(
                "ar",
                "ar_sa",
                "sa"
            );
        }

        return Array.from(
            new Set(candidates)
        );

    }


    function findExistingDictionaryKey(
        locale
    ) {

        try {

            if (
                typeof TEXTS !==
                    "object" ||
                !TEXTS
            ) {

                return null;

            }

            for (
                const candidate
                of legacyCandidates(locale)
            ) {

                if (
                    Object.prototype
                        .hasOwnProperty
                        .call(
                            TEXTS,
                            candidate
                        )
                ) {

                    return candidate;

                }

            }

        }
        catch (error) {

            console.debug(
                "SABINO_LOCALE_TEXTS_LOOKUP",
                error
            );

        }

        return null;

    }


    function callLegacyLanguageSystem(
        locale
    ) {

        try {

            if (
                typeof window.applyLanguage
                !== "function"
            ) {

                return false;

            }

            const dictionaryKey =
                findExistingDictionaryKey(
                    locale
                );

            if (
                dictionaryKey
            ) {

                window.applyLanguage(
                    dictionaryKey
                );

                return true;

            }

        }
        catch (error) {

            console.warn(
                "SABINO_LOCALE_LEGACY_BRIDGE_ERROR",
                error
            );

        }

        return false;

    }


    function dispatchChange(
        locale,
        source
    ) {

        window.dispatchEvent(
            new CustomEvent(
                "sabino:locale-change",
                {
                    detail: {
                        locale,
                        language:
                            languageBase(
                                locale
                            ),
                        source
                    }
                }
            )
        );

    }


    function applyLocale(
        locale,
        options = {}
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        const source =
            options.source ||
            "runtime";

        setDirection(
            normalized
        );

        /*
         * Compatibilidade com as páginas antigas.
         */

        localStorage.setItem(
            STORAGE_LANGUAGE,
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


        callLegacyLanguageSystem(
            normalized
        );


        dispatchChange(
            normalized,
            source
        );


        updateSelector(
            normalized
        );


        /*
         * Algumas páginas constroem cards depois do load.
         */

        /*
         * SABINO_PERF_LEGACY_LANGUAGE_RETRY_V1
         *
         * Compatibilidade apenas para páginas que ainda possuem
         * o writer legado window.applyLanguage().
         *
         * /modulos não possui esse writer e não precisa criar
         * retries de idioma após o carregamento.
         */
        if (
            typeof window.applyLanguage === "function"
        ) {

            setTimeout(
                function () {
                    callLegacyLanguageSystem(
                        normalized
                    );
                },
                100
            );

            setTimeout(
                function () {
                    callLegacyLanguageSystem(
                        normalized
                    );
                },
                600
            );

        }


        console.log(
            "SABINO_GLOBAL_LOCALE",
            normalized,
            source
        );

        return normalized;

    }


    function clearManualLocale() {

        localStorage.removeItem(
            STORAGE_MANUAL
        );

        return applyLocale(
            detectBrowserLocale(),
            {
                source:
                    "browser",
                manual:
                    false
            }
        );

    }


    function displayName(
        locale,
        displayLocale
    ) {

        try {

            const names =
                new Intl.DisplayNames(
                    [
                        displayLocale ||
                        "pt-BR"
                    ],
                    {
                        type:
                            "language"
                    }
                );

            return (
                names.of(locale) ||
                locale
            );

        }
        catch {

            return locale;

        }

    }


    function nativeName(
        locale
    ) {

        try {

            const names =
                new Intl.DisplayNames(
                    [locale],
                    {
                        type:
                            "language"
                    }
                );

            return (
                names.of(locale) ||
                locale
            );

        }
        catch {

            return locale;

        }

    }


    function createSelector() {

        if (
            document.getElementById(
                "sabinoGlobalLanguage"
            )
        ) {

            return;

        }

        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.id =
            "sabinoGlobalLanguage";

        wrapper.className =
            "sabino-global-language";


        const button =
            document.createElement(
                "button"
            );

        button.id =
            "sabinoGlobalLanguageButton";

        button.className =
            "sabino-global-language-button";

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
            "sabinoGlobalLanguagePanel";

        panel.className =
            "sabino-global-language-panel";

        panel.hidden =
            true;


        const heading =
            document.createElement(
                "div"
            );

        heading.className =
            "sabino-global-language-heading";

        heading.textContent =
            "Idioma / Language";


        const automatic =
            document.createElement(
                "button"
            );

        automatic.type =
            "button";

        automatic.className =
            "sabino-global-language-auto";

        automatic.id =
            "sabinoGlobalLanguageAuto";


        const input =
            document.createElement(
                "input"
            );

        input.type =
            "search";

        input.id =
            "sabinoGlobalLanguageSearch";

        input.className =
            "sabino-global-language-search";

        input.placeholder =
            "Selecionar idioma";

        input.autocomplete =
            "off";


        const list =
            document.createElement(
                "div"
            );

        list.id =
            "sabinoGlobalLanguageList";

        list.className =
            "sabino-global-language-list";

        list.setAttribute(
            "role",
            "listbox"
        );


        panel.appendChild(
            heading
        );

        panel.appendChild(
            automatic
        );

        panel.appendChild(
            input
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

                    renderLanguageList(
                        input.value
                    );

                    setTimeout(
                        function () {
                            input.focus();
                        },
                        0
                    );

                }

            }
        );


        automatic.addEventListener(
            "click",
            function () {

                clearManualLocale();

                panel.hidden =
                    true;

                button.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }
        );


        input.addEventListener(
            "input",
            function () {

                renderLanguageList(
                    input.value
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


        updateSelector(
            currentLocale()
        );

    }


    function renderLanguageList(
        query = ""
    ) {

        const list =
            document.getElementById(
                "sabinoGlobalLanguageList"
            );

        if (!list) {
            return;
        }

        const active =
            currentLocale();

        const search =
            String(query || "")
                .trim()
                .toLocaleLowerCase();

        list.innerHTML =
            "";


        for (
            const locale
            of SELECTOR_LOCALES
        ) {

            const native =
                nativeName(
                    locale
                );

            const translated =
                displayName(
                    locale,
                    active
                );

            const haystack =
                (
                    locale +
                    " " +
                    native +
                    " " +
                    translated
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
                "sabino-global-language-option";

            option.dataset.locale =
                locale;

            option.setAttribute(
                "role",
                "option"
            );


            if (
                normalizeLocale(active) ===
                normalizeLocale(locale)
            ) {

                option.classList.add(
                    "active"
                );

                option.setAttribute(
                    "aria-selected",
                    "true"
                );

            }


            const check =
                document.createElement(
                    "span"
                );

            check.className =
                "sabino-language-check";

            check.textContent =
                option.classList.contains(
                    "active"
                )
                    ? "✓"
                    : "";


            const label =
                document.createElement(
                    "span"
                );

            label.className =
                "sabino-language-label";


            const main =
                document.createElement(
                    "strong"
                );

            main.textContent =
                SIMPLE_SELECTOR_LABELS[locale]
                || native;


            const secondary =
                document.createElement(
                    "small"
                );

            secondary.textContent =
                (
                    translated !== native
                        ? translated + " · "
                        : ""
                )
                +
                locale;


            label.appendChild(
                main
            );

            label.appendChild(
                secondary
            );


            option.appendChild(
                check
            );

            option.appendChild(
                label
            );


            option.addEventListener(
                "click",
                function () {

                    applyLocale(
                        locale,
                        {
                            source:
                                "manual",
                            manual:
                                true
                        }
                    );

                    const panel =
                        document.getElementById(
                            "sabinoGlobalLanguagePanel"
                        );

                    if (panel) {
                        panel.hidden =
                            true;
                    }

                    const button =
                        document.getElementById(
                            "sabinoGlobalLanguageButton"
                        );

                    if (button) {

                        button.setAttribute(
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


    function updateSelector(
        locale
    ) {

        const normalized =
            normalizeLocale(
                locale
            );

        const button =
            document.getElementById(
                "sabinoGlobalLanguageButton"
            );

        const automatic =
            document.getElementById(
                "sabinoGlobalLanguageAuto"
            );


        if (button) {

            button.textContent =
                "🌐 " +
                normalized.toUpperCase() +
                " ▾";

        }


        if (automatic) {

            const detected =
                detectBrowserLocale();

            automatic.textContent =
                (
                    manualLocale()
                        ? "Automático do navegador"
                        : "✓ Automático pelo navegador: "
                )
                +
                displayName(
                    detected,
                    normalized
                )
                +
                " (" +
                detected +
                ")";

        }


        const list =
            document.getElementById(
                "sabinoGlobalLanguageList"
            );

        if (list) {

            renderLanguageList(
                document.getElementById(
                    "sabinoGlobalLanguageSearch"
                )?.value || ""
            );

        }

    }


    window.SabinoLocale = {

        all:
            SELECTOR_LOCALES.slice(),

        normalize:
            normalizeLocale,

        current:
            currentLocale,

        browser:
            detectBrowserLocale,

        apply:
            function (locale) {

                return applyLocale(
                    locale,
                    {
                        source:
                            "manual",
                        manual:
                            true
                    }
                );

            },

        automatic:
            clearManualLocale,

        base:
            languageBase

    };


    function start() {

        createSelector();

        const manual =
            manualLocale();

        applyLocale(
            manual ||
            detectBrowserLocale(),
            {
                source:
                    manual
                        ? "manual"
                        : "browser",

                manual:
                    Boolean(manual)
            }
        );

        console.log(
            "SABINO_GLOBAL_LOCALE_CORE=READY"
        );

        console.log(
            "SABINO_GLOBAL_LOCALE_COUNT=" +
            SELECTOR_LOCALES.length
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
