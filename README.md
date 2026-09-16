<div align="center">

# Crypto Price Widget

### Fast, modern desktop cryptocurrency monitoring powered by CoinGecko

**Python 3.10-3.14 • PySide6 / Qt 6 • Background Refresh • Search • Pinned Assets • Windows EXE**

</div>

## What changed in v6

Crypto Price Widget v6 replaces the old collection of `v1.py` through `v5.py` scripts with one maintainable application package. The UI no longer blocks while downloading prices, settings are stored in the user's application-data directory, network calls use explicit timeouts and retries, and Windows releases are built automatically from tested source.

The historical repository is named `CyptoPriceWidget`; the application itself now uses the corrected **Crypto Price Widget** branding.

## Features

- live CoinGecko prices and 24-hour percentage change
- searchable asset catalog by coin name, symbol or CoinGecko ID
- up to 50 pinned assets
- USD, EUR, GBP, NOK and PLN display currencies
- automatic background refresh without freezing the GUI
- resilient HTTPS requests with retries for temporary failures and rate limits
- persistent per-user settings via the platform application-data directory
- compact dark-blue Windows 11-friendly interface
- custom application icon and `by Swir` GitHub footer
- official Qt for Python bindings (PySide6, LGPL/GPL dual-licensed by Qt)
- automated tests on Python 3.10, 3.11, 3.12, 3.13 and 3.14
- automated Windows EXE + portable ZIP + SHA256 release pipeline

## Run from source

```bash
git clone https://github.com/Swir/CyptoPriceWidget.git
cd CyptoPriceWidget
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python main.py
```

On Linux/macOS, activate the virtual environment using the platform-appropriate command.

## Settings

Pinned assets, currency and refresh interval are saved outside the repository using the operating system's application-data location. This keeps personal state out of Git and lets a packaged EXE update without overwriting preferences.

Supported display currencies: **USD, EUR, GBP, NOK, PLN**. The default refresh interval is 45 seconds, with the code enforcing a minimum of 20 seconds to reduce unnecessary API pressure.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
python tools/build_icon.py
```

Project layout:

```text
src/crypto_price_widget/   application package
assets/                    source artwork
tests/                     unit tests
tools/build_icon.py        PNG/ICO generator
.github/workflows/         CI and Windows release automation
main.py                    application entry point
```

## Releases

Numbered releases contain:

- `CryptoPriceWidget.exe`
- `CryptoPriceWidget-vX.Y.Z-Windows-x64.zip`
- SHA256 checksum files for both downloads

The executable is smoke-tested before publication.

## Market-data disclaimer

Prices can be delayed, unavailable or rate-limited by the upstream provider. Crypto Price Widget is an informational monitor only; it does not execute trades and does not provide financial or investment advice.

## Author

Developed by **Swir** — https://github.com/Swir
