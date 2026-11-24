
import pandas as pd

from Config import BRONZE, PRATA


# ============================================================
# 1. CAMINHOS DOS ARQUIVOS
# ============================================================

arquivo_bronze = BRONZE / "Dados_abertos_Consumo_Mensal.xlsx"
arquivo_silver = PRATA / "consumo_industrial_tratado.csv"

# Cria a pasta Silver caso ela ainda não exista
arquivo_silver.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA DO ARQUIVO ORIGINAL
# ============================================================

dados = pd.read_excel(
    arquivo_bronze,
    sheet_name="SETOR INDUSTRIAL POR RG"
)


# ============================================================
# 3. SELEÇÃO E PADRONIZAÇÃO DAS COLUNAS
# ============================================================

dados = dados[
    [
        "DataExcel",
        "SetorIndustrial",
        "Regiao",
        "Consumo"
    ]
].copy()

dados = dados.rename(
    columns={
        "DataExcel": "Data"
    }
)


# ============================================================
# 4. GARANTIR OS TIPOS DOS DADOS
# ============================================================

dados["Data"] = pd.to_datetime(
    dados["Data"],
    errors="coerce"
)

dados["Consumo"] = pd.to_numeric(
    dados["Consumo"],
    errors="coerce"
)


# ============================================================
# 5. AGREGAR O CONSUMO POR SETOR E DATA
# ============================================================

dados = dados.groupby(
    [
        "Data",
        "SetorIndustrial"
    ],
    as_index=False
).agg(
    Consumo=("Consumo", "sum"),
    RegioesRegistradas=("Regiao", "nunique")
)


# ============================================================
# 6. SEPARAR MÊS E ANO
# ============================================================

dados["Ano"] = (
    dados["Data"]
    .dt.year
)

dados["Mes"] = (
    dados["Data"]
    .dt.month
)


# ============================================================
# 7. ORGANIZAR AS COLUNAS
# ============================================================

dados = dados[
    [
        "Data",
        "Ano",
        "Mes",
        "SetorIndustrial",
        "Consumo",
        "RegioesRegistradas"
    ]
]


# ============================================================
# 8. ORDENAR OS DADOS
# ============================================================

dados = dados.sort_values(
    by=[
        "Data",
        "SetorIndustrial"
    ]
).reset_index(
    drop=True
)


# ============================================================
# 9. SALVAR NA CAMADA SILVER
# ============================================================

dados.to_csv(
    arquivo_silver,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. MOSTRAR RESULTADO
# ============================================================

print("Tratamento concluído.")

print(
    f"Arquivo original: {arquivo_bronze}"
)

print(
    f"Arquivo tratado: {arquivo_silver}"
)

print(
    f"Quantidade de registros: {len(dados):,}"
)

print(
    f"Quantidade de colunas: {len(dados.columns)}"
)

print()

print("Período:")

print(
    f"{dados['Data'].min()} "
    f"até "
    f"{dados['Data'].max()}"
)

print()

print(
    "Quantidade de setores:",
    dados["SetorIndustrial"].nunique()
)

print()

print("Regiões registradas por combinação:")

print(
    dados["RegioesRegistradas"]
    .value_counts()
    .sort_index()
)

print()

print("Primeiros registros:")

print(
    dados.head(10).to_string(
        index=False
    )
)
