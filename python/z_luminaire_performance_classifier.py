import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import messagebox, ttk

# --- KONFIGURACJA ŚCIEŻEK ---
base_path = os.path.dirname(__file__)
# Ścieżka zakłada, że skrypt jest w folderze obok folderu 'relux'
input_file = os.path.join(base_path, '..', 'relux', '100k_rows_sample', 'wycinek_100k_rows.csv')

class LuminaireApp:
    def __init__(self, root):
        """🏗️ Inicjalizacja aplikacji i bazy norm oświetleniowych"""
        self.root = root
        self.root.title("Analizator Opraw Oświetleniowych v1.5")
        self.root.geometry("450x750")
        self.df = None
        
        # 📏 Tabela wymagań normatywnych M1-M6
        self.std = pd.DataFrame({
            'Klasa': ['M1', 'M2', 'M3', 'M4', 'M5', 'M6'],
            'Lav [cd/m2]': [2.00, 1.50, 1.00, 0.75, 0.50, 0.30],
            'Uo (L)': [0.40, 0.40, 0.40, 0.40, 0.35, 0.35],
            'Ul': [0.70, 0.70, 0.60, 0.60, 0.40, 0.40],
            'TI [%]': [10.0, 10.0, 15.0, 15.0, 15.0, 20.0],
            'Rei': [0.35, 0.35, 0.30, 0.30, 0.30, 0.30]
        })

        # --- ELEMENTY GUI ---
        tk.Label(root, text="Panel Analizy Danych", font=("Arial", 14, "bold")).pack(pady=10)

        self.btn_load = tk.Button(root, text="1. 📂 Wczytaj i Przygotuj Dane", command=self.load_data, 
                                  bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=35)
        self.btn_load.pack(pady=10)

        self.btn_view_table = tk.Button(root, text="📋 Wyświetl Dane jako Tabela", command=self.show_data_table, 
                                       state=tk.DISABLED, width=35, bg="#9b59b6", fg="white")
        self.btn_view_table.pack(pady=5)

        tk.Label(root, text="Wybierz klasę oświetleniową (do filtrów):").pack()
        self.class_var = tk.StringVar(value="M3")
        self.class_combo = ttk.Combobox(root, textvariable=self.class_var, 
                                        values=["M1", "M2", "M3", "M4", "M5", "M6"], state="readonly", width=15)
        self.class_combo.pack(pady=5)

        self.btn_best = tk.Button(root, text="⭐ Wybierz najlepsze 5 opraw", command=self.select_best_luminaires, 
                                  state=tk.DISABLED, width=35, bg="#e67e22", fg="white", font=("Arial", 10, "bold"))
        self.btn_best.pack(pady=5)

        tk.Label(root, text="Wybierz model oprawy:").pack()
        self.brand_var = tk.StringVar(value="Wszystkie")
        
        # Styl dla większego comboboxa (wysokość)
        style = ttk.Style()
        style.configure("Tall.TCombobox", padding=(5, 10))
        
        self.brand_combo = ttk.Combobox(root, textvariable=self.brand_var, state="disabled", width=90, style="Tall.TCombobox")
        self.brand_combo.pack(pady=5)

        # Przyciski wykresów
        self.btn_p1 = tk.Button(root, text="📊 Wykres Skuteczności (Wszystkie Klasy)", command=self.plot_parameters, state=tk.DISABLED, width=35)
        self.btn_p1.pack(pady=2)

        self.btn_p2 = tk.Button(root, text="📈 Bilans Strumienia dla wybranej Klasy", command=self.plot_flux_balance, state=tk.DISABLED, width=35)
        self.btn_p2.pack(pady=2)

        self.btn_p3 = tk.Button(root, text="🔥 Analiza Restrykcyjności Parametrów", command=self.plot_restriction_analysis, 
                                state=tk.DISABLED, width=35, bg="#2c3e50", fg="white")
        self.btn_p3.pack(pady=2)

        # Separator dla sekcji efektywności energetycznej
        tk.Label(root, text="─" * 40, fg="gray").pack(pady=5)
        tk.Label(root, text="Analiza Efektywności Energetycznej", font=("Arial", 11, "bold"), fg="#27ae60").pack(pady=5)

        self.btn_e1 = tk.Button(root, text="⚡ Skuteczność Świetlna (lm/W)", command=self.plot_luminous_efficacy, 
                                state=tk.DISABLED, width=35, bg="#27ae60", fg="white")
        self.btn_e1.pack(pady=2)

        self.btn_e2 = tk.Button(root, text="💡 Moc Jednostkowa (W/m)", command=self.plot_power_per_meter, 
                                state=tk.DISABLED, width=35, bg="#27ae60", fg="white")
        self.btn_e2.pack(pady=2)

        self.btn_e3 = tk.Button(root, text="📊 Analiza Mocy vs Spełnienie Normy", command=self.plot_power_vs_compliance, 
                                state=tk.DISABLED, width=35, bg="#27ae60", fg="white")
        self.btn_e3.pack(pady=2)

        self.btn_e4 = tk.Button(root, text="🏆 Ranking Opraw (Efektywność)", command=self.plot_efficiency_ranking, 
                                state=tk.DISABLED, width=35, bg="#27ae60", fg="white")
        self.btn_e4.pack(pady=2)

        self.btn_e5 = tk.Button(root, text="📉 Wskaźnik mocy Dp", command=self.plot_dp_indicator, 
                                state=tk.DISABLED, width=35, bg="#27ae60", fg="white")
        self.btn_e5.pack(pady=2)

        self.btn_e6 = tk.Button(root, text="📉 Wskaźnik energii De", command=self.plot_de_indicator, 
                                state=tk.DISABLED, width=35, bg="#27ae60", fg="white")
        self.btn_e6.pack(pady=2)

        # Pasek postępu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.BOTTOM, pady=5)
        
        # Etykieta z liczbą konfiguracji
        self.count_label = tk.Label(root, text="Liczba konfiguracji: -", font=("Arial", 9), fg="#7f8c8d")
        self.count_label.pack(side=tk.BOTTOM, pady=2)
        
        self.status_label = tk.Label(root, text="Status: Czekam na dane", fg="#e67e22")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

    def _add_class_parameter_columns(self):
        """Dodaje 30 kolumn: 6 klas × 5 parametrów z pełnymi nazwami (M1 Lav [cd/m2], M1 Uo (L), itd.)
        Wartości to procent spełnienia normy: 100% = idealnie spełniona norma, >100% = przekroczona, <100% = brakuje do normy.
        Dodatkowo tworzy kolumny logiczne 'Spełnia normę <klasa>'."""
        # Mapowanie nazw kolumn z CSV na pełne nazwy do użycia w nowych kolumnach
        col_mapping = {
            'Lav [cd/m2]': 'Lav [cd/m2]',
            'Uo (L)': 'Uo (L)',
            'Ul': 'Ul',
            'Rei': 'Rei',
            'TI [%]': 'TI [%]'
        }
        
        # Dla każdej klasy M1-M6
        for _, row in self.std.iterrows():
            klasa = row['Klasa']
            norma = row
            
            # Lav [cd/m2] (Luminancja) - oblicz % spełnienia normy (wartość / norma * 100)
            col_name_lav = f'{klasa} Lav [cd/m2]'
            if col_mapping['Lav [cd/m2]'] in self.df.columns:
                wartosc = pd.to_numeric(self.df[col_mapping['Lav [cd/m2]']], errors='coerce')
                norma_val = float(norma['Lav [cd/m2]'])
                # 100% = idealnie spełniona norma, >100% = przekroczona, <100% = brakuje
                self.df[col_name_lav] = (wartosc / norma_val * 100).round(2)
            
            # Uo (L) (Równomierność) - oblicz % spełnienia normy
            col_name_uo = f'{klasa} Uo (L)'
            if col_mapping['Uo (L)'] in self.df.columns:
                wartosc = pd.to_numeric(self.df[col_mapping['Uo (L)']], errors='coerce')
                norma_val = float(norma['Uo (L)'])
                self.df[col_name_uo] = (wartosc / norma_val * 100).round(2)
            
            # Ul (Równomierność wzdłużna) - oblicz % spełnienia normy
            col_name_ul = f'{klasa} Ul'
            if col_mapping['Ul'] in self.df.columns:
                wartosc = pd.to_numeric(self.df[col_mapping['Ul']], errors='coerce')
                norma_val = float(norma['Ul'])
                self.df[col_name_ul] = (wartosc / norma_val * 100).round(2)
            
            # Rei (Otoczenie) - oblicz % spełnienia normy
            col_name_rei = f'{klasa} Rei'
            if col_mapping['Rei'] in self.df.columns:
                wartosc = pd.to_numeric(self.df[col_mapping['Rei']], errors='coerce')
                norma_val = float(norma['Rei'])
                self.df[col_name_rei] = (wartosc / norma_val * 100).round(2)
            
            # TI [%] (Olśnienie) - oblicz % spełnienia normy (odwrotna logika, bo mniejsze TI jest lepsze)
            col_name_ti = f'{klasa} TI [%]'
            if col_mapping['TI [%]'] in self.df.columns:
                wartosc = pd.to_numeric(self.df[col_mapping['TI [%]']], errors='coerce')
                norma_val = float(norma['TI [%]'])
                # Dla TI: mniejsze jest lepsze, więc odwracamy: norma / wartość * 100
                # 100% = idealnie spełniona norma, >100% = lepsze (mniejsze TI), <100% = gorsze (większe TI)
                self.df[col_name_ti] = (norma_val / wartosc * 100).round(2)

            # Kolumna logiczna: spełnia wszystkie kryteria normy dla danej klasy (na bazie procentów)
            combined_col = f"Spełnia normę {klasa}"
            self.df[combined_col] = (
                (self.df[col_name_lav] >= 100) &
                (self.df[col_name_uo] >= 100) &
                (self.df[col_name_ul] >= 100) &
                (self.df[col_name_rei] >= 100) &
                (self.df[col_name_ti] >= 100)
            )

    def _add_power_indicators(self):
        """
        Dodaje współczynniki mocy Dp i De do DataFrame na podstawie definicji z PN-EN 13201-2.

        Przybliżenia użyte w implementacji:
        - P: korzystamy z kolumny 'Total power [W]' (moc całkowita układu dla analizowanego odcinka).
        - E: korzystamy z 'Em [lx]' jako średniego natężenia oświetlenia.
        - A: przyjmujemy A = Road W[m] * Delta [m] (szerokość jezdni × rozstaw słupów),
             czyli analizujemy pojedynczy powtarzalny moduł instalacji.
        - De liczymy dla uproszczonego profilu pracy: jedna moc P przez stałą liczbę godzin w roku.
        """
        required_cols = ['Total power [W]', 'Em [lx]', 'Road W[m]', 'Delta [m]']
        missing = [c for c in required_cols if c not in self.df.columns]
        if missing:
            print(f"⚠ Nie dodano wskaźników Dp/De – brak kolumn: {', '.join(missing)}")
            return

        d = self.df

        # Upewniamy się, że dane geometryczne są liczbowe
        road_w = pd.to_numeric(d['Road W[m]'], errors='coerce')
        delta = pd.to_numeric(d['Delta [m]'], errors='coerce')

        # Pole powierzchni modułu [m2]
        area = road_w * delta
        area = area.replace(0, np.nan)

        # --- Dp ---
        # DP = P / sum(E_i * A_i)
        # Przy pojedynczym module: sum(E_i * A_i) ~ Em * A
        em = pd.to_numeric(d['Em [lx]'], errors='coerce')
        denom_dp = em * area
        denom_dp = denom_dp.replace(0, np.nan)
        d['Dp [W/(lx*m2)]'] = (d['Total power [W]'] / denom_dp).replace([np.inf, -np.inf], np.nan)

        # --- De ---
        # DE = sum(P_j * t_j) / A
        # Uproszczenie: pojedynczy poziom mocy P przez H godzin/rok.
        ANNUAL_HOURS = 4000  # możesz zmienić tę wartość wg profilu pracy instalacji
        num_de = d['Total power [W]'] * ANNUAL_HOURS  # [Wh/rok] dla modułu
        # Konwersja z Wh na kWh (dzielimy przez 1000)
        d['De [kWh/m2 rok]'] = ((num_de / area) / 1000).replace([np.inf, -np.inf], np.nan)

    def _save_csv_with_new_columns(self):
        """Zapisuje DataFrame do nowego pliku CSV z sufiksem '_30_kolumn'"""
        # Utworzenie nazwy nowego pliku
        base_name = os.path.splitext(os.path.basename(input_file))[0]  # wycinek_100k_rows
        base_dir = os.path.dirname(input_file)  # katalog z plikiem
        new_filename = f"{base_name}_30_kolumn.csv"
        new_filepath = os.path.join(base_dir, new_filename)
        
        # Zapisanie pliku z tym samym formatem co oryginał
        self.df.to_csv(new_filepath, sep=';', encoding='cp1250', decimal=',', index=False)
        
        # Wyświetlenie informacji w konsoli
        print(f"✓ Zapisano nowy plik: {new_filepath}")
        print(f"  Liczba wierszy: {len(self.df)}")
        print(f"  Liczba kolumn: {len(self.df.columns)}")

    def load_data(self):
        """📥 Wczytywanie i czyszczenie danych"""
        try:
            # Resetowanie paska postępu
            self.progress_var.set(0)
            self.progress_bar.config(mode='determinate')
            self.status_label.config(text="Status: Wczytywanie pliku...", fg="#e67e22")
            self.root.update()
            
            # Wczytywanie pliku (0-30%)
            self.df = pd.read_csv(input_file, sep=';', encoding='cp1250', decimal=',', low_memory=False)
            self.df.columns = self.df.columns.str.strip()
            self.progress_var.set(30)
            self.status_label.config(text="Status: Konwersja danych...", fg="#e67e22")
            self.root.update()
            
            # Konwersja na liczby (30-50%)
            num_cols = ['Lav [cd/m2]', 'Uo (L)', 'Ul', 'TI [%]', 'Rei', 'Total flux [lm]', 
                       'Total power [W]', 'Road W[m]', 'Delta [m]', 'Lph [m]']
            for i, col in enumerate(num_cols):
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                # Aktualizacja postępu
                if (i + 1) % 2 == 0:  # Aktualizuj co 2 kolumny
                    self.progress_var.set(30 + (i + 1) / len(num_cols) * 20)
                    self.root.update()
            
            self.progress_var.set(50)
            self.status_label.config(text="Status: Dodawanie 30 nowych kolumn...", fg="#e67e22")
            self.root.update()

            # Dodanie 30 kolumn: 6 klas × 5 parametrów (M1 L, M1 Uo, M1 Ul, M1 Rei, M1 Fti, itd.)
            self._add_class_parameter_columns()

            # Dodanie wskaźników mocy Dp i De
            self._add_power_indicators()
            self.progress_var.set(80)
            self.status_label.config(text="Status: Zapisanie pliku...", fg="#e67e22")
            self.root.update()

            # Zapisanie nowego pliku CSV z dodanymi kolumnami
            self._save_csv_with_new_columns()
            self.progress_var.set(95)
            self.status_label.config(text="Status: Przygotowanie interfejsu...", fg="#e67e22")
            self.root.update()

            # Wypełnienie listy opraw
            lums = ["Wszystkie"] + sorted(self.df['Ldc name'].dropna().unique().tolist())
            self.brand_combo.config(values=lums, state="readonly")
            
            # Aktywacja przycisków
            self.btn_p1.config(state=tk.NORMAL)
            self.btn_p2.config(state=tk.NORMAL)
            self.btn_p3.config(state=tk.NORMAL)
            self.btn_e1.config(state=tk.NORMAL)
            self.btn_e2.config(state=tk.NORMAL)
            self.btn_e3.config(state=tk.NORMAL)
            self.btn_e4.config(state=tk.NORMAL)
            self.btn_e5.config(state=tk.NORMAL)
            self.btn_e6.config(state=tk.NORMAL)
            self.btn_view_table.config(state=tk.NORMAL)
            self.btn_best.config(state=tk.NORMAL)
            self.brand_combo.config(state="readonly")
            
            self.progress_var.set(100)
            self.status_label.config(text="Status: Dane gotowe", fg="green")
            
            # Aktualizacja liczby konfiguracji
            num_configs = len(self.df)
            self.count_label.config(text=f"Liczba konfiguracji: {num_configs:,}", fg="#2c3e50")
            self.root.update()
            
            # Pobranie nazwy zapisanego pliku do komunikatu
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            new_filename = f"{base_name}_30_kolumn.csv"
            
            messagebox.showinfo("Sukces", 
                              f"Dane wczytane pomyślnie!\n\n"
                              f"Dodano 30 nowych kolumn.\n"
                              f"Zapisano nowy plik:\n{new_filename}")
        except Exception as e:
            self.progress_var.set(0)
            self.status_label.config(text="Status: Błąd podczas wczytywania", fg="red")
            messagebox.showerror("Błąd", f"Nie znaleziono pliku lub błąd formatu: {e}")

    def get_filtered_df(self):
        """Filtracja danych po modelu oprawy"""
        selected = self.brand_var.get()
        if selected == "Wszystkie":
            return self.df
        return self.df[self.df['Ldc name'] == selected]

    def _get_norm_row(self, klasa: str):
        """Zwraca wiersz z tabeli norm dla danej klasy (M1–M6)."""
        return self.std[self.std['Klasa'] == klasa].iloc[0]

    def plot_parameters(self):
        """📊 Pokazuje jaki % scenariuszy dana oprawa spełnia dla każdej klasy"""
        d = self.get_filtered_df()
        results = []

        for _, row in self.std.iterrows():
            klasa = row['Klasa']
            mask_col = f"Spełnia normę {klasa}"
            if mask_col not in d.columns:
                continue
            success_rate = d[mask_col].mean() * 100
            results.append({'Klasa': klasa, 'Skuteczność [%]': success_rate})

        plt.figure(figsize=(10, 6))
        sns.barplot(data=pd.DataFrame(results), x='Klasa', y='Skuteczność [%]', palette="viridis")
        plt.title(f"Uniwersalność oprawy: {self.brand_var.get()}")
        plt.ylim(0, 105)
        plt.show()

    def plot_flux_balance(self):
        """📈 Histogram pokazujący rozkład strumienia dla projektów udanych vs nieudanych"""
        klasa = self.class_var.get()
        d = self.get_filtered_df().copy()

        mask_col = f"Spełnia normę {klasa}"
        if mask_col not in d.columns:
            messagebox.showerror("Błąd", f"Brak kolumny '{mask_col}' w danych. Wczytaj dane ponownie.")
            return

        d['Spełnia normę'] = d[mask_col]
        
        # Zamiana True/False na Tak/Nie w legendzie
        d['Spełnia normę'] = d['Spełnia normę'].map({True: 'Tak', False: 'Nie'})

        plt.figure(figsize=(10, 6))
        sns.histplot(data=d, x='Total flux [lm]', hue='Spełnia normę', multiple="stack", bins=20, palette="Set1")
        plt.title(f"Bilans strumienia dla klasy {klasa} (Model: {self.brand_var.get()})")
        plt.show()

    def plot_restriction_analysis(self):
        """🔥 Analiza 'wąskich gardeł' - który parametr najczęściej powoduje odrzucenie projektu dla wszystkich klas M1-M6"""
        d = self.get_filtered_df()
        
        # Przygotowanie danych dla wszystkich klas
        results = []
        
        for _, row in self.std.iterrows():
            klasa = row['Klasa']
            norma = row
            
            # Liczymy ile % razy dany parametr spowodował odrzucenie projektu (im wyższy słupek, tym częściej odrzucony)
            results.append({
                'Parametr': 'Luminancja (Lav)',
                'Klasa': klasa,
                'Stopień odrzucenia [%]': (d['Lav [cd/m2]'] < norma['Lav [cd/m2]']).mean() * 100
            })
            results.append({
                'Parametr': 'Równomierność (Uo)',
                'Klasa': klasa,
                'Stopień odrzucenia [%]': (d['Uo (L)'] < norma['Uo (L)']).mean() * 100
            })
            results.append({
                'Parametr': 'Równ. wzdłużna (Ul)',
                'Klasa': klasa,
                'Stopień odrzucenia [%]': (d['Ul'] < norma['Ul']).mean() * 100
            })
            results.append({
                'Parametr': 'Olśnienie (TI)',
                'Klasa': klasa,
                'Stopień odrzucenia [%]': (d['TI [%]'] > norma['TI [%]']).mean() * 100
            })
            results.append({
                'Parametr': 'Otoczenie (Rei)',
                'Klasa': klasa,
                'Stopień odrzucenia [%]': (d['Rei'] < norma['Rei']).mean() * 100
            })
        
        df_results = pd.DataFrame(results)
        
        # Tworzenie wykresu grupowego
        plt.figure(figsize=(14, 8))
        
        # Przygotowanie danych do wykresu - pivot table
        pivot_data = df_results.pivot(index='Parametr', columns='Klasa', values='Stopień odrzucenia [%]')
        
        # Kolejność parametrów (od góry do dołu)
        param_order = ['Luminancja (Lav)', 'Równomierność (Uo)', 'Równ. wzdłużna (Ul)', 
                      'Olśnienie (TI)', 'Otoczenie (Rei)']
        pivot_data = pivot_data.reindex(param_order)
        
        # Wykres grupowy
        x = range(len(pivot_data.index))
        width = 0.13  # Szerokość słupka (6 klas + odstępy)
        
        colors = plt.cm.viridis(np.linspace(0, 1, 6))  # 6 kolorów dla 6 klas
        
        # Mapowanie parametrów na ich normy i jednostki
        param_info = {
            'Luminancja (Lav)': {'unit': 'cd/m2', 'comparison': '<'},
            'Równomierność (Uo)': {'unit': '', 'comparison': '<'},
            'Równ. wzdłużna (Ul)': {'unit': '', 'comparison': '<'},
            'Olśnienie (TI)': {'unit': '%', 'comparison': '>'},
            'Otoczenie (Rei)': {'unit': '', 'comparison': '<'}
        }
        
        # Rysowanie słupków w kolejności M1-M6 od góry do dołu
        # M1 będzie na górze (offset ujemny), M6 na dole (offset dodatni)
        # Zapisujemy handles i labels w kolejności rysowania
        legend_handles = []
        legend_labels = []
        klasa_order = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
        
        for i, klasa in enumerate(klasa_order):
            # Offset: M1 = -2.5*width (góra), M6 = 2.5*width (dół)
            # Dla barh: większy offset = wyżej, więc odwracamy
            offset = (2.5 - i) * width  # M1 (i=0) = 2.5*width (góra), M6 (i=5) = -2.5*width (dół)
            bars = plt.barh([y + offset for y in x], pivot_data[klasa], width, 
                    label=klasa, color=colors[i], zorder=i)
            
            # Zapisujemy handle dla legendy
            legend_handles.append(bars[0])
            legend_labels.append(klasa)
            
            # Pobranie normy dla danej klasy
            norma = self.std[self.std['Klasa'] == klasa].iloc[0]
            
            # Dodanie podpisów na szczytach słupków
            for j, param in enumerate(param_order):
                bar_value = pivot_data[klasa].iloc[j]
                if pd.notna(bar_value) and bar_value > 0:
                    # Określenie tekstu podpisu na podstawie parametru
                    if param == 'Luminancja (Lav)':
                        norma_val = norma['Lav [cd/m2]']
                        label_text = f"< {norma_val} cd/m²"
                    elif param == 'Równomierność (Uo)':
                        norma_val = norma['Uo (L)']
                        label_text = f"< {norma_val}"
                    elif param == 'Równ. wzdłużna (Ul)':
                        norma_val = norma['Ul']
                        label_text = f"< {norma_val}"
                    elif param == 'Olśnienie (TI)':
                        norma_val = norma['TI [%]']
                        label_text = f"> {norma_val} %"
                    elif param == 'Otoczenie (Rei)':
                        norma_val = norma['Rei']
                        label_text = f"< {norma_val}"
                    else:
                        label_text = ""
                    
                    # Pozycja tekstu na szczycie słupka
                    x_pos = bar_value + 1  # Mały offset od szczytu słupka
                    y_pos = j + offset
                    
                    # Dodanie tekstu
                    plt.text(x_pos, y_pos, label_text, 
                            fontsize=8, va='center', ha='left',
                            rotation=0, color='black', weight='bold')
        
        plt.yticks(x, pivot_data.index)
        plt.xlabel("Stopień odrzucenia [%]")
        plt.title(f"Analiza restrykcyjności parametrów dla wszystkich klas M1-M6\n(Model: {self.brand_var.get()}, wyższy słupek = częstsze odrzucenie przez ten parametr)")
        plt.xlim(0, 110)
        
        # Legenda w kolejności zgodnej z rysowaniem słupków (M1-M6 od góry do dołu)
        plt.legend(legend_handles, legend_labels, title='Klasa', loc='lower right')
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_luminous_efficacy(self):
        """⚡ Analiza skuteczności świetlnej (lm/W) - kluczowy wskaźnik efektywności energetycznej"""
        d = self.get_filtered_df().copy()
        
        # Sprawdzenie dostępności kolumn
        if 'Total flux [lm]' not in d.columns or 'Total power [W]' not in d.columns:
            messagebox.showerror("Błąd", "Brakuje kolumn: 'Total flux [lm]' lub 'Total power [W]'")
            return
        
        # Obliczenie skuteczności świetlnej
        d['Skuteczność [lm/W]'] = d['Total flux [lm]'] / d['Total power [W]']
        d = d[d['Skuteczność [lm/W]'].notna() & (d['Skuteczność [lm/W]'] > 0)]
        
        if len(d) == 0:
            messagebox.showerror("Błąd", "Brak danych do analizy")
            return
        
        klasa = self.class_var.get()
        mask_col = f"Spełnia normę {klasa}"
        if mask_col not in d.columns:
            messagebox.showerror("Błąd", f"Brak kolumny '{mask_col}' w danych. Wczytaj dane ponownie.")
            return
        d['Spełnia normę'] = d[mask_col]
        d['Spełnia normę'] = d['Spełnia normę'].map({True: 'Tak', False: 'Nie'})
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=d, x='Spełnia normę', y='Skuteczność [lm/W]', palette="Set2")
        plt.title(f"Skuteczność świetlna dla klasy {klasa}\n(Model: {self.brand_var.get()})")
        plt.ylabel("Skuteczność świetlna [lm/W]")
        plt.xlabel("Spełnia normę")
        plt.grid(axis='y', alpha=0.3)
        plt.show()

    def plot_power_per_meter(self):
        """💡 Analiza mocy jednostkowej na metr długości drogi (W/m)"""
        d = self.get_filtered_df().copy()
        
        if 'Total power [W]' not in d.columns or 'Delta [m]' not in d.columns:
            messagebox.showerror("Błąd", "Brakuje kolumn: 'Total power [W]' lub 'Delta [m]'")
            return
        
        # Moc jednostkowa = moc / rozstaw opraw
        d['Moc jednostkowa [W/m]'] = d['Total power [W]'] / d['Delta [m]']
        d = d[d['Moc jednostkowa [W/m]'].notna() & (d['Moc jednostkowa [W/m]'] > 0)]
        
        if len(d) == 0:
            messagebox.showerror("Błąd", "Brak danych do analizy")
            return
        
        klasa = self.class_var.get()
        mask_col = f"Spełnia normę {klasa}"
        if mask_col not in d.columns:
            messagebox.showerror("Błąd", f"Brak kolumny '{mask_col}' w danych. Wczytaj dane ponownie.")
            return
        d['Spełnia normę'] = d[mask_col]
        d['Spełnia normę'] = d['Spełnia normę'].map({True: 'Tak', False: 'Nie'})
        
        plt.figure(figsize=(12, 6))
        sns.histplot(data=d, x='Moc jednostkowa [W/m]', hue='Spełnia normę', 
                     multiple="stack", bins=30, palette="Set1")
        plt.title(f"Moc jednostkowa na metr drogi dla klasy {klasa}\n(Model: {self.brand_var.get()})")
        plt.xlabel("Moc jednostkowa [W/m]")
        plt.ylabel("Liczba projektów")
        plt.grid(axis='y', alpha=0.3)
        plt.show()

    def plot_power_vs_compliance(self):
        """📊 Porównanie mocy dla projektów spełniających vs nie spełniających normy"""
        klasa = self.class_var.get()
        d = self.get_filtered_df().copy()
        
        if 'Total power [W]' not in d.columns:
            messagebox.showerror("Błąd", "Brakuje kolumny: 'Total power [W]'")
            return
        
        mask_col = f"Spełnia normę {klasa}"
        if mask_col not in d.columns:
            messagebox.showerror("Błąd", f"Brak kolumny '{mask_col}' w danych. Wczytaj dane ponownie.")
            return
        d['Spełnia normę'] = d[mask_col]
        d['Spełnia normę'] = d['Spełnia normę'].map({True: 'Tak', False: 'Nie'})
        d = d[d['Total power [W]'].notna() & (d['Total power [W]'] > 0)]
        
        if len(d) == 0:
            messagebox.showerror("Błąd", "Brak danych do analizy")
            return
        
        plt.figure(figsize=(12, 6))
        sns.violinplot(data=d, x='Spełnia normę', y='Total power [W]', palette="Set2", inner="box")
        plt.title(f"Rozkład mocy dla projektów spełniających/nie spełniających normy klasy {klasa}\n(Model: {self.brand_var.get()})")
        plt.ylabel("Moc całkowita [W]")
        plt.xlabel("Spełnia normę")
        plt.grid(axis='y', alpha=0.3)
        plt.show()

    def plot_efficiency_ranking(self):
        """🏆 Ranking opraw według efektywności energetycznej (średnia skuteczność dla projektów spełniających normę)"""
        klasa = self.class_var.get()
        d = self.get_filtered_df().copy()
        
        if 'Total flux [lm]' not in d.columns or 'Total power [W]' not in d.columns or 'Ldc name' not in d.columns:
            messagebox.showerror("Błąd", "Brakuje wymaganych kolumn")
            return
        
        # Obliczenie skuteczności świetlnej
        d['Skuteczność [lm/W]'] = d['Total flux [lm]'] / d['Total power [W]']
        d = d[d['Skuteczność [lm/W]'].notna() & (d['Skuteczność [lm/W]'] > 0)]
        
        # Filtracja tylko projektów spełniających normę (na bazie precomputed maski)
        mask_col = f"Spełnia normę {klasa}"
        if mask_col not in d.columns:
            messagebox.showerror("Błąd", f"Brak kolumny '{mask_col}' w danych. Wczytaj dane ponownie.")
            return
        d['Spełnia normę'] = d[mask_col]
        
        # Analiza tylko dla projektów spełniających normę
        d_compliant = d[d['Spełnia normę']].copy()
        
        if len(d_compliant) == 0:
            messagebox.showwarning("Uwaga", f"Brak projektów spełniających normę klasy {klasa} dla wybranego modelu")
            return
        
        # Ranking opraw według średniej skuteczności
        ranking = d_compliant.groupby('Ldc name')['Skuteczność [lm/W]'].agg(['mean', 'count']).reset_index()
        ranking = ranking[ranking['count'] >= 5]  # Minimum 5 projektów
        ranking = ranking.sort_values('mean', ascending=False).head(15)  # Top 15
        
        if len(ranking) == 0:
            messagebox.showwarning("Uwaga", "Za mało danych do utworzenia rankingu")
            return
        
        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(range(len(ranking)))
        bars = plt.barh(range(len(ranking)), ranking['mean'], color=colors)
        plt.yticks(range(len(ranking)), ranking['Ldc name'])
        plt.xlabel("Średnia skuteczność świetlna [lm/W]")
        plt.title(f"Ranking opraw według efektywności energetycznej\n(Klasa: {klasa}, tylko projekty spełniające normę, min. 5 projektów)")
        plt.gca().invert_yaxis()
        
        # Dodanie wartości na słupkach
        for i, (idx, row) in enumerate(ranking.iterrows()):
            plt.text(row['mean'], i, f" {row['mean']:.1f} lm/W\n (n={int(row['count'])})", 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        plt.grid(axis='x', alpha=0.3)
        plt.show()

    def plot_dp_indicator(self):
        """📉 Wskaźnik mocy Dp – porównanie dla projektów spełniających i niespełniających normy (dla wybranej klasy)."""
        d = self.get_filtered_df().copy()

        if 'Dp [W/(lx*m2)]' not in d.columns:
            messagebox.showerror("Błąd", "Brakuje kolumny 'Dp [W/(lx*m2)]'. Wczytaj dane ponownie.")
            return

        d = d[d['Dp [W/(lx*m2)]'].notna() & (d['Dp [W/(lx*m2)]'] > 0)]
        if len(d) == 0:
            messagebox.showerror("Błąd", "Brak danych do analizy Dp.")
            return

        klasa = self.class_var.get()
        mask_col = f"Spełnia normę {klasa}"
        if mask_col not in d.columns:
            messagebox.showerror("Błąd", f"Brak kolumny '{mask_col}' w danych. Wczytaj dane ponownie.")
            return

        d['Spełnia normę'] = d[mask_col].map({True: 'Tak', False: 'Nie'})

        plt.figure(figsize=(12, 6))
        sns.boxplot(data=d, x='Spełnia normę', y='Dp [W/(lx*m2)]', palette="Set2")
        plt.title(f"Wskaźnik mocy Dp dla klasy {klasa}\n(Model: {self.brand_var.get()})")
        plt.ylabel("Dp [W/(lx*m²)]")
        plt.xlabel("Spełnia normę")
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_de_indicator(self):
        """📉 Wskaźnik energii De – rozkład rocznego zużycia energii na m²."""
        d = self.get_filtered_df().copy()

        if 'De [kWh/m2 rok]' not in d.columns:
            messagebox.showerror("Błąd", "Brakuje kolumny 'De [kWh/m2 rok]'. Wczytaj dane ponownie.")
            return

        d = d[d['De [kWh/m2 rok]'].notna() & (d['De [kWh/m2 rok]'] > 0)]
        if len(d) == 0:
            messagebox.showerror("Błąd", "Brak danych do analizy De.")
            return

        klasa = self.class_var.get()

        plt.figure(figsize=(12, 6))
        sns.histplot(data=d, x='De [kWh/m2 rok]', bins=30, color='steelblue', kde=True)
        plt.title(f"Wskaźnik energii De (roczne zużycie energii na m²)\n(Model: {self.brand_var.get()}, Klasa: {klasa})")
        plt.xlabel("De [kWh/m²·rok]")
        plt.ylabel("Liczba projektów")
        plt.xlim(0, 1)  # Ograniczenie zakresu wartości od 0 do 1
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()

    def show_data_table(self):
        """📋 Wyświetla dane jako tabela w nowym oknie"""
        if self.df is None or len(self.df) == 0:
            messagebox.showwarning("Uwaga", "Brak danych do wyświetlenia. Najpierw wczytaj dane.")
            return
        
        # Tworzenie nowego okna
        table_window = tk.Toplevel(self.root)
        table_window.title("Tabela Danych")
        table_window.geometry("1400x700")
        
        # Pasek narzędzi z filtrami
        toolbar = tk.Frame(table_window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(toolbar, text="Pokaż wierszy:").pack(side=tk.LEFT, padx=5)
        rows_var = tk.StringVar(value="1000")
        rows_entry = tk.Entry(toolbar, textvariable=rows_var, width=10)
        rows_entry.pack(side=tk.LEFT, padx=5)
        
        # Zmienne do sortowania
        sort_column = [None]  # Używam listy, żeby móc modyfikować w zagnieżdżonej funkcji
        sort_reverse = [False]
        
        def sort_by_column(col):
            """Sortuje dane po wybranej kolumnie"""
            if sort_column[0] == col:
                # Jeśli kliknięto tę samą kolumnę, odwróć kierunek sortowania
                sort_reverse[0] = not sort_reverse[0]
            else:
                # Nowa kolumna - sortuj rosnąco
                sort_column[0] = col
                sort_reverse[0] = False
            refresh_table()
        
        def refresh_table():
            try:
                max_rows = int(rows_var.get())
            except ValueError:
                max_rows = 1000
            
            # Pobranie danych (z filtrem jeśli wybrano oprawę)
            display_df = self.get_filtered_df().copy()
            
            # Sortowanie
            if sort_column[0] is not None and sort_column[0] in display_df.columns:
                try:
                    # Próba konwersji na liczby dla sortowania numerycznego
                    if display_df[sort_column[0]].dtype == 'object':
                        # Sprawdź czy można przekonwertować na liczby
                        numeric_series = pd.to_numeric(display_df[sort_column[0]], errors='coerce')
                        if not numeric_series.isna().all():
                            display_df = display_df.copy()
                            display_df['_sort_temp'] = numeric_series
                            display_df = display_df.sort_values('_sort_temp', ascending=not sort_reverse[0], na_position='last')
                            display_df = display_df.drop('_sort_temp', axis=1)
                        else:
                            # Sortowanie tekstowe
                            display_df = display_df.sort_values(sort_column[0], ascending=not sort_reverse[0], na_position='last')
                    else:
                        # Sortowanie numeryczne
                        display_df = display_df.sort_values(sort_column[0], ascending=not sort_reverse[0], na_position='last')
                except Exception:
                    # W razie błędu, sortuj jako tekst
                    display_df = display_df.sort_values(sort_column[0], ascending=not sort_reverse[0], na_position='last')
            
            # Ograniczenie liczby wierszy
            if len(display_df) > max_rows:
                display_df = display_df.head(max_rows)
                status_text = f"Wyświetlono {max_rows} z {len(self.get_filtered_df())} wierszy"
            else:
                status_text = f"Wyświetlono {len(display_df)} wierszy"
            
            if sort_column[0]:
                arrow = " ↓" if sort_reverse[0] else " ↑"
                status_text += f" | Sortowanie: {sort_column[0]}{arrow}"
            
            # Czyszczenie istniejącej tabeli
            for item in tree.get_children():
                tree.delete(item)
            
            # Aktualizacja nagłówków z oznaczeniem sortowania
            for col in columns:
                header_text = col
                if col == sort_column[0]:
                    arrow = " ↓" if sort_reverse[0] else " ↑"
                    header_text = col + arrow
                tree.heading(col, text=header_text, command=lambda c=col: sort_by_column(c))
            
            # Dodanie wierszy do tabeli
            for idx, row in display_df.iterrows():
                values = [str(val) if pd.notna(val) else '' for val in row]
                tree.insert('', tk.END, values=values)
            
            status_label.config(text=status_text)
        
        refresh_btn = tk.Button(toolbar, text="Odśwież", command=refresh_table, bg="#3498db", fg="white")
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        reset_sort_btn = tk.Button(toolbar, text="Resetuj sortowanie", command=lambda: [sort_column.__setitem__(0, None), sort_reverse.__setitem__(0, False), refresh_table()], bg="#e67e22", fg="white")
        reset_sort_btn.pack(side=tk.LEFT, padx=5)
        
        # Ramka z tabelą i scrollbarami
        frame = tk.Frame(table_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbary
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        
        # Treeview (tabela)
        tree = ttk.Treeview(frame, yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)
        
        # Konfiguracja kolumn
        columns = list(self.df.columns)
        tree['columns'] = columns
        tree['show'] = 'headings'
        
        # Ustawienie szerokości kolumn i nagłówków z możliwością sortowania
        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            # Automatyczna szerokość kolumny (maksymalnie 200px)
            tree.column(col, width=min(200, len(str(col)) * 8 + 20), anchor=tk.W)
        
        # Układanie elementów
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        status_label = tk.Label(table_window, text="", relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Wczytanie danych przy otwarciu
        refresh_table()

    def select_best_luminaires(self):
        """⭐ Wybiera najlepsze 5 opraw dla wybranej klasy"""
        if self.df is None or len(self.df) == 0:
            messagebox.showwarning("Uwaga", "Brak danych. Najpierw wczytaj dane.")
            return
        
        klasa = self.class_var.get()
        
        # Nazwy kolumn dla wybranej klasy
        col_lav = f'{klasa} Lav [cd/m2]'
        col_uo = f'{klasa} Uo (L)'
        col_ul = f'{klasa} Ul'
        col_rei = f'{klasa} Rei'
        col_ti = f'{klasa} TI [%]'
        
        # Sprawdzenie czy kolumny istnieją
        required_cols = [col_lav, col_uo, col_ul, col_rei, col_ti]
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            messagebox.showerror("Błąd", f"Brakuje kolumn: {', '.join(missing_cols)}\nNajpierw wczytaj dane z nowymi kolumnami.")
            return
        
        # Filtrowanie: oprawy spełniające wszystkie warunki (wszystkie parametry >= 100%)
        mask = (
            (self.df[col_lav] >= 100) &
            (self.df[col_uo] >= 100) &
            (self.df[col_ul] >= 100) &
            (self.df[col_rei] >= 100) &
            (self.df[col_ti] >= 100)
        )
        
        compliant_df = self.df[mask].copy()
        
        if len(compliant_df) == 0:
            messagebox.showinfo("Wynik", f"Nie znaleziono opraw spełniających wszystkie warunki dla klasy {klasa}.")
            return
        
        # Sortowanie według Lav [cd/m2] (najbliższe lub większe niż 100%, czyli >= 100%)
        # Sortujemy rosnąco, aby najpierw były te najbliższe 100% (ale >= 100%)
        # Następnie te z większymi wartościami
        compliant_df = compliant_df.sort_values(col_lav, ascending=True, na_position='last')
        
        # Wybór top 5
        top5 = compliant_df.head(5).copy()
        
        # Wyświetlenie wyników w nowym oknie
        self._show_best_luminaires_window(top5, klasa, col_lav, col_uo, col_ul, col_rei, col_ti)
    
    def _show_best_luminaires_window(self, top5_df, klasa, col_lav, col_uo, col_ul, col_rei, col_ti):
        """Wyświetla okno z najlepszymi oprawami"""
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Najlepsze 5 opraw dla klasy {klasa}")
        result_window.geometry("1200x500")
        
        # Nagłówek
        header = tk.Label(result_window, text=f"⭐ Najlepsze 5 opraw dla klasy {klasa}", 
                         font=("Arial", 14, "bold"), fg="#e67e22")
        header.pack(pady=10)
        
        # Informacja o kryteriach
        info_text = "Kryteria: Wszystkie parametry spełniają normę (>= 100%) i posortowane według Lav [cd/m2] (najbliższe lub >= 100%)"
        info_label = tk.Label(result_window, text=info_text, font=("Arial", 9), fg="gray", wraplength=1000)
        info_label.pack(pady=5)
        
        # Ramka z tabelą
        frame = tk.Frame(result_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbary
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        
        # Kolumny do wyświetlenia
        display_cols = ['Ldc name', 'Total power [W]', 'Total flux [lm]', 
                       col_lav, col_uo, col_ul, col_rei, col_ti,
                       'Road W[m]', 'Lph [m]', 'Delta [m]']
        
        # Filtrowanie tylko istniejących kolumn
        display_cols = [col for col in display_cols if col in top5_df.columns]
        
        # Treeview
        tree = ttk.Treeview(frame, columns=display_cols, show='headings', 
                           yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)
        
        # Konfiguracja kolumn
        for col in display_cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.W)
        
        # Dodanie wierszy
        for idx, row in top5_df.iterrows():
            values = []
            for col in display_cols:
                val = row[col]
                if pd.notna(val):
                    if isinstance(val, (int, float)):
                        if col in [col_lav, col_uo, col_ul, col_rei, col_ti]:
                            values.append(f"{val:.2f}%")
                        else:
                            values.append(f"{val:.2f}")
                    else:
                        values.append(str(val))
                else:
                    values.append('')
            tree.insert('', tk.END, values=values)
        
        # Układanie elementów
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Przycisk zamknięcia
        close_btn = tk.Button(result_window, text="Zamknij", command=result_window.destroy, 
                             bg="#3498db", fg="white", width=20)
        close_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LuminaireApp(root)
    root.mainloop()