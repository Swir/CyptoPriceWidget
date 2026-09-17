# Changelog

## 6.1.0 - 2026-09-17

### Restored
- Animated compact price ticker inspired by the classic v3-v5 typewriter display.
- One-time migration of legacy `pinned_tokens.json` watch lists into modern per-user settings.

### Improved
- The restored ticker uses plain text instead of animating partial HTML markup, preventing broken intermediate rendering.
- Legacy watch-list migration sanitizes duplicates and blank entries and never blocks startup when an old file is invalid.
- README now displays the custom application icon and documents the real upgrade path from v1-v5.

### Tested
- Regression coverage for ticker summaries and long watch-list limits.
- Regression coverage for legacy pin migration and malformed legacy state.

## 6.0.0 - 2026-09-16

### Added
- Modern PySide6 / Qt 6 desktop interface with blue dark theme and responsive layout.
- CoinGecko API client with bounded timeouts, retries, rate-limit handling and clear user-facing errors.
- Searchable CoinGecko asset catalog and up to 50 pinned assets.
- USD, EUR, GBP, NOK and PLN display currencies.
- Background refresh without blocking the UI.
- Per-user settings stored outside the repository/application folder.
- Custom Crypto Price Widget application artwork and automated Windows ICO generation.
- Python 3.10-3.14 CI, unit tests and Windows release automation.
- Portable Windows ZIP, standalone EXE and SHA256 checksums.

### Changed
- Application branding is corrected to **Crypto Price Widget** while retaining the historical repository URL `CyptoPriceWidget`.
- Replaced the five parallel legacy scripts with one maintainable `src/` package.
- Migrated the interface from PyQt5 to the official Qt for Python bindings, PySide6.
- Removed repository-local runtime state (`pinned_tokens.json`).

### Removed
- `v1.py`, `v2 py QT.py`, `v3.py`, `v4.py`, `v5.py` and `Przeczytaj!.txt` from the current tree. Their history remains available through Git.
