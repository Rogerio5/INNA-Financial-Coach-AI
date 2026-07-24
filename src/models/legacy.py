from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from src.database import Base


class DiagnosticoFinanceiro(Base):
    __tablename__ = "diagnosticos_financeiros"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(String(160), nullable=True)
    idempotency_key = Column(String(160), nullable=True)
    request_fingerprint = Column(String(64), nullable=True)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)

    nome = Column(String(120), nullable=False)
    renda_mensal = Column(Float, nullable=False)
    gastos_fixos = Column(Float, nullable=False)
    gastos_variaveis = Column(Float, nullable=False)
    dividas_mensais = Column(Float, nullable=False)
    reserva_atual = Column(Float, nullable=False)
    objetivo = Column(Text, nullable=True)

    idioma = Column(String(20), nullable=False, default="pt")
    moeda = Column(String(20), nullable=False, default="BRL")
    simbolo_moeda = Column(String(10), nullable=False, default="R$")

    saldo_estimado = Column(Float, nullable=False)
    comprometimento_renda_percentual = Column(Float, nullable=False)
    meses_reserva_estimados = Column(Float, nullable=False)
    score_financeiro = Column(Integer, nullable=False)
    nivel_risco = Column(String(30), nullable=False)

    diagnostico = Column(Text, nullable=False)
    plano_30_dias = Column(Text, nullable=False)


class FeedbackUsuario(Base):
    __tablename__ = "feedbacks_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)

    nome = Column(String(120), nullable=False)
    util = Column(String(10), nullable=False)
    comentario = Column(Text, nullable=True)
    score_financeiro = Column(Integer, nullable=False)
    nivel_risco = Column(String(30), nullable=False)
