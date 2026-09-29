"""Local staging adapter; never mounted on a public route."""
import hashlib
import json
import os

import httpx

from src.inna_platform.services.finance.credit_execution import (
    ReconciliationRequired,
    run_analysis_pilot,
)


async def analyze_local(user_id, question, *, transport=None):
    if os.getenv("INNA_REAL_CREDIT_PILOT", "false").lower() != "true":
        raise RuntimeError("Real INNA credit pilot disabled")
    if not isinstance(question, str) or not 2 <= len(question.strip()) <= 2000:
        raise ValueError("Invalid pilot question")
    payload = {"pergunta": question.strip(), "idioma": "pt-BR", "top_k": 4}
    # Identical requests in this pilot are one operation, including after restart.
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    operation_id = "local-rag-pilot-v1:" + digest

    async def worker():
        try:
            async with httpx.AsyncClient(
                transport=transport, timeout=45, trust_env=False, follow_redirects=False
            ) as client:
                response = await client.post("http://127.0.0.1:8000/rag/ask", json=payload)
            # The server may have completed work even if its response is an error.
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict) or not isinstance(data.get("resposta"), str) or not data["resposta"].strip():
                raise ValueError("Missing INNA answer")
            if data.get("ok") is False or data.get("fallback") is True or data.get("error"):
                raise ValueError("INNA did not confirm a normal answer")
            return {"ok": True, "analysis": data}
        except Exception as exc:
            # Timeout/disconnection cannot prove that no remote work occurred.
            raise ReconciliationRequired("INNA result unconfirmed; inspect before resolving") from exc

    return await run_analysis_pilot(
        user_id, operation_id, worker, timeout_seconds=60, uncertain_on_interrupt=True
    )
