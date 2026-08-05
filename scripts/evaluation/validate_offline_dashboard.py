"""Valida os dados usados pelo dashboard offline."""

from __future__ import annotations

from pathlib import Path

from src.evaluation.offline_dashboard import (
    build_overview,
    load_offline_dashboard_snapshot,
    mcp_scenario_rows,
    quality_gate_rows,
    security_rows,
)


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]

    snapshot = load_offline_dashboard_snapshot(
        project_root,
        strict=True,
    )

    overview = build_overview(snapshot)

    gate_rows = quality_gate_rows(snapshot)

    mcp_rows = mcp_scenario_rows(snapshot)

    offline_rows = security_rows(snapshot)

    print(f"DASHBOARD_DATASET_VERSION={overview['dataset_version']}")

    print(f"DASHBOARD_CASE_COUNT={overview['case_count']}")

    print(f"DASHBOARD_CATEGORY_COUNT={overview['category_count']}")

    print(f"DASHBOARD_QUALITY_GATE_PASSED={overview['quality_gate_passed']}")

    print(f"DASHBOARD_QUALITY_CHECK_COUNT={len(gate_rows)}")

    print(f"DASHBOARD_MCP_SCENARIO_COUNT={len(mcp_rows)}")

    for row in mcp_rows:
        print(
            "DASHBOARD_MCP_SCENARIO="
            f"{row['Cenário']} "
            f"STATUS={row['Status']} "
            f"ERROR_CODE={row['Código de erro']}"
        )

    security_passed = all(row["Aprovado"] for row in offline_rows)

    print(f"DASHBOARD_OFFLINE_CONTROLS_PASSED={security_passed}")

    if not overview["quality_gate_passed"]:
        raise RuntimeError("O dashboard recebeu um Quality Gate reprovado.")

    if len(mcp_rows) < 8:
        raise RuntimeError("O relatório MCP possui menos de oito cenários.")

    if not security_passed:
        raise RuntimeError("Uma garantia offline não foi confirmada.")

    print("OFFLINE_DASHBOARD_DATA_VALIDATION=OK")

    print("HTTP_REQUESTS_EXECUTED=False")

    print("DATABASE_CONNECTIONS_EXECUTED=False")

    print("LIVE_SERVICES_USED=False")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
