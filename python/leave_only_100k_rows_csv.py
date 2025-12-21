import pandas as pd
import os

# --- KONFIGURACJA ŚCIEŻEK ---
base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, '..', 'relux', 'relux_calc', 'Projekt_7_all_ldt_2_pasy.Road 1.street.batch.csv')
output_file = os.path.join(base_path, 'wycinek_100k_rows.csv')


def extract_random_sample(path_in, path_out, n_samples=100000):
    try:
        print(f"1. Wczytywanie pliku (17 mln wierszy)... Proszę czekać.")
        # Wczytujemy bez konwersji typów, żeby było jak najszybciej
        df = pd.read_csv(
            path_in,
            sep=';',
            encoding='cp1250',
            decimal=',',
            low_memory=False
        )

        print(f"2. Losowanie {n_samples} wierszy...")
        # Losowanie wierszy
        df_sample = df.sample(n=n_samples, random_state=42)

        print(f"3. Zapisywanie do nowego pliku: {path_out}")
        # Zapis do nowego pliku CSV (zachowujemy separator i kodowanie)
        df_sample.to_csv(
            path_out,
            sep=';',
            encoding='cp1250',
            decimal=',',
            index=False
        )

        print("\nSukces!")
        print(f"Plik wynikowy znajduje się w: {path_out}")
        print(f"Rozmiar próbki: {len(df_sample)} wierszy.")

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku wejściowego pod ścieżką: {path_in}")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    extract_random_sample(input_file, output_file)