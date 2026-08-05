from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


WORKFLOWS_DIRECTORY = Path(".github/workflows")
REPORT_DIRECTORY = Path("artifacts/security-compliance")
REPORT_PATH = REPORT_DIRECTORY / "workflow-policy-report.json"

TRUSTED_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/setup-go",
    "actions/upload-artifact",
}

FORBIDDEN_TRIGGERS = {
    "pull_request_target",
}

FORBIDDEN_PERMISSION_VALUES = {
    "write-all",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule_id: str
    file: str
    message: str


def workflow_files() -> tuple[Path, ...]:
    return tuple(
        sorted(
            [
                *WORKFLOWS_DIRECTORY.glob("*.yml"),
                *WORKFLOWS_DIRECTORY.glob("*.yaml"),
            ]
        )
    )


def has_top_level_block(content: str, key: str) -> bool:
    pattern = rf"(?m)^{re.escape(key)}:\s*(?:$|[^\n]+)"
    return re.search(pattern, content) is not None


def extract_actions(content: str) -> tuple[str, ...]:
    return tuple(
        match.group(1).strip()
        for match in re.finditer(
            r"(?m)^\s*uses:\s*([^\s#]+)",
            content,
        )
    )


def validate_workflow(path: Path) -> list[Finding]:
    content = path.read_text(encoding="utf-8")
    findings: list[Finding] = []

    required_blocks = (
        "permissions",
        "concurrency",
        "jobs",
    )

    for block in required_blocks:
        if not has_top_level_block(content, block):
            findings.append(
                Finding(
                    severity="error",
                    rule_id=f"required-{block}",
                    file=str(path),
                    message=(
                        f"O workflow precisa declarar o bloco "
                        f"de nível superior '{block}'."
                    ),
                )
            )

    if not re.search(
        r"(?ms)^permissions:\s*\n(?:^[ \t]+.*\n)*?"
        r"^[ \t]+contents:\s*read\s*$",
        content,
    ):
        findings.append(
            Finding(
                severity="error",
                rule_id="least-privilege-contents",
                file=str(path),
                message=("O workflow precisa declarar 'permissions: contents: read'."),
            )
        )

    if "timeout-minutes:" not in content:
        findings.append(
            Finding(
                severity="error",
                rule_id="job-timeout",
                file=str(path),
                message=("Ao menos um job não possui timeout explícito."),
            )
        )

    if "cancel-in-progress:" not in content:
        findings.append(
            Finding(
                severity="error",
                rule_id="concurrency-cancellation-policy",
                file=str(path),
                message=("O workflow precisa declarar 'cancel-in-progress'."),
            )
        )

    for trigger in FORBIDDEN_TRIGGERS:
        if re.search(
            rf"(?m)^\s*{re.escape(trigger)}:",
            content,
        ):
            findings.append(
                Finding(
                    severity="error",
                    rule_id="forbidden-trigger",
                    file=str(path),
                    message=(
                        f"O gatilho '{trigger}' não é permitido pela política da INNA."
                    ),
                )
            )

    for permission in FORBIDDEN_PERMISSION_VALUES:
        if re.search(
            rf"(?m)^\s*permissions:\s*{re.escape(permission)}\s*$",
            content,
        ):
            findings.append(
                Finding(
                    severity="error",
                    rule_id="forbidden-permission",
                    file=str(path),
                    message=(f"A permissão global '{permission}' não é permitida."),
                )
            )

    for action_reference in extract_actions(content):
        action_name, separator, version = action_reference.partition("@")

        if action_name not in TRUSTED_ACTIONS:
            findings.append(
                Finding(
                    severity="error",
                    rule_id="untrusted-action",
                    file=str(path),
                    message=(f"Action não autorizada: '{action_reference}'."),
                )
            )
            continue

        if not separator or not version:
            findings.append(
                Finding(
                    severity="error",
                    rule_id="action-without-version",
                    file=str(path),
                    message=(f"Action sem versão: '{action_reference}'."),
                )
            )
            continue

        if not re.fullmatch(r"[0-9a-f]{40}", version):
            findings.append(
                Finding(
                    severity="warning",
                    rule_id="action-not-pinned-by-sha",
                    file=str(path),
                    message=(f"'{action_reference}' usa tag em vez de SHA completo."),
                )
            )

    secret_patterns = (
        r"AIza[0-9A-Za-z_-]{20,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    )

    for pattern in secret_patterns:
        if re.search(pattern, content):
            findings.append(
                Finding(
                    severity="error",
                    rule_id="possible-hardcoded-secret",
                    file=str(path),
                    message=(
                        "Possível credencial real encontrada diretamente no workflow."
                    ),
                )
            )

    database_urls = re.findall(
        r"postgres(?:ql)?://[^$\s]+:[^$\s]+@[^\s]+",
        content,
    )

    for database_url in database_urls:
        is_local_test_database = bool(
            re.search(
                r"@(?:localhost|127\.0\.0\.1):",
                database_url,
            )
        )

        if is_local_test_database:
            continue

        findings.append(
            Finding(
                severity="error",
                rule_id="possible-hardcoded-database-secret",
                file=str(path),
                message=(
                    "Possível credencial PostgreSQL não local "
                    "encontrada diretamente no workflow."
                ),
            )
        )

    return findings


def main() -> int:
    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = workflow_files()

    if not paths:
        print("Nenhum workflow foi encontrado.")
        return 1

    findings = [finding for path in paths for finding in validate_workflow(path)]

    errors = [finding for finding in findings if finding.severity == "error"]

    warnings = [finding for finding in findings if finding.severity == "warning"]

    payload = {
        "schema_version": "1.0",
        "report_type": "workflow-security-policy",
        "workflow_count": len(paths),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "status": "failed" if errors else "passed",
        "findings": [asdict(finding) for finding in findings],
    }

    REPORT_PATH.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "WORKFLOW_SECURITY_POLICY "
        f"workflows={len(paths)} "
        f"errors={len(errors)} "
        f"warnings={len(warnings)}"
    )

    for finding in findings:
        print(
            f"[{finding.severity.upper()}] "
            f"{finding.rule_id} "
            f"{finding.file}: "
            f"{finding.message}"
        )

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
