from src.database.connection import cursor_postgres

SETTINGS_TABLE = "inna_finance_settings"
BUDGET_TABLE = "inna_finance_budgets"
BUDGET_PERIOD_TABLE = "inna_finance_budget_periods"
BUDGET_LIMIT_TABLE = "inna_finance_budget_limits"
GOAL_TABLE = "inna_finance_goals"
RESERVE_TABLE = "inna_finance_reserve"


def ensure_finance_setup_schema() -> None:

    sql_settings = f"""
    CREATE TABLE IF NOT EXISTS {SETTINGS_TABLE} (
        owner_id TEXT PRIMARY KEY,
        currency VARCHAR(3) NOT NULL DEFAULT 'BRL',
        setup_completed BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    sql_budget = f"""
    CREATE TABLE IF NOT EXISTS {BUDGET_TABLE} (
        budget_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        category TEXT NOT NULL,
        monthly_limit NUMERIC(14,2) NOT NULL
            CHECK (monthly_limit >= 0),
        active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(owner_id, category)
    )
    """

    sql_budget_period = f"""
    CREATE TABLE IF NOT EXISTS {BUDGET_PERIOD_TABLE} (
        period_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        reference_month VARCHAR(7) NOT NULL,
        monthly_income NUMERIC(14,2) NOT NULL DEFAULT 0
            CHECK (monthly_income >= 0),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(owner_id, reference_month)
    )
    """

    sql_budget_limit = f"""
    CREATE TABLE IF NOT EXISTS {BUDGET_LIMIT_TABLE} (
        limit_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        reference_month VARCHAR(7) NOT NULL,
        category TEXT NOT NULL,
        monthly_limit NUMERIC(14,2) NOT NULL DEFAULT 0
            CHECK (monthly_limit >= 0),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(owner_id, reference_month, category)
    )
    """
    sql_goal = f"""
    CREATE TABLE IF NOT EXISTS {GOAL_TABLE} (
        goal_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        name TEXT NOT NULL,
        target_amount NUMERIC(14,2) NOT NULL
            CHECK (target_amount > 0),
        current_amount NUMERIC(14,2) NOT NULL DEFAULT 0
            CHECK (current_amount >= 0),
        target_date DATE NULL,
        active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    sql_reserve = f"""
    CREATE TABLE IF NOT EXISTS {RESERVE_TABLE} (
        owner_id TEXT PRIMARY KEY,
        target_amount NUMERIC(14,2) NOT NULL DEFAULT 0
            CHECK (target_amount >= 0),
        current_amount NUMERIC(14,2) NOT NULL DEFAULT 0
            CHECK (current_amount >= 0),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql_settings)
        cursor.execute(sql_budget)
        cursor.execute(sql_budget_period)
        cursor.execute(sql_budget_limit)
        cursor.execute(sql_goal)
        cursor.execute(sql_reserve)


def finance_setup_capabilities() -> dict:
    return {
        "version": "tc4-e1a",
        "persistent_settings": True,
        "persistent_budgets": True,
        "persistent_goals": True,
        "persistent_reserve": True,
        "owner_scoped": True,
    }

# TC4_E1B1_SETTINGS_CRUD

def upsert_finance_settings(
    *,
    owner_id: str,
    currency: str = "BRL",
    setup_completed: bool = False,
) -> dict:

    owner_id = str(owner_id).strip()
    currency = str(currency).strip().upper()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if len(currency) != 3:
        raise ValueError("currency inválida")

    sql = f"""
    INSERT INTO {SETTINGS_TABLE} (
        owner_id,
        currency,
        setup_completed
    )
    VALUES (%s, %s, %s)

    ON CONFLICT (owner_id)
    DO UPDATE SET
        currency = EXCLUDED.currency,
        setup_completed = EXCLUDED.setup_completed,
        updated_at = NOW()

    RETURNING
        owner_id,
        currency,
        setup_completed,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                currency,
                bool(setup_completed),
            ),
        )

        return dict(cursor.fetchone())


def get_finance_settings(
    *,
    owner_id: str,
) -> dict | None:

    sql = f"""
    SELECT
        owner_id,
        currency,
        setup_completed,
        created_at,
        updated_at
    FROM {SETTINGS_TABLE}
    WHERE owner_id = %s
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (str(owner_id).strip(),),
        )

        row = cursor.fetchone()

        return dict(row) if row else None

# TC4_E1B2_BUDGET_CRUD

def upsert_finance_budget(
    *,
    owner_id: str,
    category: str,
    monthly_limit,
) -> dict:

    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    owner_id = str(owner_id).strip()
    category = str(category).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not category:
        raise ValueError("category obrigatória")

    try:
        limit_value = Decimal(str(monthly_limit)).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as exc:
        raise ValueError("monthly_limit inválido") from exc

    if limit_value < 0:
        raise ValueError("monthly_limit não pode ser negativo")

    sql = f"""
    INSERT INTO {BUDGET_TABLE} (
        budget_id,
        owner_id,
        category,
        monthly_limit,
        active
    )
    VALUES (%s, %s, %s, %s, TRUE)

    ON CONFLICT (owner_id, category)
    DO UPDATE SET
        monthly_limit = EXCLUDED.monthly_limit,
        active = TRUE,
        updated_at = NOW()

    RETURNING
        budget_id,
        owner_id,
        category,
        monthly_limit,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                category,
                limit_value,
            ),
        )

        return dict(cursor.fetchone())


def list_finance_budgets(
    *,
    owner_id: str,
) -> list[dict]:

    sql = f"""
    SELECT
        budget_id,
        owner_id,
        category,
        monthly_limit,
        active,
        created_at,
        updated_at
    FROM {BUDGET_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY category
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (str(owner_id).strip(),),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

# TC4_E1B3_GOAL_CRUD

def create_finance_goal(
    *,
    owner_id: str,
    name: str,
    target_amount,
    target_date=None,
) -> dict:

    from datetime import date
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    owner_id = str(owner_id).strip()
    name = str(name).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not name:
        raise ValueError("name obrigatório")

    try:
        amount = Decimal(str(target_amount)).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as exc:
        raise ValueError("target_amount inválido") from exc

    if amount <= 0:
        raise ValueError("target_amount deve ser maior que zero")

    normalized_date = None

    if target_date:
        if isinstance(target_date, date):
            normalized_date = target_date
        else:
            normalized_date = date.fromisoformat(
                str(target_date)
            )

    sql = f"""
    INSERT INTO {GOAL_TABLE} (
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active
    )
    VALUES (%s, %s, %s, %s, 0, %s, TRUE)

    RETURNING
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                name,
                amount,
                normalized_date,
            ),
        )

        return dict(cursor.fetchone())


def list_finance_goals(
    *,
    owner_id: str,
) -> list[dict]:

    sql = f"""
    SELECT
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active,
        created_at,
        updated_at
    FROM {GOAL_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY created_at DESC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (str(owner_id).strip(),),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

# TC4_E1B4_RESERVE_CRUD

def upsert_finance_reserve(
    *,
    owner_id: str,
    target_amount,
    current_amount=0,
) -> dict:

    from decimal import Decimal, InvalidOperation

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    try:
        target = Decimal(str(target_amount)).quantize(
            Decimal("0.01")
        )
        current = Decimal(str(current_amount)).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as exc:
        raise ValueError("valor inválido") from exc

    if target < 0 or current < 0:
        raise ValueError("valores não podem ser negativos")

    sql = f"""
    INSERT INTO {RESERVE_TABLE} (
        owner_id,
        target_amount,
        current_amount
    )
    VALUES (%s, %s, %s)

    ON CONFLICT (owner_id)
    DO UPDATE SET
        target_amount = EXCLUDED.target_amount,
        current_amount = EXCLUDED.current_amount,
        updated_at = NOW()

    RETURNING
        owner_id,
        target_amount,
        current_amount,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id, target, current),
        )

        return dict(cursor.fetchone())


def get_finance_reserve(
    *,
    owner_id: str,
) -> dict | None:

    sql = f"""
    SELECT
        owner_id,
        target_amount,
        current_amount,
        created_at,
        updated_at
    FROM {RESERVE_TABLE}
    WHERE owner_id = %s
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (str(owner_id).strip(),),
        )

        row = cursor.fetchone()

        return dict(row) if row else None
# SABINO_BUDGET_PERIOD_CRUD_V1

def upsert_finance_budget_period(*, owner_id: str, reference_month: str, monthly_income) -> dict:
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4
    import re

    owner_id = str(owner_id).strip()
    reference_month = str(reference_month).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", reference_month):
        raise ValueError("reference_month inválido")

    try:
        income = Decimal(str(monthly_income)).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("monthly_income inválido") from exc

    if income < 0:
        raise ValueError("monthly_income não pode ser negativo")

    sql = f"""
    INSERT INTO {BUDGET_PERIOD_TABLE}
        (period_id, owner_id, reference_month, monthly_income)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (owner_id, reference_month)
    DO UPDATE SET
        monthly_income = EXCLUDED.monthly_income,
        updated_at = NOW()
    RETURNING *
    """

    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cursor:
        cursor.execute(sql, (uuid4().hex, owner_id, reference_month, income))
        return dict(cursor.fetchone())


def get_finance_budget_period(*, owner_id: str, reference_month: str) -> dict | None:
    sql = f"""
    SELECT *
    FROM {BUDGET_PERIOD_TABLE}
    WHERE owner_id = %s
      AND reference_month = %s
    """

    with cursor_postgres(dict_cursor=True) as cursor:
        cursor.execute(sql, (str(owner_id).strip(), str(reference_month).strip()))
        row = cursor.fetchone()
        return dict(row) if row else None
# SABINO_BUDGET_LIMITS_CRUD_V1

def upsert_finance_budget_limit(
    *,
    owner_id: str,
    reference_month: str,
    category: str,
    monthly_limit,
) -> dict:
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4
    import re

    owner_id = str(owner_id).strip()
    reference_month = str(reference_month).strip()
    category = str(category).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", reference_month):
        raise ValueError("reference_month inválido")

    if not category:
        raise ValueError("category obrigatória")

    try:
        limit_value = Decimal(str(monthly_limit)).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("monthly_limit inválido") from exc

    if limit_value < 0:
        raise ValueError("monthly_limit não pode ser negativo")

    sql = f"""
    INSERT INTO {BUDGET_LIMIT_TABLE}
        (limit_id, owner_id, reference_month, category, monthly_limit)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (owner_id, reference_month, category)
    DO UPDATE SET
        monthly_limit = EXCLUDED.monthly_limit,
        updated_at = NOW()
    RETURNING *
    """

    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cursor:
        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                reference_month,
                category,
                limit_value,
            ),
        )
        return dict(cursor.fetchone())


def list_finance_budget_limits(
    *,
    owner_id: str,
    reference_month: str,
) -> list[dict]:
    sql = f"""
    SELECT *
    FROM {BUDGET_LIMIT_TABLE}
    WHERE owner_id = %s
      AND reference_month = %s
    ORDER BY category
    """

    with cursor_postgres(dict_cursor=True) as cursor:
        cursor.execute(
            sql,
            (
                str(owner_id).strip(),
                str(reference_month).strip(),
            ),
        )
        return [dict(row) for row in cursor.fetchall()]
# SABINO_GOAL_CONTRIBUTION_V1

def add_finance_goal_amount(
    *,
    owner_id: str,
    goal_id: str,
    amount,
) -> dict:
    from decimal import Decimal, InvalidOperation

    owner_id = str(owner_id).strip()
    goal_id = str(goal_id).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not goal_id:
        raise ValueError("goal_id obrigatório")

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("valor inválido")

    if amount <= 0:
        raise ValueError("valor deve ser maior que zero")

    sql = f"""
    UPDATE {GOAL_TABLE}
    SET
        current_amount = LEAST(
            target_amount,
            current_amount + %s
        ),
        updated_at = NOW()
    WHERE owner_id = %s
      AND goal_id = %s
      AND active = TRUE
    RETURNING
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                amount,
                owner_id,
                goal_id,
            ),
        )

        row = cursor.fetchone()

    if not row:
        raise ValueError("meta não encontrada")

    return dict(row)
# SABINO_RESERVE_CONTRIBUTION_V1

def add_finance_reserve_amount(
    *,
    owner_id: str,
    amount,
) -> dict:

    from decimal import Decimal, InvalidOperation

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    try:
        value = Decimal(str(amount)).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as exc:
        raise ValueError("amount inválido") from exc

    if value <= 0:
        raise ValueError("amount deve ser maior que zero")

    sql = f"""
    UPDATE {RESERVE_TABLE}
    SET
        current_amount = LEAST(target_amount, current_amount + %s),
        updated_at = NOW()
    WHERE owner_id = %s
      AND target_amount > 0
    RETURNING
        owner_id,
        target_amount,
        current_amount,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                value,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "Configure a meta da reserva antes de adicionar valor"
            )

        return dict(row)

# SABINO_SECURITY_PROFILE_REPOSITORY_V1

SECURITY_PROFILE_TABLE = "inna_finance_security_profile"


def ensure_finance_security_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {SECURITY_PROFILE_TABLE} (
        owner_id TEXT PRIMARY KEY,

        strong_password BOOLEAN NOT NULL DEFAULT FALSE,
        two_factor BOOLEAN NOT NULL DEFAULT FALSE,
        movement_alerts BOOLEAN NOT NULL DEFAULT FALSE,
        verify_links BOOLEAN NOT NULL DEFAULT FALSE,
        review_devices BOOLEAN NOT NULL DEFAULT FALSE,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql)


def get_finance_security_profile(
    *,
    owner_id: str,
) -> dict | None:

    ensure_finance_security_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    sql = f"""
    SELECT
        owner_id,
        strong_password,
        two_factor,
        movement_alerts,
        verify_links,
        review_devices,
        created_at,
        updated_at
    FROM {SECURITY_PROFILE_TABLE}
    WHERE owner_id = %s
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        row = cursor.fetchone()

        return dict(row) if row else None


def upsert_finance_security_profile(
    *,
    owner_id: str,
    strong_password=False,
    two_factor=False,
    movement_alerts=False,
    verify_links=False,
    review_devices=False,
) -> dict:

    ensure_finance_security_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    values = (
        bool(strong_password),
        bool(two_factor),
        bool(movement_alerts),
        bool(verify_links),
        bool(review_devices),
    )

    sql = f"""
    INSERT INTO {SECURITY_PROFILE_TABLE} (
        owner_id,
        strong_password,
        two_factor,
        movement_alerts,
        verify_links,
        review_devices
    )
    VALUES (%s, %s, %s, %s, %s, %s)

    ON CONFLICT (owner_id)
    DO UPDATE SET
        strong_password = EXCLUDED.strong_password,
        two_factor = EXCLUDED.two_factor,
        movement_alerts = EXCLUDED.movement_alerts,
        verify_links = EXCLUDED.verify_links,
        review_devices = EXCLUDED.review_devices,
        updated_at = NOW()

    RETURNING
        owner_id,
        strong_password,
        two_factor,
        movement_alerts,
        verify_links,
        review_devices,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                *values,
            ),
        )

        return dict(cursor.fetchone())

# SABINO_FINANCE_DEBT_REPOSITORY_V1

DEBT_TABLE = "inna_finance_debts"


def ensure_finance_debt_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {DEBT_TABLE} (
        debt_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,

        debt_type TEXT NOT NULL,
        creditor TEXT NOT NULL,

        outstanding_balance NUMERIC(14,2) NOT NULL
            CHECK (outstanding_balance >= 0),

        monthly_payment NUMERIC(14,2) NOT NULL
            CHECK (monthly_payment >= 0),

        installments_remaining INTEGER NULL
            CHECK (
                installments_remaining IS NULL
                OR installments_remaining > 0
            ),

        due_date DATE NULL,

        active BOOLEAN NOT NULL DEFAULT TRUE,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(sql)


def create_finance_debt(
    *,
    owner_id: str,
    debt_type: str,
    creditor: str,
    outstanding_balance,
    monthly_payment,
    installments_remaining=None,
    due_date=None,
) -> dict:

    from datetime import date
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    ensure_finance_debt_schema()

    owner_id = str(owner_id).strip()
    debt_type = str(debt_type).strip()
    creditor = str(creditor).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not debt_type:
        raise ValueError("debt_type obrigatório")

    if not creditor:
        raise ValueError("creditor obrigatório")

    try:
        balance = Decimal(
            str(outstanding_balance)
        ).quantize(Decimal("0.01"))

        payment = Decimal(
            str(monthly_payment)
        ).quantize(Decimal("0.01"))

    except InvalidOperation as exc:
        raise ValueError("valor inválido") from exc

    if balance < 0:
        raise ValueError(
            "outstanding_balance não pode ser negativo"
        )

    if payment < 0:
        raise ValueError(
            "monthly_payment não pode ser negativo"
        )

    installments = None

    if installments_remaining not in (
        None,
        "",
    ):
        installments = int(
            installments_remaining
        )

        if installments <= 0:
            raise ValueError(
                "installments_remaining deve ser maior que zero"
            )

    normalized_due_date = None

    if due_date:
        if isinstance(due_date, date):
            normalized_due_date = due_date
        else:
            normalized_due_date = date.fromisoformat(
                str(due_date)
            )

    sql = f"""
    INSERT INTO {DEBT_TABLE} (
        debt_id,
        owner_id,
        debt_type,
        creditor,
        outstanding_balance,
        monthly_payment,
        installments_remaining,
        due_date,
        active
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)

    RETURNING
        debt_id,
        owner_id,
        debt_type,
        creditor,
        outstanding_balance,
        monthly_payment,
        installments_remaining,
        due_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                debt_type,
                creditor,
                balance,
                payment,
                installments,
                normalized_due_date,
            ),
        )

        return dict(cursor.fetchone())


def list_finance_debts(
    *,
    owner_id: str,
) -> list[dict]:

    ensure_finance_debt_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    sql = f"""
    SELECT
        debt_id,
        owner_id,
        debt_type,
        creditor,
        outstanding_balance,
        monthly_payment,
        installments_remaining,
        due_date,
        active,
        created_at,
        updated_at
    FROM {DEBT_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY created_at DESC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

# SABINO_DEBT_CLOSE_V1

def close_finance_debt(
    *,
    owner_id: str,
    debt_id: str,
) -> dict:

    owner_id = str(owner_id).strip()
    debt_id = str(debt_id).strip()

    if not owner_id or not debt_id:
        raise ValueError("owner_id e debt_id são obrigatórios")

    sql = f"""
    UPDATE {DEBT_TABLE}
    SET
        active = FALSE,
        updated_at = NOW()
    WHERE owner_id = %s
      AND debt_id = %s
      AND active = TRUE
    RETURNING
        debt_id,
        owner_id,
        active,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                debt_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "Dívida não encontrada"
            )

        return dict(row)

# SABINO_DEBT_PAYMENT_V1

DEBT_PAYMENT_TABLE = "inna_finance_debt_payments"


def ensure_finance_debt_payment_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {DEBT_PAYMENT_TABLE} (
        payment_id TEXT PRIMARY KEY,
        debt_id TEXT NOT NULL,
        owner_id TEXT NOT NULL,
        amount NUMERIC(14,2) NOT NULL
            CHECK (amount > 0),
        paid_at DATE NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(sql)


def register_finance_debt_payment(
    *,
    owner_id: str,
    debt_id: str,
) -> dict:

    from datetime import date
    from decimal import Decimal
    from uuid import uuid4

    ensure_finance_debt_schema()
    ensure_finance_debt_payment_schema()

    owner_id = str(owner_id).strip()
    debt_id = str(debt_id).strip()

    if not owner_id or not debt_id:
        raise ValueError(
            "owner_id e debt_id são obrigatórios"
        )

    select_sql = f"""
    SELECT
        debt_id,
        outstanding_balance,
        monthly_payment,
        installments_remaining,
        due_date
    FROM {DEBT_TABLE}
    WHERE owner_id = %s
      AND debt_id = %s
      AND active = TRUE
    FOR UPDATE
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            select_sql,
            (
                owner_id,
                debt_id,
            ),
        )

        current = cursor.fetchone()

        if not current:
            raise ValueError(
                "Dívida ativa não encontrada"
            )

        balance = Decimal(
            str(current["outstanding_balance"])
        )

        monthly_payment = Decimal(
            str(current["monthly_payment"])
        )

        if monthly_payment <= 0:
            raise ValueError(
                "A parcela mensal deve ser maior que zero"
            )

        payment_amount = min(
            balance,
            monthly_payment,
        )

        installments = current.get(
            "installments_remaining"
        )

        closes_by_installment = (
            installments is not None
            and int(installments) <= 1
        )

        new_balance = max(
            Decimal("0.00"),
            balance - payment_amount,
        )

        closes_debt = (
            new_balance <= 0
            or closes_by_installment
        )

        if installments is None:
            new_installments = None
        elif int(installments) <= 1:
            new_installments = None
        else:
            new_installments = (
                int(installments) - 1
            )

        payment_id = uuid4().hex
        paid_at = date.today()

        cursor.execute(
            f"""
            INSERT INTO {DEBT_PAYMENT_TABLE} (
                payment_id,
                debt_id,
                owner_id,
                amount,
                paid_at
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                payment_id,
                debt_id,
                owner_id,
                amount,
                paid_at,
                created_at
            """,
            (
                payment_id,
                debt_id,
                owner_id,
                payment_amount,
                paid_at,
            ),
        )

        payment = dict(
            cursor.fetchone()
        )

        cursor.execute(
            f"""
            UPDATE {DEBT_TABLE}
            SET
                outstanding_balance = %s,
                installments_remaining = %s,
                due_date =
                    CASE
                        WHEN %s THEN due_date
                        WHEN due_date IS NULL THEN NULL
                        ELSE (
                            due_date
                            + INTERVAL '1 month'
                        )::date
                    END,
                active = %s,
                updated_at = NOW()
            WHERE owner_id = %s
              AND debt_id = %s
            RETURNING
                debt_id,
                owner_id,
                debt_type,
                creditor,
                outstanding_balance,
                monthly_payment,
                installments_remaining,
                due_date,
                active,
                created_at,
                updated_at
            """,
            (
                new_balance,
                new_installments,
                closes_debt,
                not closes_debt,
                owner_id,
                debt_id,
            ),
        )

        debt = dict(
            cursor.fetchone()
        )

        return {
            "payment": payment,
            "debt": debt,
            "auto_closed": closes_debt,
        }

# SABINO_DEBT_DUE_DATE_V1

def update_finance_debt_due_date(
    *,
    owner_id: str,
    debt_id: str,
    due_date,
) -> dict:

    from datetime import date

    owner_id = str(owner_id).strip()
    debt_id = str(debt_id).strip()

    if not owner_id or not debt_id:
        raise ValueError(
            "owner_id e debt_id são obrigatórios"
        )

    if not due_date:
        raise ValueError(
            "due_date obrigatório"
        )

    normalized_due_date = (
        due_date
        if isinstance(due_date, date)
        else date.fromisoformat(str(due_date))
    )

    sql = f"""
    UPDATE {DEBT_TABLE}
    SET
        due_date = %s,
        updated_at = NOW()
    WHERE owner_id = %s
      AND debt_id = %s
      AND active = TRUE
    RETURNING
        debt_id,
        owner_id,
        debt_type,
        creditor,
        outstanding_balance,
        monthly_payment,
        installments_remaining,
        due_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_due_date,
                owner_id,
                debt_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "Dívida ativa não encontrada"
            )

        return dict(row)

# SABINO_DEBT_PAYMENT_HISTORY_V1

def list_finance_debt_payments(
    *,
    owner_id: str,
    debt_id: str,
) -> list[dict]:

    ensure_finance_debt_payment_schema()

    owner_id = str(owner_id).strip()
    debt_id = str(debt_id).strip()

    if not owner_id or not debt_id:
        raise ValueError(
            "owner_id e debt_id são obrigatórios"
        )

    sql = f"""
    SELECT
        payment_id,
        debt_id,
        owner_id,
        amount,
        paid_at,
        created_at
    FROM {DEBT_PAYMENT_TABLE}
    WHERE owner_id = %s
      AND debt_id = %s
    ORDER BY paid_at DESC, created_at DESC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                debt_id,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

# SABINO_FINANCE_BILLS_REPOSITORY_V1

BILL_TABLE = "inna_finance_bills"


def ensure_finance_bill_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {BILL_TABLE} (
        bill_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,

        name TEXT NOT NULL,
        category TEXT NOT NULL,

        amount NUMERIC(14,2) NOT NULL
            CHECK (amount > 0),

        due_date DATE NOT NULL,

        recurrence TEXT NOT NULL DEFAULT 'none'
            CHECK (
                recurrence IN ('none', 'monthly')
            ),

        is_subscription BOOLEAN NOT NULL DEFAULT FALSE,
        active BOOLEAN NOT NULL DEFAULT TRUE,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(sql)


def create_finance_bill(
    *,
    owner_id: str,
    name: str,
    category: str,
    amount,
    due_date,
    recurrence="none",
    is_subscription=False,
) -> dict:

    from datetime import date
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    ensure_finance_bill_schema()

    owner_id = str(owner_id).strip()
    name = str(name).strip()
    category = str(category).strip()
    recurrence = str(recurrence).strip().lower()

    if not owner_id:
        raise ValueError("owner_id obrigatório")

    if not name:
        raise ValueError("name obrigatório")

    if not category:
        raise ValueError("category obrigatório")

    if recurrence not in {
        "none",
        "monthly",
    }:
        raise ValueError("recurrence inválido")

    try:
        normalized_amount = Decimal(
            str(amount)
        ).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as exc:
        raise ValueError(
            "amount inválido"
        ) from exc

    if normalized_amount <= 0:
        raise ValueError(
            "amount deve ser maior que zero"
        )

    if not due_date:
        raise ValueError(
            "due_date obrigatório"
        )

    normalized_due_date = (
        due_date
        if isinstance(due_date, date)
        else date.fromisoformat(str(due_date))
    )

    sql = f"""
    INSERT INTO {BILL_TABLE} (
        bill_id,
        owner_id,
        name,
        category,
        amount,
        due_date,
        recurrence,
        is_subscription,
        active
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, TRUE
    )

    RETURNING
        bill_id,
        owner_id,
        name,
        category,
        amount,
        due_date,
        recurrence,
        is_subscription,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                name,
                category,
                normalized_amount,
                normalized_due_date,
                recurrence,
                bool(is_subscription),
            ),
        )

        return dict(cursor.fetchone())


def list_finance_bills(
    *,
    owner_id: str,
) -> list[dict]:

    ensure_finance_bill_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError(
            "owner_id obrigatório"
        )

    sql = f"""
    SELECT
        bill_id,
        owner_id,
        name,
        category,
        amount,
        due_date,
        recurrence,
        is_subscription,
        active,
        created_at,
        updated_at
    FROM {BILL_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY due_date ASC, created_at ASC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

# SABINO_BILL_PAYMENT_V1

BILL_PAYMENT_TABLE = "inna_finance_bill_payments"


def ensure_finance_bill_payment_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {BILL_PAYMENT_TABLE} (
        payment_id TEXT PRIMARY KEY,
        bill_id TEXT NOT NULL,
        owner_id TEXT NOT NULL,

        due_date DATE NOT NULL,
        paid_at DATE NOT NULL,

        amount NUMERIC(14,2) NOT NULL
            CHECK (amount > 0),

        transaction_id TEXT NOT NULL,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

        UNIQUE (
            owner_id,
            bill_id,
            due_date
        )
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(sql)


def register_finance_bill_payment(
    *,
    owner_id: str,
    bill_id: str,
    expected_due_date,
) -> dict:

    from datetime import date
    from uuid import uuid4

    from src.inna_platform.services.finance.transaction_repository import (
        create_financial_transaction_idempotent,
    )

    ensure_finance_bill_schema()
    ensure_finance_bill_payment_schema()

    owner_id = str(owner_id).strip()
    bill_id = str(bill_id).strip()

    if not owner_id or not bill_id:
        raise ValueError(
            "owner_id e bill_id são obrigatórios"
        )

    if not expected_due_date:
        raise ValueError(
            "expected_due_date obrigatório"
        )

    expected = (
        expected_due_date
        if isinstance(expected_due_date, date)
        else date.fromisoformat(
            str(expected_due_date)
        )
    )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            SELECT
                bill_id,
                owner_id,
                name,
                category,
                amount,
                due_date,
                recurrence,
                is_subscription,
                active
            FROM {BILL_TABLE}
            WHERE owner_id = %s
              AND bill_id = %s
              AND active = TRUE
            LIMIT 1
            """,
            (
                owner_id,
                bill_id,
            ),
        )

        bill = cursor.fetchone()

        if not bill:

            cursor.execute(
                f"""
                SELECT *
                FROM {BILL_PAYMENT_TABLE}
                WHERE owner_id = %s
                  AND bill_id = %s
                  AND due_date = %s
                LIMIT 1
                """,
                (
                    owner_id,
                    bill_id,
                    expected,
                ),
            )

            existing = cursor.fetchone()

            if existing:
                return {
                    "already_paid": True,
                    "payment": dict(existing),
                    "bill": None,
                }

            raise ValueError(
                "Conta ativa não encontrada"
            )

        bill = dict(bill)

        if bill["due_date"] != expected:

            cursor.execute(
                f"""
                SELECT *
                FROM {BILL_PAYMENT_TABLE}
                WHERE owner_id = %s
                  AND bill_id = %s
                  AND due_date = %s
                LIMIT 1
                """,
                (
                    owner_id,
                    bill_id,
                    expected,
                ),
            )

            existing = cursor.fetchone()

            if existing:
                return {
                    "already_paid": True,
                    "payment": dict(existing),
                    "bill": bill,
                }

            raise ValueError(
                "O vencimento da conta foi alterado. Atualize a página."
            )

        paid_at = date.today()

        transaction_id = (
            f"billpay_{bill_id}_"
            f"{expected.strftime('%Y%m%d')}"
        )

        transaction = (
            create_financial_transaction_idempotent(
                transaction_id=transaction_id,
                owner_id=owner_id,
                transaction_date=paid_at,
                transaction_type="Despesa",
                amount=bill["amount"],
                currency="BRL",
                description=f"Pagamento de conta: {bill['name']}",
                merchant=bill["name"],
                category=bill["category"],
                subcategory="Conta paga",
                classification_strategy="manual",
                classification_confirmed=True,
                source="financeiro_ui",
            )
        )

        cursor.execute(
            f"""
            INSERT INTO {BILL_PAYMENT_TABLE} (
                payment_id,
                bill_id,
                owner_id,
                due_date,
                paid_at,
                amount,
                transaction_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)

            ON CONFLICT (
                owner_id,
                bill_id,
                due_date
            )
            DO NOTHING

            RETURNING *
            """,
            (
                uuid4().hex,
                bill_id,
                owner_id,
                expected,
                paid_at,
                bill["amount"],
                transaction_id,
            ),
        )

        payment = cursor.fetchone()

        if not payment:

            cursor.execute(
                f"""
                SELECT *
                FROM {BILL_PAYMENT_TABLE}
                WHERE owner_id = %s
                  AND bill_id = %s
                  AND due_date = %s
                LIMIT 1
                """,
                (
                    owner_id,
                    bill_id,
                    expected,
                ),
            )

            return {
                "already_paid": True,
                "payment": dict(cursor.fetchone()),
                "bill": bill,
                "transaction": transaction,
            }

        if bill["recurrence"] == "monthly":

            cursor.execute(
                f"""
                UPDATE {BILL_TABLE}
                SET
                    due_date = (
                        due_date + INTERVAL '1 month'
                    )::date,
                    updated_at = NOW()
                WHERE owner_id = %s
                  AND bill_id = %s
                RETURNING *
                """,
                (
                    owner_id,
                    bill_id,
                ),
            )

        else:

            cursor.execute(
                f"""
                UPDATE {BILL_TABLE}
                SET
                    active = FALSE,
                    updated_at = NOW()
                WHERE owner_id = %s
                  AND bill_id = %s
                RETURNING *
                """,
                (
                    owner_id,
                    bill_id,
                ),
            )

        updated_bill = cursor.fetchone()

        return {
            "already_paid": False,
            "payment": dict(payment),
            "bill": (
                dict(updated_bill)
                if updated_bill
                else None
            ),
            "transaction": transaction,
        }

# SABINO_BILL_PAYMENT_HISTORY_V1

def list_finance_bill_payments(
    *,
    owner_id: str,
    bill_id: str,
) -> list[dict]:

    ensure_finance_bill_payment_schema()

    owner_id = str(owner_id).strip()
    bill_id = str(bill_id).strip()

    if not owner_id or not bill_id:
        raise ValueError(
            "owner_id e bill_id são obrigatórios"
        )

    sql = f"""
    SELECT
        payment_id,
        bill_id,
        owner_id,
        due_date,
        paid_at,
        amount,
        transaction_id,
        created_at
    FROM {BILL_PAYMENT_TABLE}
    WHERE owner_id = %s
      AND bill_id = %s
    ORDER BY paid_at DESC, created_at DESC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                bill_id,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

# SABINO_FINANCE_ASSETS_V1

ASSET_TABLE = "inna_finance_assets"

FINANCE_ASSET_TYPES = {
    "Conta corrente",
    "Poupança",
    "Investimentos",
    "Veículo",
    "Imóvel",
    "Previdência",
    "Dinheiro",
    "Outros",
}


def ensure_finance_asset_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {ASSET_TABLE} (
        asset_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,

        name TEXT NOT NULL,
        asset_type TEXT NOT NULL,

        value NUMERIC(14,2) NOT NULL
            CHECK (value >= 0),

        institution TEXT NULL,

        active BOOLEAN NOT NULL DEFAULT TRUE,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    index_sql = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_finance_assets_owner
    ON {ASSET_TABLE} (
        owner_id,
        active
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql)
        cursor.execute(index_sql)


def create_finance_asset(
    *,
    owner_id: str,
    name: str,
    asset_type: str,
    value,
    institution: str = "",
) -> dict:

    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    ensure_finance_asset_schema()

    owner_id = str(owner_id).strip()
    name = str(name).strip()
    asset_type = str(asset_type).strip()
    institution = str(institution or "").strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not name:
        raise ValueError("nome do ativo é obrigatório")

    if asset_type not in FINANCE_ASSET_TYPES:
        raise ValueError("tipo de ativo inválido")

    try:
        normalized_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("valor do ativo inválido")

    if normalized_value < 0:
        raise ValueError(
            "valor do ativo não pode ser negativo"
        )

    sql = f"""
    INSERT INTO {ASSET_TABLE} (
        asset_id,
        owner_id,
        name,
        asset_type,
        value,
        institution
    )
    VALUES (%s, %s, %s, %s, %s, %s)

    RETURNING
        asset_id,
        owner_id,
        name,
        asset_type,
        value,
        institution,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                name,
                asset_type,
                normalized_value,
                institution or None,
            ),
        )

        return dict(cursor.fetchone())


def list_finance_assets(
    *,
    owner_id: str,
) -> list[dict]:

    ensure_finance_asset_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    sql = f"""
    SELECT
        asset_id,
        owner_id,
        name,
        asset_type,
        value,
        institution,
        active,
        created_at,
        updated_at
    FROM {ASSET_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY value DESC, name ASC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


# SABINO_FINANCE_ASSET_CRUD_V2

def update_finance_asset(
    *,
    owner_id: str,
    asset_id: str,
    name: str,
    asset_type: str,
    value,
    institution: str = "",
) -> dict:

    from decimal import Decimal, InvalidOperation

    ensure_finance_asset_schema()

    owner_id = str(owner_id).strip()
    asset_id = str(asset_id).strip()
    name = str(name).strip()
    asset_type = str(asset_type).strip()
    institution = str(institution or "").strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not asset_id:
        raise ValueError("asset_id é obrigatório")

    if not name:
        raise ValueError("nome do ativo é obrigatório")

    if asset_type not in FINANCE_ASSET_TYPES:
        raise ValueError("tipo de ativo inválido")

    try:
        normalized_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("valor do ativo inválido")

    if normalized_value < 0:
        raise ValueError(
            "valor do ativo não pode ser negativo"
        )

    sql = f"""
    UPDATE {ASSET_TABLE}
    SET
        name = %s,
        asset_type = %s,
        value = %s,
        institution = %s,
        updated_at = NOW()
    WHERE asset_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING
        asset_id,
        owner_id,
        name,
        asset_type,
        value,
        institution,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                name,
                asset_type,
                normalized_value,
                institution,
                asset_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "ativo não encontrado"
            )

        return dict(row)


def delete_finance_asset(
    *,
    owner_id: str,
    asset_id: str,
) -> dict:

    ensure_finance_asset_schema()

    owner_id = str(owner_id).strip()
    asset_id = str(asset_id).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not asset_id:
        raise ValueError("asset_id é obrigatório")

    sql = f"""
    UPDATE {ASSET_TABLE}
    SET
        active = FALSE,
        updated_at = NOW()
    WHERE asset_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING
        asset_id,
        owner_id,
        name,
        asset_type,
        value,
        institution,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                asset_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "ativo não encontrado"
            )

        return dict(row)


# SABINO_FINANCE_INSURANCE_V1

INSURANCE_POLICY_TABLE = "inna_finance_insurance_policies"

FINANCE_INSURANCE_TYPES = {
    "Automóvel",
    "Vida",
    "Residencial",
    "Saúde",
    "Prestamista",
    "Viagem",
    "Empresarial",
    "Outros",
}

FINANCE_INSURANCE_FREQUENCIES = {
    "Mensal",
    "Anual",
}


def ensure_finance_insurance_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {INSURANCE_POLICY_TABLE} (
        policy_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,

        name TEXT NOT NULL,
        insurance_type TEXT NOT NULL,
        provider TEXT NOT NULL,

        coverage_amount NUMERIC(14,2) NOT NULL
            CHECK (coverage_amount >= 0),

        premium_amount NUMERIC(14,2) NOT NULL
            CHECK (premium_amount >= 0),

        premium_frequency TEXT NOT NULL,

        start_date DATE NULL,
        end_date DATE NULL,

        linked_asset_id TEXT NULL,
        insured_item TEXT NULL,

        active BOOLEAN NOT NULL DEFAULT TRUE,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    index_sql = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_finance_insurance_owner
    ON {INSURANCE_POLICY_TABLE} (
        owner_id,
        active
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql)
        cursor.execute(index_sql)


def create_finance_insurance_policy(
    *,
    owner_id: str,
    name: str,
    insurance_type: str,
    provider: str,
    coverage_amount,
    premium_amount,
    premium_frequency: str,
    start_date=None,
    end_date=None,
    linked_asset_id=None,
    insured_item="",
) -> dict:

    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    ensure_finance_insurance_schema()

    owner_id = str(owner_id).strip()
    name = str(name).strip()
    insurance_type = str(insurance_type).strip()
    provider = str(provider).strip()
    premium_frequency = str(premium_frequency).strip()
    insured_item = str(insured_item or "").strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not name:
        raise ValueError("nome do seguro é obrigatório")

    if insurance_type not in FINANCE_INSURANCE_TYPES:
        raise ValueError("tipo de seguro inválido")

    if not provider:
        raise ValueError("seguradora é obrigatória")

    if premium_frequency not in FINANCE_INSURANCE_FREQUENCIES:
        raise ValueError("frequência do prêmio inválida")

    try:
        coverage = Decimal(str(coverage_amount))
        premium = Decimal(str(premium_amount))
    except (InvalidOperation, ValueError):
        raise ValueError("valor financeiro inválido")

    if coverage < 0:
        raise ValueError("cobertura não pode ser negativa")

    if premium < 0:
        raise ValueError("prêmio não pode ser negativo")

    policy_id = uuid4().hex

    sql = f"""
    INSERT INTO {INSURANCE_POLICY_TABLE} (
        policy_id,
        owner_id,
        name,
        insurance_type,
        provider,
        coverage_amount,
        premium_amount,
        premium_frequency,
        start_date,
        end_date,
        linked_asset_id,
        insured_item
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s
    )
    RETURNING *
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                policy_id,
                owner_id,
                name,
                insurance_type,
                provider,
                coverage,
                premium,
                premium_frequency,
                start_date or None,
                end_date or None,
                linked_asset_id or None,
                insured_item or None,
            ),
        )

        return dict(cursor.fetchone())


def list_finance_insurance_policies(
    *,
    owner_id: str,
) -> list[dict]:

    ensure_finance_insurance_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    sql = f"""
    SELECT *
    FROM {INSURANCE_POLICY_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY
        end_date ASC NULLS LAST,
        created_at DESC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


# SABINO_FINANCE_INSURANCE_CRUD_V2

def update_finance_insurance_policy(
    *,
    owner_id: str,
    policy_id: str,
    name: str,
    insurance_type: str,
    provider: str,
    coverage_amount,
    premium_amount,
    premium_frequency: str,
    start_date=None,
    end_date=None,
    linked_asset_id=None,
    insured_item="",
) -> dict:

    from datetime import date
    from decimal import Decimal, InvalidOperation

    ensure_finance_insurance_schema()

    owner_id = str(owner_id).strip()
    policy_id = str(policy_id).strip()
    name = str(name).strip()
    insurance_type = str(insurance_type).strip()
    provider = str(provider).strip()
    premium_frequency = str(premium_frequency).strip()
    insured_item = str(insured_item or "").strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not policy_id:
        raise ValueError("policy_id é obrigatório")

    if not name:
        raise ValueError("nome do seguro é obrigatório")

    if insurance_type not in FINANCE_INSURANCE_TYPES:
        raise ValueError("tipo de seguro inválido")

    if not provider:
        raise ValueError("seguradora é obrigatória")

    if premium_frequency not in FINANCE_INSURANCE_FREQUENCIES:
        raise ValueError("frequência do prêmio inválida")

    try:
        coverage = Decimal(str(coverage_amount))
        premium = Decimal(str(premium_amount))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("valor financeiro inválido")

    if coverage < 0:
        raise ValueError("cobertura não pode ser negativa")

    if premium < 0:
        raise ValueError("prêmio não pode ser negativo")

    normalized_start = None
    normalized_end = None

    try:

        if start_date:
            normalized_start = (
                start_date
                if isinstance(start_date, date)
                else date.fromisoformat(str(start_date))
            )

        if end_date:
            normalized_end = (
                end_date
                if isinstance(end_date, date)
                else date.fromisoformat(str(end_date))
            )

    except ValueError:
        raise ValueError("data da apólice inválida")

    if (
        normalized_start
        and normalized_end
        and normalized_end < normalized_start
    ):
        raise ValueError(
            "vencimento não pode ser anterior ao início"
        )

    sql = f"""
    UPDATE {INSURANCE_POLICY_TABLE}
    SET
        name = %s,
        insurance_type = %s,
        provider = %s,
        coverage_amount = %s,
        premium_amount = %s,
        premium_frequency = %s,
        start_date = %s,
        end_date = %s,
        linked_asset_id = %s,
        insured_item = %s,
        updated_at = NOW()
    WHERE policy_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING *
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                name,
                insurance_type,
                provider,
                coverage,
                premium,
                premium_frequency,
                normalized_start,
                normalized_end,
                linked_asset_id or None,
                insured_item or None,
                policy_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "apólice não encontrada"
            )

        return dict(row)


def renew_finance_insurance_policy(
    *,
    owner_id: str,
    policy_id: str,
    new_end_date,
) -> dict:

    from datetime import date

    ensure_finance_insurance_schema()

    owner_id = str(owner_id).strip()
    policy_id = str(policy_id).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not policy_id:
        raise ValueError("policy_id é obrigatório")

    try:
        normalized_end = (
            new_end_date
            if isinstance(new_end_date, date)
            else date.fromisoformat(
                str(new_end_date)
            )
        )
    except (ValueError, TypeError):
        raise ValueError(
            "nova data de vencimento inválida"
        )

    sql = f"""
    UPDATE {INSURANCE_POLICY_TABLE}
    SET
        end_date = %s,
        updated_at = NOW()
    WHERE policy_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING *
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_end,
                policy_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "apólice não encontrada"
            )

        return dict(row)


def cancel_finance_insurance_policy(
    *,
    owner_id: str,
    policy_id: str,
) -> dict:

    ensure_finance_insurance_schema()

    owner_id = str(owner_id).strip()
    policy_id = str(policy_id).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not policy_id:
        raise ValueError("policy_id é obrigatório")

    sql = f"""
    UPDATE {INSURANCE_POLICY_TABLE}
    SET
        active = FALSE,
        updated_at = NOW()
    WHERE policy_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING *
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                policy_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "apólice não encontrada"
            )

        return dict(row)


# SABINO_FINANCE_INSURANCE_HISTORY_V1

def list_finance_insurance_policy_history(
    *,
    owner_id: str,
) -> list[dict]:

    ensure_finance_insurance_schema()

    owner_id = str(owner_id).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    sql = f"""
    SELECT
        policy_id,
        owner_id,
        name,
        insurance_type,
        provider,
        coverage_amount,
        premium_amount,
        premium_frequency,
        start_date,
        end_date,
        linked_asset_id,
        insured_item,
        active,
        created_at,
        updated_at
    FROM {INSURANCE_POLICY_TABLE}
    WHERE owner_id = %s
      AND active = FALSE
    ORDER BY
        updated_at DESC,
        end_date DESC NULLS LAST,
        name ASC
    """

    with cursor_postgres(
        dict_cursor=True,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


# ============================================================
# SABINO_FINANCE_TAX_OBLIGATIONS_V1
# ============================================================

FINANCE_TAX_OBLIGATION_TABLE = (
    "inna_finance_tax_obligations"
)

FINANCE_TAX_OBLIGATION_TYPES = {
    "IRPF",
    "IPTU",
    "IPVA",
    "DAS / MEI",
    "INSS",
    "Licenciamento",
    "Taxa pública",
    "Outros",
}

FINANCE_TAX_FREQUENCIES = {
    "Única",
    "Mensal",
    "Anual",
}


def ensure_finance_tax_obligation_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {FINANCE_TAX_OBLIGATION_TABLE} (

        obligation_id TEXT PRIMARY KEY,

        owner_id TEXT NOT NULL,

        name TEXT NOT NULL,

        obligation_type TEXT NOT NULL,

        authority_name TEXT,

        reference_label TEXT,

        amount NUMERIC(14,2)
            NOT NULL
            DEFAULT 0
            CHECK (amount >= 0),

        due_date DATE,

        frequency TEXT NOT NULL,

        document_reference TEXT,

        notes TEXT,

        paid BOOLEAN
            NOT NULL
            DEFAULT FALSE,

        paid_at DATE,

        active BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        updated_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW()
    )
    """

    index_sql = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_finance_tax_obligations_owner
    ON {FINANCE_TAX_OBLIGATION_TABLE}
        (owner_id, active, due_date)
    """

    with cursor_postgres(
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql)
        cursor.execute(index_sql)


def create_finance_tax_obligation(
    *,
    owner_id: str,
    name: str,
    obligation_type: str,
    amount,
    frequency: str,
    due_date=None,
    authority_name="",
    reference_label="",
    document_reference="",
    notes="",
) -> dict:

    from datetime import date
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    ensure_finance_tax_obligation_schema()

    owner_id = str(owner_id).strip()
    name = str(name).strip()

    obligation_type = str(
        obligation_type
    ).strip()

    frequency = str(
        frequency
    ).strip()

    if not owner_id:
        raise ValueError(
            "owner_id é obrigatório"
        )

    if not name:
        raise ValueError(
            "nome da obrigação é obrigatório"
        )

    if (
        obligation_type
        not in FINANCE_TAX_OBLIGATION_TYPES
    ):
        raise ValueError(
            "tipo de obrigação inválido"
        )

    if (
        frequency
        not in FINANCE_TAX_FREQUENCIES
    ):
        raise ValueError(
            "frequência inválida"
        )

    try:
        normalized_amount = Decimal(
            str(amount)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        raise ValueError(
            "valor inválido"
        )

    if normalized_amount < 0:
        raise ValueError(
            "valor não pode ser negativo"
        )

    normalized_due_date = None

    if due_date:

        try:
            normalized_due_date = (
                due_date
                if isinstance(due_date, date)
                else date.fromisoformat(
                    str(due_date)
                )
            )

        except ValueError:
            raise ValueError(
                "data de vencimento inválida"
            )

    obligation_id = uuid4().hex

    sql = f"""
    INSERT INTO {FINANCE_TAX_OBLIGATION_TABLE} (
        obligation_id,
        owner_id,
        name,
        obligation_type,
        authority_name,
        reference_label,
        amount,
        due_date,
        frequency,
        document_reference,
        notes
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    RETURNING *
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                obligation_id,
                owner_id,
                name,
                obligation_type,
                str(
                    authority_name or ""
                ).strip() or None,
                str(
                    reference_label or ""
                ).strip() or None,
                normalized_amount,
                normalized_due_date,
                frequency,
                str(
                    document_reference or ""
                ).strip() or None,
                str(
                    notes or ""
                ).strip() or None,
            ),
        )

        row = cursor.fetchone()

        return dict(row)


def list_finance_tax_obligations(
    *,
    owner_id: str,
) -> list[dict]:

    ensure_finance_tax_obligation_schema()

    owner_id = str(
        owner_id
    ).strip()

    if not owner_id:
        raise ValueError(
            "owner_id é obrigatório"
        )

    sql = f"""
    SELECT *
    FROM {FINANCE_TAX_OBLIGATION_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY
        paid ASC,
        due_date ASC NULLS LAST,
        name ASC
    """

    with cursor_postgres(
        dict_cursor=True,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


def mark_finance_tax_obligation_paid(
    *,
    owner_id: str,
    obligation_id: str,
    paid_at=None,
) -> dict:

    from datetime import date

    ensure_finance_tax_obligation_schema()

    owner_id = str(
        owner_id
    ).strip()

    obligation_id = str(
        obligation_id
    ).strip()

    if not owner_id:
        raise ValueError(
            "owner_id é obrigatório"
        )

    if not obligation_id:
        raise ValueError(
            "obligation_id é obrigatório"
        )

    normalized_paid_at = (
        date.today()
    )

    if paid_at:

        try:
            normalized_paid_at = (
                paid_at
                if isinstance(paid_at, date)
                else date.fromisoformat(
                    str(paid_at)
                )
            )

        except ValueError:
            raise ValueError(
                "data de pagamento inválida"
            )

    sql = f"""
    UPDATE {FINANCE_TAX_OBLIGATION_TABLE}
    SET
        paid = TRUE,
        paid_at = %s,
        updated_at = NOW()
    WHERE obligation_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING *
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_paid_at,
                obligation_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "obrigação não encontrada"
            )

        return dict(row)

# ============================================================
# SABINO_FINANCE_INVESTMENTS_SCHEMA_V1
# ============================================================

FINANCE_INVESTMENT_TABLE = "inna_finance_investments"

FINANCE_INVESTMENT_TYPES = {
    "Tesouro Direto",
    "CDB",
    "LCI / LCA",
    "Poupança",
    "Fundo de Investimento",
    "Ações",
    "ETF",
    "FII",
    "Previdência",
    "Cripto",
    "Outros",
}

FINANCE_INVESTMENT_LIQUIDITIES = {
    "Diária",
    "D+1",
    "D+2",
    "D+30",
    "No vencimento",
    "Variável",
}


def ensure_finance_investment_schema():
    sql = f"""
    CREATE TABLE IF NOT EXISTS {FINANCE_INVESTMENT_TABLE} (
        investment_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,

        name TEXT NOT NULL,
        investment_type TEXT NOT NULL,
        institution TEXT,

        invested_amount NUMERIC(18,2) NOT NULL
            CHECK (invested_amount >= 0),

        current_value NUMERIC(18,2) NOT NULL
            CHECK (current_value >= 0),

        liquidity TEXT,
        objective TEXT,
        maturity_date DATE,

        active BOOLEAN NOT NULL DEFAULT TRUE,

        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS
        idx_inna_finance_investments_owner
    ON {FINANCE_INVESTMENT_TABLE} (
        owner_id,
        active
    );
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(sql)

# ============================================================
# SABINO_FINANCE_INVESTMENTS_REPOSITORY_V1
# ============================================================

def create_finance_investment(
    *,
    owner_id,
    name,
    investment_type,
    institution=None,
    invested_amount=0,
    current_value=None,
    liquidity=None,
    objective=None,
    maturity_date=None,
):
    from datetime import date
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    owner_id = str(owner_id or "").strip()
    name = str(name or "").strip()
    investment_type = str(
        investment_type or ""
    ).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not name:
        raise ValueError(
            "nome do investimento é obrigatório"
        )

    if investment_type not in FINANCE_INVESTMENT_TYPES:
        raise ValueError(
            "tipo de investimento inválido"
        )

    try:
        invested_amount = Decimal(
            str(invested_amount)
        )
    except (InvalidOperation, TypeError):
        raise ValueError(
            "valor investido inválido"
        )

    if invested_amount < 0:
        raise ValueError(
            "valor investido não pode ser negativo"
        )

    if current_value in (None, ""):
        current_value = invested_amount

    try:
        current_value = Decimal(
            str(current_value)
        )
    except (InvalidOperation, TypeError):
        raise ValueError(
            "valor atual inválido"
        )

    if current_value < 0:
        raise ValueError(
            "valor atual não pode ser negativo"
        )

    institution = str(
        institution or ""
    ).strip() or None

    objective = str(
        objective or ""
    ).strip() or None

    liquidity = str(
        liquidity or ""
    ).strip() or None

    if (
        liquidity
        and liquidity
        not in FINANCE_INVESTMENT_LIQUIDITIES
    ):
        raise ValueError(
            "liquidez inválida"
        )

    if maturity_date:
        if isinstance(maturity_date, str):
            try:
                maturity_date = date.fromisoformat(
                    maturity_date
                )
            except ValueError:
                raise ValueError(
                    "data de vencimento inválida"
                )
    else:
        maturity_date = None

    ensure_finance_investment_schema()

    investment_id = uuid4().hex

    sql = f"""
    INSERT INTO {FINANCE_INVESTMENT_TABLE} (
        investment_id,
        owner_id,
        name,
        investment_type,
        institution,
        invested_amount,
        current_value,
        liquidity,
        objective,
        maturity_date
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s
    )
    RETURNING
        investment_id,
        owner_id,
        name,
        investment_type,
        institution,
        invested_amount,
        current_value,
        liquidity,
        objective,
        maturity_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                investment_id,
                owner_id,
                name,
                investment_type,
                institution,
                invested_amount,
                current_value,
                liquidity,
                objective,
                maturity_date,
            ),
        )

        return dict(cursor.fetchone())


def list_finance_investments(
    *,
    owner_id,
):
    owner_id = str(owner_id or "").strip()

    if not owner_id:
        raise ValueError(
            "owner_id é obrigatório"
        )

    ensure_finance_investment_schema()

    sql = f"""
    SELECT
        investment_id,
        owner_id,
        name,
        investment_type,
        institution,
        invested_amount,
        current_value,
        liquidity,
        objective,
        maturity_date,
        active,
        created_at,
        updated_at
    FROM {FINANCE_INVESTMENT_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    ORDER BY
        current_value DESC,
        created_at DESC
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


def summarize_finance_investments(
    *,
    owner_id,
):
    from decimal import Decimal

    owner_id = str(owner_id or "").strip()

    if not owner_id:
        raise ValueError(
            "owner_id é obrigatório"
        )

    ensure_finance_investment_schema()

    sql = f"""
    SELECT
        COUNT(*) AS investment_count,

        COALESCE(
            SUM(invested_amount),
            0
        ) AS total_invested,

        COALESCE(
            SUM(current_value),
            0
        ) AS current_total

    FROM {FINANCE_INVESTMENT_TABLE}
    WHERE owner_id = %s
      AND active = TRUE
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        row = dict(cursor.fetchone())

    total_invested = Decimal(
        str(row["total_invested"])
    )

    current_total = Decimal(
        str(row["current_total"])
    )

    gain_loss = (
        current_total
        - total_invested
    )

    if total_invested > 0:
        gain_percentage = (
            gain_loss
            / total_invested
            * Decimal("100")
        )
    else:
        gain_percentage = Decimal("0")

    return {
        "investment_count":
            int(row["investment_count"]),

        "total_invested":
            total_invested,

        "current_total":
            current_total,

        "gain_loss":
            gain_loss,

        "gain_percentage":
            gain_percentage,
    }

# ============================================================
# SABINO_FINANCE_INVESTMENTS_CRUD_V2
# ============================================================

def update_finance_investment(
    *,
    owner_id,
    investment_id,
    name,
    investment_type,
    institution=None,
    invested_amount=0,
    current_value=None,
    liquidity=None,
    objective=None,
    maturity_date=None,
):
    from datetime import date
    from decimal import Decimal, InvalidOperation

    ensure_finance_investment_schema()

    owner_id = str(owner_id or "").strip()
    investment_id = str(investment_id or "").strip()
    name = str(name or "").strip()
    investment_type = str(investment_type or "").strip()
    institution = str(institution or "").strip()
    liquidity = str(liquidity or "").strip()
    objective = str(objective or "").strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not investment_id:
        raise ValueError("investment_id é obrigatório")

    if not name:
        raise ValueError(
            "nome do investimento é obrigatório"
        )

    if investment_type not in FINANCE_INVESTMENT_TYPES:
        raise ValueError(
            "tipo de investimento inválido"
        )

    try:
        invested = Decimal(
            str(invested_amount)
        )
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            "valor investido inválido"
        )

    if current_value in (None, ""):
        current = invested
    else:
        try:
            current = Decimal(
                str(current_value)
            )
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):
            raise ValueError(
                "valor atual inválido"
            )

    if invested < 0 or current < 0:
        raise ValueError(
            "valores não podem ser negativos"
        )

    if (
        liquidity
        and liquidity
        not in FINANCE_INVESTMENT_LIQUIDITIES
    ):
        raise ValueError(
            "liquidez inválida"
        )

    normalized_maturity = None

    if maturity_date not in (None, ""):
        if isinstance(maturity_date, date):
            normalized_maturity = maturity_date
        else:
            try:
                normalized_maturity = date.fromisoformat(
                    str(maturity_date)
                )
            except ValueError:
                raise ValueError(
                    "data de vencimento inválida"
                )

    sql = f"""
    UPDATE {FINANCE_INVESTMENT_TABLE}
    SET
        name = %s,
        investment_type = %s,
        institution = %s,
        invested_amount = %s,
        current_value = %s,
        liquidity = %s,
        objective = %s,
        maturity_date = %s,
        updated_at = NOW()
    WHERE investment_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING
        investment_id,
        owner_id,
        name,
        investment_type,
        institution,
        invested_amount,
        current_value,
        liquidity,
        objective,
        maturity_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                name,
                investment_type,
                institution or None,
                invested,
                current,
                liquidity or None,
                objective or None,
                normalized_maturity,
                investment_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "investimento não encontrado"
            )

        return dict(row)


def delete_finance_investment(
    *,
    owner_id,
    investment_id,
):
    ensure_finance_investment_schema()

    owner_id = str(owner_id or "").strip()
    investment_id = str(
        investment_id or ""
    ).strip()

    if not owner_id:
        raise ValueError(
            "owner_id é obrigatório"
        )

    if not investment_id:
        raise ValueError(
            "investment_id é obrigatório"
        )

    sql = f"""
    UPDATE {FINANCE_INVESTMENT_TABLE}
    SET
        active = FALSE,
        updated_at = NOW()
    WHERE investment_id = %s
      AND owner_id = %s
      AND active = TRUE
    RETURNING
        investment_id,
        owner_id,
        name,
        investment_type,
        institution,
        invested_amount,
        current_value,
        liquidity,
        objective,
        maturity_date,
        active,
        created_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                investment_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

        if not row:
            raise ValueError(
                "investimento não encontrado"
            )

        return dict(row)


# ============================================================
# SABINO_FINANCE_EDUCATION_PROGRESS_REPOSITORY_V1
# ============================================================

EDUCATION_PROGRESS_TABLE = "inna_finance_education_progress"

EDUCATION_TRACK_IDS = (
    "orcamento",
    "reserva",
    "credito",
    "investimentos",
    "seguranca",
)


def ensure_finance_education_progress_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {EDUCATION_PROGRESS_TABLE} (
        owner_id TEXT NOT NULL,
        track_id TEXT NOT NULL,

        completed BOOLEAN NOT NULL DEFAULT FALSE,

        quiz_score INTEGER NOT NULL DEFAULT 0
            CHECK (
                quiz_score >= 0
                AND quiz_score <= 100
            ),

        completed_at TIMESTAMPTZ NULL,

        updated_at TIMESTAMPTZ NOT NULL
            DEFAULT NOW(),

        PRIMARY KEY (
            owner_id,
            track_id
        )
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql)


def list_finance_education_progress(
    *,
    owner_id: str,
) -> list[dict]:

    owner_id = str(owner_id or "").strip()

    if not owner_id:
        raise ValueError(
            "owner_id obrigatório"
        )

    ensure_finance_education_progress_schema()

    sql = f"""
    SELECT
        track_id,
        completed,
        quiz_score,
        completed_at,
        updated_at
    FROM {EDUCATION_PROGRESS_TABLE}
    WHERE owner_id = %s
    ORDER BY track_id
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (owner_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


def upsert_finance_education_progress(
    *,
    owner_id: str,
    track_id: str,
    quiz_score: int,
) -> dict:

    owner_id = str(owner_id or "").strip()
    track_id = str(track_id or "").strip()

    if not owner_id:
        raise ValueError(
            "owner_id obrigatório"
        )

    if track_id not in EDUCATION_TRACK_IDS:
        raise ValueError(
            "trilha de educação financeira inválida"
        )

    try:
        quiz_score = int(quiz_score)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "quiz_score inválido"
        ) from exc

    if quiz_score < 0 or quiz_score > 100:
        raise ValueError(
            "quiz_score deve estar entre 0 e 100"
        )

    completed = (
        quiz_score >= 100
    )

    ensure_finance_education_progress_schema()

    sql = f"""
    INSERT INTO {EDUCATION_PROGRESS_TABLE} (
        owner_id,
        track_id,
        completed,
        quiz_score,
        completed_at,
        updated_at
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        CASE
            WHEN %s
            THEN NOW()
            ELSE NULL
        END,
        NOW()
    )
    ON CONFLICT (
        owner_id,
        track_id
    )
    DO UPDATE SET
        completed =
            EXCLUDED.completed,

        quiz_score =
            EXCLUDED.quiz_score,

        completed_at =
            CASE
                WHEN
                    EXCLUDED.completed
                    AND {EDUCATION_PROGRESS_TABLE}.completed_at IS NULL
                THEN NOW()

                WHEN NOT EXCLUDED.completed
                THEN NULL

                ELSE
                    {EDUCATION_PROGRESS_TABLE}.completed_at
            END,

        updated_at =
            NOW()

    RETURNING
        track_id,
        completed,
        quiz_score,
        completed_at,
        updated_at
    """

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                track_id,
                completed,
                quiz_score,
                completed,
            ),
        )

        return dict(
            cursor.fetchone()
        )

# ============================================================
# SABINO_FINANCE_CENTRAL_ACCOUNTS_REPOSITORY_V1
# ============================================================

CENTRAL_ACCOUNTS_TABLE = "inna_finance_central_accounts"


def ensure_finance_central_accounts_schema():
    """Cria a estrutura da Central de Contas."""

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {CENTRAL_ACCOUNTS_TABLE} (

                id TEXT PRIMARY KEY,

                owner_id TEXT NOT NULL,

                institution TEXT NOT NULL,

                account_name TEXT NOT NULL,

                account_type TEXT NOT NULL,

                current_balance NUMERIC(18, 2)
                    NOT NULL
                    DEFAULT 0,

                currency VARCHAR(3)
                    NOT NULL
                    DEFAULT 'BRL',

                is_active BOOLEAN
                    NOT NULL
                    DEFAULT TRUE,

                source TEXT
                    NOT NULL
                    DEFAULT 'manual',

                external_account_id TEXT NULL,

                created_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT NOW(),

                updated_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT NOW(),

                CONSTRAINT finance_central_account_source_check
                    CHECK (
                        source IN (
                            'manual',
                            'open_finance'
                        )
                    )
            )
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_central_accounts_owner
            ON {CENTRAL_ACCOUNTS_TABLE}(owner_id)
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_central_accounts_owner_active
            ON {CENTRAL_ACCOUNTS_TABLE}(
                owner_id,
                is_active
            )
            """
        )


def list_finance_central_accounts(
    owner_id: str,
):

    ensure_finance_central_accounts_schema()

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            f"""
            SELECT
                id,
                institution,
                account_name,
                account_type,
                current_balance,
                currency,
                is_active,
                source,
                created_at,
                updated_at
            FROM {CENTRAL_ACCOUNTS_TABLE}
            WHERE owner_id = %s
            ORDER BY
                is_active DESC,
                institution ASC,
                account_name ASC
            """,
            (
                owner_id,
            ),
        )

        return cursor.fetchall()


def create_finance_central_account(
    owner_id: str,
    institution: str,
    account_name: str,
    account_type: str,
    current_balance=0,
):

    from uuid import uuid4
    from decimal import Decimal, InvalidOperation

    institution = str(
        institution or ""
    ).strip()

    account_name = str(
        account_name or ""
    ).strip()

    account_type = str(
        account_type or ""
    ).strip()

    if not institution:
        raise ValueError(
            "Instituição obrigatória."
        )

    if not account_name:
        raise ValueError(
            "Nome da conta obrigatório."
        )

    if not account_type:
        raise ValueError(
            "Tipo da conta obrigatório."
        )

    try:
        balance = Decimal(
            str(current_balance or 0)
        ).quantize(
            Decimal("0.01")
        )
    except InvalidOperation:
        raise ValueError(
            "Saldo inválido."
        )

    ensure_finance_central_accounts_schema()

    account_id = str(
        uuid4()
    )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            INSERT INTO {CENTRAL_ACCOUNTS_TABLE} (
                id,
                owner_id,
                institution,
                account_name,
                account_type,
                current_balance,
                currency,
                is_active,
                source
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'BRL',
                TRUE,
                'manual'
            )
            RETURNING
                id,
                institution,
                account_name,
                account_type,
                current_balance,
                currency,
                is_active,
                source,
                created_at,
                updated_at
            """,
            (
                account_id,
                owner_id,
                institution,
                account_name,
                account_type,
                balance,
            ),
        )

        return cursor.fetchone()

# ============================================================
# SABINO_FINANCE_CENTRAL_ACCOUNTS_CRUD_V2
# ============================================================

def update_finance_central_account(
    owner_id: str,
    account_id: str,
    institution: str,
    account_name: str,
    account_type: str,
    current_balance=0,
):

    from decimal import Decimal, InvalidOperation

    institution = str(
        institution or ""
    ).strip()

    account_name = str(
        account_name or ""
    ).strip()

    account_type = str(
        account_type or ""
    ).strip()

    if not institution:
        raise ValueError(
            "Instituição obrigatória."
        )

    if not account_name:
        raise ValueError(
            "Nome da conta obrigatório."
        )

    if not account_type:
        raise ValueError(
            "Tipo da conta obrigatório."
        )

    try:

        balance = Decimal(
            str(current_balance or 0)
        ).quantize(
            Decimal("0.01")
        )

    except InvalidOperation:

        raise ValueError(
            "Saldo inválido."
        )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            UPDATE {CENTRAL_ACCOUNTS_TABLE}
            SET
                institution = %s,
                account_name = %s,
                account_type = %s,
                current_balance = %s,
                updated_at = NOW()
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                institution,
                account_name,
                account_type,
                current_balance,
                currency,
                is_active,
                source,
                created_at,
                updated_at
            """,
            (
                institution,
                account_name,
                account_type,
                balance,
                account_id,
                owner_id,
            ),
        )

        return cursor.fetchone()


def set_finance_central_account_active(
    owner_id: str,
    account_id: str,
    is_active: bool,
):

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            UPDATE {CENTRAL_ACCOUNTS_TABLE}
            SET
                is_active = %s,
                updated_at = NOW()
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                institution,
                account_name,
                account_type,
                current_balance,
                currency,
                is_active,
                source,
                created_at,
                updated_at
            """,
            (
                bool(is_active),
                account_id,
                owner_id,
            ),
        )

        return cursor.fetchone()


def delete_finance_central_account(
    owner_id: str,
    account_id: str,
):

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            DELETE FROM {CENTRAL_ACCOUNTS_TABLE}
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING id
            """,
            (
                account_id,
                owner_id,
            ),
        )

        return cursor.fetchone()

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBERS_REPOSITORY_V1
# ============================================================

FAMILY_MEMBERS_TABLE = "inna_finance_family_members"


def ensure_finance_family_members_schema():

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {FAMILY_MEMBERS_TABLE} (

                id TEXT PRIMARY KEY,

                owner_id TEXT NOT NULL,

                member_name TEXT NOT NULL,

                relation TEXT NOT NULL,

                monthly_contribution NUMERIC(18, 2)
                    NOT NULL
                    DEFAULT 0,

                expense_share_percent NUMERIC(5, 2)
                    NOT NULL
                    DEFAULT 0,

                is_active BOOLEAN
                    NOT NULL
                    DEFAULT TRUE,

                linked_user_id TEXT NULL,

                created_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT NOW(),

                updated_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT NOW(),

                CONSTRAINT family_contribution_nonnegative
                    CHECK (monthly_contribution >= 0),

                CONSTRAINT family_share_range
                    CHECK (
                        expense_share_percent >= 0
                        AND expense_share_percent <= 100
                    )
            )
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_family_members_owner
            ON {FAMILY_MEMBERS_TABLE}(owner_id)
            """
        )


def list_finance_family_members(
    owner_id: str,
):

    ensure_finance_family_members_schema()

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            f"""
            SELECT
                id,
                member_name,
                relation,
                monthly_contribution,
                expense_share_percent,
                is_active,
                linked_user_id,
                created_at,
                updated_at
            FROM {FAMILY_MEMBERS_TABLE}
            WHERE owner_id = %s
            ORDER BY
                is_active DESC,
                member_name ASC
            """,
            (
                owner_id,
            ),
        )

        return cursor.fetchall()


def create_finance_family_member(
    owner_id: str,
    member_name: str,
    relation: str,
    monthly_contribution=0,
    expense_share_percent=0,
):

    from uuid import uuid4
    from decimal import Decimal, InvalidOperation

    member_name = str(
        member_name or ""
    ).strip()

    relation = str(
        relation or ""
    ).strip()

    if not member_name:
        raise ValueError(
            "Nome do membro obrigatório."
        )

    if not relation:
        raise ValueError(
            "Vínculo obrigatório."
        )

    try:
        contribution = Decimal(
            str(monthly_contribution or 0)
        ).quantize(
            Decimal("0.01")
        )

        share = Decimal(
            str(expense_share_percent or 0)
        ).quantize(
            Decimal("0.01")
        )

    except InvalidOperation:
        raise ValueError(
            "Valores financeiros inválidos."
        )

    if contribution < 0:
        raise ValueError(
            "Contribuição não pode ser negativa."
        )

    if share < 0 or share > 100:
        raise ValueError(
            "Participação deve ficar entre 0 e 100."
        )

    ensure_finance_family_members_schema()

    member_id = str(
        uuid4()
    )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            INSERT INTO {FAMILY_MEMBERS_TABLE} (
                id,
                owner_id,
                member_name,
                relation,
                monthly_contribution,
                expense_share_percent,
                is_active
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                TRUE
            )
            RETURNING
                id,
                member_name,
                relation,
                monthly_contribution,
                expense_share_percent,
                is_active,
                linked_user_id,
                created_at,
                updated_at
            """,
            (
                member_id,
                owner_id,
                member_name,
                relation,
                contribution,
                share,
            ),
        )

        return cursor.fetchone()

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBER_UPDATE_V2
# ============================================================

def update_finance_family_member(
    owner_id: str,
    member_id: str,
    member_name: str,
    relation: str,
    monthly_contribution=0,
    expense_share_percent=0,
):

    from decimal import Decimal, InvalidOperation

    member_name = str(
        member_name or ""
    ).strip()

    relation = str(
        relation or ""
    ).strip()

    if not member_name:
        raise ValueError(
            "Nome do membro obrigatório."
        )

    if not relation:
        raise ValueError(
            "Vínculo obrigatório."
        )

    try:
        contribution = Decimal(
            str(monthly_contribution or 0)
        ).quantize(
            Decimal("0.01")
        )

        share = Decimal(
            str(expense_share_percent or 0)
        ).quantize(
            Decimal("0.01")
        )

    except InvalidOperation:
        raise ValueError(
            "Valores inválidos."
        )

    if contribution < 0:
        raise ValueError(
            "Contribuição não pode ser negativa."
        )

    if share < 0 or share > 100:
        raise ValueError(
            "Participação deve ficar entre 0 e 100."
        )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            UPDATE {FAMILY_MEMBERS_TABLE}
            SET
                member_name = %s,
                relation = %s,
                monthly_contribution = %s,
                expense_share_percent = %s,
                updated_at = NOW()
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                member_name,
                relation,
                monthly_contribution,
                expense_share_percent,
                is_active,
                linked_user_id,
                created_at,
                updated_at
            """,
            (
                member_name,
                relation,
                contribution,
                share,
                member_id,
                owner_id,
            ),
        )

        return cursor.fetchone()

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBER_ACTIVE_V2
# ============================================================

def set_finance_family_member_active(
    owner_id: str,
    member_id: str,
    is_active: bool,
):

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            UPDATE {FAMILY_MEMBERS_TABLE}
            SET
                is_active = %s,
                updated_at = NOW()
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                member_name,
                relation,
                monthly_contribution,
                expense_share_percent,
                is_active,
                linked_user_id,
                created_at,
                updated_at
            """,
            (
                bool(is_active),
                member_id,
                owner_id,
            ),
        )

        return cursor.fetchone()

# ============================================================
# SABINO_FINANCE_FAMILY_MEMBER_DELETE_V2
# ============================================================

def delete_finance_family_member(
    owner_id: str,
    member_id: str,
):

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            DELETE FROM {FAMILY_MEMBERS_TABLE}
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                member_name
            """,
            (
                member_id,
                owner_id,
            ),
        )

        return cursor.fetchone()


# ============================================================
# SABINO_FINANCE_FAMILY_EXPENSES_REPOSITORY_V1
# ============================================================

FAMILY_EXPENSES_TABLE = "inna_finance_family_expenses"


def ensure_finance_family_expenses_schema():

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {FAMILY_EXPENSES_TABLE} (

                id TEXT PRIMARY KEY,

                owner_id TEXT NOT NULL,

                description TEXT NOT NULL,

                category TEXT NOT NULL,

                amount NUMERIC(18, 2)
                    NOT NULL
                    DEFAULT 0,

                due_date DATE NULL,

                responsible_member_id TEXT NULL,

                recurrence TEXT
                    NOT NULL
                    DEFAULT 'once',

                status TEXT
                    NOT NULL
                    DEFAULT 'pending',

                notes TEXT NULL,

                created_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT NOW(),

                updated_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT NOW(),

                CONSTRAINT family_expense_amount_nonnegative
                    CHECK (amount >= 0),

                CONSTRAINT family_expense_recurrence_valid
                    CHECK (
                        recurrence IN (
                            'once',
                            'weekly',
                            'monthly',
                            'yearly'
                        )
                    ),

                CONSTRAINT family_expense_status_valid
                    CHECK (
                        status IN (
                            'pending',
                            'paid',
                            'overdue',
                            'cancelled'
                        )
                    )
            )
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_family_expenses_owner
            ON {FAMILY_EXPENSES_TABLE}(owner_id)
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_family_expenses_owner_status
            ON {FAMILY_EXPENSES_TABLE}(
                owner_id,
                status
            )
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_family_expenses_due_date
            ON {FAMILY_EXPENSES_TABLE}(
                owner_id,
                due_date
            )
            """
        )


def list_finance_family_expenses(
    owner_id: str,
):

    ensure_finance_family_expenses_schema()

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            f"""
            SELECT
                e.id,
                e.description,
                e.category,
                e.amount,
                e.due_date,
                e.responsible_member_id,
                m.member_name AS responsible_member_name,
                e.recurrence,
                e.status,
                e.notes,
                e.created_at,
                e.updated_at
            FROM {FAMILY_EXPENSES_TABLE} e

            LEFT JOIN {FAMILY_MEMBERS_TABLE} m
                ON m.id = e.responsible_member_id
                AND m.owner_id = e.owner_id

            WHERE
                e.owner_id = %s

            ORDER BY
                CASE
                    WHEN e.status = 'overdue' THEN 1
                    WHEN e.status = 'pending' THEN 2
                    WHEN e.status = 'paid' THEN 3
                    ELSE 4
                END,
                e.due_date ASC NULLS LAST,
                e.created_at DESC
            """,
            (
                owner_id,
            ),
        )

        return cursor.fetchall()


def create_finance_family_expense(
    owner_id: str,
    description: str,
    category: str,
    amount=0,
    due_date=None,
    responsible_member_id=None,
    recurrence="once",
    status="pending",
    notes=None,
):

    from uuid import uuid4
    from decimal import Decimal, InvalidOperation
    from datetime import date

    description = str(
        description or ""
    ).strip()

    category = str(
        category or ""
    ).strip()

    recurrence = str(
        recurrence or "once"
    ).strip().lower()

    status = str(
        status or "pending"
    ).strip().lower()

    responsible_member_id = str(
        responsible_member_id or ""
    ).strip() or None

    notes = str(
        notes or ""
    ).strip() or None

    if not description:
        raise ValueError(
            "Descrição da despesa obrigatória."
        )

    if not category:
        raise ValueError(
            "Categoria obrigatória."
        )

    try:
        amount_decimal = Decimal(
            str(amount or 0)
        ).quantize(
            Decimal("0.01")
        )
    except InvalidOperation:
        raise ValueError(
            "Valor da despesa inválido."
        )

    if amount_decimal < 0:
        raise ValueError(
            "Valor da despesa não pode ser negativo."
        )

    allowed_recurrences = {
        "once",
        "weekly",
        "monthly",
        "yearly",
    }

    if recurrence not in allowed_recurrences:
        raise ValueError(
            "Recorrência inválida."
        )

    allowed_statuses = {
        "pending",
        "paid",
        "overdue",
        "cancelled",
    }

    if status not in allowed_statuses:
        raise ValueError(
            "Status inválido."
        )

    parsed_due_date = None

    if due_date:

        try:
            parsed_due_date = date.fromisoformat(
                str(due_date)
            )
        except ValueError:
            raise ValueError(
                "Data de vencimento inválida."
            )

    ensure_finance_family_expenses_schema()

    expense_id = str(
        uuid4()
    )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            INSERT INTO {FAMILY_EXPENSES_TABLE} (
                id,
                owner_id,
                description,
                category,
                amount,
                due_date,
                responsible_member_id,
                recurrence,
                status,
                notes
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING
                id,
                description,
                category,
                amount,
                due_date,
                responsible_member_id,
                recurrence,
                status,
                notes,
                created_at,
                updated_at
            """,
            (
                expense_id,
                owner_id,
                description,
                category,
                amount_decimal,
                parsed_due_date,
                responsible_member_id,
                recurrence,
                status,
                notes,
            ),
        )

        return cursor.fetchone()


def update_finance_family_expense(
    owner_id: str,
    expense_id: str,
    description: str,
    category: str,
    amount=0,
    due_date=None,
    responsible_member_id=None,
    recurrence="once",
    status="pending",
    notes=None,
):

    from decimal import Decimal, InvalidOperation
    from datetime import date

    description = str(
        description or ""
    ).strip()

    category = str(
        category or ""
    ).strip()

    recurrence = str(
        recurrence or "once"
    ).strip().lower()

    status = str(
        status or "pending"
    ).strip().lower()

    responsible_member_id = str(
        responsible_member_id or ""
    ).strip() or None

    notes = str(
        notes or ""
    ).strip() or None

    if not description:
        raise ValueError(
            "Descrição da despesa obrigatória."
        )

    if not category:
        raise ValueError(
            "Categoria obrigatória."
        )

    try:
        amount_decimal = Decimal(
            str(amount or 0)
        ).quantize(
            Decimal("0.01")
        )
    except InvalidOperation:
        raise ValueError(
            "Valor da despesa inválido."
        )

    if amount_decimal < 0:
        raise ValueError(
            "Valor da despesa não pode ser negativo."
        )

    if recurrence not in {
        "once",
        "weekly",
        "monthly",
        "yearly",
    }:
        raise ValueError(
            "Recorrência inválida."
        )

    if status not in {
        "pending",
        "paid",
        "overdue",
        "cancelled",
    }:
        raise ValueError(
            "Status inválido."
        )

    parsed_due_date = None

    if due_date:
        try:
            parsed_due_date = date.fromisoformat(
                str(due_date)
            )
        except ValueError:
            raise ValueError(
                "Data de vencimento inválida."
            )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            UPDATE {FAMILY_EXPENSES_TABLE}
            SET
                description = %s,
                category = %s,
                amount = %s,
                due_date = %s,
                responsible_member_id = %s,
                recurrence = %s,
                status = %s,
                notes = %s,
                updated_at = NOW()
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                description,
                category,
                amount,
                due_date,
                responsible_member_id,
                recurrence,
                status,
                notes,
                created_at,
                updated_at
            """,
            (
                description,
                category,
                amount_decimal,
                parsed_due_date,
                responsible_member_id,
                recurrence,
                status,
                notes,
                expense_id,
                owner_id,
            ),
        )

        return cursor.fetchone()


def set_finance_family_expense_status(
    owner_id: str,
    expense_id: str,
    status: str,
):

    status = str(
        status or ""
    ).strip().lower()

    if status not in {
        "pending",
        "paid",
        "overdue",
        "cancelled",
    }:
        raise ValueError(
            "Status inválido."
        )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            UPDATE {FAMILY_EXPENSES_TABLE}
            SET
                status = %s,
                updated_at = NOW()
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                description,
                category,
                amount,
                due_date,
                responsible_member_id,
                recurrence,
                status,
                notes,
                created_at,
                updated_at
            """,
            (
                status,
                expense_id,
                owner_id,
            ),
        )

        return cursor.fetchone()


def delete_finance_family_expense(
    owner_id: str,
    expense_id: str,
):

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            DELETE FROM {FAMILY_EXPENSES_TABLE}
            WHERE
                id = %s
                AND owner_id = %s
            RETURNING
                id,
                description
            """,
            (
                expense_id,
                owner_id,
            ),
        )

        return cursor.fetchone()


# ============================================================
# SABINO_FINANCE_GOALS_SCOPE_V2
# Goals pessoais + familiares na mesma tabela
# ============================================================


def ensure_finance_goal_scope_schema():

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            f"""
            ALTER TABLE {GOAL_TABLE}
            ADD COLUMN IF NOT EXISTS
                scope TEXT
                NOT NULL
                DEFAULT 'personal'
            """
        )

        cursor.execute(
            f"""
            ALTER TABLE {GOAL_TABLE}
            ADD COLUMN IF NOT EXISTS
                responsible_member_id TEXT NULL
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                idx_finance_goals_owner_scope
            ON {GOAL_TABLE}(
                owner_id,
                scope,
                active
            )
            """
        )


def _normalize_finance_goal_scope(
    scope,
):

    scope = str(
        scope or "personal"
    ).strip().lower()

    if scope not in {
        "personal",
        "family",
    }:

        raise ValueError(
            "scope deve ser personal ou family"
        )

    return scope


def _validate_family_goal_responsible(
    *,
    owner_id: str,
    responsible_member_id,
):

    responsible_member_id = str(
        responsible_member_id or ""
    ).strip()

    if not responsible_member_id:
        return None

    ensure_finance_family_members_schema()

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            f"""
            SELECT
                id
            FROM {FAMILY_MEMBERS_TABLE}
            WHERE
                id = %s
                AND owner_id = %s
                AND is_active = TRUE
            """,
            (
                responsible_member_id,
                owner_id,
            ),
        )

        row = cursor.fetchone()

    if not row:

        raise ValueError(
            "responsável familiar inválido"
        )

    return responsible_member_id


# ============================================================
# Override compatível do CREATE existente
# ============================================================

def create_finance_goal(
    *,
    owner_id: str,
    name: str,
    target_amount,
    target_date=None,
    scope="personal",
    responsible_member_id=None,
) -> dict:

    from datetime import date
    from decimal import Decimal, InvalidOperation
    from uuid import uuid4

    owner_id = str(
        owner_id or ""
    ).strip()

    name = str(
        name or ""
    ).strip()

    if not owner_id:

        raise ValueError(
            "owner_id obrigatório"
        )

    if not name:

        raise ValueError(
            "name obrigatório"
        )

    try:

        amount = Decimal(
            str(target_amount)
        ).quantize(
            Decimal("0.01")
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            "target_amount inválido"
        ) from exc


    if amount <= 0:

        raise ValueError(
            "target_amount deve ser maior que zero"
        )


    normalized_date = None

    if target_date:

        try:

            if isinstance(
                target_date,
                date,
            ):

                normalized_date = (
                    target_date
                )

            else:

                normalized_date = (
                    date.fromisoformat(
                        str(target_date)
                    )
                )

        except ValueError as exc:

            raise ValueError(
                "target_date inválida"
            ) from exc


    goal_scope = (
        _normalize_finance_goal_scope(
            scope
        )
    )


    if goal_scope == "family":

        responsible_member_id = (
            _validate_family_goal_responsible(
                owner_id=owner_id,
                responsible_member_id=
                    responsible_member_id,
            )
        )

    else:

        responsible_member_id = None


    ensure_finance_goal_scope_schema()


    sql = f"""
    INSERT INTO {GOAL_TABLE} (
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active,
        scope,
        responsible_member_id
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        0,
        %s,
        TRUE,
        %s,
        %s
    )

    RETURNING
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active,
        scope,
        responsible_member_id,
        created_at,
        updated_at
    """


    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                uuid4().hex,
                owner_id,
                name,
                amount,
                normalized_date,
                goal_scope,
                responsible_member_id,
            ),
        )

        row = cursor.fetchone()

        return (
            dict(row)
            if row
            else None
        )


# ============================================================
# Override compatível do LIST existente
# ============================================================

def list_finance_goals(
    *,
    owner_id: str,
    scope="personal",
) -> list[dict]:

    owner_id = str(
        owner_id or ""
    ).strip()

    if not owner_id:

        raise ValueError(
            "owner_id obrigatório"
        )


    goal_scope = (
        _normalize_finance_goal_scope(
            scope
        )
    )


    ensure_finance_goal_scope_schema()


    sql = f"""
    SELECT
        goal_id,
        owner_id,
        name,
        target_amount,
        current_amount,
        target_date,
        active,
        scope,
        responsible_member_id,
        created_at,
        updated_at
    FROM {GOAL_TABLE}
    WHERE
        owner_id = %s
        AND active = TRUE
        AND scope = %s
    ORDER BY
        created_at DESC
    """


    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                owner_id,
                goal_scope,
            ),
        )

        return [
            dict(row)
            for row
            in cursor.fetchall()
        ]


