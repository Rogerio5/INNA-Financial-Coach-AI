from src.dashboard_pages.platform_modules_overview import (
    OVERVIEW_TEXTS,
    build_platform_module_cards,
    overview_t,
)
from src.platform_modules import (
    PlatformModuleCategory,
    PlatformModuleStatus,
    TechnologyFamily,
)

LANGUAGES = {
    "pt",
    "en_us",
    "en_gb",
    "es",
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
    "ch",
}


def test_overview_supports_all_languages():
    assert set(OVERVIEW_TEXTS) == LANGUAGES


def test_overview_text_contract_is_complete():
    expected_keys = {
        "title",
        "caption",
        "integration",
        "available",
        "unavailable",
    }

    for texts in OVERVIEW_TEXTS.values():
        assert set(texts) == expected_keys
        assert all(value.strip() for value in texts.values())


def test_builds_seventy_six_platform_module_cards():
    cards = build_platform_module_cards("pt")

    assert len(cards) == 76
    assert len({card.module_id for card in cards}) == 76


def test_active_modules_are_available():
    cards = build_platform_module_cards("pt")

    active_cards = [
        card for card in cards if card.status_code is PlatformModuleStatus.ACTIVE
    ]

    assert active_cards
    assert all(card.is_available for card in active_cards)


def test_future_modules_are_not_available():
    cards = build_platform_module_cards("pt")

    future_cards = [
        card
        for card in cards
        if card.status_code
        in {
            PlatformModuleStatus.INTEGRATING,
            PlatformModuleStatus.PLANNED,
        }
    ]

    assert future_cards
    assert all(card.is_available is False for card in future_cards)


def test_hr_people_analytics_is_integrating():
    cards = build_platform_module_cards("pt")

    hr_module = next(card for card in cards if card.module_id == "hr_people_analytics")

    assert hr_module.status_code is PlatformModuleStatus.INTEGRATING
    assert hr_module.integration_type == "api"
    assert hr_module.is_available is False


def test_portuguese_overview_title():
    assert (
        overview_t(
            "title",
            "pt",
        )
        == "Módulos da INNA AI Platform"
    )


def test_unknown_language_falls_back():
    assert (
        overview_t(
            "available",
            "unknown",
        )
        == "Disponível"
    )


def test_ch_follows_german():
    assert OVERVIEW_TEXTS["ch"] == OVERVIEW_TEXTS["de"]


def test_support_card_is_planned():
    cards = build_platform_module_cards("pt")

    support = next(card for card in cards if card.module_id == "intelligent_support")

    assert support.status_code is PlatformModuleStatus.PLANNED
    assert support.integration_type == "hybrid"
    assert support.is_available is False


def test_enterprise_expansion_cards_are_planned():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    module_ids = {
        "data_bi_copilot",
        "quality_process_management",
        "crm_sales_intelligence",
        "legal_compliance",
        "cybersecurity_fraud_prevention",
    }

    for module_id in module_ids:
        card = cards[module_id]

        assert card.status_code is PlatformModuleStatus.PLANNED
        assert card.integration_type == "hybrid"
        assert card.is_available is False


def test_overview_is_not_rendered_as_card():
    module_ids = {card.module_id for card in build_platform_module_cards("pt")}

    assert "overview" not in module_ids


def test_cards_are_separated_by_category():
    cards = build_platform_module_cards("pt")

    category_counts = {
        category: sum(card.category is category for card in cards)
        for category in PlatformModuleCategory
    }

    assert category_counts == {
        PlatformModuleCategory.BUSINESS_SOLUTIONS: 12,
        PlatformModuleCategory.TECHNOLOGY_CORE: 56,
        PlatformModuleCategory.PLATFORM_ADMINISTRATION: 1,
        PlatformModuleCategory.SECTOR_SOLUTIONS: 7,
    }


def test_card_integration_labels_are_localized():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    assert cards["financial_solutions"].integration_type == "internal"
    assert cards["financial_solutions"].integration_label == "Interna"

    assert cards["hr_people_analytics"].integration_label == "API"

    assert cards["document_ai"].integration_label == "Híbrida"


def test_cloud_devops_finops_card():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    cloud_card = cards["cloud_devops_finops"]

    assert cloud_card.category is PlatformModuleCategory.TECHNOLOGY_CORE
    assert cloud_card.status_code is PlatformModuleStatus.PLANNED
    assert cloud_card.integration_type == "hybrid"
    assert cloud_card.integration_label == "Híbrida"
    assert cloud_card.is_available is False


def test_data_foundation_cards_are_planned():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    expected_ids = {
        "api_integrations_connectors",
        "data_platform_governance",
    }

    for module_id in expected_ids:
        card = cards[module_id]

        assert card.category is PlatformModuleCategory.TECHNOLOGY_CORE
        assert card.status_code is PlatformModuleStatus.PLANNED
        assert card.integration_type == "hybrid"
        assert card.integration_label == "Híbrida"
        assert card.is_available is False


def test_erp_supply_chain_and_crm_cards():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    assert cards["crm_sales_intelligence"].title == "🤝 CRM e Experiência do Cliente"

    expected_ids = {
        "erp_business_operations",
        "supply_chain_procurement_logistics",
    }

    for module_id in expected_ids:
        card = cards[module_id]

        assert card.category is PlatformModuleCategory.BUSINESS_SOLUTIONS
        assert card.status_code is PlatformModuleStatus.PLANNED
        assert card.integration_type == "hybrid"
        assert card.integration_label == "Híbrida"
        assert card.is_available is False


def test_sector_solution_cards():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    expected_ids = {
        "pet_shops_veterinary_services",
        "supermarkets_wholesale",
        "retail_stores",
        "dentistry",
        "hospitals_clinics",
        "mobility_transport_connected_vehicles",
        "agribusiness_smart_agriculture_bioeconomy",
    }

    for module_id in expected_ids:
        card = cards[module_id]

        assert card.category is PlatformModuleCategory.SECTOR_SOLUTIONS
        assert card.status_code is PlatformModuleStatus.PLANNED
        assert card.integration_type == "hybrid"
        assert card.integration_label == "Híbrida"
        assert card.is_available is False


def test_technology_cards_include_family_metadata():
    technology_cards = tuple(
        card
        for card in build_platform_module_cards("pt")
        if card.category is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert len(technology_cards) == 56

    assert all(card.technology_family is not None for card in technology_cards)

    assert all(card.technology_family_label for card in technology_cards)


def test_non_technology_cards_have_no_family_metadata():
    cards = tuple(
        card
        for card in build_platform_module_cards("pt")
        if card.category is not PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert cards

    assert all(card.technology_family is None for card in cards)

    assert all(card.technology_family_label is None for card in cards)


def test_existing_technology_cards_are_grouped_by_family():
    cards = build_platform_module_cards("pt")

    family_module_ids = {
        family: {card.module_id for card in cards if card.technology_family is family}
        for family in TechnologyFamily
    }

    assert family_module_ids[TechnologyFamily.AI_KNOWLEDGE_AGENTS] == {
        "enterprise_rag",
        "knowledge_graph_semantic_ai",
        "multimodal_ai",
        "voice_audio_speech_ai",
        "agent_process_orchestration",
        "ai_model_agent_security",
    }

    assert family_module_ids[TechnologyFamily.DATA_INTEGRATION_OPERATIONS] == {
        "api_integrations_connectors",
        "data_platform_governance",
        "real_time_event_intelligence",
        "cloud_devops_finops",
        "ai_operations",
        "tools_analytics",
    }

    assert family_module_ids[TechnologyFamily.SECURITY_PRIVACY_TRUST] == {
        "cybersecurity_fraud_prevention",
        "privacy_data_protection_lgpd",
        "zero_trust_identity_access",
        "cryptography_confidential_computing",
        "software_supply_chain_security",
        "privacy_enhancing_technologies",
    }

    assert family_module_ids[TechnologyFamily.GEOSPATIAL_OBSERVATION] == {
        "geoai_earth_observation",
        "gis_location_intelligence",
        "drones_aerial_intelligence",
        "spatial_computing_augmented_reality",
    }

    assert family_module_ids[TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION] == {
        "iot_edge_intelligence",
        "computer_vision_video_analytics",
        "digital_twins_simulation",
        "robotics_autonomous_systems",
    }


def test_technology_family_labels_are_localized():
    cards = {card.module_id: card for card in build_platform_module_cards("pt")}

    assert (
        cards["enterprise_rag"].technology_family_label
        == "🧠 IA, conhecimento e agentes"
    )

    assert (
        cards["api_integrations_connectors"].technology_family_label
        == "🗄️ Dados, integração e operações"
    )

    assert cards["cybersecurity_fraud_prevention"].technology_family_label == (
        "🔐 Segurança, privacidade e confiança digital"
    )


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
        family_cards = tuple(card for card in cards if card.technology_family is family)
        assert len(family_cards) == expected_count
        assert all(
            card.status_code is PlatformModuleStatus.PLANNED for card in family_cards
        )
        assert all(card.is_available is False for card in family_cards)
