from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO

from PIL import (
    Image,
    UnidentifiedImageError,
)


MAX_RECEIPT_BYTES = (
    10 * 1024 * 1024
)

MAX_IMAGE_PIXELS = (
    25_000_000
)

Image.MAX_IMAGE_PIXELS = (
    MAX_IMAGE_PIXELS
)


ALLOWED_MIME_TYPES = {
    "application/pdf":
        ".pdf",

    "image/png":
        ".png",

    "image/jpeg":
        ".jpg",
}


class ReceiptValidationError(
    ValueError
):

    def __init__(
        self,
        code: str,
        *,
        status_code: int = 400,
    ) -> None:

        super().__init__(
            code
        )

        self.code = code
        self.status_code = status_code


@dataclass(frozen=True)
class ReceiptInspection:
    mime_type: str
    extension: str
    size_bytes: int
    sha256: str


def sanitize_original_filename(
    filename: str | None,
) -> str:

    value = str(
        filename or "receipt"
    )

    #
    # Compatível com caminhos Windows e Unix.
    #
    value = value.replace(
        "\\",
        "/",
    )

    value = value.split(
        "/"
    )[-1]

    value = "".join(
        char
        for char in value
        if (
            ord(char) >= 32
            and char != "\x7f"
        )
    ).strip()

    if not value:
        value = "receipt"

    return value[:255]


def _detect_mime_type(
    content: bytes,
) -> str:

    if content.startswith(
        b"%PDF-"
    ):
        return "application/pdf"

    if content.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        return "image/png"

    if content.startswith(
        b"\xff\xd8\xff"
    ):
        return "image/jpeg"

    raise ReceiptValidationError(
        "RECEIPT_FILE_TYPE_NOT_ALLOWED",
        status_code=415,
    )


def _validate_pdf(
    content: bytes,
) -> None:

    if len(content) < 12:

        raise ReceiptValidationError(
            "RECEIPT_PDF_INVALID",
            status_code=422,
        )

    #
    # Não executamos nem renderizamos o PDF.
    # Apenas validamos estrutura mínima.
    #
    tail = content[
        -8192:
    ]

    if b"%%EOF" not in tail:

        raise ReceiptValidationError(
            "RECEIPT_PDF_INVALID",
            status_code=422,
        )


def _validate_image(
    content: bytes,
    expected_mime_type: str,
) -> None:

    try:

        with Image.open(
            BytesIO(content)
        ) as image:

            image.verify()

            detected_format = str(
                image.format or ""
            ).upper()

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:

        raise ReceiptValidationError(
            "RECEIPT_IMAGE_INVALID",
            status_code=422,
        ) from exc

    expected_format = {
        "image/png":
            "PNG",

        "image/jpeg":
            "JPEG",
    }[
        expected_mime_type
    ]

    if (
        detected_format
        !=
        expected_format
    ):

        raise ReceiptValidationError(
            "RECEIPT_IMAGE_FORMAT_MISMATCH",
            status_code=422,
        )


def inspect_receipt(
    content: bytes,
) -> ReceiptInspection:

    if not isinstance(
        content,
        bytes,
    ):

        raise ReceiptValidationError(
            "RECEIPT_CONTENT_INVALID"
        )

    size = len(
        content
    )

    if size == 0:

        raise ReceiptValidationError(
            "RECEIPT_FILE_EMPTY",
            status_code=422,
        )

    if size > MAX_RECEIPT_BYTES:

        raise ReceiptValidationError(
            "RECEIPT_FILE_TOO_LARGE",
            status_code=413,
        )

    mime_type = (
        _detect_mime_type(
            content
        )
    )

    if (
        mime_type
        ==
        "application/pdf"
    ):

        _validate_pdf(
            content
        )

    else:

        _validate_image(
            content,
            mime_type,
        )

    digest = sha256(
        content
    ).hexdigest()

    return ReceiptInspection(
        mime_type=
            mime_type,

        extension=
            ALLOWED_MIME_TYPES[
                mime_type
            ],

        size_bytes=
            size,

        sha256=
            digest,
    )