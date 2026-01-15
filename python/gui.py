from tkinter import *
from tkinter import filedialog, scrolledtext
import os
import glob
from datetime import datetime  # Import do obsługi czasu

# ---------------------------- 🗽🗽🗽 CONSTANTS 🗽🗽🗽------------------------------- #
BLACK = "#000000"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"

# KOLORY POWERSHELL
PS_BLUE = "#012456"
PS_WHITE = "#FFFFFF"
PS_GRAY = "#CCCCCC"


# --- SZKIELET KALKULATORA ---
class Calculator:
    def __init__(self):
        self.csv_files = []

    def set_csv_files(self, files):
        self.csv_files = files

    def calculate_results(self):
        return f"Przetworzono {len(self.csv_files)} plików."


# ---------------------------- 🖥️ GUI CLASS 🖥️ ------------------------------- #

class AnalyzerGUI:
    def __init__(self, calculator):
        self.terminal = None
        self.window = Tk()
        self.calculator = calculator
        self.window.title("ReluxLightAnalyzer v2.0 - PowerShell Professional")
        self.window.config(padx=40, pady=30, bg=YELLOW)

        self.csv_files = []
        self.folder_path = ""
        self.setup_main_window()

    def setup_main_window(self):
        # 1. Tytuł
        title_label = Label(self.window, text="Analizer wyników oświetleniowych (RELUX)",
                            bg=YELLOW, fg=PS_BLUE, font=(FONT_NAME, 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 2. Obrazek (Canvas)
        self.canvas = Canvas(self.window, width=640, height=250, bg=YELLOW, highlightthickness=0)
        try:
            self.latarnie_img = PhotoImage(file="./images/latarnie.png")
            self.canvas.create_image(320, 125, image=self.latarnie_img)
        except:
            self.canvas.create_rectangle(20, 20, 620, 230, outline=PS_BLUE, width=1, dash=(5, 2))
            self.canvas.create_text(320, 125, text="[ System Visualization Ready ]", fill=PS_BLUE, font=(FONT_NAME, 10))

        self.canvas.grid(row=1, column=1)

        # 3. TERMINAL POWERSHELL Z TIMESTAMPEM (Wiersz 2)
        terminal_frame = Frame(self.window, bg=PS_GRAY, bd=1)
        terminal_frame.grid(row=2, column=1, pady=15)

        self.terminal = scrolledtext.ScrolledText(
            terminal_frame,
            width=85,
            height=12,
            bg=PS_BLUE,
            fg=PS_WHITE,
            insertbackground="white",
            font=("Consolas", 9),
            padx=10,
            pady=10
        )
        self.terminal.pack()

        # Powitanie systemowe
        self.log_message("Windows PowerShell - Relux Analyzer Edition")
        self.log_message("Copyright (C) 2026 Gemini Capable AI. All rights reserved.")
        self.log_message("-" * 60)

        # 4. Przyciski boczne
        start_button = Button(self.window, width=12, height=2, text="START",
                              command=self.start_results_window, bg=GREEN, font=("Arial", 9, "bold"))
        start_button.grid(row=1, column=0, padx=10)

        reset_button = Button(self.window, width=12, height=2, text="CLEAR HOST",
                              command=self.reset_app, font=("Arial", 9))
        reset_button.grid(row=1, column=2, padx=10)

        # Przycisk dolny
        select_folder_button = Button(self.window, text="📂 WYBIERZ FOLDER PROJEKTU (.CSV)",
                                      command=self.select_csv_folder, bg=PS_BLUE, fg=PS_WHITE,
                                      font=(FONT_NAME, 11, "bold"), padx=20)
        select_folder_button.grid(row=3, column=1, pady=10)

        self.folder_label = Label(self.window, text="Status: IDLE", bg=YELLOW, fg=PS_BLUE,
                                  font=(FONT_NAME, 9, "italic"))
        self.folder_label.grid(row=4, column=1)

    def log_message(self, message):
        """Dodaje linię tekstu z aktualną datą i godziną (Timestamp)"""
        if self.terminal:
            # Pobieranie aktualnego czasu
            now = datetime.now().strftime("%H:%M:%S")

            self.terminal.config(state=NORMAL)

            # Formatowanie: Czas | Wiadomość
            if message == "" or "-" in message:
                full_log = f"{message}\n"
            else:
                full_log = f"[{now}] PS > {message}\n"

            self.terminal.insert(END, full_log)
            self.terminal.see(END)
            self.terminal.config(state=DISABLED)

    def select_csv_folder(self):
        folder_path = filedialog.askdirectory(title="Wybierz folder z danymi")

        if folder_path:
            self.folder_path = folder_path
            self.log_message(f"Zmieniono ścieżkę na: {folder_path}")

            search_pattern = os.path.join(folder_path, "*.csv")
            self.csv_files = glob.glob(search_pattern)

            if self.csv_files:
                self.log_message(f"SUCCESS: Wykryto {len(self.csv_files)} plików do analizy.")
                self.calculator.set_csv_files(self.csv_files)
                self.folder_label.config(text=f"Aktywny folder: {os.path.basename(folder_path)}", fg="black")
            else:
                self.log_message("ERROR: Brak plików CSV w wybranej lokalizacji!")
                self.folder_label.config(text="BŁĄD: Brak danych!", fg=RED)

    def reset_app(self):
        """Czyści dane i terminal"""
        self.csv_files = []
        self.terminal.config(state=NORMAL)
        self.terminal.delete('1.0', END)
        self.terminal.config(state=DISABLED)
        self.log_message("System Reset... Clear-Host executed.")
        self.folder_label.config(text="Status: IDLE", fg=PS_BLUE)

    def start_results_window(self):
        if not self.csv_files:
            self.log_message("WARNING: Nie można uruchomić analizy bez danych wejściowych.")
            return

        self.log_message("Inicjalizacja obliczeń...")
        self.calculator.calculate_results()

        results_window = Toplevel(self.window)
        results_window.title("Raporty Relux")
        results_window.config(padx=30, pady=30, bg=YELLOW)

        # Proste menu w nowym oknie
        Label(results_window, text="WYBIERZ PARAMETRY RAPORTU", bg=YELLOW, font=(FONT_NAME, 12, "bold")).pack(pady=10)

        self.selected_class = StringVar(results_window)
        self.selected_class.set("M3")

        OptionMenu(results_window, self.selected_class, "M1", "M2", "M3", "M4", "M5", "M6").pack(pady=5)

        Button(results_window, text="GENERUJ TOP 10", bg=GREEN, width=20,
               command=lambda: self.log_message(f"Generowanie TOP 10 dla klasy {self.selected_class.get()}...")).pack(
            pady=5)

        self.log_message("UI: Otwarto okno parametrów raportowania.")

    def run(self):
        self.window.mainloop()


# --- START ---
if __name__ == "__main__":
    app = AnalyzerGUI(Calculator())
    app.run()