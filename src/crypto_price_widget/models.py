from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class Coin:
    id: str
    symbol: str
    name: str


@dataclass(frozen=True, slots=True)
class PriceQuote:
    coin_id: str
    price: float | None
    change_24h: float | None


def parse_coins(payload: Any) -> list[Coin]:
    if not isinstance(payload, list):
        return []
    unique: dict[str, Coin] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        coin_id = str(item.get("id", "")).strip()
        symbol = str(item.get("symbol", "")).strip().upper()
        name = str(item.get("name", "")).strip()
        if not coin_id or not name:
            continue
        unique.setdefault(coin_id, Coin(coin_id, symbol, name))
    return sorted(unique.values(), key=lambda coin: (coin.name.casefold(), coin.symbol, coin.id))


def parse_quotes(payload: Any, coin_ids: Iterable[str], currency: str) -> dict[str, PriceQuote]:
    currency = currency.lower()
    change_key = f"{currency}_24h_change"
    source = payload if isinstance(payload, dict) else {}
    result: dict[str, PriceQuote] = {}
    for coin_id in coin_ids:
        raw = source.get(coin_id, {}) if isinstance(source.get(coin_id, {}), dict) else {}
        price = _number_or_none(raw.get(currency))
        change = _number_or_none(raw.get(change_key))
        result[coin_id] = PriceQuote(coin_id=coin_id, price=price, change_24h=change)
    return result


def _number_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
