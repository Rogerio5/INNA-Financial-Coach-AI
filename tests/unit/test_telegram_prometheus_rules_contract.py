from __future__ import annotations

import re
from pathlib import Path

import yaml


RECORDING_RULES_PATH = Path("prometheus/telegram_recording_rules.yml")

ALERT_RULES_PATH = Path("prometheus/telegram_alert_rules.yml")

KNOWN_SOURCE_METRICS = {
    "inna_telegram_operations_total",
    ("inna_telegram_operation_duration_seconds_bucket"),
    "inna_telegram_failures_total",
    "inna_telegram_worker_cycles_total",
    "inna_telegram_worker_updates_total",
    "inna_telegram_queue_operations_total",
    "inna_telegram_receipts_total",
}

FORBIDDEN_METRIC_TERMS = {
    "backlog",
    "dead_letter",
    "retry_total",
    "freshness_timestamp",
}

FORBIDDEN_PRIVATE_LABELS = {
    "chat_id",
    "telegram_user_id",
    "user_id",
    "update_id",
    "claim_token",
    "payload",
    "email",
    "username",
}


def load_yaml(
    path: Path,
) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8-sig"))


def iter_rules(
    payload: dict,
):
    for group in payload["groups"]:
        yield from group["rules"]


def test_rule_files_exist():
    assert RECORDING_RULES_PATH.is_file()
    assert ALERT_RULES_PATH.is_file()


def test_yaml_files_are_valid():
    for path in (
        RECORDING_RULES_PATH,
        ALERT_RULES_PATH,
    ):
        payload = load_yaml(path)

        assert isinstance(
            payload,
            dict,
        )

        assert payload["groups"]


def test_every_recording_rule_has_record_and_expression():
    payload = load_yaml(RECORDING_RULES_PATH)

    for rule in iter_rules(payload):
        assert rule["record"]
        assert rule["expr"]


def test_every_alert_has_required_fields():
    payload = load_yaml(ALERT_RULES_PATH)

    for rule in iter_rules(payload):
        assert rule["alert"]
        assert rule["expr"]
        assert rule["for"]

        assert rule["labels"]["severity"] in {
            "warning",
            "critical",
        }

        assert rule["labels"]["service"] == "inna"

        assert rule["labels"]["channel"] == "telegram"

        assert rule["annotations"]["summary"]

        assert rule["annotations"]["description"]

        assert rule["annotations"]["runbook"]


def test_alert_names_are_unique():
    payload = load_yaml(ALERT_RULES_PATH)

    names = [rule["alert"] for rule in iter_rules(payload)]

    assert len(names) == len(set(names))


def test_record_names_are_unique():
    payload = load_yaml(RECORDING_RULES_PATH)

    names = [rule["record"] for rule in iter_rules(payload)]

    assert len(names) == len(set(names))


def test_recording_rules_reference_known_sources():
    content = RECORDING_RULES_PATH.read_text(encoding="utf-8-sig")

    source_references = {metric for metric in KNOWN_SOURCE_METRICS if metric in content}

    assert {
        "inna_telegram_worker_updates_total",
        "inna_telegram_failures_total",
        ("inna_telegram_operation_duration_seconds_bucket"),
    }.issubset(source_references)


def test_rules_do_not_invent_absent_metrics():
    content = "\n".join(
        [
            RECORDING_RULES_PATH.read_text(encoding="utf-8-sig"),
            ALERT_RULES_PATH.read_text(encoding="utf-8-sig"),
        ]
    ).lower()

    for term in FORBIDDEN_METRIC_TERMS:
        assert term not in content


def test_rules_do_not_contain_private_labels():
    content = "\n".join(
        [
            RECORDING_RULES_PATH.read_text(encoding="utf-8-sig"),
            ALERT_RULES_PATH.read_text(encoding="utf-8-sig"),
        ]
    ).lower()

    for label in FORBIDDEN_PRIVATE_LABELS:
        assert label not in content


def test_alerts_only_reference_defined_recording_rules():
    recording_payload = load_yaml(RECORDING_RULES_PATH)

    alert_payload = load_yaml(ALERT_RULES_PATH)

    recording_names = {rule["record"] for rule in iter_rules(recording_payload)}

    alert_expressions = "\n".join(
        str(rule["expr"]) for rule in iter_rules(alert_payload)
    )

    references = set(
        re.findall(
            r"\binna:telegram_[a-zA-Z0-9_:]+",
            alert_expressions,
        )
    )

    assert references.issubset(recording_names)


def test_latency_thresholds_match_slo_policy():
    content = ALERT_RULES_PATH.read_text(encoding="utf-8-sig")

    assert "inna:telegram_operation_latency:p95_5m" in content

    assert "inna:telegram_operation_latency:p99_5m" in content

    assert "> 2" in content
    assert "> 5" in content


def test_burn_rate_thresholds_match_policy():
    content = ALERT_RULES_PATH.read_text(encoding="utf-8-sig")

    assert "/ 0.01" in content
    assert ">= 6" in content
    assert ">= 2" in content
