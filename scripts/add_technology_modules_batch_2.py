from __future__ import annotations

import ast
import pprint
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src" / "platform_modules.py"
I18N_PATH = ROOT / "src" / "platform_modules_i18n.py"
MODULE_TEST_PATH = ROOT / "tests" / "unit" / "test_platform_modules.py"
OVERVIEW_TEST_PATH = ROOT / "tests" / "unit" / "test_platform_modules_overview.py"
BACKUP_DIRECTORY = (
    ROOT
    / ".migration_backups"
    / datetime.now().strftime("technology_batch_2_%Y%m%d_%H%M%S")
)

BASE_LANGUAGES = ("pt", "en_us", "es", "fr", "de", "it", "ro", "ua", "ru", "sa")


@dataclass(frozen=True, slots=True)
class TechnologyModuleSpec:
    module_id: str
    icon: str
    family: str
    integration_type: str
    description: str
    titles: dict[str, str]


RAW_MODULES = (
    (
        "scientific_computing_engineering",
        "🧮",
        "ENGINEERING_SCIENCE_OPTIMIZATION",
        "internal",
        "Cálculos científicos, modelagem matemática, análise numérica e apoio computacional a projetos de engenharia.",
        (
            "🧮 Computação Científica e Engenharia",
            "🧮 Scientific Computing and Engineering",
            "🧮 Computación Científica e Ingeniería",
            "🧮 Calcul scientifique et ingénierie",
            "🧮 Wissenschaftliches Rechnen und Ingenieurwesen",
            "🧮 Calcolo scientifico e ingegneria",
            "🧮 Calcul științific și inginerie",
            "🧮 Наукові обчислення та інженерія",
            "🧮 Научные вычисления и инженерия",
            "🧮 الحوسبة العلمية والهندسة",
        ),
    ),
    (
        "simulation_optimization_operations_research",
        "🧪",
        "ENGINEERING_SCIENCE_OPTIMIZATION",
        "internal",
        "Simulação de cenários, otimização matemática, pesquisa operacional, alocação de recursos e apoio à decisão.",
        (
            "🧪 Simulação, Otimização e Pesquisa Operacional",
            "🧪 Simulation, Optimization and Operations Research",
            "🧪 Simulación, Optimización e Investigación Operativa",
            "🧪 Simulation, optimisation et recherche opérationnelle",
            "🧪 Simulation, Optimierung und Operations Research",
            "🧪 Simulazione, ottimizzazione e ricerca operativa",
            "🧪 Simulare, optimizare și cercetare operațională",
            "🧪 Моделювання, оптимізація та дослідження операцій",
            "🧪 Моделирование, оптимизация и исследование операций",
            "🧪 المحاكاة والتحسين وبحوث العمليات",
        ),
    ),
    (
        "research_labs_assisted_discovery",
        "🔬",
        "ENGINEERING_SCIENCE_OPTIMIZATION",
        "hybrid",
        "Organização de experimentos, análise de resultados, literatura científica, hipóteses e descoberta assistida por IA.",
        (
            "🔬 Pesquisa, Laboratórios e Descoberta Assistida",
            "🔬 Research, Laboratories and Assisted Discovery",
            "🔬 Investigación, Laboratorios y Descubrimiento Asistido",
            "🔬 Recherche, laboratoires et découverte assistée",
            "🔬 Forschung, Labore und unterstützte Entdeckung",
            "🔬 Ricerca, laboratori e scoperta assistita",
            "🔬 Cercetare, laboratoare și descoperire asistată",
            "🔬 Дослідження, лабораторії та підтримувані відкриття",
            "🔬 Исследования, лаборатории и поддерживаемые открытия",
            "🔬 البحث والمختبرات والاكتشاف المساعد",
        ),
    ),
    (
        "materials_product_engineering",
        "🧱",
        "ENGINEERING_SCIENCE_OPTIMIZATION",
        "hybrid",
        "Análise de propriedades, testes, falhas, formulações, qualidade de materiais e desenvolvimento de produtos.",
        (
            "🧱 Materiais e Engenharia de Produtos",
            "🧱 Materials and Product Engineering",
            "🧱 Materiales e Ingeniería de Productos",
            "🧱 Matériaux et ingénierie produit",
            "🧱 Werkstoffe und Produktentwicklung",
            "🧱 Materiali e ingegneria di prodotto",
            "🧱 Materiale și ingineria produselor",
            "🧱 Матеріали та інженерія продуктів",
            "🧱 Материалы и инженерия продуктов",
            "🧱 المواد وهندسة المنتجات",
        ),
    ),
    (
        "construction_bim_digital_engineering",
        "🏗️",
        "ENGINEERING_SCIENCE_OPTIMIZATION",
        "hybrid",
        "Projetos, obras, cronogramas, inspeções, documentos técnicos, modelos BIM e acompanhamento digital da execução.",
        (
            "🏗️ Construção, BIM e Engenharia Digital",
            "🏗️ Construction, BIM and Digital Engineering",
            "🏗️ Construcción, BIM e Ingeniería Digital",
            "🏗️ Construction, BIM et ingénierie numérique",
            "🏗️ Bauwesen, BIM und digitales Engineering",
            "🏗️ Costruzioni, BIM e ingegneria digitale",
            "🏗️ Construcții, BIM și inginerie digitală",
            "🏗️ Будівництво, BIM та цифрова інженерія",
            "🏗️ Строительство, BIM и цифровая инженерия",
            "🏗️ البناء ونمذجة معلومات المباني والهندسة الرقمية",
        ),
    ),
    (
        "climate_meteorological_intelligence",
        "🌦️",
        "CLIMATE_ENVIRONMENT_ENERGY",
        "api",
        "Previsões meteorológicas, riscos climáticos, chuvas, secas, ondas de calor e alertas operacionais.",
        (
            "🌦️ Inteligência Climática e Meteorológica",
            "🌦️ Climate and Meteorological Intelligence",
            "🌦️ Inteligencia Climática y Meteorológica",
            "🌦️ Intelligence climatique et météorologique",
            "🌦️ Klima- und Wetterintelligenz",
            "🌦️ Intelligenza climatica e meteorologica",
            "🌦️ Inteligență climatică și meteorologică",
            "🌦️ Кліматична та метеорологічна аналітика",
            "🌦️ Климатическая и метеорологическая аналитика",
            "🌦️ الذكاء المناخي والأرصاد الجوية",
        ),
    ),
    (
        "environmental_natural_resources_intelligence",
        "🌊",
        "CLIMATE_ENVIRONMENT_ENERGY",
        "hybrid",
        "Monitoramento de água, florestas, solo, biodiversidade, resíduos, poluição e recursos naturais.",
        (
            "🌊 Inteligência Ambiental e Recursos Naturais",
            "🌊 Environmental and Natural Resources Intelligence",
            "🌊 Inteligencia Ambiental y Recursos Naturales",
            "🌊 Intelligence environnementale et ressources naturelles",
            "🌊 Umwelt- und Ressourcenintelligenz",
            "🌊 Intelligenza ambientale e risorse naturali",
            "🌊 Inteligență de mediu și resurse naturale",
            "🌊 Екологічна аналітика та природні ресурси",
            "🌊 Экологическая аналитика и природные ресурсы",
            "🌊 الذكاء البيئي والموارد الطبيعية",
        ),
    ),
    (
        "energy_smart_grids",
        "⚡",
        "CLIMATE_ENVIRONMENT_ENERGY",
        "hybrid",
        "Consumo, geração, armazenamento, energia solar, baterias, previsão de demanda e redes inteligentes.",
        (
            "⚡ Energia e Redes Inteligentes",
            "⚡ Energy and Smart Grids",
            "⚡ Energía y Redes Inteligentes",
            "⚡ Énergie et réseaux intelligents",
            "⚡ Energie und intelligente Netze",
            "⚡ Energia e reti intelligenti",
            "⚡ Energie și rețele inteligente",
            "⚡ Енергетика та розумні мережі",
            "⚡ Энергетика и умные сети",
            "⚡ الطاقة والشبكات الذكية",
        ),
    ),
    (
        "esg_sustainability",
        "🌱",
        "CLIMATE_ENVIRONMENT_ENERGY",
        "hybrid",
        "Indicadores ambientais, sociais e de governança, metas, emissões, relatórios e compromissos ESG.",
        (
            "🌱 ESG e Sustentabilidade",
            "🌱 ESG and Sustainability",
            "🌱 ESG y Sostenibilidad",
            "🌱 ESG et durabilité",
            "🌱 ESG und Nachhaltigkeit",
            "🌱 ESG e sostenibilità",
            "🌱 ESG și sustenabilitate",
            "🌱 ESG та сталий розвиток",
            "🌱 ESG и устойчивое развитие",
            "🌱 الحوكمة البيئية والاجتماعية والاستدامة",
        ),
    ),
    (
        "emergency_disaster_management",
        "🧯",
        "CLIMATE_ENVIRONMENT_ENERGY",
        "hybrid",
        "Gestão de enchentes, queimadas, deslizamentos, acidentes, áreas afetadas, evacuação e coordenação de equipes.",
        (
            "🧯 Resposta a Emergências e Gestão de Desastres",
            "🧯 Emergency Response and Disaster Management",
            "🧯 Respuesta a Emergencias y Gestión de Desastres",
            "🧯 Intervention d'urgence et gestion des catastrophes",
            "🧯 Notfallreaktion und Katastrophenmanagement",
            "🧯 Risposta alle emergenze e gestione dei disastri",
            "🧯 Răspuns la urgențe și managementul dezastrelor",
            "🧯 Реагування на надзвичайні ситуації та катастрофи",
            "🧯 Реагирование на чрезвычайные ситуации и катастрофы",
            "🧯 الاستجابة للطوارئ وإدارة الكوارث",
        ),
    ),
    (
        "mobility_traffic_transport",
        "🚦",
        "MOBILITY_CONNECTED_INFRASTRUCTURE",
        "hybrid",
        "Rotas, frotas, congestionamentos, transporte público, entregas, acidentes e planejamento de mobilidade.",
        (
            "🚦 Mobilidade, Tráfego e Transportes",
            "🚦 Mobility, Traffic and Transportation",
            "🚦 Movilidad, Tráfico y Transportes",
            "🚦 Mobilité, trafic et transports",
            "🚦 Mobilität, Verkehr und Transport",
            "🚦 Mobilità, traffico e trasporti",
            "🚦 Mobilitate, trafic și transport",
            "🚦 Мобільність, трафік і транспорт",
            "🚦 Мобильность, трафик и транспорт",
            "🚦 التنقل والمرور والنقل",
        ),
    ),
    (
        "smart_cities_urban_infrastructure",
        "🏙️",
        "MOBILITY_CONNECTED_INFRASTRUCTURE",
        "hybrid",
        "Integração de iluminação, trânsito, água, resíduos, segurança urbana, obras, sensores e serviços municipais.",
        (
            "🏙️ Cidades Inteligentes e Infraestrutura Urbana",
            "🏙️ Smart Cities and Urban Infrastructure",
            "🏙️ Ciudades Inteligentes e Infraestructura Urbana",
            "🏙️ Villes intelligentes et infrastructures urbaines",
            "🏙️ Smart Cities und urbane Infrastruktur",
            "🏙️ Città intelligenti e infrastrutture urbane",
            "🏙️ Orașe inteligente și infrastructură urbană",
            "🏙️ Розумні міста та міська інфраструктура",
            "🏙️ Умные города и городская инфраструктура",
            "🏙️ المدن الذكية والبنية التحتية الحضرية",
        ),
    ),
    (
        "networks_telecommunications_connectivity",
        "📶",
        "MOBILITY_CONNECTED_INFRASTRUCTURE",
        "hybrid",
        "Monitoramento de redes, cobertura, falhas, qualidade, capacidade e infraestrutura de telecomunicações.",
        (
            "📶 Redes, Telecomunicações e Conectividade",
            "📶 Networks, Telecommunications and Connectivity",
            "📶 Redes, Telecomunicaciones y Conectividad",
            "📶 Réseaux, télécommunications et connectivité",
            "📶 Netzwerke, Telekommunikation und Konnektivität",
            "📶 Reti, telecomunicazioni e connettività",
            "📶 Rețele, telecomunicații și conectivitate",
            "📶 Мережі, телекомунікації та зв'язок",
            "📶 Сети, телекоммуникации и связь",
            "📶 الشبكات والاتصالات والربط",
        ),
    ),
    (
        "navigation_positioning_geolocation",
        "🧭",
        "MOBILITY_CONNECTED_INFRASTRUCTURE",
        "api",
        "GPS, GNSS, localização de ativos, rastreamento, geofencing, posicionamento e navegação.",
        (
            "🧭 Navegação, Posicionamento e Geolocalização",
            "🧭 Navigation, Positioning and Geolocation",
            "🧭 Navegación, Posicionamiento y Geolocalización",
            "🧭 Navigation, positionnement et géolocalisation",
            "🧭 Navigation, Positionierung und Geolokalisierung",
            "🧭 Navigazione, posizionamento e geolocalizzazione",
            "🧭 Navigație, poziționare și geolocalizare",
            "🧭 Навігація, позиціонування та геолокація",
            "🧭 Навигация, позиционирование и геолокация",
            "🧭 الملاحة وتحديد المواقع والموقع الجغرافي",
        ),
    ),
    (
        "asset_management_smart_maintenance",
        "🔧",
        "MOBILITY_CONNECTED_INFRASTRUCTURE",
        "hybrid",
        "Gestão de equipamentos, veículos, máquinas, ordens de serviço, peças, falhas e manutenção preditiva.",
        (
            "🔧 Gestão de Ativos e Manutenção Inteligente",
            "🔧 Asset Management and Smart Maintenance",
            "🔧 Gestión de Activos y Mantenimiento Inteligente",
            "🔧 Gestion des actifs et maintenance intelligente",
            "🔧 Asset-Management und intelligente Wartung",
            "🔧 Gestione degli asset e manutenzione intelligente",
            "🔧 Managementul activelor și mentenanță inteligentă",
            "🔧 Управління активами та розумне обслуговування",
            "🔧 Управление активами и умное обслуживание",
            "🔧 إدارة الأصول والصيانة الذكية",
        ),
    ),
    (
        "ai_software_engineering",
        "🧑‍💻",
        "SOFTWARE_PRODUCTIVITY_EXPERIENCE",
        "internal",
        "Geração, revisão e modernização de código, documentação, arquitetura e assistência ao desenvolvimento.",
        (
            "🧑‍💻 Engenharia de Software com IA",
            "🧑‍💻 AI-Assisted Software Engineering",
            "🧑‍💻 Ingeniería de Software con IA",
            "🧑‍💻 Ingénierie logicielle assistée par IA",
            "🧑‍💻 KI-gestütztes Software Engineering",
            "🧑‍💻 Ingegneria del software con IA",
            "🧑‍💻 Inginerie software asistată de IA",
            "🧑‍💻 Розробка програмного забезпечення з ШІ",
            "🧑‍💻 Разработка программного обеспечения с ИИ",
            "🧑‍💻 هندسة البرمجيات بمساعدة الذكاء الاصطناعي",
        ),
    ),
    (
        "ai_collaboration_meetings_productivity",
        "🧑‍🤝‍🧑",
        "SOFTWARE_PRODUCTIVITY_EXPERIENCE",
        "hybrid",
        "Atas, tarefas, decisões, acompanhamento de reuniões, gestão do conhecimento e colaboração entre equipes.",
        (
            "🧑‍🤝‍🧑 Colaboração, Reuniões e Produtividade com IA",
            "🧑‍🤝‍🧑 AI Collaboration, Meetings and Productivity",
            "🧑‍🤝‍🧑 Colaboración, Reuniones y Productividad con IA",
            "🧑‍🤝‍🧑 Collaboration, réunions et productivité avec l'IA",
            "🧑‍🤝‍🧑 Zusammenarbeit, Meetings und Produktivität mit KI",
            "🧑‍🤝‍🧑 Collaborazione, riunioni e produttività con IA",
            "🧑‍🤝‍🧑 Colaborare, întâlniri și productivitate cu IA",
            "🧑‍🤝‍🧑 Співпраця, зустрічі та продуктивність із ШІ",
            "🧑‍🤝‍🧑 Сотрудничество, встречи и продуктивность с ИИ",
            "🧑‍🤝‍🧑 التعاون والاجتماعات والإنتاجية بالذكاء الاصطناعي",
        ),
    ),
    (
        "digital_experiences_intelligent_interfaces",
        "🎨",
        "SOFTWARE_PRODUCTIVITY_EXPERIENCE",
        "hybrid",
        "Interfaces adaptativas, personalização, acessibilidade, experiências conversacionais e interação digital.",
        (
            "🎨 Experiências Digitais e Interfaces Inteligentes",
            "🎨 Digital Experiences and Intelligent Interfaces",
            "🎨 Experiencias Digitales e Interfaces Inteligentes",
            "🎨 Expériences numériques et interfaces intelligentes",
            "🎨 Digitale Erlebnisse und intelligente Schnittstellen",
            "🎨 Esperienze digitali e interfacce intelligenti",
            "🎨 Experiențe digitale și interfețe inteligente",
            "🎨 Цифровий досвід та інтелектуальні інтерфейси",
            "🎨 Цифровой опыт и интеллектуальные интерфейсы",
            "🎨 التجارب الرقمية والواجهات الذكية",
        ),
    ),
    (
        "software_testing_quality_reliability",
        "🧪",
        "SOFTWARE_PRODUCTIVITY_EXPERIENCE",
        "internal",
        "Testes automatizados, qualidade de código, confiabilidade, regressão, desempenho e validação de software.",
        (
            "🧪 Testes, Qualidade e Confiabilidade de Software",
            "🧪 Software Testing, Quality and Reliability",
            "🧪 Pruebas, Calidad y Confiabilidad de Software",
            "🧪 Tests, qualité et fiabilité logicielle",
            "🧪 Softwaretests, Qualität und Zuverlässigkeit",
            "🧪 Test, qualità e affidabilità del software",
            "🧪 Testare, calitate și fiabilitate software",
            "🧪 Тестування, якість і надійність ПЗ",
            "🧪 Тестирование, качество и надежность ПО",
            "🧪 اختبار البرمجيات والجودة والموثوقية",
        ),
    ),
    (
        "mobile_apps_omnichannel_experiences",
        "📱",
        "SOFTWARE_PRODUCTIVITY_EXPERIENCE",
        "hybrid",
        "Aplicações móveis e experiências integradas entre web, aplicativo, WhatsApp, e-mail, voz e outros canais.",
        (
            "📱 Aplicações Móveis e Experiências Omnicanal",
            "📱 Mobile Applications and Omnichannel Experiences",
            "📱 Aplicaciones Móviles y Experiencias Omnicanal",
            "📱 Applications mobiles et expériences omnicanales",
            "📱 Mobile Anwendungen und Omnichannel-Erlebnisse",
            "📱 Applicazioni mobili ed esperienze omnicanale",
            "📱 Aplicații mobile și experiențe omnicanal",
            "📱 Мобільні застосунки та омніканальний досвід",
            "📱 Мобильные приложения и омниканальный опыт",
            "📱 تطبيقات الهاتف وتجارب القنوات المتعددة",
        ),
    ),
    (
        "digital_identity_verifiable_credentials",
        "🪪",
        "DIGITAL_TRUST_GOVERNANCE",
        "hybrid",
        "Identidades digitais, emissão, verificação, revogação e compartilhamento controlado de credenciais.",
        (
            "🪪 Identidade Digital e Credenciais Verificáveis",
            "🪪 Digital Identity and Verifiable Credentials",
            "🪪 Identidad Digital y Credenciales Verificables",
            "🪪 Identité numérique et justificatifs vérifiables",
            "🪪 Digitale Identität und überprüfbare Nachweise",
            "🪪 Identità digitale e credenziali verificabili",
            "🪪 Identitate digitală și acreditări verificabile",
            "🪪 Цифрова ідентичність і перевірні облікові дані",
            "🪪 Цифровая идентичность и проверяемые учетные данные",
            "🪪 الهوية الرقمية وبيانات الاعتماد القابلة للتحقق",
        ),
    ),
    (
        "technology_governance_policy_compliance",
        "📜",
        "DIGITAL_TRUST_GOVERNANCE",
        "internal",
        "Políticas, controles, padrões, auditoria, responsabilidades e conformidade aplicados à tecnologia.",
        (
            "📜 Governança, Políticas e Conformidade Tecnológica",
            "📜 Technology Governance, Policy and Compliance",
            "📜 Gobernanza, Políticas y Cumplimiento Tecnológico",
            "📜 Gouvernance, politiques et conformité technologiques",
            "📜 Technologie-Governance, Richtlinien und Compliance",
            "📜 Governance, politiche e conformità tecnologica",
            "📜 Guvernanță, politici și conformitate tehnologică",
            "📜 Технологічне врядування, політики та відповідність",
            "📜 Технологическое управление, политики и соответствие",
            "📜 حوكمة التكنولوجيا والسياسات والامتثال",
        ),
    ),
    (
        "data_traceability_provenance",
        "📦",
        "DIGITAL_TRUST_GOVERNANCE",
        "internal",
        "Registro da origem, transformação, autoria, linhagem e histórico de dados, modelos e decisões.",
        (
            "📦 Rastreabilidade e Proveniência de Dados",
            "📦 Data Traceability and Provenance",
            "📦 Trazabilidad y Procedencia de Datos",
            "📦 Traçabilité et provenance des données",
            "📦 Datenrückverfolgbarkeit und Provenienz",
            "📦 Tracciabilità e provenienza dei dati",
            "📦 Trasabilitatea și proveniența datelor",
            "📦 Простежуваність і походження даних",
            "📦 Прослеживаемость и происхождение данных",
            "📦 تتبع البيانات ومصدرها",
        ),
    ),
    (
        "enterprise_decision_intelligence",
        "🧠",
        "DIGITAL_TRUST_GOVERNANCE",
        "internal",
        "Combinação de dados, regras, previsões, simulações e evidências para recomendar decisões empresariais.",
        (
            "🧠 Inteligência de Decisão Empresarial",
            "🧠 Enterprise Decision Intelligence",
            "🧠 Inteligencia de Decisión Empresarial",
            "🧠 Intelligence décisionnelle d'entreprise",
            "🧠 Unternehmensentscheidungsintelligenz",
            "🧠 Intelligenza decisionale aziendale",
            "🧠 Inteligență decizională pentru întreprinderi",
            "🧠 Інтелект підтримки бізнес-рішень",
            "🧠 Интеллект поддержки бизнес-решений",
            "🧠 ذكاء اتخاذ القرار المؤسسي",
        ),
    ),
    (
        "operational_security_resilience",
        "🛡️",
        "DIGITAL_TRUST_GOVERNANCE",
        "hybrid",
        "Continuidade de negócios, contingência, recuperação de desastres, disponibilidade e riscos operacionais.",
        (
            "🛡️ Segurança Operacional e Resiliência",
            "🛡️ Operational Security and Resilience",
            "🛡️ Seguridad Operacional y Resiliencia",
            "🛡️ Sécurité opérationnelle et résilience",
            "🛡️ Betriebssicherheit und Resilienz",
            "🛡️ Sicurezza operativa e resilienza",
            "🛡️ Securitate operațională și reziliență",
            "🛡️ Операційна безпека та стійкість",
            "🛡️ Операционная безопасность и устойчивость",
            "🛡️ الأمن التشغيلي والمرونة",
        ),
    ),
    (
        "responsible_ai_ethics_risk",
        "⚖️",
        "AI_EVALUATION_TRUST",
        "internal",
        "Princípios de IA responsável, ética, impactos, classificação de riscos e controles no ciclo de vida.",
        (
            "⚖️ IA Responsável, Ética e Avaliação de Riscos",
            "⚖️ Responsible AI, Ethics and Risk Assessment",
            "⚖️ IA Responsable, Ética y Evaluación de Riesgos",
            "⚖️ IA responsable, éthique et évaluation des risques",
            "⚖️ Verantwortungsvolle KI, Ethik und Risikobewertung",
            "⚖️ IA responsabile, etica e valutazione dei rischi",
            "⚖️ IA responsabilă, etică și evaluarea riscurilor",
            "⚖️ Відповідальний ШІ, етика та оцінювання ризиків",
            "⚖️ Ответственный ИИ, этика и оценка рисков",
            "⚖️ الذكاء الاصطناعي المسؤول والأخلاق وتقييم المخاطر",
        ),
    ),
    (
        "ai_evaluation_benchmarks_red_team",
        "🧪",
        "AI_EVALUATION_TRUST",
        "internal",
        "Avaliação de modelos e agentes, benchmarks, testes adversariais, red team, regressão e aprovação.",
        (
            "🧪 Avaliação, Benchmarks e Red Team de IA",
            "🧪 AI Evaluation, Benchmarks and Red Teaming",
            "🧪 Evaluación, Benchmarks y Red Team de IA",
            "🧪 Évaluation, benchmarks et red teaming de l'IA",
            "🧪 KI-Evaluierung, Benchmarks und Red Teaming",
            "🧪 Valutazione, benchmark e red team dell'IA",
            "🧪 Evaluare, benchmarkuri și red teaming pentru IA",
            "🧪 Оцінювання, бенчмарки та red team для ШІ",
            "🧪 Оценка, бенчмарки и red team для ИИ",
            "🧪 تقييم الذكاء الاصطناعي والمعايير والاختبارات الهجومية",
        ),
    ),
    (
        "model_explainability_interpretability",
        "🔍",
        "AI_EVALUATION_TRUST",
        "internal",
        "Explicação de previsões, fatores relevantes, interpretação de modelos, transparência e evidências.",
        (
            "🔍 Explicabilidade e Interpretabilidade de Modelos",
            "🔍 Model Explainability and Interpretability",
            "🔍 Explicabilidad e Interpretabilidad de Modelos",
            "🔍 Explicabilité et interprétabilité des modèles",
            "🔍 Erklärbarkeit und Interpretierbarkeit von Modellen",
            "🔍 Spiegabilità e interpretabilità dei modelli",
            "🔍 Explicabilitatea și interpretabilitatea modelelor",
            "🔍 Пояснюваність та інтерпретованість моделей",
            "🔍 Объяснимость и интерпретируемость моделей",
            "🔍 قابلية تفسير النماذج وشرحها",
        ),
    ),
    (
        "ai_bias_quality_monitoring",
        "📊",
        "AI_EVALUATION_TRUST",
        "internal",
        "Monitoramento de viés, qualidade, precisão, deriva, segurança e desempenho de modelos e agentes.",
        (
            "📊 Monitoramento de Viés e Qualidade de IA",
            "📊 AI Bias and Quality Monitoring",
            "📊 Monitoreo de Sesgo y Calidad de IA",
            "📊 Surveillance des biais et de la qualité de l'IA",
            "📊 Überwachung von KI-Bias und Qualität",
            "📊 Monitoraggio di bias e qualità dell'IA",
            "📊 Monitorizarea părtinirii și calității IA",
            "📊 Моніторинг упередженості та якості ШІ",
            "📊 Мониторинг предвзятости и качества ИИ",
            "📊 مراقبة التحيز وجودة الذكاء الاصطناعي",
        ),
    ),
    (
        "ai_certification_system_evidence",
        "✅",
        "AI_EVALUATION_TRUST",
        "internal",
        "Evidências, relatórios, rastreabilidade, critérios de conformidade e preparação para certificação de IA.",
        (
            "✅ Certificação e Evidências de Sistemas de IA",
            "✅ AI System Certification and Evidence",
            "✅ Certificación y Evidencias de Sistemas de IA",
            "✅ Certification et preuves des systèmes d'IA",
            "✅ Zertifizierung und Nachweise für KI-Systeme",
            "✅ Certificazione ed evidenze dei sistemi di IA",
            "✅ Certificare și dovezi pentru sistemele IA",
            "✅ Сертифікація та докази для систем ШІ",
            "✅ Сертификация и доказательства для систем ИИ",
            "✅ اعتماد أنظمة الذكاء الاصطناعي والأدلة",
        ),
    ),
)


MODULES = tuple(
    TechnologyModuleSpec(
        module_id=module_id,
        icon=icon,
        family=family,
        integration_type=integration_type,
        description=description,
        titles=dict(zip(BASE_LANGUAGES, titles, strict=True)),
    )
    for module_id, icon, family, integration_type, description, titles in RAW_MODULES
)

NEW_MODULE_IDS = {module.module_id for module in MODULES}


def source_offsets(source: str) -> list[int]:
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _utf8_column_to_character_offset(
    line: str,
    byte_column: int,
) -> int:
    """Converte uma coluna UTF-8 do AST em posição textual."""

    return len(line.encode("utf-8")[:byte_column].decode("utf-8"))


def node_span(
    source: str,
    node: ast.AST,
) -> tuple[int, int]:
    """Retorna o intervalo textual correto, inclusive com Unicode."""

    source_lines = source.splitlines(
        keepends=True,
    )

    start_line_index = node.lineno - 1
    end_line_index = node.end_lineno - 1

    start = sum(
        len(line) for line in source_lines[:start_line_index]
    ) + _utf8_column_to_character_offset(
        source_lines[start_line_index],
        node.col_offset,
    )

    end = sum(
        len(line) for line in source_lines[:end_line_index]
    ) + _utf8_column_to_character_offset(
        source_lines[end_line_index],
        node.end_col_offset,
    )

    return start, end


def find_assignment(
    tree: ast.AST,
    variable_name: str,
) -> ast.Assign | ast.AnnAssign:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == variable_name
                for target in node.targets
            ):
                return node
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == variable_name:
                return node
    raise RuntimeError(f"Atribuição não encontrada: {variable_name}")


def assignment_value(node: ast.Assign | ast.AnnAssign) -> ast.expr:
    if node.value is None:
        raise RuntimeError("Atribuição sem valor.")
    return node.value


def create_backups(paths: tuple[Path, ...]) -> None:
    BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        destination = BACKUP_DIRECTORY / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def render_platform_module(module: TechnologyModuleSpec) -> str:
    return (
        "    PlatformModule(\n"
        f'        module_id="{module.module_id}",\n'
        f'        icon="{module.icon}",\n'
        "        category=PlatformModuleCategory.TECHNOLOGY_CORE,\n"
        "        status=PlatformModuleStatus.PLANNED,\n"
        "        navigation_group_id=None,\n"
        f'        integration_type="{module.integration_type}",\n'
        f"        description={module.description!r},\n"
        "        technology_family=(\n"
        f"            TechnologyFamily.{module.family}\n"
        "        ),\n"
        "    ),\n"
    )


def update_platform_modules() -> None:
    source = MODULES_PATH.read_text(encoding="utf-8")
    missing = tuple(
        module for module in MODULES if f'module_id="{module.module_id}"' not in source
    )
    if not missing:
        print("TECHNOLOGY_BATCH_2_MODULES_ALREADY_PRESENT=OK")
        return

    anchor = '    PlatformModule(\n        module_id="pet_shops_veterinary_services",'
    position = source.find(anchor)
    if position == -1:
        raise RuntimeError("Âncora do primeiro módulo setorial não encontrada.")

    insertion = "".join(render_platform_module(module) for module in missing)
    MODULES_PATH.write_text(
        source[:position] + insertion + source[position:],
        encoding="utf-8",
    )


def update_platform_module_translations() -> None:
    source = I18N_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignment = find_assignment(tree, "PLATFORM_MODULE_TEXTS")
    value_node = assignment_value(assignment)
    texts = ast.literal_eval(value_node)

    if not isinstance(texts, dict):
        raise TypeError("PLATFORM_MODULE_TEXTS não é um dicionário.")

    for language in BASE_LANGUAGES:
        language_texts = texts.get(language)
        if not isinstance(language_texts, dict):
            raise RuntimeError(f"Idioma ausente ou inválido: {language}")
        for module in MODULES:
            language_texts[module.module_id] = module.titles[language]

    start, end = node_span(source, value_node)
    rendered = pprint.pformat(
        texts,
        width=79,
        sort_dicts=False,
        compact=False,
    )
    I18N_PATH.write_text(
        source[:start] + rendered + source[end:],
        encoding="utf-8",
    )


def update_named_string_set(
    path: Path,
    variable_name: str,
    values: set[str],
) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignment = find_assignment(tree, variable_name)
    value_node = assignment_value(assignment)
    current = ast.literal_eval(value_node)

    if not isinstance(current, set):
        raise TypeError(f"{variable_name} não é um conjunto.")

    updated = set(current) | values
    start, end = node_span(source, value_node)
    rendered = "{\n" + "".join(f'    "{item}",\n' for item in sorted(updated)) + "}"
    path.write_text(
        source[:start] + rendered + source[end:],
        encoding="utf-8",
    )


def update_planned_sets(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    replacements: list[tuple[int, int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if "planned" not in target.id.lower() or not isinstance(node.value, ast.Set):
            continue
        current = ast.literal_eval(node.value)
        if not isinstance(current, set) or not all(
            isinstance(item, str) for item in current
        ):
            continue

        updated = current | NEW_MODULE_IDS
        start, end = node_span(source, node.value)
        indentation = " " * node.col_offset
        rendered = (
            "{\n"
            + "".join(f'{indentation}    "{item}",\n' for item in sorted(updated))
            + indentation
            + "}"
        )
        replacements.append((start, end, rendered))

    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]

    path.write_text(source, encoding="utf-8")


def replace_test_function(
    source: str,
    function_name: str,
    replacement: str,
) -> str:
    marker = f"def {function_name}("
    start = source.find(marker)
    if start == -1:
        return source
    next_function = source.find("\ndef ", start + len(marker))
    end = len(source) if next_function == -1 else next_function + 1
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]


def update_module_tests() -> None:
    update_named_string_set(
        MODULE_TEST_PATH,
        "EXPECTED_MODULE_IDS",
        NEW_MODULE_IDS,
    )
    update_planned_sets(MODULE_TEST_PATH)

    source = MODULE_TEST_PATH.read_text(encoding="utf-8")
    source = source.replace(
        "assert len(technology_modules) == 26",
        "assert len(technology_modules) == 56",
    )
    source = source.replace(
        "assert len(PLATFORM_MODULES) == 44",
        "assert len(PLATFORM_MODULES) == 74",
    )

    source = replace_test_function(
        source,
        "test_future_technology_families_can_start_empty",
        """def test_all_technology_families_have_modules():
    assert all(
        platform_modules_by_technology_family(family)
        for family in TechnologyFamily
    )""",
    )

    if "def test_second_batch_technology_family_distribution" not in source:
        source += """


def test_second_batch_technology_family_distribution():
    expected_by_family = {
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: {
            "scientific_computing_engineering",
            "simulation_optimization_operations_research",
            "research_labs_assisted_discovery",
            "materials_product_engineering",
            "construction_bim_digital_engineering",
        },
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: {
            "climate_meteorological_intelligence",
            "environmental_natural_resources_intelligence",
            "energy_smart_grids",
            "esg_sustainability",
            "emergency_disaster_management",
        },
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: {
            "mobility_traffic_transport",
            "smart_cities_urban_infrastructure",
            "networks_telecommunications_connectivity",
            "navigation_positioning_geolocation",
            "asset_management_smart_maintenance",
        },
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: {
            "ai_software_engineering",
            "ai_collaboration_meetings_productivity",
            "digital_experiences_intelligent_interfaces",
            "software_testing_quality_reliability",
            "mobile_apps_omnichannel_experiences",
        },
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: {
            "digital_identity_verifiable_credentials",
            "technology_governance_policy_compliance",
            "data_traceability_provenance",
            "enterprise_decision_intelligence",
            "operational_security_resilience",
        },
        TechnologyFamily.AI_EVALUATION_TRUST: {
            "responsible_ai_ethics_risk",
            "ai_evaluation_benchmarks_red_team",
            "model_explainability_interpretability",
            "ai_bias_quality_monitoring",
            "ai_certification_system_evidence",
        },
    }

    for family, expected_ids in expected_by_family.items():
        assert {
            module.module_id
            for module in platform_modules_by_technology_family(family)
        } == expected_ids
"""

    MODULE_TEST_PATH.write_text(source.rstrip() + "\n", encoding="utf-8")


def update_overview_tests() -> None:
    source = OVERVIEW_TEST_PATH.read_text(encoding="utf-8")
    source = source.replace(
        "PlatformModuleCategory.TECHNOLOGY_CORE: 26,",
        "PlatformModuleCategory.TECHNOLOGY_CORE: 56,",
    )
    source = source.replace(
        "assert len(technology_cards) == 26",
        "assert len(technology_cards) == 56",
    )
    source = source.replace(
        "def test_builds_forty_four_platform_module_cards():",
        "def test_builds_seventy_four_platform_module_cards():",
    )
    source = source.replace("assert len(cards) == 44", "assert len(cards) == 74")
    source = source.replace(") == 44", ") == 74")

    if "def test_second_batch_cards_are_grouped_by_family" not in source:
        source += """


def test_second_batch_cards_are_grouped_by_family():
    cards = build_platform_module_cards("pt")

    expected_counts = {
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: 5,
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: 5,
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: 5,
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: 5,
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: 5,
        TechnologyFamily.AI_EVALUATION_TRUST: 5,
    }

    for family, expected_count in expected_counts.items():
        family_cards = tuple(
            card
            for card in cards
            if card.technology_family is family
        )
        assert len(family_cards) == expected_count
        assert all(
            card.status_code is PlatformModuleStatus.PLANNED
            for card in family_cards
        )
        assert all(card.is_available is False for card in family_cards)
"""

    OVERVIEW_TEST_PATH.write_text(source.rstrip() + "\n", encoding="utf-8")


def validate_specs() -> None:
    if len(MODULES) != 30:
        raise RuntimeError(
            f"O lote deveria conter 30 módulos, mas contém {len(MODULES)}."
        )

    module_ids = [module.module_id for module in MODULES]
    if len(module_ids) != len(set(module_ids)):
        raise RuntimeError("Existem IDs duplicados no lote.")

    for module in MODULES:
        if set(module.titles) != set(BASE_LANGUAGES):
            raise RuntimeError(f"Traduções incompletas para {module.module_id}.")
        if module.integration_type not in {"internal", "api", "hybrid"}:
            raise RuntimeError(f"Tipo de integração inválido: {module.module_id}.")


def validate_result() -> None:
    module_source = MODULES_PATH.read_text(encoding="utf-8")
    missing_registry = {
        module_id
        for module_id in NEW_MODULE_IDS
        if f'module_id="{module_id}"' not in module_source
    }
    if missing_registry:
        raise RuntimeError(f"Módulos ausentes no registro: {sorted(missing_registry)}")

    source = I18N_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignment = find_assignment(tree, "PLATFORM_MODULE_TEXTS")
    texts = ast.literal_eval(assignment_value(assignment))

    for language in BASE_LANGUAGES:
        missing = NEW_MODULE_IDS - set(texts[language])
        if missing:
            raise RuntimeError(f"Traduções ausentes em {language}: {sorted(missing)}")


def main() -> None:
    files = (
        MODULES_PATH,
        I18N_PATH,
        MODULE_TEST_PATH,
        OVERVIEW_TEST_PATH,
    )

    validate_specs()
    create_backups(files)

    print(f"BACKUP_DIRECTORY={BACKUP_DIRECTORY}")

    update_platform_modules()
    update_platform_module_translations()
    update_module_tests()
    update_overview_tests()
    validate_result()

    print("TECHNOLOGY_MODULES_BATCH_2_CREATED=OK")
    print(f"NEW_TECHNOLOGY_MODULES={len(MODULES)}")
    print("EXPECTED_TECHNOLOGY_TOTAL=56")
    print("EXPECTED_PLATFORM_TOTAL=74")


if __name__ == "__main__":
    main()
