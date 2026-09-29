(() => {
    "use strict";

    const VERSION =
        "2026.09.08.2d2";

    const LANGUAGE_STORAGE =
        "sabino.language.v2";

    const LEGACY_LANGUAGE_STORAGE =
        "sabino_language";


    let activeLocale =
        null;


    function normalizeLocale(
        value
    ) {

        const raw =
            String(
                value || "pt-BR"
            )
            .trim()
            .replaceAll(
                "_",
                "-"
            );


        if (
            window.SabinoI18n &&
            typeof window
                .SabinoI18n
                .normalizeLocale
                ===
                "function"
        ) {

            return window
                .SabinoI18n
                .normalizeLocale(
                    raw
                );
        }


        try {

            return new Intl.Locale(
                raw
            ).toString();

        }
        catch {

            return (
                raw ||
                "pt-BR"
            );
        }
    }


    function getLocale() {

        /*
           1. Motor global Sabino.AI
        */

        if (
            window.SabinoI18n &&
            window.SabinoI18n.locale
        ) {

            return normalizeLocale(
                window.SabinoI18n.locale
            );
        }


        /*
           2. Escolha manual salva.
        */

        const stored =
            localStorage.getItem(
                LANGUAGE_STORAGE
            );

        if (stored) {

            return normalizeLocale(
                stored
            );
        }


        /*
           3. Compatibilidade antiga.
        */

        const legacy =
            localStorage.getItem(
                LEGACY_LANGUAGE_STORAGE
            );

        if (legacy) {

            return normalizeLocale(
                legacy
            );
        }


        /*
           4. Navegador.
        */

        if (
            Array.isArray(
                navigator.languages
            ) &&
            navigator.languages.length
        ) {

            return normalizeLocale(
                navigator.languages[0]
            );
        }


        return normalizeLocale(
            navigator.language
            ||
            "pt-BR"
        );
    }


    function setActiveLocale(
        locale
    ) {

        activeLocale =
            normalizeLocale(
                locale
            );


        document.documentElement
            .dataset
            .innaLocale =
                activeLocale;


        window.dispatchEvent(
            new CustomEvent(
                "sabino:inna:locale",
                {
                    detail: {
                        locale:
                            activeLocale
                    }
                }
            )
        );
    }


    function currentLocale() {

        if (activeLocale) {
            return activeLocale;
        }

        activeLocale =
            getLocale();

        return activeLocale;
    }


    async function ask(
        question,
        options = {}
    ) {

        const pergunta =
            String(
                question || ""
            ).trim();


        if (
            pergunta.length < 2
        ) {

            throw new Error(
                "INNA_QUESTION_TOO_SHORT"
            );
        }


        if (
            pergunta.length > 4000
        ) {

            throw new Error(
                "INNA_QUESTION_TOO_LONG"
            );
        }


        const locale =
            normalizeLocale(
                options.locale
                ||
                currentLocale()
            );


        let topK =
            Number(
                options.topK
                ??
                options.top_k
                ??
                4
            );


        if (
            !Number.isFinite(
                topK
            )
        ) {

            topK = 4;
        }


        topK =
            Math.max(
                1,
                Math.min(
                    8,
                    Math.trunc(
                        topK
                    )
                )
            );


        const payload = {
            pergunta,
            idioma:
                locale,
            top_k:
                topK
        };


        window.dispatchEvent(
            new CustomEvent(
                "sabino:inna:request",
                {
                    detail: {
                        locale,
                        pergunta,
                        top_k:
                            topK
                    }
                }
            )
        );


        try {

            const { askPaid } = await import('/static/js/sabino-paid-analysis.js');
            const response = await askPaid(payload, options);

            let data = null;


            try {

                data =
                    await response.json();

            }
            catch {

                data = {};
            }


            if (
                !response.ok
            ) {

                const error =
                    new Error(
                        data?.detail
                        ||
                        `INNA_HTTP_${
                            response.status
                        }`
                    );


                error.status =
                    response.status;


                throw error;
            }


            if (
                !data ||
                typeof data
                    !==
                    "object"
            ) {

                throw new Error(
                    "INNA_INVALID_RESPONSE"
                );
            }


            const resposta =
                String(
                    data.resposta
                    ||
                    ""
                ).trim();


            if (!resposta) {

                throw new Error(
                    "INNA_EMPTY_RESPONSE"
                );
            }


            window.dispatchEvent(
                new CustomEvent(
                    "sabino:inna:response",
                    {
                        detail: {
                            locale,
                            pergunta,
                            resposta,
                            fontes:
                                data.fontes
                                ||
                                [],

                            modo:
                                data.modo
                                ||
                                null,

                            trace_id:
                                data.trace_id
                                ||
                                null,

                            raw:
                                data
                        }
                    }
                )
            );


            return data;

        }
        catch (error) {


            window.dispatchEvent(
                new CustomEvent(
                    "sabino:inna:error",
                    {
                        detail: {
                            locale,
                            pergunta,

                            message:
                                String(
                                    error?.message
                                    ||
                                    error
                                )
                        }
                    }
                )
            );


            throw error;
        }
    }


    /*
       Mudou idioma na Sabino.AI
       -> INNA muda imediatamente.
    */

    window.addEventListener(
        "sabino:languagechange",
        event => {

            setActiveLocale(
                event.detail?.locale
                ||
                getLocale()
            );
        }
    );


    /*
       API pública global.
    */

    window.SabinoINNA = {

        version:
            VERSION,

        get locale() {
            return currentLocale();
        },

        getLocale,

        normalizeLocale,

        setLocale:
            setActiveLocale,

        ask
    };


    /*
       Inicialização.
    */

    setActiveLocale(
        getLocale()
    );


    console.info(
        "[Sabino.INNA]",
        "Global client ready",
        currentLocale()
    );

})();
