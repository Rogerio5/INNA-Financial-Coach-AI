from __future__ import annotations

CORE_KEYS: tuple[str, ...] = (
    "title",
    "subtitle",
    "description",
    "history_settings",
    "history_file",
    "load_error",
    "filters",
    "branches",
    "environments",
    "status",
    "all_statuses",
    "approved",
    "failed",
    "partial",
    "runs",
    "comparable_runs",
    "approval_rate",
    "latest_score",
    "best_score",
    "incomplete_runs",
    "no_history",
    "timeline",
    "timeline_caption",
    "comparison",
    "comparison_caption",
    "baseline",
    "candidate",
    "tolerance",
    "tolerance_help",
    "need_two_runs",
    "same_run",
    "comparison_unavailable",
    "aggregate_result",
    "baseline_score",
    "candidate_score",
    "delta",
    "classification",
    "improved",
    "stable",
    "regressed",
    "unavailable",
    "candidate_approved",
    "candidate_failed",
    "candidate_unknown",
    "axis_comparison",
    "comparison_chart",
    "history_table",
    "run_reference",
    "recorded_at",
    "branch",
    "environment",
    "triad_score",
    "triad_status",
    "triad_passed",
    "complete",
    "metric",
    "score",
    "answer_relevancy",
    "faithfulness",
    "contextual_relevancy",
    "rag_triad_average",
    "latest_run",
    "best_run",
    "status_passed",
    "status_failed",
    "status_partial",
    "status_unavailable",
)

def _build_language(
    values: tuple[str, ...],
) -> dict[str, str]:
    if len(values) != len(CORE_KEYS):
        raise RuntimeError(
            "Contrato de tradução inválido: "
            f"{len(values)} valores para "
            f"{len(CORE_KEYS)} chaves."
        )

    return dict(
        zip(
            CORE_KEYS,
            values,
            strict=True,
        )
    )

RAG_LAB_CORE_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "en_gb": _build_language(
        (
            "🧪 RAG Quality Laboratory",
            (
                "Professional RAG Triad evaluation, "
                "experimentation and comparison."
            ),
            (
                "Compare real runs using Answer Relevancy, "
                "Faithfulness and Contextual Relevancy."
            ),
            "Data source",
            "History file",
            "Unable to load evaluation history",
            "Laboratory filters",
            "Branches",
            "Environments",
            "Status",
            "All",
            "Approved",
            "Failed",
            "Partial or unavailable",
            "RAG Triad runs",
            "Comparable runs",
            "Approval rate",
            "Latest score",
            "Best score",
            "Incomplete runs",
            (
                "No RAG Triad run was found for the "
                "selected filters."
            ),
            "RAG quality evolution",
            (
                "History of the three axes and "
                "aggregate score."
            ),
            "Experiment comparison",
            (
                "Select a reference run and a "
                "candidate run."
            ),
            "Baseline",
            "Candidate",
            "Stability tolerance",
            (
                "Differences within the tolerance "
                "are classified as stable."
            ),
            (
                "At least two complete runs are "
                "required for comparison."
            ),
            "Baseline and candidate must be different.",
            (
                "The comparison could not be built "
                "with the selected runs."
            ),
            "Aggregate result",
            "Baseline score",
            "Candidate score",
            "Difference",
            "Classification",
            "Improved",
            "Stable",
            "Regressed",
            "Unavailable",
            "Candidate approved",
            "Candidate failed",
            (
                "The candidate does not have a "
                "conclusive result."
            ),
            "Axis comparison",
            "Baseline × candidate",
            "Run history",
            "Run",
            "Date",
            "Branch",
            "Environment",
            "RAG Triad score",
            "RAG Triad status",
            "Approved",
            "Complete",
            "Metric",
            "Score",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "RAG Triad average",
            "Latest run",
            "Best run",
            "Approved",
            "Failed",
            "Partial",
            "Unavailable",
        )
    ),
    "es": _build_language(
        (
            "🧪 Laboratorio de Calidad RAG",
            (
                "Evaluación, experimentación y comparación "
                "profesional de la Tríada RAG."
            ),
            (
                "Compare ejecuciones reales mediante Answer "
                "Relevancy, Faithfulness y Contextual Relevancy."
            ),
            "Fuente de datos",
            "Archivo del historial",
            "No se pudo cargar el historial de evaluaciones",
            "Filtros del laboratorio",
            "Ramas",
            "Entornos",
            "Estado",
            "Todos",
            "Aprobadas",
            "Reprobadas",
            "Parciales o no disponibles",
            "Ejecuciones de la Tríada RAG",
            "Ejecuciones comparables",
            "Tasa de aprobación",
            "Puntuación más reciente",
            "Mejor puntuación",
            "Ejecuciones incompletas",
            (
                "No se encontró ninguna ejecución de la "
                "Tríada RAG para los filtros seleccionados."
            ),
            "Evolución de la calidad RAG",
            (
                "Historial de los tres ejes y de la "
                "puntuación agregada."
            ),
            "Comparación de experimentos",
            (
                "Seleccione una ejecución de referencia "
                "y una ejecución candidata."
            ),
            "Línea base",
            "Candidata",
            "Tolerancia de estabilidad",
            (
                "Las diferencias dentro de la tolerancia "
                "se clasifican como estables."
            ),
            (
                "Se necesitan al menos dos ejecuciones "
                "completas para realizar una comparación."
            ),
            (
                "La línea base y la candidata deben "
                "ser diferentes."
            ),
            (
                "No fue posible construir la comparación "
                "con las ejecuciones seleccionadas."
            ),
            "Resultado agregado",
            "Puntuación de la línea base",
            "Puntuación de la candidata",
            "Diferencia",
            "Clasificación",
            "Mejora",
            "Estable",
            "Regresión",
            "No disponible",
            "Candidata aprobada",
            "Candidata reprobada",
            (
                "La candidata todavía no tiene un "
                "resultado concluyente."
            ),
            "Comparación por eje",
            "Línea base × candidata",
            "Historial de ejecuciones",
            "Ejecución",
            "Fecha",
            "Rama",
            "Entorno",
            "Puntuación de la Tríada RAG",
            "Estado de la Tríada RAG",
            "Aprobada",
            "Completa",
            "Métrica",
            "Puntuación",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "Promedio de la Tríada RAG",
            "Última ejecución",
            "Mejor ejecución",
            "Aprobada",
            "Reprobada",
            "Parcial",
            "No disponible",
        )
    ),
    "fr": _build_language(
        (
            "🧪 Laboratoire de Qualité RAG",
            (
                "Évaluation, expérimentation et comparaison "
                "professionnelles de la Triade RAG."
            ),
            (
                "Comparez des exécutions réelles avec Answer "
                "Relevancy, Faithfulness et Contextual Relevancy."
            ),
            "Source des données",
            "Fichier d’historique",
            (
                "Impossible de charger l’historique "
                "des évaluations"
            ),
            "Filtres du laboratoire",
            "Branches",
            "Environnements",
            "État",
            "Tous",
            "Approuvées",
            "Échouées",
            "Partielles ou indisponibles",
            "Exécutions de la Triade RAG",
            "Exécutions comparables",
            "Taux d’approbation",
            "Score le plus récent",
            "Meilleur score",
            "Exécutions incomplètes",
            (
                "Aucune exécution de la Triade RAG "
                "ne correspond aux filtres sélectionnés."
            ),
            "Évolution de la qualité RAG",
            (
                "Historique des trois axes et du "
                "score agrégé."
            ),
            "Comparaison des expériences",
            (
                "Sélectionnez une exécution de référence "
                "et une exécution candidate."
            ),
            "Référence",
            "Candidate",
            "Tolérance de stabilité",
            (
                "Les différences comprises dans la "
                "tolérance sont classées comme stables."
            ),
            (
                "Au moins deux exécutions complètes sont "
                "nécessaires pour effectuer une comparaison."
            ),
            (
                "La référence et la candidate doivent "
                "être différentes."
            ),
            (
                "La comparaison n’a pas pu être construite "
                "avec les exécutions sélectionnées."
            ),
            "Résultat agrégé",
            "Score de la référence",
            "Score de la candidate",
            "Différence",
            "Classification",
            "Amélioration",
            "Stable",
            "Régression",
            "Indisponible",
            "Candidate approuvée",
            "Candidate échouée",
            (
                "La candidate ne possède pas encore "
                "de résultat concluant."
            ),
            "Comparaison par axe",
            "Référence × candidate",
            "Historique des exécutions",
            "Exécution",
            "Date",
            "Branche",
            "Environnement",
            "Score de la Triade RAG",
            "État de la Triade RAG",
            "Approuvée",
            "Complète",
            "Métrique",
            "Score",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "Moyenne de la Triade RAG",
            "Dernière exécution",
            "Meilleure exécution",
            "Approuvée",
            "Échouée",
            "Partielle",
            "Indisponible",
        )
    ),
    "de": _build_language(
        (
            "🧪 RAG-Qualitätslabor",
            (
                "Professionelle Bewertung, Experimente "
                "und Vergleiche der RAG-Triade."
            ),
            (
                "Vergleichen Sie reale Ausführungen anhand "
                "von Answer Relevancy, Faithfulness und "
                "Contextual Relevancy."
            ),
            "Datenquelle",
            "Verlaufsdatei",
            (
                "Der Bewertungsverlauf konnte nicht "
                "geladen werden"
            ),
            "Laborfilter",
            "Branches",
            "Umgebungen",
            "Status",
            "Alle",
            "Bestanden",
            "Fehlgeschlagen",
            "Teilweise oder nicht verfügbar",
            "RAG-Triade-Ausführungen",
            "Vergleichbare Ausführungen",
            "Erfolgsquote",
            "Neuester Score",
            "Bester Score",
            "Unvollständige Ausführungen",
            (
                "Für die ausgewählten Filter wurde keine "
                "RAG-Triade-Ausführung gefunden."
            ),
            "Entwicklung der RAG-Qualität",
            (
                "Verlauf der drei Achsen und des "
                "aggregierten Scores."
            ),
            "Experimentvergleich",
            (
                "Wählen Sie eine Referenzausführung und "
                "eine Kandidatenausführung aus."
            ),
            "Baseline",
            "Kandidat",
            "Stabilitätstoleranz",
            (
                "Abweichungen innerhalb der Toleranz "
                "werden als stabil eingestuft."
            ),
            (
                "Für einen Vergleich sind mindestens zwei "
                "vollständige Ausführungen erforderlich."
            ),
            (
                "Baseline und Kandidat müssen "
                "unterschiedlich sein."
            ),
            (
                "Der Vergleich konnte mit den ausgewählten "
                "Ausführungen nicht erstellt werden."
            ),
            "Aggregiertes Ergebnis",
            "Baseline-Score",
            "Kandidaten-Score",
            "Differenz",
            "Klassifizierung",
            "Verbesserung",
            "Stabil",
            "Regression",
            "Nicht verfügbar",
            "Kandidat bestanden",
            "Kandidat fehlgeschlagen",
            (
                "Für den Kandidaten liegt noch kein "
                "eindeutiges Ergebnis vor."
            ),
            "Vergleich nach Achse",
            "Baseline × Kandidat",
            "Ausführungsverlauf",
            "Ausführung",
            "Datum",
            "Branch",
            "Umgebung",
            "RAG-Triade-Score",
            "RAG-Triade-Status",
            "Bestanden",
            "Vollständig",
            "Metrik",
            "Score",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "RAG-Triade-Durchschnitt",
            "Neueste Ausführung",
            "Beste Ausführung",
            "Bestanden",
            "Fehlgeschlagen",
            "Teilweise",
            "Nicht verfügbar",
        )
    ),
    "it": _build_language(
        (
            "🧪 Laboratorio di Qualità RAG",
            (
                "Valutazione, sperimentazione e confronto "
                "professionale della Triade RAG."
            ),
            (
                "Confronta esecuzioni reali utilizzando Answer "
                "Relevancy, Faithfulness e Contextual Relevancy."
            ),
            "Origine dati",
            "File della cronologia",
            (
                "Impossibile caricare la cronologia "
                "delle valutazioni"
            ),
            "Filtri del laboratorio",
            "Branch",
            "Ambienti",
            "Stato",
            "Tutti",
            "Approvate",
            "Non approvate",
            "Parziali o non disponibili",
            "Esecuzioni della Triade RAG",
            "Esecuzioni confrontabili",
            "Tasso di approvazione",
            "Punteggio più recente",
            "Miglior punteggio",
            "Esecuzioni incomplete",
            (
                "Nessuna esecuzione della Triade RAG è "
                "stata trovata per i filtri selezionati."
            ),
            "Evoluzione della qualità RAG",
            (
                "Cronologia dei tre assi e del "
                "punteggio aggregato."
            ),
            "Confronto degli esperimenti",
            (
                "Seleziona un’esecuzione di riferimento "
                "e un’esecuzione candidata."
            ),
            "Baseline",
            "Candidata",
            "Tolleranza di stabilità",
            (
                "Le differenze comprese nella tolleranza "
                "sono classificate come stabili."
            ),
            (
                "Sono necessarie almeno due esecuzioni "
                "complete per effettuare un confronto."
            ),
            (
                "La baseline e la candidata devono "
                "essere differenti."
            ),
            (
                "Non è stato possibile costruire il confronto "
                "con le esecuzioni selezionate."
            ),
            "Risultato aggregato",
            "Punteggio della baseline",
            "Punteggio della candidata",
            "Differenza",
            "Classificazione",
            "Miglioramento",
            "Stabile",
            "Regressione",
            "Non disponibile",
            "Candidata approvata",
            "Candidata non approvata",
            (
                "La candidata non dispone ancora "
                "di un risultato conclusivo."
            ),
            "Confronto per asse",
            "Baseline × candidata",
            "Cronologia delle esecuzioni",
            "Esecuzione",
            "Data",
            "Branch",
            "Ambiente",
            "Punteggio della Triade RAG",
            "Stato della Triade RAG",
            "Approvata",
            "Completa",
            "Metrica",
            "Punteggio",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "Media della Triade RAG",
            "Ultima esecuzione",
            "Migliore esecuzione",
            "Approvata",
            "Non approvata",
            "Parziale",
            "Non disponibile",
        )
    ),
    "ro": _build_language(
        (
            "🧪 Laborator de Calitate RAG",
            (
                "Evaluare, experimentare și comparare "
                "profesională a Triadei RAG."
            ),
            (
                "Comparați execuții reale utilizând Answer "
                "Relevancy, Faithfulness și Contextual Relevancy."
            ),
            "Sursa datelor",
            "Fișierul istoricului",
            (
                "Istoricul evaluărilor nu a putut "
                "fi încărcat"
            ),
            "Filtrele laboratorului",
            "Ramuri",
            "Medii",
            "Stare",
            "Toate",
            "Aprobate",
            "Respinse",
            "Parțiale sau indisponibile",
            "Execuții ale Triadei RAG",
            "Execuții comparabile",
            "Rata de aprobare",
            "Cel mai recent scor",
            "Cel mai bun scor",
            "Execuții incomplete",
            (
                "Nu a fost găsită nicio execuție a Triadei "
                "RAG pentru filtrele selectate."
            ),
            "Evoluția calității RAG",
            (
                "Istoricul celor trei axe și al "
                "scorului agregat."
            ),
            "Compararea experimentelor",
            (
                "Selectați o execuție de referință "
                "și o execuție candidată."
            ),
            "Referință",
            "Candidată",
            "Toleranța de stabilitate",
            (
                "Diferențele aflate în limita toleranței "
                "sunt clasificate drept stabile."
            ),
            (
                "Sunt necesare cel puțin două execuții "
                "complete pentru comparație."
            ),
            (
                "Referința și candidata trebuie "
                "să fie diferite."
            ),
            (
                "Comparația nu a putut fi construită "
                "cu execuțiile selectate."
            ),
            "Rezultat agregat",
            "Scorul referinței",
            "Scorul candidatei",
            "Diferență",
            "Clasificare",
            "Îmbunătățire",
            "Stabil",
            "Regresie",
            "Indisponibil",
            "Candidată aprobată",
            "Candidată respinsă",
            (
                "Candidata nu are încă un "
                "rezultat concludent."
            ),
            "Comparație pe axe",
            "Referință × candidată",
            "Istoricul execuțiilor",
            "Execuție",
            "Dată",
            "Ramură",
            "Mediu",
            "Scorul Triadei RAG",
            "Starea Triadei RAG",
            "Aprobată",
            "Completă",
            "Metrică",
            "Scor",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "Media Triadei RAG",
            "Cea mai recentă execuție",
            "Cea mai bună execuție",
            "Aprobată",
            "Respinsă",
            "Parțială",
            "Indisponibilă",
        )
    ),
    "ua": _build_language(
        (
            "🧪 Лабораторія якості RAG",
            (
                "Професійне оцінювання, експериментування "
                "та порівняння тріади RAG."
            ),
            (
                "Порівнюйте реальні запуски за метриками "
                "Answer Relevancy, Faithfulness і "
                "Contextual Relevancy."
            ),
            "Джерело даних",
            "Файл історії",
            "Не вдалося завантажити історію оцінювання",
            "Фільтри лабораторії",
            "Гілки",
            "Середовища",
            "Стан",
            "Усі",
            "Схвалені",
            "Відхилені",
            "Часткові або недоступні",
            "Запуски тріади RAG",
            "Порівнювані запуски",
            "Рівень схвалення",
            "Останній результат",
            "Найкращий результат",
            "Неповні запуски",
            (
                "Для вибраних фільтрів не знайдено "
                "жодного запуску тріади RAG."
            ),
            "Динаміка якості RAG",
            (
                "Історія трьох осей та "
                "агрегованого результату."
            ),
            "Порівняння експериментів",
            (
                "Виберіть еталонний запуск "
                "і запуск-кандидат."
            ),
            "Еталон",
            "Кандидат",
            "Допуск стабільності",
            (
                "Відмінності в межах допуску "
                "класифікуються як стабільні."
            ),
            (
                "Для порівняння потрібні щонайменше "
                "два повні запуски."
            ),
            "Еталон і кандидат мають відрізнятися.",
            (
                "Не вдалося побудувати порівняння "
                "для вибраних запусків."
            ),
            "Агрегований результат",
            "Результат еталона",
            "Результат кандидата",
            "Різниця",
            "Класифікація",
            "Покращення",
            "Стабільно",
            "Регресія",
            "Недоступно",
            "Кандидата схвалено",
            "Кандидата відхилено",
            (
                "Кандидат ще не має "
                "остаточного результату."
            ),
            "Порівняння за осями",
            "Еталон × кандидат",
            "Історія запусків",
            "Запуск",
            "Дата",
            "Гілка",
            "Середовище",
            "Результат тріади RAG",
            "Стан тріади RAG",
            "Схвалено",
            "Повний",
            "Метрика",
            "Результат",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "Середнє тріади RAG",
            "Останній запуск",
            "Найкращий запуск",
            "Схвалено",
            "Відхилено",
            "Частково",
            "Недоступно",
        )
    ),
    "ru": _build_language(
        (
            "🧪 Лаборатория качества RAG",
            (
                "Профессиональная оценка, эксперименты "
                "и сравнение триады RAG."
            ),
            (
                "Сравнивайте реальные запуски по метрикам "
                "Answer Relevancy, Faithfulness и "
                "Contextual Relevancy."
            ),
            "Источник данных",
            "Файл истории",
            "Не удалось загрузить историю оценивания",
            "Фильтры лаборатории",
            "Ветки",
            "Среды",
            "Статус",
            "Все",
            "Одобренные",
            "Отклонённые",
            "Частичные или недоступные",
            "Запуски триады RAG",
            "Сопоставимые запуски",
            "Доля одобрения",
            "Последний результат",
            "Лучший результат",
            "Неполные запуски",
            (
                "Для выбранных фильтров не найдено "
                "ни одного запуска триады RAG."
            ),
            "Динамика качества RAG",
            (
                "История трёх осей и "
                "агрегированного результата."
            ),
            "Сравнение экспериментов",
            (
                "Выберите эталонный запуск "
                "и запуск-кандидат."
            ),
            "Эталон",
            "Кандидат",
            "Допуск стабильности",
            (
                "Различия в пределах допуска "
                "классифицируются как стабильные."
            ),
            (
                "Для сравнения необходимы как минимум "
                "два полных запуска."
            ),
            "Эталон и кандидат должны различаться.",
            (
                "Не удалось построить сравнение "
                "для выбранных запусков."
            ),
            "Агрегированный результат",
            "Результат эталона",
            "Результат кандидата",
            "Разница",
            "Классификация",
            "Улучшение",
            "Стабильно",
            "Регрессия",
            "Недоступно",
            "Кандидат одобрен",
            "Кандидат отклонён",
            (
                "У кандидата пока нет "
                "окончательного результата."
            ),
            "Сравнение по осям",
            "Эталон × кандидат",
            "История запусков",
            "Запуск",
            "Дата",
            "Ветка",
            "Среда",
            "Результат триады RAG",
            "Статус триады RAG",
            "Одобрен",
            "Полный",
            "Метрика",
            "Результат",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "Среднее значение триады RAG",
            "Последний запуск",
            "Лучший запуск",
            "Одобрен",
            "Отклонён",
            "Частичный",
            "Недоступен",
        )
    ),
    "sa": _build_language(
        (
            "🧪 مختبر جودة RAG",
            (
                "تقييم وتجريب ومقارنة احترافية "
                "لثلاثية RAG."
            ),
            (
                "قارن عمليات التشغيل الحقيقية باستخدام "
                "Answer Relevancy وFaithfulness و"
                "Contextual Relevancy."
            ),
            "مصدر البيانات",
            "ملف السجل",
            "تعذر تحميل سجل التقييمات",
            "مرشحات المختبر",
            "الفروع",
            "البيئات",
            "الحالة",
            "الكل",
            "المعتمدة",
            "المرفوضة",
            "جزئية أو غير متاحة",
            "عمليات تشغيل ثلاثية RAG",
            "عمليات التشغيل القابلة للمقارنة",
            "معدل الاعتماد",
            "أحدث نتيجة",
            "أفضل نتيجة",
            "عمليات التشغيل غير المكتملة",
            (
                "لم يتم العثور على أي تشغيل لثلاثية "
                "RAG وفق المرشحات المحددة."
            ),
            "تطور جودة RAG",
            (
                "سجل المحاور الثلاثة "
                "والنتيجة المجمعة."
            ),
            "مقارنة التجارب",
            (
                "حدد تشغيلًا مرجعيًا "
                "وتشغيلًا مرشحًا."
            ),
            "الخط المرجعي",
            "المرشح",
            "هامش الاستقرار",
            (
                "تُصنف الاختلافات الواقعة ضمن "
                "الهامش على أنها مستقرة."
            ),
            (
                "يلزم وجود تشغيلين مكتملين على الأقل "
                "لإجراء المقارنة."
            ),
            (
                "يجب أن يختلف التشغيل المرجعي "
                "عن التشغيل المرشح."
            ),
            (
                "تعذر إنشاء المقارنة باستخدام "
                "عمليات التشغيل المحددة."
            ),
            "النتيجة المجمعة",
            "نتيجة الخط المرجعي",
            "نتيجة المرشح",
            "الفرق",
            "التصنيف",
            "تحسن",
            "مستقر",
            "تراجع",
            "غير متاح",
            "تم اعتماد المرشح",
            "تم رفض المرشح",
            (
                "لا تتوفر للمرشح نتيجة "
                "نهائية حتى الآن."
            ),
            "المقارنة حسب المحور",
            "الخط المرجعي × المرشح",
            "سجل عمليات التشغيل",
            "التشغيل",
            "التاريخ",
            "الفرع",
            "البيئة",
            "نتيجة ثلاثية RAG",
            "حالة ثلاثية RAG",
            "معتمد",
            "مكتمل",
            "المقياس",
            "النتيجة",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "متوسط ثلاثية RAG",
            "أحدث تشغيل",
            "أفضل تشغيل",
            "معتمد",
            "مرفوض",
            "جزئي",
            "غير متاح",
        )
    ),
    "ch": _build_language(
        (
            "🧪 RAG 质量实验室",
            (
                "面向 RAG 三元评估的专业评价、"
                "实验与对比。"
            ),
            (
                "使用 Answer Relevancy、Faithfulness "
                "和 Contextual Relevancy 比较真实运行。"
            ),
            "数据源",
            "历史记录文件",
            "无法加载评估历史记录",
            "实验室筛选条件",
            "分支",
            "环境",
            "状态",
            "全部",
            "已通过",
            "未通过",
            "部分完成或不可用",
            "RAG 三元评估运行",
            "可比较运行",
            "通过率",
            "最新得分",
            "最佳得分",
            "不完整运行",
            (
                "未找到符合所选筛选条件的 "
                "RAG 三元评估运行。"
            ),
            "RAG 质量变化趋势",
            "三个评估维度及综合得分的历史记录。",
            "实验对比",
            "选择一个基准运行和一个候选运行。",
            "基准",
            "候选",
            "稳定性容差",
            "容差范围内的差异将被归类为稳定。",
            "至少需要两个完整运行才能进行比较。",
            "基准运行与候选运行必须不同。",
            "无法使用所选运行构建比较。",
            "综合结果",
            "基准得分",
            "候选得分",
            "差异",
            "分类",
            "提升",
            "稳定",
            "回退",
            "不可用",
            "候选运行已通过",
            "候选运行未通过",
            "候选运行尚无明确结论。",
            "按维度比较",
            "基准 × 候选",
            "运行历史",
            "运行",
            "日期",
            "分支",
            "环境",
            "RAG 三元评估得分",
            "RAG 三元评估状态",
            "已通过",
            "完整",
            "指标",
            "得分",
            "Answer Relevancy",
            "Faithfulness",
            "Contextual Relevancy",
            "RAG 三元评估平均值",
            "最新运行",
            "最佳运行",
            "已通过",
            "未通过",
            "部分完成",
            "不可用",
        )
    ),
}
