document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        const toast =
            document.getElementById(
                "inna-central-toast"
            );


        function notify(message) {

            if (!toast) {
                return;
            }


            toast.textContent =
                message;


            toast.classList.add(
                "show"
            );


            clearTimeout(
                toast._timer
            );


            toast._timer =
                setTimeout(
                    () => {

                        toast.classList.remove(
                            "show"
                        );

                    },
                    2800
                );

        }


        document
            .querySelectorAll(
                "[data-central-action]"
            )
            .forEach(
                element => {

                    element.addEventListener(
                        "click",
                        () => {

                            const action =
                                element.dataset
                                    .centralAction;


                            if (action === "inna") {

                                notify(
                                    "A INNA Central será conectada ao contexto global real na integração do backend."
                                );

                                return;

                            }


                            if (
                                action ===
                                "financial-intelligence"
                            ) {

                                window.location.href =
                                    "/plataforma/financeiro?view=intelligence";

                                return;

                            }


                            if (action === "quality") {

                                notify(
                                    "A Plataforma Qualidade & Confiabilidade está registrada na arquitetura e será integrada em uma próxima etapa."
                                );

                                return;

                            }


                            if (action === "industry") {

                                notify(
                                    "A Plataforma Indústria 4.0 está registrada na arquitetura e será construída posteriormente."
                                );

                                return;

                            }


                            if (action === "career") {

                                notify(
                                    "A Plataforma de Carreira está registrada na arquitetura e será integrada posteriormente."
                                );

                            }

                        }
                    );

                }
            );


        console.log(
            "SABINO_INNA_CENTRAL_V3=READY"
        );

    }
);

/* =========================================================
   SABINO_FORCE_FINANCIAL_NAVIGATION_V1
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const financialButton =
            document.getElementById(
                "open-financial-platform"
            );


        if (financialButton) {

            financialButton.addEventListener(
                "click",
                event => {

                    event.preventDefault();

                    event.stopPropagation();

                    window.location.assign(
                        "/plataforma/financeiro"
                    );

                }
            );

        }


        console.log(
            "SABINO_FORCE_FINANCIAL_NAVIGATION_V1=READY"
        );

    }
);

