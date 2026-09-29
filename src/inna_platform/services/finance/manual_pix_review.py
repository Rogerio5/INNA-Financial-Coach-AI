"""Manual bank review; audit, credits and access commit in one transaction."""

from uuid import uuid4

from src.database.connection import cursor_postgres
from src.inna_platform.services.finance import credit_wallet


class PixConflict(ValueError):
    pass


def assert_reviewer(cur, reviewer_id):
    cur.execute(
        """SELECT 1 FROM inna_pix_reviewers r JOIN inna_auth_users u USING(user_id)
                   WHERE r.user_id=%s AND u.active=TRUE""",
        (reviewer_id,),
    )
    if not cur.fetchone():
        raise PermissionError("Conta sem permissão para conferir Pix")


def pending(reviewer_id):
    with cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        assert_reviewer(cur, reviewer_id)
        cur.execute("""SELECT order_id,user_id,product_code,amount_cents,status,created_at,
                       receiver_key,fulfillment FROM inna_manual_pix_orders
                       WHERE status='awaiting_manual_verification' ORDER BY created_at LIMIT 100""")
        return [dict(row) for row in cur.fetchall()]


def approve(order_id, *, reviewer_id, bank_reference, received_cents, reason):
    bank_reference = bank_reference.strip()
    reason = reason.strip()
    if not 8 <= len(bank_reference) <= 120 or not 10 <= len(reason) <= 2000:
        raise ValueError("Informe a referência bancária e o motivo da conferência")
    if type(received_cents) is not int or received_cents <= 0:
        raise ValueError("Valor recebido inválido")
    if not credit_wallet.enabled():
        raise RuntimeError("Carteira de créditos desativada")
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        assert_reviewer(cur, reviewer_id)
        cur.execute(
            "SELECT * FROM inna_manual_pix_orders WHERE order_id=%s FOR UPDATE",
            (order_id,),
        )
        order = cur.fetchone()
        if not order:
            raise LookupError("Pedido não encontrado")
        cur.execute(
            "SELECT * FROM inna_manual_pix_reviews WHERE order_id=%s", (order_id,)
        )
        previous = cur.fetchone()
        if previous:
            if (
                previous["bank_reference"],
                previous["received_cents"],
                previous["reason"],
                previous["reviewer_id"],
            ) != (bank_reference, received_cents, reason, reviewer_id):
                raise PixConflict("Pedido já conferido com outros dados")
            return {"order_id": order_id, "status": "verified", "replayed": True}
        if order["status"] != "awaiting_manual_verification":
            raise PixConflict("Pedido não está pendente")
        if received_cents != order["amount_cents"]:
            raise PixConflict("Valor recebido diferente do valor do pedido")
        benefit = order["fulfillment"]
        if not benefit:
            raise PixConflict(
                "Pedido antigo sem benefícios registrados; requer revisão específica"
            )
        user_id = order["user_id"]
        # Serialize all purchases for this user, including plan renewals.
        cur.execute(
            "SELECT user_id FROM inna_auth_users WHERE user_id=%s AND active=TRUE FOR UPDATE",
            (user_id,),
        )
        if not cur.fetchone():
            raise PixConflict("Usuário inexistente ou inativo")
        # Unique bank reference prevents the same receipt being used for two orders.
        cur.execute(
            """INSERT INTO inna_manual_pix_reviews
                       (order_id,reviewer_id,bank_reference,received_cents,reason) VALUES (%s,%s,%s,%s,%s)
                       ON CONFLICT(bank_reference) DO NOTHING RETURNING order_id""",
            (order_id, reviewer_id, bank_reference, received_cents, reason),
        )
        if not cur.fetchone():
            raise PixConflict("Recebimento bancário já utilizado em outro pedido")
        credits = benefit["credits"]
        credit_wallet.validate(user_id, "pix:" + order_id, credits)
        kind = benefit["kind"]
        if kind not in {"plan", "topup"}:
            raise PixConflict("Benefício inválido")
        if kind == "plan":
            cur.execute(
                """SELECT plan_code FROM inna_user_platform_entitlements
                           WHERE user_id=%s AND platform_code='financeiro' AND status='active'
                           AND (expires_at IS NULL OR expires_at > NOW()) FOR UPDATE""",
                (user_id,),
            )
            active = cur.fetchone()
            if active and active["plan_code"] != order["product_code"]:
                raise PixConflict("Troca de plano ativo requer revisão específica")
            cur.execute(
                """INSERT INTO inna_user_platform_entitlements
                (entitlement_id,user_id,platform_code,plan_code,status,activated_at,expires_at)
                VALUES (%s,%s,'financeiro',%s,'active',NOW(),NOW()+INTERVAL '1 month')
                ON CONFLICT(user_id,platform_code) DO UPDATE SET
                plan_code=EXCLUDED.plan_code,status='active',activated_at=NOW(),updated_at=NOW(),
                expires_at=(CASE WHEN inna_user_platform_entitlements.status='active'
                  THEN GREATEST(COALESCE(inna_user_platform_entitlements.expires_at,NOW()),NOW())
                  ELSE NOW() END)+INTERVAL '1 month'""",
                (uuid4().hex, user_id, order["product_code"]),
            )
        cur.execute(
            "INSERT INTO inna_credit_wallets(user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (user_id,),
        )
        cur.execute(
            "SELECT balance FROM inna_credit_wallets WHERE user_id=%s FOR UPDATE",
            (user_id,),
        )
        cur.execute(
            """INSERT INTO inna_credit_operations(user_id,operation_id,amount,kind,source,state)
                       VALUES (%s,%s,%s,'grant',%s,'completed')""",
            (
                user_id,
                "pix:" + order_id,
                credits,
                "included" if kind == "plan" else "purchased",
            ),
        )
        cur.execute(
            "UPDATE inna_credit_wallets SET balance=balance+%s,updated_at=NOW() WHERE user_id=%s",
            (credits, user_id),
        )
        cur.execute(
            "INSERT INTO inna_credit_ledger(user_id,operation_id,event,delta) VALUES (%s,%s,'grant',%s)",
            (user_id, "pix:" + order_id, credits),
        )
        cur.execute(
            "UPDATE inna_manual_pix_orders SET status='verified' WHERE order_id=%s",
            (order_id,),
        )
        return {"order_id": order_id, "status": "verified", "replayed": False}
