import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
import glob
from datetime import datetime
from analysis import AnalysisCalculator
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



# ---------------------------- 🖥️ MAIN GUI CLASS 🖥️ ------------------------------- #

class AnalyzerGUI:
    def __init__(self, engine):
        self.engine = engine
        self.terminal = None
        self.window = tk.Tk()
        self.window.title("ReluxLightAnalyzer - IDE Console Mode")
        self.window.config(padx=40, pady=30, bg=YELLOW)

        self.csv_files = []
        self.folder_path = ""
        self.setup_main_window()

    def log_message(self, message, color=PC_TEXT):
        """Dodaje linię tekstu do terminala w stylu PyCharm"""
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
        # 1. Tytuł
        title_label = tk.Label(self.window, text="Analizer wyników oświetleniowych (RELUX)",
                               bg=YELLOW, fg=PC_BG, font=(FONT_NAME, 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 2. Wizualizacja (Canvas)
        self.canvas = tk.Canvas(self.window, width=640, height=200, bg=YELLOW, highlightthickness=0)
        self.canvas.create_rectangle(20, 20, 620, 180, outline=PC_BG, width=1)
        self.canvas.create_text(320, 100, text="[ Engine Status: Ready ]", fill=PC_BG, font=(FONT_NAME, 10))
        self.canvas.grid(row=1, column=1)

        # 3. TERMINAL W STYLU PYCHARM
        terminal_frame = tk.Frame(self.window, bg="#323232", bd=1)
        terminal_frame.grid(row=2, column=1, pady=15)

        self.terminal = scrolledtext.ScrolledText(
            terminal_frame, width=85, height=10, bg=PC_BG, fg=PC_TEXT,
            insertbackground="white", font=("Consolas", 10), padx=10, pady=10
        )
        self.terminal.tag_config("timestamp", foreground=PC_TIME)
        self.terminal.pack()

        # Log startowy
        self.log_message("C:\\Users\\Project\\venv\\Scripts\\python.exe main.py")
        self.log_message("Connected to analyzer engine. Initializing...")

        # 4. Przyciski
        tk.Button(self.window, text="START", width=12, height=2, bg=GREEN, font=("Arial", 9, "bold"),
                  command=self.start_results_window).grid(row=1, column=0, padx=10)

        tk.Button(self.window, text="RESET", width=12, height=2, font=("Arial", 9),
                  command=self.reset_app).grid(row=1, column=2, padx=10)

        tk.Button(self.window, text="📂 WYBIERZ FOLDER Z PLIKAMI CSV",
                  command=self.select_csv_folder, bg="#3c3f41", fg="white",
                  font=(FONT_NAME, 11, "bold"), padx=20).grid(row=3, column=1, pady=10)

        self.folder_label = tk.Label(self.window, text="Processes: 0 running", bg=YELLOW, fg="#666666",
                                     font=(FONT_NAME, 9))
        self.folder_label.grid(row=4, column=1)

    def select_csv_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.log_message(f"Scanning directory: {folder_path}")
            self.csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

            if self.csv_files:
                self.log_message(f"Found {len(self.csv_files)} .csv files.")
                self.engine.set_csv_files(self.csv_files)
                self.folder_label.config(text=f"Loaded: {len(self.csv_files)} files", fg="black")
            else:
                self.log_message("Error: No .csv files found in selected path.")

    def reset_app(self):
        self.csv_files = []
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete('1.0', tk.END)
        self.terminal.config(state=tk.DISABLED)
        self.log_message("Process finished with exit code 0 (Reset)")

    # ---------------------------- 📊 RESULTS WINDOW 📊 ------------------------------- #

    def start_results_window(self):
        if not self.csv_files:
            self.log_message("Execution failed: No input data.")
            return

        self.log_message("Building UI Components...")
        res_win = tk.Toplevel(self.window)
        res_win.title("Analysis Panel")
        res_win.config(padx=20, pady=20, bg=YELLOW)

        # 1. GÓRA: 8 MENU
        menu_labels = ["Rozmieszczenie", "Oprawa", "Klasa ośw.", "Szerokość", "Moduł", "Wys. mont.", "Nawis",
                       "Pochylenie"]
        top_frame = tk.Frame(res_win, bg=YELLOW)
        top_frame.pack(side="top", fill="x", pady=(0, 20))

        for c in range(8):
            m_container = tk.Frame(top_frame, bg=YELLOW)
            m_container.grid(row=0, column=c, padx=5, sticky="n")
            tk.Label(m_container, text=menu_labels[c], bg=YELLOW, font=(FONT_NAME, 8, "bold")).pack()
            v = tk.StringVar(res_win);
            v.set("Wybierz")
            opt = tk.OptionMenu(m_container, v, "Domyślne", "Zmień", "Reset")
            opt.config(bg=PINK, font=(FONT_NAME, 8), width=10)
            opt.pack(pady=(2, 0))

        # 2. ŚRODEK: WIZUALIZACJA
        mid_frame = tk.Frame(res_win, width=950, height=400, bg="white", highlightthickness=2, highlightbackground=RED)
        mid_frame.pack(fill="both", expand=True, pady=10)
        mid_frame.pack_propagate(False)
        tk.Label(mid_frame, text="GRAPHICAL DATA ANALYSIS", bg="white", font=(FONT_NAME, 16, "bold")).pack(expand=True)

        # 3. DÓŁ: 16 PRZYCISKÓW
        # --- 🛠️ FULL BLUEPRINT MAP (Podpinamy funkcje tutaj) 🛠️ ---
        blueprint = {
            # Rząd 1
            "M1 Oblicz": self.engine.print_madafaka,
            "M2 Analiza": None,
            "M3 Wyniki": None,
            "M4 Projekt": None,
            "M5 Rozstaw": None,
            "M6 Norma": None,
            "CSV Eksport": None,
            "PDF Druk": None,

            # Rząd 2
            "M1 Raport": None,
            "M2 Wykres": None,
            "M3 Dane": None,
            "M4 Koszty": None,
            "M5 Moc": None,
            "M6 Klasa": None,
            "CSV Import": None,
            "ZAMKNIJ": res_win.destroy,
        }
        # ---------------------------------------------------------
        # ---------------------------------------------------------
        bottom_frame = tk.Frame(res_win, bg=YELLOW)
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 0))

        # Iterujemy bezpośrednio po słowniku (używając enumerate, by mieć indeks i)
        for i, (title, func) in enumerate(blueprint.items()):
            row, col = divmod(i, 8)

            if func is not None:
                cmd = func
            else:
                cmd = lambda t=title: self.log_message(f"Wciśnięto przycisk: {t}")

            btn = tk.Button(bottom_frame, text=title, bg=GREEN, font=(FONT_NAME, 8, "bold"),
                            height=2, command=cmd)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        for i in range(8): bottom_frame.grid_columnconfigure(i, weight=1)
        self.log_message("Results window opened successfully.")

    def run(self):
        self.window.mainloop()
