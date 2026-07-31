from __future__ import annotations

RAG_LAB_ADVANCED_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "advanced_experiment": "Configuração da execução",
        "advanced_experiment_caption": (
            "Metadados reais registrados para a execução selecionada."
        ),
        "select_run": "Selecionar execução",
        "metadata_coverage": "Cobertura dos metadados",
        "metadata_coverage_caption": (
            "Mostra quantas execuções possuem cada informação registrada."
        ),
        "experimental_comparisons": "Comparações experimentais",
        "experimental_comparisons_caption": (
            "Disponibilidade das análises por estratégia, modelo e configuração."
        ),
        "quality_gate": "Quality Gate",
        "quality_gate_caption": (
            "Limites mínimos aplicados aos scores reais da RAG Triad."
        ),
        "minimum_answer_relevancy": "Answer Relevancy mínimo",
        "minimum_faithfulness": "Faithfulness mínimo",
        "minimum_contextual_relevancy": (
            "Contextual Relevancy mínimo"
        ),
        "minimum_aggregate": "Score agregado mínimo",
        "maximum_regression": "Regressão máxima permitida",
        "gate_passed": "Quality Gate aprovado",
        "gate_failed": "Quality Gate reprovado",
        "gate_incomplete": (
            "Quality Gate inconclusivo por ausência de dados."
        ),
        "ranking": "Ranking das execuções",
        "ranking_caption": (
            "Classificação baseada somente em informações reais disponíveis."
        ),
        "ranking_quality_only": "Somente qualidade",
        "ranking_quality_performance": "Qualidade e performance",
        "performance_cost": "Performance, tokens e custos",
        "cost_per_approved_run": "Custo por execução aprovada",
        "phoenix": "Integração com Phoenix",
        "phoenix_waiting": (
            "Aguardando um identificador real de trace do Phoenix."
        ),
        "case_details": "Detalhamento por caso de teste",
        "case_details_waiting": (
            "Aguardando perguntas, respostas, contextos e scores "
            "individuais registrados no histórico."
        ),
        "exports": "Exportação dos experimentos",
        "export_csv": "Baixar histórico em CSV",
        "export_json": "Baixar relatório em JSON",
        "available": "Disponível",
        "partially_available": "Parcialmente disponível",
        "waiting_real_data": "Aguardando dados reais",
        "no_branch_options": (
            "Nenhuma branch foi encontrada no histórico."
        ),
        "no_environment_options": (
            "Nenhum ambiente foi encontrado no histórico."
        ),
        "not_registered": "Não registrado nesta execução",
        "enabled": "Habilitado",
        "disabled": "Desabilitado",
        "capability_reranker": (
            "Reranker ligado × desligado"
        ),
        "capability_retrieval_strategy": (
            "Híbrida × vetorial × lexical"
        ),
        "capability_model_prompt": (
            "Modelo × versão do prompt"
        ),
        "capability_rag_configuration": (
            "Top K, embedding e chunking"
        ),
        "capability_performance_cost": (
            "Latência, tokens e custos"
        ),
        "capability_phoenix": (
            "Integração das traces do Phoenix"
        ),
        "capability_active_message": (
            "Dados reais disponíveis em todas as execuções."
        ),
        "capability_partial_message": (
            "Somente parte do histórico possui os metadados necessários."
        ),
        "capability_waiting_message": (
            "Aguardando metadados reais nas execuções."
        ),
        "gate_reason_passed": "Limite atendido.",
        "gate_reason_failed": (
            "Score abaixo do limite configurado."
        ),
        "gate_reason_score_missing": (
            "Score não registrado nesta execução."
        ),
        "gate_reason_regression_passed": (
            "Regressão dentro do limite permitido."
        ),
        "gate_reason_regression_failed": (
            "Regressão acima do limite permitido."
        ),
        "gate_reason_regression_unavailable": (
            "Comparação de regressão indisponível."
        ),
        "coverage": "Cobertura",
        "registered_runs": "Execuções registradas",
        "distinct_values": "Valores encontrados",
        "capability": "Recurso",
        "availability": "Disponibilidade",
        "message": "Descrição",
        "position": "Posição",
        "quality_score": "Score de qualidade",
        "failed_metrics": "Métricas reprovadas",
        "latency": "Latência",
        "estimated_cost": "Custo estimado",
        "ranking_basis": "Critério do ranking",
        "threshold": "Limite",
        "result": "Resultado",
        "reason": "Motivo",
        "passed": "Aprovado",
        "failed_label": "Reprovado",
        "inconclusive": "Inconclusivo",
        "field_retrieval_strategy": "Estratégia de busca",
        "field_reranker_enabled": "Reranker",
        "field_top_k": "Top K",
        "field_model_name": "Modelo",
        "field_prompt_version": "Versão do prompt",
        "field_temperature": "Temperatura",
        "field_max_output_tokens": "Limite de tokens",
        "field_embedding_model": "Modelo de embedding",
        "field_knowledge_base_version": "Versão da base",
        "field_chunk_size": "Tamanho do chunk",
        "field_chunk_overlap": "Sobreposição dos chunks",
        "field_dataset_name": "Dataset",
        "field_language": "Idioma",
        "field_latency_ms": "Latência",
        "field_input_tokens": "Tokens de entrada",
        "field_output_tokens": "Tokens de saída",
        "field_estimated_cost_usd": "Custo estimado",
    },
    "en_us": {
        "advanced_experiment": "Run configuration",
        "advanced_experiment_caption": (
            "Real metadata recorded for the selected run."
        ),
        "select_run": "Select run",
        "metadata_coverage": "Metadata coverage",
        "metadata_coverage_caption": (
            "Shows how many runs contain each recorded field."
        ),
        "experimental_comparisons": "Experimental comparisons",
        "experimental_comparisons_caption": (
            "Availability of analyses by strategy, model and configuration."
        ),
        "quality_gate": "Quality Gate",
        "quality_gate_caption": (
            "Minimum thresholds applied to real RAG Triad scores."
        ),
        "minimum_answer_relevancy": "Minimum Answer Relevancy",
        "minimum_faithfulness": "Minimum Faithfulness",
        "minimum_contextual_relevancy": (
            "Minimum Contextual Relevancy"
        ),
        "minimum_aggregate": "Minimum aggregate score",
        "maximum_regression": "Maximum allowed regression",
        "gate_passed": "Quality Gate approved",
        "gate_failed": "Quality Gate failed",
        "gate_incomplete": (
            "Quality Gate is inconclusive due to missing data."
        ),
        "ranking": "Run ranking",
        "ranking_caption": (
            "Ranking based only on real available information."
        ),
        "ranking_quality_only": "Quality only",
        "ranking_quality_performance": "Quality and performance",
        "performance_cost": "Performance, tokens and costs",
        "cost_per_approved_run": "Cost per approved run",
        "phoenix": "Phoenix integration",
        "phoenix_waiting": (
            "Waiting for a real Phoenix trace identifier."
        ),
        "case_details": "Test case details",
        "case_details_waiting": (
            "Waiting for questions, answers, contexts and individual "
            "scores recorded in history."
        ),
        "exports": "Experiment exports",
        "export_csv": "Download history as CSV",
        "export_json": "Download report as JSON",
        "available": "Available",
        "partially_available": "Partially available",
        "waiting_real_data": "Waiting for real data",
        "no_branch_options": (
            "No branch was found in the evaluation history."
        ),
        "no_environment_options": (
            "No environment was found in the evaluation history."
        ),
        "not_registered": "Not recorded for this run",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "capability_reranker": (
            "Reranker enabled × disabled"
        ),
        "capability_retrieval_strategy": (
            "Hybrid × vector × lexical"
        ),
        "capability_model_prompt": (
            "Model × prompt version"
        ),
        "capability_rag_configuration": (
            "Top K, embedding and chunking"
        ),
        "capability_performance_cost": (
            "Latency, tokens and costs"
        ),
        "capability_phoenix": (
            "Phoenix trace integration"
        ),
        "capability_active_message": (
            "Real data is available for every run."
        ),
        "capability_partial_message": (
            "Only part of the history contains the required metadata."
        ),
        "capability_waiting_message": (
            "Waiting for real metadata in the runs."
        ),
        "gate_reason_passed": "Threshold met.",
        "gate_reason_failed": (
            "Score is below the configured threshold."
        ),
        "gate_reason_score_missing": (
            "Score was not recorded for this run."
        ),
        "gate_reason_regression_passed": (
            "Regression is within the allowed limit."
        ),
        "gate_reason_regression_failed": (
            "Regression exceeds the allowed limit."
        ),
        "gate_reason_regression_unavailable": (
            "Regression comparison is unavailable."
        ),
        "coverage": "Coverage",
        "registered_runs": "Recorded runs",
        "distinct_values": "Found values",
        "capability": "Capability",
        "availability": "Availability",
        "message": "Description",
        "position": "Position",
        "quality_score": "Quality score",
        "failed_metrics": "Failed metrics",
        "latency": "Latency",
        "estimated_cost": "Estimated cost",
        "ranking_basis": "Ranking basis",
        "threshold": "Threshold",
        "result": "Result",
        "reason": "Reason",
        "passed": "Passed",
        "failed_label": "Failed",
        "inconclusive": "Inconclusive",
        "field_retrieval_strategy": "Retrieval strategy",
        "field_reranker_enabled": "Reranker",
        "field_top_k": "Top K",
        "field_model_name": "Model",
        "field_prompt_version": "Prompt version",
        "field_temperature": "Temperature",
        "field_max_output_tokens": "Token limit",
        "field_embedding_model": "Embedding model",
        "field_knowledge_base_version": "Knowledge base version",
        "field_chunk_size": "Chunk size",
        "field_chunk_overlap": "Chunk overlap",
        "field_dataset_name": "Dataset",
        "field_language": "Language",
        "field_latency_ms": "Latency",
        "field_input_tokens": "Input tokens",
        "field_output_tokens": "Output tokens",
        "field_estimated_cost_usd": "Estimated cost",
    },
}


_LANGUAGE_OVERRIDES: dict[
    str,
    dict[str, str],
] = {
    "en_gb": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
    },
    "es": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Configuración de la ejecución",
        "select_run": "Seleccionar ejecución",
        "metadata_coverage": "Cobertura de metadatos",
        "experimental_comparisons": "Comparaciones experimentales",
        "ranking": "Clasificación de ejecuciones",
        "performance_cost": "Rendimiento, tokens y costes",
        "phoenix": "Integración con Phoenix",
        "case_details": "Detalle por caso de prueba",
        "exports": "Exportación de experimentos",
        "export_csv": "Descargar historial en CSV",
        "export_json": "Descargar informe en JSON",
        "available": "Disponible",
        "partially_available": "Parcialmente disponible",
        "waiting_real_data": "Esperando datos reales",
        "not_registered": "No registrado en esta ejecución",
        "field_retrieval_strategy": "Estrategia de búsqueda",
        "field_model_name": "Modelo",
        "field_prompt_version": "Versión del prompt",
        "field_temperature": "Temperatura",
        "field_max_output_tokens": "Límite de tokens",
        "field_embedding_model": "Modelo de embedding",
        "field_knowledge_base_version": "Versión de la base",
        "field_chunk_size": "Tamaño del chunk",
        "field_chunk_overlap": "Solapamiento de chunks",
        "field_dataset_name": "Dataset",
        "field_language": "Idioma",
        "field_latency_ms": "Latencia",
        "field_input_tokens": "Tokens de entrada",
        "field_output_tokens": "Tokens de salida",
        "field_estimated_cost_usd": "Coste estimado",
    },
    "fr": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Configuration de l’exécution",
        "select_run": "Sélectionner une exécution",
        "metadata_coverage": "Couverture des métadonnées",
        "experimental_comparisons": "Comparaisons expérimentales",
        "ranking": "Classement des exécutions",
        "performance_cost": "Performance, jetons et coûts",
        "phoenix": "Intégration Phoenix",
        "case_details": "Détails par cas de test",
        "exports": "Exportation des expériences",
        "export_csv": "Télécharger l’historique CSV",
        "export_json": "Télécharger le rapport JSON",
        "available": "Disponible",
        "partially_available": "Partiellement disponible",
        "waiting_real_data": "En attente de données réelles",
        "not_registered": "Non enregistré pour cette exécution",
        "field_retrieval_strategy": "Stratégie de recherche",
        "field_model_name": "Modèle",
        "field_prompt_version": "Version du prompt",
        "field_temperature": "Température",
        "field_max_output_tokens": "Limite de jetons",
        "field_embedding_model": "Modèle d’embedding",
        "field_knowledge_base_version": "Version de la base",
        "field_chunk_size": "Taille du chunk",
        "field_chunk_overlap": "Chevauchement des chunks",
        "field_dataset_name": "Jeu de données",
        "field_language": "Langue",
        "field_latency_ms": "Latence",
        "field_input_tokens": "Jetons d’entrée",
        "field_output_tokens": "Jetons de sortie",
        "field_estimated_cost_usd": "Coût estimé",
    },
    "de": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Ausführungskonfiguration",
        "select_run": "Ausführung auswählen",
        "metadata_coverage": "Metadatenabdeckung",
        "experimental_comparisons": "Experimentvergleiche",
        "ranking": "Rangfolge der Ausführungen",
        "performance_cost": "Leistung, Token und Kosten",
        "phoenix": "Phoenix-Integration",
        "case_details": "Details nach Testfall",
        "exports": "Experimentexport",
        "export_csv": "Verlauf als CSV herunterladen",
        "export_json": "Bericht als JSON herunterladen",
        "available": "Verfügbar",
        "partially_available": "Teilweise verfügbar",
        "waiting_real_data": "Warten auf reale Daten",
        "not_registered": "Für diese Ausführung nicht erfasst",
        "field_retrieval_strategy": "Suchstrategie",
        "field_model_name": "Modell",
        "field_prompt_version": "Prompt-Version",
        "field_temperature": "Temperatur",
        "field_max_output_tokens": "Token-Limit",
        "field_embedding_model": "Embedding-Modell",
        "field_knowledge_base_version": "Wissensbasis-Version",
        "field_chunk_size": "Chunk-Größe",
        "field_chunk_overlap": "Chunk-Überlappung",
        "field_dataset_name": "Datensatz",
        "field_language": "Sprache",
        "field_latency_ms": "Latenz",
        "field_input_tokens": "Eingabe-Token",
        "field_output_tokens": "Ausgabe-Token",
        "field_estimated_cost_usd": "Geschätzte Kosten",
    },
    "it": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Configurazione dell’esecuzione",
        "select_run": "Seleziona esecuzione",
        "metadata_coverage": "Copertura dei metadati",
        "experimental_comparisons": "Confronti sperimentali",
        "ranking": "Classifica delle esecuzioni",
        "performance_cost": "Prestazioni, token e costi",
        "phoenix": "Integrazione Phoenix",
        "case_details": "Dettaglio per caso di test",
        "exports": "Esportazione degli esperimenti",
        "export_csv": "Scarica cronologia CSV",
        "export_json": "Scarica rapporto JSON",
        "available": "Disponibile",
        "partially_available": "Parzialmente disponibile",
        "waiting_real_data": "In attesa di dati reali",
        "not_registered": "Non registrato per questa esecuzione",
        "field_retrieval_strategy": "Strategia di ricerca",
        "field_model_name": "Modello",
        "field_prompt_version": "Versione del prompt",
        "field_temperature": "Temperatura",
        "field_max_output_tokens": "Limite token",
        "field_embedding_model": "Modello di embedding",
        "field_knowledge_base_version": "Versione della base",
        "field_chunk_size": "Dimensione chunk",
        "field_chunk_overlap": "Sovrapposizione chunk",
        "field_dataset_name": "Dataset",
        "field_language": "Lingua",
        "field_latency_ms": "Latenza",
        "field_input_tokens": "Token di input",
        "field_output_tokens": "Token di output",
        "field_estimated_cost_usd": "Costo stimato",
    },
    "ro": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Configurarea execuției",
        "select_run": "Selectați execuția",
        "metadata_coverage": "Acoperirea metadatelor",
        "experimental_comparisons": "Comparații experimentale",
        "ranking": "Clasamentul execuțiilor",
        "performance_cost": "Performanță, tokenuri și costuri",
        "phoenix": "Integrare Phoenix",
        "case_details": "Detalii pentru fiecare caz de test",
        "exports": "Exportul experimentelor",
        "export_csv": "Descărcați istoricul CSV",
        "export_json": "Descărcați raportul JSON",
        "available": "Disponibil",
        "partially_available": "Disponibil parțial",
        "waiting_real_data": "Se așteaptă date reale",
        "not_registered": "Neînregistrat pentru această execuție",
        "field_retrieval_strategy": "Strategie de căutare",
        "field_model_name": "Model",
        "field_prompt_version": "Versiunea promptului",
        "field_temperature": "Temperatură",
        "field_max_output_tokens": "Limită de tokenuri",
        "field_embedding_model": "Model de embedding",
        "field_knowledge_base_version": "Versiunea bazei",
        "field_chunk_size": "Dimensiunea chunkului",
        "field_chunk_overlap": "Suprapunerea chunkurilor",
        "field_dataset_name": "Set de date",
        "field_language": "Limbă",
        "field_latency_ms": "Latență",
        "field_input_tokens": "Tokenuri de intrare",
        "field_output_tokens": "Tokenuri de ieșire",
        "field_estimated_cost_usd": "Cost estimat",
    },
    "ua": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Конфігурація запуску",
        "select_run": "Вибрати запуск",
        "metadata_coverage": "Покриття метаданих",
        "experimental_comparisons": "Експериментальні порівняння",
        "ranking": "Рейтинг запусків",
        "performance_cost": "Продуктивність, токени та витрати",
        "phoenix": "Інтеграція Phoenix",
        "case_details": "Деталі тестових випадків",
        "exports": "Експорт експериментів",
        "export_csv": "Завантажити історію CSV",
        "export_json": "Завантажити звіт JSON",
        "available": "Доступно",
        "partially_available": "Частково доступно",
        "waiting_real_data": "Очікування реальних даних",
        "not_registered": "Не зареєстровано для цього запуску",
        "field_retrieval_strategy": "Стратегія пошуку",
        "field_model_name": "Модель",
        "field_prompt_version": "Версія промпту",
        "field_language": "Мова",
        "field_latency_ms": "Затримка",
        "field_input_tokens": "Вхідні токени",
        "field_output_tokens": "Вихідні токени",
        "field_estimated_cost_usd": "Орієнтовна вартість",
    },
    "ru": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "Конфигурация запуска",
        "select_run": "Выбрать запуск",
        "metadata_coverage": "Покрытие метаданных",
        "experimental_comparisons": "Экспериментальные сравнения",
        "ranking": "Рейтинг запусков",
        "performance_cost": "Производительность, токены и стоимость",
        "phoenix": "Интеграция Phoenix",
        "case_details": "Детализация тестовых случаев",
        "exports": "Экспорт экспериментов",
        "export_csv": "Скачать историю CSV",
        "export_json": "Скачать отчёт JSON",
        "available": "Доступно",
        "partially_available": "Частично доступно",
        "waiting_real_data": "Ожидание реальных данных",
        "no_branch_options": (
            "В истории оценок не найдено ни одной ветки."
        ),
        "no_environment_options": (
            "В истории оценок не найдено ни одной среды."
        ),
        "not_registered": "Не зарегистрировано для этого запуска",
        "field_retrieval_strategy": "Стратегия поиска",
        "field_model_name": "Модель",
        "field_prompt_version": "Версия промпта",
        "field_language": "Язык",
        "field_latency_ms": "Задержка",
        "field_input_tokens": "Входные токены",
        "field_output_tokens": "Выходные токены",
        "field_estimated_cost_usd": "Расчётная стоимость",
    },
    "sa": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "إعداد التشغيل",
        "select_run": "اختيار التشغيل",
        "metadata_coverage": "تغطية البيانات الوصفية",
        "experimental_comparisons": "المقارنات التجريبية",
        "ranking": "ترتيب عمليات التشغيل",
        "performance_cost": "الأداء والرموز والتكلفة",
        "phoenix": "تكامل Phoenix",
        "case_details": "تفاصيل حالات الاختبار",
        "exports": "تصدير التجارب",
        "export_csv": "تنزيل السجل بصيغة CSV",
        "export_json": "تنزيل التقرير بصيغة JSON",
        "available": "متاح",
        "partially_available": "متاح جزئياً",
        "waiting_real_data": "بانتظار بيانات حقيقية",
        "not_registered": "غير مسجل لهذا التشغيل",
        "field_retrieval_strategy": "استراتيجية البحث",
        "field_model_name": "النموذج",
        "field_prompt_version": "إصدار الموجه",
        "field_language": "اللغة",
        "field_latency_ms": "زمن الاستجابة",
        "field_input_tokens": "رموز الإدخال",
        "field_output_tokens": "رموز الإخراج",
        "field_estimated_cost_usd": "التكلفة المقدرة",
    },
    "ch": {
        **RAG_LAB_ADVANCED_TEXTS["en_us"],
        "advanced_experiment": "运行配置",
        "select_run": "选择运行",
        "metadata_coverage": "元数据覆盖率",
        "experimental_comparisons": "实验比较",
        "ranking": "运行排名",
        "performance_cost": "性能、令牌与成本",
        "phoenix": "Phoenix 集成",
        "case_details": "测试案例详情",
        "exports": "实验导出",
        "export_csv": "下载 CSV 历史记录",
        "export_json": "下载 JSON 报告",
        "available": "可用",
        "partially_available": "部分可用",
        "waiting_real_data": "等待真实数据",
        "not_registered": "本次运行未记录",
        "field_retrieval_strategy": "检索策略",
        "field_model_name": "模型",
        "field_prompt_version": "提示词版本",
        "field_language": "语言",
        "field_latency_ms": "延迟",
        "field_input_tokens": "输入令牌",
        "field_output_tokens": "输出令牌",
        "field_estimated_cost_usd": "预计成本",
    },
}


RAG_LAB_ADVANCED_TEXTS.update(
    _LANGUAGE_OVERRIDES
)
