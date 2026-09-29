"""Apply additive Pix migrations; optionally authorize an existing active account."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    from getpass import getpass

    from src.database.connection import cursor_postgres
    from src.inna_platform.services.finance.finance_identity import create_user

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--authorize-email")
    parser.add_argument(
        "--create-admin",
        action="store_true",
        help="Prompt locally for a password if the administrator account does not exist",
    )
    args = parser.parse_args()
    if not args.apply:
        parser.error("Use --apply to apply the five additive migrations")
    if args.create_admin:
        if not args.authorize_email:
            parser.error("--create-admin requires --authorize-email")
        with cursor_postgres(commit_automatico=False) as cur:
            cur.execute(
                "SELECT active FROM inna_auth_users WHERE lower(email)=%s",
                (args.authorize_email.strip().lower(),),
            )
            existing = cur.fetchone()
        if existing is not None and not existing[0]:
            raise ValueError("Conta inativa. Revise o cadastro existente.")
        if existing is None:
            password = getpass(
                "Crie uma senha para a conta administradora (mínimo 12 caracteres): "
            )
            confirmation = getpass("Confirme a senha: ")
            if len(password) < 12 or password != confirmation:
                raise ValueError(
                    "Senha curta ou confirmação diferente. Nenhuma conta criada."
                )
            create_user(email=args.authorize_email, password=password)
            del password, confirmation
    files = [
        "20260924_001_credit_wallet.sql",
        "20260924_002_credit_reviews.sql",
        "20260924_003_manual_pix.sql",
        "20260925_004_pix_approval.sql",
        "20260927_005_paid_analysis.sql",
    ]
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute("SELECT pg_advisory_xact_lock(20260925, 4)")
        for name in files:
            content = (ROOT / "migrations" / name).read_text(encoding="utf-8-sig")
            # Keep the complete migration set in one transaction.
            content = "\n".join(
                line
                for line in content.splitlines()
                if line.strip().upper() not in {"BEGIN;", "COMMIT;"}
            )
            cur.execute(content)
        if args.authorize_email:
            cur.execute(
                "SELECT user_id FROM inna_auth_users WHERE lower(email)=%s AND active=TRUE",
                (args.authorize_email.strip().lower(),),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(
                    "Conta ativa não encontrada. Cadastre a conta antes de autorizar."
                )
            cur.execute(
                "INSERT INTO inna_pix_reviewers(user_id) VALUES (%s) ON CONFLICT DO NOTHING",
                (row[0],),
            )
    print(
        "Migrações Pix aplicadas. Emissão permanece controlada pela configuração existente."
    )
    if args.authorize_email:
        print("Conta existente autorizada a conferir Pix.")


if __name__ == "__main__":
    main()
