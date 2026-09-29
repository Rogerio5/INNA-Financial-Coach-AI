document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    /*
     * GATE:
     * sem Go Live, não acessa esta área.
     */

    const active =
        localStorage.getItem(
            "inna_platform_active"
        ) === "true";


    if (!active) {

        window.location.replace(
            "/jornada"
        );

        return;

    }


    function getJson(key) {

        try {

            const value =
                localStorage.getItem(key);

            return value
                ? JSON.parse(value)
                : null;

        }
        catch {

            return null;

        }

    }


    const configuration =
        getJson(
            "inna_solution_config"
        );


    function setText(id, value) {

        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                value || "-";
        }

    }


    function labelOf(value) {

        if (
            value &&
            typeof value === "object"
        ) {

            return (
                value.label ||
                value.value ||
                "-"
            );

        }

        return value || "-";

    }


    const modules =
        configuration?.modules || [];


    const integrations =
        configuration?.integrations || [];


    setText(
        "active-module-count",
        `${modules.length} módulos`
    );


    setText(
        "active-kpi-modules",
        String(modules.length)
    );


    setText(
        "active-kpi-users",
        labelOf(
            configuration?.users
        )
    );


    setText(
        "active-kpi-rag",
        labelOf(
            configuration?.rag
        )
    );


    setText(
        "active-kpi-integrations",
        String(
            integrations.length
        )
    );


    setText(
        "active-solution-id",
        localStorage.getItem(
            "inna_solution_id"
        ) || "-"
    );


    const activatedAt =
        localStorage.getItem(
            "inna_platform_activated_at"
        );


    const review =
        activatedAt
            ? new Date(activatedAt)
            : new Date();


    review.setDate(
        review.getDate() + 30
    );


    setText(
        "active-next-review",
        review.toLocaleDateString(
            "pt-BR"
        )
    );


    const moduleList =
        document.getElementById(
            "active-module-list"
        );


    if (moduleList) {

        moduleList.innerHTML = "";


        modules.forEach(
            (module, index) => {

                const item =
                    document.createElement(
                        "div"
                    );


                item.innerHTML = `
                    <span>${String(index + 1).padStart(2, "0")}</span>

                    <strong>
                        ${module}
                    </strong>

                    <small>
                        ● Ativo
                    </small>
                `;


                moduleList.appendChild(
                    item
                );

            }
        );

    }

});
