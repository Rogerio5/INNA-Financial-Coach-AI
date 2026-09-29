document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        document.body.classList.add(
            "sab-home-v6-root"
        );


        const main =
            document.querySelector(
                "main"
            )
            ||
            document.body;


        main.classList.add(
            "sab-home-v6-main"
        );


        function normalize(value) {

            return (
                value ||
                ""
            )
            .replace(
                /\s+/g,
                " "
            )
            .trim()
            .toLowerCase();

        }


        function findByText(text) {

            const expected =
                normalize(text);


            const candidates =
                document.querySelectorAll(
                    "h1,h2,h3,h4,p,span,strong"
                );


            for (
                const element
                of candidates
            ) {

                const value =
                    normalize(
                        element.textContent
                    );


                if (
                    value.includes(
                        expected
                    )
                ) {

                    return element;

                }

            }


            return null;

        }


        function findSection(text) {

            const target =
                findByText(
                    text
                );


            if (!target) {
                return null;
            }


            return (
                target.closest(
                    "section"
                )
                ||
                target.closest(
                    "article"
                )
                ||
                target.parentElement
            );

        }


        function upgradeCards(section) {

            if (!section) {
                return;
            }


            const headings =
                Array.from(
                    section.querySelectorAll(
                        "h3,h4"
                    )
                );


            const cards = [];


            headings.forEach(
                heading => {

                    let card =
                        heading.closest(
                            "article"
                        );


                    if (!card) {

                        card =
                            heading.parentElement;

                    }


                    if (
                        !card ||
                        card === section
                    ) {

                        return;

                    }


                    if (
                        !cards.includes(
                            card
                        )
                    ) {

                        cards.push(
                            card
                        );

                    }

                }
            );


            if (
                cards.length < 2
            ) {

                return;
            }


            cards.forEach(
                card => {

                    card.classList.add(
                        "sab-home-v6-card"
                    );

                }
            );


            const groups =
                new Map();


            cards.forEach(
                card => {

                    const parent =
                        card.parentElement;


                    if (!parent) {
                        return;
                    }


                    const current =
                        groups.get(
                            parent
                        )
                        ||
                        [];


                    current.push(
                        card
                    );


                    groups.set(
                        parent,
                        current
                    );

                }
            );


            let bestParent =
                null;


            let bestCards =
                [];


            groups.forEach(
                (
                    groupedCards,
                    parent
                ) => {

                    if (
                        groupedCards.length >
                        bestCards.length
                    ) {

                        bestParent =
                            parent;


                        bestCards =
                            groupedCards;

                    }

                }
            );


            if (
                bestParent &&
                bestCards.length >= 2
            ) {

                bestParent.classList.add(
                    "sab-home-v6-grid"
                );


                bestParent.setAttribute(
                    "data-sab-count",
                    String(
                        Math.min(
                            bestCards.length,
                            4
                        )
                    )
                );

            }

        }


        /* =================================================
           HERO
           ================================================= */

        const hero =
            findSection(
                "Plataforma Inteligente"
            );


        if (hero) {

            hero.classList.add(
                "sab-home-v6-hero"
            );


            const images =
                Array.from(
                    hero.querySelectorAll(
                        "img"
                    )
                );


            const innaImage =
                images.find(
                    image => {

                        const data =
                            (
                                image.src +
                                " " +
                                image.alt
                            )
                            .toLowerCase();


                        return (
                            data.includes(
                                "inna"
                            )
                            ||
                            data.includes(
                                "hero"
                            )
                        );

                    }
                )
                ||
                images.find(
                    image =>
                        !(
                            image.src ||
                            ""
                        )
                        .toLowerCase()
                        .includes(
                            "logo"
                        )
                );


            if (innaImage) {

                innaImage.classList.add(
                    "sab-home-v6-inna"
                );


                const wrapper =
                    innaImage.parentElement;


                if (wrapper) {

                    wrapper.classList.add(
                        "sab-home-v6-inna-wrap"
                    );

                }

            }

        }


        /* =================================================
           COMO FUNCIONA
           ================================================= */

        const how =
            findSection(
                "Como funciona"
            );


        if (how) {

            how.classList.add(
                "sab-home-v6-section",
                "sab-home-v6-how"
            );


            upgradeCards(
                how
            );

        }


        /* =================================================
           BENEFICIOS / OPERACAO
           ================================================= */

        const intelligence =
            findSection(
                "Inteligência aplicada"
            );


        if (intelligence) {

            intelligence.classList.add(
                "sab-home-v6-section",
                "sab-home-v6-benefits"
            );


            upgradeCards(
                intelligence
            );

        }


        /* =================================================
           MODULOS
           ================================================= */

        const modules =
            findSection(
                "Soluções especializadas"
            );


        if (modules) {

            modules.classList.add(
                "sab-home-v6-section",
                "sab-home-v6-modules"
            );


            upgradeCards(
                modules
            );

        }


        /* =================================================
           NEWSLETTER
           ================================================= */

        const newsletter =
            findSection(
                "Receba novidades"
            );


        if (newsletter) {

            newsletter.classList.add(
                "sab-home-v6-newsletter"
            );

        }


        console.log(
            "SABINO_HOME_V6_RESPONSIVE=READY"
        );

    }
);
