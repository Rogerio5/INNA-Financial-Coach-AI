from src.platform_modules import (
    PLATFORM_MODULES,
    PlatformModuleStatus,
)
from src.platform_modules_i18n import (
    PLATFORM_MODULE_STATUS_TEXTS,
    PLATFORM_MODULE_TEXTS,
    platform_module_status_t,
    platform_module_t,
    validate_platform_module_translations,
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


def test_platform_module_translations_are_valid():
    validate_platform_module_translations()


def test_all_languages_are_supported():
    assert set(PLATFORM_MODULE_TEXTS) == LANGUAGES
    assert set(PLATFORM_MODULE_STATUS_TEXTS) == LANGUAGES


def test_all_modules_have_translations():
    expected_module_ids = {module.module_id for module in PLATFORM_MODULES}

    for texts in PLATFORM_MODULE_TEXTS.values():
        assert set(texts) == expected_module_ids


def test_all_statuses_have_translations():
    expected_statuses = set(PlatformModuleStatus)

    for texts in PLATFORM_MODULE_STATUS_TEXTS.values():
        assert set(texts) == expected_statuses


def test_portuguese_module_names():
    assert (
        platform_module_t(
            "financial_solutions",
            "pt",
        )
        == "💰 Soluções Financeiras"
    )

    assert (
        platform_module_t(
            "business_automation",
            "pt",
        )
        == "🤖 Automação Empresarial"
    )


def test_portuguese_status_names():
    assert (
        platform_module_status_t(
            PlatformModuleStatus.ACTIVE,
            "pt",
        )
        == "Ativo"
    )

    assert (
        platform_module_status_t(
            PlatformModuleStatus.INTEGRATING,
            "pt",
        )
        == "Em integração"
    )


def test_english_variants_follow_contract():
    assert PLATFORM_MODULE_TEXTS["en_gb"] == PLATFORM_MODULE_TEXTS["en_us"]

    assert (
        PLATFORM_MODULE_STATUS_TEXTS["en_gb"] == PLATFORM_MODULE_STATUS_TEXTS["en_us"]
    )


def test_ch_follows_german():
    assert PLATFORM_MODULE_TEXTS["ch"] == PLATFORM_MODULE_TEXTS["de"]

    assert PLATFORM_MODULE_STATUS_TEXTS["ch"] == PLATFORM_MODULE_STATUS_TEXTS["de"]


def test_unknown_language_falls_back_to_portuguese():
    assert (
        platform_module_t(
            "financial_solutions",
            "unknown",
        )
        == "💰 Soluções Financeiras"
    )


def test_unknown_module_returns_module_id():
    assert (
        platform_module_t(
            "unknown_module",
            "pt",
        )
        == "unknown_module"
    )


def test_creation_and_support_module_names():
    assert platform_module_t(
        "site_app_generator",
        "pt",
    ) == ("🌐 Gerador de Sites, Apps e Dashboards")

    assert platform_module_t(
        "intelligent_support",
        "pt",
    ) == ("🎧 Atendimento e Suporte Inteligente")


def test_enterprise_expansion_names_in_portuguese():
    expected = {
        "data_bi_copilot": "📊 Data & BI Copilot",
        "quality_process_management": ("✅ Gestão da Qualidade e Processos"),
        "crm_sales_intelligence": ("🤝 CRM e Experiência do Cliente"),
        "legal_compliance": ("⚖️ Jurídico e Compliance"),
        "cybersecurity_fraud_prevention": ("🛡️ Cibersegurança e Prevenção a Fraudes"),
    }

    for module_id, label in expected.items():
        assert (
            platform_module_t(
                module_id,
                "pt",
            )
            == label
        )


def test_hr_people_analytics_name():
    assert (
        platform_module_t(
            "hr_people_analytics",
            "pt",
        )
        == "👥 RH e People Analytics"
    )

    assert (
        platform_module_t(
            "hr_people_analytics",
            "en_us",
        )
        == "👥 HR and People Analytics"
    )


def test_portuguese_business_expansion_labels():
    assert (
        platform_module_t(
            "crm_sales_intelligence",
            "pt",
        )
        == "🤝 CRM e Experiência do Cliente"
    )

    assert (
        platform_module_t(
            "erp_business_operations",
            "pt",
        )
        == "🏢 ERP e Operações Empresariais"
    )

    assert (
        platform_module_t(
            "supply_chain_procurement_logistics",
            "pt",
        )
        == "📦 Supply Chain, Compras e Logística"
    )


def test_portuguese_sector_solution_labels():
    expected = {
        "pet_shops_veterinary_services": ("🐾 Pet Shops e Serviços Veterinários"),
        "supermarkets_wholesale": ("🛒 Supermercados e Atacado"),
        "retail_stores": ("🏪 Lojas e Varejo"),
        "dentistry": ("🦷 Odontologia"),
        "hospitals_clinics": ("🏥 Hospitais e Clínicas"),
    }

    for module_id, label in expected.items():
        assert (
            platform_module_t(
                module_id,
                "pt",
            )
            == label
        )
