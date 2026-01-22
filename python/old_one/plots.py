import matplotlib.pyplot as plt
import gc  # Garbage collector dla lepszego zarządzania pamięcią

_logger = None


def set_logger(logger_func):
    """Ustawia funkcję logowania: logger_func(message, level)."""
    global _logger
    _logger = logger_func


def optimize_dataframe(df, sample_size=None):
    """Optymalizuje DataFrame dla dużych zbiorów danych."""
    if df is None or df.empty:
        return df

    df_size = len(df)

    # Próbkowanie dla dużych zbiorów
    if sample_size and df_size > sample_size:
        _log(f"Optymalizacja: próbkowanie {df_size} -> {sample_size} wierszy", "info")
        return df.sample(n=sample_size, random_state=42).copy()

    return df.copy()


def cleanup_memory():
    """Czyści pamięć po dużych operacjach."""
    gc.collect()
    _log("Oczyszczono pamięć", "info")


def show_progress(message, progress_callback=None):
    """Pokazuje postęp operacji."""
    _log(message, "info")
    if progress_callback:
        progress_callback(message)


def _log(message, level="info"):
    if _logger:
        _logger(message, level)
    else:
        print(message)
import seaborn as sns
import pandas as pd


def draw_arrangement_comparison(df, mode='efficiency'):
    """Obsługuje wykresy 1, 2 i 3 z optymalizacją dla dużych zbiorów"""
    if df is None or df.empty:
        _log("Brak danych do wyświetlenia dla wybranych filtrów!", "warning")
        return

    # Optymalizacja dla dużych zbiorów danych
    df_size = len(df)
    if df_size > 100000:
        _log(f"Duży zbiór danych ({df_size} wierszy). Używam próbkowania dla porównania układów.", "info")
        df_work = df.sample(n=50000, random_state=42).copy()
    else:
        df_work = df

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))

    try:
        # Mapowanie trybów na dane
        if mode == 'efficiency':
            # Liczymy % wariantów spełniających normę (Lav >= 100) dla każdego układu i szerokości
            lav_cols = df_work.filter(like='Lav').columns
            if len(lav_cols) > 0:
                df_work['is_valid'] = (df_work[lav_cols].max(axis=1) >= 100).astype(int)
                plot_data = df_work.groupby(['Arrangement', 'Road W[m]'])['is_valid'].mean() * 100
                ylabel, title = "% spełnionych wariantów", "Skuteczność układów oświetleniowych"
            else:
                _log("Brak kolumn Lav w danych", "error")
                return
        elif mode == 'De':
            plot_data = df_work.groupby(['Arrangement', 'Road W[m]'])['De'].mean()
            ylabel, title = "Średnie De [kWh/(m2*rok)]", "Wskaźnik energii De vs Szerokość drogi"
        elif mode == 'Dp':
            plot_data = df_work.groupby(['Arrangement', 'Road W[m]'])['Dp'].mean()
            ylabel, title = "Średnie Dp [W/(lx*m2)]", "Wskaźnik gęstości mocy Dp vs Szerokość drogi"
        else:
            _log(f"Nieznany tryb: {mode}", "error")
            return

        plot_data.unstack(level=0).plot(kind='line', marker='o', ax=ax)

        ax.set_title(f"{title} (n={len(df_work)})", color='#00ff88', pad=20)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Szerokość drogi [m]")
        ax.grid(True, alpha=0.2)
        plt.legend(title="Układ")
        plt.show()

    except Exception as e:
        _log(f"Błąd podczas tworzenia wykresu porównania: {e}", "error")
        return
    finally:
        # Zwolnij pamięć
        if df_size > 100000:
            del df_work
            cleanup_memory()


def draw_arrangement_comparison_agg(df, mode='efficiency'):
    """Rysuje wykresy 1-3 z danych zagregowanych."""
    if df is None or df.empty:
        _log("Brak danych do wyświetlenia dla wybranych filtrów!", "warning")
        return

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))

    if mode == 'efficiency':
        ylabel, title = "% spełnionych wariantów", "Skuteczność układów oświetleniowych"
    elif mode == 'De':
        ylabel, title = "Średnie De [kWh/(m2*rok)]", "Wskaźnik energii De vs Szerokość drogi"
    elif mode == 'Dp':
        ylabel, title = "Średnie Dp [W/(lx*m2)]", "Wskaźnik gęstości mocy Dp vs Szerokość drogi"
    else:
        ylabel, title = "Wartość", "Porównanie układów"

    plot_data = df.pivot_table(index='Road W[m]', columns='Arrangement', values='value', aggfunc='mean')
    plot_data.plot(kind='line', marker='o', ax=ax)

    ax.set_title(title, color='#00ff88', pad=20)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Szerokość drogi [m]")
    ax.grid(True, alpha=0.2)
    plt.legend(title="Układ")
    plt.show()


def draw_top20_fixtures(df, arrangement):
    """Wykresy 4, 5, 6: Top 20 opraw pod kątem De z optymalizacją dla dużych zbiorów"""
    import matplotlib.pyplot as plt

    if df is None or df.empty:
        _log("Brak danych do wyświetlenia!", "warning")
        return

    # Optymalizacja dla dużych zbiorów danych
    df_size = len(df)
    if df_size > 100000:
        _log(f"Duży zbiór danych ({df_size} wierszy). Używam próbkowania dla wydajności.", "info")
        # Dla bardzo dużych zbiorów użyj próbkowania
        df_sample = df.sample(n=50000, random_state=42)
    elif df_size > 50000:
        # Dla średnich zbiorów użyj próbkowania
        df_sample = df.sample(n=25000, random_state=42)
    else:
        df_sample = df

    # --- DEBUGER ---
    # To wypisze w konsoli wszystkie unikalne nazwy układów jakie masz w bazie
    faktyczne_uklady = df_sample['Arrangement'].unique()
    _log(f"DEBUG: Szukam: '{arrangement}' | W bazie są: {faktyczne_uklady}", "info")
    # ---------------

    # Agresywne czyszczenie: usuwamy spacje z danych w bazie
    df_sample['Arrangement'] = df_sample['Arrangement'].astype(str).str.strip()

    # Filtrowanie z optymalizacją
    try:
        # Sprawdź czy kolumny Lav istnieją
        lav_cols = df_sample.filter(like='Lav').columns
        if len(lav_cols) == 0:
            _log("Brak kolumn Lav w danych!", "error")
            return

        # Użyj wektoryzowanych operacji zamiast iteracji
        max_lav = df_sample[lav_cols].max(axis=1)
        valid_df = df_sample[(max_lav >= 100) & (df_sample['Arrangement'] == arrangement)]

    except Exception as e:
        _log(f"Błąd podczas filtrowania danych: {e}", "error")
        return

    if valid_df.empty:
        _log(f"Filtr zwrócił 0 wierszy dla układu: {arrangement}", "warning")
        return

    # Grupowanie i ranking z optymalizacją pamięci
    try:
        top20 = valid_df.groupby('Ldc name')['De'].min().sort_values().head(20)
    except Exception as e:
        _log(f"Błąd podczas grupowania danych: {e}", "error")
        return

    # Ostateczny test przed rysowaniem
    if top20.empty:
        _log("Brak danych spełniających normę Lav >= 100 dla tego układu.", "warning")
        return

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 8))
    top20.plot(kind='barh', color='#569cd6', ax=ax)

    ax.set_title(f"TOP 20 OPRAW: {arrangement} (Najniższe De)", color='#00ff88')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()

    # Zwolnij pamięć
    del df_sample, valid_df, top20
    cleanup_memory()





def draw_flux_balance(df, class_name):
    """Wykres 7: Bilans strumienia z pogrupowaną osią X (Biny) z optymalizacją"""
    if df is None or df.empty: return

    if class_name == "Wszystkie":
        from tkinter import messagebox
        messagebox.showinfo("Informacja", "Wybierz konkretną klasę w menu, aby zobaczyć bilans.")
        return

    col_lav = f"Lav({class_name})"
    if col_lav not in df.columns: return

    # Optymalizacja dla dużych zbiorów danych
    df_size = len(df)
    if df_size > 100000:
        _log(f"Duży zbiór danych ({df_size} wierszy). Używam próbkowania dla wydajności.", "info")
        df = df.sample(n=50000, random_state=42).copy()
    elif df_size > 50000:
        df = df.sample(n=25000, random_state=42).copy()

    df['Status'] = df[col_lav] >= 100
    df['Status_Label'] = df['Status'].map({True: 'Spełnia', False: 'Nie spełnia'})

    # --- AGREGACJA (BINOWANIE) z optymalizacją ---
    # Dostosuj step w zależności od rozmiaru danych
    if df_size > 50000:
        step = 5000  # Większe bins dla dużych zbiorów
    else:
        step = 2000

    try:
        max_flux = df['Total flux [lm]'].max()
        if pd.isna(max_flux):
            _log("Brak prawidłowych danych strumienia", "warning")
            return

        bins = range(0, int(max_flux) + step, step)
        df['Flux_Range'] = pd.cut(df['Total flux [lm]'], bins=bins, precision=0)

        # Przygotowanie danych do wykresu słupkowego skumulowanego
        plot_data = df.groupby(['Flux_Range', 'Status_Label']).size().unstack(fill_value=0)

    except Exception as e:
        _log(f"Błąd podczas przetwarzania danych: {e}", "error")
        return

    # --- RYSOWANIE ---
    plt.style.use('dark_background')
    ax = plot_data.plot(kind='bar', stacked=True, figsize=(12, 6),
                        color={'Spełnia': '#44aaff', 'Nie spełnia': '#ff4444'})

    plt.title(f"Bilans strumienia dla klasy {class_name} (Dane pogrupowane co {step} lm)",
              color='white', pad=20, fontsize=12)
    plt.xlabel("Przedział strumienia świetlnego [lm]", fontsize=10)
    plt.ylabel("Liczba wariantów projektowych", fontsize=10)

    # Poprawa czytelności etykiet osi X
    plt.xticks(rotation=45, ha='right')
    plt.legend(title="Wynik analizy")
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    plt.subplots_adjust(bottom=0.2)
    plt.show()

    # Zwolnij pamięć
    del df, plot_data
    cleanup_memory()


import seaborn as sns
import matplotlib.pyplot as plt


def draw_dp_boxplot(df, class_name):
    """Wykres 8: Rozkład Dp (Świeczkowy) z optymalizacją dla dużych zbiorów"""
    if df is None or df.empty:
        return

    # 1. Zabezpieczenie przed 'Wszystkie' - sprawdzamy czy class_name to tekst i czy nie jest 'Wszystkie'
    if not isinstance(class_name, str) or class_name == "Wszystkie" or class_name.strip() == "":
        from tkinter import messagebox
        messagebox.showwarning("Wybierz klasę",
                               "Wykres rozkładu wymaga wybrania konkretnej klasy oświetleniowej (np. M3).")
        return

    col_lav = f"Lav({class_name})"

    if col_lav not in df.columns:
        _log(f"Brak kolumny {col_lav} w bazie.", "error")
        return

    # Optymalizacja dla dużych zbiorów danych
    df_size = len(df)
    if df_size > 50000:
        _log(f"Duży zbiór danych ({df_size} wierszy). Używam próbkowania dla boxplot.", "info")
        df_plot = df.sample(n=25000, random_state=42).copy()
    else:
        df_plot = df.copy()

    # Definiujemy etykiety (muszą być identyczne jak w palecie poniżej!)
    label_tak = "TAK (spełnia)"
    label_nie = "NIE (brak normy)"

    try:
        df_plot['Norma'] = df_plot[col_lav].apply(lambda x: label_tak if x >= 100 else label_nie)
    except Exception as e:
        _log(f"Błąd podczas przetwarzania danych: {e}", "error")
        return

    plt.style.use('dark_background')
    plt.figure(figsize=(10, 7))

    # 2. Rysowanie z poprawioną paletą i parametrami
    sns.boxplot(
        x='Norma',
        y='Dp',
        hue='Norma',
        data=df_plot,
        palette={label_tak: '#00ff88', label_nie: '#ff4444'},
        legend=False
    )

    # Dodaj informacje o liczbie próbek
    n_tak = (df_plot['Norma'] == label_tak).sum()
    n_nie = (df_plot['Norma'] == label_nie).sum()
    plt.title(f"Rozkład wskaźnika gęstości mocy Dp\nKlasa: {class_name} (n={n_tak+n_nie})",
              color='#00ff88', pad=20, fontsize=13, fontweight='bold')

    plt.xlabel("Czy spełnia wymagania luminancji?", fontsize=10)
    plt.ylabel("Dp [W / (lx * m2)]", fontsize=10)

    plt.grid(axis='y', linestyle='--', alpha=0.2)
    plt.tight_layout()
    plt.show()

    # Zwolnij pamięć
    del df_plot
    cleanup_memory()


def draw_de_histogram(df):
    """Wykres 9: Rozkład energii De z optymalizacją dla dużych zbiorów"""
    if df is None or df.empty:
        _log("Brak danych do wyświetlenia dla wybranych filtrów!", "warning")
        return

    # Optymalizacja dla dużych zbiorów danych
    df_size = len(df)
    if df_size > 100000:
        _log(f"Duży zbiór danych ({df_size} wierszy). Używam próbkowania dla histogramu.", "info")
        df_plot = df.sample(n=50000, random_state=42)
    elif df_size > 50000:
        df_plot = df.sample(n=25000, random_state=42)
    else:
        df_plot = df

    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))

    try:
        # Histogram z automatycznym dostosowaniem liczby bins
        if df_size > 50000:
            bins = 50  # Więcej bins dla dużych zbiorów z próbkowania
        else:
            bins = 30

        sns.histplot(df_plot['De'], bins=bins, color='#569cd6', kde=False)

        # Linia średniej
        avg_de = df_plot['De'].mean()
        plt.axvline(avg_de, color='red', linestyle='--',
                   label=f'Średnia: {avg_de:.3f} (n={len(df_plot)})')

        # Dodaj medianę
        median_de = df_plot['De'].median()
        plt.axvline(median_de, color='orange', linestyle=':',
                   label=f'Mediana: {median_de:.3f}')

    except Exception as e:
        _log(f"Błąd podczas tworzenia histogramu: {e}", "error")
        return

    plt.title("Rozkład wskaźnika rocznego zużycia energii De")
    plt.xlabel("De [kWh/(m2*rok)]")
    plt.ylabel("Liczba projektów")
    plt.legend()
    plt.show()

    # Zwolnij pamięć
    if df_size > 50000:
        del df_plot
        cleanup_memory()