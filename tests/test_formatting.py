from crypto_price_widget.formatting import build_ticker_text, format_change, format_price
from crypto_price_widget.models import PriceQuote


def test_price_precision_and_currency() -> None:
    assert format_price(1250.5, "USD") == "$1,250.50"
    assert format_price(0.004321, "NOK") == "kr 0.00432100"
    assert format_price(None, "EUR") == "No data"


def test_change_formatting() -> None:
    assert format_change(3.14159) == "+3.14%"
    assert format_change(-1.0) == "-1.00%"
    assert format_change(None) == "—"


def test_ticker_text_preserves_classic_price_and_change_summary() -> None:
    quotes = {
        "bitcoin": PriceQuote("bitcoin", 60000.0, 2.5),
        "tiny": PriceQuote("tiny", 0.004321, -1.0),
    }
    text = build_ticker_text(["bitcoin", "tiny"], quotes, "USD")
    assert "bitcoin: $60,000.00 +2.50%" in text
    assert "tiny: $0.00432100 -1.00%" in text


def test_ticker_limits_long_watchlists() -> None:
    pinned = [f"coin-{index}" for index in range(12)]
    text = build_ticker_text(pinned, {}, "USD", max_items=3)
    assert "coin-0" in text
    assert "coin-2" in text
    assert "coin-3" not in text
