from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


IDEMPOTENCY_KEY_PATTERN = (
    r"^[A-Za-z0-9._:-]{16,160}$"
)


class FinancialDiagnosisRecord(
    BaseModel
):
    """
    Conteúdo financeiro validado que poderá ser
    persistido.

    Não contém identidade, chave de idempotência
    nem campos controlados pelo banco.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
        validate_assignment=True,
    )

    nome: str = Field(
        min_length=1,
        max_length=120,
    )

    renda_mensal: float = Field(
        ge=0,
    )

    gastos_fixos: float = Field(
        ge=0,
    )

    gastos_variaveis: float = Field(
        ge=0,
    )

    dividas_mensais: float = Field(
        ge=0,
    )

    reserva_atual: float = Field(
        ge=0,
    )

    objetivo: str | None = Field(
        default=None,
        max_length=10_000,
    )

    idioma: str = Field(
        min_length=1,
        max_length=20,
    )

    moeda: str = Field(
        min_length=1,
        max_length=20,
    )

    simbolo_moeda: str = Field(
        min_length=1,
        max_length=10,
    )

    saldo_estimado: float

    comprometimento_renda_percentual: float = (
        Field(
            ge=0,
        )
    )

    meses_reserva_estimados: float = Field(
        ge=0,
    )

    score_financeiro: int = Field(
        ge=0,
        le=100,
    )

    nivel_risco: str = Field(
        min_length=1,
        max_length=30,
    )

    diagnostico: str = Field(
        min_length=1,
        max_length=50_000,
    )

    plano_30_dias: str = Field(
        min_length=1,
        max_length=50_000,
    )

    @field_validator(
        "idioma",
        mode="after",
    )
    @classmethod
    def normalizar_idioma(
        cls,
        value: str,
    ) -> str:
        return (
            value
            .strip()
            .lower()
            .replace(
                "-",
                "_",
            )
        )

    @field_validator(
        "moeda",
        mode="after",
    )
    @classmethod
    def normalizar_moeda(
        cls,
        value: str,
    ) -> str:
        return (
            value
            .strip()
            .upper()
        )

    def canonical_payload(
        self,
    ) -> dict[str, Any]:
        """
        Retorna somente os campos financeiros
        validados em formato serializável.
        """
        return self.model_dump(
            mode="json",
            exclude_none=False,
        )

    def request_fingerprint(
        self,
    ) -> str:
        """
        Gera SHA-256 determinístico do conteúdo
        validado que será persistido.
        """
        canonical_json = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        )

        return hashlib.sha256(
            canonical_json.encode(
                "utf-8"
            )
        ).hexdigest()


class TrustedDiagnosisPersistenceContext(
    BaseModel
):
    """
    Contexto interno proveniente de identidade
    confiável.

    Não deve ser criado a partir do body financeiro
    enviado pelo cliente ou de argumentos do LLM.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    usuario_id: str = Field(
        min_length=1,
        max_length=160,
    )

    idempotency_key: str = Field(
        min_length=16,
        max_length=160,
        pattern=IDEMPOTENCY_KEY_PATTERN,
    )


class FinancialDiagnosisPersistenceCommand(
    BaseModel
):
    """
    Comando interno completo entregue futuramente
    ao serviço de persistência.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    context: TrustedDiagnosisPersistenceContext
    diagnosis: FinancialDiagnosisRecord

    @property
    def request_fingerprint(
        self,
    ) -> str:
        return (
            self.diagnosis
            .request_fingerprint()
        )

    def to_repository_payload(
        self,
    ) -> dict[str, Any]:
        return {
            "usuario_id": (
                self.context.usuario_id
            ),
            "idempotency_key": (
                self.context.idempotency_key
            ),
            "request_fingerprint": (
                self.request_fingerprint
            ),
            **self.diagnosis.model_dump(
                mode="python",
                exclude_none=False,
            ),
        }


__all__ = [
    "FinancialDiagnosisPersistenceCommand",
    "FinancialDiagnosisRecord",
    "IDEMPOTENCY_KEY_PATTERN",
    "TrustedDiagnosisPersistenceContext",
]
