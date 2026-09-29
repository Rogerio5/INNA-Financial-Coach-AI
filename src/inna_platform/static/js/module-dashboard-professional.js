document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    const isEducation =
        document.body.classList.contains(
            "ef2-page"
        );

    const isSecurity =
        document.body.classList.contains(
            "sf-page"
        );


    if (!isEducation && !isSecurity) {
        return;
    }


    const moduleConfig =
        isEducation
            ? {
                key:
                    "education",

                name:
                    "Educação Financeira",

                quality:
                    98,

                legacyToolbar:
                    ".ef3-toolbar",

                refreshSelector:
                    "#ef3-refresh",

                exportName:
                    "educacao-financeira",

                exportRows: [
                    ["Usuários", "84"],
                    ["Diagnósticos", "342"],
                    ["Alertas", "18"],
                    ["Metas financeiras", "126"],
                    ["Consultas INNA", "519"],
                    ["Saúde do módulo", "96%"],
                    ["Qualidade dos dados", "98%"]
                ]
            }
            : {
                key:
                    "security",

                name:
                    "Segurança Financeira",

                quality:
                    97,

                legacyToolbar:
                    ".sf-toolbar",

                refreshSelector:
                    "#sf-refresh",

                exportName:
                    "seguranca-financeira",

                exportRows: [
                    ["Eventos monitorados", "12.840"],
                    ["Alertas ativos", "27"],
                    ["Alertas detectados", "184"],
                    ["Incidentes críticos", "3"],
                    ["HITL pendente", "4"],
                    ["Saúde do módulo", "97%"],
                    ["Qualidade dos dados", "97%"]
                ]
            };


    const STORAGE_PREFIX =
        `sabino_${moduleConfig.key}_professional_`;


    const syncKey =
        `${STORAGE_PREFIX}last_sync`;


    const periodKey =
        `${STORAGE_PREFIX}period`;


    const autoRefreshKey =
        `${STORAGE_PREFIX}auto_refresh`;


    let autoRefreshTimer =
        null;


    let lastFocusedElement =
        null;


    /* ======================================================
       HELPERS
       ====================================================== */

    function formatTime(date) {

        return date.toLocaleTimeString(
            "pt-BR",
            {
                hour:
                    "2-digit",

                minute:
                    "2-digit",

                second:
                    "2-digit"
            }
        );

    }


    function formatDateTime(date) {

        return date.toLocaleString(
            "pt-BR",
            {
                day:
                    "2-digit",

                month:
                    "2-digit",

                year:
                    "numeric",

                hour:
                    "2-digit",

                minute:
                    "2-digit",

                second:
                    "2-digit"
            }
        );

    }


    function readLastSync() {

        const saved =
            localStorage.getItem(
                syncKey
            );


        if (!saved) {

            const now =
                new Date();


            localStorage.setItem(
                syncKey,
                now.toISOString()
            );


            return now;

        }


        const date =
            new Date(
                saved
            );


        return Number.isNaN(
            date.getTime()
        )
            ? new Date()
            : date;

    }


    function saveLastSync() {

        const now =
            new Date();


        localStorage.setItem(
            syncKey,
            now.toISOString()
        );


        return now;

    }


    function notify(message) {

        let toast =
            document.getElementById(
                "module-prof-toast"
            );


        if (!toast) {

            toast =
                document.createElement(
                    "div"
                );


            toast.id =
                "module-prof-toast";


            toast.className =
                "module-prof-toast";


            toast.setAttribute(
                "role",
                "status"
            );


            document.body.appendChild(
                toast
            );

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


    /* ======================================================
       TOOLBAR PROFISSIONAL
       ====================================================== */

    const viewController =
        document.querySelector(
            ".module-view-controller"
        );


    const fallbackAnchor =
        document.querySelector(
            ".ef2-demo, .sf-demo"
        );


    const toolbarAnchor =
        viewController ||
        fallbackAnchor;


    if (
        toolbarAnchor &&
        !document.getElementById(
            "module-professional-toolbar"
        )
    ) {

        toolbarAnchor.insertAdjacentHTML(
            "afterend",
            `
            <section
                class="module-professional-toolbar"
                id="module-professional-toolbar"
            >

                <div class="module-prof-period-area">

                    <small>
                        Período global
                    </small>

                    <div class="module-prof-periods">

                        <button
                            type="button"
                            data-prof-period="today"
                        >
                            Hoje
                        </button>

                        <button
                            type="button"
                            data-prof-period="7d"
                        >
                            7 dias
                        </button>

                        <button
                            type="button"
                            data-prof-period="30d"
                        >
                            30 dias
                        </button>

                        <button
                            type="button"
                            data-prof-period="90d"
                        >
                            90 dias
                        </button>

                        <button
                            type="button"
                            data-prof-period="custom"
                        >
                            Personalizado
                        </button>

                    </div>

                </div>


                <div class="module-prof-metadata">

                    <div
                        class="module-prof-meta"
                        data-prof-tooltip="Percentual demonstrativo de completude, consistência e disponibilidade dos dados."
                    >

                        <small>
                            Qualidade dos dados
                        </small>

                        <strong>
                            ${moduleConfig.quality}%
                        </strong>

                    </div>


                    <div
                        class="module-prof-meta"
                        data-prof-tooltip="Horário da última sincronização conhecida desta interface."
                    >

                        <small>
                            Última sincronização
                        </small>

                        <strong id="module-prof-last-sync">
                            -
                        </strong>

                    </div>


                    <div class="module-prof-meta">

                        <small>
                            Estado dos dados
                        </small>

                        <strong
                            id="module-prof-data-status"
                            class="ready"
                        >
                            ● Atualizado
                        </strong>

                    </div>


                    <div class="module-prof-meta">

                        <small>
                            Perfil da interface
                        </small>

                        <strong>
                            Demo
                        </strong>

                    </div>


                    <div class="module-prof-meta">

                        <small>
                            Auditoria
                        </small>

                        <strong>
                            Preparada
                        </strong>

                    </div>

                </div>


                <div class="module-prof-actions">

                    <button
                        type="button"
                        id="module-prof-auto-refresh"
                        class="module-prof-action"
                    >
                        Auto: desligado
                    </button>

                    <button
                        type="button"
                        id="module-prof-export"
                        class="module-prof-action"
                    >
                        Exportar CSV
                    </button>

                    <button
                        type="button"
                        id="module-prof-refresh"
                        class="module-prof-action primary"
                    >
                        ↻ Atualizar
                    </button>

                </div>


                <div class="module-prof-progress">

                    <span></span>

                </div>

            </section>


            <section
                class="module-data-state-banner"
                id="module-data-state-banner"
                hidden
            >

                <span
                    id="module-data-state-icon"
                >
                    i
                </span>

                <div>

                    <strong
                        id="module-data-state-title"
                    >
                        Estado
                    </strong>

                    <p
                        id="module-data-state-message"
                    >
                    </p>

                </div>

            </section>
            `
        );

    }


    /* ======================================================
       PERIODO GLOBAL
       ====================================================== */

    const savedPeriod =
        localStorage.getItem(
            periodKey
        ) ||
        "30d";


    function setPeriod(
        period,
        triggerLegacy = true
    ) {

        localStorage.setItem(
            periodKey,
            period
        );


        document
            .querySelectorAll(
                "[data-prof-period]"
            )
            .forEach(
                button => {

                    button.classList.toggle(
                        "active",
                        button.dataset.profPeriod === period
                    );

                }
            );


        if (triggerLegacy) {

            const legacyButton =
                document.querySelector(
                    `${moduleConfig.legacyToolbar} [data-period="${period}"]`
                );


            if (legacyButton) {

                legacyButton.click();

            }

        }


        if (period === "custom") {

            notify(
                "O seletor personalizado está preparado para receber datas reais."
            );

        }

    }


    document
        .querySelectorAll(
            "[data-prof-period]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        setPeriod(
                            button.dataset.profPeriod
                        );

                    }
                );

            }
        );


    setPeriod(
        savedPeriod,
        false
    );


    /* ======================================================
       SINCRONIZACAO / STALE
       ====================================================== */

    function updateSyncDisplay() {

        const lastSync =
            readLastSync();


        const element =
            document.getElementById(
                "module-prof-last-sync"
            );


        if (element) {

            element.textContent =
                formatTime(
                    lastSync
                );

            element.title =
                formatDateTime(
                    lastSync
                );

        }


        updateStaleState();

    }


    function updateStaleState() {

        const lastSync =
            readLastSync();


        const age =
            Date.now() -
            lastSync.getTime();


        const staleAfter =
            10 * 60 * 1000;


        const status =
            document.getElementById(
                "module-prof-data-status"
            );


        if (!status) {
            return;
        }


        if (age >= staleAfter) {

            status.className =
                "stale";


            status.textContent =
                "● Desatualizado";

        }
        else {

            status.className =
                "ready";


            status.textContent =
                "● Atualizado";

        }

    }


    updateSyncDisplay();


    setInterval(
        updateStaleState,
        30000
    );


    /* ======================================================
       LOADING
       ====================================================== */

    function setLoading(active) {

        document.body.classList.toggle(
            "module-dashboard-loading",
            active
        );


        const status =
            document.getElementById(
                "module-prof-data-status"
            );


        if (status && active) {

            status.className =
                "loading";


            status.textContent =
                "● Atualizando";

        }

    }


    function refreshDashboard(
        automatic = false
    ) {

        setLoading(
            true
        );


        const legacyRefresh =
            document.querySelector(
                moduleConfig.refreshSelector
            );


        if (legacyRefresh) {

            legacyRefresh.click();

        }


        setTimeout(
            () => {

                const now =
                    saveLastSync();


                setLoading(
                    false
                );


                updateSyncDisplay();


                if (!automatic) {

                    notify(
                        `Dashboard atualizado às ${formatTime(now)}.`
                    );

                }

            },
            700
        );

    }


    document
        .getElementById(
            "module-prof-refresh"
        )
        ?.addEventListener(
            "click",
            () => {

                refreshDashboard(
                    false
                );

            }
        );


    /* ======================================================
       AUTO REFRESH
       ====================================================== */

    function setAutoRefresh(enabled) {

        localStorage.setItem(
            autoRefreshKey,
            enabled
                ? "true"
                : "false"
        );


        const button =
            document.getElementById(
                "module-prof-auto-refresh"
            );


        if (button) {

            button.textContent =
                enabled
                    ? "Auto: 60 s"
                    : "Auto: desligado";


            button.classList.toggle(
                "active",
                enabled
            );

        }


        if (autoRefreshTimer) {

            clearInterval(
                autoRefreshTimer
            );


            autoRefreshTimer =
                null;

        }


        if (enabled) {

            autoRefreshTimer =
                setInterval(
                    () => {

                        refreshDashboard(
                            true
                        );

                    },
                    60000
                );

        }

    }


    const autoRefreshEnabled =
        localStorage.getItem(
            autoRefreshKey
        ) === "true";


    setAutoRefresh(
        autoRefreshEnabled
    );


    document
        .getElementById(
            "module-prof-auto-refresh"
        )
        ?.addEventListener(
            "click",
            () => {

                const current =
                    localStorage.getItem(
                        autoRefreshKey
                    ) === "true";


                setAutoRefresh(
                    !current
                );


                notify(
                    current
                        ? "Atualização automática desativada."
                        : "Atualização automática ativada a cada 60 segundos."
                );

            }
        );


    /* ======================================================
       CSV
       ====================================================== */

    function csvValue(value) {

        const text =
            String(
                value ?? ""
            );


        return `"${text.replaceAll(
            '"',
            '""'
        )}"`;

    }


    function exportCsv() {

        const period =
            localStorage.getItem(
                periodKey
            ) ||
            "30d";


        const rows = [
            [
                "Sabino.AI",
                moduleConfig.name
            ],
            [
                "Período",
                period
            ],
            [
                "Última sincronização",
                formatDateTime(
                    readLastSync()
                )
            ],
            [
                "Origem",
                "Dados demonstrativos"
            ],
            [],
            [
                "Indicador",
                "Valor"
            ],
            ...moduleConfig.exportRows
        ];


        const csv =
            rows
                .map(
                    row =>
                        row
                            .map(
                                csvValue
                            )
                            .join(";")
                )
                .join("\r\n");


        const blob =
            new Blob(
                [
                    "\uFEFF",
                    csv
                ],
                {
                    type:
                        "text/csv;charset=utf-8"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const anchor =
            document.createElement(
                "a"
            );


        anchor.href =
            url;


        anchor.download =
            `${moduleConfig.exportName}-dashboard-demo.csv`;


        document.body.appendChild(
            anchor
        );


        anchor.click();


        anchor.remove();


        URL.revokeObjectURL(
            url
        );


        notify(
            "CSV demonstrativo exportado."
        );

    }


    document
        .getElementById(
            "module-prof-export"
        )
        ?.addEventListener(
            "click",
            exportCsv
        );


    /* ======================================================
       TOOLTIP / DEFINICOES
       ====================================================== */

    document
        .querySelectorAll(
            "[data-prof-tooltip]"
        )
        .forEach(
            element => {

                element.title =
                    element.dataset.profTooltip;

            }
        );


    const tooltipDefinitions = [
        {
            selector:
                ".ef2-health-ring, .sf-health-ring, .module-overview-health",

            text:
                "Saúde do módulo: indicador composto por disponibilidade, integrações, RAG ou regras, HITL e taxa de erros."
        },
        {
            selector:
                ".inna-confidence",

            text:
                "Confiança: nível demonstrativo associado à consistência das evidências utilizadas na análise."
        },
        {
            selector:
                ".sf-live-card",

            text:
                "Clique para abrir o detalhamento deste indicador."
        },
        {
            selector:
                ".ef2-live-card",

            text:
                "Clique para abrir o detalhamento deste indicador."
        }
    ];


    tooltipDefinitions.forEach(
        item => {

            document
                .querySelectorAll(
                    item.selector
                )
                .forEach(
                    element => {

                        if (!element.title) {

                            element.title =
                                item.text;

                        }

                    }
                );

        }
    );


    /* ======================================================
       MODAL DRILL-DOWN
       ====================================================== */

    if (
        !document.getElementById(
            "module-prof-modal"
        )
    ) {

        document.body.insertAdjacentHTML(
            "beforeend",
            `
            <div
                class="module-prof-modal"
                id="module-prof-modal"
                hidden
            >

                <div
                    class="module-prof-modal-backdrop"
                    data-prof-modal-close
                ></div>


                <section
                    class="module-prof-modal-card"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="module-prof-modal-title"
                >

                    <header>

                        <div>

                            <small>
                                DETALHAMENTO
                            </small>

                            <h2
                                id="module-prof-modal-title"
                            >
                                Indicador
                            </h2>

                        </div>


                        <button
                            type="button"
                            aria-label="Fechar"
                            data-prof-modal-close
                        >
                            ×
                        </button>

                    </header>


                    <div
                        class="module-prof-modal-body"
                        id="module-prof-modal-body"
                    >
                    </div>


                    <footer>

                        <span>
                            Fonte:
                            <strong>
                                demonstração local
                            </strong>
                        </span>

                        <span>
                            Auditoria:
                            <strong>
                                preparada
                            </strong>
                        </span>

                        <button
                            type="button"
                            data-prof-modal-close
                        >
                            Fechar
                        </button>

                    </footer>

                </section>

            </div>
            `
        );

    }


    const modal =
        document.getElementById(
            "module-prof-modal"
        );


    const modalTitle =
        document.getElementById(
            "module-prof-modal-title"
        );


    const modalBody =
        document.getElementById(
            "module-prof-modal-body"
        );


    function currentView() {

        return (
            document
                .querySelector(
                    "[data-module-view].active"
                )
                ?.textContent
                ?.trim()
            ||
            "Visão Geral"
        );

    }


    function openDrilldown(
        title,
        value,
        description
    ) {

        if (
            !modal ||
            !modalTitle ||
            !modalBody
        ) {
            return;
        }


        lastFocusedElement =
            document.activeElement;


        modalTitle.textContent =
            title ||
            "Indicador";


        modalBody.innerHTML =
            `
            <div class="module-prof-detail-value">

                <small>
                    VALOR ATUAL
                </small>

                <strong>
                    ${value || "—"}
                </strong>

            </div>


            <div class="module-prof-detail-grid">

                <div>

                    <small>
                        Módulo
                    </small>

                    <strong>
                        ${moduleConfig.name}
                    </strong>

                </div>

                <div>

                    <small>
                        Visão
                    </small>

                    <strong>
                        ${currentView()}
                    </strong>

                </div>

                <div>

                    <small>
                        Última atualização
                    </small>

                    <strong>
                        ${formatDateTime(readLastSync())}
                    </strong>

                </div>

                <div>

                    <small>
                        Estado
                    </small>

                    <strong class="ready">
                        Demonstrativo
                    </strong>

                </div>

            </div>


            <div class="module-prof-detail-description">

                <small>
                    CONTEXTO
                </small>

                <p>
                    ${
                        description ||
                        "Este detalhamento está preparado para receber registros reais do backend e permitir investigação completa."
                    }
                </p>

            </div>


            <div class="module-prof-detail-next">

                <strong>
                    Próxima etapa de produção
                </strong>

                <p>
                    O drill-down será conectado ao FastAPI/PostgreSQL
                    para exibir registros, filtros, histórico,
                    responsável e trilha de auditoria.
                </p>

            </div>
            `;


        modal.hidden =
            false;


        document.body.classList.add(
            "module-prof-modal-open"
        );


        modal
            .querySelector(
                "[data-prof-modal-close]"
            )
            ?.focus();

    }


    function closeModal() {

        if (!modal) {
            return;
        }


        modal.hidden =
            true;


        document.body.classList.remove(
            "module-prof-modal-open"
        );


        lastFocusedElement
            ?.focus?.();

    }


    document
        .querySelectorAll(
            "[data-prof-modal-close]"
        )
        .forEach(
            element => {

                element.addEventListener(
                    "click",
                    closeModal
                );

            }
        );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape" &&
                modal &&
                !modal.hidden
            ) {

                closeModal();

            }

        }
    );


    /* ======================================================
       CARDS CLICAVEIS
       ====================================================== */

    const clickableSelectors = [
        ".ef2-live-card",
        ".sf-live-card",
        ".module-overview-kpis article",
        ".ef2-kpis article",
        ".sf-kpis article",
        ".inna-intelligence-summary article"
    ];


    document
        .querySelectorAll(
            clickableSelectors.join(",")
        )
        .forEach(
            card => {

                card.classList.add(
                    "module-prof-clickable"
                );


                if (
                    !card.hasAttribute(
                        "tabindex"
                    )
                ) {

                    card.tabIndex =
                        0;

                }


                card.setAttribute(
                    "role",
                    "button"
                );


                function openCard() {

                    const title =
                        card
                            .querySelector(
                                "small"
                            )
                            ?.textContent
                            ?.trim()
                        ||
                        card
                            .querySelector(
                                "h3"
                            )
                            ?.textContent
                            ?.trim()
                        ||
                        "Indicador";


                    const value =
                        card
                            .querySelector(
                                ":scope > strong"
                            )
                            ?.textContent
                            ?.trim()
                        ||
                        card
                            .querySelector(
                                "strong"
                            )
                            ?.textContent
                            ?.trim()
                        ||
                        "—";


                    const description =
                        card
                            .querySelector(
                                "p"
                            )
                            ?.textContent
                            ?.trim();


                    openDrilldown(
                        title,
                        value,
                        description
                    );

                }


                card.addEventListener(
                    "click",
                    event => {

                        if (
                            event.target.closest(
                                "button, a, select, input"
                            )
                        ) {
                            return;
                        }


                        openCard();

                    }
                );


                card.addEventListener(
                    "keydown",
                    event => {

                        if (
                            event.key === "Enter" ||
                            event.key === " "
                        ) {

                            event.preventDefault();

                            openCard();

                        }

                    }
                );

            }
        );


    /* ======================================================
       LINHAS DAS TABELAS
       ====================================================== */

    document
        .querySelectorAll(
            ".ef2-table-wrapper tbody tr, " +
            ".sf-table-wrapper tbody tr, " +
            ".inna-intelligence-table tbody tr"
        )
        .forEach(
            row => {

                row.classList.add(
                    "module-prof-table-row"
                );


                row.tabIndex =
                    0;


                function openRow() {

                    const cells =
                        Array.from(
                            row.querySelectorAll(
                                "td"
                            )
                        )
                        .map(
                            cell =>
                                cell.textContent
                                    .trim()
                                    .replace(
                                        /\s+/g,
                                        " "
                                    )
                        );


                    openDrilldown(
                        cells[0] ||
                        "Registro",

                        cells[1] ||
                        "—",

                        `Registro relacionado: ${cells.join(" · ")}`
                    );

                }


                row.addEventListener(
                    "click",
                    openRow
                );


                row.addEventListener(
                    "keydown",
                    event => {

                        if (
                            event.key === "Enter"
                        ) {

                            openRow();

                        }

                    }
                );

            }
        );


    /* ======================================================
       ESTADOS PROFISSIONAIS
       ====================================================== */

    const stateBanner =
        document.getElementById(
            "module-data-state-banner"
        );


    function showDataState(
        state
    ) {

        if (!stateBanner) {
            return;
        }


        const title =
            document.getElementById(
                "module-data-state-title"
            );


        const message =
            document.getElementById(
                "module-data-state-message"
            );


        const icon =
            document.getElementById(
                "module-data-state-icon"
            );


        const states = {

            ready: {
                hidden:
                    true
            },

            empty: {
                title:
                    "Nenhum dado encontrado",

                message:
                    "Não existem registros para os filtros selecionados.",

                icon:
                    "○"
            },

            error: {
                title:
                    "Falha ao carregar os dados",

                message:
                    "A interface está preparada para apresentar erro controlado e permitir nova tentativa.",

                icon:
                    "!"
            },

            stale: {
                title:
                    "Dados desatualizados",

                message:
                    "A última sincronização ultrapassou o limite esperado. Atualize o dashboard.",

                icon:
                    "↻"
            },

            loading: {
                title:
                    "Atualizando informações",

                message:
                    "Aguarde enquanto os indicadores são atualizados.",

                icon:
                    "…"
            }

        };


        const selected =
            states[state] ||
            states.ready;


        if (selected.hidden) {

            stateBanner.hidden =
                true;


            return;

        }


        stateBanner.hidden =
            false;


        stateBanner.dataset.state =
            state;


        title.textContent =
            selected.title;


        message.textContent =
            selected.message;


        icon.textContent =
            selected.icon;

    }


    const requestedState =
        new URL(
            window.location.href
        )
            .searchParams
            .get(
                "state"
            );


    if (
        [
            "empty",
            "error",
            "stale",
            "loading"
        ].includes(
            requestedState
        )
    ) {

        showDataState(
            requestedState
        );

    }
    else {

        showDataState(
            "ready"
        );

    }


    /* ======================================================
       API FUTURA
       ====================================================== */

    window.SabinoModuleDashboardProfessional = {

        refresh:
            refreshDashboard,

        setState:
            showDataState,

        openDrilldown:
            openDrilldown,

        module:
            moduleConfig.key

    };


    console.log(
        `SABINO_PROFESSIONAL_DASHBOARD=${moduleConfig.key.toUpperCase()}_READY`
    );

});
