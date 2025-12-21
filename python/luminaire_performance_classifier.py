import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import messagebox, ttk

# --- KONFIGURACJA ŚCIEŻEK ---
base_path = os.path.dirname(__file__)
# Ścieżka zakłada, że skrypt jest w folderze obok folderu 'relux'
input_file = os.path.join(base_path, '..', 'relux', 'relux_calc', 'wycinek_100k_rows.csv')

class LuminaireApp:
    def __init__(self, root):
        """🏗️ Inicjalizacja aplikacji i bazy norm oświetleniowych"""
        self.root = root
        self.root.title("Analizator Opraw Oświetleniowych v1.4")
        self.root.geometry("450x600")
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

        tk.Label(root, text="Wybierz klasę oświetleniową (do filtrów):").pack()
        self.class_var = tk.StringVar(value="M3")
        self.class_combo = ttk.Combobox(root, textvariable=self.class_var, 
                                        values=["M1", "M2", "M3", "M4", "M5", "M6"], state="readonly", width=15)
        self.class_combo.pack(pady=5)

        tk.Label(root, text="Wybierz model oprawy:").pack()
        self.brand_var = tk.StringVar(value="Wszystkie")
        self.brand_combo = ttk.Combobox(root, textvariable=self.brand_var, state="disabled", width=45)
        self.brand_combo.pack(pady=5)

        # Przyciski wykresów
        self.btn_p1 = tk.Button(root, text="📊 Wykres Skuteczności (Wszystkie Klasy)", command=self.plot_parameters, state=tk.DISABLED, width=35)
        self.btn_p1.pack(pady=2)

        self.btn_p2 = tk.Button(root, text="📈 Bilans Strumienia dla wybranej Klasy", command=self.plot_flux_balance, state=tk.DISABLED, width=35)
        self.btn_p2.pack(pady=2)

        self.btn_p3 = tk.Button(root, text="🔥 Analiza Restrykcyjności Parametrów", command=self.plot_restriction_analysis, 
                                state=tk.DISABLED, width=35, bg="#2c3e50", fg="white")
        self.btn_p3.pack(pady=2)

        self.status_label = tk.Label(root, text="Status: Czekam na dane", fg="#e67e22")
        self.status_label.pack(side=tk.BOTTOM, pady=20)

    def load_data(self):
        """📥 Wczytywanie i czyszczenie danych"""
        try:
            self.df = pd.read_csv(input_file, sep=';', encoding='cp1250', decimal=',', low_memory=False)
            self.df.columns = self.df.columns.str.strip()
            
            # Konwersja na liczby
            num_cols = ['Lav [cd/m2]', 'Uo (L)', 'Ul', 'TI [%]', 'Rei', 'Total flux [lm]']
            for col in num_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

            # Wypełnienie listy opraw
            lums = ["Wszystkie"] + sorted(self.df['Ldc name'].dropna().unique().tolist())
            self.brand_combo.config(values=lums, state="readonly")
            
            # Aktywacja przycisków
            self.btn_p1.config(state=tk.NORMAL)
            self.btn_p2.config(state=tk.NORMAL)
            self.btn_p3.config(state=tk.NORMAL)
            self.brand_combo.config(state="readonly")
            
            self.status_label.config(text="Status: Dane gotowe", fg="green")
            messagebox.showinfo("Sukces", "Dane wczytane pomyślnie!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku lub błąd formatu: {e}")

    def get_filtered_df(self):
        """Filtracja danych po modelu oprawy"""
        selected = self.brand_var.get()
        if selected == "Wszystkie":
            return self.df
        return self.df[self.df['Ldc name'] == selected]

    def plot_parameters(self):
        """📊 Pokazuje jaki % scenariuszy dana oprawa spełnia dla każdej klasy"""
        d = self.get_filtered_df()
        results = []

        for _, row in self.std.iterrows():
            klasa = row['Klasa']
            mask = (
                (d['Lav [cd/m2]'] >= row['Lav [cd/m2]']) &
                (d['Uo (L)'] >= row['Uo (L)']) &
                (d['Ul'] >= row['Ul']) &
                (d['TI [%]'] <= row['TI [%]']) &
                (d['Rei'] >= row['Rei'])
            )
            success_rate = mask.mean() * 100
            results.append({'Klasa': klasa, 'Skuteczność [%]': success_rate})

        plt.figure(figsize=(10, 6))
        sns.barplot(data=pd.DataFrame(results), x='Klasa', y='Skuteczność [%]', palette="viridis")
        plt.title(f"Uniwersalność oprawy: {self.brand_var.get()}")
        plt.ylim(0, 105)
        plt.show()

    def plot_flux_balance(self):
        """📈 Histogram pokazujący rozkład strumienia dla projektów udanych vs nieudanych"""
        klasa = self.class_var.get()
        norma = self.std[self.std['Klasa'] == klasa].iloc[0]
        d = self.get_filtered_df().copy()

        d['Spełnia normę'] = (
            (d['Lav [cd/m2]'] >= norma['Lav [cd/m2]']) &
            (d['Uo (L)'] >= norma['Uo (L)']) &
            (d['Ul'] >= norma['Ul']) &
            (d['TI [%]'] <= norma['TI [%]']) &
            (d['Rei'] >= norma['Rei'])
        )

        plt.figure(figsize=(10, 6))
        sns.histplot(data=d, x='Total flux [lm]', hue='Spełnia normę', multiple="stack", bins=20, palette="Set1")
        plt.title(f"Bilans strumienia dla klasy {klasa} (Model: {self.brand_var.get()})")
        plt.show()

    def plot_restriction_analysis(self):
        """🔥 Analiza 'wąskich gardeł' - który parametr najczęściej powoduje odrzucenie projektu"""
        klasa = self.class_var.get()
        norma = self.std[self.std['Klasa'] == klasa].iloc[0]
        d = self.get_filtered_df()

        # Liczymy ile % razy dany parametr został spełniony izolowanie
        stats = {
            'Luminancja (Lav)': (d['Lav [cd/m2]'] >= norma['Lav [cd/m2]']).mean() * 100,
            'Równomierność (Uo)': (d['Uo (L)'] >= norma['Uo (L)']).mean() * 100,
            'Równ. wzdłużna (Ul)': (d['Ul'] >= norma['Ul']).mean() * 100,
            'Olśnienie (TI)': (d['TI [%]'] <= norma['TI [%]']).mean() * 100,
            'Otoczenie (Rei)': (d['Rei'] >= norma['Rei']).mean() * 100
        }

        plt.figure(figsize=(12, 6))
        plt.barh(list(stats.keys()), list(stats.values()), color='salmon')
        plt.axvline(100, color='red', linestyle='--')
        plt.title(f"Analiza restrykcyjności parametrów dla klasy {klasa}\n(Wartości bliższe 0% to główne przyczyny odrzucenia)")
        plt.xlabel("Stopień spełnienia kryterium [%]")
        plt.xlim(0, 110)
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = LuminaireApp(root)
    root.mainloop()