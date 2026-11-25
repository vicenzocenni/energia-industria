import pandas as pd
import streamlit as st
import consultas


# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Produção Industrial e Energia",
    layout="wide"
)

st.title("Produção Industrial e Consumo de Energia")
st.write(
    "Explore a relação entre a produção industrial "
    "e o consumo de energia elétrica."
)


# ============================================================
# 2. FILTROS LATERAIS
# ============================================================

anos_disponiveis = consultas.anos()["ano"].astype(int).tolist()

atividades_disponiveis = (
    consultas.atividades_com_consumo()["atividade"].tolist()
)

if not anos_disponiveis or not atividades_disponiveis:
    st.error("Não existem dados disponíveis para consulta.")
    st.stop()

st.sidebar.header("Filtros")

ano = st.sidebar.selectbox(
    "Ano",
    anos_disponiveis,
    index=len(anos_disponiveis) - 1
)

atividade = st.sidebar.selectbox(
    "Atividade industrial",
    atividades_disponiveis
)


# ============================================================
# 3. BUSCAR OS DADOS
# ============================================================

dados = consultas.indicador_por_atividade(
    atividade,
    int(ano)
)

dados = dados.sort_values("data")

if dados.empty:
    st.warning("Não foram encontrados registros para os filtros selecionados.")
    st.stop()


# ============================================================
# 4. INDICADORES RESUMIDOS
# ============================================================

def ultimo_valor(df, coluna):
    """
    Retorna o último valor disponível de uma coluna
    e sua respectiva data.
    """

    validos = df.dropna(subset=[coluna])

    if validos.empty:
        return None, None

    registro = validos.iloc[-1]

    valor = float(registro[coluna])
    data = pd.to_datetime(registro["data"]).strftime("%m/%Y")

    return valor, data


producao, data_producao = ultimo_valor(dados, "valor")

variacao_producao, _ = ultimo_valor(
    dados, "variacao_pct_producao"
)

consumo, data_consumo = ultimo_valor(dados, "consumo")

variacao_consumo, _ = ultimo_valor(
    dados, "variacao_pct_consumo"
)


def formatar_numero(valor):
    if valor is None:
        return "Não disponível"

    return f"{valor:,.2f}"


def formatar_percentual(valor):
    if valor is None:
        return "Não disponível"

    return f"{valor:.2f}%"


st.subheader(f"{atividade} — {ano}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Último valor de produção",
        formatar_numero(producao)
    )
    if data_producao:
        st.caption(f"Referência: {data_producao}")

with col2:
    st.metric(
        "Variação da produção",
        formatar_percentual(variacao_producao)
    )

with col3:
    st.metric(
        "Último consumo de energia",
        formatar_numero(consumo)
    )
    if data_consumo:
        st.caption(f"Referência: {data_consumo}")

with col4:
    st.metric(
        "Variação do consumo",
        formatar_percentual(variacao_consumo)
    )


# ============================================================
# 5. GRÁFICOS
# ============================================================

st.divider()

st.subheader("Evolução mensal")

col1, col2 = st.columns(2)

with col1:
    st.write("Produção industrial")

    grafico_producao = dados.dropna(
        subset=["valor"]
    )

    st.line_chart(
        grafico_producao,
        x="mes",
        y="valor",
        x_label="Mês",
        y_label="Valor do indicador",
        width="stretch"
    )

with col2:
    st.write("Consumo de energia elétrica")

    grafico_consumo = dados.dropna(
        subset=["consumo"]
    )

    st.line_chart(
        grafico_consumo,
        x="mes",
        y="consumo",
        x_label="Mês",
        y_label="Consumo de energia",
        width="stretch"
    )


# ============================================================
# 6. TABELA DETALHADA
# ============================================================

st.divider()

st.subheader("Dados detalhados")

colunas = [
    "data",
    "valor",
    "variacao_pct_producao",
    "consumo",
    "variacao_pct_consumo",
    "diferenca_variacao_pct",
    "status_correspondencia_consumo"
]

dados_tabela = dados[colunas].rename(
    columns={
        "data": "Data",
        "valor": "Produção",
        "variacao_pct_producao": "Variação da produção (%)",
        "consumo": "Consumo de energia",
        "variacao_pct_consumo": "Variação do consumo (%)",
        "diferenca_variacao_pct": "Diferença das variações",
        "status_correspondencia_consumo": "Correspondência"
    }
)

st.dataframe(
    dados_tabela,
    hide_index=True,
    width="stretch"
)


# ============================================================
# 7. PROVENIÊNCIA
# ============================================================

st.divider()

st.caption(
    "Fonte: Camada Ouro do projeto de Engenharia de Dados. "
    "Modelo: ouro.vw_industria_consumo. "
    "Os dados são consultados diretamente no DuckDB."
)