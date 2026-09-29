"""Static BR Code and durable manual-payment instructions; no access grants."""

import binascii
import io
import json
import os
import re
from pathlib import Path
from uuid import uuid4

from src.database.connection import cursor_postgres

ROOT = Path(__file__).resolve().parents[4]


def configuration():
    config = json.loads(
        (ROOT / "config/pix-receiver.json").read_text(encoding="utf-8-sig")
    )
    names = {
        "key": "SABINO_PIX_KEY",
        "receiver": "SABINO_PIX_RECEIVER",
        "city": "SABINO_PIX_CITY",
    }
    # Environment configuration is a complete set, never mixed with local data.
    if any(name in os.environ for name in (*names.values(), "SABINO_PIX_ENABLED")):
        config = {field: os.getenv(name, "").strip() for field, name in names.items()}
        config["enabled"] = os.getenv("SABINO_PIX_ENABLED", "false").strip().lower() == "true"
        if config["enabled"]:
            try:
                payload(config["key"], config["receiver"], config["city"], 1, "CONFIGCHECK")
            except ValueError:
                # Invalid or incomplete receiver settings must not expose checkout.
                config["enabled"] = False
    return config


def products():
    proposal = json.loads(
        (ROOT / "config/credit-commercial-proposal.json").read_text(
            encoding="utf-8-sig"
        )
    )
    result = {
        code: {
            "amount_cents": value["monthly_price_cents"],
            "fulfillment": {"kind": "plan", "credits": value["included_credits"]},
            "label": "Financeiro " + code + " · 1 mês",
        }
        for code, value in proposal["plans"].items()
    }
    result.update(
        {
            code: {
                "amount_cents": value["price_cents"],
                "fulfillment": {"kind": "topup", "credits": value["credits"]},
                "label": str(value["credits"]) + " créditos",
            }
            for code, value in proposal["topups"].items()
        }
    )
    return result


def tlv(tag, value):
    size = len(value.encode("utf-8"))
    if size > 99:
        raise ValueError("Pix field too long")
    return f"{tag}{size:02d}{value}"


def payload(key, receiver, city, cents, txid):
    if not re.fullmatch(r"\+55\d{11}", key):
        raise ValueError("Expected Brazilian mobile Pix key")
    if not re.fullmatch(r"[A-Z0-9 ]{1,25}", receiver) or not re.fullmatch(
        r"[A-Z0-9 ]{1,15}", city
    ):
        raise ValueError("Invalid receiver name or city")
    if type(cents) is not int or not 0 < cents <= 999999999:
        raise ValueError("Invalid amount")
    if not re.fullmatch(r"[A-Za-z0-9]{1,25}", txid):
        raise ValueError("Invalid transaction reference")
    value = (
        tlv("00", "01")
        + tlv("26", tlv("00", "br.gov.bcb.pix") + tlv("01", key))
        + tlv("52", "0000")
        + tlv("53", "986")
        + tlv("54", f"{cents // 100}.{cents % 100:02d}")
        + tlv("58", "BR")
        + tlv("59", receiver)
        + tlv("60", city)
        + tlv("62", tlv("05", txid))
        + "6304"
    )
    return value + f"{binascii.crc_hqx(value.encode(), 0xFFFF):04X}"


def qr_svg(code):
    import qrcode
    from qrcode.image.svg import SvgPathImage

    image = qrcode.make(code, image_factory=SvgPathImage, border=4)
    output = io.BytesIO()
    image.save(output)
    return output.getvalue().decode()


def create_order(user_id, product_code):
    config = configuration()
    if config.get("enabled") is not True:
        raise RuntimeError("Pix manual ainda não habilitado")
    product = products()[product_code]
    order_id = uuid4().hex[:25]
    code = payload(
        config["key"],
        config["receiver"],
        config["city"],
        product["amount_cents"],
        order_id,
    )
    svg = qr_svg(code)  # Fail before recording if the QR dependency is missing.
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute(
            """INSERT INTO inna_manual_pix_orders
        (order_id,user_id,product_code,amount_cents,pix_payload,receiver_name,receiver_city,receiver_key,fulfillment)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
            (
                order_id,
                user_id,
                product_code,
                product["amount_cents"],
                code,
                config["receiver"],
                config["city"],
                config["key"],
                json.dumps(product["fulfillment"]),
            ),
        )
    return {
        "order_id": order_id,
        **product,
        "payload": code,
        "svg": svg,
        "receiver": config["receiver"],
        "key": config["key"],
        "status": "awaiting_manual_verification",
    }


def user_orders(user_id):
    with cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        cur.execute(
            """SELECT order_id,product_code,amount_cents,status,created_at
                       FROM inna_manual_pix_orders WHERE user_id=%s
                       ORDER BY created_at DESC LIMIT 100""",
            (user_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def user_order(user_id, order_id):
    with cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        cur.execute(
            "SELECT * FROM inna_manual_pix_orders WHERE user_id=%s AND order_id=%s",
            (user_id, order_id),
        )
        row = cur.fetchone()
    if row is None:
        raise LookupError("Pedido não encontrado")
    return {
        "order_id": row["order_id"],
        "label": row["product_code"],
        "amount_cents": row["amount_cents"],
        "status": row["status"],
        "payload": row["pix_payload"],
        "svg": qr_svg(row["pix_payload"]),
        "receiver": row["receiver_name"],
        "key": row["receiver_key"],
    }
