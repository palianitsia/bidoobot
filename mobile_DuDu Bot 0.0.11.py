import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from threading import Thread, Event
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import re
from datetime import datetime
import os
import pyautogui
import base64
import random


class BidooBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DUDU")
        self.root.geometry("230x500")  # Dimensioni della finestra
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.96)  # Imposta la trasparenza della finestra principale

        icon_path = os.path.normpath(r"duduico.ico")  # Path to the icon
        try:
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            messagebox.showerror("Error", "Unable to load the icon.")

        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        self.stop_event = Event()

        self.used_bids_count = 0

        self.top_frame = tk.Frame(self.root, bg='sky blue', height=200)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.root, bg='goldenrod', height=200)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame = tk.Frame(self.top_frame, bg='sky blue', highlightthickness=10)
        self.main_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        self.username_label = ttk.Label(self.main_frame, text="Username o E-mail:")
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.main_frame)
        self.username_entry.pack(pady=5)
        self.add_context_menu(self.username_entry)

        self.show_email_var = tk.BooleanVar(value=True)  # Checkbox inizialmente selezionato
        self.show_email_check = ttk.Checkbutton(self.main_frame, text="Nascondi Email", variable=self.show_email_var, command=self.toggle_show_email)
        self.show_email_check.pack(pady=5)

        self.password_label = ttk.Label(self.main_frame, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.main_frame, show="")
        self.password_entry.pack(pady=5)
        self.add_context_menu(self.password_entry)

        self.show_password_var = tk.BooleanVar(value=True)  # Checkbox inizialmente selezionato
        self.show_password_check = ttk.Checkbutton(self.main_frame, text="Nascondi Password", variable=self.show_password_var, command=self.toggle_show_password)
        self.show_password_check.pack(pady=5)

        self.auction_id_label = ttk.Label(self.main_frame, text="ID Asta:")
        self.auction_id_label.pack(pady=5)
        self.auction_id_entry = ttk.Entry(self.main_frame)
        self.auction_id_entry.pack(pady=5)
        self.add_context_menu(self.auction_id_entry)

        self.saldo_label = ttk.Label(self.main_frame, text="Saldo: --")
        self.saldo_label.pack(pady=5)

        self.total_bids_label = ttk.Label(self.main_frame, text="Puntate Totali Usate: 0")
        self.total_bids_label.pack(pady=5)

        self.start_button = ttk.Button(self.main_frame, text="Avvia Asta", command=self.start_bot)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(self.main_frame, text="Ferma Asta", command=self.stop_bot)
        self.stop_button.pack(pady=5)

        self.dev_label = ttk.Label(self.bottom_frame, text="dev by vmkhlv", font=('Helvetica', 20, 'bold'), background='goldenrod', foreground="black")
        self.dev_label.pack(side=tk.BOTTOM, pady=10)  # Posiziona la scritta in fondo


    def add_context_menu(self, widget):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Copia", command=lambda: self.copy(widget))
        context_menu.add_command(label="Incolla", command=lambda: self.paste(widget))
        widget.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))

    def copy(self, widget):
        self.root.clipboard_clear()
        self.root.clipboard_append(widget.selection_get())

    def paste(self, widget):
        widget.insert(tk.INSERT, self.root.clipboard_get())

    def toggle_show_email(self):
        if self.show_email_var.get():
            self.username_entry.config(show="")
            self.show_email_check.config(text="Nascondi Email")
        else:
            self.username_entry.config(show="*")
            self.show_email_check.config(text="Mostra Email")

    def toggle_show_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
            self.show_password_check.config(text="Nascondi Password")
        else:
            self.password_entry.config(show="*")
            self.show_password_check.config(text="Mostra Password")

    def start_bot(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        auction_id = self.auction_id_entry.get()

        if not username or not password or not auction_id:
            messagebox.showerror("Error", "All fields are required")
            return

        # Cambia il testo del pulsante a "Asta Attiva"
        self.start_button.config(text="Asta Attiva", state=tk.DISABLED)

        # Resetta l'evento di stop
        self.stop_event.clear()

        # Avvia il bot in un nuovo thread
        thread = Thread(target=self.run_bot, args=(username, password, auction_id))
        thread.start()

    def stop_bot(self):
        self.stop_event.set()
        self.start_button.config(text="Avvia Asta", state=tk.NORMAL)

    def run_bot(self, username, password, auction_id):


        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36"
        }

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service("chromedriver.exe") # Update with the correct path to chromedriver

        driver = webdriver.Chrome(service=service, options=chrome_options)

        log_file = "asta_log.txt"
        self.log_event(log_file, f"Asta avviata: {datetime.now()}")
        self.log_event(log_file, f"Username: {username}")
        self.log_event(log_file, f"Password: {password}")
        self.log_event(log_file, f"ID Asta: {auction_id}")

        try:

            driver.get("https://it.bidoo.com")
            print("Pagina caricata: https://it.bidoo.com")

            self.simulate_human_presence(driver)

            print("Attesa per il pulsante di login...")
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "login_btn"))
            )
            self.simulate_human_click(driver, login_button)
            print("Pulsante di login cliccato")

            time.sleep(random.uniform(0.8, 1.2))

            print("Attesa per il campo email...")
            email_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "field_email"))
            )
            self.simulate_human_typing(driver, email_field, username)
            print("Email inserita")

            print("Inserimento password...")
            password_field = driver.find_element(By.ID, "password")
            self.simulate_human_typing(driver, password_field, password)
            print("Password inserita")

            print("Attesa per il pulsante ENTRA...")
            entra_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btlogin:nth-child(1)'))
            )
            self.simulate_human_click(driver, entra_button)
            print("Pulsante ENTRA cliccato")

            try:
                print("Attesa per il CAPTCHA...")
                captcha_frame = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]'))
                )
                messagebox.showinfo("CAPTCHA", "CAPTCHA detected. Please solve it manually.")
                while True:
                    try:
                        # Wait for user to solve CAPTCHA and page to refresh
                        WebDriverWait(driver, 5).until_not(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]'))
                        )
                        break
                    except:
                        continue
            except:
                print("No CAPTCHA detected")

            time.sleep(2)

            print("Attesa per il saldo dopo il login...")
            balance_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#divSaldoBidMobile'))
            )
            balance = balance_element.text
            self.update_balance(balance)
            print(f"Saldo: {balance}")

            auction_url = f"https://it.bidoo.com/auction.php?a={auction_id}"
            print(f"Apertura della pagina dell'asta: {auction_url}")
            driver.get(auction_url)

            def monitor_and_bid():
                last_second = -1  # Variabile per memorizzare l'ultimo secondo per evitare clic multipli
                consecutive_zero_seconds = 0  # Contatore per i secondi consecutivi a zero

                while not self.stop_event.is_set():
                    try:

                        timer = driver.find_element(By.CSS_SELECTOR, 'body > div.auction-action-info-container.visible-xs.flexible > div.auction-action-info-auction.col-xs-4.text-right > b')

                        timer_text = timer.text.strip()

                        if re.match(r'^\d{1,2}:\d{2}$', timer_text):
                            minutes, seconds = timer_text.split(':')
                            total_seconds = int(minutes) * 60 + int(seconds)

                            print(f"Time left: {total_seconds} seconds")

                            if total_seconds == 1 and last_second != 1:
                                self.start_precise_timer(0.05, self.clicca_pulsante_punta, driver)
                                print("Clicked the PUNTA button")
                                self.log_event(log_file, f"Puntata eseguita: {datetime.now()} - Sono la tua puntata")
                                last_second = 1

                                updated_balance_element = WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, '#divSaldoBidMobile'))
                                )
                                updated_balance = updated_balance_element.text
                                self.update_balance(updated_balance)

                                self.simulate_human_presence(driver)
                            else:
                                last_second = total_seconds

                            if total_seconds == 0:
                                consecutive_zero_seconds += 1
                                if consecutive_zero_seconds >= 2:  # Se rimane a zero per 2 iterazioni
                                    print("Timer stuck at zero. Starting rapid bid sequence.")
                                    for _ in range(10):
                                        self.clicca_pulsante_punta(driver)
                                        time.sleep(0.05)  # Aggiungi un piccolo ritardo tra le puntate
                                    consecutive_zero_seconds = 0  # Resetta il contatore
                            else:
                                consecutive_zero_seconds = 0  # Resetta il contatore se il timer cambia

                        else:
                            print(f"Timer text is not in the expected format: '{timer_text}'")
                    except Exception as e:
                        # Debug: stampa l'eccezione
                        print(f"Exception occurred: {e}")

                    time.sleep(0.05)

            monitor_and_bid()

        finally:

            driver.quit()
            self.stop_event.set()
            self.start_button.config(text="Avvia Asta", state=tk.NORMAL)

    def update_balance(self, balance):
        self.saldo_label.config(text=f"Saldo: {balance}")

    def update_total_bids_label(self, total_bids):
        self.total_bids_label.config(text=f"Puntate Totali Usate: {total_bids}")

    def start_precise_timer(self, duration, callback, driver):
        start_time = time.perf_counter()
        end_time = start_time + duration
        while time.perf_counter() < end_time:
            pass
        callback(driver)

    def clicca_pulsante_punta(self, driver, timeout=10):
        try:
            bottone_punta = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn-lg'))
            )
            self.simulate_human_click(driver, bottone_punta)
            print("Puntata effettuata con successo")
            self.used_bids_count += 1
            self.update_total_bids_label(self.used_bids_count)
            self.log_event("asta_log.txt", f"Puntata eseguita: {datetime.now()} - Puntate Totali Usate: {self.used_bids_count}")
        except Exception as e:
            print(f"Errore durante il tentativo di cliccare il bottone di puntata: {e}")

    def log_event(self, log_file, message):
        with open(log_file, "a") as file:
            file.write(f"{message}\n")

    def simulate_human_presence(self, driver):
        # Simulate scrolling
        pyautogui.scroll(-100)
        time.sleep(random.uniform(1, 2))
        pyautogui.scroll(100)
        # Simulate random mouse movement
        self.simulate_mouse_movement()

    def simulate_mouse_movement(self):
        screen_width, screen_height = pyautogui.size()
        for _ in range(random.randint(5, 10)):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))

    def simulate_human_click(self, driver, element):
        action = webdriver.ActionChains(driver)
        action.move_to_element(element).perform()
        time.sleep(random.uniform(0.1, 0.3))
        action.click(element).perform()

    def simulate_human_typing(self, driver, element, text):
        action = webdriver.ActionChains(driver)
        action.move_to_element(element).perform()
        element.click()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))


if __name__ == "__main__":
    root = tk.Tk()
    app = BidooBotApp(root)
    root.mainloop()
