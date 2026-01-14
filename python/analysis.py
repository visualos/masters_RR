# Mam 10 funkcji do zapełnienia wynikami z pliku csv
# Funkcje mają być zdefiniowane w pliku analysis.py
# Funkcje mają być wywoływane z pliku main.py
# Funkcje mają być wywoływane z main.py
# Funkcje mają być wywoływane z main.py
import pandas as pd
import os



# Słownik wymagań na podstawie Twojej tabeli
NORMS = {
    'M1': {'Lav': 2.0,  'Uo': 0.4,  'Ul': 0.7,  'TI': 10, 'Rei': 0.35},
    'M2': {'Lav': 1.5,  'Uo': 0.4,  'Ul': 0.7,  'TI': 10, 'Rei': 0.35},
    'M3': {'Lav': 1.0,  'Uo': 0.4,  'Ul': 0.6,  'TI': 15, 'Rei': 0.30},
    'M4': {'Lav': 0.75, 'Uo': 0.4,  'Ul': 0.6,  'TI': 15, 'Rei': 0.30},
    'M5': {'Lav': 0.5,  'Uo': 0.35, 'Ul': 0.4,  'TI': 15, 'Rei': 0.30},
    'M6': {'Lav': 0.3,  'Uo': 0.35, 'Ul': 0.4,  'TI': 20, 'Rei': 0.30},
}


# ---------------------------- 📂📂📂 FOLDER SELECTION 📂📂📂------------------------------- #
class AnalysisCalculator:
    def __init__(self):
        self.csv_files = []

    def set_csv_files(self, csv_files):
        """Otrzymuje listę ścieżek do plików z GUI"""
        self.csv_files = csv_files

    def calculate_results(self):
        # Lista kolumn, które Cię interesują (skopiowane dokładnie z Twojego logu)
        chosen_columns = [
            'Ldc name', 'Lamp info', 'Total flux [lm]', 'Total power [W]',
            'Power/km  [W/km]', 'Road W[m]', 'Lum pos y [m]', 'Lph [m]',
            'Delta [m]', 'Tilt [°]', 'Lav [cd/m2]', 'Uo (L)', 'Ul', 'TI [%]', 'Rei'
        ]

        if not self.csv_files:
            print("Błąd: Najpierw wybierz folder!")
            return

        for csv_file in self.csv_files:
            try:
                print(f"\n--- ANALIZA PLIKU: {os.path.basename(csv_file)} ---")

                # Czytamy plik używając wybranych kolumn
                # Przy 7GB dodajemy chunksize, żeby nie zapchać RAMu
                chunks = pd.read_csv(
                    csv_file,
                    sep=None,
                    engine='python',
                    encoding='cp1250',
                    usecols=chosen_columns,
                    chunksize=50000  # czyta po 50 tyś wierszy na raz
                )

                for chunk in chunks:
                    # Tutaj będziemy wykonywać operacje dla Twoich 10 przycisków
                    # Na razie tylko sprawdzamy, czy widzi dane
                    print(f"Przetworzono partię: {len(chunk)} wierszy.")
                    # Przykład: wypisujemy 3 pierwsze nazwy opraw z tej partii
                    print(chunk['Ldc name'].head(3).tolist())

                    # Tu w przyszłości wstawisz wywołania swoich 10 funkcji:
                    # self.analiza_mocy(chunk)
                    # self.analiza_olsnienia(chunk)

            except Exception as e:
                print(f"Błąd podczas głębokiej analizy: {e}")

    def check_norms(self, row):
        """Sprawdza jaką najwyższą klasę spełnia dany wiersz"""
        achieved_classes = []
        for name, req in NORMS.items():
            # Sprawdzamy wszystkie warunki (Lav, Uo, Ul, TI, Rei)
            if (row['Lav [cd/m2]'] >= req['Lav'] and
                    row['Uo (L)'] >= req['Uo'] and
                    row['Ul'] >= req['Ul'] and
                    row['TI [%]'] <= req['TI'] and
                    row['Rei'] >= req['Rei']):
                achieved_classes.append(name)

        # Zwracamy np. 'M3' (najwyższa spełniona) lub None
        return achieved_classes[0] if achieved_classes else None

    def process_and_merge(self):
        # Słownik, gdzie kluczem będzie (Ldc name, Lamp info)
        # Wartością będą wyniki dla różnych układów (jednostronny itp.)
        self.master_db = {}

        for csv_file in self.csv_files:
            # Określamy typ układu na podstawie nazwy pliku
            layout_type = self.identify_layout(csv_file)

            chunks = pd.read_csv(csv_file, usecols=chosen_columns, chunksize=100000, encoding='cp1250')

            for chunk in chunks:
                # 1. Filtrujemy tylko te, które spełniają COKOLWIEK (przyspieszenie)
                # Tu można zastosować wektoryzację w Pandas dla szybkości
                for idx, row in chunk.iterrows():
                    best_class = self.check_norms(row)
                    if best_class:
                        key = (row['Ldc name'], row['Lamp info'])
                        # Tworzymy strukturę: oprawa -> layout -> najlepsze wyniki
                        if key not in self.master_db:
                            self.master_db[key] = {}

                        # Zapisujemy tylko "najlepszy" wynik (np. największy Delta - rozstaw)
                        # dla danej oprawy w tym layoucie, który spełnia normę
                        self.update_best_result(key, layout_type, row, best_class)