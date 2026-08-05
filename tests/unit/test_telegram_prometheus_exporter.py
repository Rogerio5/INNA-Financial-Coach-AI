from __future__ import annotations

from types import MappingProxyType
from types import SimpleNamespace

import pytest

from src.services.telegram_observability import (
    InMemoryTelegramProductiveMetrics,
    OPENMETRICS_CONTENT_TYPE,
    PROMETHEUS_CONTENT_TYPE,
    SafeTelegramPrometheusMetricsExporter,
    TelegramMetricsExportFormat,
    TelegramPrometheusExportError,
    TelegramPrometheusMetricsExporter,
)


def populated_registry():
    registry = InMemoryTelegramProductiveMetrics()

    registry.increment(
        "inna_telegram_operations_total",
        labels={
            "component": "bridge",
            "operation": "save_session",
            "outcome": "success",
            "error_category": "none",
        },
    )

    registry.observe(
        ("inna_telegram_operation_duration_seconds"),
        0.25,
        labels={
            "component": "bridge",
            "operation": "save_session",
            "outcome": "success",
        },
    )

    return registry


def test_exports_counter_family():
    exported = TelegramPrometheusMetricsExporter().export(
        populated_registry().snapshot()
    )

    assert exported.content_type == PROMETHEUS_CONTENT_TYPE

    assert exported.format is TelegramMetricsExportFormat.PROMETHEUS

    assert "# TYPE inna_telegram_operations_total counter" in exported.body

    assert "inna_telegram_operations_total{" in exported.body

    assert 'component="bridge"' in exported.body

    assert 'error_category="none"' in exported.body


def test_exports_histogram_family():
    body = (
        TelegramPrometheusMetricsExporter().export(populated_registry().snapshot()).body
    )

    metric_name = "inna_telegram_operation_duration_seconds"

    assert f"# TYPE {metric_name} histogram" in body

    assert f"{metric_name}_bucket" in body

    assert f"{metric_name}_sum" in body

    assert f"{metric_name}_count" in body

    assert 'le="+Inf"' in body


def test_openmetrics_ends_with_eof():
    exported = TelegramPrometheusMetricsExporter().export(
        populated_registry().snapshot(),
        format="openmetrics",
    )

    assert exported.content_type == OPENMETRICS_CONTENT_TYPE

    assert exported.format is TelegramMetricsExportFormat.OPENMETRICS

    assert exported.body.endswith("# EOF\n")


def test_prometheus_does_not_end_with_eof():
    exported = TelegramPrometheusMetricsExporter().export(
        populated_registry().snapshot(),
        format="prometheus",
    )

    assert not exported.body.endswith("# EOF\n")


def test_output_is_deterministic():
    registry = populated_registry()

    exporter = TelegramPrometheusMetricsExporter()

    first = exporter.export(
        registry.snapshot(),
        format="openmetrics",
    )

    second = exporter.export(
        registry.snapshot(),
        format="openmetrics",
    )

    assert first == second


def test_export_does_not_mutate_snapshot():
    registry = populated_registry()

    snapshot = registry.snapshot()

    counters_before = repr(snapshot.counters)

    histograms_before = repr(snapshot.histograms)

    (TelegramPrometheusMetricsExporter().export(snapshot))

    assert repr(snapshot.counters) == counters_before

    assert repr(snapshot.histograms) == histograms_before


def test_label_order_is_stable():
    snapshot = SimpleNamespace(
        counters={
            "example_total": {
                (
                    ("z_label", "z"),
                    ("a_label", "a"),
                ): 1.0,
            },
        },
        histograms={},
    )

    body = TelegramPrometheusMetricsExporter().export(snapshot).body

    assert 'example_total{a_label="a",z_label="z"} 1' in body


def test_series_order_is_stable():
    snapshot = SimpleNamespace(
        counters={
            "example_total": {
                (("outcome", "z"),): 2.0,
                (("outcome", "a"),): 1.0,
            },
        },
        histograms={},
    )

    lines = TelegramPrometheusMetricsExporter().export(snapshot).body.splitlines()

    sample_lines = [line for line in lines if line.startswith("example_total{")]

    assert sample_lines == [
        'example_total{outcome="a"} 1',
        'example_total{outcome="z"} 2',
    ]


def test_metric_families_are_sorted():
    snapshot = SimpleNamespace(
        counters={
            "z_metric_total": {
                (): 1.0,
            },
            "a_metric_total": {
                (): 2.0,
            },
        },
        histograms={},
    )

    body = TelegramPrometheusMetricsExporter().export(snapshot).body

    assert body.index("# TYPE a_metric_total") < body.index("# TYPE z_metric_total")


def test_escapes_label_values():
    snapshot = SimpleNamespace(
        counters={
            "example_total": {
                (
                    (
                        "value",
                        'line1\n"quoted"\\end',
                    ),
                ): 1.0,
            },
        },
        histograms={},
    )

    body = TelegramPrometheusMetricsExporter().export(snapshot).body

    assert 'value="line1\\n\\"quoted\\"\\\\end"' in body


@pytest.mark.parametrize(
    (
        "raw_value",
        "expected",
    ),
    [
        (
            float("nan"),
            "NaN",
        ),
        (
            float("inf"),
            "+Inf",
        ),
        (
            float("-inf"),
            "-Inf",
        ),
        (
            0,
            "0",
        ),
        (
            2.0,
            "2",
        ),
        (
            0.125,
            "0.125",
        ),
    ],
)
def test_formats_special_numbers(
    raw_value,
    expected,
):
    snapshot = SimpleNamespace(
        counters={
            "example_total": {
                (): raw_value,
            },
        },
        histograms={},
    )

    body = TelegramPrometheusMetricsExporter().export(snapshot).body

    assert f"example_total {expected}" in body


@pytest.mark.parametrize(
    "metric_name",
    [
        "invalid metric",
        "1_invalid",
        "invalid-name",
        "",
    ],
)
def test_rejects_invalid_metric_names(
    metric_name,
):
    snapshot = SimpleNamespace(
        counters={
            metric_name: {
                (): 1.0,
            },
        },
        histograms={},
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


@pytest.mark.parametrize(
    "label_name",
    [
        "invalid label",
        "1_invalid",
        "invalid-name",
        "",
    ],
)
def test_rejects_invalid_label_names(
    label_name,
):
    snapshot = SimpleNamespace(
        counters={
            "example_total": {
                (
                    (
                        label_name,
                        "value",
                    ),
                ): 1.0,
            },
        },
        histograms={},
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_duplicate_label_names():
    snapshot = SimpleNamespace(
        counters={
            "example_total": {
                (
                    ("outcome", "success"),
                    ("outcome", "error"),
                ): 1.0,
            },
        },
        histograms={},
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_invalid_snapshot():
    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(SimpleNamespace()))


def test_rejects_invalid_counter_series():
    snapshot = SimpleNamespace(
        counters={
            "example_total": [],
        },
        histograms={},
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_invalid_histogram_series():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": [],
        },
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_histogram_without_buckets():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": {
                (): SimpleNamespace(
                    count=1,
                    sum=0.5,
                ),
            },
        },
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_negative_histogram_count():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": {
                (): SimpleNamespace(
                    count=-1,
                    sum=0.5,
                    buckets={
                        1.0: 1,
                    },
                ),
            },
        },
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_negative_bucket_count():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": {
                (): SimpleNamespace(
                    count=1,
                    sum=0.5,
                    buckets={
                        1.0: -1,
                    },
                ),
            },
        },
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_rejects_non_cumulative_buckets():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": {
                (): SimpleNamespace(
                    count=2,
                    sum=0.5,
                    buckets={
                        0.5: 2,
                        1.0: 1,
                    },
                ),
            },
        },
    )

    with pytest.raises(TelegramPrometheusExportError):
        (TelegramPrometheusMetricsExporter().export(snapshot))


def test_adds_positive_infinity_bucket():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": {
                (): SimpleNamespace(
                    count=2,
                    sum=0.75,
                    buckets={
                        0.5: 1,
                        1.0: 2,
                    },
                ),
            },
        },
    )

    body = TelegramPrometheusMetricsExporter().export(snapshot).body

    assert 'example_seconds_bucket{le="+Inf"} 2' in body


def test_does_not_duplicate_existing_infinity_bucket():
    snapshot = SimpleNamespace(
        counters={},
        histograms={
            "example_seconds": {
                (): SimpleNamespace(
                    count=2,
                    sum=0.75,
                    buckets={
                        0.5: 1,
                        float("inf"): 2,
                    },
                ),
            },
        },
    )

    body = TelegramPrometheusMetricsExporter().export(snapshot).body

    assert body.count('example_seconds_bucket{le="+Inf"}') == 1


def test_empty_prometheus_snapshot_is_valid():
    snapshot = SimpleNamespace(
        counters=MappingProxyType({}),
        histograms=MappingProxyType({}),
    )

    exported = TelegramPrometheusMetricsExporter().export(snapshot)

    assert exported.body == ""


def test_empty_openmetrics_snapshot_has_eof():
    snapshot = SimpleNamespace(
        counters=MappingProxyType({}),
        histograms=MappingProxyType({}),
    )

    exported = TelegramPrometheusMetricsExporter().export(
        snapshot,
        format="openmetrics",
    )

    assert exported.body == "# EOF\n"


def test_rejects_unknown_format():
    with pytest.raises(TelegramPrometheusExportError):
        (
            TelegramPrometheusMetricsExporter().export(
                populated_registry().snapshot(),
                format="private-format",
            )
        )


def test_safe_exporter_returns_empty_prometheus():
    exporter = SafeTelegramPrometheusMetricsExporter(
        TelegramPrometheusMetricsExporter()
    )

    exported = exporter.export(SimpleNamespace())

    assert exported.body == ""

    assert exported.content_type == PROMETHEUS_CONTENT_TYPE


def test_safe_exporter_returns_valid_openmetrics():
    exporter = SafeTelegramPrometheusMetricsExporter(
        TelegramPrometheusMetricsExporter()
    )

    exported = exporter.export(
        SimpleNamespace(),
        format="openmetrics",
    )

    assert exported.body == "# EOF\n"

    assert exported.content_type == OPENMETRICS_CONTENT_TYPE


def test_private_values_are_not_created_by_exporter():
    registry = InMemoryTelegramProductiveMetrics()

    for index in range(100):
        registry.increment(
            "inna_telegram_worker_updates_total",
            labels={
                "outcome": (f"private-outcome-{index}"),
                "error_category": (f"private-error-{index}"),
            },
        )

    body = TelegramPrometheusMetricsExporter().export(registry.snapshot()).body

    assert "private-outcome" not in body
    assert "private-error" not in body

    assert 'outcome="unknown"' in body

    assert 'error_category="unknown"' in body


def test_real_snapshot_mappingproxy_is_supported():
    snapshot = populated_registry().snapshot()

    assert isinstance(
        snapshot.counters,
        MappingProxyType,
    )

    assert isinstance(
        snapshot.histograms,
        MappingProxyType,
    )

    exported = TelegramPrometheusMetricsExporter().export(snapshot)

    assert exported.body
