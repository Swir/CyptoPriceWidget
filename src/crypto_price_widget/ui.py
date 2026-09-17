from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .api import CoinGeckoClient
from .formatting import build_ticker_text, format_change, format_price
from .models import Coin, PriceQuote
from .settings import AppSettings, SUPPORTED_CURRENCIES, save_settings


class TaskSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class ApiTask(QRunnable):
    def __init__(self, function: Callable[[], Any]) -> None:
        super().__init__()
        self.function = function
        self.signals = TaskSignals()

    def run(self) -> None:
        try:
            self.signals.result.emit(self.function())
        except Exception as exc:  # user-facing boundary for background network work
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()


class CryptoPriceWindow(QMainWindow):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.client = CoinGeckoClient()
        self.pool = QThreadPool.globalInstance()
        self.coins: list[Coin] = []
        self._active_tasks: set[ApiTask] = set()
        self._prices_busy = False
        self._ticker_full_text = ""
        self._ticker_index = 0

        self.setWindowTitle("Crypto Price Widget — by Swir")
        self.resize(820, 550)
        self.setMinimumSize(680, 440)
        self._build_ui()
        self._apply_theme()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_quotes)
        self.refresh_timer.start(self.settings.refresh_seconds * 1000)

        self.ticker_timer = QTimer(self)
        self.ticker_timer.timeout.connect(self._advance_ticker)
        self.ticker_timer.start(28)

        self._rebuild_table({})
        self.load_coin_catalog()
        self.refresh_quotes()

    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("CRYPTO PRICE WIDGET")
        title.setObjectName("title")
        subtitle = QLabel("CoinGecko market monitor")
        subtitle.setObjectName("muted")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(subtitle)
        root.addLayout(header)

        self.ticker = QLabel("Classic ticker • waiting for market data…")
        self.ticker.setObjectName("ticker")
        self.ticker.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.ticker)

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by name, symbol or CoinGecko ID…")
        self.search.textChanged.connect(self._filter_coins)
        controls.addWidget(self.search, 2)

        self.coin_combo = QComboBox()
        self.coin_combo.setMinimumWidth(260)
        controls.addWidget(self.coin_combo, 2)

        self.pin_button = QPushButton("Pin")
        self.pin_button.clicked.connect(self.pin_selected)
        controls.addWidget(self.pin_button)

        self.unpin_button = QPushButton("Unpin")
        self.unpin_button.clicked.connect(self.unpin_selected)
        controls.addWidget(self.unpin_button)

        self.currency = QComboBox()
        self.currency.addItems(SUPPORTED_CURRENCIES)
        self.currency.setCurrentText(self.settings.currency)
        self.currency.currentTextChanged.connect(self.change_currency)
        controls.addWidget(self.currency)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_quotes)
        controls.addWidget(self.refresh_button)
        root.addLayout(controls)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Asset", "Price", "24h", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table, 1)

        footer = QHBoxLayout()
        self.status = QLabel("Starting…")
        self.status.setObjectName("muted")
        self.updated = QLabel("")
        self.updated.setObjectName("muted")
        footer.addWidget(self.status)
        footer.addStretch(1)
        footer.addWidget(self.updated)
        root.addLayout(footer)

        author = QLabel('by Swir • <a href="https://github.com/Swir">github.com/Swir</a>')
        author.setOpenExternalLinks(True)
        author.setObjectName("author")
        root.addWidget(author, alignment=Qt.AlignmentFlag.AlignRight)
        self.setCentralWidget(central)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #07111f; color: #e7f1ff; font-size: 13px; }
            QLabel#title { font-size: 22px; font-weight: 800; color: #55b7ff; letter-spacing: 2px; }
            QLabel#muted { color: #7892ad; }
            QLabel#author { color: #6d89a5; }
            QLabel#author a { color: #55b7ff; }
            QLabel#ticker { background: #091728; border: 1px solid #1f4d73; border-radius: 7px; padding: 8px 10px; color: #9fd4ff; font-family: Consolas, monospace; }
            QLineEdit, QComboBox { background: #0d1c2f; border: 1px solid #254766; border-radius: 7px; padding: 8px; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #55b7ff; }
            QPushButton { background: #12304b; border: 1px solid #2c628c; border-radius: 7px; padding: 8px 12px; font-weight: 600; }
            QPushButton:hover { background: #174366; border-color: #55b7ff; }
            QPushButton:disabled { color: #52677b; background: #0b1827; }
            QTableWidget { background: #091728; alternate-background-color: #0c1c30; border: 1px solid #203b55; border-radius: 8px; gridline-color: #17314a; }
            QHeaderView::section { background: #10253a; color: #9fd4ff; padding: 8px; border: 0; border-right: 1px solid #1f3e59; font-weight: 700; }
            QTableWidget::item { padding: 7px; }
            QTableWidget::item:selected { background: #174d73; }
            """
        )
        self.table.setAlternatingRowColors(True)

    def _start_task(self, function: Callable[[], Any], on_result: Callable[[Any], None], *, price_task: bool = False) -> None:
        task = ApiTask(function)
        self._active_tasks.add(task)
        if price_task:
            self._prices_busy = True
            self.refresh_button.setEnabled(False)
        task.signals.result.connect(on_result)
        task.signals.error.connect(self._show_error)

        def finished() -> None:
            self._active_tasks.discard(task)
            if price_task:
                self._prices_busy = False
                self.refresh_button.setEnabled(True)

        task.signals.finished.connect(finished)
        self.pool.start(task)

    def load_coin_catalog(self) -> None:
        self.status.setText("Loading CoinGecko asset catalog…")
        self._start_task(self.client.list_coins, self._catalog_loaded)

    def _catalog_loaded(self, coins: list[Coin]) -> None:
        self.coins = coins
        self._filter_coins(self.search.text())
        self.status.setText(f"Loaded {len(coins):,} assets")

    def _filter_coins(self, text: str) -> None:
        needle = text.strip().casefold()
        if needle:
            matches = [
                coin for coin in self.coins
                if needle in coin.name.casefold() or needle in coin.symbol.casefold() or needle in coin.id.casefold()
            ][:300]
        else:
            matches = self.coins[:300]
        self.coin_combo.blockSignals(True)
        self.coin_combo.clear()
        for coin in matches:
            self.coin_combo.addItem(f"{coin.name} ({coin.symbol})", coin.id)
        self.coin_combo.blockSignals(False)

    def pin_selected(self) -> None:
        coin_id = self.coin_combo.currentData()
        if not coin_id or coin_id in self.settings.pinned:
            return
        if len(self.settings.pinned) >= 50:
            self.status.setText("Pinned-asset limit reached (50).")
            return
        self.settings.pinned.append(str(coin_id))
        save_settings(self.settings)
        self._rebuild_table({})
        self.refresh_quotes()

    def unpin_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        coin_id = item.data(Qt.ItemDataRole.UserRole) if item else None
        if coin_id in self.settings.pinned:
            self.settings.pinned.remove(coin_id)
            save_settings(self.settings)
            self._rebuild_table({})
            self.refresh_quotes()

    def change_currency(self, currency: str) -> None:
        self.settings.currency = currency
        save_settings(self.settings)
        self.refresh_quotes()

    def refresh_quotes(self) -> None:
        if self._prices_busy:
            return
        if not self.settings.pinned:
            self._rebuild_table({})
            self._set_ticker_text("No pinned assets")
            self.status.setText("Pin an asset to begin monitoring.")
            return
        ids = tuple(self.settings.pinned)
        currency = self.settings.currency
        self.status.setText(f"Refreshing {len(ids)} pinned asset(s)…")
        self._start_task(lambda: self.client.get_quotes(ids, currency), self._quotes_loaded, price_task=True)

    def _quotes_loaded(self, quotes: dict[str, PriceQuote]) -> None:
        self._rebuild_table(quotes)
        self._set_ticker_text(build_ticker_text(self.settings.pinned, quotes, self.settings.currency))
        stamp = datetime.now().strftime("%H:%M:%S")
        self.updated.setText(f"Updated {stamp}")
        self.status.setText(f"Live • refresh every {self.settings.refresh_seconds}s")

    def _set_ticker_text(self, text: str) -> None:
        self._ticker_full_text = text or "Waiting for market data…"
        self._ticker_index = 0
        self.ticker.setText("")

    def _advance_ticker(self) -> None:
        if not self._ticker_full_text:
            return
        if self._ticker_index <= len(self._ticker_full_text):
            self.ticker.setText(self._ticker_full_text[: self._ticker_index])
            self._ticker_index += 1
        else:
            # Briefly loop the familiar typewriter animation from the classic widget
            # without reconstructing partial HTML markup character by character.
            self._ticker_index = 0

    def _coin_label(self, coin_id: str) -> str:
        coin = next((item for item in self.coins if item.id == coin_id), None)
        if coin:
            return f"{coin.name} ({coin.symbol})"
        return coin_id

    def _rebuild_table(self, quotes: dict[str, PriceQuote]) -> None:
        self.table.setRowCount(len(self.settings.pinned))
        for row, coin_id in enumerate(self.settings.pinned):
            quote = quotes.get(coin_id)
            asset = QTableWidgetItem(self._coin_label(coin_id))
            asset.setData(Qt.ItemDataRole.UserRole, coin_id)
            price = QTableWidgetItem(format_price(quote.price if quote else None, self.settings.currency))
            change_value = quote.change_24h if quote else None
            change = QTableWidgetItem(format_change(change_value))
            if change_value is not None:
                change.setForeground(QColor("#58d68d" if change_value >= 0 else "#ff6b7a"))
            status = QTableWidgetItem("Live" if quote and quote.price is not None else "Waiting")
            self.table.setItem(row, 0, asset)
            self.table.setItem(row, 1, price)
            self.table.setItem(row, 2, change)
            self.table.setItem(row, 3, status)
        self.table.resizeColumnsToContents()

    def _show_error(self, message: str) -> None:
        self.status.setText(f"Market data unavailable: {message}")

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        save_settings(self.settings)
        self.pool.waitForDone(1500)
        super().closeEvent(event)
