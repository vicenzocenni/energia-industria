from pathlib import Path
import duckdb


# ============================================================
# 1. CAMINHOS DO PROJETO
# ============================================================

RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / "ouro" / "projeto.duckdb"


# ============================================================
# 2. FUNÇÃO DE CONSULTA
# ============================================================

def _consultar(sql, parametros=None):
    """
    Executa uma consulta SQL no DuckDB em modo somente leitura.
    Retorna o resultado como DataFrame do pandas.
    """

    if not BANCO.exists():
        raise FileNotFoundError(
            f"Banco de dados não encontrado: {BANCO}"
        )

    con = duckdb.connect(str(BANCO), read_only=True)

    try:
        return con.execute(sql, parametros or []).df()
    finally:
        con.close()


# ============================================================
# 3. CONSULTAS PARA OS FILTROS
# ============================================================

def anos():
    """Retorna os anos disponíveis no banco."""

    return _consultar(
        """
        SELECT DISTINCT Ano AS ano
        FROM ouro.vw_industria_consumo
        WHERE Ano IS NOT NULL
        ORDER BY ano
        """
    )


def atividades():
    """Retorna as atividades industriais disponíveis."""

    return _consultar(
        """
        SELECT DISTINCT Atividade AS atividade
        FROM ouro.vw_industria_consumo
        WHERE Atividade IS NOT NULL
        ORDER BY atividade
        """
    )


def atividades_com_consumo():
    """Retorna atividades que possuem correspondência de consumo."""

    return _consultar(
        """
        SELECT DISTINCT Atividade AS atividade
        FROM ouro.vw_industria_consumo
        WHERE status_correspondencia_consumo = 'com_correspondencia'
          AND Consumo IS NOT NULL
        ORDER BY atividade
        """
    )


# ============================================================
# 4. CONSULTA DOS INDICADORES
# ============================================================

def indicador_por_atividade(atividade, ano):
    """
    Retorna os indicadores mensais de produção e consumo
    de uma atividade industrial em determinado ano.
    """

    return _consultar(
        """
        SELECT
            Data AS data,
            Ano AS ano,
            Mes AS mes,
            Atividade AS atividade,
            Valor AS valor,
            VariacaoPctProducao AS variacao_pct_producao,
            Consumo AS consumo,
            VariacaoPctConsumo AS variacao_pct_consumo,
            DiferencaVariacaoPct AS diferenca_variacao_pct,
            status_correspondencia_consumo

        FROM ouro.vw_industria_consumo

        WHERE Atividade = ?
          AND Ano = ?

        ORDER BY Data
        """,
        [atividade, ano],
    )