from tkinter import *
from tkinter import filedialog
import os
import glob

# ----------------------------🗽🗽🗽 CONSTANTS 🗽🗽🗽------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"


# ---------------------------- 🖼️🖼️🖼️ AnalyzerGUI 🖼️🖼️🖼️------------------------------- #
class AnalyzerGUI:
    def __init__(self, calculator):  # Dodajemy parametr calculator
        self.folder_label = None
        self.latarnie_img = None
        self.canvas = None
        self.window = Tk()  # TWORZENIE GŁÓWNEGO OKNA
        self.calculator = calculator  # Zapisujemy go w klasie
        self.window.title("ReluxLightAnalyzer")  # TYTUŁ GŁÓWNEGO OKNA. TYLKO JEDNO W PROJEKCIE!!!
        self.window.config(padx=40, pady=30, bg=YELLOW)
        self.csv_files = []  # Lista plików CSV z wybranego folderu
        self.folder_path = ""  # Ścieżka do wybranego folderu
        self.setup_main_window()

    def setup_main_window(self):
        self.canvas = Canvas(self.window, width=640, height=512, bg=YELLOW, highlightthickness=0)  # CANVAS TWORZY CZYSTE PŁÓTNO

        self.latarnie_img = PhotoImage(file="./images/latarnie.png")  # wczytanie obrazka
        self.canvas.create_image(320, 256, image=self.latarnie_img)  # POZYCJA X, Y TO POŁOWA WIELKOŚCI OBRAZKA Z GÓRY
        self.canvas.grid(row=1, column=1)  # pozycja obrazka w oknie

        timer = Label(self.window, text="Analizer wyników oświetleniowych (RELUX)", bg=YELLOW, fg=GREEN,
                      font=(FONT_NAME, 20, "bold"))  # tytuł napisu nad obrazkiem
        timer.grid(row=0, column=1)  # pozycja napisu nad obrazkiem

        start = Button(self.window, width=7, height=2, text="Start",
                       command=self.start_results_window)  # przycisk start, inicjacja
        start.grid(row=2, column=0)  # pozycja przycisku start w oknie

        reset = Button(self.window, width=7, height=2,
                       text="Reset")  # tu w nawiasie wstawisz command= i nazwa funkcji która coś robi )
        reset.grid(row=2, column=2)  # pozycja przycisku reset w oknie

        select_folder_button = Button(self.window, text="Wybierz folder z plikami .csv", command=self.select_csv_folder,
                                      bg=GREEN, font=(FONT_NAME, 12))
        select_folder_button.grid(row=3, column=1, pady=10)

        self.folder_label = Label(self.window, text="", bg=YELLOW, fg=PINK, font=(FONT_NAME, 10), justify=LEFT,
                                  anchor="w")  # poprawienie wyglądu labela
        self.folder_label.grid(row=4, column=1, pady=5)

    # ---------------------------- 📂📂📂 FOLDER SELECTION 📂📂📂------------------------------- #
    def select_csv_folder(self):
        # 1. Otwarcie okna dialogowego wyboru folderu
        folder_path = filedialog.askdirectory(
            title="Wybierz folder z plikami .csv"
        )

        # 2. Sprawdzenie, czy użytkownik nie zamknął okna bez wyboru
        if folder_path:
            self.folder_path = folder_path
            print(f"Wczytano wybrany folder: {folder_path}")

            # 3. Znalezienie wszystkich plików CSV przy użyciu glob i os
            # os.path.join dba o to, żeby ścieżka była poprawna na Windows/Mac/Linux
            search_pattern = os.path.join(folder_path, "*.csv")
            self.csv_files = glob.glob(search_pattern)

            # 4. KLUCZOWY MOMENT: Przekazujemy listę plików do obiektu kalkulatora
            # Dzięki temu kalkulator "już wie" na czym ma pracować
            if hasattr(self, 'calculator'):
                self.calculator.set_csv_files(self.csv_files)

            # 5. Aktualizacja interfejsu (Label)
            if self.csv_files:
                print(f"Znaleziono {len(self.csv_files)} plików CSV.")

                # Tworzymy ładną listę samych nazw plików (bez pełnych ścieżek) do wyświetlenia
                file_names = [os.path.basename(f) for f in self.csv_files]
                file_list_text = "\n".join(file_names)

                self.folder_label.config(
                    text=f"Wybrany folder: {folder_path}\n\nZnalezione pliki:\n{file_list_text}",
                    fg=GREEN  # Zmieniamy kolor na zielony, jeśli pliki są obecne
                )
            else:
                print("Brak plików CSV w tym folderze.")
                self.folder_label.config(
                    text=f"Folder: {folder_path}\n(Brak plików .csv!)",
                    fg=RED  # Zmieniamy kolor na czerwony, żeby ostrzec użytkownika
                )

    # ---------------------------- 📊📊📊 RESULTS WINDOW SETUP 📊📊📊------------------------------- #
    def start_results_window(self):
        results_window = Toplevel(self.window)
        results_window.title("Opracowane dane oświetleniowe")
        results_window.config(padx=40, pady=30, bg=YELLOW)

        # Siatka 10 przycisków: 2 kolumny x 5 rzędów - każdy zdefiniowany osobno
        button_1 = Button(results_window, width=15, height=3, text="Przycisk 1", command=self.function_1, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_1.grid(row=0, column=0, padx=10, pady=10)

        button_2 = Button(results_window, width=15, height=3, text="Przycisk 2", command=self.function_2, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_2.grid(row=0, column=1, padx=10, pady=10)

        button_3 = Button(results_window, width=15, height=3, text="Przycisk 3", command=self.function_3, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_3.grid(row=1, column=0, padx=10, pady=10)

        button_4 = Button(results_window, width=15, height=3, text="Przycisk 4", command=self.function_4, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_4.grid(row=1, column=1, padx=10, pady=10)

        button_5 = Button(results_window, width=15, height=3, text="Przycisk 5", command=self.function_5, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_5.grid(row=2, column=0, padx=10, pady=10)

        button_6 = Button(results_window, width=15, height=3, text="Przycisk 6", command=self.function_6, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_6.grid(row=2, column=1, padx=10, pady=10)

        button_7 = Button(results_window, width=15, height=3, text="Przycisk 7", command=self.function_7, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_7.grid(row=3, column=0, padx=10, pady=10)

        button_8 = Button(results_window, width=15, height=3, text="Przycisk 8", command=self.function_8, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_8.grid(row=3, column=1, padx=10, pady=10)

        button_9 = Button(results_window, width=15, height=3, text="Przycisk 9", command=self.function_9, bg=GREEN,
                          font=(FONT_NAME, 12))
        button_9.grid(row=4, column=0, padx=10, pady=10)

        button_10 = Button(results_window, width=15, height=3, text="Przycisk 10", command=self.function_10, bg=GREEN,
                           font=(FONT_NAME, 12))
        button_10.grid(row=4, column=1, padx=10, pady=10)

    # ---------------------------- ⏯️⏯️⏯️ BUTTON FUNCTIONS ⏯️⏯️⏯️------------------------------- #
    def function_1(self):
        print("Function 1 został kliknięty")
        # Tutaj dodaj kod dla function_1 - odnośnik do analysis.py

    def function_2(self):
        print("Function 2 został kliknięty")
        # Tutaj dodaj kod dla function_2 - odnośnik do analysis.py

    def function_3(self):
        print("Function 3 został kliknięty")
        # Tutaj dodaj kod dla function_3 - odnośnik do analysis.py

    def function_4(self):
        print("Function 4 został kliknięty")
        # Tutaj dodaj kod dla function_4 - odnośnik do analysis.py

    def function_5(self):
        print("Function 5 został kliknięty")
        # Tutaj dodaj kod dla function_5 - odnośnik do analysis.py

    def function_6(self):
        print("Function 6 został kliknięty")
        # Tutaj dodaj kod dla function_6 - odnośnik do analysis.py

    def function_7(self):
        print("Function 7 został kliknięty")
        # Tutaj dodaj kod dla function_7 - odnośnik do analysis.py

    def function_8(self):
        print("Function 8 został kliknięty")
        # Tutaj dodaj kod dla function_8 - odnośnik do analysis.py

    def function_9(self):
        print("Function 9 został kliknięty")
        # Tutaj dodaj kod dla function_9 - odnośnik do analysis.py

    def function_10(self):
        print("Function 10 został kliknięty")
        # Tutaj dodaj kod dla function_10 - odnośnik do analysis.py

    def run(self):
        """Uruchamia główną pętlę aplikacji"""
        self.window.mainloop()

