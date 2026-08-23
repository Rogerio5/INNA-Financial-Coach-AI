from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Mapping


PROMETHEUS_CONTENT_TYPE = (
    "text/plain; version=0.0.4; charset=utf-8"
)

OPENMETRICS_CONTENT_TYPE = (
    "application/openmetrics-text; "
    "version=1.0.0; charset=utf-8"
)


_METRIC_NAME_PATTERN = re.compile(
    r"^[a-zA-Z_:][a-zA-Z0-9_:]*$"
)

_LABEL_NAME_PATTERN = re.compile(
    r"^[a-zA-Z_][a-zA-Z0-9_]*$"
)


class TelegramMetricsExportFormat(
    str,
    Enum,
):
    PROMETHEUS = "prometheus"
    OPENMETRICS = "openmetrics"


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramMetricsExport:
    body: str
    content_type: str
    format: TelegramMetricsExportFormat


class TelegramPrometheusExportError(
    ValueError
):
    """Erro de serialização das métricas Telegram."""


def _validate_metric_name(
    name: object,
) -> str:
    normalized = str(
        name
    ).strip()

    if not _METRIC_NAME_PATTERN.fullmatch(
        normalized
    ):
        raise TelegramPrometheusExportError(
            "Nome de métrica inválido: "
            f"{name!r}."
        )

    return normalized


def _validate_label_name(
    name: object,
) -> str:
    normalized = str(
        name
    ).strip()

    if not _LABEL_NAME_PATTERN.fullmatch(
        normalized
    ):
        raise TelegramPrometheusExportError(
            "Nome de label inválido: "
            f"{name!r}."
        )

    return normalized


def _escape_label_value(
    value: object,
) -> str:
    return (
        str(value)
        .replace(
            "\\",
            "\\\\",
        )
        .replace(
            "\n",
            "\\n",
        )
        .replace(
            '"',
            '\\"',
        )
    )


def _format_number(
    value: object,
) -> str:
    try:
        number = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TelegramPrometheusExportError(
            "Valor numérico inválido: "
            f"{value!r}."
        ) from exc

    if math.isnan(
        number
    ):
        return "NaN"

    if math.isinf(
        number
    ):
        return (
            "+Inf"
            if number > 0
            else "-Inf"
        )

    if number == 0:
        return "0"

    if number.is_integer():
        return str(
            int(number)
        )

    return format(
        number,
        ".15g",
    )


def _normalize_labels(
    labels: object,
) -> tuple[
    tuple[str, str],
    ...,
]:
    if labels is None:
        return ()

    if isinstance(
        labels,
        Mapping,
    ):
        raw_items = tuple(
            labels.items()
        )
    else:
        try:
            raw_items = tuple(
                labels  # type: ignore[arg-type]
            )
        except TypeError as exc:
            raise TelegramPrometheusExportError(
                "Labels devem ser um mapping "
                "ou uma sequência de pares."
            ) from exc

    normalized: list[
        tuple[str, str]
    ] = []

    seen_names: set[str] = set()

    for raw_item in raw_items:
        try:
            raw_name, raw_value = (
                raw_item
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TelegramPrometheusExportError(
                "Par de label inválido: "
                f"{raw_item!r}."
            ) from exc

        label_name = (
            _validate_label_name(
                raw_name
            )
        )

        if label_name in seen_names:
            raise TelegramPrometheusExportError(
                "Label duplicada: "
                f"{label_name!r}."
            )

        seen_names.add(
            label_name
        )

        normalized.append(
            (
                label_name,
                str(raw_value),
            )
        )

    normalized.sort(
        key=lambda item: item[0]
    )

    return tuple(
        normalized
    )


def _render_labels(
    labels: tuple[
        tuple[str, str],
        ...,
    ],
) -> str:
    if not labels:
        return ""

    rendered = ",".join(
        (
            f'{name}="'
            f'{_escape_label_value(value)}"'
        )
        for name, value in labels
    )

    return (
        "{"
        + rendered
        + "}"
    )


def _render_sample(
    metric_name: str,
    value: object,
    *,
    labels: object = None,
) -> str:
    normalized_name = (
        _validate_metric_name(
            metric_name
        )
    )

    normalized_labels = (
        _normalize_labels(
            labels
        )
    )

    return (
        normalized_name
        + _render_labels(
            normalized_labels
        )
        + " "
        + _format_number(
            value
        )
    )


def _read_histogram_field(
    histogram: object,
    name: str,
) -> object:
    if isinstance(
        histogram,
        Mapping,
    ):
        if name not in histogram:
            raise TelegramPrometheusExportError(
                "Histograma sem campo "
                f"{name!r}."
            )

        return histogram[
            name
        ]

    if not hasattr(
        histogram,
        name,
    ):
        raise TelegramPrometheusExportError(
            "Histograma sem atributo "
            f"{name!r}."
        )

    return getattr(
        histogram,
        name
    )


def _normalize_histogram_buckets(
    histogram: object,
) -> tuple[
    tuple[float, float],
    ...,
]:
    raw_buckets = (
        _read_histogram_field(
            histogram,
            "buckets",
        )
    )

    if isinstance(
        raw_buckets,
        Mapping,
    ):
        raw_items = tuple(
            raw_buckets.items()
        )
    else:
        try:
            raw_items = tuple(
                raw_buckets  # type: ignore[arg-type]
            )
        except TypeError as exc:
            raise TelegramPrometheusExportError(
                "Buckets de histograma inválidos."
            ) from exc

    normalized: list[
        tuple[float, float]
    ] = []

    for raw_item in raw_items:
        try:
            raw_bound, raw_count = (
                raw_item
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TelegramPrometheusExportError(
                "Bucket inválido: "
                f"{raw_item!r}."
            ) from exc

        try:
            bound = float(
                raw_bound
            )

            count = float(
                raw_count
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TelegramPrometheusExportError(
                "Bucket não numérico: "
                f"{raw_item!r}."
            ) from exc

        if math.isnan(
            bound
        ):
            raise TelegramPrometheusExportError(
                "Limite de bucket não pode ser NaN."
            )

        if count < 0:
            raise TelegramPrometheusExportError(
                "Contagem de bucket negativa."
            )

        normalized.append(
            (
                bound,
                count,
            )
        )

    normalized.sort(
        key=lambda item: item[0]
    )

    previous_count = 0.0

    for _, count in normalized:
        if count < previous_count:
            raise TelegramPrometheusExportError(
                "Buckets cumulativos fora de ordem."
            )

        previous_count = count

    return tuple(
        normalized
    )


def _render_counter_family(
    metric_name: str,
    series: Mapping[
        object,
        object,
    ],
) -> list[str]:
    lines = [
        f"# TYPE {metric_name} counter",
    ]

    ordered_series = sorted(
        series.items(),
        key=lambda item: (
            _normalize_labels(
                item[0]
            )
        ),
    )

    for labels, value in ordered_series:
        lines.append(
            _render_sample(
                metric_name,
                value,
                labels=labels,
            )
        )

    return lines


def _render_histogram_family(
    metric_name: str,
    series: Mapping[
        object,
        object,
    ],
) -> list[str]:
    lines = [
        f"# TYPE {metric_name} histogram",
    ]

    ordered_series = sorted(
        series.items(),
        key=lambda item: (
            _normalize_labels(
                item[0]
            )
        ),
    )

    for labels, histogram in ordered_series:
        normalized_labels = (
            _normalize_labels(
                labels
            )
        )

        count = float(
            _read_histogram_field(
                histogram,
                "count",
            )
        )

        total_sum = float(
            _read_histogram_field(
                histogram,
                "sum",
            )
        )

        if count < 0:
            raise TelegramPrometheusExportError(
                "Contagem de histograma negativa."
            )

        buckets = (
            _normalize_histogram_buckets(
                histogram
            )
        )

        has_positive_infinity = False

        for upper_bound, bucket_count in buckets:
            if (
                math.isinf(
                    upper_bound
                )
                and upper_bound > 0
            ):
                has_positive_infinity = True

            bucket_labels = (
                normalized_labels
                + (
                    (
                        "le",
                        _format_number(
                            upper_bound
                        ),
                    ),
                )
            )

            lines.append(
                _render_sample(
                    metric_name
                    + "_bucket",
                    bucket_count,
                    labels=bucket_labels,
                )
            )

        if not has_positive_infinity:
            bucket_labels = (
                normalized_labels
                + (
                    (
                        "le",
                        "+Inf",
                    ),
                )
            )

            lines.append(
                _render_sample(
                    metric_name
                    + "_bucket",
                    count,
                    labels=bucket_labels,
                )
            )

        lines.append(
            _render_sample(
                metric_name
                + "_sum",
                total_sum,
                labels=normalized_labels,
            )
        )

        lines.append(
            _render_sample(
                metric_name
                + "_count",
                count,
                labels=normalized_labels,
            )
        )

    return lines


class TelegramPrometheusMetricsExporter:
    def export(
        self,
        snapshot: object,
        *,
        format: (
            TelegramMetricsExportFormat
            | str
        ) = (
            TelegramMetricsExportFormat
            .PROMETHEUS
        ),
    ) -> TelegramMetricsExport:
        try:
            resolved_format = (
                TelegramMetricsExportFormat(
                    format
                )
            )
        except ValueError as exc:
            raise TelegramPrometheusExportError(
                "Formato não suportado: "
                f"{format!r}."
            ) from exc

        counters = getattr(
            snapshot,
            "counters",
            None,
        )

        histograms = getattr(
            snapshot,
            "histograms",
            None,
        )

        if not isinstance(
            counters,
            Mapping,
        ):
            raise TelegramPrometheusExportError(
                "Snapshot sem counters válidos."
            )

        if not isinstance(
            histograms,
            Mapping,
        ):
            raise TelegramPrometheusExportError(
                "Snapshot sem histograms válidos."
            )

        lines: list[str] = []

        for raw_metric_name in sorted(
            counters
        ):
            metric_name = (
                _validate_metric_name(
                    raw_metric_name
                )
            )

            series = counters[
                raw_metric_name
            ]

            if not isinstance(
                series,
                Mapping,
            ):
                raise TelegramPrometheusExportError(
                    "Séries de contador inválidas para "
                    f"{metric_name!r}."
                )

            lines.extend(
                _render_counter_family(
                    metric_name,
                    series,
                )
            )

        for raw_metric_name in sorted(
            histograms
        ):
            metric_name = (
                _validate_metric_name(
                    raw_metric_name
                )
            )

            series = histograms[
                raw_metric_name
            ]

            if not isinstance(
                series,
                Mapping,
            ):
                raise TelegramPrometheusExportError(
                    "Séries de histograma inválidas para "
                    f"{metric_name!r}."
                )

            lines.extend(
                _render_histogram_family(
                    metric_name,
                    series,
                )
            )

        if (
            resolved_format
            is TelegramMetricsExportFormat
            .OPENMETRICS
        ):
            lines.append(
                "# EOF"
            )

            content_type = (
                OPENMETRICS_CONTENT_TYPE
            )
        else:
            content_type = (
                PROMETHEUS_CONTENT_TYPE
            )

        body = (
            "\n".join(
                lines
            )
            + (
                "\n"
                if lines
                else ""
            )
        )

        return TelegramMetricsExport(
            body=body,
            content_type=content_type,
            format=resolved_format,
        )


class SafeTelegramPrometheusMetricsExporter:
    def __init__(
        self,
        delegate: (
            TelegramPrometheusMetricsExporter
        ),
    ) -> None:
        self._delegate = delegate

    def export(
        self,
        snapshot: object,
        *,
        format: (
            TelegramMetricsExportFormat
            | str
        ) = (
            TelegramMetricsExportFormat
            .PROMETHEUS
        ),
    ) -> TelegramMetricsExport:
        try:
            return self._delegate.export(
                snapshot,
                format=format,
            )
        except Exception:
            try:
                resolved_format = (
                    TelegramMetricsExportFormat(
                        format
                    )
                )
            except ValueError:
                resolved_format = (
                    TelegramMetricsExportFormat
                    .PROMETHEUS
                )

            if (
                resolved_format
                is TelegramMetricsExportFormat
                .OPENMETRICS
            ):
                return TelegramMetricsExport(
                    body="# EOF\n",
                    content_type=(
                        OPENMETRICS_CONTENT_TYPE
                    ),
                    format=resolved_format,
                )

            return TelegramMetricsExport(
                body="",
                content_type=(
                    PROMETHEUS_CONTENT_TYPE
                ),
                format=resolved_format,
            )


__all__ = [
    "OPENMETRICS_CONTENT_TYPE",
    "PROMETHEUS_CONTENT_TYPE",
    "SafeTelegramPrometheusMetricsExporter",
    "TelegramMetricsExport",
    "TelegramMetricsExportFormat",
    "TelegramPrometheusExportError",
    "TelegramPrometheusMetricsExporter",
]
