from crypto_price_widget.formatting import format_change, format_price


def test_price_precision_and_currency() -> None:
    assert format_price(1250.5, "USD") == "$1,250.50"
    assert format_price(0.004321, "NOK") == "kr 0.00432100"
    assert format_price(None, "EUR") == "No data"


def test_change_formatting() -> None:
    assert format_change(3.14159) == "+3.14%"
    assert format_change(-1.0) == "-1.00%"
    assert format_change(None) == "—"
