import pandas as pd

from Config import BRONZE, OURO, PRATA

producao_industria = pd.read_csv(
    PRATA / "producao_industria_2012_2025_tratada.csv",
    encoding="utf-8-sig"
)

consumo_industrial = pd.read_excel(
    BRONZE / "Dados_abertos_Consumo_Mensal.xlsx",
    sheet_name="SETOR INDUSTRIAL POR RG"
)

producao_industria["Data"] = pd.to_datetime(
    producao_industria["Data"],
    errors="coerce"
)

consumo_industrial["DataExcel"] = pd.to_datetime(
    consumo_industrial["DataExcel"],
    errors="coerce"
)


# Criar a chave de atividade na produção
producao_industria["ChaveAtividade"] = (
    producao_industria["Atividade"]
    .str.extract(r"^3\.(\d+)")
    .astype("Int64")
)

# Criar a chave de atividade no consumo
consumo_industrial["ChaveAtividade"] = (
    consumo_industrial["SetorIndustrial"]
    .str.extract(r"^(\d+)")
    .astype("Int64")
)

chaves_prod = set(
    producao_industria["ChaveAtividade"].dropna()
)

chaves_cons = set(
    consumo_industrial["ChaveAtividade"].dropna()
)

print("Só na produção:", chaves_prod - chaves_cons)
print("Só no consumo:", chaves_cons - chaves_prod)
print("Nos dois:", chaves_prod & chaves_cons)

consumo_industrial = consumo_industrial[
    (consumo_industrial["DataExcel"].dt.year >= 2012) &
    (consumo_industrial["DataExcel"].dt.year <= 2025) &
    (consumo_industrial["DataExcel"].dt.year != 2020)
].copy()

# Somar o consumo das regiões
consumo_setor_mensal = (
    consumo_industrial
    .groupby(
        ["DataExcel", "ChaveAtividade"],
        as_index=False
    )["Consumo"]
    .sum()
)

producao_industria = producao_industria.sort_values(
    ["Atividade", "Data"]
)

producao_industria["VariacaoPctProducao"] = (
    producao_industria
    .groupby("Atividade")["Valor"]
    .pct_change(fill_method=None) * 100
)

# Verificar continuidade mensal da produção
mes_producao = (
    producao_industria["Data"].dt.year * 12
    + producao_industria["Data"].dt.month
)

intervalo_producao = (
    mes_producao.groupby(producao_industria["Atividade"])
    .diff()
)

producao_industria["VariacaoPctProducao"] = (
    producao_industria["VariacaoPctProducao"]
    .where(intervalo_producao == 1)
)

consumo_setor_mensal = consumo_setor_mensal.sort_values(
    ["ChaveAtividade", "DataExcel"]
)

consumo_setor_mensal["VariacaoPctConsumo"] = (
    consumo_setor_mensal
    .groupby("ChaveAtividade")["Consumo"]
    .pct_change(fill_method=None) * 100
)

# Verificar continuidade mensal do consumo
mes_consumo = (
    consumo_setor_mensal["DataExcel"].dt.year * 12
    + consumo_setor_mensal["DataExcel"].dt.month
)

intervalo_consumo = (
    mes_consumo.groupby(
        consumo_setor_mensal["ChaveAtividade"]
    ).diff()
)

consumo_setor_mensal["VariacaoPctConsumo"] = (
    consumo_setor_mensal["VariacaoPctConsumo"]
    .where(intervalo_consumo == 1)
)

resultado = producao_industria.merge(
    consumo_setor_mensal[
        [
            "DataExcel",
            "ChaveAtividade",
            "Consumo",
            "VariacaoPctConsumo"
        ]
    ],
    left_on=["Data", "ChaveAtividade"],
    right_on=["DataExcel", "ChaveAtividade"],
    how="left",
    validate="many_to_one"
)

print("Produção:", len(producao_industria))
print("Resultado:", len(resultado))

sem_par = resultado["Consumo"].isna()

print("Sem correspondência:", int(sem_par.sum()))

print("\nAtividades sem correspondência:")
print(
    resultado.loc[sem_par, "Atividade"]
    .value_counts()
)

print("\nRegistros com correspondência:",
      int(resultado["Consumo"].notna().sum()))

resultado["DiferencaVariacaoPct"] = (
    resultado["VariacaoPctProducao"]
    - resultado["VariacaoPctConsumo"]
)

OURO.mkdir(parents=True, exist_ok=True)
arquivo_resultado = OURO / "producao_industria_enriquecida.parquet"
resultado.to_parquet(arquivo_resultado, index=False)
print("Resultado salvo em:", arquivo_resultado)

print("\nValidação do atributo derivado:")

print(
    "Diferenças calculadas:",
    resultado["DiferencaVariacaoPct"].notna().sum()
)

print(
    "Diferenças ausentes:",
    resultado["DiferencaVariacaoPct"].isna().sum()
)

print(
    "Diferenças ausentes entre registros correspondentes:",
    resultado.loc[
        resultado["Consumo"].notna(),
        "DiferencaVariacaoPct"
    ].isna().sum()
)

print(
    consumo_setor_mensal.duplicated(
        ["DataExcel", "ChaveAtividade"]
    ).sum()
)

print(
    resultado.loc[
        resultado["Consumo"].notna()
        & resultado["DiferencaVariacaoPct"].isna(),
        ["Data", "Atividade"]
    ].groupby("Atividade").size()
)

