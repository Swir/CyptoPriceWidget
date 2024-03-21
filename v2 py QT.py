import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer

import requests
import json
import threading
import time

class CryptoPriceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Price Widget")
        self.setGeometry(100, 100, 500, 300)
        layout = QVBoxLayout()
        self.setStyleSheet("background-color: black; color: white;")

        self.label = QLabel("Wybierz kryptowalutę:")
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Wyszukaj...")
        self.search_edit.textChanged.connect(self.filter_crypto_list)
        layout.addWidget(self.search_edit)

        self.search_combobox = QComboBox()
        layout.addWidget(self.search_combobox)

        self.price_label = QLabel("")
        layout.addWidget(self.price_label)

        self.pin_button = QPushButton("Przypnij")
        self.pin_button.clicked.connect(self.pin_token)
        layout.addWidget(self.pin_button)

        self.setLayout(layout)

        self.pinned_tokens = self.load_pinned_tokens()
        self.colors = {}
        self.crypto_list = []
        self.filtered_crypto_list = []

        self.update_crypto_list()
        self.update_combobox_values()

        self.refresh_thread = threading.Thread(target=self.refresh_prices)
        self.refresh_thread.daemon = True
        self.refresh_thread.start()

        self.animate_timer = QTimer()
        self.animate_timer.timeout.connect(self.animate_text)
        self.animate_timer.start(100)

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

    def refresh_prices(self):
        while True:
            data = self.get_crypto_prices()

            price_info = ""
            for token in self.pinned_tokens:
                color = 'white'  # Domyślnie biały kolor tekstu
                if token in data:
                    price = data[token].get('usd', None)
                    change_percentage = data[token].get('usd_24h_change', None)
                    if price is not None:
                        if change_percentage is not None:
                            if change_percentage < 0:
                                color = 'red'  # Ustaw kolor na czerwony dla ujemnych zmian
                            elif change_percentage > 0:
                                color = 'green'  # Ustaw kolor na zielony dla dodatnich zmian
                        if price < 0.01:
                            price_str = f"({price:.10f})"
                        else:
                            price_str = f"{price:.2f}"
                        if change_percentage is not None:
                            change_text = f" ({change_percentage:.2f}%)"
                        else:
                            change_text = ""
                        price_info += f"{token}: ${price_str}{change_text}\n"
                    else:
                        price_info += f"{token}: Brak danych\n"
                else:
                    price_info += f"{token}: Brak danych\n"
                self.price_label.setText(price_info.strip())
                self.price_label.setStyleSheet(f"color: {color};")  # Ustawienie koloru tekstu
            time.sleep(60)

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

    def animate_text(self):
        text = self.price_label.text()
        if text:
            self.price_label.setText(text[1:] + text[0])

def main():
    app = QApplication(sys.argv)
    widget = CryptoPriceWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
