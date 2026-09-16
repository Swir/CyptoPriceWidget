from crypto_price_widget.models import parse_coins, parse_quotes


def test_parse_coins_deduplicates_and_sorts() -> None:
    coins = parse_coins([
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
        {"id": "bitcoin", "symbol": "btc2", "name": "Duplicate"},
        {"id": "", "symbol": "bad", "name": "Bad"},
    ])
    assert [coin.id for coin in coins] == ["bitcoin", "ethereum"]
    assert coins[0].symbol == "BTC"


def test_parse_quotes_keeps_missing_assets() -> None:
    quotes = parse_quotes(
        {"bitcoin": {"usd": 123.5, "usd_24h_change": -2.25}},
        ["bitcoin", "ethereum"],
        "usd",
    )
    assert quotes["bitcoin"].price == 123.5
    assert quotes["bitcoin"].change_24h == -2.25
    assert quotes["ethereum"].price is None
