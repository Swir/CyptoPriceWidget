from __future__ import annotations

from collections.abc import Mapping, Sequence

from .models import PriceQuote

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


def build_ticker_text(
    pinned: Sequence[str], quotes: Mapping[str, PriceQuote], currency: str, *, max_items: int = 8
) -> str:
    """Build the compact price line used by the restored animated ticker."""
    parts: list[str] = []
    for coin_id in pinned[:max_items]:
        quote = quotes.get(coin_id)
        if quote is None or quote.price is None:
            parts.append(f"{coin_id}: No data")
            continue
        parts.append(f"{coin_id}: {format_price(quote.price, currency)} {format_change(quote.change_24h)}")
    return "   •   ".join(parts)
