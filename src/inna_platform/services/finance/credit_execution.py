"""Internal staging orchestration; not connected to public INNA routes.

The caller supplies a stable server-owned operation ID bound to the request.
This pilot uses an illustrative fixed cost, never a browser-provided amount.
No result cache: replay reports accounting state and never calls the worker again.
A process crash or an accounting failure leaves reconciliation to an operator.
"""
import asyncio
import os

from src.inna_platform.services.finance import credit_wallet

PILOT_COST = 5


class ReconciliationRequired(RuntimeError):
    """Do not rerun the worker automatically; inspect the reservation first."""


async def run_analysis_pilot(user_id, operation_id, worker, *, timeout_seconds=30, uncertain_on_interrupt=False):
    if os.getenv("INNA_CREDIT_EXECUTION_PILOT", "false").lower() != "true":
        raise RuntimeError("Credit execution pilot disabled")
    if not 0 < timeout_seconds <= 120:
        raise ValueError("Invalid pilot timeout")
    # Deliberately synchronous accounting: no cancellation can abandon a thread
    # whose transaction may later commit. Pilot only; no public async endpoint.
    reservation = credit_wallet.start(
        user_id, operation_id, PILOT_COST, kind="usage", source="analysis"
    )
    if reservation["replayed"]:
        return {"accounting": reservation, "executed": False, "result": None}
    try:
        result = await asyncio.wait_for(worker(), timeout=timeout_seconds)
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise ValueError("Analysis did not return a successful result")
    except ReconciliationRequired:
        raise
    except (Exception, asyncio.CancelledError) as execution_error:
        if uncertain_on_interrupt and isinstance(execution_error, (TimeoutError, asyncio.CancelledError)):
            raise ReconciliationRequired("Remote execution interrupted; reconciliation required") from execution_error
        try:
            credit_wallet.finish(user_id, operation_id, success=False)
        except Exception as refund_error:
            raise ReconciliationRequired("Refund could not be confirmed") from refund_error
        raise
    try:
        accounting = credit_wallet.finish(user_id, operation_id, success=True)
    except Exception as completion_error:
        # Never refund a successful worker merely because final accounting failed.
        raise ReconciliationRequired("Analysis succeeded; accounting needs reconciliation") from completion_error
    return {"accounting": accounting, "executed": True, "result": result}
