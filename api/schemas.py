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
    nome: str
    saldo_estimado: float
    comprometimento_renda_percentual: float
    meses_reserva_estimados: float
    score_financeiro: int
    nivel_risco: str
    diagnostico: str
    plano_30_dias: str
