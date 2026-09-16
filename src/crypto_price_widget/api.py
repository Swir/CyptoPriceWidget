from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import __version__
from .models import Coin, PriceQuote, parse_coins, parse_quotes


class MarketDataError(RuntimeError):
    """Raised when market data cannot be retrieved safely."""


class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, timeout: tuple[float, float] = (4.0, 12.0)) -> None:
        self.timeout = timeout

    def _session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.headers.update({"User-Agent": f"CryptoPriceWidget/{__version__} (+https://github.com/Swir/CyptoPriceWidget)"})
        return session

    def _get_json(self, path: str, params: dict[str, str] | None = None) -> Any:
        try:
            with self._session() as session:
                response = session.get(f"{self.BASE_URL}{path}", params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        except (requests.RequestException, ValueError) as exc:
            raise MarketDataError(f"CoinGecko request failed: {exc}") from exc

    def list_coins(self) -> list[Coin]:
        coins = parse_coins(self._get_json("/coins/list", {"include_platform": "false"}))
        if not coins:
            raise MarketDataError("CoinGecko returned an empty or invalid coin list.")
        return coins

    def get_quotes(self, coin_ids: Sequence[str], currency: str = "usd") -> dict[str, PriceQuote]:
        ids = list(dict.fromkeys(str(item).strip() for item in coin_ids if str(item).strip()))
        if not ids:
            return {}
        if len(ids) > 50:
            raise MarketDataError("A maximum of 50 pinned assets is supported.")
        currency = currency.lower().strip()
        if currency not in {"usd", "eur", "gbp", "nok", "pln"}:
            raise MarketDataError(f"Unsupported currency: {currency}")
        payload = self._get_json(
            "/simple/price",
            {
                "ids": ",".join(ids),
                "vs_currencies": currency,
                "include_24hr_change": "true",
            },
        )
        return parse_quotes(payload, ids, currency)
