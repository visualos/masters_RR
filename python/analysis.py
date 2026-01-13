# Mam 10 funkcji do zapełnienia wynikami z pliku csv
# Funkcje mają być zdefiniowane w pliku analysis.py
# Funkcje mają być wywoływane z pliku main.py
# Funkcje mają być wywoływane z main.py
# Funkcje mają być wywoływane z main.py


# ---------------------------- 📂📂📂 FOLDER SELECTION 📂📂📂------------------------------- #
class AnalysisCalculator:
    def __init__(self):
        self.csv_files = []

    def set_csv_files(self, csv_files):
        self.csv_files = csv_files

    def calculate_results(self):
        for csv_file in self.csv_files:
            print(f"Analizuję plik: {csv_file}")

