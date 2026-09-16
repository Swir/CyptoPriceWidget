from crypto_price_widget.settings import AppSettings, load_settings, save_settings


def test_settings_round_trip(tmp_path) -> None:
    path = tmp_path / "settings.json"
    original = AppSettings(pinned=["bitcoin", "ethereum"], currency="NOK", refresh_seconds=60)
    save_settings(original, path)
    loaded = load_settings(path)
    assert loaded.pinned == original.pinned
    assert loaded.currency == "NOK"
    assert loaded.refresh_seconds == 60


def test_settings_sanitize_bad_values() -> None:
    loaded = AppSettings.from_dict({"pinned": ["bitcoin", "bitcoin", ""], "currency": "xyz", "refresh_seconds": 1})
    assert loaded.pinned == ["bitcoin"]
    assert loaded.currency == "USD"
    assert loaded.refresh_seconds == 20
