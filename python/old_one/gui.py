import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext
import os
import glob
import threading
from datetime import datetime
import plots

# ---------------------------- 🗽🗽🗽 CONSTANTS 🗽🗽🗽------------------------------- #
BLACK = "#000000"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"

# KOLORY PYCHARM (DARCULA / JETBRAINS)
PC_BG = "#1e1f22"  # Ciemne tło terminala PyCharm
PC_TEXT = "#bcbec4"  # Jasnoszary tekst (standard w PyCharm)
PC_TIME = "#56a8f5"  # Niebieski dla timestampów
PC_SUCCESS = "#6aab73"  # Zielony dla pozytywnych komunikatów


# ----------------------------  CONSOLE WINDOW  ------------------------------- #
# ----------------------------  CONSOLE WINDOW  ------------------------------- #
class ConsoleWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("System Progress Console")
        self.top.geometry("700x450")
        self.top.config(bg="#1e1f22")

        # ScrolledText - ustawiamy state="disabled", aby użytkownik nie mógł tam pisać ręcznie
        self.text = scrolledtext.ScrolledText(
            self.top, bg="#1e1f22", fg="#bcbec4",
            font=("Consolas", 10), insertbackground="white",
            padx=10, pady=10, state="disabled"
        )
        self.text.pack(fill="both", expand=True)

        # Definicja stylów (tagów)
        self.text.tag_config("timestamp", foreground="#7a7e85")
        self.text.tag_config("info", foreground="#bcbec4")
        self.text.tag_config("success", foreground="#62bc64", font=("Consolas", 10, "bold"))
        self.text.tag_config("warning", foreground="#d19a66")
        self.text.tag_config("error", foreground="#f44747", font=("Consolas", 10, "bold"))
        self.text.tag_config("header", foreground="#b452cd", font=("Consolas", 11, "bold"))

    def log(self, message, level="info"):
        """Główna metoda wypisywania do konsoli"""
        from datetime import datetime
        now = datetime.now().strftime("[%H:%M:%S] ")

        self.text.config(state="normal")  # Odblokuj do zapisu
        self.text.insert("end", now, "timestamp")

        # Wybór symbolu w zależności od poziomu
        symbol = {
            "info": "ℹ ",
            "success": "✅ ",
            "warning": "⚠️ ",
            "error": "❌ ",
            "header": "🚀 "
        }.get(level, "")

        self.text.insert("end", f"{symbol}{message}\n", level)
        self.text.config(state="disabled")  # Zablokuj ponownie
        self.text.see("end")  # Autoscroll na dół
        self.top.update_idletasks()

# ---------------------------- 🖥️ MAIN GUI CLASS 🖥️ ------------------------------- #
# ---------------------------- 🖥️ MAIN GUI CLASS 🖥️ ------------------------------- #
# ---------------------------- 🖥️ MAIN GUI CLASS 🖥️ ------------------------------- #
class AnalyzerGUI:
    def __init__(self, engine):
        self.menu_vars = None
        self.option_menus = None
        self.engine = engine
        self.terminal = None
        self.console = None
        self._all_data_cache = None
        self.window = tk.Tk()
        self.window.title("ReluxLightAnalyzer - IDE Console Mode")
        self.window.config(padx=40, pady=30, bg=YELLOW)

        self.csv_files = []
        self.folder_path = ""
        self.setup_main_window()
        self._init_system_console()

    def _init_system_console(self):
        """Otwiera System Progress Console od razu po starcie programu."""
        if self.console:
            return
        self.console = ConsoleWindow(self.window)
        self.engine.set_console(self.console)
        try:
            plots.set_logger(self.console.log)
        except Exception:
            pass
        self.console.log("SYSTEM START", "header")

    def log_message(self, message, color=PC_TEXT):
        """Dodaje linię tekstu do terminala w pierwszym pierwszym oknie programu"""
        # Jeśli istnieje "System Progress Console", kierujemy logi tam,
        # żeby nie dublować komunikatów w dwóch terminalach.
        if hasattr(self, "console") and self.console:
            self.console.log(message, "info")
            return
        if self.terminal:
            now = datetime.now().strftime("%H:%M:%S")
            self.terminal.config(state=tk.NORMAL)

            # Wstawianie timestampu z innym kolorem (niebieskim)
            start_index = self.terminal.index(tk.END)
            self.terminal.insert(tk.END, f"[{now}] ", "timestamp")

            # Wstawianie właściwej wiadomości
            self.terminal.insert(tk.END, f"{message}\n")

            # Przewijanie i blokada
            self.terminal.see(tk.END)
            self.terminal.config(state=tk.DISABLED)

    def setup_main_window(self):
        """Tworzy nowoczesny, minimalistyczny interfejs w stylu Dark Mode"""
        # Główne kolory modern UI
        BG_MAIN = "#121212"    # Prawie czarny mat
        ACCENT_START = "#00ff88" # Neonowa zieleń
        ACCENT_RESET = "#ff4444" # Neonowa czerwień
        ACCENT_GRAY = "#2a2a2a"  # Ciemny szary dla kart

        self.window.config(bg=BG_MAIN, padx=50, pady=40)

        # 1. Header - Cienki, nowoczesny font
        title_label = tk.Label(
            self.window, text="RELUX ANALYZER SYSTEM",
            bg=BG_MAIN, fg="white", font=("Segoe UI Light", 28)
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 40))

        # 2. Kontener na przyciski (Karta sterowania)
        button_frame = tk.Frame(self.window, bg=BG_MAIN)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)

        # Stylizacja przycisków — używamy FLAT design
        # Dodajemy 'activebackground', żeby przycisk reagował na najechanie
        self.start_btn = tk.Button(
            button_frame, text="RUN ENGINE",
            width=18, height=2, bg=ACCENT_START, fg=BG_MAIN,
            font=("Segoe UI Semibold", 12),
            command=self.start_presetup_window,
            relief="flat", bd=0, cursor="hand2",
            activebackground="#00cc6e"
        )
        self.start_btn.pack(side="left", padx=15)

        self.reset_btn = tk.Button(
            button_frame, text="RESET CORE",
            width=18, height=2, bg=ACCENT_GRAY, fg="white",
            font=("Segoe UI Semibold", 12),
            command=self.reset_app,
            relief="flat", bd=0, cursor="hand2",
            activebackground="#3a3a3a"
        )
        self.reset_btn.pack(side="left", padx=15)

        # 3. GRAFIKA (zamiast starego terminala)
        image_frame = tk.Frame(self.window, bg=BG_MAIN, padx=2, pady=2)
        image_frame.grid(row=2, column=0, columnspan=2, pady=30)

        image_path = os.path.join(os.path.dirname(__file__), "images", "latarnie.png")
        try:
            self.main_image = tk.PhotoImage(file=image_path)
            image_label = tk.Label(image_frame, image=self.main_image, bg=BG_MAIN)
            image_label.pack()
        except Exception:
            image_label = tk.Label(
                image_frame,
                text="Nie udało się wczytać obrazu latarnie.png",
                bg=BG_MAIN,
                fg="#888888",
                font=("Segoe UI", 12)
            )
            image_label.pack()

        # 4. Footer - Przycisk wyboru folderu jako subtelny link/przycisk
        select_btn = tk.Button(
            self.window, text="📂 SELECT DATA SOURCE",
            command=self.select_csv_folder,
            bg=BG_MAIN, fg="#888888",
            font=("Segoe UI", 20),
            relief="flat", bd=0, cursor="hand2",
            activebackground=BG_MAIN, activeforeground="white"
        )
        select_btn.grid(row=3, column=0, columnspan=2, pady=20)

        self.status_label = tk.Label(
            self.window, text="READY // STANDBY",
            bg=BG_MAIN, fg="#444444", font=("Consolas", 8)
        )
        self.status_label.grid(row=4, column=0, columnspan=2)

    def select_csv_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_path = path
            self._all_data_cache = None

            # --- KLUCZ: Podpinamy silnik pod TĘ KLASĘ GUI ---
            # Teraz silnik będzie mógł wywołać self.log()
            self.engine.set_console(self)

            self.log_message(f"Scanning directory: {path}")
            self.csv_files = glob.glob(os.path.join(path, "*.csv"))

            if self.csv_files:
                self.log_message(f"Found {len(self.csv_files)} .csv files.")
                # Teraz to wywołanie zadziała bez błędu w PyCharmie
                self.engine.set_csv_files(self.csv_files)

                self.status_label.config(
                    text=f"SYSTEM READY // {len(self.csv_files)} FILES LOADED",
                    fg="#00ff88"
                )
            else:
                self.log_message("Error: No .csv files found in selected path.")
                self.status_label.config(text="SYSTEM ERROR // NO DATA", fg="#ff4444")

    def reset_app(self):
        self.csv_files = []
        self._all_data_cache = None
        # Zamykamy wszystkie okna poza głównym
        for child in list(self.window.winfo_children()):
            try:
                if isinstance(child, tk.Toplevel):
                    if hasattr(self, "console") and self.console and child is self.console.top:
                        continue
                    child.destroy()
            except Exception:
                pass
        self.log_message("Process finished with exit code 0 (Reset)")


    # ---------------------------- 📊 PRESETUP WINDOW 📊 ------------------------------- #
    def start_presetup_window(self):
        """Krok 1: Otwarcie konsoli i odczekanie chwili na jej narysowanie przed skanowaniem"""
        if not self.csv_files:
            self.log_message("Błąd: Najpierw wybierz folder z plikami!")
            return

        # 1. Upewniamy się, że konsola już istnieje
        self._init_system_console()
        self.console.log("INICJALIZACJA PROCESU", "header")

        # 2. Zamiast blokować wątek od razu, dajemy Tkinterowi 200ms na narysowanie okna
        # Metoda .after(opóźnienie, funkcja) jest tu kluczowa
        self.window.after(200, self._continue_presetup)

    def _continue_presetup(self):
        """Część dalsza po krótkiej pauzie na odświeżenie GUI"""
        self.console.log("Skanowanie plików CSV w poszukiwaniu opraw...", "info")

        # Teraz skanowanie może trwać nawet kilka sekund, a okno konsoli już tam będzie
        lum_list = self.engine.get_unique_luminaires()

        if not lum_list:
            self.console.log("Nie znaleziono opraw w plikach!", "error")
            return

        self.console.log(f"Znaleziono {len(lum_list)} unikalnych modeli opraw.", "success")

        # Otwieramy okno parametrów
        self.show_mf_setup_window(lum_list)


    def show_mf_setup_window(self, lum_list):
        # 3. Tworzymy okno ustawień (sett_win) - Twoja oryginalna stylizacja
        sett_win = tk.Toplevel(self.window)
        sett_win.title("PARAMETRY ANALIZY")
        sett_win.geometry("700x500")
        sett_win.config(bg="#121212", padx=20, pady=20)

        # --- Sekcja Główne Parametry ---
        main_params = tk.LabelFrame(sett_win, text=" PARAMETRY GLOBALNE ", bg="#121212", fg="#00ff88")
        main_params.pack(fill="x", pady=10)

        tk.Label(main_params, text="Czas świecenia [h/rok]:", bg="#121212", fg="white").grid(row=0, column=0, padx=5,
                                                                                             pady=5)
        self.ent_burning = tk.Entry(main_params, width=10)
        self.ent_burning.insert(0, "4000")
        self.ent_burning.grid(row=0, column=1)

        tk.Label(main_params, text="Max zapas Lav [%] (0=brak):", bg="#121212", fg="white").grid(row=0, column=2,
                                                                                                 padx=5, pady=5)
        self.ent_max_lav = tk.Entry(main_params, width=10)
        self.ent_max_lav.insert(0, "0")
        self.ent_max_lav.grid(row=0, column=3)

        # --- Sekcja Tabela MF ---
        tk.Label(sett_win, text="Współczynniki utrzymania (MF) dla opraw:", bg="#121212", fg="#569cd6").pack()

        mf_container = tk.Frame(sett_win, bg="#1e1e1e")
        mf_container.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(mf_container, bg="#1e1e1e", highlightthickness=0)
        scroll_v = ttk.Scrollbar(mf_container, orient="vertical", command=canvas.yview)
        self.mf_scroll_frame = tk.Frame(canvas, bg="#1e1e1e")

        self.mf_entries = {}
        for lum in lum_list:
            row = tk.Frame(self.mf_scroll_frame, bg="#1e1e1e")
            row.pack(fill="x", pady=1)
            tk.Label(row, text=lum, bg="#1e1e1e", fg="white", width=60, anchor="w").pack(side="left")
            ent = tk.Entry(row, width=8)
            ent.insert(0, "0.8")
            ent.pack(side="right", padx=10)
            self.mf_entries[lum] = ent

        canvas.create_window((0, 0), window=self.mf_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_v.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll_v.pack(side="right", fill="y")

        self.mf_scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Przycisk startowy
        tk.Button(sett_win, text="ZATWIERDŹ I URUCHOM MIELENIE", bg="#00ff88", fg="black",
                  command=lambda: self.run_calculation_thread(sett_win)).pack(pady=10)

    def run_calculation_thread(self, sett_win):
        """Krok 2: Pobranie wartości z GUI i start wątku w tle"""
        try:
            config = {
                "burning_hours": float(self.ent_burning.get()),
                "max_lav_excess": float(self.ent_max_lav.get()),
                "mf_map": {lum: float(ent.get()) for lum, ent in self.mf_entries.items()}
            }
        except ValueError:
            self.console.log("Błąd: Nieprawidłowe wartości w parametrach!", "error")
            return

        # Zamykamy okno ustawień, ale KONSOLA zostaje otwarta
        sett_win.destroy()

        # Logujemy parametry do istniejącej konsoli
        self.console.log("PARAMETRY ZATWIERDZONE", "header")
        self.console.log(f"Czas świecenia: {config['burning_hours']}h", "info")
        self.console.log("Rozpoczynam obliczenia główne...", "info")

        def worker():
            try:
                # Silnik pisze bezpośrednio do self.console za pomocą self.log()
                self.engine.calculate_results(config=config)

                self._all_data_cache = None
                self.window.after(0, lambda: self.console.log("Obliczenia zakończone sukcesem!", "success"))
                # Otwieramy panel finałowy przekazując istniejącą konsolę
                self.window.after(500, lambda: self.open_final_panel(self.console))
            except Exception as e:
                self.window.after(0, lambda: self.console.log(f"BŁĄD KRYTYCZNY: {e}", "error"))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    # ---------------------------- 📊 FINAL WINDOW 📊 ------------------------------- #
    def open_final_panel(self, console_win):
        """Maksymalnie uproszczony panel — tylko filtry i przyciski"""

        # --- KLUCZOWA POPRAWKA ---
        # Musimy powiedzieć silnikowi: "Hej, od teraz pisz do tej konkretnej konsoli"
        self.engine.set_console(console_win)

        # Teraz to wywołanie poprawnie wyśle log "Indeksowanie bazy filtrów..." do okna GUI
        unique_items = self.engine.get_unique_items()

        res_win = tk.Toplevel(self.window)
        res_win.title("PARAMETRY ANALIZY")
        res_win.geometry("400x900")
        res_win.config(bg="#1e1e1e", padx=20, pady=20)

        # --- 1. SEKCJA FILTRÓW ---
        tk.Label(res_win, text="--- FILTRY PROJEKTU ---", bg="#1e1e1e", fg="#569cd6",
                 font=("Arial", 10, "bold")).pack(pady=(0, 15))

        self.menu_vars = {}
        for label, vals in unique_items.items():
            f_container = tk.Frame(res_win, bg="#1e1e1e")
            f_container.pack(fill="x", pady=5)
            tk.Label(f_container, text=label, bg="#1e1e1e", fg="#aaaaaa", font=("Arial", 9)).pack(anchor="w")

            var = tk.StringVar()
            self.menu_vars[label] = var
            cb = ttk.Combobox(f_container, textvariable=var, values=vals, state="readonly")
            cb.pack(fill="x")
            if vals: cb.current(0)

        # --- 2. SEKCJA PRZYCISKÓW (NARZĘDZIA) ---
        tk.Label(res_win, text="--- NARZĘDZIA ---", bg="#1e1e1e", fg="#00ff88",
                 font=("Arial", 10, "bold")).pack(pady=(25, 15))

        # Pomocnicze funkcje
        # Upewnij się, że Twoje funkcje filtrujące w silniku też używają logowania!
        f = lambda: {label: var.get() for label, var in self.menu_vars.items()}
        def _get_all_data():
            if self._all_data_cache is None:
                self._all_data_cache = self.engine.get_all_data()
            return self._all_data_cache
        data = lambda: _get_all_data()
        filtered = lambda: self.engine.get_filtered_data(f())

        blueprint = [
            ("1. SKUTECZNOŚĆ vs SZEROKOŚĆ", lambda: plots.draw_arrangement_comparison_agg(
                self.engine.get_arrangement_comparison_data(f(), 'efficiency'), 'efficiency'),
             "#2d2d2d"),
            ("2. ZUŻYCIE De vs SZEROKOŚĆ", lambda: plots.draw_arrangement_comparison_agg(
                self.engine.get_arrangement_comparison_data(f(), 'De'), 'De'), "#2d2d2d"),
            ("3. MOC Dp vs SZEROKOŚĆ", lambda: plots.draw_arrangement_comparison_agg(
                self.engine.get_arrangement_comparison_data(f(), 'Dp'), 'Dp'), "#2d2d2d"),
            ("4. TOP 20: JEDNOSTRONNY", lambda: plots.draw_top20_fixtures(filtered(), 'Jednostronny'), "#3a3f4b"),
            ("5. TOP 20: NAPRZECIWLEGŁY", lambda: plots.draw_top20_fixtures(filtered(), 'Naprzeciwlegly'), "#3a3f4b"),
            ("6. TOP 20: NAPRZEMIANLEGŁY", lambda: plots.draw_top20_fixtures(filtered(), 'Naprzemianlegly'), "#3a3f4b"),
            ("7. BILANS STRUMIENIA (KLASA)", lambda: plots.draw_flux_balance(filtered(), f().get('Klasa oświetleniowa')), "#1e3d59"),
            ("8. ROZKŁAD Dp (ŚWIECZKOWY)", lambda: plots.draw_dp_boxplot(filtered(), f().get('Klasa oświetleniowa')), "#1e3d59"),
            ("9. HISTOGRAM ENERGII De", lambda: plots.draw_de_histogram(filtered()), "#1e3d59"),

            # Przycisk, o który pytałeś wcześniej - teraz log "Wyświetlono 100 wierszy" trafi do GUI
            ("M2: LOSOWE 100 WIERSZY", self.show_random_100, "#2d2d2d"),
            ("ZAMKNIJ PANEL", res_win.destroy, "#4b2121")
        ]

        tools_frame = tk.Frame(res_win, bg="#1e1e1e")
        tools_frame.pack(fill="x", pady=5)
        tools_frame.grid_columnconfigure(0, weight=1)
        tools_frame.grid_columnconfigure(1, weight=1)

        for idx, (text, cmd, color) in enumerate(blueprint):
            btn = tk.Button(tools_frame, text=text, command=cmd, bg=color, fg="white",
                            font=("Arial", 8, "bold"), height=1, relief="flat",
                            activebackground="#00ff88", cursor="hand2", pady=2)
            row = idx // 2
            col = idx % 2
            btn.grid(row=row, column=col, sticky="ew", padx=3, pady=3)

    def show_random_100(self):
        """Wyświetla okno z losowymi 100 wierszami i loguje to do terminala GUI"""
        # 1. Pobieramy dane
        full_df = self.engine.get_all_data()

        if full_df is None or full_df.empty:
            from tkinter import messagebox
            messagebox.showwarning("Brak danych", "Baza danych jest pusta. Najpierw przeprowadź mielenie.")
            return

        # 2. Losujemy wiersze
        sample_size = min(100, len(full_df))
        random_df = full_df.sample(n=sample_size)

        # 3. Tworzymy okno podglądu
        top = tk.Toplevel(self.window)
        top.title(f"Random {sample_size} Rows Preview")
        top.geometry("1200x600")
        top.config(bg="#1e1f22")

        # Stylizacja tabeli (Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2d30", foreground="white", fieldbackground="#2b2d30", borderwidth=0)
        style.map("Treeview", background=[('selected', '#2a5082')])

        table_frame = tk.Frame(top, bg="#1e1f22")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 4. Tworzymy tabelę i scrollbary
        cols = list(random_df.columns)
        tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Nagłówki
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        # 5. Wstawianie danych
        for _, row in random_df.iterrows():
            values = [f"{v:.4f}" if isinstance(v, (float, int)) and not isinstance(v, bool) and abs(v) < 1000 else v for
                      v in row]
            tree.insert("", "end", values=values)

        # Logujemy do "System Progress Console", a gdy jej nie ma, do głównego terminala
        message = f"Wyświetlono {sample_size} losowych wierszy w nowym oknie."
        if hasattr(self, "console") and self.console:
            self.console.log(message, "success")
        else:
            self.log_message(message, "#00ff88")

    def run(self):
        self.window.mainloop()
