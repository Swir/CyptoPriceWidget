from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from . import __version__
from .settings import load_settings
from .ui import CryptoPriceWindow


def resource_path(relative: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / relative


def _create_application() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("Crypto Price Widget")
    app.setOrganizationName("Swir")
    icon = resource_path("assets/crypto-price-widget.svg")
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    return app


def main() -> int:
    if "--version" in sys.argv:
        print(f"Crypto Price Widget {__version__}")
        return 0

    smoke_gui = "--smoke-gui" in sys.argv
    app = _create_application()
    window = CryptoPriceWindow(load_settings(), start_network=not smoke_gui)
    window.show()
    if smoke_gui:
        # Exercise QApplication, QMainWindow, translations, settings and packaged
        # Qt platform plugins without depending on external network availability.
        QTimer.singleShot(350, app.quit)
    return app.exec()
