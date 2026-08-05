from __future__ import annotations

import pytest

from src.services.telegram_observability.contracts import (
    ALLOWED_ERROR_CATEGORIES,
)
from src.services.telegram_observability.productive_metrics import (
    normalize_metric_labels,
)


PROMETHEUS_SPECIFIC_ERROR_CATEGORIES = frozenset(
    {
        "dependency",
        "delivery",
        "encryption",
    }
)


def normalized_failure_category(
    category: object,
) -> str:
    labels = dict(
        normalize_metric_labels(
            metric_name=("inna_telegram_failures_total"),
            labels={
                "component": "worker",
                "operation": "process_update",
                "error_category": category,
            },
        )
    )

    return labels["error_category"]


@pytest.mark.parametrize(
    "category",
    sorted(ALLOWED_ERROR_CATEGORIES),
)
def test_domain_error_categories_are_preserved(
    category,
):
    assert normalized_failure_category(category) == category


@pytest.mark.parametrize(
    "category",
    sorted(PROMETHEUS_SPECIFIC_ERROR_CATEGORIES),
)
def test_prometheus_specific_categories_are_preserved(
    category,
):
    assert normalized_failure_category(category) == category


def test_none_error_category_is_preserved():
    labels = dict(
        normalize_metric_labels(
            metric_name=("inna_telegram_worker_updates_total"),
            labels={
                "outcome": "success",
                "error_category": None,
            },
        )
    )

    assert labels["error_category"] == "none"


@pytest.mark.parametrize(
    "category",
    [
        "processing_error",
        "database",
        "internal",
        "arbitrary_private_value",
    ],
)
def test_unknown_categories_are_normalized_safely(
    category,
):
    assert normalized_failure_category(category) == "unknown"
