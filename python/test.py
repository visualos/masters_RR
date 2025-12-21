import pandas as pd
import os

# Ścieżka do pliku wejściowego
base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, '..', 'relux', 'relux_calc', 'sprawdzam_obrot_ies_philips.Road 1.street.batch.csv')


def filter_and_save_all_columns(path):
    try:
        # 1. Wczytanie danych z zachowaniem oryginalnej struktury
        df = pd.read_csv(path, sep=';', encoding='cp1250', decimal=',')

        # Czyszczenie nazw kolumn (usuwa ukryte spacje, które Relux dodaje do nagłówków)
        df.columns = df.columns.str.strip()

        # 2. Parametry filtrowania
        target_luminaire = "BGP290 T25 LED50-1F/740 PSD DM10 FG"
        target_width = 10.0

        # 3. Filtrowanie wierszy (zachowujemy wszystkie kolumny)
        filtered_df = df[
            (df['Ldc name'].str.contains(target_luminaire, na=False)) &
            (df['Road W[m]'] == target_width)
            ]

        if filtered_df.empty:
            print(f"Nie znaleziono danych dla oprawy '{target_luminaire}' przy szerokości {target_width}m.")
        else:
            # 4. Zapis do pliku test.csv - wszystkie kolumny
            output_file = os.path.join(base_path, 'test.csv')

            # Zapisujemy cały obiekt filtered_df (wszystkie 30+ kolumn)
            filtered_df.to_csv(output_file, sep=';', encoding='cp1250', decimal=',', index=False)

            print(f"--- Sukces! ---")
            print(f"Znaleziono wierszy: {len(filtered_df)}")
            print(f"Liczba kolumn w pliku wyjściowym: {len(filtered_df.columns)}")
            print(f"Plik został zapisany tutaj: {output_file}")

            # Opcjonalnie: podgląd pierwszych kilku kolumn w konsoli
            print("\nPodgląd danych (pierwsze 5 kolumn):")
            print(filtered_df.iloc[:, :5].to_string(index=False))

    except Exception as e:
        print(f"Wystąpił błąd podczas przetwarzania: {e}")


if __name__ == "__main__":
    filter_and_save_all_columns(file_path)