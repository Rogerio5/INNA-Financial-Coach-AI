from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GuardrailResult:
    allowed: bool
    flags: list[str] = field(default_factory=list)


BLOCKED_INSTRUCTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "execute command",
    "run powershell",
    "run shell",
)


def validate_reimbursement_input(
    *,
    description: str,
    amount: int,
    currency: str,
) -> GuardrailResult:

    flags: list[str] = []

    if amount <= 0:
        flags.append(
            "INVALID_AMOUNT"
        )

    if len(currency.strip()) != 3:
        flags.append(
            "INVALID_CURRENCY"
        )

    normalized = (
        description
        .lower()
        .strip()
    )

    for pattern in BLOCKED_INSTRUCTION_PATTERNS:
        if pattern in normalized:
            flags.append(
                "UNTRUSTED_INSTRUCTION_DETECTED"
            )
            break

    return GuardrailResult(
        allowed=not flags,
        flags=flags,
    )