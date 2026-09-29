/* ============================================================
   SABINO.AI - FINANCE I18N COMPLETION V1

   Objetivos:
   - Sabino.AI nunca traduz
   - INNA nunca traduz
   - completa textos que ficaram em português
   - acompanha sabino:locale-change
   - traduz meses do gráfico
   - não altera layout
   - não altera valores/moeda
   ============================================================ */

(function () {

    "use strict";


    if (window.SabinoFinanceI18nCompletionV1) {
        return;
    }


    window.SabinoFinanceI18nCompletionV1 = true;


    const ORIGINAL_TEXT =
        new WeakMap();


    const ORIGINAL_MONTH =
        new WeakMap();


    function normalize(value) {

        return String(value || "")
            .normalize("NFD")
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }


    function currentLocale() {

        try {

            if (
                window.SabinoLocale &&
                typeof window.SabinoLocale.current ===
                    "function"
            ) {

                return (
                    window.SabinoLocale.current()
                    ||
                    document.documentElement.lang
                    ||
                    "pt-BR"
                );
            }

        }
        catch (_) {}


        return (
            document.documentElement.lang
            ||
            localStorage.getItem(
                "sabino_language_manual"
            )
            ||
            localStorage.getItem(
                "sabino_language"
            )
            ||
            "pt-BR"
        );
    }


    function languageBase(locale) {

        return String(
            locale || "pt-BR"
        )
        .replace("_", "-")
        .split("-")[0]
        .toLowerCase();
    }


    /* ========================================================
       DICIONARIO COMPLEMENTAR

       Sabino.AI e INNA permanecem exatamente iguais.
       ======================================================== */

    const DICTIONARY = {};


    function add(
        source,
        translations
    ) {

        DICTIONARY[
            normalize(source)
        ] = {

            pt: source,

            ...translations
        };
    }


    add(
        "FINANCEIRO",
        {
            en: "FINANCE",
            es: "FINANZAS",
            de: "FINANZEN",
            fr: "FINANCES",
            it: "FINANZE",
            ro: "FINANȚE",
            ru: "ФИНАНСЫ",
            uk: "ФІНАНСИ",
            ar: "المالية"
        }
    );


    add(
        "Visão Geral",
        {
            en: "Overview",
            es: "Vista general",
            de: "Übersicht",
            fr: "Vue d’ensemble",
            it: "Panoramica",
            ro: "Prezentare generală",
            ru: "Обзор",
            uk: "Огляд",
            ar: "نظرة عامة"
        }
    );


    add(
        "EDUCAÇÃO E ORGANIZAÇÃO",
        {
            en: "EDUCATION & ORGANIZATION",
            es: "EDUCACIÓN Y ORGANIZACIÓN",
            de: "BILDUNG UND ORGANISATION",
            fr: "ÉDUCATION ET ORGANISATION",
            it: "EDUCAZIONE E ORGANIZZAZIONE",
            ro: "EDUCAȚIE ȘI ORGANIZARE",
            ru: "ОБУЧЕНИЕ И ОРГАНИЗАЦИЯ",
            uk: "ОСВІТА ТА ОРГАНІЗАЦІЯ",
            ar: "التعليم والتنظيم"
        }
    );


    add(
        "CONTAS E COMPROMISSOS",
        {
            en: "ACCOUNTS & COMMITMENTS",
            es: "CUENTAS Y COMPROMISOS",
            de: "KONTEN UND VERPFLICHTUNGEN",
            fr: "COMPTES ET ENGAGEMENTS",
            it: "CONTI E IMPEGNI",
            ro: "CONTURI ȘI ANGAJAMENTE",
            ru: "СЧЕТА И ОБЯЗАТЕЛЬСТВА",
            uk: "РАХУНКИ ТА ЗОБОВ’ЯЗАННЯ",
            ar: "الحسابات والالتزامات"
        }
    );


    add(
        "PATRIMÔNIO E PROTEÇÃO",
        {
            en: "ASSETS & PROTECTION",
            es: "PATRIMONIO Y PROTECCIÓN",
            de: "VERMÖGEN UND SCHUTZ",
            fr: "PATRIMOINE ET PROTECTION",
            it: "PATRIMONIO E PROTEZIONE",
            ro: "PATRIMONIU ȘI PROTECȚIE",
            ru: "АКТИВЫ И ЗАЩИТА",
            uk: "АКТИВИ ТА ЗАХИСТ",
            ar: "الأصول والحماية"
        }
    );


    add(
        "INTELIGÊNCIA E APOIO",
        {
            en: "INTELLIGENCE & SUPPORT",
            es: "INTELIGENCIA Y APOYO",
            de: "INTELLIGENZ UND UNTERSTÜTZUNG",
            fr: "INTELLIGENCE ET ASSISTANCE",
            it: "INTELLIGENZA E SUPPORTO",
            ro: "INTELIGENȚĂ ȘI SUPORT",
            ru: "ИНТЕЛЛЕКТ И ПОДДЕРЖКА",
            uk: "ІНТЕЛЕКТ І ПІДТРИМКА",
            ar: "الذكاء والدعم"
        }
    );


    add(
        "Sair",
        {
            en: "Sign out",
            es: "Salir",
            de: "Abmelden",
            fr: "Déconnexion",
            it: "Esci",
            ro: "Ieșire",
            ru: "Выйти",
            uk: "Вийти",
            ar: "تسجيل الخروج"
        }
    );


    add(
        "Visão geral financeira",
        {
            en: "Financial overview",
            es: "Resumen financiero",
            de: "Finanzübersicht",
            fr: "Vue d’ensemble financière",
            it: "Panoramica finanziaria",
            ro: "Prezentare financiară",
            ru: "Финансовый обзор",
            uk: "Фінансовий огляд",
            ar: "نظرة مالية عامة"
        }
    );


    add(
        "Veja seus resultados, acompanhe seus gastos e organize sua vida financeira.",
        {
            en:
                "Review your results, track your spending and organize your financial life.",

            es:
                "Consulta tus resultados, controla tus gastos y organiza tu vida financiera.",

            de:
                "Sehen Sie Ihre Ergebnisse, verfolgen Sie Ihre Ausgaben und organisieren Sie Ihre Finanzen.",

            fr:
                "Consultez vos résultats, suivez vos dépenses et organisez votre vie financière.",

            it:
                "Consulta i risultati, monitora le spese e organizza la tua vita finanziaria.",

            ro:
                "Vezi rezultatele, urmărește cheltuielile și organizează-ți viața financiară.",

            ru:
                "Просматривайте результаты, отслеживайте расходы и управляйте своими финансами.",

            uk:
                "Переглядайте результати, відстежуйте витрати та впорядковуйте свої фінанси.",

            ar:
                "راجع نتائجك، وتابع نفقاتك، ونظّم حياتك المالية."
        }
    );


    add(
        "Saldo atual",
        {
            en: "Current balance",
            es: "Saldo actual",
            de: "Aktueller Saldo",
            fr: "Solde actuel",
            it: "Saldo attuale",
            ro: "Sold actual",
            ru: "Текущий баланс",
            uk: "Поточний баланс",
            ar: "الرصيد الحالي"
        }
    );


    add(
        "Entradas",
        {
            en: "Income",
            es: "Ingresos",
            de: "Einnahmen",
            fr: "Revenus",
            it: "Entrate",
            ro: "Venituri",
            ru: "Доходы",
            uk: "Надходження",
            ar: "الإيرادات"
        }
    );


    add(
        "Gastos",
        {
            en: "Expenses",
            es: "Gastos",
            de: "Ausgaben",
            fr: "Dépenses",
            it: "Spese",
            ro: "Cheltuieli",
            ru: "Расходы",
            uk: "Витрати",
            ar: "المصروفات"
        }
    );


    add(
        "Reserva",
        {
            en: "Reserve",
            es: "Reserva",
            de: "Rücklage",
            fr: "Réserve",
            it: "Riserva",
            ro: "Rezervă",
            ru: "Резерв",
            uk: "Резерв",
            ar: "الاحتياطي"
        }
    );


    add(
        "Gastos por mês",
        {
            en: "Expenses by month",
            es: "Gastos por mes",
            de: "Ausgaben pro Monat",
            fr: "Dépenses par mois",
            it: "Spese per mese",
            ro: "Cheltuieli pe lună",
            ru: "Расходы по месяцам",
            uk: "Витрати за місяцями",
            ar: "المصروفات حسب الشهر"
        }
    );


    add(
        "Acompanhe quanto você gastou nos últimos meses.",
        {
            en:
                "Track how much you spent over the last few months.",

            es:
                "Consulta cuánto has gastado en los últimos meses.",

            de:
                "Verfolgen Sie Ihre Ausgaben der letzten Monate.",

            fr:
                "Suivez vos dépenses des derniers mois.",

            it:
                "Monitora quanto hai speso negli ultimi mesi.",

            ro:
                "Urmărește cât ai cheltuit în ultimele luni.",

            ru:
                "Отслеживайте расходы за последние месяцы.",

            uk:
                "Відстежуйте витрати за останні місяці.",

            ar:
                "تابع مقدار ما أنفقته خلال الأشهر الماضية."
        }
    );


    add(
        "Últimos 6 meses",
        {
            en: "Last 6 months",
            es: "Últimos 6 meses",
            de: "Letzte 6 Monate",
            fr: "6 derniers mois",
            it: "Ultimi 6 mesi",
            ro: "Ultimele 6 luni",
            ru: "Последние 6 месяцев",
            uk: "Останні 6 місяців",
            ar: "آخر 6 أشهر"
        }
    );


    add(
        "Maior gasto do período",
        {
            en: "Highest spending in period",
            es: "Mayor gasto del período",
            de: "Höchste Ausgabe im Zeitraum",
            fr: "Dépense la plus élevée de la période",
            it: "Spesa più alta del periodo",
            ro: "Cea mai mare cheltuială din perioadă",
            ru: "Наибольший расход за период",
            uk: "Найбільша витрата за період",
            ar: "أعلى إنفاق في الفترة"
        }
    );


    add(
        "Gastos por categoria",
        {
            en: "Expenses by category",
            es: "Gastos por categoría",
            de: "Ausgaben nach Kategorie",
            fr: "Dépenses par catégorie",
            it: "Spese per categoria",
            ro: "Cheltuieli pe categorii",
            ru: "Расходы по категориям",
            uk: "Витрати за категоріями",
            ar: "المصروفات حسب الفئة"
        }
    );


    add(
        "Veja onde seu dinheiro está sendo mais usado.",
        {
            en:
                "See where your money is being spent the most.",

            es:
                "Consulta dónde estás gastando más dinero.",

            de:
                "Sehen Sie, wofür Sie am meisten Geld ausgeben.",

            fr:
                "Découvrez où vous dépensez le plus d’argent.",

            it:
                "Scopri dove spendi la maggior parte del tuo denaro.",

            ro:
                "Vezi unde cheltuiești cei mai mulți bani.",

            ru:
                "Посмотрите, на что уходит больше всего денег.",

            uk:
                "Подивіться, на що витрачається найбільше коштів.",

            ar:
                "تعرّف على المجالات التي تنفق فيها أكبر قدر من أموالك."
        }
    );


    add(
        "Total",
        {
            en: "Total",
            es: "Total",
            de: "Gesamt",
            fr: "Total",
            it: "Totale",
            ro: "Total",
            ru: "Итого",
            uk: "Разом",
            ar: "الإجمالي"
        }
    );


    add(
        "Maior gasto do mês",
        {
            en: "Highest spending this month",
            es: "Mayor gasto del mes",
            de: "Höchste Ausgabe des Monats",
            fr: "Dépense la plus élevée du mois",
            it: "Spesa più alta del mese",
            ro: "Cea mai mare cheltuială a lunii",
            ru: "Самая крупная трата месяца",
            uk: "Найбільша витрата місяця",
            ar: "أعلى إنفاق في الشهر"
        }
    );


    add(
        "Categoria com maior participação nas despesas.",
        {
            en:
                "Category with the largest share of expenses.",

            es:
                "Categoría con mayor participación en los gastos.",

            de:
                "Kategorie mit dem größten Anteil an den Ausgaben.",

            fr:
                "Catégorie représentant la plus grande part des dépenses.",

            it:
                "Categoria con la quota maggiore delle spese.",

            ro:
                "Categoria cu cea mai mare pondere în cheltuieli.",

            ru:
                "Категория с наибольшей долей расходов.",

            uk:
                "Категорія з найбільшою часткою витрат.",

            ar:
                "الفئة ذات الحصة الأكبر من المصروفات."
        }
    );


    add(
        "Transporte",
        {
            en: "Transport",
            es: "Transporte",
            de: "Transport",
            fr: "Transport",
            it: "Trasporti",
            ro: "Transport",
            ru: "Транспорт",
            uk: "Транспорт",
            ar: "المواصلات"
        }
    );


    add(
        "Alimentação",
        {
            en: "Food",
            es: "Alimentación",
            de: "Lebensmittel",
            fr: "Alimentation",
            it: "Alimentazione",
            ro: "Alimentație",
            ru: "Питание",
            uk: "Харчування",
            ar: "الطعام"
        }
    );


    add(
        "Moradia",
        {
            en: "Housing",
            es: "Vivienda",
            de: "Wohnen",
            fr: "Logement",
            it: "Casa",
            ro: "Locuință",
            ru: "Жильё",
            uk: "Житло",
            ar: "السكن"
        }
    );


    add(
        "Lazer",
        {
            en: "Leisure",
            es: "Ocio",
            de: "Freizeit",
            fr: "Loisirs",
            it: "Tempo libero",
            ro: "Timp liber",
            ru: "Досуг",
            uk: "Дозвілля",
            ar: "الترفيه"
        }
    );


    add(
        "Saúde",
        {
            en: "Health",
            es: "Salud",
            de: "Gesundheit",
            fr: "Santé",
            it: "Salute",
            ro: "Sănătate",
            ru: "Здоровье",
            uk: "Здоров’я",
            ar: "الصحة"
        }
    );


    add(
        "Outros",
        {
            en: "Other",
            es: "Otros",
            de: "Sonstiges",
            fr: "Autres",
            it: "Altro",
            ro: "Altele",
            ru: "Другое",
            uk: "Інше",
            ar: "أخرى"
        }
    );


    add(
        "Próximos passos",
        {
            en: "Next steps",
            es: "Próximos pasos",
            de: "Nächste Schritte",
            fr: "Prochaines étapes",
            it: "Prossimi passi",
            ro: "Pașii următori",
            ru: "Следующие шаги",
            uk: "Наступні кроки",
            ar: "الخطوات التالية"
        }
    );


    add(
        "Ações simples para melhorar sua organização.",
        {
            en:
                "Simple actions to improve your organization.",

            es:
                "Acciones sencillas para mejorar tu organización.",

            de:
                "Einfache Schritte für eine bessere Organisation.",

            fr:
                "Des actions simples pour mieux vous organiser.",

            it:
                "Azioni semplici per migliorare la tua organizzazione.",

            ro:
                "Acțiuni simple pentru o organizare mai bună.",

            ru:
                "Простые действия для лучшей организации.",

            uk:
                "Прості дії для кращої організації.",

            ar:
                "خطوات بسيطة لتحسين تنظيمك."
        }
    );


    add(
        "Registrar gastos da semana",
        {
            en: "Record this week's expenses",
            es: "Registrar gastos de la semana",
            de: "Wochenausgaben erfassen",
            fr: "Enregistrer les dépenses de la semaine",
            it: "Registra le spese della settimana",
            ro: "Înregistrează cheltuielile săptămânii",
            ru: "Записать расходы за неделю",
            uk: "Записати витрати за тиждень",
            ar: "تسجيل مصروفات الأسبوع"
        }
    );


    add(
        "Revisar meta do mês",
        {
            en: "Review this month's goal",
            es: "Revisar la meta del mes",
            de: "Monatsziel überprüfen",
            fr: "Revoir l’objectif du mois",
            it: "Rivedi l’obiettivo del mese",
            ro: "Revizuiește obiectivul lunii",
            ru: "Проверить цель месяца",
            uk: "Переглянути ціль місяця",
            ar: "مراجعة هدف الشهر"
        }
    );


    add(
        "Conferir sua reserva",
        {
            en: "Check your reserve",
            es: "Revisar tu reserva",
            de: "Rücklage prüfen",
            fr: "Vérifier votre réserve",
            it: "Controlla la tua riserva",
            ro: "Verifică rezerva",
            ru: "Проверить резерв",
            uk: "Перевірити резерв",
            ar: "مراجعة احتياطك"
        }
    );


    add(
        "Organizar categorias",
        {
            en: "Organize categories",
            es: "Organizar categorías",
            de: "Kategorien organisieren",
            fr: "Organiser les catégories",
            it: "Organizza le categorie",
            ro: "Organizează categoriile",
            ru: "Организовать категории",
            uk: "Упорядкувати категорії",
            ar: "تنظيم الفئات"
        }
    );


    add(
        "Dica da INNA",
        {
            en: "INNA tip",
            es: "Consejo de INNA",
            de: "Tipp von INNA",
            fr: "Conseil de INNA",
            it: "Suggerimento di INNA",
            ro: "Sfat de la INNA",
            ru: "Совет INNA",
            uk: "Порада INNA",
            ar: "نصيحة INNA"
        }
    );


    add(
        "Sua assistente financeira.",
        {
            en: "Your financial assistant.",
            es: "Tu asistente financiera.",
            de: "Ihre Finanzassistentin.",
            fr: "Votre assistante financière.",
            it: "La tua assistente finanziaria.",
            ro: "Asistentul tău financiar.",
            ru: "Ваш финансовый помощник.",
            uk: "Ваш фінансовий помічник.",
            ar: "مساعدتك المالية."
        }
    );


    add(
        "Conversar com a INNA",
        {
            en: "Talk to INNA",
            es: "Hablar con INNA",
            de: "Mit INNA sprechen",
            fr: "Parler à INNA",
            it: "Parla con INNA",
            ro: "Vorbește cu INNA",
            ru: "Поговорить с INNA",
            uk: "Поговорити з INNA",
            ar: "التحدث مع INNA"
        }
    );


    add(
        "Perguntar a INNA",
        {
            en: "Ask INNA",
            es: "Preguntar a INNA",
            de: "INNA fragen",
            fr: "Demander à INNA",
            it: "Chiedi a INNA",
            ro: "Întreabă INNA",
            ru: "Спросить INNA",
            uk: "Запитати INNA",
            ar: "اسأل INNA"
        }
    );


    add(
        "Modo demonstração",
        {
            en: "Demo mode",
            es: "Modo de demostración",
            de: "Demomodus",
            fr: "Mode démonstration",
            it: "Modalità demo",
            ro: "Mod demonstrație",
            ru: "Демо-режим",
            uk: "Демонстраційний режим",
            ar: "وضع العرض التجريبي"
        }
    );


    add(
        "Conta Sabino.AI",
        {
            en: "Sabino.AI Account",
            es: "Cuenta Sabino.AI",
            de: "Sabino.AI-Konto",
            fr: "Compte Sabino.AI",
            it: "Account Sabino.AI",
            ro: "Cont Sabino.AI",
            ru: "Аккаунт Sabino.AI",
            uk: "Обліковий запис Sabino.AI",
            ar: "حساب Sabino.AI"
        }
    );


    /* ========================================================
       MESES DO GRAFICO
       ======================================================== */

    const PT_MONTHS = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez"
    ];


    const MONTHS = {

        pt: PT_MONTHS,

        en: [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ],

        es: [
            "Ene","Feb","Mar","Abr","May","Jun",
            "Jul","Ago","Sep","Oct","Nov","Dic"
        ],

        de: [
            "Jan","Feb","Mär","Apr","Mai","Jun",
            "Jul","Aug","Sep","Okt","Nov","Dez"
        ],

        fr: [
            "Jan","Fév","Mar","Avr","Mai","Juin",
            "Juil","Aoû","Sep","Oct","Nov","Déc"
        ],

        it: [
            "Gen","Feb","Mar","Apr","Mag","Giu",
            "Lug","Ago","Set","Ott","Nov","Dic"
        ],

        ro: [
            "Ian","Feb","Mar","Apr","Mai","Iun",
            "Iul","Aug","Sep","Oct","Nov","Dec"
        ],

        ru: [
            "Янв","Фев","Мар","Апр","Май","Июн",
            "Июл","Авг","Сен","Окт","Ноя","Дек"
        ],

        uk: [
            "Січ","Лют","Бер","Кві","Тра","Чер",
            "Лип","Сер","Вер","Жов","Лис","Гру"
        ],

        ar: [
            "ينا","فبر","مار","أبر","ماي","يون",
            "يول","أغس","سبت","أكت","نوف","ديس"
        ]
    };


    /* ========================================================
       MARCAS PROTEGIDAS
       ======================================================== */

    function protectBrands() {

        if (!document.body) {
            return;
        }


        const walker =
            document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT
            );


        const nodes = [];


        while (walker.nextNode()) {
            nodes.push(
                walker.currentNode
            );
        }


        nodes.forEach(
            function (node) {

                const value =
                    String(
                        node.nodeValue || ""
                    )
                    .trim();


                if (
                    value !== "Sabino.AI" &&
                    value !== "INNA"
                ) {

                    return;
                }


                const parent =
                    node.parentElement;


                if (!parent) {
                    return;
                }


                parent.setAttribute(
                    "translate",
                    "no"
                );


                parent.classList.add(
                    "notranslate"
                );


                parent.dataset
                    .sabinoBrandProtected =
                    "true";
            }
        );
    }


    /* ========================================================
       TRADUZIR TEXT NODE
       ======================================================== */

    function translateTextNode(
        node,
        language
    ) {

        const parent =
            node.parentElement;


        if (!parent) {
            return;
        }


        if (
            parent.closest(
                [
                    "script",
                    "style",
                    "noscript",
                    "textarea",
                    "code",
                    "pre",
                    "#sabinoLanguageSwitcher",
                    ".sabino-global-language",
                    ".sabino-language-menu"
                ].join(",")
            )
        ) {

            return;
        }


        const raw =
            String(
                node.nodeValue || ""
            );


        const trimmed =
            raw.trim();


        if (!trimmed) {
            return;
        }


        let source =
            ORIGINAL_TEXT.get(
                node
            );


        if (!source) {

            const entry =
                DICTIONARY[
                    normalize(trimmed)
                ];


            if (!entry) {
                return;
            }


            source =
                trimmed;


            ORIGINAL_TEXT.set(
                node,
                source
            );
        }


        const entry =
            DICTIONARY[
                normalize(source)
            ];


        if (!entry) {
            return;
        }


        const translated =
            entry[language]
            ||
            entry.en
            ||
            source;


        const leading =
            raw.match(/^\s*/)?.[0]
            ||
            "";


        const trailing =
            raw.match(/\s*$/)?.[0]
            ||
            "";


        node.nodeValue =
            leading +
            translated +
            trailing;
    }


    /* ========================================================
       TRADUZIR MESES
       ======================================================== */

    function translateMonths(
        language
    ) {

        const targetMonths =
            MONTHS[language]
            ||
            MONTHS.en;


        const elements =
            Array.from(
                document.querySelectorAll(
                    "span,div,p,strong,small"
                )
            );


        elements.forEach(
            function (element) {

                if (
                    element.children.length > 0
                ) {

                    return;
                }


                let source =
                    ORIGINAL_MONTH.get(
                        element
                    );


                const current =
                    String(
                        element.textContent || ""
                    )
                    .trim();


                if (!source) {

                    const match =
                        current.match(
                            /^(Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)\/(\d{2})$/i
                        );


                    if (!match) {
                        return;
                    }


                    source = {
                        month:
                            match[1],
                        year:
                            match[2]
                    };


                    ORIGINAL_MONTH.set(
                        element,
                        source
                    );
                }


                const monthIndex =
                    PT_MONTHS.findIndex(
                        function (month) {

                            return (
                                normalize(month) ===
                                normalize(
                                    source.month
                                )
                            );
                        }
                    );


                if (monthIndex < 0) {
                    return;
                }


                element.textContent =
                    targetMonths[
                        monthIndex
                    ]
                    +
                    "/"
                    +
                    source.year;
            }
        );
    }


    /* ========================================================
       APLICAR
       ======================================================== */

    function apply() {

        const locale =
            currentLocale();


        const language =
            languageBase(
                locale
            );


        protectBrands();


        if (!document.body) {
            return;
        }


        const walker =
            document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT
            );


        const nodes = [];


        while (
            walker.nextNode()
        ) {

            nodes.push(
                walker.currentNode
            );
        }


        nodes.forEach(
            function (node) {

                translateTextNode(
                    node,
                    language
                );
            }
        );


        translateMonths(
            language
        );


        document.body.dataset
            .sabinoFinanceLanguage =
            language;
    }


    function scheduleApply() {

        [
            0,
            80,
            250,
            700,
            1400,
            2200
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
            scheduleApply,
            {
                once: true
            }
        );

    }
    else {

        scheduleApply();
    }


    window.addEventListener(
        "load",
        scheduleApply
    );


    window.addEventListener(
        "sabino:locale-change",
        scheduleApply
    );


    window.addEventListener(
        "sabino:finance-data-updated",
        scheduleApply
    );


    window.SabinoFinanceI18nCompletionV1 = {

        refresh:
            apply,

        protectBrands:
            protectBrands

    };

})();
