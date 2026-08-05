from __future__ import annotations

import json
from pathlib import Path

import yaml


DASHBOARD_PATH = Path("grafana/dashboards/telegram_operational_dashboard.json")

PROVISIONING_PATH = Path("grafana/provisioning/dashboards/telegram_dashboards.yml")

REQUIRED_RECORDING_RULES = {
    "inna:telegram_worker_updates:rate5m",
    "inna:telegram_worker_failures:rate5m",
    "inna:telegram_worker_error_ratio:rate5m",
    "inna:telegram_worker_conflict_ratio:rate5m",
    "inna:telegram_operation_latency:p95_5m",
    "inna:telegram_operation_latency:p99_5m",
    "inna:telegram_queue_failures:rate5m",
    "inna:telegram_receipt_failures:rate5m",
}

FORBIDDEN_PRIVATE_TERMS = {
    "chat_id",
    "telegram_user_id",
    "user_id",
    "update_id",
    "claim_token",
    "payload",
    "email",
    "username",
    "message_text",
}


def load_dashboard() -> dict:
    return json.loads(DASHBOARD_PATH.read_text(encoding="utf-8-sig"))


def panel_targets(
    dashboard: dict,
):
    for panel in dashboard["panels"]:
        for target in panel.get(
            "targets",
            [],
        ):
            yield target


def test_dashboard_files_exist():
    assert DASHBOARD_PATH.is_file()
    assert PROVISIONING_PATH.is_file()


def test_dashboard_json_is_valid():
    dashboard = load_dashboard()

    assert dashboard["uid"] == ("inna-telegram-operational")

    assert dashboard["title"] == ("INNA — Telegram Operational")

    assert dashboard["schemaVersion"] >= 39


def test_dashboard_panel_ids_are_unique():
    dashboard = load_dashboard()

    panel_ids = [panel["id"] for panel in dashboard["panels"]]

    assert len(panel_ids) == len(set(panel_ids))


def test_dashboard_has_operational_panels():
    dashboard = load_dashboard()

    titles = {panel["title"] for panel in dashboard["panels"]}

    expected = {
        "Worker updates",
        "Worker error ratio",
        "SLO burn rate",
        "Worker conflict ratio",
        "Worker throughput e falhas",
        "Latência p95 e p99",
        "Falhas por categoria",
        "Falhas de fila e receipts",
    }

    assert expected.issubset(titles)


def test_dashboard_references_required_rules():
    dashboard = load_dashboard()

    expressions = "\n".join(
        str(target.get("expr", "")) for target in panel_targets(dashboard)
    )

    missing = {
        record for record in REQUIRED_RECORDING_RULES if record not in expressions
    }

    assert not missing


def test_dashboard_uses_prometheus_datasource():
    dashboard = load_dashboard()

    for panel in dashboard["panels"]:
        datasource = panel["datasource"]

        assert datasource["type"] == ("prometheus")

        assert datasource["uid"] == ("${DS_PROMETHEUS}")


def test_dashboard_has_no_private_identifiers():
    content = DASHBOARD_PATH.read_text(encoding="utf-8-sig").lower()

    for term in FORBIDDEN_PRIVATE_TERMS:
        assert term not in content


def test_dashboard_has_safe_refresh_interval():
    dashboard = load_dashboard()

    assert dashboard["refresh"] in {
        "30s",
        "1m",
        "5m",
    }


def test_provisioning_yaml_is_valid():
    payload = yaml.safe_load(PROVISIONING_PATH.read_text(encoding="utf-8-sig"))

    assert payload["apiVersion"] == 1

    providers = payload["providers"]

    assert len(providers) == 1

    provider = providers[0]

    assert provider["type"] == "file"
    assert provider["folder"] == "INNA"

    assert provider["options"]["path"]
