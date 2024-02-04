# -*- coding: utf-8 -*-
"""bonus.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Oe3hyvVEqfhUAAnR-LwiSldrnJQUD96A
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import ttest_ind, mannwhitneyu, shapiro, levene
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# Načítanie dát
root_dir = "/content/drive/MyDrive/"
base_dir = root_dir + "Colab Notebooks/"
data_path = base_dir + "REPROMEDA/transfery.csv"
data = pd.read_csv(data_path)

# Vytvorenie stĺpca pre vekové kategórie matiek
bins = [0, 29, 34, 39, float('inf')]
data['vek_mother'] = pd.to_numeric(data['vek_mother'], errors='coerce')
labels = ['do 29', '30-34', '35-39', '40 a výše']
data['vek_kategorie'] = pd.cut(data['vek_mother'], bins=bins, labels=labels, right=False)

# Odstránenie NaN hodnôt
df_filtr_mother = data.dropna(subset=['vek_mother', 'clinical_gravidity'])

# Vytvorenie tabuľky úspešnosti v %
tabulka_uspesnosti_mother = df_filtr_mother.groupby(['vek_kategorie', 'clinical_gravidity']).size().unstack().div(
    df_filtr_mother.groupby('vek_kategorie').size(), axis=0) * 100

# Pridanie riadku pre všetky vekové kategórie
tabulka_uspesnosti_mother.loc['všechny věkové kategorie'] = df_filtr_mother.groupby('clinical_gravidity').size() / len(df_filtr_mother) * 100

# Preusporiadanie
tabulka_uspesnosti_mother = tabulka_uspesnosti_mother.reindex(['všechny věkové kategorie'] + labels)

# Premenovanie riadkov a stĺpcov
tabulka_uspesnosti_mother.columns = ['Neúspěch', 'Úspěch']
tabulka_uspesnosti_mother.index.name = 'Věková skupina matiek'

# Vytvorenie stĺpca pre vekové kategórie embryí
bins_embryo = [0, 29, 34, 39, float('inf')]
data['vek_embryo'] = pd.to_numeric(data['vek_embryo'], errors='coerce')
labels_embryo = ['do 29', '30-34', '35-39', '40 a výše']
data['vek_kategorie_embryo'] = pd.cut(data['vek_embryo'], bins=bins_embryo, labels=labels_embryo, right=False)

# Odstránenie meraní "f_donor" = 1 a NaN
df_filtr_embryo = data[data['f_donor'] != 1].dropna(subset=['vek_embryo', 'clinical_gravidity'])

# Vytvorenie tabuľky úspešnosti v %
tabulka_uspesnosti_embryo = df_filtr_embryo.groupby(['vek_kategorie_embryo', 'clinical_gravidity']).size().unstack().div(
    df_filtr_embryo.groupby('vek_kategorie_embryo').size(), axis=0) * 100

# Pridanie riadku pre všetky vekové kategórie
tabulka_uspesnosti_embryo.loc['všechny věkové kategorie'] = df_filtr_embryo.groupby('clinical_gravidity').size() / len(df_filtr_embryo) * 100

# Preusporiadanie
tabulka_uspesnosti_embryo = tabulka_uspesnosti_embryo.reindex(['všechny věkové kategorie'] + labels_embryo)

# Premenovanie riadkov a stĺpcov
tabulka_uspesnosti_embryo.columns = ['Neúspěch', 'Úspěch']
tabulka_uspesnosti_embryo.index.name = 'Věková skupina embryí'

# Vytvorenie skupin pre stlpec "genetic_method"
skupiny = {
    'PGT-A': ['PGT-A'],
    'PGT-SR': ['PGT-SR'],
    'Karyomapping': ['Karyomapping'],
    'OneGene': ['OneGene']
}

# Vytvorenie noveho sloupce s názvem "skupina_genetic_method"
data['skupina_genetic_method'] = None

# Priradenie hodnot do noveho sloupce podle skupin
for skupina, hodnoty in skupiny.items():
    mask = data['genetic_method'].isin(hodnoty)
    data.loc[mask, 'skupina_genetic_method'] = skupina

# Identifikace hodnot pro skupinu 'Ostatni'
hodnoty_ostatni = set(data['genetic_method'].unique()) - set([hodnota for hodnoty in skupiny.values() for hodnota in hodnoty])

# Vytvoreni skupiny 'Ostatní'
data.loc[data['genetic_method'].isin(hodnoty_ostatni), 'skupina_genetic_method'] = 'Ostatní'

# Vytvoreni skupiny 'Prázdné hodnoty' pro NaN hodnoty
data.loc[data['genetic_method'].isna(), 'skupina_genetic_method'] = 'Prázdné hodnoty'

# Serazeni sloupcu podle pozadavku
poradi_sloupcu = ['PGT-A', 'PGT-SR', 'Karyomapping', 'OneGene', 'Prázdné hodnoty', 'Ostatní']
tabulka_skupiny_genetic_method = data['skupina_genetic_method'].value_counts().reindex(poradi_sloupcu).reset_index()
tabulka_skupiny_genetic_method.columns = ['skupina_genetic_method', 'Počet']

# Pridani radku s sumou vsech hodnot ve sloupci "Počet"
tabulka_skupiny_genetic_method.loc['Suma'] = tabulka_skupiny_genetic_method['Počet'].sum()

# Transpozice tabulky
tabulka_skupiny_genetic_method_transponovana = tabulka_skupiny_genetic_method.set_index('skupina_genetic_method').transpose()

# Výpis transponovane tabulky
print(tabulka_skupiny_genetic_method_transponovana)

# Vylucenie nan
data = data.dropna(subset=['vek_mother', 'clinical_gravidity'])

# rozdelenie dat podle pohlavi
group_0 = data[data['sex'] == 'XX']['clinical_gravidity']
group_1 = data[data['sex'] == 'XY']['clinical_gravidity']

# Overenie predpokladu normalniho rozdeleni
statistic_0, p_value_0 = shapiro(group_0)
statistic_1, p_value_1 = shapiro(group_1)

# Overenie predpokladu homogenity varianci
statistic_levene, p_value_levene = levene(group_0, group_1)

# Nastaveni hladiny vyznamnosti
alpha = 0.05

# Kontrola
if p_value_0 > alpha and p_value_1 > alpha and p_value_levene > alpha:
    # Použití t-testu
    statistic, p_value = ttest_ind(group_0, group_1)
    print("T-test:")
else:
    # Pouziti Mann-Whitneyho testu
    statistic, p_value = mannwhitneyu(group_0, group_1, alternative='two-sided')
    print("Mann-Whitneyho test:")

# Kontrola zamitnuti nebo prijeti nulove hypotezy pro obe metody
if p_value < alpha:
    print("Nulová hypotéza se zamítá na hladině významnosti", alpha)
    print("Existuje statisticky významný rozdíl v úspěchu transferů mezi pohlavím XX a XY.")
else:
    print("Nulová hypotéza se nepřijímá na hladině významnosti", alpha)
    print("Rozdíl v úspěchu transferů mezi pohlavím XX a XY není statisticky významný.")

# Vytvorenie Dash aplikácie
app = dash.Dash(__name__)

# Layout aplikácie
app.layout = html.Div([
    dcc.Graph(
        id='success-failure-bar-chart-mother',
        figure=px.bar(tabulka_uspesnosti_mother, x=tabulka_uspesnosti_mother.index, y=['Neúspěch', 'Úspěch'],
                      labels={'Neúspěch': 'Neúspěch (%)', 'Úspěch': 'Úspěch (%)'},
                      title='Tabuľka úspešnosti podľa vekovej kategórie matiek'
                      )
    ),

    dcc.Graph(
        id='success-failure-bar-chart-embryo',
        figure=px.bar(tabulka_uspesnosti_embryo, x=tabulka_uspesnosti_embryo.index, y=['Neúspěch', 'Úspěch'],
                      labels={'Neúspěch': 'Neúspěch (%)', 'Úspěch': 'Úspěch (%)'},
                      title='Tabuľka úspešnosti podľa vekovej kategórie embryí'
                      )
    ),

    html.Div([
        dcc.Dropdown(
            id='feature-dropdown',
            options=[
                {'label': 'Veková skupina matiek', 'value': 'vek_kategorie'},
                {'label': 'Veková skupina embryí', 'value': 'vek_kategorie_embryo'}
            ],
            value='vek_kategorie',
            style={'width': '50%'}
        ),
        dcc.Graph(
            id='box-plot',
            figure={}
        ),
        html.P(id='result-text', style={'margin-top': '20px'})
    ]),

    dcc.Graph(
        id='genetic-method-count-bar-chart',
        figure=px.bar(tabulka_skupiny_genetic_method, x='skupina_genetic_method', y='Počet',
                      labels={'Počet': 'Počet záznamov', 'skupina_genetic_method': 'Genetická metoda'},
                      title='Počet záznamov podľa genetických metód'
                      )
    ),

    html.P(id='genetic-method-text', style={'margin-top': '20px'})
])

# Callback pre aktualizáciu box plotu a výsledku testu
@app.callback(
    [Output('box-plot', 'figure'),
     Output('result-text', 'children')],
    [Input('feature-dropdown', 'value')]
)
def update_box_plot(selected_feature):
    if selected_feature is None:
        raise PreventUpdate

    # Rozdelenie dat do dvoch skupin podľa vybratej vlastnosti
    group_0 = df_filtr_embryo[df_filtr_embryo[selected_feature] == labels_embryo[0]]['vek_embryo']
    group_1 = df_filtr_embryo[df_filtr_embryo[selected_feature] == labels_embryo[1]]['vek_embryo']

    # Overenie predpokladu normálneho rozdelenia
    statistic_0, p_value_0 = shapiro(group_0)
    statistic_1, p_value_1 = shapiro(group_1)

    # Overenie predpokladu homogenity variancii
    statistic_levene, p_value_levene = levene(group_0, group_1)

    # Nastavenie hladiny významnosti
    alpha = 0.05

    # Kontrola
    if p_value_0 > alpha and p_value_1 > alpha and p_value_levene > alpha:
        # Použití t-testu
        statistic, p_value = ttest_ind(group_0, group_1)
        test_type = "T-test"
    else:
        # Použití Mann-Whitneyho testu
        statistic, p_value = mannwhitneyu(group_0, group_1, alternative='two-sided')
        test_type = "Mann-Whitneyho test"

    # Vytvorenie box plotu
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Group 1', 'Group 2'])
    fig.add_trace(go.Box(y=group_0, name='Group 1'), row=1, col=1)
    fig.add_trace(go.Box(y=group_1, name='Group 2'), row=1, col=2)

    # Vytvorenie výsledku testu
    result_text = f"{test_type} Result:\n"
    result_text += f"Statistic: {statistic:.4f}\n"
    result_text += f"P-value: {p_value:.4f}\n"

    # Kontrola zamietnutia alebo prijatia nulovej hypotézy pre obe metody
    if p_value < alpha:
        result_text += f"Nulová hypotéza sa zamietla na hladine významnosti {alpha}\n"
        result_text += "Existuje štatisticky významný rozdiel vo veku embryí medzi dvoma skupinami."
    else:
        result_text += f"Nulová hypotéza sa neprijíma na hladine významnosti {alpha}\n"
        result_text += "Rozdiel vo veku embryí medzi skupinami nie je štatisticky významný."

    return fig, result_text

# Callback pre aktualizáciu textu o genetických metódach
@app.callback(
    [Output('genetic-method-count-bar-chart', 'figure'),
     Output('genetic-method-text', 'children')],
    [Input('genetic-method-count-bar-chart', 'selectedData')]
)
def update_genetic_method_text(selected_data):
    if selected_data is None:
        raise PreventUpdate

    # Získanie označených hodnôt zo selektovaných dát
    selected_values = [point['x'] for point in selected_data['points']]

    # Vytvorenie textu
    text = f"Počet záznamov pre jednotlivé genetické metódy:\n"
    for value in selected_values:
        count = tabulka_skupiny_genetic_method.loc[tabulka_skupiny_genetic_method['skupina_genetic_method'] == value, 'Počet'].values[0]
        text += f"{value}: {count}\n"

    # Vytvorenie vylepšeného sloupcového grafu
    updated_fig = px.bar(tabulka_skupiny_genetic_method, x='skupina_genetic_method', y='Počet',
                         labels={'Počet': 'Počet záznamov', 'skupina_genetic_method': 'Genetická metoda'},
                         title='Počet záznamov podľa genetických metód'
                         )
    updated_fig.update_traces(marker_color='rgba(0, 0, 255, 0.5)', marker_line_color='rgb(0, 0, 0)', marker_line_width=1.5)

    return updated_fig, text

# Spustenie aplikácie
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)

