/* ============================================================
   SABINO.AI - MONTH PEAK BAR FINAL V2

   Mantém a cor dourada original.
   Somente o maior gasto recebe laranja.
   ============================================================ */

(function () {

    "use strict";

    if (window.SabinoMonthPeakBarFinalV2) {
        return;
    }

    window.SabinoMonthPeakBarFinalV2 = true;


    function normalize(value) {

        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }


    function findMonthCard() {

        const headings =
            Array.from(
                document.querySelectorAll(
                    "h1,h2,h3,h4"
                )
            );


        const heading =
            headings.find(function (element) {

                const text =
                    normalize(
                        element.textContent
                    );


                return (
                    text === "gastos por mes" ||
                    text.includes("gastos por mes")
                );

            });


        if (!heading) {
            return null;
        }


        let node =
            heading;


        while (
            node &&
            node !== document.body
        ) {

            const rect =
                node.getBoundingClientRect();


            const monthLabels =
                Array.from(
                    node.querySelectorAll("*")
                )
                .filter(function (element) {

                    const text =
                        String(
                            element.textContent ||
                            ""
                        )
                        .trim();


                    return (
                        /^.{2,12}\/\d{2}$/u.test(text)
                    );

                });


            if (
                rect.width > 350 &&
                rect.height > 250 &&
                monthLabels.length >= 4
            ) {

                return node;
            }


            node =
                node.parentElement;
        }


        return null;
    }


    function parseMoney(text) {

        text =
            String(text || "")
                .replace(/\s/g, "");


        /*
         * pt-BR:
         * R$3.290,00
         */

        const match =
            text.match(
                /(?:R\$|[$€£₽₴]|CHF|lei)?\s*([\d.]+,\d{2})/i
            );


        if (!match) {
            return null;
        }


        const normalized =
            match[1]
                .replace(/\./g, "")
                .replace(",", ".");


        const value =
            Number(normalized);


        return (
            Number.isFinite(value)
                ? value
                : null
        );
    }


    function getMonthLabels(card) {

        return Array.from(
            card.querySelectorAll("*")
        )
        .filter(function (element) {

            if (
                element.children.length > 0
            ) {

                return false;
            }


            const text =
                String(
                    element.textContent ||
                    ""
                )
                .trim();


            return (
                /^.{2,12}\/\d{2}$/u.test(text)
            );

        });
    }


    function findColumn(
        card,
        monthLabel
    ) {

        let node =
            monthLabel.parentElement;


        for (
            let level = 0;
            node &&
            node !== card &&
            level < 7;
            level += 1
        ) {

            const rect =
                node.getBoundingClientRect();


            const moneyElements =
                Array.from(
                    node.querySelectorAll("*")
                )
                .filter(function (element) {

                    if (
                        element.children.length > 0
                    ) {

                        return false;
                    }


                    return (
                        parseMoney(
                            element.textContent
                        ) !== null
                    );

                });


            if (
                rect.width >= 35 &&
                rect.width <= 160 &&
                rect.height >= 80 &&
                moneyElements.length >= 1
            ) {

                return {
                    container: node,
                    moneyElements: moneyElements
                };
            }


            node =
                node.parentElement;
        }


        return null;
    }


    function findValueElement(
        monthLabel,
        moneyElements
    ) {

        const monthRect =
            monthLabel.getBoundingClientRect();


        const candidates =
            moneyElements
                .map(function (element) {

                    return {
                        element: element,
                        value:
                            parseMoney(
                                element.textContent
                            ),
                        rect:
                            element.getBoundingClientRect()
                    };

                })
                .filter(function (item) {

                    return (
                        item.value !== null &&
                        item.rect.bottom <
                        monthRect.top
                    );

                });


        if (!candidates.length) {
            return null;
        }


        /*
         * Valor mais próximo da barra/mês.
         */

        candidates.sort(
            function (a, b) {

                return (
                    b.rect.top -
                    a.rect.top
                );

            }
        );


        return candidates[0];
    }


    function isVisibleBarCandidate(
        element,
        monthLabel
    ) {

        const rect =
            element.getBoundingClientRect();


        const monthRect =
            monthLabel.getBoundingClientRect();


        if (
            rect.width < 18 ||
            rect.width > 110 ||
            rect.height < 25 ||
            rect.height > 500
        ) {

            return false;
        }


        if (
            rect.top >= monthRect.top ||
            rect.bottom >
            monthRect.top + 8
        ) {

            return false;
        }


        if (
            element.children.length > 3
        ) {

            return false;
        }


        if (
            element.tagName &&
            element.tagName.toLowerCase() ===
            "rect"
        ) {

            return true;
        }


        const style =
            window.getComputedStyle(
                element
            );


        const hasBackground =
            (
                style.backgroundColor &&
                style.backgroundColor !==
                "rgba(0, 0, 0, 0)" &&
                style.backgroundColor !==
                "transparent"
            ) ||
            (
                style.backgroundImage &&
                style.backgroundImage !==
                "none"
            );


        const classText =
            normalize(
                element.className &&
                element.className.baseVal
                    ? element.className.baseVal
                    : element.className
            );


        return (
            hasBackground ||
            classText.includes("bar") ||
            classText.includes("column")
        );
    }


    /* SABINO_MONTH_PEAK_BAR_EXACT_V3 */

    function cleanupPreviousPeak(card) {

        const previous =
            Array.from(
                card.querySelectorAll(
                    '[data-sabino-peak="true"]'
                )
            );


        previous.forEach(
            function (element) {

                /*
                 * Restaura o container que recebeu
                 * laranja incorretamente no V2.
                 */

                if (
                    element.dataset &&
                    element.dataset.sabinoOriginalSaved
                ) {

                    if (
                        element.dataset.sabinoOriginalBackground
                    ) {

                        element.style.background =
                            element.dataset
                                .sabinoOriginalBackground;

                    }
                    else {

                        element.style.removeProperty(
                            "background"
                        );
                    }


                    if (
                        element.dataset
                            .sabinoOriginalBackgroundColor
                    ) {

                        element.style.backgroundColor =
                            element.dataset
                                .sabinoOriginalBackgroundColor;

                    }
                    else {

                        element.style.removeProperty(
                            "background-color"
                        );
                    }


                    if (
                        element.dataset
                            .sabinoOriginalBoxShadow
                    ) {

                        element.style.boxShadow =
                            element.dataset
                                .sabinoOriginalBoxShadow;

                    }
                    else {

                        element.style.removeProperty(
                            "box-shadow"
                        );
                    }


                    if (
                        element.tagName &&
                        element.tagName
                            .toLowerCase() ===
                            "rect"
                    ) {

                        const fill =
                            element.dataset
                                .sabinoOriginalFill;


                        if (fill) {

                            element.setAttribute(
                                "fill",
                                fill
                            );

                        }
                        else {

                            element.removeAttribute(
                                "fill"
                            );
                        }
                    }
                }


                element.removeAttribute(
                    "data-sabino-peak"
                );

            }
        );
    }


    function findBar(
        column,
        monthLabel
    ) {

        const monthRect =
            monthLabel.getBoundingClientRect();


        const columnRect =
            column.getBoundingClientRect();


        /*
         * IMPORTANTE:
         * nunca considerar o próprio container.
         *
         * Procuramos apenas elementos internos.
         */

        const elements =
            Array.from(
                column.querySelectorAll("*")
            );


        const candidates =
            elements
                .map(
                    function (element) {

                        const rect =
                            element.getBoundingClientRect();


                        const style =
                            window.getComputedStyle(
                                element
                            );


                        const tag =
                            String(
                                element.tagName ||
                                ""
                            )
                            .toLowerCase();


                        const text =
                            String(
                                element.textContent ||
                                ""
                            )
                            .trim();


                        const visibleBackground =
                            (
                                style.backgroundColor &&
                                style.backgroundColor !==
                                    "rgba(0, 0, 0, 0)" &&
                                style.backgroundColor !==
                                    "transparent"
                            )
                            ||
                            (
                                style.backgroundImage &&
                                style.backgroundImage !==
                                    "none"
                            );


                        const svgRect =
                            tag === "rect";


                        return {
                            element,
                            rect,
                            text,
                            visibleBackground,
                            svgRect
                        };

                    }
                )
                .filter(
                    function (item) {

                        const rect =
                            item.rect;


                        /*
                         * Dimensões esperadas da barra.
                         */

                        if (
                            rect.width < 20 ||
                            rect.width > 110 ||
                            rect.height < 25 ||
                            rect.height > 450
                        ) {

                            return false;
                        }


                        /*
                         * Não aceitar novamente o wrapper
                         * que ocupa praticamente toda a
                         * altura da coluna.
                         */

                        if (
                            columnRect.height > 0 &&
                            rect.height >=
                                columnRect.height * 0.90
                        ) {

                            return false;
                        }


                        /*
                         * A barra fica acima do rótulo
                         * Abr/26, Mai/26, Ago/26 etc.
                         */

                        if (
                            rect.top >=
                                monthRect.top
                        ) {

                            return false;
                        }


                        /*
                         * Parte inferior deve ficar próxima
                         * da linha de base do gráfico.
                         */

                        const distance =
                            monthRect.top -
                            rect.bottom;


                        if (
                            distance < -8 ||
                            distance > 80
                        ) {

                            return false;
                        }


                        /*
                         * Evitar pegar textos/labels.
                         */

                        if (
                            item.text &&
                            item.text.length > 4
                        ) {

                            return false;
                        }


                        return (
                            item.visibleBackground ||
                            item.svgRect
                        );

                    }
                );


        if (!candidates.length) {
            return null;
        }


        /*
         * Preferimos:
         *
         * 1. barra mais próxima da linha de base
         * 2. maior altura entre essas candidatas
         */

        candidates.sort(
            function (a, b) {

                const aDistance =
                    Math.abs(
                        monthRect.top -
                        a.rect.bottom
                    );


                const bDistance =
                    Math.abs(
                        monthRect.top -
                        b.rect.bottom
                    );


                if (
                    Math.abs(
                        aDistance -
                        bDistance
                    ) > 4
                ) {

                    return (
                        aDistance -
                        bDistance
                    );
                }


                return (
                    b.rect.height -
                    a.rect.height
                );

            }
        );


        return (
            candidates[0].element
        );
    }


    function saveOriginal(bar) {

        if (
            bar.dataset &&
            !bar.dataset.sabinoOriginalSaved
        ) {

            bar.dataset.sabinoOriginalSaved =
                "1";


            bar.dataset.sabinoOriginalBackground =
                bar.style.background || "";


            bar.dataset.sabinoOriginalBackgroundColor =
                bar.style.backgroundColor || "";


            bar.dataset.sabinoOriginalBoxShadow =
                bar.style.boxShadow || "";


            if (
                bar.tagName &&
                bar.tagName.toLowerCase() ===
                "rect"
            ) {

                bar.dataset.sabinoOriginalFill =
                    bar.getAttribute("fill") ||
                    "";
            }
        }
    }


    function restoreOriginal(bar) {

        if (
            !bar.dataset ||
            !bar.dataset.sabinoOriginalSaved
        ) {

            return;
        }


        if (
            bar.dataset.sabinoOriginalBackground
        ) {

            bar.style.background =
                bar.dataset
                    .sabinoOriginalBackground;

        }
        else {

            bar.style.removeProperty(
                "background"
            );
        }


        if (
            bar.dataset.sabinoOriginalBackgroundColor
        ) {

            bar.style.backgroundColor =
                bar.dataset
                    .sabinoOriginalBackgroundColor;

        }
        else {

            bar.style.removeProperty(
                "background-color"
            );
        }


        if (
            bar.dataset.sabinoOriginalBoxShadow
        ) {

            bar.style.boxShadow =
                bar.dataset
                    .sabinoOriginalBoxShadow;

        }
        else {

            bar.style.removeProperty(
                "box-shadow"
            );
        }


        if (
            bar.tagName &&
            bar.tagName.toLowerCase() ===
            "rect"
        ) {

            const fill =
                bar.dataset
                    .sabinoOriginalFill;


            if (fill) {

                bar.setAttribute(
                    "fill",
                    fill
                );

            }
            else {

                bar.removeAttribute(
                    "fill"
                );
            }
        }


        bar.removeAttribute(
            "data-sabino-peak"
        );
    }


    function makeOrange(bar) {

        saveOriginal(
            bar
        );


        bar.setAttribute(
            "data-sabino-peak",
            "true"
        );


        if (
            bar.tagName &&
            bar.tagName.toLowerCase() ===
            "rect"
        ) {

            bar.setAttribute(
                "fill",
                "#F59E0B"
            );

            return;
        }


        bar.style.setProperty(
            "background",
            "linear-gradient(180deg, #FFB347 0%, #F59E0B 100%)",
            "important"
        );


        bar.style.setProperty(
            "background-color",
            "#F59E0B",
            "important"
        );


        bar.style.setProperty(
            "box-shadow",
            "0 8px 18px rgba(245,158,11,.18)",
            "important"
        );
    }


    function apply() {

        const card =
            findMonthCard();


        if (!card) {
            return false;
        }


        /*
         * Remove primeiro o retângulo laranja
         * errado criado pelo V2.
         */

        cleanupPreviousPeak(
            card
        );


        const months =
            getMonthLabels(
                card
            );


        const data = [];


        months.forEach(
            function (monthLabel) {

                const columnInfo =
                    findColumn(
                        card,
                        monthLabel
                    );


                if (!columnInfo) {
                    return;
                }


                const valueInfo =
                    findValueElement(
                        monthLabel,
                        columnInfo.moneyElements
                    );


                if (!valueInfo) {
                    return;
                }


                const bar =
                    findBar(
                        columnInfo.container,
                        monthLabel
                    );


                if (!bar) {
                    return;
                }


                saveOriginal(
                    bar
                );


                data.push({
                    month:
                        monthLabel.textContent
                            .trim(),
                    value:
                        valueInfo.value,
                    bar:
                        bar
                });

            }
        );


        if (!data.length) {
            return false;
        }


        /*
         * Primeiro restaura todas.
         * Isso preserva exatamente o dourado
         * original do projeto.
         */

        data.forEach(
            function (item) {

                restoreOriginal(
                    item.bar
                );

            }
        );


        const maxValue =
            Math.max.apply(
                null,
                data.map(
                    function (item) {

                        return item.value;

                    }
                )
            );


        const peak =
            data.find(
                function (item) {

                    return (
                        item.value ===
                        maxValue
                    );

                }
            );


        if (!peak) {
            return false;
        }


        makeOrange(
            peak.bar
        );


        card.setAttribute(
            "data-sabino-month-peak",
            peak.month
        );


        return true;
    }


    function boot() {

        apply();


        [
            100,
            300,
            700,
            1200,
            2000
        ]
        .forEach(
            function (delay) {

                window.setTimeout(
                    apply,
                    delay
                );

            }
        );
    }


    if (
        document.readyState ===
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


    window.addEventListener(
        "load",
        boot
    );


    window.addEventListener(
        "sabino:finance-data-updated",
        boot
    );

})();
