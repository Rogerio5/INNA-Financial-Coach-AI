"""
Sabino.AI Finance FX Engine V1.

Responsabilidades:
- consultar taxa cambial real;
- preservar moeda de origem;
- cachear taxas;
- usar Decimal;
- nunca inventar taxa;
- nunca alterar valores persistidos.

Provider V1:
Frankfurter API v2.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from time import monotonic
from datetime import datetime, timezone
from typing import Any

import json
import os
import re

import httpx


# SABINO_FX_ENGINE_V1

DEFAULT_BASE_URL = (
    "https://api.frankfurter.dev/v2"
)

CURRENCY_CODE = re.compile(
    r"^[A-Z]{3}$"
)

_RATE_CACHE: dict[
    tuple[str, str],
    dict[str, Any],
] = {}


class FxValidationError(ValueError):
    """Dados de moeda/valor inválidos."""


class FxProviderError(RuntimeError):
    """Falha ao obter taxa real do provider."""


def _normalize_currency(
    value: str,
) -> str:

    currency = str(
        value or ""
    ).strip().upper()

    if not CURRENCY_CODE.fullmatch(
        currency
    ):
        raise FxValidationError(
            "Código de moeda inválido. "
            "Use ISO 4217 com 3 letras."
        )

    return currency


def _decimal(
    value: Any,
) -> Decimal:

    try:
        number = Decimal(
            str(value)
        )
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:

        raise FxValidationError(
            "Valor monetário inválido."
        ) from exc

    if not number.is_finite():
        raise FxValidationError(
            "Valor monetário deve ser finito."
        )

    return number


def _cache_seconds() -> int:

    raw = os.getenv(
        "SABINO_FX_CACHE_SECONDS",
        "21600",
    )

    try:
        value = int(raw)
    except ValueError:
        value = 21600

    return max(
        60,
        value,
    )


def _base_url() -> str:

    return (
        os.getenv(
            "SABINO_FX_BASE_URL",
            DEFAULT_BASE_URL,
        )
        .strip()
        .rstrip("/")
    )


def _decimal_text(
    value: Decimal,
) -> str:

    return format(
        value,
        "f",
    )


async def get_rate(
    base_currency: str,
    quote_currency: str,
) -> dict[str, Any]:

    base = _normalize_currency(
        base_currency
    )

    quote = _normalize_currency(
        quote_currency
    )


    # Mesma moeda:
    # nenhuma consulta externa necessária.
    if base == quote:

        return {
            "base": base,
            "quote": quote,
            "rate": Decimal("1"),
            "rate_date": None,
            "provider": "identity",
            "cached": False,
        }


    cache_key = (
        base,
        quote,
    )

    cached = _RATE_CACHE.get(
        cache_key
    )

    now = monotonic()


    if (
        cached
        and
        cached["expires_at"] > now
    ):

        record = dict(
            cached["record"]
        )

        record["cached"] = True

        return record


    url = (
        f"{_base_url()}"
        f"/rate/{base}/{quote}"
    )


    try:

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                8.0
            ),
            follow_redirects=True,
        ) as client:

            response = await client.get(
                url,
                headers={
                    "Accept":
                        "application/json",
                    "User-Agent":
                        "Sabino.AI-Finance/1.0",
                },
            )


    except httpx.HTTPError as exc:

        raise FxProviderError(
            "Não foi possível consultar "
            "a cotação neste momento."
        ) from exc


    if response.status_code in (
        400,
        404,
        422,
    ):

        raise FxValidationError(
            f"Par de moedas não suportado: "
            f"{base}/{quote}."
        )


    try:

        response.raise_for_status()

    except httpx.HTTPStatusError as exc:

        raise FxProviderError(
            "O serviço de câmbio retornou "
            "uma falha temporária."
        ) from exc


    try:

        payload = json.loads(
            response.text,
            parse_float=Decimal,
        )

        raw_rate = payload[
            "rate"
        ]

        rate = (
            raw_rate
            if isinstance(
                raw_rate,
                Decimal,
            )
            else
            Decimal(
                str(raw_rate)
            )
        )

    except (
        KeyError,
        InvalidOperation,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:

        raise FxProviderError(
            "Resposta de cotação inválida."
        ) from exc


    if (
        not rate.is_finite()
        or
        rate <= 0
    ):

        raise FxProviderError(
            "Taxa cambial inválida."
        )


    record = {
        "base": base,
        "quote": quote,
        "rate": rate,
        "rate_date": payload.get(
            "date"
        ),
        "provider": "frankfurter",
        "cached": False,
    }


    _RATE_CACHE[
        cache_key
    ] = {
        "expires_at":
            now
            +
            _cache_seconds(),
        "record":
            dict(record),
    }


    return record


async def rate_payload(
    base_currency: str,
    quote_currency: str,
) -> dict[str, Any]:

    result = await get_rate(
        base_currency,
        quote_currency,
    )

    return {
        "base_currency":
            result["base"],

        "quote_currency":
            result["quote"],

        "rate":
            _decimal_text(
                result["rate"]
            ),

        "rate_date":
            result["rate_date"],

        "provider":
            result["provider"],

        "cached":
            bool(
                result["cached"]
            ),

        "retrieved_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


async def convert_currency(
    amount: Any,
    from_currency: str,
    to_currency: str,
) -> dict[str, Any]:

    original_amount = _decimal(
        amount
    )

    result = await get_rate(
        from_currency,
        to_currency,
    )

    converted_amount = (
        original_amount
        *
        result["rate"]
    )


    return {
        "original": {
            "amount":
                _decimal_text(
                    original_amount
                ),

            "currency":
                result["base"],
        },

        "converted": {
            "amount":
                _decimal_text(
                    converted_amount
                ),

            "currency":
                result["quote"],
        },

        "exchange": {
            "rate":
                _decimal_text(
                    result["rate"]
                ),

            "rate_date":
                result["rate_date"],

            "provider":
                result["provider"],

            "cached":
                bool(
                    result["cached"]
                ),
        },

        "converted_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


def clear_rate_cache() -> None:

    _RATE_CACHE.clear()
