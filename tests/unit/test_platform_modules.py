from src.platform_modules import (
    PLATFORM_MODULE_BY_ID,
    PLATFORM_MODULES,
    PlatformModuleCategory,
    PlatformModuleStatus,
    TechnologyFamily,
    active_platform_modules,
    platform_module,
    platform_modules_by_category,
    platform_modules_by_status,
    platform_modules_by_technology_family,
    validate_platform_module_registry,
)

EXPECTED_MODULE_IDS = {
    "administration",
    "agent_process_orchestration",
    "agribusiness_smart_agriculture_bioeconomy",
    "ai_bias_quality_monitoring",
    "ai_certification_system_evidence",
    "ai_collaboration_meetings_productivity",
    "ai_evaluation_benchmarks_red_team",
    "ai_model_agent_security",
    "ai_operations",
    "ai_software_engineering",
    "api_integrations_connectors",
    "asset_management_smart_maintenance",
    "business_automation",
    "climate_meteorological_intelligence",
    "cloud_devops_finops",
    "computer_vision_video_analytics",
    "construction_bim_digital_engineering",
    "crm_sales_intelligence",
    "cryptography_confidential_computing",
    "cybersecurity_fraud_prevention",
    "data_bi_copilot",
    "data_platform_governance",
    "data_traceability_provenance",
    "dentistry",
    "digital_experiences_intelligent_interfaces",
    "digital_identity_verifiable_credentials",
    "digital_twins_simulation",
    "document_ai",
    "drones_aerial_intelligence",
    "emergency_disaster_management",
    "energy_smart_grids",
    "enterprise_decision_intelligence",
    "enterprise_rag",
    "environmental_natural_resources_intelligence",
    "erp_business_operations",
    "esg_sustainability",
    "financial_solutions",
    "geoai_earth_observation",
    "gis_location_intelligence",
    "hospitals_clinics",
    "hr_people_analytics",
    "intelligent_support",
    "iot_edge_intelligence",
    "knowledge_graph_semantic_ai",
    "legal_compliance",
    "materials_product_engineering",
    "mobile_apps_omnichannel_experiences",
    "mobility_traffic_transport",
    "mobility_transport_connected_vehicles",
    "model_explainability_interpretability",
    "multimodal_ai",
    "navigation_positioning_geolocation",
    "networks_telecommunications_connectivity",
    "operational_security_resilience",
    "pet_shops_veterinary_services",
    "privacy_data_protection_lgpd",
    "privacy_enhancing_technologies",
    "quality_process_management",
    "real_time_event_intelligence",
    "research_labs_assisted_discovery",
    "responsible_ai_ethics_risk",
    "retail_stores",
    "robotics_autonomous_systems",
    "scientific_computing_engineering",
    "simulation_optimization_operations_research",
    "site_app_generator",
    "smart_cities_urban_infrastructure",
    "software_supply_chain_security",
    "software_testing_quality_reliability",
    "spatial_computing_augmented_reality",
    "supermarkets_wholesale",
    "supply_chain_procurement_logistics",
    "technology_governance_policy_compliance",
    "tools_analytics",
    "voice_audio_speech_ai",
    "zero_trust_identity_access",
}


def test_platform_module_registry_is_valid():
    validate_platform_module_registry()


def test_platform_module_ids_are_unique():
    module_ids = [module.module_id for module in PLATFORM_MODULES]

    assert len(module_ids) == len(set(module_ids))


def test_platform_has_expected_modules():
    assert set(PLATFORM_MODULE_BY_ID) == (EXPECTED_MODULE_IDS)


def test_active_modules_have_navigation_groups():
    for module in active_platform_modules():
        assert module.navigation_group_id is not None
        assert module.is_available is True


def test_hr_people_analytics_is_integrating():
    hr_module = platform_module("hr_people_analytics")

    assert hr_module is not None
    assert hr_module.status is PlatformModuleStatus.INTEGRATING
    assert hr_module.integration_type == "api"
    assert hr_module.is_external_integration is True
    assert "ATS" in hr_module.description


def test_planned_modules_are_not_available():
    planned_modules = platform_modules_by_status(PlatformModuleStatus.PLANNED)

    expected_planned_module_ids = {
        "agent_process_orchestration",
        "agribusiness_smart_agriculture_bioeconomy",
        "ai_bias_quality_monitoring",
        "ai_certification_system_evidence",
        "ai_collaboration_meetings_productivity",
        "ai_evaluation_benchmarks_red_team",
        "ai_model_agent_security",
        "ai_software_engineering",
        "api_integrations_connectors",
        "asset_management_smart_maintenance",
        "business_automation",
        "climate_meteorological_intelligence",
        "cloud_devops_finops",
        "computer_vision_video_analytics",
        "construction_bim_digital_engineering",
        "crm_sales_intelligence",
        "cryptography_confidential_computing",
        "cybersecurity_fraud_prevention",
        "data_bi_copilot",
        "data_platform_governance",
        "data_traceability_provenance",
        "dentistry",
        "digital_experiences_intelligent_interfaces",
        "digital_identity_verifiable_credentials",
        "digital_twins_simulation",
        "document_ai",
        "drones_aerial_intelligence",
        "emergency_disaster_management",
        "energy_smart_grids",
        "enterprise_decision_intelligence",
        "environmental_natural_resources_intelligence",
        "erp_business_operations",
        "esg_sustainability",
        "geoai_earth_observation",
        "gis_location_intelligence",
        "hospitals_clinics",
        "intelligent_support",
        "iot_edge_intelligence",
        "knowledge_graph_semantic_ai",
        "legal_compliance",
        "materials_product_engineering",
        "mobile_apps_omnichannel_experiences",
        "mobility_traffic_transport",
        "mobility_transport_connected_vehicles",
        "model_explainability_interpretability",
        "multimodal_ai",
        "navigation_positioning_geolocation",
        "networks_telecommunications_connectivity",
        "operational_security_resilience",
        "pet_shops_veterinary_services",
        "privacy_data_protection_lgpd",
        "privacy_enhancing_technologies",
        "quality_process_management",
        "real_time_event_intelligence",
        "research_labs_assisted_discovery",
        "responsible_ai_ethics_risk",
        "retail_stores",
        "robotics_autonomous_systems",
        "scientific_computing_engineering",
        "simulation_optimization_operations_research",
        "site_app_generator",
        "smart_cities_urban_infrastructure",
        "software_supply_chain_security",
        "software_testing_quality_reliability",
        "spatial_computing_augmented_reality",
        "supermarkets_wholesale",
        "supply_chain_procurement_logistics",
        "technology_governance_policy_compliance",
        "voice_audio_speech_ai",
        "zero_trust_identity_access",
    }

    assert {
        module.module_id for module in planned_modules
    } == expected_planned_module_ids

    assert all(module.navigation_group_id is None for module in planned_modules)

    assert all(module.is_available is False for module in planned_modules)


def test_unknown_module_returns_none():
    assert platform_module("unknown_module") is None


def test_internal_module_is_not_external():
    financial = platform_module("financial_solutions")

    assert financial is not None
    assert financial.is_external_integration is False


def test_registry_contains_seventy_six_modules():
    assert len(PLATFORM_MODULES) == 76


def test_intelligent_support_is_planned():
    support = platform_module("intelligent_support")

    assert support is not None
    assert support.status is PlatformModuleStatus.PLANNED
    assert support.integration_type == "hybrid"
    assert support.is_available is False
    assert support.is_external_integration is True


def test_enterprise_expansion_modules_are_planned():
    module_ids = {
        "data_bi_copilot",
        "quality_process_management",
        "crm_sales_intelligence",
        "legal_compliance",
        "cybersecurity_fraud_prevention",
    }

    for module_id in module_ids:
        module = platform_module(module_id)

        assert module is not None
        assert module.status is PlatformModuleStatus.PLANNED
        assert module.navigation_group_id is None
        assert module.integration_type == "hybrid"
        assert module.is_available is False


def test_modules_are_grouped_by_category():
    business_modules = platform_modules_by_category(
        PlatformModuleCategory.BUSINESS_SOLUTIONS
    )
    technology_modules = platform_modules_by_category(
        PlatformModuleCategory.TECHNOLOGY_CORE
    )
    administration_modules = platform_modules_by_category(
        PlatformModuleCategory.PLATFORM_ADMINISTRATION
    )
    sector_modules = platform_modules_by_category(
        PlatformModuleCategory.SECTOR_SOLUTIONS
    )

    assert len(business_modules) == 12
    assert len(technology_modules) == 56
    assert len(administration_modules) == 1
    assert len(sector_modules) == 7

    registered_ids = {
        module.module_id
        for module in (
            business_modules
            + technology_modules
            + administration_modules
            + sector_modules
        )
    }

    assert registered_ids == EXPECTED_MODULE_IDS


def test_overview_is_not_a_platform_module():
    assert platform_module("overview") is None


def test_cybersecurity_is_in_technology_core():
    cybersecurity = platform_module("cybersecurity_fraud_prevention")

    assert cybersecurity is not None
    assert cybersecurity.category is PlatformModuleCategory.TECHNOLOGY_CORE


def test_cloud_devops_finops_is_planned():
    cloud_module = platform_module("cloud_devops_finops")

    assert cloud_module is not None
    assert cloud_module.category is PlatformModuleCategory.TECHNOLOGY_CORE
    assert cloud_module.status is PlatformModuleStatus.PLANNED
    assert cloud_module.integration_type == "hybrid"
    assert cloud_module.is_available is False


def test_api_integrations_connectors_is_planned():
    module = platform_module("api_integrations_connectors")

    assert module is not None
    assert module.category is PlatformModuleCategory.TECHNOLOGY_CORE
    assert module.status is PlatformModuleStatus.PLANNED
    assert module.integration_type == "hybrid"
    assert module.is_available is False


def test_data_platform_governance_is_planned():
    module = platform_module("data_platform_governance")

    assert module is not None
    assert module.category is PlatformModuleCategory.TECHNOLOGY_CORE
    assert module.status is PlatformModuleStatus.PLANNED
    assert module.integration_type == "hybrid"
    assert module.is_available is False


def test_erp_and_supply_chain_are_planned():
    expected_ids = {
        "erp_business_operations",
        "supply_chain_procurement_logistics",
    }

    for module_id in expected_ids:
        module = platform_module(module_id)

        assert module is not None
        assert module.category is PlatformModuleCategory.BUSINESS_SOLUTIONS
        assert module.status is PlatformModuleStatus.PLANNED
        assert module.integration_type == "hybrid"
        assert module.is_available is False


def test_crm_covers_customer_experience():
    module = platform_module("crm_sales_intelligence")

    assert module is not None
    assert module.icon == "🤝"
    assert "Customer 360" in module.description
    assert "pós-venda" in module.description


def test_sector_solutions_are_planned():
    expected_ids = {
        "pet_shops_veterinary_services",
        "supermarkets_wholesale",
        "retail_stores",
        "dentistry",
        "hospitals_clinics",
        "mobility_transport_connected_vehicles",
        "agribusiness_smart_agriculture_bioeconomy",
    }

    sector_modules = platform_modules_by_category(
        PlatformModuleCategory.SECTOR_SOLUTIONS
    )

    assert {module.module_id for module in sector_modules} == expected_ids

    assert all(
        module.status is PlatformModuleStatus.PLANNED for module in sector_modules
    )

    assert all(module.integration_type == "hybrid" for module in sector_modules)

    assert all(
        module.navigation_group_id is None and module.is_available is False
        for module in sector_modules
    )


def test_technology_modules_have_families():
    technology_modules = platform_modules_by_category(
        PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert len(technology_modules) == 56
    assert all(module.technology_family is not None for module in technology_modules)


def test_non_technology_modules_have_no_family():
    non_technology_modules = tuple(
        module
        for module in PLATFORM_MODULES
        if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert non_technology_modules
    assert all(module.technology_family is None for module in non_technology_modules)


def test_existing_technology_family_distribution():
    assert {
        module.module_id
        for module in (
            platform_modules_by_technology_family(TechnologyFamily.AI_KNOWLEDGE_AGENTS)
        )
    } == {
        "enterprise_rag",
        "knowledge_graph_semantic_ai",
        "multimodal_ai",
        "voice_audio_speech_ai",
        "agent_process_orchestration",
        "ai_model_agent_security",
    }

    assert {
        module.module_id
        for module in (
            platform_modules_by_technology_family(
                TechnologyFamily.DATA_INTEGRATION_OPERATIONS
            )
        )
    } == {
        "api_integrations_connectors",
        "data_platform_governance",
        "real_time_event_intelligence",
        "cloud_devops_finops",
        "ai_operations",
        "tools_analytics",
    }

    assert {
        module.module_id
        for module in (
            platform_modules_by_technology_family(
                TechnologyFamily.SECURITY_PRIVACY_TRUST
            )
        )
    } == {
        "cybersecurity_fraud_prevention",
        "privacy_data_protection_lgpd",
        "zero_trust_identity_access",
        "cryptography_confidential_computing",
        "software_supply_chain_security",
        "privacy_enhancing_technologies",
    }

    assert {
        module.module_id
        for module in (
            platform_modules_by_technology_family(
                TechnologyFamily.GEOSPATIAL_OBSERVATION
            )
        )
    } == {
        "geoai_earth_observation",
        "gis_location_intelligence",
        "drones_aerial_intelligence",
        "spatial_computing_augmented_reality",
    }

    assert {
        module.module_id
        for module in (
            platform_modules_by_technology_family(
                TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION
            )
        )
    } == {
        "iot_edge_intelligence",
        "computer_vision_video_analytics",
        "digital_twins_simulation",
        "robotics_autonomous_systems",
    }


def test_all_technology_families_have_modules():
    assert all(
        platform_modules_by_technology_family(family) for family in TechnologyFamily
    )


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
            module.module_id for module in platform_modules_by_technology_family(family)
        } == expected_ids


def test_specialized_sector_solution_cards():
    expected_ids = {
        "mobility_transport_connected_vehicles",
        "agribusiness_smart_agriculture_bioeconomy",
    }

    for module_id in expected_ids:
        module = platform_module(module_id)

        assert module is not None
        assert module.category is PlatformModuleCategory.SECTOR_SOLUTIONS
        assert module.status is PlatformModuleStatus.PLANNED
        assert module.integration_type == "hybrid"
        assert module.navigation_group_id is None
        assert module.is_available is False
