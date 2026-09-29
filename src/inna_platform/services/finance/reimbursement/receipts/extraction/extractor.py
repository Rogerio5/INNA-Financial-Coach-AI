from __future__ import annotations

import re

from datetime import (
    date,
    time,
)

from io import BytesIO

from ..models import ReceiptRecord

from ...agent.guardrails import (
    BLOCKED_INSTRUCTION_PATTERNS,
)

from .models import (
    ReceiptExtractionRecord,
    ReceiptExtractionStatus,
)


EXTRACTOR_VERSION = "2b2"

MAX_EXTRACTED_TEXT_CHARS = 100_000


def _clean_text(
    value: str,
) -> tuple[str, bool]:

    text = str(
        value or ""
    )

    text = text.replace(
        "\x00",
        " ",
    )

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    truncated = (
        len(text)
        >
        MAX_EXTRACTED_TEXT_CHARS
    )

    if truncated:

        text = text[
            :MAX_EXTRACTED_TEXT_CHARS
        ]

    return (
        text.strip(),
        truncated,
    )


def _money_to_minor(
    value: str | None,
) -> int | None:

    if value is None:
        return None

    token = re.sub(
        r"[^0-9,.]",
        "",
        str(value),
    )

    if not token:
        return None

    try:

        if "," in token:

            integer_part, decimal_part = (
                token.rsplit(
                    ",",
                    1,
                )
            )

            integer_part = (
                integer_part
                .replace(
                    ".",
                    "",
                )
                .replace(
                    ",",
                    "",
                )
            )

            if len(
                decimal_part
            ) == 2:

                return (
                    int(
                        integer_part
                        or
                        "0"
                    )
                    * 100
                    +
                    int(
                        decimal_part
                    )
                )

            normalized = (
                integer_part
                +
                decimal_part
            )

            return (
                int(normalized)
                * 100
            )

        if "." in token:

            parts = token.split(
                "."
            )

            if (
                len(
                    parts[-1]
                )
                ==
                2
            ):

                integer_part = "".join(
                    parts[:-1]
                )

                return (
                    int(
                        integer_part
                        or
                        "0"
                    )
                    * 100
                    +
                    int(
                        parts[-1]
                    )
                )

            return (
                int(
                    "".join(
                        parts
                    )
                )
                * 100
            )

        return (
            int(token)
            * 100
        )

    except ValueError:

        return None


def _first_money(
    text: str,
    labels: str,
) -> int | None:

    pattern = (
        r"(?im)^\s*(?:"
        + labels
        + r")"
        r"\s*[:\-]?\s*"
        r"(?:R\$|US\$|USD|EUR|€|\$)?"
        r"\s*"
        r"([0-9][0-9.,]*)"
    )

    match = re.search(
        pattern,
        text,
    )

    if not match:
        return None

    return _money_to_minor(
        match.group(1)
    )


def _extract_currency(
    text: str,
) -> str | None:

    upper = text.upper()

    if (
        "R$" in text
        or
        "BRL" in upper
    ):
        return "BRL"

    if (
        "US$" in upper
        or
        "USD" in upper
    ):
        return "USD"

    if (
        "€" in text
        or
        "EUR" in upper
    ):
        return "EUR"

    return None


def _extract_date(
    text: str,
) -> date | None:

    iso = re.search(
        r"\b"
        r"(20\d{2})"
        r"-"
        r"(\d{2})"
        r"-"
        r"(\d{2})"
        r"\b",
        text,
    )

    if iso:

        try:

            return date(
                int(
                    iso.group(1)
                ),
                int(
                    iso.group(2)
                ),
                int(
                    iso.group(3)
                ),
            )

        except ValueError:
            pass

    brazil = re.search(
        r"\b"
        r"(\d{2})"
        r"/"
        r"(\d{2})"
        r"/"
        r"(20\d{2})"
        r"\b",
        text,
    )

    if brazil:

        try:

            return date(
                int(
                    brazil.group(3)
                ),
                int(
                    brazil.group(2)
                ),
                int(
                    brazil.group(1)
                ),
            )

        except ValueError:
            pass

    return None


def _extract_time(
    text: str,
) -> time | None:

    match = re.search(
        r"\b"
        r"([01]\d|2[0-3])"
        r":"
        r"([0-5]\d)"
        r"(?:"
        r":"
        r"([0-5]\d)"
        r")?"
        r"\b",
        text,
    )

    if not match:
        return None

    return time(
        hour=int(
            match.group(1)
        ),
        minute=int(
            match.group(2)
        ),
        second=int(
            match.group(3)
            or
            0
        ),
    )


def _extract_merchant(
    text: str,
) -> str | None:

    match = re.search(
        r"(?im)^\s*"
        r"(?:"
        r"estabelecimento"
        r"|merchant"
        r"|raz[aã]o\s+social"
        r")"
        r"\s*[:\-]\s*"
        r"(.{2,120})$",
        text,
    )

    if not match:
        return None

    return (
        match.group(1)
        .strip()
    )


def _extract_tax_id(
    text: str,
) -> str | None:

    match = re.search(
        r"(?i)\bCNPJ"
        r"\s*[:\-]?\s*"
        r"([0-9.\-/]{14,20})",
        text,
    )

    if not match:
        return None

    digits = re.sub(
        r"\D",
        "",
        match.group(1),
    )

    if len(
        digits
    ) != 14:
        return None

    return digits


def _extract_document_number(
    text: str,
) -> str | None:

    match = re.search(
        r"(?im)^\s*"
        r"(?:"
        r"NFC-e"
        r"|NF-e"
        r"|NF"
        r"|nota\s+fiscal"
        r")"
        r"\s*"
        r"(?:"
        r"n(?:[º°o.]|umero)?"
        r"\s*"
        r")?"
        r"[:#\-]?\s*"
        r"([A-Za-z0-9./\-]{2,50})",
        text,
    )

    if not match:
        return None

    return (
        match.group(1)
        .strip()
    )


def _extract_payment_method(
    text: str,
) -> str | None:

    normalized = (
        text
        .lower()
    )

    methods = (
        (
            "pix",
            "pix",
        ),
        (
            "cartão de crédito",
            "credit_card",
        ),
        (
            "cartao de credito",
            "credit_card",
        ),
        (
            "crédito",
            "credit_card",
        ),
        (
            "credito",
            "credit_card",
        ),
        (
            "cartão de débito",
            "debit_card",
        ),
        (
            "cartao de debito",
            "debit_card",
        ),
        (
            "débito",
            "debit_card",
        ),
        (
            "debito",
            "debit_card",
        ),
        (
            "dinheiro",
            "cash",
        ),
        (
            "cash",
            "cash",
        ),
    )

    for (
        pattern,
        result,
    ) in methods:

        if pattern in normalized:
            return result

    return None


def _contains_untrusted_instruction(
    text: str,
) -> bool:

    normalized = (
        text.lower()
    )

    return any(
        pattern
        in
        normalized

        for pattern
        in
        BLOCKED_INSTRUCTION_PATTERNS
    )


def _confidence(
    *,
    text_available: bool,
    merchant_name: str | None,
    merchant_tax_id: str | None,
    document_number: str | None,
    expense_date: date | None,
    currency: str | None,
    total_minor: int | None,
    payment_method: str | None,
) -> float:

    score = 0.0

    if text_available:
        score += 0.10

    if merchant_name:
        score += 0.10

    if merchant_tax_id:
        score += 0.10

    if document_number:
        score += 0.10

    if expense_date:
        score += 0.15

    if currency:
        score += 0.10

    if total_minor is not None:
        score += 0.25

    if payment_method:
        score += 0.10

    return round(
        min(
            score,
            1.0,
        ),
        4,
    )


def parse_receipt_text(
    *,
    receipt: ReceiptRecord,
    text: str,
) -> ReceiptExtractionRecord:

    cleaned_text, truncated = (
        _clean_text(
            text
        )
    )

    warnings = [
        "DOCUMENT_CONTENT_UNTRUSTED"
    ]

    if truncated:
        warnings.append(
            "DOCUMENT_TEXT_TRUNCATED"
        )

    suspicious_instruction = (
        _contains_untrusted_instruction(
            cleaned_text
        )
    )

    if suspicious_instruction:

        warnings.append(
            "UNTRUSTED_DOCUMENT_INSTRUCTION"
        )

    merchant_name = (
        _extract_merchant(
            cleaned_text
        )
    )

    merchant_tax_id = (
        _extract_tax_id(
            cleaned_text
        )
    )

    document_number = (
        _extract_document_number(
            cleaned_text
        )
    )

    expense_date = (
        _extract_date(
            cleaned_text
        )
    )

    expense_time = (
        _extract_time(
            cleaned_text
        )
    )

    currency = (
        _extract_currency(
            cleaned_text
        )
    )

    subtotal_minor = _first_money(
        cleaned_text,
        (
            r"subtotal"
            r"|sub\s*total"
        ),
    )

    tax_minor = _first_money(
        cleaned_text,
        (
            r"imposto"
            r"|tributos?"
            r"|tax"
        ),
    )

    total_minor = _first_money(
        cleaned_text,
        (
            r"valor\s+total"
            r"|total\s+a\s+pagar"
            r"|total"
            r"|amount\s+due"
        ),
    )

    payment_method = (
        _extract_payment_method(
            cleaned_text
        )
    )

    confidence = _confidence(
        text_available=
            bool(
                cleaned_text
            ),

        merchant_name=
            merchant_name,

        merchant_tax_id=
            merchant_tax_id,

        document_number=
            document_number,

        expense_date=
            expense_date,

        currency=
            currency,

        total_minor=
            total_minor,

        payment_method=
            payment_method,
    )

    found_any = any(
        (
            merchant_name,
            merchant_tax_id,
            document_number,
            expense_date,
            currency,
            subtotal_minor
            is not None,
            tax_minor
            is not None,
            total_minor
            is not None,
            payment_method,
        )
    )

    if not found_any:

        warnings.append(
            "STRUCTURED_FIELDS_NOT_FOUND"
        )

    status = (
        ReceiptExtractionStatus.EXTRACTED
        if (
            found_any
            and
            not suspicious_instruction
        )
        else
        ReceiptExtractionStatus.NEEDS_REVIEW
    )

    if suspicious_instruction:

        confidence = min(
            confidence,
            0.50,
        )

    return ReceiptExtractionRecord(
        tenant_id=
            receipt.tenant_id,

        reimbursement_id=
            receipt.reimbursement_id,

        receipt_id=
            receipt.receipt_id,

        extractor=
            "local-pdf-text",

        extractor_version=
            EXTRACTOR_VERSION,

        merchant_name=
            merchant_name,

        merchant_tax_id=
            merchant_tax_id,

        document_number=
            document_number,

        expense_date=
            expense_date,

        expense_time=
            expense_time,

        currency=
            currency,

        subtotal_minor=
            subtotal_minor,

        tax_minor=
            tax_minor,

        total_minor=
            total_minor,

        payment_method=
            payment_method,

        confidence=
            confidence,

        warnings=
            warnings,

        inconsistencies=[],

        extraction_status=
            status,

        document_content_trusted=
            False,

        human_review_required=
            True,
    )


def _read_pdf_text(
    content: bytes,
) -> str:

    from pypdf import PdfReader

    reader = PdfReader(
        BytesIO(
            content
        )
    )

    parts: list[str] = []

    for page in reader.pages:

        text = page.extract_text()

        if text:

            parts.append(
                text
            )

    return "\n".join(
        parts
    )


def extract_receipt_content(
    *,
    receipt: ReceiptRecord,
    content: bytes,
) -> ReceiptExtractionRecord:

    if (
        receipt.mime_type
        ==
        "application/pdf"
    ):

        try:

            text = _read_pdf_text(
                content
            )

        except Exception:

            return ReceiptExtractionRecord(
                tenant_id=
                    receipt.tenant_id,

                reimbursement_id=
                    receipt.reimbursement_id,

                receipt_id=
                    receipt.receipt_id,

                extractor=
                    "local-pdf-text",

                extractor_version=
                    EXTRACTOR_VERSION,

                confidence=
                    0.0,

                warnings=[
                    "DOCUMENT_CONTENT_UNTRUSTED",
                    "PDF_TEXT_EXTRACTION_FAILED",
                ],

                extraction_status=
                    ReceiptExtractionStatus.FAILED,

                document_content_trusted=
                    False,

                human_review_required=
                    True,
            )

        if not text.strip():

            return ReceiptExtractionRecord(
                tenant_id=
                    receipt.tenant_id,

                reimbursement_id=
                    receipt.reimbursement_id,

                receipt_id=
                    receipt.receipt_id,

                extractor=
                    "local-pdf-text",

                extractor_version=
                    EXTRACTOR_VERSION,

                confidence=
                    0.0,

                warnings=[
                    "DOCUMENT_CONTENT_UNTRUSTED",
                    "PDF_TEXT_NOT_AVAILABLE",
                    "VISION_REQUIRED",
                ],

                extraction_status=
                    ReceiptExtractionStatus.NEEDS_REVIEW,

                document_content_trusted=
                    False,

                human_review_required=
                    True,
            )

        return parse_receipt_text(
            receipt=
                receipt,

            text=
                text,
        )

    if receipt.mime_type in (
        "image/png",
        "image/jpeg",
    ):

        return ReceiptExtractionRecord(
            tenant_id=
                receipt.tenant_id,

            reimbursement_id=
                receipt.reimbursement_id,

            receipt_id=
                receipt.receipt_id,

            extractor=
                "local-image-deferred",

            extractor_version=
                EXTRACTOR_VERSION,

            confidence=
                0.0,

            warnings=[
                "DOCUMENT_CONTENT_UNTRUSTED",
                "IMAGE_REQUIRES_VISION",
            ],

            extraction_status=
                ReceiptExtractionStatus.NEEDS_REVIEW,

            document_content_trusted=
                False,

            human_review_required=
                True,
        )

    return ReceiptExtractionRecord(
        tenant_id=
            receipt.tenant_id,

        reimbursement_id=
            receipt.reimbursement_id,

        receipt_id=
            receipt.receipt_id,

        extractor=
            "local-unsupported",

        extractor_version=
            EXTRACTOR_VERSION,

        confidence=
            0.0,

        warnings=[
            "DOCUMENT_CONTENT_UNTRUSTED",
            "UNSUPPORTED_RECEIPT_MIME_TYPE",
        ],

        extraction_status=
            ReceiptExtractionStatus.FAILED,

        document_content_trusted=
            False,

        human_review_required=
            True,
    )