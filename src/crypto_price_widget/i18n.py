from __future__ import annotations

import locale
from collections.abc import Mapping

SUPPORTED_UI_LANGUAGES = ("EN", "PL", "NO")

_TRANSLATIONS: dict[str, Mapping[str, str]] = {
    "EN": {
        "subtitle": "CoinGecko market monitor",
        "ticker_waiting": "Classic ticker • waiting for market data…",
        "search_placeholder": "Search by name, symbol or CoinGecko ID…",
        "pin": "Pin",
        "unpin": "Unpin",
        "refresh": "Refresh",
        "currency": "Currency",
        "language": "Language",
        "refresh_interval": "Refresh interval",
        "asset": "Asset",
        "price": "Price",
        "change_24h": "24h",
        "state": "Status",
        "starting": "Starting…",
        "loading_catalog": "Loading CoinGecko asset catalog…",
        "loaded_assets": "Loaded {count:,} assets",
        "pin_limit": "Pinned-asset limit reached (50).",
        "no_pins": "No pinned assets",
        "pin_to_begin": "Pin an asset to begin monitoring.",
        "refreshing": "Refreshing {count} pinned asset(s)…",
        "updated": "Updated {time}",
        "live": "Live • refresh every {seconds}s",
        "live_state": "Live",
        "waiting": "Waiting",
        "market_error": "Market data unavailable: {message}",
        "smoke_ready": "GUI smoke test ready",
    },
    "PL": {
        "subtitle": "monitor rynku CoinGecko",
        "ticker_waiting": "Klasyczny pasek • oczekiwanie na dane rynkowe…",
        "search_placeholder": "Szukaj po nazwie, symbolu lub ID CoinGecko…",
        "pin": "Przypnij",
        "unpin": "Odepnij",
        "refresh": "Odśwież",
        "currency": "Waluta",
        "language": "Język",
        "refresh_interval": "Odświeżanie",
        "asset": "Aktywo",
        "price": "Cena",
        "change_24h": "24h",
        "state": "Stan",
        "starting": "Uruchamianie…",
        "loading_catalog": "Pobieranie listy aktywów CoinGecko…",
        "loaded_assets": "Wczytano {count:,} aktywów",
        "pin_limit": "Osiągnięto limit 50 przypiętych aktywów.",
        "no_pins": "Brak przypiętych aktywów",
        "pin_to_begin": "Przypnij aktywo, aby rozpocząć monitorowanie.",
        "refreshing": "Odświeżanie {count} przypiętych aktywów…",
        "updated": "Aktualizacja {time}",
        "live": "Na żywo • odświeżanie co {seconds}s",
        "live_state": "Na żywo",
        "waiting": "Oczekiwanie",
        "market_error": "Dane rynkowe niedostępne: {message}",
        "smoke_ready": "Test GUI gotowy",
    },
    "NO": {
        "subtitle": "CoinGecko-markedsovervåking",
        "ticker_waiting": "Klassisk ticker • venter på markedsdata…",
        "search_placeholder": "Søk etter navn, symbol eller CoinGecko-ID…",
        "pin": "Fest",
        "unpin": "Fjern",
        "refresh": "Oppdater",
        "currency": "Valuta",
        "language": "Språk",
        "refresh_interval": "Oppdatering",
        "asset": "Aktiva",
        "price": "Pris",
        "change_24h": "24t",
        "state": "Status",
        "starting": "Starter…",
        "loading_catalog": "Laster CoinGecko-aktivaliste…",
        "loaded_assets": "Lastet {count:,} aktiva",
        "pin_limit": "Grensen på 50 festede aktiva er nådd.",
        "no_pins": "Ingen festede aktiva",
        "pin_to_begin": "Fest et aktiva for å starte overvåkingen.",
        "refreshing": "Oppdaterer {count} festede aktiva…",
        "updated": "Oppdatert {time}",
        "live": "Live • oppdateres hvert {seconds}s",
        "live_state": "Live",
        "waiting": "Venter",
        "market_error": "Markedsdata utilgjengelig: {message}",
        "smoke_ready": "GUI-røyktest klar",
    },
}


def system_language() -> str:
    """Return a supported UI language without failing on unusual host locales."""
    try:
        current = locale.getlocale()[0] or ""
    except (ValueError, TypeError):
        current = ""
    code = current.replace("-", "_").split("_", 1)[0].lower()
    if code == "pl":
        return "PL"
    if code in {"no", "nb", "nn"}:
        return "NO"
    return "EN"


def resolve_language(preference: str) -> str:
    value = str(preference or "AUTO").upper()
    if value == "AUTO":
        return system_language()
    return value if value in SUPPORTED_UI_LANGUAGES else "EN"


def tr(language: str, key: str, **values: object) -> str:
    lang = resolve_language(language)
    template = _TRANSLATIONS.get(lang, _TRANSLATIONS["EN"]).get(key, _TRANSLATIONS["EN"].get(key, key))
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return template
