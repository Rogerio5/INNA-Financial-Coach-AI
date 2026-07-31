from __future__ import annotations

RAG_OBSERVABILITY_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "title": "📊 Observabilidade RAG",
        "subtitle": (
            "Monitoramento operacional dos fluxos reais de "
            "recuperação, geração, segurança e fallback."
        ),
        "real_data_notice": (
            "Esta página utiliza somente registros reais da tabela rag_logs."
        ),
        "source_status": "Status da fonte de dados",
        "source_connected": "Fonte conectada",
        "source_empty": "Fonte conectada, mas sem logs registrados",
        "source_error": "Não foi possível consultar os logs RAG",
        "source_table": "Tabela consultada",
        "source_value": "PostgreSQL/Neon — rag_logs",
        "waiting_real_data": "Aguardando dados reais",
        "no_logs": "Nenhum log RAG foi encontrado.",
        "questions": "Perguntas",
        "gemini": "Gemini",
        "security": "Segurança",
        "fallback": "Fallback",
        "average_latency": "Latência média",
        "maximum_latency": "Maior latência",
        "not_available": "Não disponível",
        "field_coverage": "Cobertura dos campos",
        "field_coverage_caption": (
            "Percentual de registros que possuem cada campo preenchido."
        ),
        "field": "Campo",
        "available_rows": "Registros preenchidos",
        "total_rows": "Total de registros",
        "coverage": "Cobertura",
        "available": "Disponível",
        "yes": "Sim",
        "no": "Não",
        "mode_distribution": "Distribuição por modo",
        "mode_distribution_caption": (
            "Quantidade real de logs registrada em cada modo RAG."
        ),
        "mode": "Modo",
        "total": "Total",
        "unregistered": "Não registrado",
        "latest_questions": "Últimas perguntas",
        "latest_questions_caption": (
            "Registros mais recentes disponíveis na fonte de dados."
        ),
        "question": "Pergunta",
        "sources": "Fontes",
        "date": "Data",
        "latency": "Latência",
        "logs_table": "Logs RAG",
        "export": "Exportação",
        "export_caption": (
            "O arquivo contém somente os registros reais carregados."
        ),
        "download_csv": "Baixar logs RAG em CSV",
        "export_unavailable": (
            "A exportação será habilitada quando existirem logs reais."
        ),
        "field_pergunta": "Pergunta",
        "field_modo": "Modo",
        "field_fontes": "Fontes",
        "field_data_hora": "Data e hora",
        "field_tempo_ms": "Latência",
        "field_gemini": "Gemini",
        "field_seguranca": "Segurança",
        "field_fallback": "Fallback",
    },
    "en_us": {
        "title": "📊 RAG Observability",
        "subtitle": (
            "Operational monitoring of real retrieval, generation, "
            "safety and fallback flows."
        ),
        "real_data_notice": (
            "This page uses only real records from the rag_logs table."
        ),
        "source_status": "Data source status",
        "source_connected": "Source connected",
        "source_empty": "Source connected, but no logs have been recorded",
        "source_error": "Unable to query RAG logs",
        "source_table": "Queried table",
        "source_value": "PostgreSQL/Neon — rag_logs",
        "waiting_real_data": "Waiting for real data",
        "no_logs": "No RAG logs were found.",
        "questions": "Questions",
        "gemini": "Gemini",
        "security": "Safety",
        "fallback": "Fallback",
        "average_latency": "Average latency",
        "maximum_latency": "Maximum latency",
        "not_available": "Not available",
        "field_coverage": "Field coverage",
        "field_coverage_caption": (
            "Percentage of records containing each populated field."
        ),
        "field": "Field",
        "available_rows": "Populated records",
        "total_rows": "Total records",
        "coverage": "Coverage",
        "available": "Available",
        "yes": "Yes",
        "no": "No",
        "mode_distribution": "Distribution by mode",
        "mode_distribution_caption": (
            "Real number of logs recorded for each RAG mode."
        ),
        "mode": "Mode",
        "total": "Total",
        "unregistered": "Not recorded",
        "latest_questions": "Latest questions",
        "latest_questions_caption": (
            "Most recent records available from the data source."
        ),
        "question": "Question",
        "sources": "Sources",
        "date": "Date",
        "latency": "Latency",
        "logs_table": "RAG logs",
        "export": "Export",
        "export_caption": (
            "The file contains only the real records that were loaded."
        ),
        "download_csv": "Download RAG logs as CSV",
        "export_unavailable": (
            "Export will be enabled when real logs are available."
        ),
        "field_pergunta": "Question",
        "field_modo": "Mode",
        "field_fontes": "Sources",
        "field_data_hora": "Date and time",
        "field_tempo_ms": "Latency",
        "field_gemini": "Gemini",
        "field_seguranca": "Safety",
        "field_fallback": "Fallback",
    },
}


RAG_OBSERVABILITY_NATIVE_OVERRIDES = {
    "en_gb": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
    },
    "es": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 Observabilidad RAG",
        "subtitle": (
            "Supervisión operativa de los flujos reales de "
            "recuperación, generación, seguridad y fallback."
        ),
        "real_data_notice": (
            "Esta página utiliza únicamente registros reales "
            "de la tabla rag_logs."
        ),
        "source_status": "Estado de la fuente de datos",
        "source_connected": "Fuente conectada",
        "source_empty": (
            "Fuente conectada, pero todavía no hay logs registrados"
        ),
        "source_error": "No fue posible consultar los logs RAG",
        "waiting_real_data": "Esperando datos reales",
        "no_logs": "No se encontraron logs RAG.",
        "questions": "Preguntas",
        "security": "Seguridad",
        "average_latency": "Latencia media",
        "maximum_latency": "Latencia máxima",
        "not_available": "No disponible",
        "field_coverage": "Cobertura de campos",
        "field": "Campo",
        "available_rows": "Registros completos",
        "total_rows": "Total de registros",
        "coverage": "Cobertura",
        "available": "Disponible",
        "yes": "Sí",
        "no": "No",
        "mode_distribution": "Distribución por modo",
        "mode": "Modo",
        "unregistered": "No registrado",
        "latest_questions": "Últimas preguntas",
        "question": "Pregunta",
        "sources": "Fuentes",
        "date": "Fecha",
        "latency": "Latencia",
        "logs_table": "Logs RAG",
        "export": "Exportación",
        "download_csv": "Descargar logs RAG en CSV",
        "export_unavailable": (
            "La exportación se habilitará cuando existan logs reales."
        ),
    },
    "fr": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 Observabilité RAG",
        "subtitle": (
            "Supervision opérationnelle des flux réels de "
            "récupération, génération, sécurité et fallback."
        ),
        "source_status": "État de la source de données",
        "source_connected": "Source connectée",
        "source_empty": (
            "Source connectée, mais aucun log n’est encore enregistré"
        ),
        "source_error": "Impossible de consulter les logs RAG",
        "waiting_real_data": "En attente de données réelles",
        "no_logs": "Aucun log RAG n’a été trouvé.",
        "questions": "Questions",
        "security": "Sécurité",
        "average_latency": "Latence moyenne",
        "maximum_latency": "Latence maximale",
        "not_available": "Indisponible",
        "field_coverage": "Couverture des champs",
        "field": "Champ",
        "available_rows": "Enregistrements renseignés",
        "total_rows": "Total des enregistrements",
        "coverage": "Couverture",
        "available": "Disponible",
        "yes": "Oui",
        "no": "Non",
        "mode_distribution": "Répartition par mode",
        "mode": "Mode",
        "unregistered": "Non enregistré",
        "latest_questions": "Dernières questions",
        "question": "Question",
        "sources": "Sources",
        "date": "Date",
        "latency": "Latence",
        "logs_table": "Logs RAG",
        "export": "Exportation",
        "download_csv": "Télécharger les logs RAG en CSV",
    },
    "de": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 RAG-Beobachtbarkeit",
        "subtitle": (
            "Operative Überwachung realer Abruf-, Generierungs-, "
            "Sicherheits- und Fallback-Abläufe."
        ),
        "source_status": "Status der Datenquelle",
        "source_connected": "Datenquelle verbunden",
        "source_empty": (
            "Datenquelle verbunden, aber noch keine Logs vorhanden"
        ),
        "source_error": "RAG-Logs konnten nicht abgefragt werden",
        "waiting_real_data": "Warten auf reale Daten",
        "no_logs": "Keine RAG-Logs gefunden.",
        "questions": "Fragen",
        "security": "Sicherheit",
        "average_latency": "Durchschnittliche Latenz",
        "maximum_latency": "Maximale Latenz",
        "not_available": "Nicht verfügbar",
        "field_coverage": "Feldabdeckung",
        "field": "Feld",
        "available_rows": "Ausgefüllte Datensätze",
        "total_rows": "Gesamtdatensätze",
        "coverage": "Abdeckung",
        "available": "Verfügbar",
        "yes": "Ja",
        "no": "Nein",
        "mode_distribution": "Verteilung nach Modus",
        "mode": "Modus",
        "unregistered": "Nicht erfasst",
        "latest_questions": "Letzte Fragen",
        "question": "Frage",
        "sources": "Quellen",
        "date": "Datum",
        "latency": "Latenz",
        "logs_table": "RAG-Logs",
        "export": "Export",
        "download_csv": "RAG-Logs als CSV herunterladen",
    },
    "it": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 Osservabilità RAG",
        "source_status": "Stato della fonte dati",
        "source_connected": "Fonte collegata",
        "source_empty": (
            "Fonte collegata, ma non sono ancora presenti log"
        ),
        "source_error": "Impossibile consultare i log RAG",
        "waiting_real_data": "In attesa di dati reali",
        "no_logs": "Nessun log RAG trovato.",
        "questions": "Domande",
        "security": "Sicurezza",
        "average_latency": "Latenza media",
        "maximum_latency": "Latenza massima",
        "not_available": "Non disponibile",
        "field_coverage": "Copertura dei campi",
        "field": "Campo",
        "available_rows": "Record compilati",
        "total_rows": "Record totali",
        "coverage": "Copertura",
        "available": "Disponibile",
        "yes": "Sì",
        "no": "No",
        "mode_distribution": "Distribuzione per modalità",
        "mode": "Modalità",
        "unregistered": "Non registrato",
        "latest_questions": "Ultime domande",
        "question": "Domanda",
        "sources": "Fonti",
        "date": "Data",
        "latency": "Latenza",
        "logs_table": "Log RAG",
        "export": "Esportazione",
        "download_csv": "Scarica i log RAG in CSV",
    },
    "ro": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 Observabilitate RAG",
        "source_status": "Starea sursei de date",
        "source_connected": "Sursă conectată",
        "source_empty": (
            "Sursa este conectată, dar nu există încă loguri"
        ),
        "source_error": "Logurile RAG nu au putut fi interogate",
        "waiting_real_data": "Se așteaptă date reale",
        "no_logs": "Nu au fost găsite loguri RAG.",
        "questions": "Întrebări",
        "security": "Siguranță",
        "average_latency": "Latență medie",
        "maximum_latency": "Latență maximă",
        "not_available": "Indisponibil",
        "field_coverage": "Acoperirea câmpurilor",
        "field": "Câmp",
        "available_rows": "Înregistrări completate",
        "total_rows": "Total înregistrări",
        "coverage": "Acoperire",
        "available": "Disponibil",
        "yes": "Da",
        "no": "Nu",
        "mode_distribution": "Distribuție după mod",
        "mode": "Mod",
        "unregistered": "Neînregistrat",
        "latest_questions": "Ultimele întrebări",
        "question": "Întrebare",
        "sources": "Surse",
        "date": "Dată",
        "latency": "Latență",
        "logs_table": "Loguri RAG",
        "export": "Export",
        "download_csv": "Descărcați logurile RAG în CSV",
    },
    "ua": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 Спостережуваність RAG",
        "source_status": "Стан джерела даних",
        "source_connected": "Джерело підключено",
        "source_empty": (
            "Джерело підключено, але журналів ще немає"
        ),
        "source_error": "Не вдалося отримати журнали RAG",
        "waiting_real_data": "Очікування реальних даних",
        "no_logs": "Журналів RAG не знайдено.",
        "questions": "Запитання",
        "security": "Безпека",
        "average_latency": "Середня затримка",
        "maximum_latency": "Максимальна затримка",
        "not_available": "Недоступно",
        "field_coverage": "Покриття полів",
        "field": "Поле",
        "available_rows": "Заповнені записи",
        "total_rows": "Усього записів",
        "coverage": "Покриття",
        "available": "Доступно",
        "yes": "Так",
        "no": "Ні",
        "mode_distribution": "Розподіл за режимом",
        "mode": "Режим",
        "unregistered": "Не зареєстровано",
        "latest_questions": "Останні запитання",
        "question": "Запитання",
        "sources": "Джерела",
        "date": "Дата",
        "latency": "Затримка",
        "logs_table": "Журнали RAG",
        "export": "Експорт",
        "download_csv": "Завантажити журнали RAG у CSV",
    },
    "ru": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 Наблюдаемость RAG",
        "source_status": "Состояние источника данных",
        "source_connected": "Источник подключён",
        "source_empty": (
            "Источник подключён, но журналы ещё не зарегистрированы"
        ),
        "source_error": "Не удалось получить журналы RAG",
        "waiting_real_data": "Ожидание реальных данных",
        "no_logs": "Журналы RAG не найдены.",
        "questions": "Вопросы",
        "security": "Безопасность",
        "average_latency": "Средняя задержка",
        "maximum_latency": "Максимальная задержка",
        "not_available": "Недоступно",
        "field_coverage": "Покрытие полей",
        "field": "Поле",
        "available_rows": "Заполненные записи",
        "total_rows": "Всего записей",
        "coverage": "Покрытие",
        "available": "Доступно",
        "yes": "Да",
        "no": "Нет",
        "mode_distribution": "Распределение по режимам",
        "mode": "Режим",
        "unregistered": "Не зарегистрировано",
        "latest_questions": "Последние вопросы",
        "question": "Вопрос",
        "sources": "Источники",
        "date": "Дата",
        "latency": "Задержка",
        "logs_table": "Журналы RAG",
        "export": "Экспорт",
        "download_csv": "Скачать журналы RAG в CSV",
    },
    "sa": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 مراقبة RAG",
        "source_status": "حالة مصدر البيانات",
        "source_connected": "المصدر متصل",
        "source_empty": (
            "المصدر متصل، ولكن لم يتم تسجيل سجلات بعد"
        ),
        "source_error": "تعذر الاستعلام عن سجلات RAG",
        "waiting_real_data": "بانتظار بيانات حقيقية",
        "no_logs": "لم يتم العثور على سجلات RAG.",
        "questions": "الأسئلة",
        "security": "الأمان",
        "average_latency": "متوسط زمن الاستجابة",
        "maximum_latency": "أقصى زمن استجابة",
        "not_available": "غير متاح",
        "field_coverage": "تغطية الحقول",
        "field": "الحقل",
        "available_rows": "السجلات المكتملة",
        "total_rows": "إجمالي السجلات",
        "coverage": "التغطية",
        "available": "متاح",
        "yes": "نعم",
        "no": "لا",
        "mode_distribution": "التوزيع حسب الوضع",
        "mode": "الوضع",
        "unregistered": "غير مسجل",
        "latest_questions": "أحدث الأسئلة",
        "question": "السؤال",
        "sources": "المصادر",
        "date": "التاريخ",
        "latency": "زمن الاستجابة",
        "logs_table": "سجلات RAG",
        "export": "التصدير",
        "download_csv": "تنزيل سجلات RAG بصيغة CSV",
    },
    "ch": {
        **RAG_OBSERVABILITY_TEXTS["en_us"],
        "title": "📊 RAG 可观测性",
        "source_status": "数据源状态",
        "source_connected": "数据源已连接",
        "source_empty": "数据源已连接，但尚未记录日志",
        "source_error": "无法查询 RAG 日志",
        "waiting_real_data": "等待真实数据",
        "no_logs": "未找到 RAG 日志。",
        "questions": "问题",
        "security": "安全",
        "average_latency": "平均延迟",
        "maximum_latency": "最大延迟",
        "not_available": "不可用",
        "field_coverage": "字段覆盖率",
        "field": "字段",
        "available_rows": "已填写记录",
        "total_rows": "记录总数",
        "coverage": "覆盖率",
        "available": "可用",
        "yes": "是",
        "no": "否",
        "mode_distribution": "按模式分布",
        "mode": "模式",
        "unregistered": "未记录",
        "latest_questions": "最新问题",
        "question": "问题",
        "sources": "来源",
        "date": "日期",
        "latency": "延迟",
        "logs_table": "RAG 日志",
        "export": "导出",
        "download_csv": "下载 RAG 日志 CSV",
    },
}


RAG_OBSERVABILITY_TEXTS.update(
    RAG_OBSERVABILITY_NATIVE_OVERRIDES
)


RAG_OBSERVABILITY_FULL_NATIVE_TRANSLATIONS = {
    "es": {
        "source_table": "Tabla consultada",
        "field_coverage_caption": (
            "Porcentaje de registros que contienen cada campo completado."
        ),
        "no": "No",
        "mode_distribution_caption": (
            "Cantidad real de logs registrada para cada modo RAG."
        ),
        "total": "Total",
        "latest_questions_caption": (
            "Registros más recientes disponibles en la fuente de datos."
        ),
        "export_caption": (
            "El archivo contiene únicamente los registros reales cargados."
        ),
        "field_pergunta": "Pregunta",
        "field_modo": "Modo",
        "field_fontes": "Fuentes",
        "field_data_hora": "Fecha y hora",
        "field_tempo_ms": "Latencia",
        "field_seguranca": "Seguridad",
    },
    "fr": {
        "real_data_notice": (
            "Cette page utilise uniquement les enregistrements réels "
            "de la table rag_logs."
        ),
        "source_table": "Table interrogée",
        "questions": "Questions",
        "field_coverage_caption": (
            "Pourcentage d’enregistrements dont chaque champ est renseigné."
        ),
        "mode_distribution_caption": (
            "Nombre réel de logs enregistrés pour chaque mode RAG."
        ),
        "mode": "Mode",
        "total": "Total",
        "latest_questions_caption": (
            "Enregistrements les plus récents disponibles dans "
            "la source de données."
        ),
        "question": "Question",
        "sources": "Sources",
        "date": "Date",
        "export_caption": (
            "Le fichier contient uniquement les enregistrements réels chargés."
        ),
        "export_unavailable": (
            "L’exportation sera disponible lorsque des logs réels existeront."
        ),
        "field_pergunta": "Question",
        "field_modo": "Mode",
        "field_fontes": "Sources",
        "field_data_hora": "Date et heure",
        "field_tempo_ms": "Latence",
        "field_seguranca": "Sécurité",
    },
    "de": {
        "real_data_notice": (
            "Diese Seite verwendet ausschließlich reale Datensätze "
            "aus der Tabelle rag_logs."
        ),
        "source_table": "Abgefragte Tabelle",
        "field_coverage_caption": (
            "Prozentsatz der Datensätze, in denen das jeweilige Feld "
            "ausgefüllt ist."
        ),
        "mode_distribution_caption": (
            "Tatsächliche Anzahl der für jeden RAG-Modus "
            "gespeicherten Logs."
        ),
        "total": "Gesamt",
        "latest_questions_caption": (
            "Neueste in der Datenquelle verfügbare Datensätze."
        ),
        "export": "Export",
        "export_caption": (
            "Die Datei enthält ausschließlich die tatsächlich "
            "geladenen Datensätze."
        ),
        "export_unavailable": (
            "Der Export wird aktiviert, sobald reale Logs verfügbar sind."
        ),
        "field_pergunta": "Frage",
        "field_modo": "Modus",
        "field_fontes": "Quellen",
        "field_data_hora": "Datum und Uhrzeit",
        "field_tempo_ms": "Latenz",
        "field_seguranca": "Sicherheit",
    },
    "it": {
        "subtitle": (
            "Monitoraggio operativo dei flussi reali di recupero, "
            "generazione, sicurezza e fallback."
        ),
        "real_data_notice": (
            "Questa pagina utilizza esclusivamente record reali "
            "della tabella rag_logs."
        ),
        "source_table": "Tabella interrogata",
        "field_coverage_caption": (
            "Percentuale di record nei quali ciascun campo è compilato."
        ),
        "no": "No",
        "mode_distribution_caption": (
            "Numero reale di log registrati per ciascuna modalità RAG."
        ),
        "total": "Totale",
        "latest_questions_caption": (
            "Record più recenti disponibili nella fonte dati."
        ),
        "export_caption": (
            "Il file contiene esclusivamente i record reali caricati."
        ),
        "export_unavailable": (
            "L’esportazione sarà disponibile quando saranno presenti "
            "log reali."
        ),
        "field_pergunta": "Domanda",
        "field_modo": "Modalità",
        "field_fontes": "Fonti",
        "field_data_hora": "Data e ora",
        "field_tempo_ms": "Latenza",
        "field_seguranca": "Sicurezza",
    },
    "ro": {
        "subtitle": (
            "Monitorizarea operațională a fluxurilor reale de "
            "recuperare, generare, siguranță și fallback."
        ),
        "real_data_notice": (
            "Această pagină utilizează numai înregistrări reale "
            "din tabelul rag_logs."
        ),
        "source_table": "Tabel interogat",
        "field_coverage_caption": (
            "Procentul înregistrărilor în care fiecare câmp este completat."
        ),
        "mode_distribution_caption": (
            "Numărul real de loguri înregistrate pentru fiecare mod RAG."
        ),
        "total": "Total",
        "latest_questions_caption": (
            "Cele mai recente înregistrări disponibile în sursa de date."
        ),
        "export": "Export",
        "export_caption": (
            "Fișierul conține numai înregistrările reale încărcate."
        ),
        "export_unavailable": (
            "Exportul va fi activat când vor exista loguri reale."
        ),
        "field_pergunta": "Întrebare",
        "field_modo": "Mod",
        "field_fontes": "Surse",
        "field_data_hora": "Data și ora",
        "field_tempo_ms": "Latență",
        "field_seguranca": "Siguranță",
    },
    "ua": {
        "subtitle": (
            "Операційний моніторинг реальних процесів пошуку, "
            "генерації, безпеки та резервного режиму."
        ),
        "real_data_notice": (
            "Ця сторінка використовує лише реальні записи "
            "з таблиці rag_logs."
        ),
        "source_table": "Таблиця запиту",
        "field_coverage_caption": (
            "Відсоток записів, у яких заповнене кожне відповідне поле."
        ),
        "mode_distribution_caption": (
            "Фактична кількість журналів, зареєстрованих "
            "для кожного режиму RAG."
        ),
        "total": "Усього",
        "latest_questions_caption": (
            "Найновіші записи, доступні в джерелі даних."
        ),
        "export_caption": (
            "Файл містить лише фактично завантажені реальні записи."
        ),
        "export_unavailable": (
            "Експорт стане доступним після появи реальних журналів."
        ),
        "field_pergunta": "Запитання",
        "field_modo": "Режим",
        "field_fontes": "Джерела",
        "field_data_hora": "Дата й час",
        "field_tempo_ms": "Затримка",
        "field_seguranca": "Безпека",
    },
    "ru": {
        "subtitle": (
            "Операционный мониторинг реальных процессов поиска, "
            "генерации, безопасности и резервного режима."
        ),
        "real_data_notice": (
            "Эта страница использует только реальные записи "
            "из таблицы rag_logs."
        ),
        "source_table": "Запрашиваемая таблица",
        "field_coverage_caption": (
            "Процент записей, в которых заполнено каждое соответствующее поле."
        ),
        "mode_distribution_caption": (
            "Фактическое количество журналов, зарегистрированных "
            "для каждого режима RAG."
        ),
        "total": "Всего",
        "latest_questions_caption": (
            "Самые последние записи, доступные в источнике данных."
        ),
        "export_caption": (
            "Файл содержит только фактически загруженные реальные записи."
        ),
        "export_unavailable": (
            "Экспорт станет доступен после появления реальных журналов."
        ),
        "field_pergunta": "Вопрос",
        "field_modo": "Режим",
        "field_fontes": "Источники",
        "field_data_hora": "Дата и время",
        "field_tempo_ms": "Задержка",
        "field_seguranca": "Безопасность",
    },
    "sa": {
        "subtitle": (
            "مراقبة تشغيلية لعمليات الاسترجاع والتوليد والأمان "
            "والوضع الاحتياطي باستخدام البيانات الحقيقية."
        ),
        "real_data_notice": (
            "تستخدم هذه الصفحة السجلات الحقيقية فقط من جدول rag_logs."
        ),
        "source_table": "الجدول الذي تم الاستعلام عنه",
        "field_coverage_caption": (
            "النسبة المئوية للسجلات التي يحتوي فيها كل حقل "
            "على قيمة مكتملة."
        ),
        "mode_distribution_caption": (
            "العدد الفعلي للسجلات المسجلة لكل وضع من أوضاع RAG."
        ),
        "total": "الإجمالي",
        "latest_questions_caption": (
            "أحدث السجلات المتوفرة في مصدر البيانات."
        ),
        "export_caption": (
            "يحتوي الملف فقط على السجلات الحقيقية التي تم تحميلها."
        ),
        "export_unavailable": (
            "سيتم تفعيل التصدير عند توفر سجلات حقيقية."
        ),
        "field_pergunta": "السؤال",
        "field_modo": "الوضع",
        "field_fontes": "المصادر",
        "field_data_hora": "التاريخ والوقت",
        "field_tempo_ms": "زمن الاستجابة",
        "field_seguranca": "الأمان",
    },
    "ch": {
        "subtitle": (
            "对真实检索、生成、安全和回退流程进行运行监控。"
        ),
        "real_data_notice": (
            "此页面仅使用 rag_logs 表中的真实记录。"
        ),
        "source_table": "查询的数据表",
        "field_coverage_caption": (
            "每个字段已填写记录所占的百分比。"
        ),
        "mode_distribution_caption": (
            "每种 RAG 模式实际记录的日志数量。"
        ),
        "total": "总计",
        "latest_questions_caption": (
            "数据源中可用的最新记录。"
        ),
        "export_caption": (
            "该文件仅包含实际加载的真实记录。"
        ),
        "export_unavailable": (
            "存在真实日志后将启用导出功能。"
        ),
        "field_pergunta": "问题",
        "field_modo": "模式",
        "field_fontes": "来源",
        "field_data_hora": "日期和时间",
        "field_tempo_ms": "延迟",
        "field_seguranca": "安全",
    },
}

for language, translations in (
    RAG_OBSERVABILITY_FULL_NATIVE_TRANSLATIONS.items()
):
    RAG_OBSERVABILITY_TEXTS[
        language
    ].update(
        translations
    )

# Rótulos técnicos contextualizados em russo.
RAG_OBSERVABILITY_TEXTS["ru"].update({
    "gemini": "Модель Gemini",
    "fallback": "Резервный режим (Fallback)",
    "field_gemini": "Использование Gemini",
    "field_fallback": "Резервный режим (Fallback)",
})
