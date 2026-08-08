"""
Traduções dos módulos e estados da INNA AI Platform.
"""

from __future__ import annotations

from src.platform_modules import (
    PLATFORM_MODULES,
    PlatformModuleCategory,
    PlatformModuleStatus,
    TechnologyFamily,
)

PLATFORM_MODULE_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "financial_solutions": "💰 Soluções Financeiras",
        "hr_people_analytics": "👥 RH e People Analytics",
        "document_ai": "📄 Document AI",
        "business_automation": "🤖 Automação Empresarial",
        "enterprise_rag": "📚 Enterprise RAG",
        "site_app_generator": "🌐 Gerador de Sites e Apps",
        "intelligent_support": "🎧 Atendimento e Suporte Inteligente",
        "data_bi_copilot": "📊 Data & BI Copilot",
        "quality_process_management": "✅ Gestão da Qualidade e Processos",
        "crm_sales_intelligence": "🤝 CRM e Experiência do Cliente",
        "erp_business_operations": "🏢 ERP e Operações Empresariais",
        "supply_chain_procurement_logistics": "📦 Supply Chain, Compras e Logística",
        "legal_compliance": "⚖️ Jurídico e Compliance",
        "api_integrations_connectors": "🔌 API, Integrações e Conectores",
        "data_platform_governance": "🗄️ Plataforma e Governança de Dados",
        "cybersecurity_fraud_prevention": "🛡️ Cibersegurança e Prevenção a Fraudes",
        "cloud_devops_finops": "☁️ Cloud, DevOps e FinOps Copilot",
        "ai_operations": "⚙️ Operação e Governança de IA",
        "tools_analytics": "🛠️ Ferramentas e Analytics",
        "pet_shops_veterinary_services": "🐾 Pet Shops e Serviços Veterinários",
        "supermarkets_wholesale": "🛒 Supermercados e Atacado",
        "retail_stores": "🏪 Lojas e Varejo",
        "dentistry": "🦷 Odontologia",
        "hospitals_clinics": "🏥 Hospitais e Clínicas",
        "administration": "🔐 Administração",
        "knowledge_graph_semantic_ai": "🧠 Knowledge Graph e IA Semântica",
        "multimodal_ai": "🧬 IA Multimodal",
        "voice_audio_speech_ai": "🎙️ Voz, Áudio e Speech AI",
        "agent_process_orchestration": "🧩 Orquestração de Agentes e Processos",
        "ai_model_agent_security": "🤖 Segurança de IA, Modelos e Agentes",
        "real_time_event_intelligence": "⚡ Inteligência de Eventos em Tempo Real",
        "privacy_data_protection_lgpd": "🔐 Privacidade, Proteção de Dados e LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, Identidade e Gestão de Acessos",
        "cryptography_confidential_computing": "🔏 Criptografia e Computação "
        "Confidencial",
        "software_supply_chain_security": "🧬 Segurança da Cadeia de Software",
        "privacy_enhancing_technologies": "🕵️ Tecnologias de Preservação de Privacidade",
        "geoai_earth_observation": "🛰️ GeoAI e Observação da Terra",
        "gis_location_intelligence": "🗺️ GIS e Inteligência de Localização",
        "drones_aerial_intelligence": "🛸 Drones e Inteligência Aérea",
        "spatial_computing_augmented_reality": "🥽 Computação Espacial e "
        "Realidade Aumentada",
        "iot_edge_intelligence": "📡 IoT e Inteligência de Borda",
        "computer_vision_video_analytics": "👁️ Visão Computacional e Vídeo Analytics",
        "digital_twins_simulation": "🏭 Gêmeos Digitais e Simulação",
        "robotics_autonomous_systems": "🤖 Robótica e Sistemas Autônomos",
        "scientific_computing_engineering": "🧮 Computação Científica e Engenharia",
        "simulation_optimization_operations_research": "🧪 Simulação, "
        "Otimização e Pesquisa "
        "Operacional",
        "research_labs_assisted_discovery": "🔬 Pesquisa, Laboratórios e "
        "Descoberta Assistida",
        "materials_product_engineering": "🧱 Materiais e Engenharia de Produtos",
        "construction_bim_digital_engineering": "🏗️ Construção, BIM e "
        "Engenharia Digital",
        "climate_meteorological_intelligence": "🌦️ Inteligência Climática e "
        "Meteorológica",
        "environmental_natural_resources_intelligence": "🌊 Inteligência "
        "Ambiental e Recursos "
        "Naturais",
        "energy_smart_grids": "⚡ Energia e Redes Inteligentes",
        "esg_sustainability": "🌱 ESG e Sustentabilidade",
        "emergency_disaster_management": "🧯 Resposta a Emergências e Gestão "
        "de Desastres",
        "mobility_traffic_transport": "🚦 Mobilidade, Tráfego e Transportes",
        "smart_cities_urban_infrastructure": "🏙️ Cidades Inteligentes e "
        "Infraestrutura Urbana",
        "networks_telecommunications_connectivity": "📶 Redes, "
        "Telecomunicações e "
        "Conectividade",
        "navigation_positioning_geolocation": "🧭 Navegação, Posicionamento e "
        "Geolocalização",
        "asset_management_smart_maintenance": "🔧 Gestão de Ativos e "
        "Manutenção Inteligente",
        "ai_software_engineering": "🧑\u200d💻 Engenharia de Software com IA",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Colaboração, Reuniões e "
        "Produtividade com IA",
        "digital_experiences_intelligent_interfaces": "🎨 Experiências "
        "Digitais e Interfaces "
        "Inteligentes",
        "software_testing_quality_reliability": "🧪 Testes, Qualidade e "
        "Confiabilidade de Software",
        "mobile_apps_omnichannel_experiences": "📱 Aplicações Móveis e "
        "Experiências Omnicanal",
        "digital_identity_verifiable_credentials": "🪪 Identidade Digital e "
        "Credenciais Verificáveis",
        "technology_governance_policy_compliance": "📜 Governança, Políticas e "
        "Conformidade Tecnológica",
        "data_traceability_provenance": "📦 Rastreabilidade e Proveniência de Dados",
        "enterprise_decision_intelligence": "🧠 Inteligência de Decisão Empresarial",
        "operational_security_resilience": "🛡️ Segurança Operacional e Resiliência",
        "responsible_ai_ethics_risk": "⚖️ IA Responsável, Ética e Avaliação de Riscos",
        "ai_evaluation_benchmarks_red_team": "🧪 Avaliação, Benchmarks e Red "
        "Team de IA",
        "model_explainability_interpretability": "🔍 Explicabilidade e "
        "Interpretabilidade de "
        "Modelos",
        "ai_bias_quality_monitoring": "📊 Monitoramento de Viés e Qualidade de IA",
        "ai_certification_system_evidence": "✅ Certificação e Evidências de "
        "Sistemas de IA",
        "mobility_transport_connected_vehicles": "🚚 Mobilidade, Transporte e "
        "Veículos Conectados",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agronegócio, "
        "Agricultura Inteligente "
        "e Bioeconomia",
    },
    "en_us": {
        "financial_solutions": "💰 Financial Solutions",
        "hr_people_analytics": "👥 HR and People Analytics",
        "document_ai": "📄 Document AI",
        "business_automation": "🤖 Business Automation",
        "enterprise_rag": "📚 Enterprise RAG",
        "site_app_generator": "🌐 Site and App Generator",
        "intelligent_support": "🎧 Intelligent Service and Support",
        "data_bi_copilot": "📊 Data & BI Copilot",
        "quality_process_management": "✅ Quality and Process Management",
        "crm_sales_intelligence": "🤝 CRM and Customer Experience",
        "erp_business_operations": "🏢 ERP and Business Operations",
        "supply_chain_procurement_logistics": "📦 Supply Chain, Procurement "
        "and Logistics",
        "legal_compliance": "⚖️ Legal and Compliance",
        "api_integrations_connectors": "🔌 API, Integrations and Connectors",
        "data_platform_governance": "🗄️ Data Platform and Governance",
        "cybersecurity_fraud_prevention": "🛡️ Cybersecurity and Fraud Prevention",
        "cloud_devops_finops": "☁️ Cloud, DevOps and FinOps Copilot",
        "ai_operations": "⚙️ AI Operations and Governance",
        "tools_analytics": "🛠️ Tools and Analytics",
        "pet_shops_veterinary_services": "🐾 Pet Shops and Veterinary Services",
        "supermarkets_wholesale": "🛒 Supermarkets and Wholesale",
        "retail_stores": "🏪 Stores and Retail",
        "dentistry": "🦷 Dentistry",
        "hospitals_clinics": "🏥 Hospitals and Clinics",
        "administration": "🔐 Administration",
        "knowledge_graph_semantic_ai": "🧠 Knowledge Graph and Semantic AI",
        "multimodal_ai": "🧬 Multimodal AI",
        "voice_audio_speech_ai": "🎙️ Voice, Audio and Speech AI",
        "agent_process_orchestration": "🧩 Agent and Process Orchestration",
        "ai_model_agent_security": "🤖 AI, Model and Agent Security",
        "real_time_event_intelligence": "⚡ Real-Time Event Intelligence",
        "privacy_data_protection_lgpd": "🔐 Privacy, Data Protection and LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, Identity and Access Management",
        "cryptography_confidential_computing": "🔏 Cryptography and "
        "Confidential Computing",
        "software_supply_chain_security": "🧬 Software Supply Chain Security",
        "privacy_enhancing_technologies": "🕵️ Privacy-Enhancing Technologies",
        "geoai_earth_observation": "🛰️ GeoAI and Earth Observation",
        "gis_location_intelligence": "🗺️ GIS and Location Intelligence",
        "drones_aerial_intelligence": "🛸 Drones and Aerial Intelligence",
        "spatial_computing_augmented_reality": "🥽 Spatial Computing and "
        "Augmented Reality",
        "iot_edge_intelligence": "📡 IoT and Edge Intelligence",
        "computer_vision_video_analytics": "👁️ Computer Vision and Video Analytics",
        "digital_twins_simulation": "🏭 Digital Twins and Simulation",
        "robotics_autonomous_systems": "🤖 Robotics and Autonomous Systems",
        "scientific_computing_engineering": "🧮 Scientific Computing and Engineering",
        "simulation_optimization_operations_research": "🧪 Simulation, "
        "Optimization and "
        "Operations "
        "Research",
        "research_labs_assisted_discovery": "🔬 Research, Laboratories and "
        "Assisted Discovery",
        "materials_product_engineering": "🧱 Materials and Product Engineering",
        "construction_bim_digital_engineering": "🏗️ Construction, BIM and "
        "Digital Engineering",
        "climate_meteorological_intelligence": "🌦️ Climate and "
        "Meteorological "
        "Intelligence",
        "environmental_natural_resources_intelligence": "🌊 Environmental "
        "and Natural "
        "Resources "
        "Intelligence",
        "energy_smart_grids": "⚡ Energy and Smart Grids",
        "esg_sustainability": "🌱 ESG and Sustainability",
        "emergency_disaster_management": "🧯 Emergency Response and "
        "Disaster Management",
        "mobility_traffic_transport": "🚦 Mobility, Traffic and Transportation",
        "smart_cities_urban_infrastructure": "🏙️ Smart Cities and Urban Infrastructure",
        "networks_telecommunications_connectivity": "📶 Networks, "
        "Telecommunications "
        "and Connectivity",
        "navigation_positioning_geolocation": "🧭 Navigation, Positioning "
        "and Geolocation",
        "asset_management_smart_maintenance": "🔧 Asset Management and "
        "Smart Maintenance",
        "ai_software_engineering": "🧑\u200d💻 AI-Assisted Software Engineering",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 AI "
        "Collaboration, Meetings "
        "and Productivity",
        "digital_experiences_intelligent_interfaces": "🎨 Digital "
        "Experiences and "
        "Intelligent "
        "Interfaces",
        "software_testing_quality_reliability": "🧪 Software Testing, "
        "Quality and Reliability",
        "mobile_apps_omnichannel_experiences": "📱 Mobile Applications and "
        "Omnichannel Experiences",
        "digital_identity_verifiable_credentials": "🪪 Digital Identity and "
        "Verifiable Credentials",
        "technology_governance_policy_compliance": "📜 Technology "
        "Governance, Policy and "
        "Compliance",
        "data_traceability_provenance": "📦 Data Traceability and Provenance",
        "enterprise_decision_intelligence": "🧠 Enterprise Decision Intelligence",
        "operational_security_resilience": "🛡️ Operational Security and Resilience",
        "responsible_ai_ethics_risk": "⚖️ Responsible AI, Ethics and Risk Assessment",
        "ai_evaluation_benchmarks_red_team": "🧪 AI Evaluation, Benchmarks "
        "and Red Teaming",
        "model_explainability_interpretability": "🔍 Model Explainability "
        "and Interpretability",
        "ai_bias_quality_monitoring": "📊 AI Bias and Quality Monitoring",
        "ai_certification_system_evidence": "✅ AI System Certification and Evidence",
        "mobility_transport_connected_vehicles": "🚚 Mobility, "
        "Transportation and "
        "Connected Vehicles",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agribusiness, "
        "Smart Agriculture "
        "and Bioeconomy",
    },
    "es": {
        "financial_solutions": "💰 Soluciones financieras",
        "hr_people_analytics": "👥 RR. HH. y People Analytics",
        "document_ai": "📄 IA documental",
        "business_automation": "🤖 Automatización empresarial",
        "enterprise_rag": "📚 RAG empresarial",
        "site_app_generator": "🌐 Generador de sitios y aplicaciones",
        "intelligent_support": "🎧 Atención y Soporte Inteligente",
        "data_bi_copilot": "📊 Copiloto de Datos y BI",
        "quality_process_management": "✅ Gestión de Calidad y Procesos",
        "crm_sales_intelligence": "🤝 CRM y Experiencia del Cliente",
        "erp_business_operations": "🏢 ERP y Operaciones Empresariales",
        "supply_chain_procurement_logistics": "📦 Cadena de Suministro, "
        "Compras y Logística",
        "legal_compliance": "⚖️ Jurídico y Cumplimiento",
        "api_integrations_connectors": "🔌 API, Integraciones y Conectores",
        "data_platform_governance": "🗄️ Plataforma y Gobernanza de Datos",
        "cybersecurity_fraud_prevention": "🛡️ Ciberseguridad y Prevención del Fraude",
        "cloud_devops_finops": "☁️ Cloud, DevOps y FinOps Copilot",
        "ai_operations": "⚙️ Operación y gobernanza de IA",
        "tools_analytics": "🛠️ Herramientas y analítica",
        "pet_shops_veterinary_services": "🐾 Tiendas de Mascotas y Servicios "
        "Veterinarios",
        "supermarkets_wholesale": "🛒 Supermercados y Mayoristas",
        "retail_stores": "🏪 Tiendas y Comercio Minorista",
        "dentistry": "🦷 Odontología",
        "hospitals_clinics": "🏥 Hospitales y Clínicas",
        "administration": "🔐 Administración",
        "knowledge_graph_semantic_ai": "🧠 Knowledge Graph e IA Semántica",
        "multimodal_ai": "🧬 IA Multimodal",
        "voice_audio_speech_ai": "🎙️ Voz, Audio y Speech AI",
        "agent_process_orchestration": "🧩 Orquestación de Agentes y Procesos",
        "ai_model_agent_security": "🤖 Seguridad de IA, Modelos y Agentes",
        "real_time_event_intelligence": "⚡ Inteligencia de Eventos en Tiempo Real",
        "privacy_data_protection_lgpd": "🔐 Privacidad, Protección de Datos y LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, Identidad y Gestión de Accesos",
        "cryptography_confidential_computing": "🔏 Criptografía y Computación "
        "Confidencial",
        "software_supply_chain_security": "🧬 Seguridad de la Cadena de Software",
        "privacy_enhancing_technologies": "🕵️ Tecnologías de Preservación de "
        "la Privacidad",
        "geoai_earth_observation": "🛰️ GeoAI y Observación de la Tierra",
        "gis_location_intelligence": "🗺️ GIS e Inteligencia de Ubicación",
        "drones_aerial_intelligence": "🛸 Drones e Inteligencia Aérea",
        "spatial_computing_augmented_reality": "🥽 Computación Espacial y "
        "Realidad Aumentada",
        "iot_edge_intelligence": "📡 IoT e Inteligencia de Borde",
        "computer_vision_video_analytics": "👁️ Visión Computacional y Video Analytics",
        "digital_twins_simulation": "🏭 Gemelos Digitales y Simulación",
        "robotics_autonomous_systems": "🤖 Robótica y Sistemas Autónomos",
        "scientific_computing_engineering": "🧮 Computación Científica e Ingeniería",
        "simulation_optimization_operations_research": "🧪 Simulación, "
        "Optimización e "
        "Investigación "
        "Operativa",
        "research_labs_assisted_discovery": "🔬 Investigación, Laboratorios y "
        "Descubrimiento Asistido",
        "materials_product_engineering": "🧱 Materiales e Ingeniería de Productos",
        "construction_bim_digital_engineering": "🏗️ Construcción, BIM e "
        "Ingeniería Digital",
        "climate_meteorological_intelligence": "🌦️ Inteligencia Climática y "
        "Meteorológica",
        "environmental_natural_resources_intelligence": "🌊 Inteligencia "
        "Ambiental y Recursos "
        "Naturales",
        "energy_smart_grids": "⚡ Energía y Redes Inteligentes",
        "esg_sustainability": "🌱 ESG y Sostenibilidad",
        "emergency_disaster_management": "🧯 Respuesta a Emergencias y Gestión "
        "de Desastres",
        "mobility_traffic_transport": "🚦 Movilidad, Tráfico y Transportes",
        "smart_cities_urban_infrastructure": "🏙️ Ciudades Inteligentes e "
        "Infraestructura Urbana",
        "networks_telecommunications_connectivity": "📶 Redes, "
        "Telecomunicaciones y "
        "Conectividad",
        "navigation_positioning_geolocation": "🧭 Navegación, Posicionamiento "
        "y Geolocalización",
        "asset_management_smart_maintenance": "🔧 Gestión de Activos y "
        "Mantenimiento Inteligente",
        "ai_software_engineering": "🧑\u200d💻 Ingeniería de Software con IA",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Colaboración, Reuniones y "
        "Productividad con IA",
        "digital_experiences_intelligent_interfaces": "🎨 Experiencias "
        "Digitales e Interfaces "
        "Inteligentes",
        "software_testing_quality_reliability": "🧪 Pruebas, Calidad y "
        "Confiabilidad de Software",
        "mobile_apps_omnichannel_experiences": "📱 Aplicaciones Móviles y "
        "Experiencias Omnicanal",
        "digital_identity_verifiable_credentials": "🪪 Identidad Digital y "
        "Credenciales Verificables",
        "technology_governance_policy_compliance": "📜 Gobernanza, Políticas y "
        "Cumplimiento Tecnológico",
        "data_traceability_provenance": "📦 Trazabilidad y Procedencia de Datos",
        "enterprise_decision_intelligence": "🧠 Inteligencia de Decisión Empresarial",
        "operational_security_resilience": "🛡️ Seguridad Operacional y Resiliencia",
        "responsible_ai_ethics_risk": "⚖️ IA Responsable, Ética y Evaluación de Riesgos",
        "ai_evaluation_benchmarks_red_team": "🧪 Evaluación, Benchmarks y Red "
        "Team de IA",
        "model_explainability_interpretability": "🔍 Explicabilidad e "
        "Interpretabilidad de "
        "Modelos",
        "ai_bias_quality_monitoring": "📊 Monitoreo de Sesgo y Calidad de IA",
        "ai_certification_system_evidence": "✅ Certificación y Evidencias de "
        "Sistemas de IA",
        "mobility_transport_connected_vehicles": "🚚 Movilidad, Transporte y "
        "Vehículos Conectados",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agronegocio, "
        "Agricultura Inteligente "
        "y Bioeconomía",
    },
    "fr": {
        "financial_solutions": "💰 Solutions financières",
        "hr_people_analytics": "👥 RH et People Analytics",
        "document_ai": "📄 IA documentaire",
        "business_automation": "🤖 Automatisation d’entreprise",
        "enterprise_rag": "📚 RAG d’entreprise",
        "site_app_generator": "🌐 Générateur de sites et applications",
        "intelligent_support": "🎧 Service et Support Intelligents",
        "data_bi_copilot": "📊 Copilote Data et BI",
        "quality_process_management": "✅ Gestion de la Qualité et des Processus",
        "crm_sales_intelligence": "🤝 CRM et Expérience Client",
        "erp_business_operations": "🏢 ERP et Opérations d’Entreprise",
        "supply_chain_procurement_logistics": "📦 Chaîne d’Approvisionnement, "
        "Achats et Logistique",
        "legal_compliance": "⚖️ Juridique et Conformité",
        "api_integrations_connectors": "🔌 API, Intégrations et Connecteurs",
        "data_platform_governance": "🗄️ Plateforme et Gouvernance des Données",
        "cybersecurity_fraud_prevention": "🛡️ Cybersécurité et Prévention de la Fraude",
        "cloud_devops_finops": "☁️ Cloud, DevOps et FinOps Copilot",
        "ai_operations": "⚙️ Opérations et gouvernance IA",
        "tools_analytics": "🛠️ Outils et analytique",
        "pet_shops_veterinary_services": "🐾 Animaleries et Services Vétérinaires",
        "supermarkets_wholesale": "🛒 Supermarchés et Commerce de Gros",
        "retail_stores": "🏪 Magasins et Commerce de Détail",
        "dentistry": "🦷 Odontologie",
        "hospitals_clinics": "🏥 Hôpitaux et Cliniques",
        "administration": "🔐 Administration",
        "knowledge_graph_semantic_ai": "🧠 Graphe de connaissances et IA sémantique",
        "multimodal_ai": "🧬 IA multimodale",
        "voice_audio_speech_ai": "🎙️ Voix, audio et IA vocale",
        "agent_process_orchestration": "🧩 Orchestration des agents et des processus",
        "ai_model_agent_security": "🤖 Sécurité de l'IA, des modèles et des agents",
        "real_time_event_intelligence": "⚡ Intelligence des événements en temps réel",
        "privacy_data_protection_lgpd": "🔐 Confidentialité, protection des "
        "données et LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, identité et gestion des accès",
        "cryptography_confidential_computing": "🔏 Cryptographie et "
        "informatique confidentielle",
        "software_supply_chain_security": "🧬 Sécurité de la chaîne logicielle",
        "privacy_enhancing_technologies": "🕵️ Technologies de protection de "
        "la vie privée",
        "geoai_earth_observation": "🛰️ GeoAI et observation de la Terre",
        "gis_location_intelligence": "🗺️ SIG et intelligence de localisation",
        "drones_aerial_intelligence": "🛸 Drones et intelligence aérienne",
        "spatial_computing_augmented_reality": "🥽 Informatique spatiale et "
        "réalité augmentée",
        "iot_edge_intelligence": "📡 IoT et intelligence en périphérie",
        "computer_vision_video_analytics": "👁️ Vision par ordinateur et analyse vidéo",
        "digital_twins_simulation": "🏭 Jumeaux numériques et simulation",
        "robotics_autonomous_systems": "🤖 Robotique et systèmes autonomes",
        "scientific_computing_engineering": "🧮 Calcul scientifique et ingénierie",
        "simulation_optimization_operations_research": "🧪 Simulation, "
        "optimisation et "
        "recherche "
        "opérationnelle",
        "research_labs_assisted_discovery": "🔬 Recherche, laboratoires et "
        "découverte assistée",
        "materials_product_engineering": "🧱 Matériaux et ingénierie produit",
        "construction_bim_digital_engineering": "🏗️ Construction, BIM et "
        "ingénierie numérique",
        "climate_meteorological_intelligence": "🌦️ Intelligence climatique et "
        "météorologique",
        "environmental_natural_resources_intelligence": "🌊 Intelligence "
        "environnementale et "
        "ressources "
        "naturelles",
        "energy_smart_grids": "⚡ Énergie et réseaux intelligents",
        "esg_sustainability": "🌱 ESG et durabilité",
        "emergency_disaster_management": "🧯 Intervention d'urgence et gestion "
        "des catastrophes",
        "mobility_traffic_transport": "🚦 Mobilité, trafic et transports",
        "smart_cities_urban_infrastructure": "🏙️ Villes intelligentes et "
        "infrastructures urbaines",
        "networks_telecommunications_connectivity": "📶 Réseaux, "
        "télécommunications et "
        "connectivité",
        "navigation_positioning_geolocation": "🧭 Navigation, positionnement "
        "et géolocalisation",
        "asset_management_smart_maintenance": "🔧 Gestion des actifs et "
        "maintenance intelligente",
        "ai_software_engineering": "🧑\u200d💻 Ingénierie logicielle assistée par IA",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Collaboration, réunions et "
        "productivité avec l'IA",
        "digital_experiences_intelligent_interfaces": "🎨 Expériences "
        "numériques et "
        "interfaces "
        "intelligentes",
        "software_testing_quality_reliability": "🧪 Tests, qualité et "
        "fiabilité logicielle",
        "mobile_apps_omnichannel_experiences": "📱 Applications mobiles et "
        "expériences omnicanales",
        "digital_identity_verifiable_credentials": "🪪 Identité numérique et "
        "justificatifs vérifiables",
        "technology_governance_policy_compliance": "📜 Gouvernance, politiques "
        "et conformité "
        "technologiques",
        "data_traceability_provenance": "📦 Traçabilité et provenance des données",
        "enterprise_decision_intelligence": "🧠 Intelligence décisionnelle "
        "d'entreprise",
        "operational_security_resilience": "🛡️ Sécurité opérationnelle et résilience",
        "responsible_ai_ethics_risk": "⚖️ IA responsable, éthique et "
        "évaluation des risques",
        "ai_evaluation_benchmarks_red_team": "🧪 Évaluation, benchmarks et red "
        "teaming de l'IA",
        "model_explainability_interpretability": "🔍 Explicabilité et "
        "interprétabilité des "
        "modèles",
        "ai_bias_quality_monitoring": "📊 Surveillance des biais et de la "
        "qualité de l'IA",
        "ai_certification_system_evidence": "✅ Certification et preuves des "
        "systèmes d'IA",
        "mobility_transport_connected_vehicles": "🚚 Mobilité, transport et "
        "véhicules connectés",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agrobusiness, "
        "agriculture "
        "intelligente et "
        "bioéconomie",
    },
    "de": {
        "financial_solutions": "💰 Finanzlösungen",
        "hr_people_analytics": "👥 Personalwesen und People Analytics",
        "document_ai": "📄 Dokumenten-KI",
        "business_automation": "🤖 Unternehmensautomatisierung",
        "enterprise_rag": "📚 Enterprise RAG",
        "site_app_generator": "🌐 Website- und App-Generator",
        "intelligent_support": "🎧 Intelligenter Service und Support",
        "data_bi_copilot": "📊 Daten- und BI-Copilot",
        "quality_process_management": "✅ Qualitäts- und Prozessmanagement",
        "crm_sales_intelligence": "🤝 CRM und Kundenerlebnis",
        "erp_business_operations": "🏢 ERP und Geschäftsabläufe",
        "supply_chain_procurement_logistics": "📦 Lieferkette, Beschaffung und "
        "Logistik",
        "legal_compliance": "⚖️ Recht und Compliance",
        "api_integrations_connectors": "🔌 APIs, Integrationen und Konnektoren",
        "data_platform_governance": "🗄️ Datenplattform und Data Governance",
        "cybersecurity_fraud_prevention": "🛡️ Cybersicherheit und Betrugsprävention",
        "cloud_devops_finops": "☁️ Cloud-, DevOps- und FinOps-Copilot",
        "ai_operations": "⚙️ KI-Betrieb und Governance",
        "tools_analytics": "🛠️ Werkzeuge und Analysen",
        "pet_shops_veterinary_services": "🐾 Tierhandlungen und Veterinärdienste",
        "supermarkets_wholesale": "🛒 Supermärkte und Großhandel",
        "retail_stores": "🏪 Geschäfte und Einzelhandel",
        "dentistry": "🦷 Zahnmedizin",
        "hospitals_clinics": "🏥 Krankenhäuser und Kliniken",
        "administration": "🔐 Administration",
        "knowledge_graph_semantic_ai": "🧠 Wissensgraph und semantische KI",
        "multimodal_ai": "🧬 Multimodale KI",
        "voice_audio_speech_ai": "🎙️ Sprache, Audio und Speech AI",
        "agent_process_orchestration": "🧩 Orchestrierung von Agenten und Prozessen",
        "ai_model_agent_security": "🤖 Sicherheit für KI, Modelle und Agenten",
        "real_time_event_intelligence": "⚡ Echtzeit-Ereignisintelligenz",
        "privacy_data_protection_lgpd": "🔐 Datenschutz, Datensicherheit und LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, Identität und Zugriffsverwaltung",
        "cryptography_confidential_computing": "🔏 Kryptografie und "
        "vertrauliches Computing",
        "software_supply_chain_security": "🧬 Sicherheit der Software-Lieferkette",
        "privacy_enhancing_technologies": "🕵️ Technologien zum Schutz der Privatsphäre",
        "geoai_earth_observation": "🛰️ GeoAI und Erdbeobachtung",
        "gis_location_intelligence": "🗺️ GIS und Standortintelligenz",
        "drones_aerial_intelligence": "🛸 Drohnen und Luftbildintelligenz",
        "spatial_computing_augmented_reality": "🥽 Räumliches Computing und "
        "erweiterte Realität",
        "iot_edge_intelligence": "📡 IoT und Edge Intelligence",
        "computer_vision_video_analytics": "👁️ Computer Vision und Videoanalyse",
        "digital_twins_simulation": "🏭 Digitale Zwillinge und Simulation",
        "robotics_autonomous_systems": "🤖 Robotik und autonome Systeme",
        "scientific_computing_engineering": "🧮 Wissenschaftliches Rechnen und "
        "Ingenieurwesen",
        "simulation_optimization_operations_research": "🧪 Simulation, "
        "Optimierung und "
        "Operations Research",
        "research_labs_assisted_discovery": "🔬 Forschung, Labore und "
        "unterstützte Entdeckung",
        "materials_product_engineering": "🧱 Werkstoffe und Produktentwicklung",
        "construction_bim_digital_engineering": "🏗️ Bauwesen, BIM und "
        "digitales Engineering",
        "climate_meteorological_intelligence": "🌦️ Klima- und Wetterintelligenz",
        "environmental_natural_resources_intelligence": "🌊 Umwelt- und "
        "Ressourcenintelligenz",
        "energy_smart_grids": "⚡ Energie und intelligente Netze",
        "esg_sustainability": "🌱 ESG und Nachhaltigkeit",
        "emergency_disaster_management": "🧯 Notfallreaktion und "
        "Katastrophenmanagement",
        "mobility_traffic_transport": "🚦 Mobilität, Verkehr und Transport",
        "smart_cities_urban_infrastructure": "🏙️ Smart Cities und urbane Infrastruktur",
        "networks_telecommunications_connectivity": "📶 Netzwerke, "
        "Telekommunikation und "
        "Konnektivität",
        "navigation_positioning_geolocation": "🧭 Navigation, Positionierung "
        "und Geolokalisierung",
        "asset_management_smart_maintenance": "🔧 Asset-Management und "
        "intelligente Wartung",
        "ai_software_engineering": "🧑\u200d💻 KI-gestütztes Software Engineering",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Zusammenarbeit, Meetings "
        "und Produktivität mit KI",
        "digital_experiences_intelligent_interfaces": "🎨 Digitale Erlebnisse "
        "und intelligente "
        "Schnittstellen",
        "software_testing_quality_reliability": "🧪 Softwaretests, Qualität "
        "und Zuverlässigkeit",
        "mobile_apps_omnichannel_experiences": "📱 Mobile Anwendungen und "
        "Omnichannel-Erlebnisse",
        "digital_identity_verifiable_credentials": "🪪 Digitale Identität und "
        "überprüfbare Nachweise",
        "technology_governance_policy_compliance": "📜 Technologie-Governance, "
        "Richtlinien und "
        "Compliance",
        "data_traceability_provenance": "📦 Datenrückverfolgbarkeit und Provenienz",
        "enterprise_decision_intelligence": "🧠 Unternehmensentscheidungsintelligenz",
        "operational_security_resilience": "🛡️ Betriebssicherheit und Resilienz",
        "responsible_ai_ethics_risk": "⚖️ Verantwortungsvolle KI, Ethik und "
        "Risikobewertung",
        "ai_evaluation_benchmarks_red_team": "🧪 KI-Evaluierung, Benchmarks "
        "und Red Teaming",
        "model_explainability_interpretability": "🔍 Erklärbarkeit und "
        "Interpretierbarkeit von "
        "Modellen",
        "ai_bias_quality_monitoring": "📊 Überwachung von KI-Bias und Qualität",
        "ai_certification_system_evidence": "✅ Zertifizierung und Nachweise "
        "für KI-Systeme",
        "mobility_transport_connected_vehicles": "🚚 Mobilität, Transport und "
        "vernetzte Fahrzeuge",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agribusiness, "
        "intelligente "
        "Landwirtschaft und "
        "Bioökonomie",
    },
    "it": {
        "financial_solutions": "💰 Soluzioni finanziarie",
        "hr_people_analytics": "👥 Risorse Umane e People Analytics",
        "document_ai": "📄 IA documentale",
        "business_automation": "🤖 Automazione aziendale",
        "enterprise_rag": "📚 RAG aziendale",
        "site_app_generator": "🌐 Generatore di siti e app",
        "intelligent_support": "🎧 Assistenza e Supporto Intelligente",
        "data_bi_copilot": "📊 Copilota Dati e BI",
        "quality_process_management": "✅ Gestione della Qualità e dei Processi",
        "crm_sales_intelligence": "🤝 CRM ed Esperienza Cliente",
        "erp_business_operations": "🏢 ERP e Operazioni Aziendali",
        "supply_chain_procurement_logistics": "📦 Supply Chain, Acquisti e Logistica",
        "legal_compliance": "⚖️ Legale e Compliance",
        "api_integrations_connectors": "🔌 API, Integrazioni e Connettori",
        "data_platform_governance": "🗄️ Piattaforma e Governance dei Dati",
        "cybersecurity_fraud_prevention": "🛡️ Cybersicurezza e Prevenzione delle Frodi",
        "cloud_devops_finops": "☁️ Cloud, DevOps e FinOps Copilot",
        "ai_operations": "⚙️ Operazioni e governance IA",
        "tools_analytics": "🛠️ Strumenti e analisi",
        "pet_shops_veterinary_services": "🐾 Negozi per Animali e Servizi Veterinari",
        "supermarkets_wholesale": "🛒 Supermercati e Commercio all'Ingrosso",
        "retail_stores": "🏪 Negozi e Commercio al Dettaglio",
        "dentistry": "🦷 Odontoiatria",
        "hospitals_clinics": "🏥 Ospedali e Cliniche",
        "administration": "🔐 Amministrazione",
        "knowledge_graph_semantic_ai": "🧠 Knowledge Graph e IA semantica",
        "multimodal_ai": "🧬 IA multimodale",
        "voice_audio_speech_ai": "🎙️ Voce, audio e Speech AI",
        "agent_process_orchestration": "🧩 Orchestrazione di agenti e processi",
        "ai_model_agent_security": "🤖 Sicurezza di IA, modelli e agenti",
        "real_time_event_intelligence": "⚡ Intelligenza degli eventi in tempo reale",
        "privacy_data_protection_lgpd": "🔐 Privacy, protezione dei dati e LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, identità e gestione "
        "degli accessi",
        "cryptography_confidential_computing": "🔏 Crittografia e confidential "
        "computing",
        "software_supply_chain_security": "🧬 Sicurezza della catena del software",
        "privacy_enhancing_technologies": "🕵️ Tecnologie per la tutela della privacy",
        "geoai_earth_observation": "🛰️ GeoAI e osservazione della Terra",
        "gis_location_intelligence": "🗺️ GIS e intelligenza della posizione",
        "drones_aerial_intelligence": "🛸 Droni e intelligenza aerea",
        "spatial_computing_augmented_reality": "🥽 Spatial computing e realtà "
        "aumentata",
        "iot_edge_intelligence": "📡 IoT e intelligenza edge",
        "computer_vision_video_analytics": "👁️ Visione artificiale e analisi video",
        "digital_twins_simulation": "🏭 Gemelli digitali e simulazione",
        "robotics_autonomous_systems": "🤖 Robotica e sistemi autonomi",
        "scientific_computing_engineering": "🧮 Calcolo scientifico e ingegneria",
        "simulation_optimization_operations_research": "🧪 Simulazione, "
        "ottimizzazione e "
        "ricerca operativa",
        "research_labs_assisted_discovery": "🔬 Ricerca, laboratori e scoperta "
        "assistita",
        "materials_product_engineering": "🧱 Materiali e ingegneria di prodotto",
        "construction_bim_digital_engineering": "🏗️ Costruzioni, BIM e "
        "ingegneria digitale",
        "climate_meteorological_intelligence": "🌦️ Intelligenza climatica e "
        "meteorologica",
        "environmental_natural_resources_intelligence": "🌊 Intelligenza "
        "ambientale e risorse "
        "naturali",
        "energy_smart_grids": "⚡ Energia e reti intelligenti",
        "esg_sustainability": "🌱 ESG e sostenibilità",
        "emergency_disaster_management": "🧯 Risposta alle emergenze e "
        "gestione dei disastri",
        "mobility_traffic_transport": "🚦 Mobilità, traffico e trasporti",
        "smart_cities_urban_infrastructure": "🏙️ Città intelligenti e "
        "infrastrutture urbane",
        "networks_telecommunications_connectivity": "📶 Reti, "
        "telecomunicazioni e "
        "connettività",
        "navigation_positioning_geolocation": "🧭 Navigazione, posizionamento "
        "e geolocalizzazione",
        "asset_management_smart_maintenance": "🔧 Gestione degli asset e "
        "manutenzione intelligente",
        "ai_software_engineering": "🧑\u200d💻 Ingegneria del software con IA",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Collaborazione, riunioni e "
        "produttività con IA",
        "digital_experiences_intelligent_interfaces": "🎨 Esperienze digitali "
        "e interfacce "
        "intelligenti",
        "software_testing_quality_reliability": "🧪 Test, qualità e "
        "affidabilità del software",
        "mobile_apps_omnichannel_experiences": "📱 Applicazioni mobili ed "
        "esperienze omnicanale",
        "digital_identity_verifiable_credentials": "🪪 Identità digitale e "
        "credenziali verificabili",
        "technology_governance_policy_compliance": "📜 Governance, politiche e "
        "conformità tecnologica",
        "data_traceability_provenance": "📦 Tracciabilità e provenienza dei dati",
        "enterprise_decision_intelligence": "🧠 Intelligenza decisionale aziendale",
        "operational_security_resilience": "🛡️ Sicurezza operativa e resilienza",
        "responsible_ai_ethics_risk": "⚖️ IA responsabile, etica e "
        "valutazione dei rischi",
        "ai_evaluation_benchmarks_red_team": "🧪 Valutazione, benchmark e red "
        "team dell'IA",
        "model_explainability_interpretability": "🔍 Spiegabilità e "
        "interpretabilità dei "
        "modelli",
        "ai_bias_quality_monitoring": "📊 Monitoraggio di bias e qualità dell'IA",
        "ai_certification_system_evidence": "✅ Certificazione ed evidenze dei "
        "sistemi di IA",
        "mobility_transport_connected_vehicles": "🚚 Mobilità, trasporti e "
        "veicoli connessi",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agribusiness, "
        "agricoltura "
        "intelligente e "
        "bioeconomia",
    },
    "ro": {
        "financial_solutions": "💰 Soluții financiare",
        "hr_people_analytics": "👥 Resurse Umane și People Analytics",
        "document_ai": "📄 IA pentru documente",
        "business_automation": "🤖 Automatizare empresarială",
        "enterprise_rag": "📚 RAG pentru întreprinderi",
        "site_app_generator": "🌐 Generator de site-uri și aplicații",
        "intelligent_support": "🎧 Asistență și Suport Inteligent",
        "data_bi_copilot": "📊 Copilot de Date și BI",
        "quality_process_management": "✅ Managementul Calității și Proceselor",
        "crm_sales_intelligence": "🤝 CRM și Experiența Clienților",
        "erp_business_operations": "🏢 ERP și Operațiuni de Afaceri",
        "supply_chain_procurement_logistics": "📦 Lanț de Aprovizionare, "
        "Achiziții și Logistică",
        "legal_compliance": "⚖️ Juridic și Conformitate",
        "api_integrations_connectors": "🔌 API, Integrări și Conectori",
        "data_platform_governance": "🗄️ Platformă și Guvernanță a Datelor",
        "cybersecurity_fraud_prevention": "🛡️ Securitate Cibernetică și "
        "Prevenirea Fraudelor",
        "cloud_devops_finops": "☁️ Cloud, DevOps și FinOps Copilot",
        "ai_operations": "⚙️ Operațiuni și guvernanță IA",
        "tools_analytics": "🛠️ Instrumente și analiză",
        "pet_shops_veterinary_services": "🐾 Magazine pentru Animale și "
        "Servicii Veterinare",
        "supermarkets_wholesale": "🛒 Supermarketuri și Comerț Angro",
        "retail_stores": "🏪 Magazine și Comerț cu Amănuntul",
        "dentistry": "🦷 Stomatologie",
        "hospitals_clinics": "🏥 Spitale și Clinici",
        "administration": "🔐 Administrare",
        "knowledge_graph_semantic_ai": "🧠 Graf de cunoștințe și IA semantică",
        "multimodal_ai": "🧬 IA multimodală",
        "voice_audio_speech_ai": "🎙️ Voce, audio și Speech AI",
        "agent_process_orchestration": "🧩 Orchestrarea agenților și proceselor",
        "ai_model_agent_security": "🤖 Securitatea IA, modelelor și agenților",
        "real_time_event_intelligence": "⚡ Inteligența evenimentelor în timp real",
        "privacy_data_protection_lgpd": "🔐 Confidențialitate, protecția "
        "datelor și LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, identitate și "
        "managementul accesului",
        "cryptography_confidential_computing": "🔏 Criptografie și calcul confidențial",
        "software_supply_chain_security": "🧬 Securitatea lanțului software",
        "privacy_enhancing_technologies": "🕵️ Tehnologii de protejare a "
        "confidențialității",
        "geoai_earth_observation": "🛰️ GeoAI și observarea Pământului",
        "gis_location_intelligence": "🗺️ GIS și inteligență de localizare",
        "drones_aerial_intelligence": "🛸 Drone și inteligență aeriană",
        "spatial_computing_augmented_reality": "🥽 Calcul spațial și realitate "
        "augmentată",
        "iot_edge_intelligence": "📡 IoT și inteligență la margine",
        "computer_vision_video_analytics": "👁️ Viziune computerizată și analiză video",
        "digital_twins_simulation": "🏭 Gemeni digitali și simulare",
        "robotics_autonomous_systems": "🤖 Robotică și sisteme autonome",
        "scientific_computing_engineering": "🧮 Calcul științific și inginerie",
        "simulation_optimization_operations_research": "🧪 Simulare, "
        "optimizare și "
        "cercetare "
        "operațională",
        "research_labs_assisted_discovery": "🔬 Cercetare, laboratoare și "
        "descoperire asistată",
        "materials_product_engineering": "🧱 Materiale și ingineria produselor",
        "construction_bim_digital_engineering": "🏗️ Construcții, BIM și "
        "inginerie digitală",
        "climate_meteorological_intelligence": "🌦️ Inteligență climatică și "
        "meteorologică",
        "environmental_natural_resources_intelligence": "🌊 Inteligență de "
        "mediu și resurse "
        "naturale",
        "energy_smart_grids": "⚡ Energie și rețele inteligente",
        "esg_sustainability": "🌱 ESG și sustenabilitate",
        "emergency_disaster_management": "🧯 Răspuns la urgențe și "
        "managementul dezastrelor",
        "mobility_traffic_transport": "🚦 Mobilitate, trafic și transport",
        "smart_cities_urban_infrastructure": "🏙️ Orașe inteligente și "
        "infrastructură urbană",
        "networks_telecommunications_connectivity": "📶 Rețele, "
        "telecomunicații și "
        "conectivitate",
        "navigation_positioning_geolocation": "🧭 Navigație, poziționare și "
        "geolocalizare",
        "asset_management_smart_maintenance": "🔧 Managementul activelor și "
        "mentenanță inteligentă",
        "ai_software_engineering": "🧑\u200d💻 Inginerie software asistată de IA",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Colaborare, întâlniri și "
        "productivitate cu IA",
        "digital_experiences_intelligent_interfaces": "🎨 Experiențe digitale "
        "și interfețe "
        "inteligente",
        "software_testing_quality_reliability": "🧪 Testare, calitate și "
        "fiabilitate software",
        "mobile_apps_omnichannel_experiences": "📱 Aplicații mobile și "
        "experiențe omnicanal",
        "digital_identity_verifiable_credentials": "🪪 Identitate digitală și "
        "acreditări verificabile",
        "technology_governance_policy_compliance": "📜 Guvernanță, politici și "
        "conformitate tehnologică",
        "data_traceability_provenance": "📦 Trasabilitatea și proveniența datelor",
        "enterprise_decision_intelligence": "🧠 Inteligență decizională pentru "
        "întreprinderi",
        "operational_security_resilience": "🛡️ Securitate operațională și reziliență",
        "responsible_ai_ethics_risk": "⚖️ IA responsabilă, etică și evaluarea "
        "riscurilor",
        "ai_evaluation_benchmarks_red_team": "🧪 Evaluare, benchmarkuri și red "
        "teaming pentru IA",
        "model_explainability_interpretability": "🔍 Explicabilitatea și "
        "interpretabilitatea "
        "modelelor",
        "ai_bias_quality_monitoring": "📊 Monitorizarea părtinirii și calității IA",
        "ai_certification_system_evidence": "✅ Certificare și dovezi pentru "
        "sistemele IA",
        "mobility_transport_connected_vehicles": "🚚 Mobilitate, transport și "
        "vehicule conectate",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Agribusiness, "
        "agricultură inteligentă "
        "și bioeconomie",
    },
    "ua": {
        "financial_solutions": "💰 Фінансові рішення",
        "hr_people_analytics": "👥 HR та аналітика персоналу",
        "document_ai": "📄 ШІ для документів",
        "business_automation": "🤖 Автоматизація бізнесу",
        "enterprise_rag": "📚 Корпоративний RAG",
        "site_app_generator": "🌐 Генератор сайтів і застосунків",
        "intelligent_support": "🎧 Інтелектуальне Обслуговування та Підтримка",
        "data_bi_copilot": "📊 Помічник з Даних і BI",
        "quality_process_management": "✅ Управління Якістю та Процесами",
        "crm_sales_intelligence": "🤝 CRM і Клієнтський Досвід",
        "erp_business_operations": "🏢 ERP і Бізнес-Операції",
        "supply_chain_procurement_logistics": "📦 Ланцюг Постачання, Закупівлі "
        "та Логістика",
        "legal_compliance": "⚖️ Юридичні Питання та Відповідність",
        "api_integrations_connectors": "🔌 API, Інтеграції та Конектори",
        "data_platform_governance": "🗄️ Платформа та Управління Даними",
        "cybersecurity_fraud_prevention": "🛡️ Кібербезпека та Запобігання Шахрайству",
        "cloud_devops_finops": "☁️ Cloud, DevOps і FinOps Copilot",
        "ai_operations": "⚙️ Операції та управління ШІ",
        "tools_analytics": "🛠️ Інструменти й аналітика",
        "pet_shops_veterinary_services": "🐾 Зоомагазини та Ветеринарні Послуги",
        "supermarkets_wholesale": "🛒 Супермаркети та Оптова Торгівля",
        "retail_stores": "🏪 Магазини та Роздрібна Торгівля",
        "dentistry": "🦷 Стоматологія",
        "hospitals_clinics": "🏥 Лікарні та Клініки",
        "administration": "🔐 Адміністрування",
        "knowledge_graph_semantic_ai": "🧠 Граф знань і семантичний ШІ",
        "multimodal_ai": "🧬 Мультимодальний ШІ",
        "voice_audio_speech_ai": "🎙️ Голос, аудіо та мовленнєвий ШІ",
        "agent_process_orchestration": "🧩 Оркестрація агентів і процесів",
        "ai_model_agent_security": "🤖 Безпека ШІ, моделей і агентів",
        "real_time_event_intelligence": "⚡ Аналітика подій у реальному часі",
        "privacy_data_protection_lgpd": "🔐 Приватність, захист даних і LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, ідентичність і керування "
        "доступом",
        "cryptography_confidential_computing": "🔏 Криптографія та "
        "конфіденційні обчислення",
        "software_supply_chain_security": "🧬 Безпека ланцюга постачання ПЗ",
        "privacy_enhancing_technologies": "🕵️ Технології збереження приватності",
        "geoai_earth_observation": "🛰️ GeoAI та спостереження Землі",
        "gis_location_intelligence": "🗺️ GIS та геолокаційна аналітика",
        "drones_aerial_intelligence": "🛸 Дрони та повітряна аналітика",
        "spatial_computing_augmented_reality": "🥽 Просторові обчислення та "
        "доповнена реальність",
        "iot_edge_intelligence": "📡 IoT та периферійний інтелект",
        "computer_vision_video_analytics": "👁️ Комп'ютерний зір і відеоаналітика",
        "digital_twins_simulation": "🏭 Цифрові двійники та моделювання",
        "robotics_autonomous_systems": "🤖 Робототехніка та автономні системи",
        "scientific_computing_engineering": "🧮 Наукові обчислення та інженерія",
        "simulation_optimization_operations_research": "🧪 Моделювання, "
        "оптимізація та "
        "дослідження операцій",
        "research_labs_assisted_discovery": "🔬 Дослідження, лабораторії та "
        "підтримувані відкриття",
        "materials_product_engineering": "🧱 Матеріали та інженерія продуктів",
        "construction_bim_digital_engineering": "🏗️ Будівництво, BIM та "
        "цифрова інженерія",
        "climate_meteorological_intelligence": "🌦️ Кліматична та "
        "метеорологічна аналітика",
        "environmental_natural_resources_intelligence": "🌊 Екологічна "
        "аналітика та "
        "природні ресурси",
        "energy_smart_grids": "⚡ Енергетика та розумні мережі",
        "esg_sustainability": "🌱 ESG та сталий розвиток",
        "emergency_disaster_management": "🧯 Реагування на надзвичайні "
        "ситуації та катастрофи",
        "mobility_traffic_transport": "🚦 Мобільність, трафік і транспорт",
        "smart_cities_urban_infrastructure": "🏙️ Розумні міста та міська інфраструктура",
        "networks_telecommunications_connectivity": "📶 Мережі, "
        "телекомунікації та "
        "зв'язок",
        "navigation_positioning_geolocation": "🧭 Навігація, позиціонування та "
        "геолокація",
        "asset_management_smart_maintenance": "🔧 Управління активами та "
        "розумне обслуговування",
        "ai_software_engineering": "🧑\u200d💻 Розробка програмного забезпечення з ШІ",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 Співпраця, "
        "зустрічі та продуктивність "
        "із ШІ",
        "digital_experiences_intelligent_interfaces": "🎨 Цифровий досвід та "
        "інтелектуальні "
        "інтерфейси",
        "software_testing_quality_reliability": "🧪 Тестування, якість і надійність ПЗ",
        "mobile_apps_omnichannel_experiences": "📱 Мобільні застосунки та "
        "омніканальний досвід",
        "digital_identity_verifiable_credentials": "🪪 Цифрова ідентичність і "
        "перевірні облікові дані",
        "technology_governance_policy_compliance": "📜 Технологічне "
        "врядування, політики та "
        "відповідність",
        "data_traceability_provenance": "📦 Простежуваність і походження даних",
        "enterprise_decision_intelligence": "🧠 Інтелект підтримки бізнес-рішень",
        "operational_security_resilience": "🛡️ Операційна безпека та стійкість",
        "responsible_ai_ethics_risk": "⚖️ Відповідальний ШІ, етика та "
        "оцінювання ризиків",
        "ai_evaluation_benchmarks_red_team": "🧪 Оцінювання, бенчмарки та red "
        "team для ШІ",
        "model_explainability_interpretability": "🔍 Пояснюваність та "
        "інтерпретованість моделей",
        "ai_bias_quality_monitoring": "📊 Моніторинг упередженості та якості ШІ",
        "ai_certification_system_evidence": "✅ Сертифікація та докази для систем ШІ",
        "mobility_transport_connected_vehicles": "🚚 Мобільність, транспорт і "
        "підключені транспортні "
        "засоби",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Агробізнес, розумне "
        "сільське господарство "
        "та біоекономіка",
    },
    "ru": {
        "financial_solutions": "💰 Финансовые решения",
        "hr_people_analytics": "👥 HR и аналитика персонала",
        "document_ai": "📄 ИИ для документов",
        "business_automation": "🤖 Автоматизация бизнеса",
        "enterprise_rag": "📚 Корпоративный RAG",
        "site_app_generator": "🌐 Генератор сайтов и приложений",
        "intelligent_support": "🎧 Интеллектуальное Обслуживание и Поддержка",
        "data_bi_copilot": "📊 Помощник по Данным и BI",
        "quality_process_management": "✅ Управление Качеством и Процессами",
        "crm_sales_intelligence": "🤝 CRM и Клиентский Опыт",
        "erp_business_operations": "🏢 ERP и Бизнес-Операции",
        "supply_chain_procurement_logistics": "📦 Цепочка Поставок, Закупки и "
        "Логистика",
        "legal_compliance": "⚖️ Юридические Вопросы и Комплаенс",
        "api_integrations_connectors": "🔌 API, Интеграции и Коннекторы",
        "data_platform_governance": "🗄️ Платформа и Управление Данными",
        "cybersecurity_fraud_prevention": "🛡️ Кибербезопасность и "
        "Предотвращение Мошенничества",
        "cloud_devops_finops": "☁️ Cloud, DevOps и FinOps Copilot",
        "ai_operations": "⚙️ Операции и управление ИИ",
        "tools_analytics": "🛠️ Инструменты и аналитика",
        "pet_shops_veterinary_services": "🐾 Зоомагазины и Ветеринарные Услуги",
        "supermarkets_wholesale": "🛒 Супермаркеты и Оптовая Торговля",
        "retail_stores": "🏪 Магазины и Розничная Торговля",
        "dentistry": "🦷 Стоматология",
        "hospitals_clinics": "🏥 Больницы и Клиники",
        "administration": "🔐 Администрирование",
        "knowledge_graph_semantic_ai": "🧠 Граф знаний и семантический ИИ",
        "multimodal_ai": "🧬 Мультимодальный ИИ",
        "voice_audio_speech_ai": "🎙️ Голос, аудио и речевой ИИ",
        "agent_process_orchestration": "🧩 Оркестрация агентов и процессов",
        "ai_model_agent_security": "🤖 Безопасность ИИ, моделей и агентов",
        "real_time_event_intelligence": "⚡ Аналитика событий в реальном времени",
        "privacy_data_protection_lgpd": "🔐 Конфиденциальность, защита данных и LGPD",
        "zero_trust_identity_access": "🧱 Zero Trust, идентификация и "
        "управление доступом",
        "cryptography_confidential_computing": "🔏 Криптография и "
        "конфиденциальные вычисления",
        "software_supply_chain_security": "🧬 Безопасность цепочки поставок ПО",
        "privacy_enhancing_technologies": "🕵️ Технологии сохранения конфиденциальности",
        "geoai_earth_observation": "🛰️ GeoAI и наблюдение Земли",
        "gis_location_intelligence": "🗺️ GIS и геолокационная аналитика",
        "drones_aerial_intelligence": "🛸 Дроны и воздушная аналитика",
        "spatial_computing_augmented_reality": "🥽 Пространственные вычисления "
        "и дополненная реальность",
        "iot_edge_intelligence": "📡 IoT и периферийный интеллект",
        "computer_vision_video_analytics": "👁️ Компьютерное зрение и видеоаналитика",
        "digital_twins_simulation": "🏭 Цифровые двойники и моделирование",
        "robotics_autonomous_systems": "🤖 Робототехника и автономные системы",
        "scientific_computing_engineering": "🧮 Научные вычисления и инженерия",
        "simulation_optimization_operations_research": "🧪 Моделирование, "
        "оптимизация и "
        "исследование операций",
        "research_labs_assisted_discovery": "🔬 Исследования, лаборатории и "
        "поддерживаемые открытия",
        "materials_product_engineering": "🧱 Материалы и инженерия продуктов",
        "construction_bim_digital_engineering": "🏗️ Строительство, BIM и "
        "цифровая инженерия",
        "climate_meteorological_intelligence": "🌦️ Климатическая и "
        "метеорологическая аналитика",
        "environmental_natural_resources_intelligence": "🌊 Экологическая "
        "аналитика и "
        "природные ресурсы",
        "energy_smart_grids": "⚡ Энергетика и умные сети",
        "esg_sustainability": "🌱 ESG и устойчивое развитие",
        "emergency_disaster_management": "🧯 Реагирование на чрезвычайные "
        "ситуации и катастрофы",
        "mobility_traffic_transport": "🚦 Мобильность, трафик и транспорт",
        "smart_cities_urban_infrastructure": "🏙️ Умные города и городская "
        "инфраструктура",
        "networks_telecommunications_connectivity": "📶 Сети, телекоммуникации и связь",
        "navigation_positioning_geolocation": "🧭 Навигация, позиционирование "
        "и геолокация",
        "asset_management_smart_maintenance": "🔧 Управление активами и умное "
        "обслуживание",
        "ai_software_engineering": "🧑\u200d💻 Разработка программного "
        "обеспечения с ИИ",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 "
        "Сотрудничество, встречи и "
        "продуктивность с ИИ",
        "digital_experiences_intelligent_interfaces": "🎨 Цифровой опыт и "
        "интеллектуальные "
        "интерфейсы",
        "software_testing_quality_reliability": "🧪 Тестирование, качество и "
        "надежность ПО",
        "mobile_apps_omnichannel_experiences": "📱 Мобильные приложения и "
        "омниканальный опыт",
        "digital_identity_verifiable_credentials": "🪪 Цифровая идентичность и "
        "проверяемые учетные "
        "данные",
        "technology_governance_policy_compliance": "📜 Технологическое "
        "управление, политики и "
        "соответствие",
        "data_traceability_provenance": "📦 Прослеживаемость и происхождение данных",
        "enterprise_decision_intelligence": "🧠 Интеллект поддержки бизнес-решений",
        "operational_security_resilience": "🛡️ Операционная безопасность и устойчивость",
        "responsible_ai_ethics_risk": "⚖️ Ответственный ИИ, этика и оценка рисков",
        "ai_evaluation_benchmarks_red_team": "🧪 Оценка, бенчмарки и red team для ИИ",
        "model_explainability_interpretability": "🔍 Объяснимость и "
        "интерпретируемость моделей",
        "ai_bias_quality_monitoring": "📊 Мониторинг предвзятости и качества ИИ",
        "ai_certification_system_evidence": "✅ Сертификация и доказательства "
        "для систем ИИ",
        "mobility_transport_connected_vehicles": "🚚 Мобильность, транспорт и "
        "подключенные автомобили",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 Агробизнес, умное "
        "сельское хозяйство и "
        "биоэкономика",
    },
    "sa": {
        "financial_solutions": "💰 الحلول المالية",
        "hr_people_analytics": "👥 الموارد البشرية وتحليلات الأفراد",
        "document_ai": "📄 الذكاء الاصطناعي للمستندات",
        "business_automation": "🤖 أتمتة الأعمال",
        "enterprise_rag": "📚 نظام RAG للمؤسسات",
        "site_app_generator": "🌐 منشئ المواقع والتطبيقات",
        "intelligent_support": "🎧 خدمة ودعم ذكي",
        "data_bi_copilot": "📊 مساعد البيانات وذكاء الأعمال",
        "quality_process_management": "✅ إدارة الجودة والعمليات",
        "crm_sales_intelligence": "🤝 إدارة علاقات العملاء وتجربة العميل",
        "erp_business_operations": "🏢 تخطيط موارد المؤسسة وعمليات الأعمال",
        "supply_chain_procurement_logistics": "📦 سلسلة الإمداد والمشتريات "
        "والخدمات اللوجستية",
        "legal_compliance": "⚖️ الشؤون القانونية والامتثال",
        "api_integrations_connectors": "🔌 واجهات API والتكاملات والموصلات",
        "data_platform_governance": "🗄️ منصة البيانات وحوكمتها",
        "cybersecurity_fraud_prevention": "🛡️ الأمن السيبراني ومنع الاحتيال",
        "cloud_devops_finops": "☁️ مساعد السحابة وDevOps وFinOps",
        "ai_operations": "⚙️ عمليات وحوكمة الذكاء الاصطناعي",
        "tools_analytics": "🛠️ الأدوات والتحليلات",
        "pet_shops_veterinary_services": "🐾 متاجر الحيوانات والخدمات البيطرية",
        "supermarkets_wholesale": "🛒 المتاجر الكبرى وتجارة الجملة",
        "retail_stores": "🏪 المتاجر وتجارة التجزئة",
        "dentistry": "🦷 طب الأسنان",
        "hospitals_clinics": "🏥 المستشفيات والعيادات",
        "administration": "🔐 الإدارة",
        "knowledge_graph_semantic_ai": "🧠 الرسم البياني المعرفي والذكاء الدلالي",
        "multimodal_ai": "🧬 الذكاء الاصطناعي متعدد الوسائط",
        "voice_audio_speech_ai": "🎙️ الصوت والتسجيل والذكاء الاصطناعي للكلام",
        "agent_process_orchestration": "🧩 تنسيق الوكلاء والعمليات",
        "ai_model_agent_security": "🤖 أمن الذكاء الاصطناعي والنماذج والوكلاء",
        "real_time_event_intelligence": "⚡ ذكاء الأحداث في الوقت الفعلي",
        "privacy_data_protection_lgpd": "🔐 الخصوصية وحماية البيانات وقانون LGPD",
        "zero_trust_identity_access": "🧱 الثقة الصفرية وإدارة الهوية والوصول",
        "cryptography_confidential_computing": "🔏 التشفير والحوسبة السرية",
        "software_supply_chain_security": "🧬 أمن سلسلة توريد البرمجيات",
        "privacy_enhancing_technologies": "🕵️ تقنيات تعزيز الخصوصية",
        "geoai_earth_observation": "🛰️ الذكاء الجغرافي ومراقبة الأرض",
        "gis_location_intelligence": "🗺️ نظم المعلومات الجغرافية وذكاء الموقع",
        "drones_aerial_intelligence": "🛸 الطائرات المسيرة والذكاء الجوي",
        "spatial_computing_augmented_reality": "🥽 الحوسبة المكانية والواقع المعزز",
        "iot_edge_intelligence": "📡 إنترنت الأشياء وذكاء الحافة",
        "computer_vision_video_analytics": "👁️ الرؤية الحاسوبية وتحليلات الفيديو",
        "digital_twins_simulation": "🏭 التوائم الرقمية والمحاكاة",
        "robotics_autonomous_systems": "🤖 الروبوتات والأنظمة الذاتية",
        "scientific_computing_engineering": "🧮 الحوسبة العلمية والهندسة",
        "simulation_optimization_operations_research": "🧪 المحاكاة والتحسين "
        "وبحوث العمليات",
        "research_labs_assisted_discovery": "🔬 البحث والمختبرات والاكتشاف المساعد",
        "materials_product_engineering": "🧱 المواد وهندسة المنتجات",
        "construction_bim_digital_engineering": "🏗️ البناء ونمذجة معلومات "
        "المباني والهندسة الرقمية",
        "climate_meteorological_intelligence": "🌦️ الذكاء المناخي والأرصاد الجوية",
        "environmental_natural_resources_intelligence": "🌊 الذكاء البيئي "
        "والموارد الطبيعية",
        "energy_smart_grids": "⚡ الطاقة والشبكات الذكية",
        "esg_sustainability": "🌱 الحوكمة البيئية والاجتماعية والاستدامة",
        "emergency_disaster_management": "🧯 الاستجابة للطوارئ وإدارة الكوارث",
        "mobility_traffic_transport": "🚦 التنقل والمرور والنقل",
        "smart_cities_urban_infrastructure": "🏙️ المدن الذكية والبنية التحتية الحضرية",
        "networks_telecommunications_connectivity": "📶 الشبكات والاتصالات والربط",
        "navigation_positioning_geolocation": "🧭 الملاحة وتحديد المواقع "
        "والموقع الجغرافي",
        "asset_management_smart_maintenance": "🔧 إدارة الأصول والصيانة الذكية",
        "ai_software_engineering": "🧑\u200d💻 هندسة البرمجيات بمساعدة الذكاء "
        "الاصطناعي",
        "ai_collaboration_meetings_productivity": "🧑\u200d🤝\u200d🧑 التعاون "
        "والاجتماعات والإنتاجية "
        "بالذكاء الاصطناعي",
        "digital_experiences_intelligent_interfaces": "🎨 التجارب الرقمية "
        "والواجهات الذكية",
        "software_testing_quality_reliability": "🧪 اختبار البرمجيات والجودة "
        "والموثوقية",
        "mobile_apps_omnichannel_experiences": "📱 تطبيقات الهاتف وتجارب "
        "القنوات المتعددة",
        "digital_identity_verifiable_credentials": "🪪 الهوية الرقمية وبيانات "
        "الاعتماد القابلة للتحقق",
        "technology_governance_policy_compliance": "📜 حوكمة التكنولوجيا "
        "والسياسات والامتثال",
        "data_traceability_provenance": "📦 تتبع البيانات ومصدرها",
        "enterprise_decision_intelligence": "🧠 ذكاء اتخاذ القرار المؤسسي",
        "operational_security_resilience": "🛡️ الأمن التشغيلي والمرونة",
        "responsible_ai_ethics_risk": "⚖️ الذكاء الاصطناعي المسؤول والأخلاق "
        "وتقييم المخاطر",
        "ai_evaluation_benchmarks_red_team": "🧪 تقييم الذكاء الاصطناعي "
        "والمعايير والاختبارات الهجومية",
        "model_explainability_interpretability": "🔍 قابلية تفسير النماذج وشرحها",
        "ai_bias_quality_monitoring": "📊 مراقبة التحيز وجودة الذكاء الاصطناعي",
        "ai_certification_system_evidence": "✅ اعتماد أنظمة الذكاء الاصطناعي والأدلة",
        "mobility_transport_connected_vehicles": "🚚 التنقل والنقل والمركبات المتصلة",
        "agribusiness_smart_agriculture_bioeconomy": "🌾 الأعمال الزراعية "
        "والزراعة الذكية "
        "والاقتصاد الحيوي",
    },
}


PLATFORM_MODULE_TEXTS["en_gb"] = dict(PLATFORM_MODULE_TEXTS["en_us"])

PLATFORM_MODULE_TEXTS["ch"] = dict(PLATFORM_MODULE_TEXTS["de"])


PLATFORM_MODULE_STATUS_TEXTS: dict[
    str,
    dict[PlatformModuleStatus, str],
] = {
    "pt": {
        PlatformModuleStatus.ACTIVE: "Ativo",
        PlatformModuleStatus.INTEGRATING: ("Em integração"),
        PlatformModuleStatus.PLANNED: "Planejado",
        PlatformModuleStatus.DISABLED: "Desativado",
    },
    "en_us": {
        PlatformModuleStatus.ACTIVE: "Active",
        PlatformModuleStatus.INTEGRATING: ("Integrating"),
        PlatformModuleStatus.PLANNED: "Planned",
        PlatformModuleStatus.DISABLED: "Disabled",
    },
    "es": {
        PlatformModuleStatus.ACTIVE: "Activo",
        PlatformModuleStatus.INTEGRATING: ("En integración"),
        PlatformModuleStatus.PLANNED: "Planificado",
        PlatformModuleStatus.DISABLED: "Desactivado",
    },
    "fr": {
        PlatformModuleStatus.ACTIVE: "Actif",
        PlatformModuleStatus.INTEGRATING: ("En intégration"),
        PlatformModuleStatus.PLANNED: "Planifié",
        PlatformModuleStatus.DISABLED: "Désactivé",
    },
    "de": {
        PlatformModuleStatus.ACTIVE: "Aktiv",
        PlatformModuleStatus.INTEGRATING: ("In Integration"),
        PlatformModuleStatus.PLANNED: "Geplant",
        PlatformModuleStatus.DISABLED: "Deaktiviert",
    },
    "it": {
        PlatformModuleStatus.ACTIVE: "Attivo",
        PlatformModuleStatus.INTEGRATING: ("In integrazione"),
        PlatformModuleStatus.PLANNED: "Pianificato",
        PlatformModuleStatus.DISABLED: "Disattivato",
    },
    "ro": {
        PlatformModuleStatus.ACTIVE: "Activ",
        PlatformModuleStatus.INTEGRATING: ("În integrare"),
        PlatformModuleStatus.PLANNED: "Planificat",
        PlatformModuleStatus.DISABLED: "Dezactivat",
    },
    "ua": {
        PlatformModuleStatus.ACTIVE: "Активний",
        PlatformModuleStatus.INTEGRATING: ("Інтегрується"),
        PlatformModuleStatus.PLANNED: "Запланований",
        PlatformModuleStatus.DISABLED: "Вимкнений",
    },
    "ru": {
        PlatformModuleStatus.ACTIVE: "Активен",
        PlatformModuleStatus.INTEGRATING: ("Интегрируется"),
        PlatformModuleStatus.PLANNED: "Запланирован",
        PlatformModuleStatus.DISABLED: "Отключён",
    },
    "sa": {
        PlatformModuleStatus.ACTIVE: "نشط",
        PlatformModuleStatus.INTEGRATING: ("قيد التكامل"),
        PlatformModuleStatus.PLANNED: "مخطط",
        PlatformModuleStatus.DISABLED: "معطل",
    },
}


PLATFORM_MODULE_STATUS_TEXTS["en_gb"] = dict(PLATFORM_MODULE_STATUS_TEXTS["en_us"])

PLATFORM_MODULE_STATUS_TEXTS["ch"] = dict(PLATFORM_MODULE_STATUS_TEXTS["de"])


# Nomes atualizados dos módulos de criação e suporte.
_PLATFORM_CREATION_AND_SUPPORT_TEXTS = {
    "pt": {
        "site_app_generator": ("🌐 Gerador de Sites, Apps e Dashboards"),
        "intelligent_support": ("🎧 Atendimento e Suporte Inteligente"),
    },
    "en_us": {
        "site_app_generator": ("🌐 Site, App and Dashboard Generator"),
        "intelligent_support": ("🎧 Intelligent Customer Support"),
    },
    "es": {
        "site_app_generator": ("🌐 Generador de Sitios, Apps y Paneles"),
        "intelligent_support": ("🎧 Atención y Soporte Inteligente"),
    },
    "fr": {
        "site_app_generator": (
            "🌐 Générateur de Sites, Applications et Tableaux de Bord"
        ),
        "intelligent_support": ("🎧 Assistance et Support Intelligents"),
    },
    "de": {
        "site_app_generator": ("🌐 Website-, App- und Dashboard-Generator"),
        "intelligent_support": ("🎧 Intelligenter Kundenservice"),
    },
    "it": {
        "site_app_generator": ("🌐 Generatore di Siti, App e Dashboard"),
        "intelligent_support": ("🎧 Assistenza e Supporto Intelligente"),
    },
    "ro": {
        "site_app_generator": (
            "🌐 Generator de Site-uri, Aplicații și Panouri de Control"
        ),
        "intelligent_support": ("🎧 Asistență și Suport Inteligent"),
    },
    "ua": {
        "site_app_generator": ("🌐 Генератор Сайтів, Застосунків і Панелей Керування"),
        "intelligent_support": ("🎧 Інтелектуальна Підтримка Клієнтів"),
    },
    "ru": {
        "site_app_generator": ("🌐 Генератор Сайтов, Приложений и Панелей Управления"),
        "intelligent_support": ("🎧 Интеллектуальная Поддержка Клиентов"),
    },
    "sa": {
        "site_app_generator": ("🌐 منشئ المواقع والتطبيقات ولوحات المعلومات"),
        "intelligent_support": ("🎧 خدمة ودعم العملاء الذكي"),
    },
}


for _language, _texts in _PLATFORM_CREATION_AND_SUPPORT_TEXTS.items():
    PLATFORM_MODULE_TEXTS[_language].update(_texts)


PLATFORM_MODULE_TEXTS["en_gb"] = dict(PLATFORM_MODULE_TEXTS["en_us"])

PLATFORM_MODULE_TEXTS["ch"] = dict(PLATFORM_MODULE_TEXTS["de"])


_PLATFORM_ENTERPRISE_EXPANSION_TEXTS = {
    "pt": {
        "data_bi_copilot": "📊 Data & BI Copilot",
        "quality_process_management": ("✅ Gestão da Qualidade e Processos"),
        "crm_sales_intelligence": ("🤝 CRM e Experiência do Cliente"),
        "legal_compliance": ("⚖️ Jurídico e Compliance"),
        "cybersecurity_fraud_prevention": ("🛡️ Cibersegurança e Prevenção a Fraudes"),
    },
    "en_us": {
        "data_bi_copilot": "📊 Data & BI Copilot",
        "quality_process_management": ("✅ Quality and Process Management"),
        "crm_sales_intelligence": ("📈 CRM and Sales Intelligence"),
        "legal_compliance": ("⚖️ Legal and Compliance"),
        "cybersecurity_fraud_prevention": ("🛡️ Cybersecurity and Fraud Prevention"),
    },
    "es": {
        "data_bi_copilot": "📊 Copiloto de Datos y BI",
        "quality_process_management": ("✅ Gestión de Calidad y Procesos"),
        "crm_sales_intelligence": ("📈 CRM e Inteligencia Comercial"),
        "legal_compliance": ("⚖️ Área Jurídica y Cumplimiento"),
        "cybersecurity_fraud_prevention": ("🛡️ Ciberseguridad y Prevención del Fraude"),
    },
    "fr": {
        "data_bi_copilot": "📊 Copilote Données et BI",
        "quality_process_management": ("✅ Gestion de la Qualité et des Processus"),
        "crm_sales_intelligence": ("📈 CRM et Intelligence Commerciale"),
        "legal_compliance": ("⚖️ Juridique et Conformité"),
        "cybersecurity_fraud_prevention": ("🛡️ Cybersécurité et Prévention des Fraudes"),
    },
    "de": {
        "data_bi_copilot": "📊 Daten- und BI-Copilot",
        "quality_process_management": ("✅ Qualitäts- und Prozessmanagement"),
        "crm_sales_intelligence": ("📈 CRM und Vertriebsanalyse"),
        "legal_compliance": ("⚖️ Recht und Compliance"),
        "cybersecurity_fraud_prevention": ("🛡️ Cybersicherheit und Betrugsprävention"),
    },
    "it": {
        "data_bi_copilot": "📊 Copilota Dati e BI",
        "quality_process_management": ("✅ Gestione della Qualità e dei Processi"),
        "crm_sales_intelligence": ("📈 CRM e Intelligence Commerciale"),
        "legal_compliance": ("⚖️ Area Legale e Conformità"),
        "cybersecurity_fraud_prevention": (
            "🛡️ Cybersicurezza e Prevenzione delle Frodi"
        ),
    },
    "ro": {
        "data_bi_copilot": "📊 Copilot pentru Date și BI",
        "quality_process_management": ("✅ Managementul Calității și Proceselor"),
        "crm_sales_intelligence": ("📈 CRM și Inteligență Comercială"),
        "legal_compliance": ("⚖️ Juridic și Conformitate"),
        "cybersecurity_fraud_prevention": (
            "🛡️ Securitate Cibernetică și Prevenirea Fraudelor"
        ),
    },
    "ua": {
        "data_bi_copilot": "📊 Помічник із Даних та BI",
        "quality_process_management": ("✅ Управління Якістю та Процесами"),
        "crm_sales_intelligence": ("📈 CRM і Комерційна Аналітика"),
        "legal_compliance": ("⚖️ Юридичний Супровід і Відповідність"),
        "cybersecurity_fraud_prevention": ("🛡️ Кібербезпека та Запобігання Шахрайству"),
    },
    "ru": {
        "data_bi_copilot": "📊 Помощник по Данным и BI",
        "quality_process_management": ("✅ Управление Качеством и Процессами"),
        "crm_sales_intelligence": ("📈 CRM и Коммерческая Аналитика"),
        "legal_compliance": ("⚖️ Юридическое Сопровождение и Комплаенс"),
        "cybersecurity_fraud_prevention": (
            "🛡️ Кибербезопасность и Предотвращение Мошенничества"
        ),
    },
    "sa": {
        "data_bi_copilot": ("📊 مساعد البيانات وذكاء الأعمال"),
        "quality_process_management": ("✅ إدارة الجودة والعمليات"),
        "crm_sales_intelligence": ("📈 إدارة العملاء والذكاء التجاري"),
        "legal_compliance": ("⚖️ الشؤون القانونية والامتثال"),
        "cybersecurity_fraud_prevention": ("🛡️ الأمن السيبراني ومنع الاحتيال"),
    },
}


for _language, _texts in _PLATFORM_ENTERPRISE_EXPANSION_TEXTS.items():
    PLATFORM_MODULE_TEXTS[_language].update(_texts)


PLATFORM_MODULE_TEXTS["en_gb"] = dict(PLATFORM_MODULE_TEXTS["en_us"])

PLATFORM_MODULE_TEXTS["ch"] = dict(PLATFORM_MODULE_TEXTS["de"])


TECHNOLOGY_FAMILY_TEXTS: dict[
    str,
    dict[TechnologyFamily, str],
] = {
    "pt": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 IA, conhecimento e agentes"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Dados, integração e operações"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Segurança, privacidade e confiança digital"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Tecnologias geoespaciais e observação"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Mundo físico, automação e simulação"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Engenharia, ciência e otimização"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: ("🌦️ Clima, ambiente e energia"),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Mobilidade e infraestrutura conectada"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Software, produtividade e experiência digital"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Confiança, identidade e governança digital"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ Avaliação, qualidade e confiança em IA"
        ),
    },
    "en_us": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 AI, Knowledge and Agents"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Data, Integration and Operations"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Security, Privacy and Digital Trust"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Geospatial Technologies and Observation"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Physical World, Automation and Simulation"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Engineering, Science and Optimization"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: (
            "🌦️ Climate, Environment and Energy"
        ),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Mobility and Connected Infrastructure"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Software, Productivity and Digital Experience"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Trust, Identity and Digital Governance"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: ("⚖️ AI Evaluation, Quality and Trust"),
    },
    "es": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 IA, conocimiento y agentes"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Datos, integración y operaciones"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Seguridad, privacidad y confianza digital"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Tecnologías geoespaciales y observación"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Mundo físico, automatización y simulación"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Ingeniería, ciencia y optimización"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: (
            "🌦️ Clima, medio ambiente y energía"
        ),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Movilidad e infraestructura conectada"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Software, productividad y experiencia digital"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Confianza, identidad y gobernanza digital"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ Evaluación, calidad y confianza en IA"
        ),
    },
    "fr": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 IA, connaissances et agents"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Données, intégration et opérations"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Sécurité, confidentialité et confiance numérique"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Technologies géospatiales et observation"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Monde physique, automatisation et simulation"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Ingénierie, science et optimisation"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: (
            "🌦️ Climat, environnement et énergie"
        ),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Mobilité et infrastructure connectée"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Logiciels, productivité et expérience numérique"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Confiance, identité et gouvernance numériques"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ Évaluation, qualité et confiance en IA"
        ),
    },
    "de": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 KI, Wissen und Agenten"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Daten, Integration und Betrieb"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Sicherheit, Datenschutz und digitales Vertrauen"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Geospatiale Technologien und Beobachtung"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Physische Welt, Automatisierung und Simulation"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Ingenieurwesen, Wissenschaft und Optimierung"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: ("🌦️ Klima, Umwelt und Energie"),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Mobilität und vernetzte Infrastruktur"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Software, Produktivität und digitale Erfahrung"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Vertrauen, Identität und digitale Governance"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ Bewertung, Qualität und Vertrauen in KI"
        ),
    },
    "it": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 IA, conoscenza e agenti"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Dati, integrazione e operazioni"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Sicurezza, privacy e fiducia digitale"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Tecnologie geospaziali e osservazione"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Mondo fisico, automazione e simulazione"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Ingegneria, scienza e ottimizzazione"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: ("🌦️ Clima, ambiente ed energia"),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Mobilità e infrastrutture connesse"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Software, produttività ed esperienza digitale"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Fiducia, identità e governance digitale"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ Valutazione, qualità e fiducia nell'IA"
        ),
    },
    "ro": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 IA, cunoaștere și agenți"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Date, integrare și operațiuni"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Securitate, confidențialitate și încredere digitală"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Tehnologii geospațiale și observare"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Lume fizică, automatizare și simulare"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Inginerie, știință și optimizare"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: ("🌦️ Climă, mediu și energie"),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Mobilitate și infrastructură conectată"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Software, productivitate și experiență digitală"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Încredere, identitate și guvernanță digitală"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ Evaluare, calitate și încredere în IA"
        ),
    },
    "ua": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 ШІ, знання та агенти"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Дані, інтеграція та операції"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Безпека, приватність і цифрова довіра"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Геопросторові технології та спостереження"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Фізичний світ, автоматизація та моделювання"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Інженерія, наука та оптимізація"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: (
            "🌦️ Клімат, довкілля та енергетика"
        ),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Мобільність і підключена інфраструктура"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 Програмне забезпечення, продуктивність і цифровий досвід"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Довіра, ідентичність і цифрове врядування"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: ("⚖️ Оцінювання, якість і довіра до ШІ"),
    },
    "ru": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 ИИ, знания и агенты"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: (
            "🗄️ Данные, интеграция и операции"
        ),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: (
            "🔐 Безопасность, конфиденциальность и цифровое доверие"
        ),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ Геопространственные технологии и наблюдение"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 Физический мир, автоматизация и моделирование"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 Инженерия, наука и оптимизация"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: (
            "🌦️ Климат, окружающая среда и энергетика"
        ),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 Мобильность и подключенная инфраструктура"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 ПО, продуктивность и цифровой опыт"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 Доверие, идентичность и цифровое управление"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: ("⚖️ Оценка, качество и доверие к ИИ"),
    },
    "sa": {
        TechnologyFamily.AI_KNOWLEDGE_AGENTS: ("🧠 الذكاء الاصطناعي والمعرفة والوكلاء"),
        TechnologyFamily.DATA_INTEGRATION_OPERATIONS: ("🗄️ البيانات والتكامل والعمليات"),
        TechnologyFamily.SECURITY_PRIVACY_TRUST: ("🔐 الأمن والخصوصية والثقة الرقمية"),
        TechnologyFamily.GEOSPATIAL_OBSERVATION: (
            "🛰️ التقنيات الجغرافية المكانية والرصد"
        ),
        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION: (
            "🏭 العالم المادي والأتمتة والمحاكاة"
        ),
        TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION: (
            "🧮 الهندسة والعلوم والتحسين"
        ),
        TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY: ("🌦️ المناخ والبيئة والطاقة"),
        TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE: (
            "🚦 التنقل والبنية التحتية المتصلة"
        ),
        TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE: (
            "🧑‍💻 البرمجيات والإنتاجية والتجربة الرقمية"
        ),
        TechnologyFamily.DIGITAL_TRUST_GOVERNANCE: (
            "🪪 الثقة والهوية والحوكمة الرقمية"
        ),
        TechnologyFamily.AI_EVALUATION_TRUST: (
            "⚖️ تقييم الذكاء الاصطناعي والجودة والثقة"
        ),
    },
}

TECHNOLOGY_FAMILY_TEXTS["en_gb"] = dict(TECHNOLOGY_FAMILY_TEXTS["en_us"])
TECHNOLOGY_FAMILY_TEXTS["ch"] = dict(TECHNOLOGY_FAMILY_TEXTS["de"])

PLATFORM_MODULE_CATEGORY_TEXTS: dict[
    str,
    dict[PlatformModuleCategory, str],
] = {
    "pt": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Soluções de negócio"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Núcleo tecnológico"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("Administração da plataforma"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Soluções por setor"),
    },
    "en_us": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Business solutions"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Technology core"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("Platform administration"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Industry solutions"),
    },
    "es": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Soluciones de negocio"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Núcleo tecnológico"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: (
            "Administración de la plataforma"
        ),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Soluciones por sector"),
    },
    "fr": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Solutions métier"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Noyau technologique"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: (
            "Administration de la plateforme"
        ),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Solutions sectorielles"),
    },
    "de": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Geschäftslösungen"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Technologiekern"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("Plattformverwaltung"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Branchenlösungen"),
    },
    "it": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Soluzioni aziendali"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Nucleo tecnologico"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: (
            "Amministrazione della piattaforma"
        ),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Soluzioni settoriali"),
    },
    "ro": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Soluții de afaceri"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Nucleu tehnologic"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("Administrarea platformei"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Soluții sectoriale"),
    },
    "ua": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Бізнес-рішення"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Технологічне ядро"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("Адміністрування платформи"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Галузеві рішення"),
    },
    "ru": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("Бизнес-решения"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("Технологическое ядро"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("Администрирование платформы"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("Отраслевые решения"),
    },
    "sa": {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: ("حلول الأعمال"),
        PlatformModuleCategory.TECHNOLOGY_CORE: ("النواة التقنية"),
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: ("إدارة المنصة"),
        PlatformModuleCategory.SECTOR_SOLUTIONS: ("حلول القطاعات"),
    },
}


PLATFORM_MODULE_CATEGORY_TEXTS["en_gb"] = dict(PLATFORM_MODULE_CATEGORY_TEXTS["en_us"])

PLATFORM_MODULE_CATEGORY_TEXTS["ch"] = dict(PLATFORM_MODULE_CATEGORY_TEXTS["de"])


PLATFORM_INTEGRATION_TYPE_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "internal": "Interna",
        "api": "API",
        "hybrid": "Híbrida",
        "webhook": "Webhook",
    },
    "en_us": {
        "internal": "Internal",
        "api": "API",
        "hybrid": "Hybrid",
        "webhook": "Webhook",
    },
    "es": {
        "internal": "Interna",
        "api": "API",
        "hybrid": "Híbrida",
        "webhook": "Webhook",
    },
    "fr": {
        "internal": "Interne",
        "api": "API",
        "hybrid": "Hybride",
        "webhook": "Webhook",
    },
    "de": {
        "internal": "Intern",
        "api": "API",
        "hybrid": "Hybrid",
        "webhook": "Webhook",
    },
    "it": {
        "internal": "Interna",
        "api": "API",
        "hybrid": "Ibrida",
        "webhook": "Webhook",
    },
    "ro": {
        "internal": "Internă",
        "api": "API",
        "hybrid": "Hibridă",
        "webhook": "Webhook",
    },
    "ua": {
        "internal": "Внутрішня",
        "api": "API",
        "hybrid": "Гібридна",
        "webhook": "Webhook",
    },
    "ru": {
        "internal": "Внутренняя",
        "api": "API",
        "hybrid": "Гибридная",
        "webhook": "Webhook",
    },
    "sa": {
        "internal": "داخلي",
        "api": "واجهة API",
        "hybrid": "هجين",
        "webhook": "Webhook",
    },
}


PLATFORM_INTEGRATION_TYPE_TEXTS["en_gb"] = dict(
    PLATFORM_INTEGRATION_TYPE_TEXTS["en_us"]
)

PLATFORM_INTEGRATION_TYPE_TEXTS["ch"] = dict(PLATFORM_INTEGRATION_TYPE_TEXTS["de"])


def technology_family_t(
    family: TechnologyFamily,
    language: str = "pt",
) -> str:
    """Traduz uma família do núcleo tecnológico."""

    selected_language = language if language in TECHNOLOGY_FAMILY_TEXTS else "pt"

    return TECHNOLOGY_FAMILY_TEXTS[selected_language].get(
        family,
        family.value,
    )


def platform_module_category_t(
    category: PlatformModuleCategory,
    language: str = "pt",
) -> str:
    """Traduz a categoria de um módulo."""

    selected_language = language if language in PLATFORM_MODULE_CATEGORY_TEXTS else "pt"

    return PLATFORM_MODULE_CATEGORY_TEXTS[selected_language].get(
        category,
        category.value,
    )


def platform_integration_type_t(
    integration_type: str,
    language: str = "pt",
) -> str:
    """Traduz o tipo de integração."""

    selected_language = (
        language if language in PLATFORM_INTEGRATION_TYPE_TEXTS else "pt"
    )

    return PLATFORM_INTEGRATION_TYPE_TEXTS[selected_language].get(
        integration_type,
        integration_type,
    )


def validate_platform_module_metadata_translations() -> None:
    """Valida categorias e tipos de integração."""

    expected_categories = set(PlatformModuleCategory)

    expected_integrations = {
        "internal",
        "api",
        "hybrid",
        "webhook",
    }

    for language, texts in PLATFORM_MODULE_CATEGORY_TEXTS.items():
        if set(texts) != expected_categories:
            raise ValueError(f"Contrato inválido de categorias: {language}")

        if not all(
            isinstance(value, str) and value.strip() for value in texts.values()
        ):
            raise ValueError(f"Categoria sem tradução válida: {language}")

    for language, texts in PLATFORM_INTEGRATION_TYPE_TEXTS.items():
        if set(texts) != expected_integrations:
            raise ValueError(f"Contrato inválido de integrações: {language}")

        if not all(
            isinstance(value, str) and value.strip() for value in texts.values()
        ):
            raise ValueError(f"Integração sem tradução válida: {language}")


def platform_module_t(
    module_id: str,
    language: str = "pt",
) -> str:
    """Traduz o nome de um módulo."""

    selected_language = language if language in PLATFORM_MODULE_TEXTS else "pt"

    return PLATFORM_MODULE_TEXTS[selected_language].get(
        module_id,
        PLATFORM_MODULE_TEXTS["pt"].get(
            module_id,
            module_id,
        ),
    )


def platform_module_status_t(
    status: PlatformModuleStatus,
    language: str = "pt",
) -> str:
    """Traduz o estado de um módulo."""

    selected_language = language if language in PLATFORM_MODULE_STATUS_TEXTS else "pt"

    return PLATFORM_MODULE_STATUS_TEXTS[selected_language].get(
        status,
        status.value,
    )


def validate_platform_module_translations() -> None:
    """Valida cobertura e integridade dos catálogos."""

    expected_module_ids = {module.module_id for module in PLATFORM_MODULES}

    expected_statuses = set(PlatformModuleStatus)

    for language, texts in PLATFORM_MODULE_TEXTS.items():
        if set(texts) != expected_module_ids:
            raise ValueError(f"Contrato inválido de módulos: {language}")

        if not all(
            isinstance(value, str) and value.strip() for value in texts.values()
        ):
            raise ValueError(f"Tradução inválida de módulo: {language}")

    for language, texts in PLATFORM_MODULE_STATUS_TEXTS.items():
        if set(texts) != expected_statuses:
            raise ValueError(f"Contrato inválido de estados: {language}")

        if not all(
            isinstance(value, str) and value.strip() for value in texts.values()
        ):
            raise ValueError(f"Tradução inválida de estado: {language}")


validate_platform_module_translations()
validate_platform_module_metadata_translations()
