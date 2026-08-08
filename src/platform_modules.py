"""
Registro central dos módulos da INNA AI Platform.

O registro separa módulos ativos, em integração e planejados,
evitando páginas vazias e configurações espalhadas pelo projeto.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PlatformModuleStatus(StrEnum):
    """Estados possíveis de um módulo da plataforma."""

    ACTIVE = "active"
    INTEGRATING = "integrating"
    PLANNED = "planned"
    DISABLED = "disabled"


class PlatformModuleCategory(StrEnum):
    """Categorias principais do catálogo de módulos."""

    BUSINESS_SOLUTIONS = "business_solutions"
    TECHNOLOGY_CORE = "technology_core"
    SECTOR_SOLUTIONS = "sector_solutions"
    PLATFORM_ADMINISTRATION = "platform_administration"


class TechnologyFamily(StrEnum):
    """Famílias internas do núcleo tecnológico."""

    AI_KNOWLEDGE_AGENTS = "ai_knowledge_agents"
    DATA_INTEGRATION_OPERATIONS = "data_integration_operations"
    SECURITY_PRIVACY_TRUST = "security_privacy_trust"
    GEOSPATIAL_OBSERVATION = "geospatial_observation"
    PHYSICAL_AUTOMATION_SIMULATION = "physical_automation_simulation"
    ENGINEERING_SCIENCE_OPTIMIZATION = "engineering_science_optimization"
    CLIMATE_ENVIRONMENT_ENERGY = "climate_environment_energy"
    MOBILITY_CONNECTED_INFRASTRUCTURE = "mobility_connected_infrastructure"
    SOFTWARE_PRODUCTIVITY_EXPERIENCE = "software_productivity_experience"
    DIGITAL_TRUST_GOVERNANCE = "digital_trust_governance"
    AI_EVALUATION_TRUST = "ai_evaluation_trust"


@dataclass(frozen=True, slots=True)
class PlatformModule:
    """Representa um módulo principal da INNA."""

    module_id: str
    icon: str
    category: PlatformModuleCategory
    status: PlatformModuleStatus
    navigation_group_id: str | None
    integration_type: str
    description: str
    technology_family: TechnologyFamily | None = None

    @property
    def is_available(self) -> bool:
        """Indica se o módulo pode aparecer como funcional."""

        return self.status is PlatformModuleStatus.ACTIVE

    @property
    def is_external_integration(self) -> bool:
        """Indica se o módulo será conectado por integração."""

        return self.integration_type in {
            "api",
            "webhook",
            "hybrid",
        }


PLATFORM_MODULES: tuple[PlatformModule, ...] = (
    PlatformModule(
        module_id="financial_solutions",
        icon="💰",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.ACTIVE,
        navigation_group_id="financial_solutions",
        integration_type="internal",
        description=(
            "Educação financeira, segurança financeira, "
            "diagnósticos, planejamento, orçamento, "
            "dívidas e orientação financeira inteligente."
        ),
    ),
    PlatformModule(
        module_id="hr_people_analytics",
        icon="👥",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.INTEGRATING,
        navigation_group_id=None,
        integration_type="api",
        description=(
            "RH e People Analytics com ATS, recrutamento, "
            "entrevistas, onboarding, desempenho, clima, "
            "treinamentos, turnover e absenteísmo."
        ),
    ),
    PlatformModule(
        module_id="document_ai",
        icon="📄",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Extração, classificação, validação e análise inteligente de documentos."
        ),
    ),
    PlatformModule(
        module_id="business_automation",
        icon="🤖",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Automação empresarial com n8n, RPA, agentes e aprovações humanas."
        ),
    ),
    PlatformModule(
        module_id="enterprise_rag",
        technology_family=(TechnologyFamily.AI_KNOWLEDGE_AGENTS),
        icon="📚",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.ACTIVE,
        navigation_group_id="enterprise_rag",
        integration_type="internal",
        description=(
            "Bases de conhecimento, recuperação, observabilidade e avaliação RAG."
        ),
    ),
    PlatformModule(
        module_id="site_app_generator",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        icon="🌐",
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description=(
            "Geração assistida de sites, aplicativos, dashboards, formulários e APIs."
        ),
    ),
    PlatformModule(
        module_id="intelligent_support",
        icon="🎧",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Atendimento e suporte inteligente com "
            "chamados, SLA, múltiplos canais, RAG "
            "e encaminhamento para atendimento humano."
        ),
    ),
    PlatformModule(
        module_id="data_bi_copilot",
        icon="📊",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Análise de dados, geração de SQL, KPIs, "
            "relatórios, previsões e dashboards."
        ),
    ),
    PlatformModule(
        module_id="quality_process_management",
        icon="✅",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Gestão da qualidade, auditorias, não "
            "conformidades, PDCA, 5W2H e planos de ação."
        ),
    ),
    PlatformModule(
        module_id="crm_sales_intelligence",
        icon="🤝",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "CRM, leads, oportunidades, campanhas, "
            "Customer 360, propostas, contratos, "
            "pós-venda e previsão comercial."
        ),
    ),
    PlatformModule(
        module_id="erp_business_operations",
        icon="🏢",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Finanças, contabilidade, contas a pagar e "
            "receber, faturamento, compras, estoque, "
            "ativos e operações empresariais."
        ),
    ),
    PlatformModule(
        module_id="supply_chain_procurement_logistics",
        icon="📦",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Fornecedores, cotações, requisições, "
            "armazéns, previsão de demanda, transporte, "
            "entregas e custos logísticos."
        ),
    ),
    PlatformModule(
        module_id="legal_compliance",
        icon="⚖️",
        category=PlatformModuleCategory.BUSINESS_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Análise de contratos, políticas, LGPD, riscos jurídicos e conformidade."
        ),
    ),
    PlatformModule(
        module_id="api_integrations_connectors",
        technology_family=(TechnologyFamily.DATA_INTEGRATION_OPERATIONS),
        icon="🔌",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "APIs, webhooks, conectores, gateway, "
            "autenticação, filas, eventos e integração "
            "com sistemas CRM, ERP e serviços externos."
        ),
    ),
    PlatformModule(
        module_id="data_platform_governance",
        technology_family=(TechnologyFamily.DATA_INTEGRATION_OPERATIONS),
        icon="🗄️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Data Lake, Lakehouse, ETL, ELT, catálogo, "
            "linhagem, qualidade, dados mestres, acesso, "
            "retenção e preparação para BI, RAG e IA."
        ),
    ),
    PlatformModule(
        module_id="cybersecurity_fraud_prevention",
        technology_family=(TechnologyFamily.SECURITY_PRIVACY_TRUST),
        icon="🛡️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Prevenção a fraudes, golpes, phishing, incidentes e riscos de segurança."
        ),
    ),
    PlatformModule(
        module_id="cloud_devops_finops",
        technology_family=(TechnologyFamily.DATA_INTEGRATION_OPERATIONS),
        icon="☁️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Infraestrutura em nuvem, CI/CD, deploy, "
            "observabilidade, disponibilidade, custos, "
            "FinOps e otimização de recursos."
        ),
    ),
    PlatformModule(
        module_id="ai_operations",
        technology_family=(TechnologyFamily.DATA_INTEGRATION_OPERATIONS),
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        icon="⚙️",
        status=PlatformModuleStatus.ACTIVE,
        navigation_group_id="ai_operations",
        integration_type="internal",
        description=(
            "LLMOps, custos, saúde, timeline e governança de inteligência artificial."
        ),
    ),
    PlatformModule(
        module_id="tools_analytics",
        technology_family=(TechnologyFamily.DATA_INTEGRATION_OPERATIONS),
        icon="🛠️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.ACTIVE,
        navigation_group_id="tools_analytics",
        integration_type="internal",
        description=(
            "Observabilidade, análise e monitoramento das ferramentas da INNA."
        ),
    ),
    PlatformModule(
        module_id="knowledge_graph_semantic_ai",
        icon="🧠",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Grafos de conhecimento, ontologias, relações semânticas, "
            "entidades e raciocínio contextual para integrar dados e conhecimento empresarial."
        ),
        technology_family=(TechnologyFamily.AI_KNOWLEDGE_AGENTS),
    ),
    PlatformModule(
        module_id="multimodal_ai",
        icon="🧬",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Processamento integrado de texto, imagens, áudio, vídeo, "
            "documentos e outros formatos por modelos de inteligência artificial."
        ),
        technology_family=(TechnologyFamily.AI_KNOWLEDGE_AGENTS),
    ),
    PlatformModule(
        module_id="voice_audio_speech_ai",
        icon="🎙️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="api",
        description=(
            "Reconhecimento de voz, síntese de fala, transcrição, "
            "análise de áudio, "
            "identificação de intenção e interfaces conversacionais."
        ),
        technology_family=(TechnologyFamily.AI_KNOWLEDGE_AGENTS),
    ),
    PlatformModule(
        module_id="agent_process_orchestration",
        icon="🧩",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description=(
            "Orquestração de agentes, ferramentas, fluxos, "
            "processos empresariais, aprovações humanas, "
            "memória e execução coordenada de tarefas."
        ),
        technology_family=(TechnologyFamily.AI_KNOWLEDGE_AGENTS),
    ),
    PlatformModule(
        module_id="ai_model_agent_security",
        icon="🤖",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Proteção de modelos, agentes, ferramentas, prompts, "
            "contexto, bases RAG e permissões contra ataques, "
            "abusos e vazamentos."
        ),
        technology_family=(TechnologyFamily.AI_KNOWLEDGE_AGENTS),
    ),
    PlatformModule(
        module_id="real_time_event_intelligence",
        icon="⚡",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Processamento de eventos, streams, filas, "
            "telemetria e alertas em tempo real para decisões e automações operacionais."
        ),
        technology_family=(TechnologyFamily.DATA_INTEGRATION_OPERATIONS),
    ),
    PlatformModule(
        module_id="privacy_data_protection_lgpd",
        icon="🔐",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Inventário de dados pessoais, consentimento, retenção, "
            "anonimização, "
            "solicitações de titulares e apoio à conformidade com a LGPD."
        ),
        technology_family=(TechnologyFamily.SECURITY_PRIVACY_TRUST),
    ),
    PlatformModule(
        module_id="zero_trust_identity_access",
        icon="🧱",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Zero Trust, IAM, autenticação multifator, SSO, "
            "controle de acesso, "
            "privilégios mínimos e identidades de usuários e serviços."
        ),
        technology_family=(TechnologyFamily.SECURITY_PRIVACY_TRUST),
    ),
    PlatformModule(
        module_id="cryptography_confidential_computing",
        icon="🔏",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Criptografia de dados, gestão de chaves, segredos, "
            "assinaturas, "
            "ambientes confidenciais e proteção durante o processamento."
        ),
        technology_family=(TechnologyFamily.SECURITY_PRIVACY_TRUST),
    ),
    PlatformModule(
        module_id="software_supply_chain_security",
        icon="🧬",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Proteção da cadeia de software, dependências, SBOM, "
            "imagens de contêiner, artefatos, "
            "pipelines CI/CD e componentes de terceiros."
        ),
        technology_family=(TechnologyFamily.SECURITY_PRIVACY_TRUST),
    ),
    PlatformModule(
        module_id="privacy_enhancing_technologies",
        icon="🕵️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Tecnologias de preservação de privacidade, "
            "dados sintéticos, aprendizado federado, "
            "privacidade diferencial e computação segura."
        ),
        technology_family=(TechnologyFamily.SECURITY_PRIVACY_TRUST),
    ),
    PlatformModule(
        module_id="geoai_earth_observation",
        icon="🛰️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="api",
        description=(
            "Imagens de satélite, sensoriamento remoto, "
            "análise geoespacial, "
            "detecção de mudanças e inteligência territorial apoiada por IA."
        ),
        technology_family=(TechnologyFamily.GEOSPATIAL_OBSERVATION),
    ),
    PlatformModule(
        module_id="gis_location_intelligence",
        icon="🗺️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="api",
        description=(
            "Mapas, geocodificação, roteamento, consultas espaciais, "
            "territórios, "
            "camadas geográficas e inteligência baseada em localização."
        ),
        technology_family=(TechnologyFamily.GEOSPATIAL_OBSERVATION),
    ),
    PlatformModule(
        module_id="drones_aerial_intelligence",
        icon="🛸",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="api",
        description=(
            "Integração de drones, imagens aéreas, missões, inspeções, "
            "mapeamento, "
            "monitoramento territorial e análise automatizada de dados capturados."
        ),
        technology_family=(TechnologyFamily.GEOSPATIAL_OBSERVATION),
    ),
    PlatformModule(
        module_id="spatial_computing_augmented_reality",
        icon="🥽",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Computação espacial, realidade aumentada, "
            "visualização imersiva, "
            "sobreposição de dados e experiências digitais vinculadas ao espaço."
        ),
        technology_family=(TechnologyFamily.GEOSPATIAL_OBSERVATION),
    ),
    PlatformModule(
        module_id="iot_edge_intelligence",
        icon="📡",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Sensores, dispositivos conectados, telemetria, "
            "protocolos IoT, "
            "processamento de borda e decisões próximas aos equipamentos físicos."
        ),
        technology_family=(TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION),
    ),
    PlatformModule(
        module_id="computer_vision_video_analytics",
        icon="👁️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Análise de imagens e vídeos, detecção, classificação, "
            "rastreamento, "
            "inspeção visual e monitoramento inteligente em tempo real."
        ),
        technology_family=(TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION),
    ),
    PlatformModule(
        module_id="digital_twins_simulation",
        icon="🏭",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Representações digitais de ativos, "
            "ambientes e processos para simulação, monitoramento, "
            "previsão e otimização operacional."
        ),
        technology_family=(TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION),
    ),
    PlatformModule(
        module_id="robotics_autonomous_systems",
        icon="🤖",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Robôs, máquinas autônomas, planejamento de tarefas, "
            "percepção, controle, "
            "integração com sensores e supervisão humana."
        ),
        technology_family=(TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION),
    ),
    PlatformModule(
        module_id="scientific_computing_engineering",
        icon="🧮",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Cálculos científicos, modelagem matemática, análise numérica e apoio computacional a projetos de engenharia.",
        technology_family=(TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION),
    ),
    PlatformModule(
        module_id="simulation_optimization_operations_research",
        icon="🧪",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Simulação de cenários, otimização matemática, pesquisa operacional, alocação de recursos e apoio à decisão.",
        technology_family=(TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION),
    ),
    PlatformModule(
        module_id="research_labs_assisted_discovery",
        icon="🔬",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Organização de experimentos, análise de resultados, literatura científica, hipóteses e descoberta assistida por IA.",
        technology_family=(TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION),
    ),
    PlatformModule(
        module_id="materials_product_engineering",
        icon="🧱",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Análise de propriedades, testes, falhas, formulações, qualidade de materiais e desenvolvimento de produtos.",
        technology_family=(TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION),
    ),
    PlatformModule(
        module_id="construction_bim_digital_engineering",
        icon="🏗️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Projetos, obras, cronogramas, inspeções, documentos técnicos, modelos BIM e acompanhamento digital da execução.",
        technology_family=(TechnologyFamily.ENGINEERING_SCIENCE_OPTIMIZATION),
    ),
    PlatformModule(
        module_id="climate_meteorological_intelligence",
        icon="🌦️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="api",
        description="Previsões meteorológicas, riscos climáticos, chuvas, secas, ondas de calor e alertas operacionais.",
        technology_family=(TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY),
    ),
    PlatformModule(
        module_id="environmental_natural_resources_intelligence",
        icon="🌊",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Monitoramento de água, florestas, solo, biodiversidade, resíduos, poluição e recursos naturais.",
        technology_family=(TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY),
    ),
    PlatformModule(
        module_id="energy_smart_grids",
        icon="⚡",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Consumo, geração, armazenamento, energia solar, baterias, previsão de demanda e redes inteligentes.",
        technology_family=(TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY),
    ),
    PlatformModule(
        module_id="esg_sustainability",
        icon="🌱",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Indicadores ambientais, sociais e de governança, metas, emissões, relatórios e compromissos ESG.",
        technology_family=(TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY),
    ),
    PlatformModule(
        module_id="emergency_disaster_management",
        icon="🧯",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Gestão de enchentes, queimadas, deslizamentos, acidentes, áreas afetadas, evacuação e coordenação de equipes.",
        technology_family=(TechnologyFamily.CLIMATE_ENVIRONMENT_ENERGY),
    ),
    PlatformModule(
        module_id="mobility_traffic_transport",
        icon="🚦",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Rotas, frotas, congestionamentos, transporte público, entregas, acidentes e planejamento de mobilidade.",
        technology_family=(TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE),
    ),
    PlatformModule(
        module_id="smart_cities_urban_infrastructure",
        icon="🏙️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Integração de iluminação, trânsito, água, resíduos, segurança urbana, obras, sensores e serviços municipais.",
        technology_family=(TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE),
    ),
    PlatformModule(
        module_id="networks_telecommunications_connectivity",
        icon="📶",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Monitoramento de redes, cobertura, falhas, qualidade, capacidade e infraestrutura de telecomunicações.",
        technology_family=(TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE),
    ),
    PlatformModule(
        module_id="navigation_positioning_geolocation",
        icon="🧭",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="api",
        description="GPS, GNSS, localização de ativos, rastreamento, geofencing, posicionamento e navegação.",
        technology_family=(TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE),
    ),
    PlatformModule(
        module_id="asset_management_smart_maintenance",
        icon="🔧",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Gestão de equipamentos, veículos, máquinas, ordens de serviço, peças, falhas e manutenção preditiva.",
        technology_family=(TechnologyFamily.MOBILITY_CONNECTED_INFRASTRUCTURE),
    ),
    PlatformModule(
        module_id="ai_software_engineering",
        icon="🧑‍💻",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Geração, revisão e modernização de código, documentação, arquitetura e assistência ao desenvolvimento.",
        technology_family=(TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE),
    ),
    PlatformModule(
        module_id="ai_collaboration_meetings_productivity",
        icon="🧑‍🤝‍🧑",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Atas, tarefas, decisões, acompanhamento de reuniões, gestão do conhecimento e colaboração entre equipes.",
        technology_family=(TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE),
    ),
    PlatformModule(
        module_id="digital_experiences_intelligent_interfaces",
        icon="🎨",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Interfaces adaptativas, personalização, acessibilidade, experiências conversacionais e interação digital.",
        technology_family=(TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE),
    ),
    PlatformModule(
        module_id="software_testing_quality_reliability",
        icon="🧪",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Testes automatizados, qualidade de código, confiabilidade, regressão, desempenho e validação de software.",
        technology_family=(TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE),
    ),
    PlatformModule(
        module_id="mobile_apps_omnichannel_experiences",
        icon="📱",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Aplicações móveis e experiências integradas entre web, aplicativo, WhatsApp, e-mail, voz e outros canais.",
        technology_family=(TechnologyFamily.SOFTWARE_PRODUCTIVITY_EXPERIENCE),
    ),
    PlatformModule(
        module_id="digital_identity_verifiable_credentials",
        icon="🪪",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Identidades digitais, emissão, verificação, revogação e compartilhamento controlado de credenciais.",
        technology_family=(TechnologyFamily.DIGITAL_TRUST_GOVERNANCE),
    ),
    PlatformModule(
        module_id="technology_governance_policy_compliance",
        icon="📜",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Políticas, controles, padrões, auditoria, responsabilidades e conformidade aplicados à tecnologia.",
        technology_family=(TechnologyFamily.DIGITAL_TRUST_GOVERNANCE),
    ),
    PlatformModule(
        module_id="data_traceability_provenance",
        icon="📦",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Registro da origem, transformação, autoria, linhagem e histórico de dados, modelos e decisões.",
        technology_family=(TechnologyFamily.DIGITAL_TRUST_GOVERNANCE),
    ),
    PlatformModule(
        module_id="enterprise_decision_intelligence",
        icon="🧠",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Combinação de dados, regras, previsões, simulações e evidências para recomendar decisões empresariais.",
        technology_family=(TechnologyFamily.DIGITAL_TRUST_GOVERNANCE),
    ),
    PlatformModule(
        module_id="operational_security_resilience",
        icon="🛡️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description="Continuidade de negócios, contingência, recuperação de desastres, disponibilidade e riscos operacionais.",
        technology_family=(TechnologyFamily.DIGITAL_TRUST_GOVERNANCE),
    ),
    PlatformModule(
        module_id="responsible_ai_ethics_risk",
        icon="⚖️",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Princípios de IA responsável, ética, impactos, classificação de riscos e controles no ciclo de vida.",
        technology_family=(TechnologyFamily.AI_EVALUATION_TRUST),
    ),
    PlatformModule(
        module_id="ai_evaluation_benchmarks_red_team",
        icon="🧪",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Avaliação de modelos e agentes, benchmarks, testes adversariais, red team, regressão e aprovação.",
        technology_family=(TechnologyFamily.AI_EVALUATION_TRUST),
    ),
    PlatformModule(
        module_id="model_explainability_interpretability",
        icon="🔍",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Explicação de previsões, fatores relevantes, interpretação de modelos, transparência e evidências.",
        technology_family=(TechnologyFamily.AI_EVALUATION_TRUST),
    ),
    PlatformModule(
        module_id="ai_bias_quality_monitoring",
        icon="📊",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Monitoramento de viés, qualidade, precisão, deriva, segurança e desempenho de modelos e agentes.",
        technology_family=(TechnologyFamily.AI_EVALUATION_TRUST),
    ),
    PlatformModule(
        module_id="ai_certification_system_evidence",
        icon="✅",
        category=PlatformModuleCategory.TECHNOLOGY_CORE,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="internal",
        description="Evidências, relatórios, rastreabilidade, critérios de conformidade e preparação para certificação de IA.",
        technology_family=(TechnologyFamily.AI_EVALUATION_TRUST),
    ),
    PlatformModule(
        module_id="pet_shops_veterinary_services",
        icon="🐾",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Gestão de clientes, animais, agenda, banho, tosa, consultas, estoque, pagamentos, lembretes e serviços veterinários."
        ),
    ),
    PlatformModule(
        module_id="supermarkets_wholesale",
        icon="🛒",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Compras, vendas, preços, estoque, validade, reposição, fornecedores, fidelidade, margem e operação de supermercados e atacado."
        ),
    ),
    PlatformModule(
        module_id="retail_stores",
        icon="🏪",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Clientes, vendas, pedidos, caixa, estoque, promoções, fidelização, pós-venda e gestão inteligente de lojas e varejo."
        ),
    ),
    PlatformModule(
        module_id="dentistry",
        icon="🦷",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Agenda, pacientes, retornos, planos de tratamento, documentos, orçamentos, pagamentos e gestão odontológica."
        ),
    ),
    PlatformModule(
        module_id="hospitals_clinics",
        icon="🏥",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Atendimento administrativo, agenda, fluxos, documentos, estoque, fornecedores, recursos e indicadores de hospitais e clínicas."
        ),
    ),
    PlatformModule(
        module_id="mobility_transport_connected_vehicles",
        icon="🚚",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Solução para veículos, frotas, transporte "
            "rodoviário, ferroviário, aéreo, marítimo, "
            "mobilidade urbana e máquinas especiais."
        ),
    ),
    PlatformModule(
        module_id="agribusiness_smart_agriculture_bioeconomy",
        icon="🌾",
        category=PlatformModuleCategory.SECTOR_SOLUTIONS,
        status=PlatformModuleStatus.PLANNED,
        navigation_group_id=None,
        integration_type="hybrid",
        description=(
            "Produção vegetal, pecuária, máquinas, clima, "
            "solo, água, armazenagem, logística, riscos, "
            "sustentabilidade e rastreabilidade agrícola."
        ),
    ),
    PlatformModule(
        module_id="administration",
        category=PlatformModuleCategory.PLATFORM_ADMINISTRATION,
        icon="🔐",
        status=PlatformModuleStatus.ACTIVE,
        navigation_group_id="administration",
        integration_type="internal",
        description=(
            "Administração, exportações, segurança e configurações da plataforma."
        ),
    ),
)


PLATFORM_MODULE_BY_ID: dict[str, PlatformModule] = {
    module.module_id: module for module in PLATFORM_MODULES
}


def platform_module(
    module_id: str,
) -> PlatformModule | None:
    """Retorna um módulo pelo identificador."""

    return PLATFORM_MODULE_BY_ID.get(module_id)


def platform_modules_by_status(
    status: PlatformModuleStatus,
) -> tuple[PlatformModule, ...]:
    """Retorna módulos de um determinado estado."""

    return tuple(module for module in PLATFORM_MODULES if module.status is status)


def active_platform_modules() -> tuple[PlatformModule, ...]:
    """Retorna somente módulos atualmente funcionais."""

    return platform_modules_by_status(PlatformModuleStatus.ACTIVE)


def platform_modules_by_category(
    category: PlatformModuleCategory,
) -> tuple[PlatformModule, ...]:
    """Retorna módulos de uma categoria."""

    return tuple(module for module in PLATFORM_MODULES if module.category is category)


def platform_modules_by_technology_family(
    family: TechnologyFamily,
) -> tuple[PlatformModule, ...]:
    """Retorna módulos de uma família tecnológica."""

    return tuple(
        module for module in PLATFORM_MODULES if module.technology_family is family
    )


def validate_platform_module_registry() -> None:
    """Valida a integridade do registro central."""

    module_ids = [module.module_id for module in PLATFORM_MODULES]

    if len(module_ids) != len(set(module_ids)):
        raise ValueError("Existem módulos duplicados no registro.")

    for module in PLATFORM_MODULES:
        if not module.module_id.strip():
            raise ValueError("Módulo com identificador vazio.")

        if not module.icon.strip():
            raise ValueError(f"Módulo sem ícone: {module.module_id}")

        if not isinstance(
            module.category,
            PlatformModuleCategory,
        ):
            raise TypeError(f"Categoria inválida: {module.module_id}")

        if (
            module.category is PlatformModuleCategory.TECHNOLOGY_CORE
            and module.technology_family is None
        ):
            raise ValueError(f"Módulo tecnológico sem família: {module.module_id}")

        if (
            module.category is not PlatformModuleCategory.TECHNOLOGY_CORE
            and module.technology_family is not None
        ):
            raise ValueError(
                "Família tecnológica aplicada fora "
                "do núcleo tecnológico: "
                f"{module.module_id}"
            )

        if module.technology_family is not None and not isinstance(
            module.technology_family,
            TechnologyFamily,
        ):
            raise TypeError(f"Família tecnológica inválida: {module.module_id}")

        if not module.description.strip():
            raise ValueError(f"Módulo sem descrição: {module.module_id}")

        if (
            module.status is PlatformModuleStatus.ACTIVE
            and module.navigation_group_id is None
        ):
            raise ValueError(f"Módulo ativo sem grupo de navegação: {module.module_id}")


validate_platform_module_registry()
