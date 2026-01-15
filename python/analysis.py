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
        self.cache_dir = "data_cache"

        # DEFINICJA TWOICH KOLUMN (atrybut klasy dostępny wszędzie)
        self.chosen_columns = [
            'Ldc name', 'Lamp info', 'Total flux [lm]', 'Total power [W]',
            'Power/km  [W/km]', 'Road W[m]', 'Lum pos y [m]', 'Lph [m]',
            'Delta [m]', 'Tilt [°]', 'Lav [cd/m2]', 'Uo (L)', 'Ul', 'TI [%]', 'Rei'
        ]

        # Tworzenie folderu na pliki binarne, jeśli nie istnieje
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def set_csv_files(self, csv_files):
        """Otrzymuje listę ścieżek do plików z GUI"""
        self.csv_files = csv_files

    @staticmethod
    def label_norms_vectorized(df):
        """Szybkie sprawdzanie norm dla całego chunka (miliony wierszy w sekundę)"""
        df['best_class'] = "Brak"
        # Sprawdzamy od M6 do M1, aby najwyższa spełniona klasa była ostateczną
        for class_name in ['M6', 'M5', 'M4', 'M3', 'M2', 'M1']:
            n = NORMS[class_name]
            mask = (
                    (df['Lav [cd/m2]'] >= n['Lav']) &
                    (df['Uo (L)'] >= n['Uo']) &
                    (df['Ul'] >= n['Ul']) &
                    (df['TI [%]'] <= n['TI']) &
                    (df['Rei'] >= n['Rei'])
            )
            df.loc[mask, 'best_class'] = class_name

        # SZYBKI TEST:
        print("\n--- PODGLĄD PO ETYKIETOWANIU ---")
        print(df[['Ldc name', 'best_class']].head())
        print("Rozkład klas w tej partii:")
        print(df['best_class'].value_counts())
        return df

    def convert_all_to_parquet(self):
        """Główna pętla mieląca 30GB CSV -> Parquet"""
        if not self.csv_files:
            print("Błąd: Nie wybrano żadnych plików!")
            return

        for csv_file in self.csv_files:
            base_name = os.path.basename(csv_file).replace(".csv", "")
            # Tworzymy podfolder dla każdego pliku, bo Parquet najlepiej trzymać w częściach
            file_cache_path = os.path.join(self.cache_dir, base_name)

            if os.path.exists(file_cache_path):
                print(f"Pominięto: {base_name} (folder cache już istnieje)")
                continue

            os.makedirs(file_cache_path)
            print(f"\n--- START KONWERSJI: {base_name}.csv ---")

            try:
                # Czytanie w kawałkach po 100 000 wierszy
                chunks = pd.read_csv(
                    csv_file,
                    usecols=self.chosen_columns,
                    chunksize=100000,
                    encoding='cp1250',
                    sep=None,
                    engine='python'
                )

                for i, chunk in enumerate(chunks):
                    # 1. Oznaczamy normy
                    chunk = self.label_norms_vectorized(chunk)

                    # 2. Zapisujemy chunk jako oddzielny plik parquet w folderze
                    chunk_filename = f"part_{i}.parquet"
                    chunk.to_parquet(
                        os.path.join(file_cache_path, chunk_filename),
                        engine='pyarrow',
                        index=False
                    )

                    if i % 10 == 0:
                        print(f"Przetworzono {i * 100000} wierszy...")

                print(f"Zakończono sukcesem: {base_name}")

            except Exception as e:
                print(f"Błąd krytyczny przy pliku {csv_file}: {e}")

    def get_results_for_class(self, target_class="M3"):
        """Pobiera i agreguje dane dla konkretnej klasy oświetleniowej"""
        import glob

        all_dfs = []
        # Szukamy wszystkich podfolderów w cache (dla różnych układów/plików)
        folders = glob.glob(os.path.join(self.cache_dir, "*"))

        for folder in folders:
            if os.path.isdir(folder):
                # Wczytujemy dane (Pandas automatycznie połączy wszystkie part_X.parquet)
                temp_df = pd.read_parquet(folder)

                # Pobieramy nazwę układu z nazwy folderu (np. 'wycinek_100k_rows')
                layout_name = os.path.basename(folder)
                temp_df['Source_Layout'] = layout_name
                all_dfs.append(temp_df)

        if not all_dfs:
            return "Brak danych w cache. Uruchom najpierw konwersję."

        df = pd.concat(all_dfs, ignore_index=True)

        # 1. Filtrujemy wiersze, które spełniają klasę target_class
        # (Wybieramy tę klasę LUB wyższe, np. dla M3 bierzemy też M2 i M1)
        classes = ['M6', 'M5', 'M4', 'M3', 'M2', 'M1']
        valid_classes = classes[classes.index(target_class):]

        filtered = df[df['best_class'].isin(valid_classes)].copy()

        if filtered.empty:
            return f"Żadna oprawa nie spełnia normy {target_class}."

        # 2. RACJONALIZACJA: Dla każdej oprawy szukamy wiersza z najniższym 'Power/km  [W/km]'
        # Grupowanie po oprawie i lampie
        best_results = (
            filtered.sort_values(by='Power/km  [W/km]', ascending=True)
            .drop_duplicates(subset=['Ldc name', 'Lamp info'])
        )

        # Zwracamy Top 10 najbardziej 'racjonalnych' rozwiązań
        return best_results[[
            'Ldc name', 'Lamp info', 'Total power [W]',
            'Power/km  [W/km]', 'Delta [m]', 'best_class', 'Source_Layout'
        ]].head(10)

    def load_full_data(self, file_name_no_ext):
        """Przykład wczytywania danych dla jednego układu (np. do wykresu)"""
        path = os.path.join(self.cache_dir, file_name_no_ext)
        if os.path.exists(path):
            # Pandas wczyta wszystkie pliki part_X.parquet z folderu jako jedną tabelę!
            return pd.read_parquet(path)
        return None

    def calculate_results(self):
        """Metoda uruchamiana przyciskiem Start w GUI"""
        print("Rozpoczynam proces przygotowania danych...")
        self.convert_all_to_parquet()
        print("\nWSZYSTKIE DANE SĄ GOTOWE W FORMACIE BINARNYM.")


