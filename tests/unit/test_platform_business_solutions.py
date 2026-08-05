from src.platform_business_solutions import (
    BUSINESS_AUTOMATION_SOLUTION,
    CRM_CUSTOMER_EXPERIENCE_SOLUTION,
    DATA_BI_COPILOT_SOLUTION,
    DOCUMENT_AI_SOLUTION,
    ERP_BUSINESS_OPERATIONS_SOLUTION,
    FINANCIAL_SOLUTIONS_SOLUTION,
    HR_PEOPLE_ANALYTICS_SOLUTION,
    INTELLIGENT_SUPPORT_SOLUTION,
    LEGAL_COMPLIANCE_SOLUTION,
    PLATFORM_BUSINESS_SOLUTIONS,
    QUALITY_PROCESS_MANAGEMENT_SOLUTION,
    SITE_APP_GENERATOR_SOLUTION,
    SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
    BusinessSolutionStatus,
    platform_business_solution,
    validate_platform_business_solution_registry,
)


def test_business_solution_registry_is_valid():
    validate_platform_business_solution_registry()


def test_document_ai_is_registered():
    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 12

    assert platform_business_solution("document_ai") is DOCUMENT_AI_SOLUTION


def test_document_ai_solution_is_complete():
    assert DOCUMENT_AI_SOLUTION.solution_id == "document_ai"
    assert DOCUMENT_AI_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert DOCUMENT_AI_SOLUTION.integration_type == "hybrid"
    assert len(DOCUMENT_AI_SOLUTION.areas) == 6
    assert DOCUMENT_AI_SOLUTION.capability_count == 17


def test_document_ai_capabilities_have_dependencies():
    for area in DOCUMENT_AI_SOLUTION.areas:
        assert area.capabilities

        for capability in area.capabilities:
            assert capability.technology_dependencies


def test_document_ai_dependency_list_has_no_duplicates():
    dependencies = DOCUMENT_AI_SOLUTION.technology_dependencies

    assert dependencies
    assert len(dependencies) == len(set(dependencies))


def test_unknown_business_solution_returns_none():
    assert platform_business_solution("unknown_business_solution") is None


def test_business_automation_solution_is_complete():
    assert BUSINESS_AUTOMATION_SOLUTION.solution_id == "business_automation"
    assert BUSINESS_AUTOMATION_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert BUSINESS_AUTOMATION_SOLUTION.integration_type == "hybrid"
    assert len(BUSINESS_AUTOMATION_SOLUTION.areas) == 6
    assert BUSINESS_AUTOMATION_SOLUTION.capability_count == 18


def test_business_automation_lookup():
    assert (
        platform_business_solution("business_automation")
        is BUSINESS_AUTOMATION_SOLUTION
    )


def test_intelligent_support_solution_is_complete():
    assert INTELLIGENT_SUPPORT_SOLUTION.solution_id == "intelligent_support"
    assert INTELLIGENT_SUPPORT_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert INTELLIGENT_SUPPORT_SOLUTION.integration_type == "hybrid"
    assert len(INTELLIGENT_SUPPORT_SOLUTION.areas) == 6
    assert INTELLIGENT_SUPPORT_SOLUTION.capability_count == 18


def test_intelligent_support_lookup():
    assert (
        platform_business_solution("intelligent_support")
        is INTELLIGENT_SUPPORT_SOLUTION
    )


def test_data_bi_copilot_solution_is_complete():
    assert DATA_BI_COPILOT_SOLUTION.solution_id == "data_bi_copilot"
    assert DATA_BI_COPILOT_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert DATA_BI_COPILOT_SOLUTION.integration_type == "hybrid"
    assert len(DATA_BI_COPILOT_SOLUTION.areas) == 6
    assert DATA_BI_COPILOT_SOLUTION.capability_count == 18


def test_data_bi_copilot_lookup():
    assert platform_business_solution("data_bi_copilot") is DATA_BI_COPILOT_SOLUTION


def test_quality_process_solution_is_complete():
    assert (
        QUALITY_PROCESS_MANAGEMENT_SOLUTION.solution_id == "quality_process_management"
    )
    assert QUALITY_PROCESS_MANAGEMENT_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert QUALITY_PROCESS_MANAGEMENT_SOLUTION.integration_type == "hybrid"
    assert len(QUALITY_PROCESS_MANAGEMENT_SOLUTION.areas) == 6
    assert QUALITY_PROCESS_MANAGEMENT_SOLUTION.capability_count == 18


def test_quality_process_solution_lookup():
    assert (
        platform_business_solution("quality_process_management")
        is QUALITY_PROCESS_MANAGEMENT_SOLUTION
    )


def test_crm_customer_experience_solution_is_complete():
    assert CRM_CUSTOMER_EXPERIENCE_SOLUTION.solution_id == "crm_sales_intelligence"
    assert CRM_CUSTOMER_EXPERIENCE_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert CRM_CUSTOMER_EXPERIENCE_SOLUTION.integration_type == "hybrid"
    assert len(CRM_CUSTOMER_EXPERIENCE_SOLUTION.areas) == 6
    assert CRM_CUSTOMER_EXPERIENCE_SOLUTION.capability_count == 18


def test_crm_customer_experience_lookup():
    assert (
        platform_business_solution("crm_sales_intelligence")
        is CRM_CUSTOMER_EXPERIENCE_SOLUTION
    )


def test_legal_compliance_solution_is_complete():
    assert LEGAL_COMPLIANCE_SOLUTION.solution_id == "legal_compliance"
    assert LEGAL_COMPLIANCE_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert LEGAL_COMPLIANCE_SOLUTION.integration_type == "hybrid"
    assert len(LEGAL_COMPLIANCE_SOLUTION.areas) == 6
    assert LEGAL_COMPLIANCE_SOLUTION.capability_count == 18


def test_legal_compliance_solution_lookup():
    assert platform_business_solution("legal_compliance") is LEGAL_COMPLIANCE_SOLUTION


def test_erp_business_operations_solution_is_complete():
    assert ERP_BUSINESS_OPERATIONS_SOLUTION.solution_id == "erp_business_operations"
    assert ERP_BUSINESS_OPERATIONS_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert ERP_BUSINESS_OPERATIONS_SOLUTION.integration_type == "hybrid"
    assert len(ERP_BUSINESS_OPERATIONS_SOLUTION.areas) == 6
    assert ERP_BUSINESS_OPERATIONS_SOLUTION.capability_count == 18


def test_erp_business_operations_solution_lookup():
    assert (
        platform_business_solution("erp_business_operations")
        is ERP_BUSINESS_OPERATIONS_SOLUTION
    )


def test_supply_chain_solution_is_complete():
    assert (
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.solution_id
        == "supply_chain_procurement_logistics"
    )
    assert (
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.integration_type == "hybrid"
    assert len(SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.areas) == 6
    assert SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.capability_count == 18


def test_supply_chain_solution_lookup():
    assert (
        platform_business_solution("supply_chain_procurement_logistics")
        is SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION
    )


def test_hr_people_analytics_solution_is_complete():
    assert HR_PEOPLE_ANALYTICS_SOLUTION.solution_id == "hr_people_analytics"
    assert HR_PEOPLE_ANALYTICS_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert HR_PEOPLE_ANALYTICS_SOLUTION.integration_type == "hybrid"
    assert len(HR_PEOPLE_ANALYTICS_SOLUTION.areas) == 6
    assert HR_PEOPLE_ANALYTICS_SOLUTION.capability_count == 18


def test_hr_people_analytics_solution_lookup():
    assert (
        platform_business_solution("hr_people_analytics")
        is HR_PEOPLE_ANALYTICS_SOLUTION
    )


def test_financial_solutions_solution_is_complete():
    assert FINANCIAL_SOLUTIONS_SOLUTION.solution_id == "financial_solutions"
    assert FINANCIAL_SOLUTIONS_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert FINANCIAL_SOLUTIONS_SOLUTION.integration_type == "hybrid"
    assert len(FINANCIAL_SOLUTIONS_SOLUTION.areas) == 6
    assert FINANCIAL_SOLUTIONS_SOLUTION.capability_count == 18


def test_financial_solutions_solution_lookup():
    assert (
        platform_business_solution("financial_solutions")
        is FINANCIAL_SOLUTIONS_SOLUTION
    )


def test_site_app_generator_solution_is_complete():
    assert SITE_APP_GENERATOR_SOLUTION.solution_id == "site_app_generator"
    assert SITE_APP_GENERATOR_SOLUTION.status is BusinessSolutionStatus.PLANNED
    assert SITE_APP_GENERATOR_SOLUTION.integration_type == "hybrid"
    assert len(SITE_APP_GENERATOR_SOLUTION.areas) == 6
    assert SITE_APP_GENERATOR_SOLUTION.capability_count == 18


def test_site_app_generator_solution_lookup():
    assert (
        platform_business_solution("site_app_generator") is SITE_APP_GENERATOR_SOLUTION
    )
