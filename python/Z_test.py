import tkinter as tk

# --- KONFIGURACJA ---
BLACK = "#000000"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"

root = tk.Tk()
root.title("Panel Wyników - Układ Poziomy z Podpisami")
root.config(padx=20, pady=20, bg=YELLOW)

# 1. LISTA TYTUŁÓW DLA PRZYCISKÓW (16 nazw)
titles = [
    "M1 Oblicz", "M2 Analiza", "M3 Wyniki", "M4 Projekt",
    "M5 Rozstaw", "M6 Norma", "CSV Eksport", "PDF Druk",
    "M1 Raport", "M2 Wykres", "M3 Dane", "M4 Koszty",
    "M5 Moc", "M6 Klasa", "CSV Import", "ZAMKNIJ"
]

# 2. LISTA PODPISÓW DLA MENU (8 nazw)
menu_labels = [
    "Rozmieszczenie", "Oprawa", "Klasa oświetleniowa", "Szerokość drogi", "Moduł", "Wys. montażu", "Nawis", "Pochylenie"
]

# --- SEKCJA GÓRNA: 8 PODPISÓW + 8 LIST ROZWIJANYCH ---
top_frame = tk.Frame(root, bg=YELLOW)
top_frame.pack(side="top", fill="x", pady=(0, 20))

for c in range(8):
    # Kontener dla pojedynczego zestawu (Label + OptionMenu)
    m_container = tk.Frame(top_frame, bg=YELLOW)
    m_container.grid(row=0, column=c, padx=5, sticky="n")

    # Podpis nad menu
    label = tk.Label(
        m_container,
        text=menu_labels[c],
        bg=YELLOW,
        fg=BLACK,
        font=(FONT_NAME, 8, "bold")
    )
    label.pack()

    # Menu rozwijane
    v = tk.StringVar(root)
    v.set("Wybierz")
    opt = tk.OptionMenu(m_container, v, "Opcja 1", "Opcja 2", "Reset")
    opt.config(bg=PINK, font=(FONT_NAME, 8), width=10)
    opt.pack(pady=(2, 0))

# --- SEKCJA ŚRODKOWA: WIZUALIZACJA ---
mid_frame = tk.Frame(root, width=900, height=350, bg="white", highlightthickness=2, highlightbackground=RED)
mid_frame.pack(fill="both", expand=True, pady=10)
mid_frame.pack_propagate(False)

tk.Label(
    mid_frame,
    text="OBSZAR WIZUALIZACJI / WYKRESÓW",
    bg="white",
    font=(FONT_NAME, 16, "bold")
).pack(expand=True)

# --- SEKCJA DOLNA: SIATKA PRZYCISKÓW 2x8 ---
bottom_frame = tk.Frame(root, bg=YELLOW)
bottom_frame.pack(side="bottom", fill="x", pady=(10, 0))

# Konfiguracja kolumn, aby przyciski były równe i wypełniały szerokość
for i in range(8):
    bottom_frame.grid_columnconfigure(i, weight=1)

for i in range(16):
    row = 0 if i < 8 else 1  # 0-7 wiersz górny, 8-15 wiersz dolny
    col = i % 8

    btn = tk.Button(
        bottom_frame,
        text=titles[i],
        bg=GREEN,
        font=(FONT_NAME, 8, "bold"),
        height=2
    )
    btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

root.mainloop()