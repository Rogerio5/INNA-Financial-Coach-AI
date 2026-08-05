from datetime import date

from src.dashboard_pages.human_review.state import (
    HumanReviewDashboardFilters,
    HumanReviewDashboardState,
    dashboard_state_from_mapping,
    dashboard_state_to_dict,
)


def test_filters_normalize_values() -> None:
    filters = HumanReviewDashboardFilters(
        statuses=[
            "pending",
            "unknown",
            "pending",
        ],
        risk_levels=[
            "HIGH",
            "invalid",
        ],
        requested_by=" agent ",
        limit=500,
        offset=-20,
    )

    assert filters.statuses == ("pending",)

    assert filters.risk_levels == ("high",)

    assert filters.requested_by == ("agent")

    assert filters.limit == 200
    assert filters.offset == 0


def test_filters_swap_invalid_date_range() -> None:
    filters = HumanReviewDashboardFilters(
        created_from=date(
            2026,
            7,
            30,
        ),
        created_to=date(
            2026,
            7,
            1,
        ),
    )

    assert filters.created_from == date(
        2026,
        7,
        1,
    )

    assert filters.created_to == date(
        2026,
        7,
        30,
    )


def test_filters_build_api_kwargs() -> None:
    filters = HumanReviewDashboardFilters(
        statuses=[
            "approved",
        ],
        created_from=date(
            2026,
            7,
            1,
        ),
        limit=25,
        offset=50,
    )

    result = filters.to_api_kwargs()

    assert result["statuses"] == ("approved",)

    assert result["created_from"] == ("2026-07-01")

    assert filters.page_number == 3


def test_pagination_navigation() -> None:
    filters = HumanReviewDashboardFilters(
        limit=25,
        offset=25,
    )

    next_filters = filters.next_page(has_next=True)

    previous_filters = next_filters.previous_page()

    assert next_filters.offset == 50
    assert previous_filters.offset == 25


def test_next_page_does_not_move_when_absent() -> None:
    filters = HumanReviewDashboardFilters(
        limit=25,
        offset=25,
    )

    assert filters.next_page(has_next=False) is filters


def test_state_selection_and_refresh() -> None:
    state = HumanReviewDashboardState(filters=(HumanReviewDashboardFilters()))

    selected = state.select_review("review-1")

    refreshed = selected.refresh()

    assert selected.selected_review_id == "review-1"

    assert refreshed.refresh_token == 1


def test_state_serialization_roundtrip() -> None:
    state = dashboard_state_from_mapping(
        {
            "filters": {
                "statuses": [
                    "pending",
                ],
                "limit": 50,
                "offset": 100,
            },
            "selected_review_id": ("review-99"),
            "active_tab": "history",
            "refresh_token": 2,
        }
    )

    result = dashboard_state_to_dict(state)

    assert result["filters"]["offset"] == 100

    assert result["selected_review_id"] == "review-99"

    assert result["refresh_token"] == 2
