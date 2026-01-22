import time
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

class AnalysisCalculator:
    def __init__(self):
        self.console = None
        self.csv_files = []
        self.cache_dir = "../data_cache"
        self._filters_cache = {}
        self._filters_cache_order = []
        self._filters_cache_limit = 5
        self._filters_index_cache_file = os.path.join(self.cache_dir, "_filters_cache.json")
        # Kolumny potrzebne, na których się skupiam
        self.chosen_columns = [
            'Ldc name', 'Lamp info', 'Total flux [lm]', 'Total power [W]', 'Street',
            'Power/km  [W/km]', 'Road W[m]', 'Lum pos y [m]', 'Lph [m]',
            'Delta [m]', 'Tilt [°]', 'Lav [cd/m2]', 'Uo (L)', 'Ul', 'TI [%]', 'Rei'
        ]
        # Tworzenie folderu na pliki binarne, jeśli nie istnieje
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    # W analysis.py wewnątrz klasy AnalysisCalculator
    def set_console(self, console_instance):
        """Metoda do podpinania okna konsoli pod silnik"""
        self.console = console_instance
        # TEST: Wymuś log od razu po podpięciu
        self.log("Silnik: Pomyślnie nawiązano połączenie z konsolą GUI.", "success")

    def log(self, message, level="info"):
        """Przekazuje log do GUI używając metody log_message"""
        if hasattr(self, 'console') and self.console:
            # Mapowanie Twoich poziomów na kolory (jeśli chcesz)
            color_map = {
                "success": "#00ff88",
                "error": "#ff4444",
                "warning": "#ffaa00",
                "info": "#cccccc"
            }
            chosen_color = color_map.get(level, "#cccccc")

            # Sprawdzamy, czy podpięta konsola to nasze GUI i ma log_message
            if hasattr(self.console, 'log_message'):
                self.console.log_message(message, color=chosen_color)
            elif hasattr(self.console, 'log'):  # Jeśli to okno terminala z VS Code style
                self.console.log(message, level)
            return

        # Ostateczność, jeśli nic nie jest podpięte
        print(f"[{level.upper()}] {message}")

    def set_csv_files(self, csv_files):
        """Metoda wywoływana przez GUI zaraz po wyborze folderu"""
        self.csv_files = csv_files
        self._filters_cache.clear()
        self._filters_cache_order = []
        # Zamiast print, używamy log:
        if csv_files:
            self.log(f"Załadowano listę plików: {len(csv_files)} szt.", "success")
        else:
            self.log("Wybrany folder nie zawiera plików CSV!", "warning")

    def decode_arrangement(self, df):
        """Rozpoznaje typ rozmieszczenia i raportuje statystyki do konsoli"""
        if 'Street' not in df.columns:
            self.log("Brak kolumny 'Street' – nie można rozpoznać układu!", "warning")
            df['Arrangement'] = "Nieokreślone"
            return df

        # Słownik mapujący
        mapping = {
            'SGL': 'Jednostronny',
            'OPP': 'Naprzeciwlegly',
            'STG': 'Naprzemianlegly'
        }

        df['Arrangement'] = "Inne"

        # Logujemy rozpoczęcie analizy geometrii
        # (używamy małego wcięcia ∟, żeby log był czytelny pod nazwą pliku)
        for code, name in mapping.items():
            mask = df['Street'].str.contains(code, na=False)
            df.loc[mask, 'Arrangement'] = name

        # --- FAJNA OPCJA: Statystyka układów w tym pliku ---
        found_types = df['Arrangement'].value_counts()
        summary = ", ".join([f"{k}: {v}" for k, v in found_types.items() if k != "Inne"])

        if summary:
            self.log(f"  ∟ Geometria: {summary}", "info")
        else:
            self.log("  ∟ Nie rozpoznano standardowych układów (SGL/OPP/STG)", "warning")

        return df

    def apply_custom_mf(self, df, mf_map):
        """Przelicza parametry świetlne na podstawie MF wybranego przez użytkownika"""
        if not mf_map:
            return df

        # Tworzymy klucz identyfikujący oprawę
        df['lum_key'] = df['Ldc name'].astype(str) + " " + df['Lamp info'].astype(str)

        # Logujemy tylko zmienione MF dla opraw, które występują w chunce
        present_lums = set(df['lum_key'].unique())
        for lum, mf in mf_map.items():
            try:
                new_mf = float(mf)
            except Exception:
                continue
            if new_mf != 0.8 and lum in present_lums:
                multiplier = new_mf / 0.8
                self.log(f"  ∟ Korekta fotometrii: {lum[:40]}... -> MF: {new_mf} (x{multiplier:.2f})", "info")

        mf_map_float = {}
        for lum, mf in mf_map.items():
            try:
                mf_map_float[lum] = float(mf)
            except Exception:
                continue

        mf_series = df['lum_key'].map(mf_map_float).fillna(0.8).astype(float)
        multiplier = mf_series / 0.8
        mask = multiplier != 1.0

        if mask.any():
            cols_to_adjust = ['Lav [cd/m2]', 'Eav [lx]', 'Emin [lx]', 'Emax [lx]', 'Lmin [cd/m2]',
                              'Lmax [cd/m2]']
            for col in cols_to_adjust:
                if col in df.columns:
                    df.loc[mask, col] = df.loc[mask, col].mul(multiplier[mask], axis=0)

        return df

    def label_norms_vectorized(self, df):
        """Oblicza stopień spełnienia normy (30 kolumn) i klasyfikuje warianty"""
        # 1. Mapowanie kolumn
        col_map = {
            'Lav': 'Lav [cd/m2]',
            'Uo': 'Uo (L)',
            'Ul': 'Ul',
            'TI': 'TI [%]',
            'Rei': 'Rei'
        }

        # Sprawdzenie czy kolumny istnieją w tym pliku
        missing = [c for c in col_map.values() if c not in df.columns]
        if missing:
            self.log(f"  ⚠ Brak kolumn do weryfikacji norm: {missing}", "warning")
            return df

        # 2. Obliczanie 30 kolumn procentowych (wektorowo - bardzo szybko)
        for class_name, limits in NORMS.items():
            for param, req_val in limits.items():
                col_name = f"{param}({class_name})"
                csv_col = col_map[param]

                if param == 'TI':
                    # Olśnienie: im mniej, tym lepiej
                    df[col_name] = (req_val / df[csv_col].replace(0, 0.1)) * 100
                else:
                    # Jasność/Równomierność: im więcej, tym lepiej
                    df[col_name] = (df[csv_col] / req_val) * 100

                df[col_name] = df[col_name].round(1)

        # 3. Klasyfikacja 'best_class' (od najwyższej klasy M1 do najniższej M6)
        df['best_class'] = "Brak"
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

        # --- RAPORTOWANIE DO KONSOLI ---
        # Wyciągamy statystykę klas, aby wiedzieć, co siedzi w danych
        class_stats = df['best_class'].value_counts()

        # Budujemy czytelny ciąg tekstowy, np. "M3: 50, M4: 120, Brak: 1000"
        stats_str = ", ".join([f"{k}: {v}" for k, v in class_stats.items() if v > 0])

        # Logujemy to tylko dla pierwszego chunka pliku, żeby nie powtarzać w kółko
        if not getattr(self, 'already_logged_norms', False):
            self.log(f"  ∟ Normy EN13201: Wygenerowano 30 kolumn wskaźnikowych.", "info")
            self.log(f"  ∟ Rozkład klas: {stats_str}", "info")
            self.already_logged_norms = True

        return df

    def calculate_efficiency_indicators(self, df, burning_hours):
        """
        Oblicza wskaźniki efektywności energetycznej Dp i De oraz Power_per_km.
        Loguje średnie wartości dla aktualnego pliku.
        """
        # 1. Obliczamy pole powierzchni obliczeniowej (A)
        df['A [m2]'] = df['Road W[m]'] * df['Delta [m]']

        # 2. Obliczamy Dp [W / (lx * m2)] - Wskaźnik gęstości mocy
        df['Dp'] = df['Total power [W]'] / (df['Em [lx]'] * df['A [m2]']).replace(0, 0.01)

        # 3. Obliczamy De [kWh / (m2 * rok)] - Wskaźnik zużycia energii
        df['De'] = (df['Total power [W]'] * burning_hours) / (df['A [m2]'] * 1000)

        # 4. Dodatkowa kolumna: Moc na kilometr [W/km]
        df['Power_per_km'] = (1000 / df['Delta [m]']) * df['Total power [W]']

        # Zaokrąglanie
        df['Dp'] = df['Dp'].round(4)
        df['De'] = df['De'].round(4)
        df['Power_per_km'] = df['Power_per_km'].round(2)

        # --- RAPORTOWANIE DO KONSOLI ---
        # Logujemy tylko raz na plik (używając flagi resetowanej w pętli głównej)
        if not getattr(self, 'already_logged_efficiency', False):
            avg_dp = df['Dp'].mean()
            avg_de = df['De'].mean()
            avg_p_km = df['Power_per_km'].mean()

            self.log(f"  ∟ Efektywność (śr.): Dp: {avg_dp:.4f}, De: {avg_de:.2f} kWh/m²/rok", "info")
            self.log(f"  ∟ Moc linii (śr.): {avg_p_km / 1000:.2f} kW/km", "info")

            self.already_logged_efficiency = True

        return df

    def calculate_results(self, config=None):
        """Główna pętla mielenia danych z pełnym raportowaniem statusu"""
        if not self.csv_files:
            self.log("Brak plików CSV do przetworzenia!", "error")
            return
        self._filters_cache.clear()
        self._filters_cache_order = []

        # Pobieramy dane z configu
        mf_map = config.get("mf_map", {}) if config else {}
        burning_hours = config.get("burning_hours", 4000.0) if config else 4000.0

        self.log("ROZPOCZĘTO PROCES KONWERSJI I ANALIZY", "header")
        self.log(f"Pliki: {len(self.csv_files)} | Czas świecenia: {burning_hours}h", "info")

        start_total = time.time()

        for idx, csv_path in enumerate(self.csv_files):
            # --- RESET FLAG LOGOWANIA DLA KAŻDEGO PLIKU ---
            self.already_logged_mf = False
            self.already_logged_norms = False
            self.already_logged_efficiency = False

            import hashlib
            file_name = os.path.basename(csv_path)
            base_name = os.path.splitext(file_name)[0]
            # Unikamy nadpisywania cache, gdy istnieją pliki o tej samej nazwie
            path_hash = hashlib.md5(csv_path.encode("utf-8")).hexdigest()[:8]
            folder_name = f"{base_name}_{path_hash}"
            file_cache_path = os.path.join(self.cache_dir, folder_name)

            self.log(f"Plik {idx + 1}/{len(self.csv_files)}: {file_name}", "success")
            start_file = time.time()

            if not os.path.exists(file_cache_path):
                os.makedirs(file_cache_path)

            try:
                # Czytamy CSV w kawałkach (chunks)
                chunks = pd.read_csv(csv_path, sep=';', chunksize=500000, low_memory=False, encoding='cp1252')

                total_rows = 0
                for i, chunk in enumerate(chunks):
                    # 1. Dekodowanie układu (loguje geometrię)
                    chunk = self.decode_arrangement(chunk)

                    # 2. Aplikacja MF (loguje zmianę współczynnika)
                    chunk = self.apply_custom_mf(chunk, mf_map)

                    # 3. Liczenie norm (loguje rozkład klas M1-M6)
                    chunk = self.label_norms_vectorized(chunk)

                    # 4. Obliczanie wskaźników (loguje De, Dp i moc linii)
                    chunk = self.calculate_efficiency_indicators(chunk, burning_hours)

                    # 5. Zapis do Parquet
                    chunk.to_parquet(os.path.join(file_cache_path, f"part_{i}.parquet"), index=False)

                    total_rows += len(chunk)

                end_file = time.time()
                self.log(f"   ∟ Sukces: {total_rows} rekordów w {end_file - start_file:.2f}s", "info")

            except Exception as e:
                self.log(f"Błąd krytyczny pliku {file_name}: {str(e)}", "error")

        end_total = time.time()
        self.log(f"PROCES ZAKOŃCZONY W {end_total - start_total:.2f}s", "header")
        self.log("Dane gotowe do wizualizacji w panelu końcowym.", "success")

    def get_unique_items(self):
        """Wyciąga unikalne wartości używając poprawnych nazw kolumn z Parquet"""
        import glob
        import os
        import pandas as pd
        import json
        try:
            import pyarrow.parquet as pq
        except Exception:
            pq = None

        all_files = glob.glob(os.path.join(self.cache_dir, "**", "*.parquet"), recursive=True)
        if not all_files:
            return {}

        self.log(f"Indeksowanie bazy filtrów ({len(all_files)} plików)...", "info")

        def _signature(files):
            items = []
            for f in files:
                try:
                    items.append([f, os.path.getmtime(f), os.path.getsize(f)])
                except Exception:
                    items.append([f, 0, 0])
            return sorted(items)

        signature = _signature(all_files)

        # Cache na dysku dla menu wstążkowego
        try:
            if os.path.exists(self._filters_index_cache_file):
                with open(self._filters_index_cache_file, "r", encoding="utf-8") as fh:
                    cached = json.load(fh)
                if cached.get("signature") == signature:
                    return cached.get("data", {})
        except Exception:
            pass

        try:
            # Używamy nazw kolumn, które widnieją w Twoim logu (np. 'best_class')
            mapping = {
                'Nazwa oprawy': 'Ldc name',
                'Rozmieszczenie': 'Arrangement',
                'Szerekość drogi [m]': 'Road W[m]',
                'Odstęp między oprawami [m]': 'Delta [m]',
                'Wysokość montażu [m]': 'Lph [m]',
                'Nachylenie (°)': 'Tilt [°]',
                'Klasa oświetleniowa': 'best_class'  # Mapujemy ładną nazwę na fizyczną kolumnę
            }

            cols_to_extract = {nice_name: set() for nice_name in mapping.keys()}

            for file in all_files:
                # Sprawdzamy jakie kolumny są w tym konkretnym pliku
                actual_columns = None
                if pq is not None:
                    try:
                        actual_columns = pq.ParquetFile(file).schema.names
                    except Exception:
                        actual_columns = None
                if actual_columns is None:
                    try:
                        actual_columns = pd.read_parquet(file).columns
                    except Exception:
                        continue

                # Budujemy listę kolumn do wczytania, które faktycznie istnieją
                to_read = [phys for nice, phys in mapping.items() if phys in actual_columns]

                if to_read:
                    if pq is not None:
                        try:
                            temp_df = pq.read_table(file, columns=to_read).to_pandas()
                        except Exception:
                            temp_df = pd.read_parquet(file, columns=to_read)
                    else:
                        temp_df = pd.read_parquet(file, columns=to_read)

                    # Przepisujemy dane do zestawów unikalnych wartości
                    for nice_name, phys_name in mapping.items():
                        if phys_name in temp_df.columns:
                            cols_to_extract[nice_name].update(temp_df[phys_name].dropna().unique())

            # Budowanie finalnego słownika dla GUI
            final_menu_data = {}
            for col, values in cols_to_extract.items():
                sorted_vals = sorted([str(v) for v in values])
                final_menu_data[col] = ["Wszystkie"] + sorted_vals

            try:
                with open(self._filters_index_cache_file, "w", encoding="utf-8") as fh:
                    json.dump({"signature": signature, "data": final_menu_data}, fh)
            except Exception:
                pass

            return final_menu_data

        except Exception as e:
            self.log(f"❌ Błąd indeksowania: {e}", "error")
            # Zwracamy pusty słownik, żeby GUI się nie zawiesiło
            return {}

    def get_unique_luminaires(self):
        """Skanuje pliki CSV w poszukiwaniu unikalnych opraw dla tabeli MF"""
        if not self.csv_files:
            self.log("Błąd skanowania: Brak wybranych plików CSV.", "error")
            return []

        self.log(f"Rozpoczynam głębokie skanowanie {len(self.csv_files)} plików w poszukiwaniu opraw...", "info")
        lums = set()

        import time
        start_time = time.time()

        for f in self.csv_files:
            f_name = os.path.basename(f)
            try:
                # Wczytujemy TYLKO niezbędne kolumny – to oszczędza mnóstwo czasu i RAMu
                temp_df = pd.read_csv(f, sep=';', usecols=['Ldc name', 'Lamp info'], encoding='cp1252')

                # Tworzymy klucz (taki sam jak później w apply_custom_mf!)
                # Używamy separatora " | " dla czytelności w tabeli GUI
                temp_df['key'] = temp_df['Ldc name'].astype(str) + " | " + temp_df['Lamp info'].astype(str)

                # Update zbioru unikalnymi wartościami
                new_lums = temp_df['key'].dropna().unique()
                lums.update(new_lums)

                # Subtelny log postępu dla każdego pliku
                # self.log(f"  ∟ {f_name}: znaleziono {len(new_lums)} modeli", "info")

            except Exception as e:
                self.log(f"Pominięto plik {f_name} przy skanowaniu: {e}", "warning")
                continue

        sorted_lums = sorted(list(lums))
        duration = time.time() - start_time

        self.log(
            f"Skanowanie zakończone w {duration:.2f}s. Znaleziono łącznie {len(sorted_lums)} unikalnych konfiguracji opraw.",
            "success")

        return sorted_lums

    def get_sample_data(self, n_rows=100):
        """Pobiera próbkę danych i loguje to do Twojej konsoli GUI"""
        import glob
        import os

        folders = [f for f in glob.glob(os.path.join(self.cache_dir, "*")) if os.path.isdir(f)]

        if not folders:
            # ZAMIAST print() -> używamy self.log()
            self.log("Błąd podglądu: Cache jest pusty.", "error")
            return None

        try:
            df = pd.read_parquet(folders[0])
            sample = df.head(n_rows)

            # TUTAJ BYŁ PROBLEM: Zmieniamy print na self.log
            self.log(f"Wyświetlono {len(sample)} wierszy w tabeli podglądu.", "success")

            return sample
        except Exception as e:
            self.log(f"Błąd podglądu: {e}", "error")
            return None

    def get_all_data(self):
        """Ładuje całą bazę cache do analiz statystycznych"""
        import glob
        all_files = glob.glob(os.path.join(self.cache_dir, "**", "*.parquet"), recursive=True)
        if not all_files:
            return pd.DataFrame()
        return pd.concat([pd.read_parquet(f) for f in all_files], ignore_index=True)

    def _filters_cache_key(self, filters):
        return tuple(sorted((k, str(v)) for k, v in (filters or {}).items()))

    def get_filtered_data(self, filters):
        """Pobiera i łączy dane z cache, stosując filtry z GUI"""
        import glob
        import os
        import pandas as pd
        try:
            import pyarrow.parquet as pq
        except Exception:
            pq = None

        cache_key = self._filters_cache_key(filters)
        if cache_key in self._filters_cache:
            return self._filters_cache[cache_key].copy()

        all_files = glob.glob(os.path.join(self.cache_dir, "**", "*.parquet"), recursive=True)

        # 1. Nie filtrujemy po nazwie folderu - Arrangement jest kolumną w danych
        filtered_files = all_files

        final_dfs = []
        for file in filtered_files:
            try:
                # Czytamy tylko potrzebne kolumny (oszczędność RAM)
                base_cols = {
                    'Arrangement', 'Road W[m]', 'De', 'Dp', 'Ldc name',
                    'Total flux [lm]', 'best_class', 'Delta [m]', 'Lph [m]', 'Tilt [°]'
                }
                schema_cols = None
                if pq is not None:
                    try:
                        schema_cols = pq.ParquetFile(file).schema.names
                    except Exception:
                        schema_cols = None

                selected_class = filters.get('Klasa oświetleniowa', "Wszystkie")
                if schema_cols:
                    if selected_class != "Wszystkie":
                        lav_cols = [f"Lav({selected_class})"]
                        lav_cols = [c for c in lav_cols if c in schema_cols]
                    else:
                        lav_cols = [c for c in schema_cols if 'Lav' in c]
                    cols_to_read = list(base_cols.union(lav_cols))
                    df = pd.read_parquet(file, columns=cols_to_read)
                else:
                    df = pd.read_parquet(file)

                # Downcast liczbowych kolumn, żeby ograniczyć zużycie pamięci
                for col in df.select_dtypes(include=['float64']).columns:
                    df[col] = pd.to_numeric(df[col], downcast='float')
                for col in df.select_dtypes(include=['int64']).columns:
                    df[col] = pd.to_numeric(df[col], downcast='integer')

                # --- FILTROWANIE KOLUMN ---

                # Układ (Arrangement)
                selected_arrangement = filters.get('Rozmieszczenie', "Wszystkie")
                if selected_arrangement != "Wszystkie":
                    df['Arrangement'] = df['Arrangement'].astype(str).str.strip()
                    df = df[df['Arrangement'] == selected_arrangement]

                # Oprawa (Ldc name)
                if filters.get('Nazwa oprawy') != "Wszystkie":
                    df = df[df['Ldc name'] == filters.get('Nazwa oprawy')]

                # Klasa oświetleniowa (mapujemy na 'best_class')
                if filters.get('Klasa oświetleniowa') != "Wszystkie":
                    df = df[df['best_class'] == filters.get('Klasa oświetleniowa')]

                # Parametry numeryczne (Szerokość, Rozstaw, Wysokość)
                # Używamy bezpiecznej konwersji, bo dane z Combobox to Stringi
                num_filters = {
                    'Szerekość drogi [m]': 'Road W[m]',
                    'Odstęp między oprawami [m]': 'Delta [m]',
                    'Wysokość montażu [m]': 'Lph [m]',
                    'Nachylenie (°)': 'Tilt [°]'
                }

                for nice_name, col_name in num_filters.items():
                    val = filters.get(nice_name)
                    if val and val != "Wszystkie":
                        try:
                            df = df[df[col_name] == float(val)]
                        except (ValueError, TypeError):
                            continue

                if not df.empty:
                    final_dfs.append(df)

            except Exception as e:
                self.log(f"Błąd filtrowania w pliku {file}: {e}", "error")

        if not final_dfs:
            self.log("Brak danych spełniających wybrane kryteria.", "warning")
            return pd.DataFrame()

        result = pd.concat(final_dfs, ignore_index=True)
        self._filters_cache[cache_key] = result
        self._filters_cache_order.append(cache_key)
        if len(self._filters_cache_order) > self._filters_cache_limit:
            old_key = self._filters_cache_order.pop(0)
            self._filters_cache.pop(old_key, None)
        return result.copy()

    def get_arrangement_comparison_data(self, filters, mode='efficiency'):
        """Agreguje dane do wykresów 1-3 bez ładowania całej bazy."""
        import glob
        import pandas as pd
        try:
            import pyarrow.parquet as pq
        except Exception:
            pq = None

        all_files = glob.glob(os.path.join(self.cache_dir, "**", "*.parquet"), recursive=True)
        if not all_files:
            return pd.DataFrame()

        base_cols = {'Arrangement', 'Road W[m]', 'Ldc name', 'best_class', 'Delta [m]', 'Lph [m]', 'Tilt [°]'}
        if mode in ('De', 'Dp'):
            base_cols.add(mode)
        base_cols.add('Total flux [lm]')

        selected_class = filters.get('Klasa oświetleniowa', "Wszystkie")
        grouped_chunks = []

        for file in all_files:
            try:
                schema_cols = None
                if pq is not None:
                    try:
                        schema_cols = pq.ParquetFile(file).schema.names
                    except Exception:
                        schema_cols = None

                if schema_cols:
                    if mode == 'efficiency':
                        if selected_class != "Wszystkie":
                            lav_cols = [f"Lav({selected_class})"]
                            lav_cols = [c for c in lav_cols if c in schema_cols]
                        else:
                            lav_cols = [c for c in schema_cols if 'Lav' in c]
                    else:
                        lav_cols = []
                    cols_to_read = list(base_cols.union(lav_cols))
                    df = pd.read_parquet(file, columns=cols_to_read)
                else:
                    df = pd.read_parquet(file)

                if df.empty:
                    continue

                # Filtry
                selected_arrangement = filters.get('Rozmieszczenie', "Wszystkie")
                if selected_arrangement != "Wszystkie":
                    df['Arrangement'] = df['Arrangement'].astype(str).str.strip()
                    df = df[df['Arrangement'] == selected_arrangement]

                if filters.get('Nazwa oprawy') != "Wszystkie":
                    df = df[df['Ldc name'] == filters.get('Nazwa oprawy')]

                if filters.get('Klasa oświetleniowa') != "Wszystkie":
                    df = df[df['best_class'] == filters.get('Klasa oświetleniowa')]

                num_filters = {
                    'Szerekość drogi [m]': 'Road W[m]',
                    'Odstęp między oprawami [m]': 'Delta [m]',
                    'Wysokość montażu [m]': 'Lph [m]',
                    'Nachylenie (°)': 'Tilt [°]'
                }
                for nice_name, col_name in num_filters.items():
                    val = filters.get(nice_name)
                    if val and val != "Wszystkie":
                        try:
                            df = df[df[col_name] == float(val)]
                        except (ValueError, TypeError):
                            continue

                if df.empty:
                    continue

                if mode == 'efficiency':
                    lav_cols = [c for c in df.columns if 'Lav' in c]
                    if not lav_cols:
                        continue
                    is_valid = (df[lav_cols].max(axis=1) >= 100).astype(int)
                    grouped = df.assign(is_valid=is_valid).groupby(
                        ['Arrangement', 'Road W[m]']
                    )['is_valid'].agg(['sum', 'count']).reset_index()
                else:
                    if mode not in df.columns:
                        continue
                    grouped = df.groupby(['Arrangement', 'Road W[m]'])[mode].agg(['sum', 'count']).reset_index()

                grouped = grouped.rename(columns={'sum': 'val_sum', 'count': 'val_count'})
                grouped_chunks.append(grouped)
            except Exception:
                continue

        if not grouped_chunks:
            return pd.DataFrame()

        combined = pd.concat(grouped_chunks, ignore_index=True)
        agg = combined.groupby(['Arrangement', 'Road W[m]'])[['val_sum', 'val_count']].sum().reset_index()

        if mode == 'efficiency':
            agg['value'] = (agg['val_sum'] / agg['val_count']) * 100.0
        else:
            agg['value'] = agg['val_sum'] / agg['val_count']

        return agg[['Arrangement', 'Road W[m]', 'value']]