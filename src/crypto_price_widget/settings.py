from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

SUPPORTED_CURRENCIES = ("USD", "EUR", "GBP", "NOK", "PLN")
SUPPORTED_LANGUAGES = ("AUTO", "EN", "PL", "NO")


@dataclass(slots=True)
class AppSettings:
    pinned: list[str]
    currency: str = "USD"
    refresh_seconds: int = 40
    language: str = "AUTO"

    @classmethod
    def defaults(cls) -> "AppSettings":
        return cls(pinned=["bitcoin", "ethereum"])

    @classmethod
    def from_dict(cls, data: Any) -> "AppSettings":
        if not isinstance(data, dict):
            return cls.defaults()

        raw_pinned = data.get("pinned")
        if isinstance(raw_pinned, list):
            # An intentionally empty watch list is valid and must survive a restart.
            pinned: list[str] = []
            for item in raw_pinned:
                value = str(item).strip()
                if value and value not in pinned and len(pinned) < 50:
                    pinned.append(value)
        else:
            pinned = cls.defaults().pinned.copy()

        currency = str(data.get("currency", "USD")).upper()
        if currency not in SUPPORTED_CURRENCIES:
            currency = "USD"

        try:
            refresh = int(data.get("refresh_seconds", 40))
        except (TypeError, ValueError):
            refresh = 40
        refresh = min(900, max(20, refresh))

        language = str(data.get("language", "AUTO")).upper()
        if language not in SUPPORTED_LANGUAGES:
            language = "AUTO"

        return cls(
            pinned=pinned,
            currency=currency,
            refresh_seconds=refresh,
            language=language,
        )


def settings_path() -> Path:
    return Path(user_config_dir("CryptoPriceWidget", "Swir")) / "settings.json"


def _load_legacy_pins(path: Path) -> list[str] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, list):
        return None
    pinned: list[str] = []
    for item in raw:
        value = str(item).strip()
        if value and value not in pinned and len(pinned) < 50:
            pinned.append(value)
    return pinned


def load_settings(path: Path | None = None, legacy_path: Path | None = None) -> AppSettings:
    target = path or settings_path()
    try:
        return AppSettings.from_dict(json.loads(target.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return AppSettings.defaults()
    except OSError:
        pass

    # v1-v5 stored the pin list beside the script/executable as pinned_tokens.json.
    # Import it once when the modern per-user settings file does not exist, so an
    # upgrade does not silently reset a user's watch list. A valid empty legacy
    # list is meaningful and must remain empty after migration.
    legacy = legacy_path or (Path.cwd() / "pinned_tokens.json")
    pins = _load_legacy_pins(legacy)
    if pins is not None:
        migrated = AppSettings(pinned=pins)
        try:
            save_settings(migrated, target)
        except OSError:
            # Migration should never prevent the application from starting.
            pass
        return migrated
    return AppSettings.defaults()


def save_settings(settings: AppSettings, path: Path | None = None) -> Path:
    target = path or settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(settings), indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)
    return target
