"""Load budget defaults from local_config.py when present (kept out of git)."""

try:
    from local_config import (  # type: ignore
        PLUXEE_GROCERIES,
        RENT_PAYEE_LABEL,
        RENT_TARGET,
        SALARY,
        ZERODHA_TARGET,
    )
except ImportError:
    SALARY = 150000
    ZERODHA_TARGET = 100000
    PLUXEE_GROCERIES = 5000
    RENT_TARGET = 15000
    RENT_PAYEE_LABEL = "Rent"
