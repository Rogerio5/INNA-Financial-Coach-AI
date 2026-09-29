/* SABINO_SHARED_FINANCE_SIDEBAR_V1 */
/* SABINO_SHARED_FINANCE_SIDEBAR_FULL_V2 */
/* SABINO_FINANCE_UI_POLISH_V3 */

(function(){

    const currentPath =
        window.location.pathname.replace(/\/+$/, "") ||
        "/";

    const groups = [

        {
            title:"Educação e Organização",
            items:[
                {
                    label:"Educação Financeira",
                    href:"/financeiro/educacao"
                },
                {
                    label:"Orçamento",
                    href:"/financeiro/orcamento"
                },
                {
                    label:"Gastos",
                    href:"/financeiro/gastos"
                },
                {
                    label:"Planejamento",
                    href:"/financeiro/planejamento"
                },
                {
                    label:"Metas",
                    href:"/financeiro/metas"
                }
            ]
        },

        {
            title:"Contas e Compromissos",
            items:[
                {
                    label:"Central de Contas",
                    href:"/financeiro/central-contas"
                },
                {
                    label:"Contas & Assinaturas",
                    href:"/financeiro/contas"
                },
                {
                    label:"Crédito & Endividamento",
                    href:"/financeiro/credito"
                },
                {
                    label:"Impostos & Obrigações",
                    href:"/financeiro/impostos"
                }
            ]
        },

        {
            title:"Patrimônio e Proteção",
            items:[
                {
                    label:"Investimentos & Reserva",
                    href:"/financeiro/reserva"
                },
                {
                    label:"Patrimônio & Saúde",
                    href:"/financeiro/patrimonio"
                },
                {
                    label:"Proteção Financeira & Seguros",
                    href:"/financeiro/protecao"
                },
                {
                    label:"Segurança Financeira",
                    href:"/financeiro/seguranca"
                }
            ]
        },

        {
            title:"Inteligência e Apoio",
            items:[
                {
                    label:"Reembolso Inteligente",
                    href:"/financeiro/reembolso",
                    planned:true
                },
                {
                    label:"Relatórios Financeiros",
                    href:"/financeiro/relatorios"
                },
                {
                    label:"Finanças Familiares",
                    href:"/financeiro/familia"
                }
            ]
        }

    ];


    function isActive(href){

        return currentPath === href;
    }


    function createItem(item){

        if(item.planned){

            return `
                <span
                    class="sab-fin-link sab-fin-planned"
                    title="Módulo em construção"
                >
                    <span>${item.label}</span>
                    <small>Em construção</small>
                </span>
            `;
        }

        return `
            <a
                href="${item.href}"
                class="sab-fin-link module-link ${
                    isActive(item.href)
                        ? "active"
                        : ""
                }"
            >
                ${item.label}
            </a>
        `;
    }


    function createGroups(){

        let html = `
            <a
                href="/financeiro"
                class="sab-fin-link sab-fin-overview ${
                    isActive("/financeiro")
                        ? "active"
                        : ""
                }"
            >
                Visão Geral
            </a>
        `;

        groups.forEach(function(group){

            const hasActive =
                group.items.some(function(item){
                    return isActive(item.href);
                });

            html += `
                <details
                    class="sab-fin-group"
                    ${hasActive ? "open" : ""}
                >

                    <summary>
                        ${group.title}
                    </summary>

                    <div class="sab-fin-group-items">

                        ${
                            group.items
                                .map(createItem)
                                .join("")
                        }

                    </div>

                </details>
            `;
        });

        return html;
    }


    function addStyle(){

        if(
            document.getElementById(
                "SABINO_SHARED_FINANCE_SIDEBAR_V1_STYLE"
            )
        ){
            return;
        }

        const style =
            document.createElement("style");

        style.id =
            "SABINO_SHARED_FINANCE_SIDEBAR_V1_STYLE";

        style.textContent = `

            aside.sidebar,
            aside.side{
                overflow-y:auto;
                max-height:100vh;
            }

            .sab-fin-shared-menu{
                padding-bottom:18px;
            }

            .sab-fin-brand{
                display:block;
                padding:8px 10px 18px;
                font-size:21px;
                font-weight:900;
                text-decoration:none;
                color:#ffffff;
            }

            .sab-fin-brand{
                display:flex;
                align-items:center;
                gap:10px;
            }

            .sab-fin-logo-mark{
                width:30px;
                height:30px;
                object-fit:contain;
                flex:0 0 auto;
            }

            .sab-fin-brand-name{
                color:#ffffff;
            }

            .sab-fin-brand-name b{
                color:#d9b441;
            }

            .sab-fin-section-label{
                display:block;
                margin:12px 10px 8px;
                color:#d9b441;
                font-size:10px;
                font-weight:900;
                letter-spacing:.08em;
            }

            .sab-fin-link{
                display:flex !important;
                align-items:center;
                justify-content:space-between;
                gap:8px;
                width:100%;
                margin:2px 0;
                padding:9px 10px !important;
                border-radius:8px;
                color:#dce1e4 !important;
                text-decoration:none !important;
                font-size:12px !important;
                font-weight:600;
                line-height:1.35;
                background:transparent;
                border:1px solid transparent;
            }

            .sab-fin-link:hover{
                background:#121719;
                border-color:#272f33;
            }

            .sab-fin-link.active{
                background:#211f12 !important;
                border-color:#5d501d !important;
                color:#f4cf57 !important;
                font-weight:900 !important;
            }

            .sab-fin-overview{
                margin-bottom:10px;
            }

            .sab-fin-group{
                margin:7px 0;
                border-top:1px solid #242b2f;
                padding-top:7px;
            }

            .sab-fin-group > summary{
                cursor:pointer;
                list-style:none;
                padding:8px 10px;
                color:#9fa8ad;
                font-size:10px;
                font-weight:900;
                letter-spacing:.055em;
                text-transform:uppercase;
                user-select:none;
            }

            .sab-fin-group > summary::-webkit-details-marker{
                display:none;
            }

            .sab-fin-group > summary::after{
                content:"+";
                float:right;
                color:#d9b441;
                font-size:14px;
            }

            .sab-fin-group[open] > summary::after{
                content:"−";
            }

            .sab-fin-group-items{
                padding:2px 0 4px;
            }

            .sab-fin-planned{
                opacity:.50;
                cursor:default;
            }

            .sab-fin-planned small{
                color:#737d82;
                font-size:8px;
                text-transform:uppercase;
                white-space:nowrap;
            }

            .sab-fin-footer{
                border-top:1px solid #242b2f;
                margin-top:12px;
                padding-top:10px;
            }

            .sab-fin-logout{
                color:#d7dcdf !important;
            }

        `;

        document.head.appendChild(style);
    }


    function render(){

        addStyle();

        const sidebar =
            document.querySelector(
                "aside.sidebar, aside.side"
            );

        if(!sidebar){
            return;
        }
/*
         * Páginas antigas:
         * transforma a sidebar inteira no padrão único.
         */

        sidebar.innerHTML = `

            <a
                href="/dashboard"
                class="sab-fin-brand"
            >
                <img
                    src="/static/images/sabino-s-logo.png"
                    alt="Sabino.AI"
                    class="sab-fin-logo-mark"
                >

                <span class="sab-fin-brand-name">
                    Sabino<b>.AI</b>
                </span>
            </a>

            <span class="sab-fin-section-label">
                FINANCEIRO
            </span>

            <div class="sab-fin-shared-menu">

                ${createGroups()}

            </div>

            <div class="sab-fin-footer"><a href="/financeiro/meu-plano" class="sab-fin-link">Meu plano</a>

                <a
                    href="/inna"
                    class="sab-fin-link"
                >
                    INNA
                </a>

                <a
                    href="/logout"
                    class="sab-fin-link sab-fin-logout"
                >
                    Sair
                </a>

            </div>
        `;
    }


    /*
     * SABINO_FINANCE_PERCENT_FORMAT_V1
     *
     * 38.0%  -> 38%
     * 39.00% -> 39%
     * 38,50% -> 38,5%
     */

    function normalizeFinancePercentages(root){

        const target =
            root || document.body;

        if(!target){
            return;
        }

        const walker =
            document.createTreeWalker(
                target,
                NodeFilter.SHOW_TEXT
            );

        const nodes = [];

        while(walker.nextNode()){
            nodes.push(
                walker.currentNode
            );
        }

        nodes.forEach(function(node){

            const parent =
                node.parentElement;

            if(!parent){
                return;
            }

            const tag =
                parent.tagName;

            if(
                tag === "SCRIPT" ||
                tag === "STYLE" ||
                tag === "TEXTAREA"
            ){
                return;
            }

            const original =
                node.nodeValue;

            const formatted =
                original.replace(
                    /(-?\d+)([.,])(\d+)%/g,
                    function(
                        match,
                        integer,
                        separator,
                        decimal
                    ){

                        const cleanDecimal =
                            decimal.replace(
                                /0+$/,
                                ""
                            );

                        if(!cleanDecimal){
                            return integer + "%";
                        }

                        return (
                            integer +
                            separator +
                            cleanDecimal +
                            "%"
                        );
                    }
                );

            if(formatted !== original){
                node.nodeValue = formatted;
            }
        });
    }


    function startFinanceUiPolish(){

        normalizeFinancePercentages(
            document.body
        );

        const observer =
            new MutationObserver(
                function(){

                    normalizeFinancePercentages(
                        document.body
                    );
                }
            );

        observer.observe(
            document.body,
            {
                childList:true,
                subtree:true,
                characterData:true
            }
        );

        window.sabinoFinanceUiObserver =
            observer;
    }


    if(document.readyState === "loading"){

        document.addEventListener(
            "DOMContentLoaded",
            function(){

                render();
                startFinanceUiPolish();
            }
        );

    }else{

        render();
        startFinanceUiPolish();
    }

})();