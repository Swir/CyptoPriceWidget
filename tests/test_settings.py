import json

from crypto_price_widget.settings import AppSettings, load_settings, save_settings


def test_settings_round_trip(tmp_path) -> None:
    path = tmp_path / "settings.json"
    original = AppSettings(
        pinned=["bitcoin", "ethereum"],
        currency="NOK",
        refresh_seconds=60,
        language="PL",
    )
    save_settings(original, path)
    loaded = load_settings(path)
    assert loaded.pinned == original.pinned
    assert loaded.currency == "NOK"
    assert loaded.refresh_seconds == 60
    assert loaded.language == "PL"


def test_settings_sanitize_bad_values() -> None:
    loaded = AppSettings.from_dict(
        {
            "pinned": ["bitcoin", "bitcoin", ""],
            "currency": "xyz",
            "refresh_seconds": 1,
            "language": "xx",
        }
    )
    assert loaded.pinned == ["bitcoin"]
    assert loaded.currency == "USD"
    assert loaded.refresh_seconds == 20
    assert loaded.language == "AUTO"


def test_empty_watch_list_survives_restart(tmp_path) -> None:
    path = tmp_path / "settings.json"
    save_settings(AppSettings(pinned=[], currency="PLN", refresh_seconds=40), path)
    loaded = load_settings(path)
    assert loaded.pinned == []
    assert loaded.currency == "PLN"


def test_missing_pinned_key_uses_defaults() -> None:
    loaded = AppSettings.from_dict({"currency": "EUR"})
    assert loaded.pinned == ["bitcoin", "ethereum"]


def test_legacy_pinned_tokens_are_migrated(tmp_path) -> None:
    target = tmp_path / "modern" / "settings.json"
    legacy = tmp_path / "pinned_tokens.json"
    legacy.write_text(json.dumps(["solana", "bitcoin", "solana", ""]), encoding="utf-8")

    loaded = load_settings(target, legacy)

    assert loaded.pinned == ["solana", "bitcoin"]
    assert target.exists()
    persisted = json.loads(target.read_text(encoding="utf-8"))
    assert persisted["pinned"] == ["solana", "bitcoin"]


def test_empty_legacy_watch_list_stays_empty(tmp_path) -> None:
    target = tmp_path / "modern" / "settings.json"
    legacy = tmp_path / "pinned_tokens.json"
    legacy.write_text("[]", encoding="utf-8")

    loaded = load_settings(target, legacy)

    assert loaded.pinned == []
    assert json.loads(target.read_text(encoding="utf-8"))["pinned"] == []


def test_broken_legacy_file_does_not_break_startup(tmp_path) -> None:
    target = tmp_path / "settings.json"
    legacy = tmp_path / "pinned_tokens.json"
    legacy.write_text("not-json", encoding="utf-8")
    loaded = load_settings(target, legacy)
    assert loaded.pinned == ["bitcoin", "ethereum"]
