import os
import csv
import pandas as pd


def otvor_csv_subor(cesta_k_suboru):
    try:
        with open(cesta_k_suboru, 'r') as subor:
            return pd.read_csv(subor)
    except FileNotFoundError:
        print(f"Súbor na ceste {cesta_k_suboru} neexistuje.")
        return None
    except Exception as e:
        print(f"Chyba pri otváraní súboru: {e}")
        return None


def vytvor_tabulku_uspesnosti(dataframe):
    if dataframe is not None:
        try:
            # Filtruj data pre vekové kategórie 0-5 a 6-10
            dataframe.columns = dataframe.columns.str.strip()

            dataframe['clinical_gravidity'] = pd.to_numeric(dataframe['clinical_gravidity'], errors='coerce')
            dataframe['vek_mother'] = pd.to_numeric(dataframe['vek_mother'], errors='coerce')


            df_filtr = dataframe[
                (dataframe['vek_mother'] >= 0) & (dataframe['vek_mother'] <= 29) | (dataframe['vek_mother'] >= 30) & (dataframe['vek_mother'] <= 34)]

            # Vytvor tabuľku úspešnosti procesu podľa sloupca "gravidity"
            tabulka_uspesnosti = pd.pivot_table(df_filtr, index='vek_mother', columns='clinical_gravidity', values='úspěšnosti_embryotransferu ',
                                                aggfunc='mean')

            # Vypíš tabuľku úspešnosti procesu
            print(tabulka_uspesnosti)
        except Exception as e:
            print(f"Chyba pri vytváraní tabuľky úspešnosti procesu: {e}")


if __name__ == "__main__":
    cesta_k_suboru = input("Zadaj cestu k .csv súboru: ")
    data = otvor_csv_subor(cesta_k_suboru)
    vytvor_tabulku_uspesnosti(data)
