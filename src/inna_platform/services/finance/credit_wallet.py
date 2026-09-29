"""Internal credit accounting. No public grant/debit endpoints.

Callers must supply authenticated identity and a stable server-side operation ID.
Grant only after independently verifying a payment or an authorized allocation.
Amounts are determined by trusted backend pricing, never browser input.
"""
import os
from contextlib import contextmanager

from src.database.connection import cursor_postgres


class CreditConflict(ValueError):
    pass


class InsufficientCredits(ValueError):
    pass


def enabled():
    return os.getenv("INNA_CREDITS_ENABLED", "false").lower() == "true"


def validate(user_id, operation_id, amount):
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("Missing authenticated identity")
    if not isinstance(operation_id, str) or not operation_id.strip() or len(operation_id) > 200:
        raise ValueError("Invalid operation ID")
    if type(amount) is not int or not 0 < amount <= 1_000_000_000:
        raise ValueError("Credits must be a positive bounded integer")


@contextmanager
def locked_wallet(user_id):
    if not enabled():
        raise RuntimeError("Credit accounting is not enabled")
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        cur.execute("INSERT INTO inna_credit_wallets(user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
        cur.execute("SELECT balance FROM inna_credit_wallets WHERE user_id=%s FOR UPDATE", (user_id,))
        wallet = cur.fetchone()
        yield cur, wallet["balance"]


def start(user_id, operation_id, amount, *, kind, source):
    validate(user_id, operation_id, amount)
    if kind not in {"grant", "usage"} or source not in {"purchased", "included", "analysis", "document", "report"}:
        raise ValueError("Invalid accounting category")
    if (kind == "grant") != (source in {"purchased", "included"}):
        raise ValueError("Invalid source for operation")
    with locked_wallet(user_id) as (cur, balance):
        cur.execute("SELECT * FROM inna_credit_operations WHERE user_id=%s AND operation_id=%s", (user_id, operation_id))
        prior = cur.fetchone()
        if prior:
            if (prior["amount"], prior["kind"], prior["source"]) != (amount, kind, source):
                raise CreditConflict("Operation ID reused with different values")
            return {"state": prior["state"], "balance": balance, "replayed": True}
        if kind == "usage" and balance < amount:
            raise InsufficientCredits("Insufficient credits")
        state, event, delta = ("completed", "grant", amount) if kind == "grant" else ("reserved", "reserve", -amount)
        cur.execute("INSERT INTO inna_credit_operations(user_id,operation_id,amount,kind,source,state) VALUES (%s,%s,%s,%s,%s,%s)", (user_id, operation_id, amount, kind, source, state))
        cur.execute("UPDATE inna_credit_wallets SET balance=balance+%s,updated_at=NOW() WHERE user_id=%s", (delta, user_id))
        cur.execute("INSERT INTO inna_credit_ledger(user_id,operation_id,event,delta) VALUES (%s,%s,%s,%s)", (user_id, operation_id, event, delta))
        return {"state": state, "balance": balance + delta, "replayed": False}


def finish(user_id, operation_id, *, success, review=None):
    if review is not None:
        _validate_review(review)
    validate(user_id, operation_id, 1)
    if type(success) is not bool:
        raise ValueError("success must be boolean")
    with locked_wallet(user_id) as (cur, balance):
        cur.execute("SELECT * FROM inna_credit_operations WHERE user_id=%s AND operation_id=%s", (user_id, operation_id))
        operation = cur.fetchone()
        if not operation or operation["kind"] != "usage":
            raise CreditConflict("Usage reservation not found")
        target = "completed" if success else "refunded"
        if review is not None:
            cur.execute("SELECT reviewer_id,decision,reason,evidence_ref FROM inna_credit_reviews WHERE user_id=%s AND operation_id=%s", (user_id, operation_id))
            previous_review = cur.fetchone()
            if previous_review:
                if dict(previous_review) != {**review, "decision": target}:
                    raise CreditConflict("Review already recorded with different evidence")
            elif operation["state"] != "reserved":
                raise CreditConflict("Only pending reservations may be reviewed")
        if operation["state"] == target:
            return {"state": target, "balance": balance, "replayed": True}
        if operation["state"] != "reserved":
            raise CreditConflict("Reservation already finalized")
        if review is not None:
            cur.execute("INSERT INTO inna_credit_reviews(user_id,operation_id,reviewer_id,decision,reason,evidence_ref) VALUES (%s,%s,%s,%s,%s,%s)", (user_id, operation_id, review["reviewer_id"], target, review["reason"], review["evidence_ref"]))
        delta = 0 if success else operation["amount"]
        cur.execute("UPDATE inna_credit_operations SET state=%s WHERE user_id=%s AND operation_id=%s", (target, user_id, operation_id))
        cur.execute("UPDATE inna_credit_wallets SET balance=balance+%s,updated_at=NOW() WHERE user_id=%s", (delta, user_id))
        cur.execute("INSERT INTO inna_credit_ledger(user_id,operation_id,event,delta) VALUES (%s,%s,%s,%s)", (user_id, operation_id, "complete" if success else "refund", delta))
        return {"state": target, "balance": balance + delta, "replayed": False}


def snapshot(user_id):
    validate(user_id, "read", 1)
    with cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        # One statement gives a consistent balance/history snapshot during writes.
        cur.execute("""SELECT COALESCE((SELECT balance FROM inna_credit_wallets WHERE user_id=%s),0) AS balance,
        COALESCE((SELECT json_agg(x) FROM (SELECT l.entry_id,l.event,l.delta,l.created_at,o.source
        FROM inna_credit_ledger l JOIN inna_credit_operations o USING(user_id,operation_id)
        WHERE l.user_id=%s ORDER BY l.entry_id DESC LIMIT 50) x),'[]'::json) AS history""", (user_id, user_id))
        return dict(cur.fetchone())


def pending_reservations(user_id, *, minimum_age_seconds=300):
    """Read-only triage. Age alone never authorizes refund or a new execution."""
    validate(user_id, "pending-read", 1)
    if type(minimum_age_seconds) is not int or minimum_age_seconds < 0:
        raise ValueError("Invalid reservation age")
    if not enabled():
        raise RuntimeError("Credit accounting is not enabled")
    with cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        cur.execute("""SELECT operation_id,amount,source,created_at FROM inna_credit_operations
        WHERE user_id=%s AND kind='usage' AND state='reserved'
        AND created_at <= NOW() - (%s * INTERVAL '1 second')
        ORDER BY created_at LIMIT 100""", (user_id, minimum_age_seconds))
        return [dict(row) for row in cur.fetchall()]


def _validate_review(review):
    if not isinstance(review, dict) or set(review) != {"reviewer_id", "reason", "evidence_ref"}:
        raise ValueError("Invalid review")
    allowed = {value.strip() for value in os.getenv("INNA_CREDIT_REVIEWERS", "").split(",") if value.strip()}
    if review["reviewer_id"] not in allowed:
        raise PermissionError("Reviewer is not authorized")
    if not isinstance(review["reason"], str) or not 10 <= len(review["reason"].strip()) <= 2000:
        raise ValueError("A review reason is required")
    if not isinstance(review["evidence_ref"], str) or not 3 <= len(review["evidence_ref"].strip()) <= 300:
        raise ValueError("An evidence reference is required")


def reconcile(user_id, operation_id, *, reviewer_id, success, reason, evidence_ref):
    """Internal only. Reviewer ID must come from trusted authentication, not input.

    No automatic age-based resolution. Requires verified evidence of the outcome.
    Audit, wallet, operation and ledger are committed in the same transaction.
    """
    return finish(user_id, operation_id, success=success, review={
        "reviewer_id": reviewer_id, "reason": reason, "evidence_ref": evidence_ref,
    })