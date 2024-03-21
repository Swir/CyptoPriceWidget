import tkinter as tk
from tkinter import ttk
import requests
import json

class CryptoPriceWidget:
    def __init__(self, master):
        self.master = master
        self.master.title("Crypto Price Widget")
        self.master.configure(bg="black")
        self.master.geometry("500x400")

        self.label = tk.Label(master, text="Wpisz nazwę kryptowaluty:", fg="green", bg="black", font=("Courier", 14))
        self.label.pack()

        self.search_combobox = ttk.Combobox(master, width=30, font=("Courier", 12))
        self.search_combobox.pack()

        self.search_combobox.bind("<KeyRelease>", self.update_list)

        self.price_label = tk.Label(master, text="", bg="black", font=("Courier", 12), justify="left", fg="green")  # Zmiana koloru tekstu na zielony
        self.price_label.pack()

        self.pin_button = tk.Button(master, text="Przypnij", command=self.pin_token, fg="green", bg="black", font=("Courier", 12))
        self.pin_button.pack()

        self.pinned_tokens = self.load_pinned_tokens()
        self.colors = {}  # Słownik do przechowywania kolorów dla poszczególnych kryptowalut

        self.update_crypto_list()
        self.update_combobox_values()
        self.refresh_prices()
        self.animate_text()

    def update_list(self, event=None):
        search_text = self.search_combobox.get().strip().lower()

        if not search_text:
            self.filtered_crypto_list = self.crypto_list
        else:
            self.filtered_crypto_list = [crypto for crypto in self.crypto_list if search_text in crypto.lower()]

        self.update_combobox_values()

    def update_combobox_values(self):
        self.search_combobox['values'] = self.filtered_crypto_list

    def pin_token(self):
        selected_crypto = self.search_combobox.get().strip()
        if selected_crypto and selected_crypto not in self.pinned_tokens:
            self.pinned_tokens.append(selected_crypto)
            self.colors[selected_crypto] = 'black'  # Ustaw domyślny kolor na czarny
            self.update_pinned_tokens()
            self.save_pinned_tokens()

    def update_pinned_tokens(self):
        self.refresh_prices()

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
            response.raise_for_status()  # Sprawdź, czy otrzymano kod 2xx
            data = response.json()
            self.crypto_list = [crypto['id'] for crypto in data]
            self.filtered_crypto_list = self.crypto_list
        except requests.exceptions.HTTPError as err:
            print(f"Błąd pobierania danych: {err}")
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {e}")

    def get_crypto_prices(self):
        tokens_str = ','.join(self.pinned_tokens)
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={tokens_str}&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(url)
            response.raise_for_status()  # Sprawdź, czy otrzymano kod 2xx
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Błąd pobierania danych: {err}")
            return {}
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {e}")
            return {}

    def refresh_prices(self):
        data = self.get_crypto_prices()
        price_info = ""
        
        for token in self.pinned_tokens:
            color = self.colors.get(token, 'black')  # Ustaw kolor na domyślny dla danej kryptowaluty
            if token in data:
                price = data[token].get('usd', None)
                change_percentage = data[token].get('usd_24h_change', None)
                if price is not None:
                    if price < 0.01:
                        price_str = f"({price:.10f})"
                    else:
                        price_str = f"{price:.2f}"
                    if change_percentage is not None:
                        if change_percentage < 0:
                            color = 'red'
                        elif change_percentage > 0:
                            color = 'green'
                        change_text = f" ({change_percentage:.2f}%)"
                    else:
                        change_text = ""
                    price_info += f"{token}: ${price_str}{change_text}\n"
                else:
                    price_info += f"{token}: Brak danych\n"
            else:
                price_info += f"{token}: Brak danych\n"
            self.price_label.config(text=price_info.strip(), fg="green", bg="black", font=("Courier", 12), justify="left")

        self.master.after(60000, self.refresh_prices)  # Odśwież co 1 minutę

    def animate_text(self):
        text = self.price_label.cget("text")
        if text:
            self.price_label.config(text=text[1:] + text[0])
        self.master.after(100, self.animate_text)

def main():
    root = tk.Tk()
    root.configure(bg="black")
    crypto_widget = CryptoPriceWidget(root)
    root.mainloop()

if __name__ == "__main__":
    main()
