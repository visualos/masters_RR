import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('./data/MastersCalc.2lanes_SGL.street.batch.csv', sep=';', engine='python', encoding='cp1250')

# 1. Wyłącz zawijanie kolumn (szerokość ustawiona na bardzo dużą wartość)
pd.set_option('display.width', 2000)

# 2. Upewnij się, że wyświetlane są wszystkie kolumny
pd.set_option('display.max_columns', None)

# 3. Opcjonalnie: wyłącz skracanie tekstu wewnątrz komórek
pd.set_option('display.max_colwidth', None)

# Wyświetl pierwszy wiersz
print(df.iloc[[0]])