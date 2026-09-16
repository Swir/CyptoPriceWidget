from __future__ import annotations

CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£", "NOK": "kr ", "PLN": "zł "}


def format_price(value: float | None, currency: str) -> str:
    if value is None:
        return "No data"
    symbol = CURRENCY_SYMBOLS.get(currency.upper(), f"{currency.upper()} ")
    absolute = abs(value)
    if absolute >= 1000:
        number = f"{value:,.2f}"
    elif absolute >= 1:
        number = f"{value:.2f}"
    elif absolute >= 0.01:
        number = f"{value:.4f}"
    else:
        number = f"{value:.8f}"
    return f"{symbol}{number}"


def format_change(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:+.2f}%"
