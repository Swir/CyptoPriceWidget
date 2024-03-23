import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QThread

import requests
import json
import time

class PriceUpdater(QObject):
    updatePriceSignal = pyqtSignal(dict)

    def __init__(self, pinned_tokens):
        super().__init__()
        self.pinned_tokens = pinned_tokens
        self.running = True
        self.last_prices = {}

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            data = self.get_crypto_prices()
            price_info = self.generate_price_info(data)
            if price_info != self.last_prices:
                self.updatePriceSignal.emit(price_info)
                self.last_prices = price_info
            time.sleep(40)  # Reduced to update every 40 seconds

    def get_crypto_prices(self):
        tokens_str = ','.join(self.pinned_tokens)
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={tokens_str}&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Błąd pobierania danych: {err}")
            return {}
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {e}")
            return {}

    def generate_price_info(self, data):
        price_info = {}
        for token in self.pinned_tokens:
            if token in data:
                price = data[token].get('usd', None)
                change_percentage = data[token].get('usd_24h_change', None)
                if price is not None:
                    color = 'white'
                    if change_percentage is not None:
                        color = 'red' if change_percentage < 0 else 'green'
                    price_str = f"({price:.10f})" if price < 0.01 else f"{price:.2f}"
                    change_text = f" ({change_percentage:.2f}%)" if change_percentage is not None else ""
                    price_info[token] = f"<font style='color: {color};'>{token}: ${price_str}{change_text}</font><br>"
                else:
                    price_info[token] = f"<font style='color: white;'>{token}: Brak danych</font><br>"
            else:
                price_info[token] = f"<font style='color: white;'>{token}: Brak danych</font><br>"
        return price_info

class CryptoPriceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Price Widget")
        self.setGeometry(100, 100, 500, 300)
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet("background-color: black; color: green;")

        self.label = QLabel("Wybierz kryptowalutę:")
        layout.addWidget(self.label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Wyszukaj...")
        self.search_edit.textChanged.connect(self.filter_crypto_list)
        layout.addWidget(self.search_edit)

        self.search_combobox = QComboBox()
        layout.addWidget(self.search_combobox)

        self.price_label = QLabel("")
        self.price_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.price_label)

        self.pin_button = QPushButton("Przypnij")
        self.pin_button.clicked.connect(self.pin_token)
        layout.addWidget(self.pin_button)

        self.setLayout(layout)

        self.pinned_tokens = self.load_pinned_tokens()
        self.crypto_list = []
        self.filtered_crypto_list = []

        self.update_crypto_list()
        self.update_combobox_values()

        self.price_updater = PriceUpdater(self.pinned_tokens)
        self.price_updater_thread = QThread()
        self.price_updater.moveToThread(self.price_updater_thread)
        self.price_updater.updatePriceSignal.connect(self.update_price_label)
        self.price_updater_thread.started.connect(self.price_updater.run)
        self.price_updater_thread.start()

        self.full_text = ""
        self.current_text = ""
        self.current_index = 0
        self.animate_text()

    def load_pinned_tokens(self):
        try:
            with open("pinned_tokens.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_pinned_tokens(self):
        with open("pinned_tokens.json", "w") as file:
            json.dump(self.pinned_tokens, file)

    def update_crypto_list(self):
        try:
            url = "https://api.coingecko.com/api/v3/coins/list"
            response = requests.get(url)
            response.raise_for_status()  
            data = response.json()
            self.crypto_list = [crypto['id'] for crypto in data]
        except requests.exceptions.HTTPError as err:
            print(f"Błąd pobierania danych: {err}")
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {e}")

    def update_combobox_values(self):
        self.search_combobox.clear()
        self.search_combobox.addItems(self.crypto_list)

    def filter_crypto_list(self, text):
        self.filtered_crypto_list = [crypto for crypto in self.crypto_list if text.lower() in crypto.lower()]
        self.search_combobox.clear()
        self.search_combobox.addItems(self.filtered_crypto_list)

    def pin_token(self):
        selected_crypto = self.search_combobox.currentText().strip()
        if selected_crypto and selected_crypto not in self.pinned_tokens:
            self.pinned_tokens.append(selected_crypto)
            self.update_combobox_values()
            self.save_pinned_tokens()

    def update_price_label(self, price_info):
        html = ""
        for price in price_info.values():
            html += price
        self.full_text = html
        self.price_label.setText(html)
        self.price_label.setFont(QFont("Arial", 12))  # Zmiana rozmiaru czcionki

    def animate_text(self):
        if self.current_index < len(self.full_text):
            self.current_text += self.full_text[self.current_index]
            self.price_label.setText(self.current_text)
            self.current_index += 1
        else:
            self.current_text = ""
            self.current_index = 0
        QTimer.singleShot(20, self.animate_text)

def main():
    app = QApplication(sys.argv)
    widget = CryptoPriceWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
