<div align="center">

<img src="assets/crypto-price-widget.svg" width="160" alt="Crypto Price Widget application icon">

# Crypto Price Widget v6.1

### Fast, modern desktop cryptocurrency monitoring powered by CoinGecko

**Python 3.10-3.14 • PySide6 / Qt 6 • Background Refresh • Search • Pinned Assets • Animated Ticker • Windows EXE**

</div>

## Why v6.1 exists

The v6 modernization replaced the old `v1.py` through `v5.py` scripts with one maintainable application, but the regression audit found two useful pieces of classic behavior that were no longer represented: the old animated price line and automatic reuse of the legacy `pinned_tokens.json` watch list. v6.1 restores both while keeping the safer and more capable v6 architecture.

The historical repository is named `CyptoPriceWidget`; the application itself uses the corrected **Crypto Price Widget** branding.

## Features

- live CoinGecko prices and 24-hour percentage change
- searchable asset catalog by coin name, symbol or CoinGecko ID
- up to 50 pinned assets
- **restored animated compact price ticker** inspired by the v3-v5 typewriter display, implemented as plain text so partially rendered HTML can no longer corrupt the animation
- **one-time migration of legacy `pinned_tokens.json`** when modern settings do not yet exist
- USD, EUR, GBP, NOK and PLN display currencies
- automatic background refresh without freezing the GUI
- resilient HTTPS requests with explicit timeouts and retries for temporary failures and rate limits
- persistent per-user settings via the platform application-data directory
- Pin and Unpin controls plus manual Refresh
- compact dark-blue Windows 11-friendly interface
- custom application icon displayed here, used by the GUI and embedded in the Windows EXE
- `by Swir` GitHub footer
- official Qt for Python bindings (PySide6, LGPL/GPL dual-licensed by Qt)
- automated tests on Python 3.10, 3.11, 3.12, 3.13 and 3.14
- automated Windows EXE + portable ZIP + SHA256 release pipeline

## Upgrade from v1-v5

Older releases kept the watch list in a `pinned_tokens.json` file beside the program. On first v6.1 start, if the modern settings file does not exist and a valid `pinned_tokens.json` is present in the working directory, the app imports those coin IDs into the modern per-user settings location. Duplicates and blank entries are cleaned automatically. A broken legacy file is ignored rather than preventing startup.

After successful migration the modern settings file becomes authoritative; the old file is not modified.

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

Regression tests now cover price formatting, the restored ticker summary, legacy pinned-token migration, settings sanitization and model parsing.

Project layout:

```text
src/crypto_price_widget/   application package
assets/                    source artwork shown in this README and used for the app icon
tests/                     unit and regression tests
tools/build_icon.py        PNG/ICO generator
.github/workflows/         CI and Windows release automation
main.py                    application entry point
```

## Releases

Numbered releases contain:

- `CryptoPriceWidget.exe`
- `CryptoPriceWidget-vX.Y.Z-Windows-x64.zip`
- SHA256 checksum files for both downloads

The release pipeline runs tests, generates the Windows ICO, builds the executable and smoke-tests `CryptoPriceWidget.exe --version` before publication.

## Market-data disclaimer

Prices can be delayed, unavailable or rate-limited by the upstream provider. Crypto Price Widget is an informational monitor only; it does not execute trades and does not provide financial or investment advice.

## Author

Developed by **Swir** — https://github.com/Swir
