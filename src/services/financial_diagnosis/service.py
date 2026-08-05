from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from pydantic import ValidationError

from . import repository
from .contracts import (
    FinancialDiagnosisPersistenceCommand,
    FinancialDiagnosisRecord,
    TrustedDiagnosisPersistenceContext,
)


IDEMPOTENCY_ORIGIN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,31}$")


FORBIDDEN_DIAGNOSIS_FIELDS = frozenset(
    {
        "id",
        "data_hora",
        "usuario_id",
        "user_id",
        "idempotency_key",
        "request_fingerprint",
    }
)


class FinancialDiagnosisServiceError(RuntimeError):
    """
    Erro sanitizado da camada de aplicação.
    """


class FinancialDiagnosisValidationError(FinancialDiagnosisServiceError):
    """
    Os dados financeiros não formam um diagnóstico
    persistível válido.
    """


class TrustedDiagnosisIdentityError(FinancialDiagnosisServiceError):
    """
    Identidade confiável ou chave de idempotência
    ausente ou inválida.
    """


class FinancialDiagnosisIdempotencyConflictError(FinancialDiagnosisServiceError):
    """
    A chave já foi utilizada com conteúdo diferente.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class FinancialDiagnosisPersistenceOutcome:
    id: int

    status: Literal[
        "created",
        "existing",
    ]

    data_hora: datetime

    @property
    def created(
        self,
    ) -> bool:
        return self.status == "created"

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Resultado compacto apropriado para APIs,
        traces e integrações.

        Não inclui identidade, fingerprint ou dados
        financeiros completos.
        """
        return {
            "id": self.id,
            "status": self.status,
            "created": self.created,
            "data_hora": (self.data_hora.isoformat()),
        }


def gerar_chave_idempotencia(
    *,
    origem: str,
    request_id: str,
) -> str:
    """
    Gera uma chave segura a partir de um identificador
    de requisição.

    O request_id original não é armazenado na chave.
    """
    if not isinstance(
        origem,
        str,
    ):
        raise TrustedDiagnosisIdentityError("A origem da requisição é inválida.")

    normalized_origin = origem.strip().lower()

    if not IDEMPOTENCY_ORIGIN_PATTERN.fullmatch(normalized_origin):
        raise TrustedDiagnosisIdentityError("A origem da requisição é inválida.")

    if not isinstance(
        request_id,
        str,
    ):
        raise TrustedDiagnosisIdentityError("O identificador da requisição é inválido.")

    normalized_request_id = request_id.strip()

    if not (1 <= len(normalized_request_id) <= 512):
        raise TrustedDiagnosisIdentityError("O identificador da requisição é inválido.")

    digest = hashlib.sha256(
        (normalized_origin + "\0" + normalized_request_id).encode("utf-8")
    ).hexdigest()

    return f"diagnosis:{normalized_origin}:{digest[:40]}"


def _construir_contexto_confiavel(
    *,
    usuario_id_confiavel: str,
    idempotency_key: str,
) -> TrustedDiagnosisPersistenceContext:
    if not isinstance(
        usuario_id_confiavel,
        str,
    ):
        raise TrustedDiagnosisIdentityError("A identidade confiável é inválida.")

    if not isinstance(
        idempotency_key,
        str,
    ):
        raise TrustedDiagnosisIdentityError("A chave de idempotência é inválida.")

    try:
        return TrustedDiagnosisPersistenceContext(
            usuario_id=(usuario_id_confiavel),
            idempotency_key=(idempotency_key),
        )

    except ValidationError:
        raise TrustedDiagnosisIdentityError(
            "A identidade confiável ou a chave de idempotência é inválida."
        ) from None


def _construir_diagnostico(
    diagnostico: (FinancialDiagnosisRecord | Mapping[str, Any]),
) -> FinancialDiagnosisRecord:
    if isinstance(
        diagnostico,
        FinancialDiagnosisRecord,
    ):
        return diagnostico

    if not isinstance(
        diagnostico,
        Mapping,
    ):
        raise FinancialDiagnosisValidationError("O diagnóstico financeiro é inválido.")

    raw_data = dict(diagnostico)

    forbidden_present = FORBIDDEN_DIAGNOSIS_FIELDS.intersection(raw_data)

    if forbidden_present:
        raise FinancialDiagnosisValidationError(
            "O diagnóstico contém campos controlados pela aplicação."
        )

    try:
        return FinancialDiagnosisRecord.model_validate(raw_data)

    except ValidationError:
        raise FinancialDiagnosisValidationError(
            "O diagnóstico financeiro não passou pela validação."
        ) from None


def persistir_diagnostico_financeiro(
    *,
    usuario_id_confiavel: str,
    idempotency_key: str,
    diagnostico: (FinancialDiagnosisRecord | Mapping[str, Any]),
) -> FinancialDiagnosisPersistenceOutcome:
    """
    Valida e persiste um diagnóstico financeiro.

    A identidade e a chave são argumentos separados
    do conteúdo financeiro para impedir que sejam
    controladas pelo body, pelo modelo de linguagem
    ou pelo diagnóstico.
    """
    context = _construir_contexto_confiavel(
        usuario_id_confiavel=(usuario_id_confiavel),
        idempotency_key=(idempotency_key),
    )

    validated_diagnosis = _construir_diagnostico(diagnostico)

    command = FinancialDiagnosisPersistenceCommand(
        context=context,
        diagnosis=validated_diagnosis,
    )

    try:
        result = repository.salvar_diagnostico_financeiro(command)

    except repository.IdempotencyConflictError:
        raise (
            FinancialDiagnosisIdempotencyConflictError(
                "A chave de idempotência já foi utilizada com outro diagnóstico."
            )
        ) from None

    except repository.FinancialDiagnosisRepositoryError:
        raise FinancialDiagnosisServiceError(
            "Não foi possível persistir o diagnóstico financeiro."
        ) from None

    return FinancialDiagnosisPersistenceOutcome(
        id=result.id,
        status=result.status,
        data_hora=result.data_hora,
    )


__all__ = [
    "FORBIDDEN_DIAGNOSIS_FIELDS",
    "FinancialDiagnosisIdempotencyConflictError",
    "FinancialDiagnosisPersistenceOutcome",
    "FinancialDiagnosisServiceError",
    "FinancialDiagnosisValidationError",
    "TrustedDiagnosisIdentityError",
    "gerar_chave_idempotencia",
    "persistir_diagnostico_financeiro",
]
