(function () {

    "use strict";

    const OPTIONS = [

        {
            locale: "pt-BR",
            label: "Português Brasil",
            currency: "BRL",
            symbol: "R$"
        },

        {
            locale: "en-US",
            label: "English US",
            currency: "USD",
            symbol: "$"
        },

        {
            locale: "en-GB",
            label: "English UK",
            currency: "GBP",
            symbol: "£"
        },

        {
            locale: "es-ES",
            label: "Español",
            currency: "EUR",
            symbol: "€"
        },

        {
            locale: "de-DE",
            label: "Deutsch",
            currency: "EUR",
            symbol: "€"
        },

        {
            locale: "fr-FR",
            label: "Français",
            currency: "EUR",
            symbol: "€"
        },

        {
            locale: "it-IT",
            label: "Italiano",
            currency: "EUR",
            symbol: "€"
        },

        {
            locale: "ru-RU",
            label: "Русский",
            currency: "RUB",
            symbol: "₽"
        },

        {
            locale: "ar-SA",
            label: "العربية",
            currency: "SAR",
            symbol: "ر.س"
        },

        {
            locale: "ro-RO",
            label: "Română",
            currency: "RON",
            symbol: "lei"
        },

        {
            locale: "uk-UA",
            label: "Українська",
            currency: "UAH",
            symbol: "₴"
        },

        {
            locale: "de-CH",
            label: "Schweiz",
            currency: "CHF",
            symbol: "CHF"
        }

    ];


    const STORAGE_LANGUAGE =
        "sabino_language";

    const STORAGE_MANUAL =
        "sabino_language_manual";

    const STORAGE_SOURCE =
        "sabino_language_source";


    function currentManualLocale() {

        const source =
            localStorage.getItem(
                STORAGE_SOURCE
            );

        if (source !== "manual") {
            return null;
        }

        return localStorage.getItem(
            STORAGE_MANUAL
        );

    }


    function selectedOption() {

        const locale =
            currentManualLocale();

        if (!locale) {
            return null;
        }

        return OPTIONS.find(
            item =>
                item.locale === locale
        ) || null;

    }


    function chooseAutomatic() {

        localStorage.removeItem(
            STORAGE_MANUAL
        );

        localStorage.removeItem(
            STORAGE_SOURCE
        );

        localStorage.removeItem(
            STORAGE_LANGUAGE
        );

        /*
         * O navegador volta a ser a fonte.
         * Nenhuma limitação é aplicada a navigator.language.
         */

        window.location.reload();

    }


    function chooseLocale(locale) {

        const option =
            OPTIONS.find(
                item =>
                    item.locale === locale
            );

        if (!option) {
            return;
        }


        localStorage.setItem(
            STORAGE_MANUAL,
            locale
        );

        localStorage.setItem(
            STORAGE_SOURCE,
            "manual"
        );

        localStorage.setItem(
            STORAGE_LANGUAGE,
            locale
        );


        /*
         * Reload garante que:
         *
         * SabinoLocale
         * SabinoCurrency
         * Money Runtime
         * Global i18n
         *
         * iniciem usando o mesmo locale.
         */

        window.location.reload();

    }


    function createOption(item) {

        const button =
            document.createElement(
                "button"
            );

        button.type =
            "button";

        button.className =
            "sabino-lang-switcher-option";

        button.dataset.locale =
            item.locale;


        const left =
            document.createElement(
                "span"
            );

        left.className =
            "sabino-lang-option-left";


        const check =
            document.createElement(
                "span"
            );

        check.className =
            "sabino-lang-option-check";


        const current =
            currentManualLocale();

        check.textContent =
            current === item.locale
                ? "✓"
                : "";


        const label =
            document.createElement(
                "span"
            );

        label.className =
            "sabino-lang-option-label";

        label.textContent =
            item.label;

        label.dir =
            item.locale === "ar-SA"
                ? "rtl"
                : "auto";


        left.appendChild(
            check
        );

        left.appendChild(
            label
        );


        const money =
            document.createElement(
                "span"
            );

        money.className =
            "sabino-lang-option-money";

        money.textContent =
            item.currency +
            " · " +
            item.symbol;


        button.appendChild(
            left
        );

        button.appendChild(
            money
        );


        button.addEventListener(
            "click",
            function () {

                chooseLocale(
                    item.locale
                );

            }
        );


        return button;

    }


    function build() {

        /*
         * Evita duplicidade.
         */

        if (
            document.getElementById(
                "sabinoLanguageSwitcher"
            )
        ) {
            return;
        }


        const root =
            document.createElement(
                "div"
            );

        root.id =
            "sabinoLanguageSwitcher";

        root.className =
            "sabino-lang-switcher";


        const trigger =
            document.createElement(
                "button"
            );

        trigger.id =
            "sabinoLanguageTrigger";

        trigger.type =
            "button";

        trigger.className =
            "sabino-lang-trigger";

        trigger.setAttribute(
            "aria-haspopup",
            "true"
        );

        trigger.setAttribute(
            "aria-expanded",
            "false"
        );


        const globe =
            document.createElement(
                "span"
            );

        globe.className =
            "sabino-lang-globe";

        globe.textContent =
            "🌐";


        const triggerText =
            document.createElement(
                "span"
            );

        triggerText.className =
            "sabino-lang-trigger-text";


        const selected =
            selectedOption();


        if (selected) {

            triggerText.textContent =
                selected.label;

        }
        else {

            triggerText.textContent =
                "Idioma";

        }


        const chevron =
            document.createElement(
                "span"
            );

        chevron.className =
            "sabino-lang-chevron";

        chevron.textContent =
            "⌄";


        trigger.appendChild(
            globe
        );

        trigger.appendChild(
            triggerText
        );

        trigger.appendChild(
            chevron
        );


        const panel =
            document.createElement(
                "div"
            );

        panel.id =
            "sabinoLanguagePanel";

        panel.className =
            "sabino-lang-panel";

        panel.hidden =
            true;


        const header =
            document.createElement(
                "div"
            );

        header.className =
            "sabino-lang-panel-header";


        const title =
            document.createElement(
                "strong"
            );

        title.textContent =
            "Idioma";


        const subtitle =
            document.createElement(
                "span"
            );

        subtitle.textContent =
            "Idioma e moeda da plataforma";


        header.appendChild(
            title
        );

        header.appendChild(
            subtitle
        );


        const automatic =
            document.createElement(
                "button"
            );

        automatic.type =
            "button";

        automatic.className =
            "sabino-lang-auto";


        const autoLeft =
            document.createElement(
                "span"
            );

        autoLeft.textContent =
            currentManualLocale()
                ? "Automático do navegador"
                : "✓ Automático do navegador";


        const browserLocale =
            (
                navigator.language ||
                "pt-BR"
            );


        const autoRight =
            document.createElement(
                "span"
            );

        autoRight.className =
            "sabino-lang-browser-locale";

        autoRight.textContent =
            browserLocale;


        automatic.appendChild(
            autoLeft
        );

        automatic.appendChild(
            autoRight
        );


        automatic.addEventListener(
            "click",
            chooseAutomatic
        );


        const divider =
            document.createElement(
                "div"
            );

        divider.className =
            "sabino-lang-divider";


        const list =
            document.createElement(
                "div"
            );

        list.className =
            "sabino-lang-options";


        OPTIONS.forEach(
            function (item) {

                list.appendChild(
                    createOption(item)
                );

            }
        );


        panel.appendChild(
            header
        );

        panel.appendChild(
            automatic
        );

        panel.appendChild(
            divider
        );

        panel.appendChild(
            list
        );


        root.appendChild(
            trigger
        );

        root.appendChild(
            panel
        );

        const mount =
            document.getElementById(
                "sabinoLanguageMount"
            );

        if (mount) {

            mount.appendChild(
                root
            );

        }
        else {
            const profile = document.querySelector("header.topbar > .profile");
            if (profile) {
                const header = profile.parentElement;
                header.classList.add("sabino-language-header");
                header.insertBefore(root, profile);
            } else {
                document.body.appendChild(root);
            }
        }


        function closePanel() {

            panel.hidden =
                true;

            trigger.setAttribute(
                "aria-expanded",
                "false"
            );

            root.classList.remove(
                "open"
            );

        }


        function openPanel() {

            panel.hidden =
                false;

            trigger.setAttribute(
                "aria-expanded",
                "true"
            );

            root.classList.add(
                "open"
            );

        }


        trigger.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                if (panel.hidden) {
                    openPanel();
                }
                else {
                    closePanel();
                }

            }
        );


        panel.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

            }
        );


        document.addEventListener(
            "click",
            closePanel
        );


        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                    "Escape"
                ) {
                    closePanel();
                }

            }
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            build,
            {
                once: true
            }
        );

    }
    else {

        build();

    }

})();
