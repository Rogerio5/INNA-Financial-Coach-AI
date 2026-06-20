from datetime import datetime
from pydantic import BaseModel, Field


class FinancialInput(BaseModel):
    nome: str = Field(default="Usuário Demo")
    renda_mensal: float = Field(ge=0)
    gastos_fixos: float = Field(ge=0)
    gastos_variaveis: float = Field(ge=0)
    dividas_mensais: float = Field(ge=0)
    reserva_atual: float = Field(ge=0)
    objetivo: str = Field(default="Organizar minha vida financeira")


class FinancialResponse(BaseModel):
    id: int | None = None
    nome: str
    saldo_estimado: float
    comprometimento_renda_percentual: float
    meses_reserva_estimados: float
    score_financeiro: int
    nivel_risco: str
    diagnostico: str
    plano_30_dias: str


class FeedbackInput(BaseModel):
    nome: str = Field(default="Usuário Demo")
    util: str = Field(default="Sim")
    comentario: str = Field(default="")
    score_financeiro: int = Field(ge=0, le=100)
    nivel_risco: str = Field(default="Medio")


class FeedbackResponse(BaseModel):
    status: str
    message: str


class DiagnosticoItem(BaseModel):
    id: int
    data_hora: datetime
    nome: str
    renda_mensal: float
    gastos_fixos: float
    gastos_variaveis: float
    dividas_mensais: float
    reserva_atual: float
    objetivo: str | None
    saldo_estimado: float
    comprometimento_renda_percentual: float
    meses_reserva_estimados: float
    score_financeiro: int
    nivel_risco: str
    diagnostico: str
    plano_30_dias: str


class FeedbackItem(BaseModel):
    id: int
    data_hora: datetime
    nome: str
    util: str
    comentario: str | None
    score_financeiro: int
    nivel_risco: str


class EmailRequest(BaseModel):
    email: str
