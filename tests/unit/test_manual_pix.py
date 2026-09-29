import binascii
from unittest.mock import patch

import pytest

from src.inna_platform.services.finance import manual_pix


def test_pix_payload_fields_and_checksum():
    value = manual_pix.payload("+5511999999999", "TEST RECEIVER", "SAO PAULO", 1990, "TEST123")
    assert value.startswith("000201")
    assert "540519.90" in value
    assert "620b" not in value
    assert "62110507TEST123" in value
    assert value[-4:] == f"{binascii.crc_hqx(value[:-4].encode(), 0xFFFF):04X}"


@pytest.mark.parametrize("amount", [0, -1, True, "19.90"])
def test_invalid_amount(amount):
    with pytest.raises(ValueError):
        manual_pix.payload("+5511999999999", "TEST", "CITY", amount, "TEST123")


def test_disabled_pix_never_creates_order():
    with patch.object(manual_pix, "configuration", return_value={"enabled": False}), patch.object(manual_pix, "cursor_postgres") as db:
        with pytest.raises(RuntimeError):
            manual_pix.create_order("test-user", "credits_100")
        db.assert_not_called()
