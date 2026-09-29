from __future__ import annotations

from abc import ABC, abstractmethod

from src.database.connection import (
    cursor_postgres,
)

from src.inna_platform.services.finance.finance_identity import (
    USER_TABLE,
    normalize_email,
)


class IdentityDirectory(ABC):

    @abstractmethod
    def get_user_by_id(
        self,
        *,
        user_id: str,
    ) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(
        self,
        *,
        email: str,
    ) -> dict | None:
        raise NotImplementedError


class PostgresIdentityDirectory(
    IdentityDirectory
):

    def get_user_by_id(
        self,
        *,
        user_id: str,
    ) -> dict | None:

        normalized = str(
            user_id or ""
        ).strip()

        if not normalized:
            return None

        sql = f"""
        SELECT
            user_id,
            email

        FROM {USER_TABLE}

        WHERE
            user_id = %s

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    normalized,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def get_user_by_email(
        self,
        *,
        email: str,
    ) -> dict | None:

        try:
            normalized = (
                normalize_email(
                    email
                )
            )

        except ValueError:
            return None

        sql = f"""
        SELECT
            user_id,
            email

        FROM {USER_TABLE}

        WHERE
            email = %s

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    normalized,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)


class InMemoryIdentityDirectory(
    IdentityDirectory
):

    def __init__(
        self,
        users: list[dict] | None = None,
    ) -> None:

        self.users_by_id: dict[
            str,
            dict,
        ] = {}

        self.users_by_email: dict[
            str,
            dict,
        ] = {}

        for user in users or []:
            self.add_user(
                user_id=str(
                    user["user_id"]
                ),

                email=str(
                    user["email"]
                ),
            )

    def add_user(
        self,
        *,
        user_id: str,
        email: str,
    ) -> dict:

        normalized_email = (
            str(email)
            .strip()
            .lower()
        )

        user = {
            "user_id":
                str(user_id).strip(),

            "email":
                normalized_email,
        }

        self.users_by_id[
            user["user_id"]
        ] = user

        self.users_by_email[
            normalized_email
        ] = user

        return user

    def get_user_by_id(
        self,
        *,
        user_id: str,
    ) -> dict | None:

        return self.users_by_id.get(
            str(user_id).strip()
        )

    def get_user_by_email(
        self,
        *,
        email: str,
    ) -> dict | None:

        return self.users_by_email.get(
            str(email)
            .strip()
            .lower()
        )