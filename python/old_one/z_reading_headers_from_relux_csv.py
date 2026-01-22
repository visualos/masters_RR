import pandas as pd
import os

base_path = os.path.dirname(__file__)
# file_path = os.path.join(base_path, '..', 'relux', 'relux_calc', 'Projekt_7_all_ldt_2_pasy.Road 1.street.batch.csv')
file_path = os.path.join(base_path, '..', 'relux', 'relux_calc', 'wycinek_100k_rows_MastersCalc.csv')


def load_full_optimized_data(path):
    try:
        # 1. Wczytujemy wszystko (low_memory=False dla stabilności)
        df = pd.read_csv(path, sep=';', encoding='cp1250', decimal=',', low_memory=False)

        # Czyszczenie nazw
        df.columns = df.columns.str.strip()

        # 2. Optymalizacja kolumn liczbowych (Lav, Uo, Ul, TI, Rei, Tilt, Road W itd.)
        # Wybieramy kolumny, które są wynikami/parametrami
        numeric_cols = [
            'Road W[m]', 'Lum pos y [m]', 'Lph [m]', 'Delta [m]', 'Tilt [°]',
            'Lav [cd/m2]', 'Lmin [cd/m2]', 'Lmax [cd/m2]', 'Uo (L)', 'Uow (L)',
            'Ul', 'TI [%]', 'Rei', 'Em [lx]', 'Emin [lx]', 'Uo (E)', 'Total power [W]'
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')

        # 3. Optymalizacja kolumn tekstowych (Category)
        # Te kolumny mają dużo powtórzeń - typ category drastycznie zmniejsza RAM
        cat_cols = ['Ldc name', 'Ldc type', 'Lamp info', 'Street', 'class', 'valid']
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')

        return df

    except Exception as e:
        print(f"Błąd: {e}")
        return None


if __name__ == "__main__":
    df_results = load_full_optimized_data(file_path)

    if df_results is not None:
        print(f"--- Pełne dane wczytane i zoptymalizowane ---")
        print(f"Liczba wierszy: {len(df_results)}")
        print(f"Liczba kolumn: {len(df_results.columns)}")

        mem_usage = df_results.memory_usage(deep=True).sum() / (1024 ** 2)
        print(f"Zużycie pamięci po optymalizacji: {mem_usage:.2f} MB")

        # Podgląd, czy wszystko jest na miejscu
        print("\nPierwsze 3 wiersze (pełna szerokość):")
        pd.set_option('display.max_columns', None)  # Żeby wyświetlić wszystkie kolumny w konsoli
        print(df_results.head(3))
        print(df_results.columns)