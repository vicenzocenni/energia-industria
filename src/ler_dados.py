import pandas as pd
from Config import BRONZE

def carregar():
    df_excel = pd.read_excel(CAMINHO2, decimal=",")
    df_csv = pd.read_csv(CAMINHO, sep=";", decimal=",", skiprows=4)
    return df_csv, df_excel

def conferir_estrutura(df):
    print(df.shape)
    print(df.dtypes)

CAMINHO = BRONZE / "producao_industria_2012_2025.csv"
CAMINHO2 = BRONZE / "Dados_abertos_Consumo_Mensal.xlsx"

if __name__ == "__main__":
    df_csv, df_excel = carregar()
    conferir_estrutura(df_csv)
    conferir_estrutura(df_excel)