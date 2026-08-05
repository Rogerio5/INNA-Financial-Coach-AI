from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone

import src.observability.llm_notifications as notifications
import src.observability.resend_webhook as resend_webhook


class FakeMappingsResult:
    def __init__(self, *, first_value=None, all_values=None):
        self.first_value = first_value
        self.all_values = all_values or []

    def mappings(self):
        return self

    def first(self):
        return self.first_value

    def all(self):
        return self.all_values


class FakeConnection:
    def __init__(self, results):
        self.results = list(results)

    def execute(self, *args, **kwargs):
        if not self.results:
            raise AssertionError("Não existe resultado falso configurado.")

        return self.results.pop(0)

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False


class FakeEngine:
    def __init__(self, results):
        self.results = results
        self.disposed = False

    def connect(self):
        return FakeConnection(self.results)

    def begin(self):
        return FakeConnection(self.results)

    def dispose(self):
        self.disposed = True


def test_carregar_eventos_resend(monkeypatch):
    recebido_em = datetime(
        2026,
        7,
        15,
        17,
        0,
        tzinfo=timezone.utc,
    )

    eventos = [
        {
            "id": 2,
            "svix_id": "msg_evento_2",
            "evento_tipo": "email.sent",
            "provider_message_id": "email_123",
            "recebido_em": recebido_em,
            "processado": True,
            "processado_em": recebido_em,
            "resultado": "notificacao_atualizada",
            "erro_mensagem": None,
        },
        {
            "id": 1,
            "svix_id": "msg_evento_1",
            "evento_tipo": "email.delivered",
            "provider_message_id": "email_123",
            "recebido_em": recebido_em,
            "processado": True,
            "processado_em": recebido_em,
            "resultado": "notificacao_atualizada",
            "erro_mensagem": None,
        },
    ]

    engine = FakeEngine(
        [
            FakeMappingsResult(
                all_values=eventos,
            )
        ]
    )

    monkeypatch.setattr(
        resend_webhook,
        "inicializar_tabelas_resend_webhook",
        lambda: {"ok": True},
    )

    monkeypatch.setattr(
        resend_webhook,
        "_criar_engine",
        lambda: engine,
    )

    resultado = resend_webhook.carregar_eventos_resend(
        limite=100,
        horas=24,
    )

    assert resultado["ok"] is True
    assert resultado["total"] == 2
    assert resultado["eventos"][0]["evento_tipo"] == "email.sent"
    assert resultado["eventos"][1]["evento_tipo"] == "email.delivered"
    assert engine.disposed is True


def test_carregar_saude_integracoes(monkeypatch):
    agora = datetime(
        2026,
        7,
        15,
        17,
        0,
        tzinfo=timezone.utc,
    )

    row = {
        "ultimo_evento_tipo": "email.delivered",
        "ultimo_evento_recebido_em": agora,
        "ultimo_evento_processado": True,
        "ultimo_evento_resultado": ("notificacao_atualizada"),
        "ultimo_email_entregue_em": agora,
        "emails_entregues": 1,
        "emails_com_falha": 0,
        "eventos_webhook_24h": 2,
        "falhas_webhook_24h": 0,
    }

    engine = FakeEngine(
        [
            FakeMappingsResult(
                first_value=row,
            )
        ]
    )

    monkeypatch.setenv(
        "RESEND_API_KEY",
        "re_teste",
    )
    monkeypatch.setenv(
        "RESEND_WEBHOOK_SECRET",
        "whsec_teste",
    )
    monkeypatch.setenv(
        "LLM_ALERT_EMAIL_ENABLED",
        "true",
    )
    monkeypatch.setenv(
        "LLM_ALERT_EMAIL_TO",
        "teste@example.com",
    )

    monkeypatch.setattr(
        resend_webhook,
        "inicializar_tabelas_resend_webhook",
        lambda: {"ok": True},
    )

    monkeypatch.setattr(
        resend_webhook,
        "_criar_engine",
        lambda: engine,
    )

    resultado = resend_webhook.carregar_saude_integracoes()

    assert resultado["ok"] is True
    assert resultado["banco_conectado"] is True
    assert resultado["resend_configurado"] is True
    assert resultado["webhook_configurado"] is True
    assert resultado["email_alertas_habilitado"] is True
    assert resultado["emails_entregues"] == 1
    assert resultado["eventos_webhook_24h"] == 2
    assert resultado["falhas_webhook_24h"] == 0
    assert engine.disposed is True


def test_reenvio_bloqueia_email_entregue(
    monkeypatch,
):
    registro = {
        "notificacao_id": 4,
        "alerta_id": 7,
        "id": 7,
        "status": "enviado",
        "status_entrega": "entregue",
        "tentativas": 1,
        "provider_message_id": "email_123",
        "codigo": "chamadas_lentas",
        "titulo": ("Chamadas de LLM com alta latência"),
        "descricao": "Descrição técnica.",
        "categoria": "performance",
        "severidade": "alta",
        "alerta_status": "aberto",
        "valor_atual": 173028.445,
        "valor_limite": 30000,
        "unidade": "ms",
        "modelo": None,
        "operacao": None,
        "recomendacao": "Verificar latência.",
        "criado_em": datetime.now(timezone.utc),
    }

    engine = FakeEngine(
        [
            FakeMappingsResult(
                first_value=registro,
            )
        ]
    )

    monkeypatch.setattr(
        notifications,
        "inicializar_tabela_notificacoes",
        lambda: {"ok": True},
    )

    monkeypatch.setattr(
        notifications,
        "carregar_configuracao",
        lambda: {
            "habilitado": True,
            "destinatario": "teste@example.com",
        },
    )

    monkeypatch.setattr(
        notifications,
        "_criar_engine",
        lambda: engine,
    )

    resultado = notifications.reenviar_notificacao_email(
        notificacao_id=4,
        max_tentativas=3,
    )

    assert resultado["ok"] is False
    assert resultado["reenviado"] is False
    assert "entregues" in resultado["message"]
    assert engine.disposed is True
