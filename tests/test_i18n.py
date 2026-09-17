from crypto_price_widget.i18n import resolve_language, tr


def test_explicit_languages_are_supported() -> None:
    assert resolve_language("PL") == "PL"
    assert resolve_language("NO") == "NO"
    assert resolve_language("EN") == "EN"


def test_invalid_language_falls_back_to_english() -> None:
    assert resolve_language("XX") == "EN"


def test_polish_classic_pin_label_is_restored() -> None:
    assert tr("PL", "pin") == "Przypnij"
    assert tr("PL", "unpin") == "Odepnij"


def test_translation_parameters_are_formatted() -> None:
    assert "40" in tr("EN", "live", seconds=40)
