from __future__ import annotations

import os

from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from .models import ReceiptRecord


DEFAULT_RECEIPT_STORAGE_ROOT = Path(
    os.getenv(
        "REIMBURSEMENT_RECEIPT_STORAGE_ROOT",
        "data/reimbursements/receipts",
    )
)


def _scope_component(
    value: str,
) -> str:

    return sha256(
        str(value)
        .encode(
            "utf-8"
        )
    ).hexdigest()[:24]


def build_safe_filename(
    *,
    receipt_id: str,
    extension: str,
) -> str:

    allowed = {
        ".pdf",
        ".png",
        ".jpg",
    }

    if extension not in allowed:

        raise ValueError(
            "RECEIPT_EXTENSION_NOT_ALLOWED"
        )

    return (
        str(receipt_id)
        + extension
    )


class LocalReceiptStorage:

    def __init__(
        self,
        root: Path | str | None = None,
    ) -> None:

        self.root = Path(
            root
            or
            DEFAULT_RECEIPT_STORAGE_ROOT
        ).resolve()

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _destination(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
        safe_filename: str,
    ) -> Path:

        organization_dir = (
            _scope_component(
                tenant_id
            )
        )

        reimbursement_dir = (
            _scope_component(
                reimbursement_id
            )
        )

        destination = (
            self.root
            / organization_dir
            / reimbursement_dir
            / safe_filename
        ).resolve()

        try:

            destination.relative_to(
                self.root
            )

        except ValueError as exc:

            raise ValueError(
                "RECEIPT_STORAGE_ESCAPE_BLOCKED"
            ) from exc

        return destination

    def save(
        self,
        *,
        record: ReceiptRecord,
        content: bytes,
    ) -> str:

        destination = (
            self._destination(
                tenant_id=
                    record.tenant_id,

                reimbursement_id=
                    record.reimbursement_id,

                safe_filename=
                    record.safe_filename,
            )
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = (
            destination.parent
            /
            (
                "."
                + record.receipt_id
                + "."
                + uuid4().hex
                + ".tmp"
            )
        )

        try:

            with temporary.open(
                "xb"
            ) as handle:

                handle.write(
                    content
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )

            os.replace(
                temporary,
                destination,
            )

        finally:

            if temporary.exists():

                temporary.unlink(
                    missing_ok=True
                )

        return str(
            destination.relative_to(
                self.root
            )
        ).replace(
            "\\",
            "/",
        )

    def resolve(
        self,
        storage_reference: str,
    ) -> Path:

        reference = str(
            storage_reference or ""
        ).strip()

        if not reference:

            raise ValueError(
                "RECEIPT_STORAGE_REFERENCE_REQUIRED"
            )

        candidate = (
            self.root
            /
            reference
        ).resolve()

        try:

            candidate.relative_to(
                self.root
            )

        except ValueError as exc:

            raise ValueError(
                "RECEIPT_STORAGE_ESCAPE_BLOCKED"
            ) from exc

        return candidate

    def delete(
        self,
        storage_reference: str,
    ) -> bool:

        candidate = self.resolve(
            storage_reference
        )

        if not candidate.exists():

            return False

        candidate.unlink()

        return True