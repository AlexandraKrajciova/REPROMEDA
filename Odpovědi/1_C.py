# -*- coding: utf-8 -*-
"""C_vysledek.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-UjhtCpTg9CuZuVirvN0jjnUA1Ad2XP0
"""

import pandas as pd
from scipy.stats import ttest_ind, mannwhitneyu, shapiro, levene


root_dir = "/content/drive/MyDrive/"
base_dir = root_dir + "Colab Notebooks/"

data_path = base_dir + "REPROMEDA/transfery.csv"
print(data_path)
data = pd.read_csv(data_path)


# Vytvorenie stlpca pre vekove kategorie
bins = [0, 29, 34, 39, float('inf')]
data['vek_embryo'] = pd.to_numeric(data['vek_embryo'], errors='coerce')
labels = ['do 29', '30-34', '35-39', '40 a výše']
data['vek_kategorie'] = pd.cut(data['vek_embryo'], bins=bins, labels=labels, right=False)

# Vylucenie merani "f_donor" = 1 a nan
df_filtr = data[data['f_donor'] != 1].dropna(subset=['vek_embryo', 'clinical_gravidity'])

# Vytvoření tabulky úspěšnosti podle věkových skupin
tabulka_uspesnosti = df_filtr.groupby(['vek_kategorie', 'clinical_gravidity']).size().unstack().div(
    df_filtr.groupby('vek_kategorie').size(), axis=0) * 100

# Pridanie riadku pre vsetky vekove kategorie
tabulka_uspesnosti.loc['všechny věkové kategorie'] = df_filtr.groupby('clinical_gravidity').size() / len(df_filtr) * 100

# Preusporiadanie riadkov
tabulka_uspesnosti = tabulka_uspesnosti.reindex(['všechny věkové kategorie'] + labels)

# Premenovanie riadkov a stlpcov
tabulka_uspesnosti.columns = ['Neúspěch', 'Úspěch']
tabulka_uspesnosti.index.name = 'Věková skupina'

# Tabulka uspesnosti
print(tabulka_uspesnosti)

# Tabulky s hodnotami uspesnosti embryotransferu pre jednotlive vekove kategorie
tabulka_uspesnost_kategorie = tabulka_uspesnosti[['Úspěch']].transpose()
tabulka_uspesnost_kategorie.columns.name = 'Věková skupina'
print(tabulka_uspesnost_kategorie)


# Odstranenie prazdnych hodnot
data = data.dropna(subset=['vek_embryo', 'clinical_gravidity'])

# Rozdelenie dat do dvoch skupin podla hodnot 'clinical_gravidity'
group_0 = data[data['clinical_gravidity'] == 0]['vek_embryo']
group_1 = data[data['clinical_gravidity'] == 1]['vek_embryo']

# Overenie predpokladu normalneho rozdelenia
statistic_0, p_value_0 = shapiro(group_0)
statistic_1, p_value_1 = shapiro(group_1)

# Overenie predpokladu homogenity variancii
statistic_levene, p_value_levene = levene(group_0, group_1)

# Nastavenie hladiny vyznamnosti
alpha = 0.05

# Kontrola
if p_value_0 > alpha and p_value_1 > alpha and p_value_levene > alpha:
    # Použití t-testu
    statistic, p_value = ttest_ind(group_0, group_1)
    print("T-test:")
else:
    # Použitie Mann-Whitneyho testu
    statistic, p_value = mannwhitneyu(group_0, group_1)
    print("Mann-Whitneyho test:")

# Kontrola zamietnutia alebo prijatia nulovej hypotézy pre obe metody
if p_value < alpha:
    print("Nulová hypotéza sa zamietla na hladine významnosti", alpha)
    print("Existuje štatisticky významný rozdiel vo veku embryí medzi dvoma skupinami.")
else:
    print("Nulová hypotéza sa neprijíma na hladine významnosti", alpha)
    print("Rozdiel vo veku embryí medzi skupinami nie je štatisticky významný.")