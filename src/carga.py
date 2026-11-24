
import duckdb
from Config import PRATA, OURO

BANCO = OURO / "projeto.duckdb"

con = duckdb.connect(str(BANCO))

con.execute("CREATE SCHEMA IF NOT EXISTS prata")
con.execute("CREATE SCHEMA IF NOT EXISTS ouro")


def carregar_prata():
    caminho = (PRATA / "consumo_mensal.parquet").as_posix()

    con.execute(f"""
        CREATE OR REPLACE TABLE prata.consumo_mensal AS
        SELECT * FROM read_parquet('{caminho}')
    """)

    caminho = (PRATA / "producao_industria.parquet").as_posix()

    con.execute(f"""
        CREATE OR REPLACE TABLE prata.producao_industria AS
        SELECT * FROM read_parquet('{caminho}')
    """)

    caminho = (PRATA / "producao_industria_enriquecida.parquet").as_posix()

    con.execute(f"""
        CREATE OR REPLACE TABLE prata.producao_industria_enriquecida AS
        SELECT * FROM read_parquet('{caminho}')
    """)

    for tabela in [
        "consumo_mensal",
        "producao_industria",
        "producao_industria_enriquecida"
    ]:
        print(f"\nTabela: {tabela}")
        print(con.execute(
            f"DESCRIBE prata.{tabela}"
        ).fetchdf())

    caminho = (PRATA / "consumo_industrial_tratado.csv").as_posix()

    con.execute(f"""
        CREATE OR REPLACE TABLE prata.consumo_industrial AS
        SELECT
            CAST(Data AS DATE) AS Data,
            Ano,
            Mes,
            SetorIndustrial,
            Consumo,
            RegioesRegistradas,

            TRY_CAST(
                regexp_extract(
                    SetorIndustrial,
                    '^[[:space:]]*([0-9]+[.])?0*([0-9]+)',
                    2
                ) AS INTEGER
            ) AS ChaveAtividade

        FROM read_csv_auto('{caminho}', header = true)
    """)


def explorar_prata():
    consultas = {
        "Classes de consumo": """
            SELECT DISTINCT Classe
            FROM prata.consumo_mensal
            ORDER BY Classe
        """,

        "Tipos de consumidor": """
            SELECT DISTINCT TipoConsumidor
            FROM prata.consumo_mensal
            ORDER BY TipoConsumidor
        """,

        "Atividades industriais": """
            SELECT DISTINCT Atividade
            FROM prata.producao_industria
            ORDER BY Atividade
        """,

        "Duplicatas no consumo": """
            SELECT Data, Classe, TipoConsumidor, COUNT(*) AS quantidade
            FROM prata.consumo_mensal
            GROUP BY Data, Classe, TipoConsumidor
            HAVING COUNT(*) > 1
        """,

        "Duplicatas na produção": """
            SELECT Data, Atividade, COUNT(*) AS quantidade
            FROM prata.producao_industria
            GROUP BY Data, Atividade
            HAVING COUNT(*) > 1
        """,

        "Comparação das fontes de produção": """
            SELECT
                (SELECT COUNT(*) FROM prata.producao_industria) AS original,
                (SELECT COUNT(*) FROM prata.producao_industria_enriquecida) AS enriquecida
        """,

        "Consumo agregado": """
            SELECT
                Data,
                Classe,
                TipoConsumidor,
                COUNT(*) AS registros,
                SUM(Consumo) AS consumo_nacional,
                SUM(Consumidores) AS consumidores_nacionais
            FROM prata.consumo_mensal
            GROUP BY Data, Classe, TipoConsumidor
            ORDER BY Data, Classe, TipoConsumidor
            LIMIT 15
        """,

        "Quantidade de registros por mês": """
            SELECT
                Data,
                COUNT(*) AS registros
            FROM prata.consumo_mensal
            GROUP BY Data
            ORDER BY Data
            LIMIT 15
        """,

        "Localidades da produção enriquecida": """
            SELECT DISTINCT Local
            FROM prata.producao_industria_enriquecida
        """,

        "Variação percentual do consumo": """
            SELECT
                Data,
                Classe,
                TipoConsumidor,
                COUNT(*) AS registros,
                MIN(VariacaoPct) AS variacao_minima,
                MAX(VariacaoPct) AS variacao_maxima
            FROM prata.consumo_mensal
            WHERE Classe = 'Industrial'
            GROUP BY Data, Classe, TipoConsumidor
            ORDER BY Data, TipoConsumidor
            LIMIT 20
        """,

        "Distribuição das Atividades na produção enriquecida": """
            SELECT
                Atividade,
                ChaveAtividade,
                COUNT(*) AS registros,
                COUNT(Consumo) AS registros_com_consumo,
                COUNT(VariacaoPctConsumo) AS registros_com_variacao
            FROM prata.producao_industria_enriquecida
            GROUP BY Atividade, ChaveAtividade
            ORDER BY ChaveAtividade
        """,

        "Registros sem Correspondência": """
            SELECT
                Atividade,
                ChaveAtividade,
                COUNT(*) AS registros,
                COUNT(Consumo) AS registros_com_consumo
            FROM prata.producao_industria_enriquecida
            WHERE Consumo IS NULL
            GROUP BY Atividade, ChaveAtividade
            ORDER BY ChaveAtividade
        """,

        "Verificar a Agregação do Consumo": """
            SELECT
                Data,
                Classe,
                TipoConsumidor,
                COUNT(*) AS registros,
                SUM(Consumo) AS consumo_total,
                SUM(Consumidores) AS consumidores_total
            FROM prata.consumo_mensal
            WHERE Classe = 'Industrial'
            GROUP BY Data, Classe, TipoConsumidor
            ORDER BY Data, TipoConsumidor
            LIMIT 20
        """,

        "Quais Datas não possuem Variação?": """
            SELECT
                Data,
                COUNT(*) AS registros,
                COUNT(VariacaoPctProducao) AS variacoes_producao,
                COUNT(VariacaoPctConsumo) AS variacoes_consumo
            FROM prata.producao_industria_enriquecida
            GROUP BY Data
            HAVING
                COUNT(VariacaoPctProducao) < COUNT(*)
                OR COUNT(VariacaoPctConsumo) < COUNT(*)
            ORDER BY Data
        """,

        "Existem duplicatas na tabela enriquecida?": """
            SELECT
                Data,
                Atividade,
                COUNT(*) AS quantidade
            FROM prata.producao_industria_enriquecida
            GROUP BY Data, Atividade
            HAVING COUNT(*) > 1
        """,

        "Data de produção e data de consumo coincidem?": """
            SELECT
                COUNT(*) AS total,
                COUNT(DataExcel) AS datas_consumo_preenchidas,
                COUNT(*) FILTER (
                    WHERE Data = DataExcel
                ) AS datas_iguais,
                COUNT(*) FILTER (
                    WHERE Data <> DataExcel
                ) AS datas_diferentes
            FROM prata.producao_industria_enriquecida
            WHERE Consumo IS NOT NULL
        """

    }

    for nome, sql in consultas.items():
        print(f"\n--- {nome} ---")
        print(con.execute(sql).fetchdf())

    print("\nArquivos disponíveis na Prata:")

    for arquivo in PRATA.iterdir():
        print(arquivo.name)


def construir_ouro():
    # ========================================================
    # 1. DIMENSÃO TEMPO
    # ========================================================

    con.execute("""
        CREATE OR REPLACE TABLE ouro.dim_tempo AS

        WITH datas AS (

            SELECT DISTINCT CAST(Data AS DATE) AS data
            FROM prata.producao_industria_enriquecida

            UNION

            SELECT DISTINCT CAST(Data AS DATE) AS data
            FROM prata.consumo_industrial
        )

        SELECT
            YEAR(data) * 100 + MONTH(data) AS tempo_id,
            data,
            YEAR(data) AS ano,
            MONTH(data) AS mes

        FROM datas

        WHERE
            YEAR(data) BETWEEN 2012 AND 2019
            OR YEAR(data) BETWEEN 2021 AND 2025
    """)

    # ========================================================
    # 2. DIMENSÃO ATIVIDADE
    # ========================================================

    con.execute("""
        CREATE OR REPLACE TABLE ouro.dim_atividade AS

        WITH atividades AS (

            SELECT
                COALESCE(
                    ChaveAtividade,
                    TRY_CAST(
                        regexp_extract(
                            Atividade,
                            '^[[:space:]]*([0-9]+[.])?0*([0-9]+)',
                            2
                        ) AS INTEGER
                    )
                ) AS chave_atividade,

                Atividade AS nome,
                1 AS prioridade

            FROM prata.producao_industria_enriquecida

            UNION ALL

            SELECT
                ChaveAtividade AS chave_atividade,
                SetorIndustrial AS nome,
                2 AS prioridade

            FROM prata.consumo_industrial
        ),

        ordenadas AS (

            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY
                        CASE
                            WHEN chave_atividade IS NOT NULL
                            THEN 'COD:' || CAST(chave_atividade AS VARCHAR)
                            ELSE 'NOME:' || nome
                        END
                    ORDER BY prioridade, nome
                ) AS ordem

            FROM atividades
        )

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY chave_atividade NULLS LAST, nome
            ) AS atividade_id,

            chave_atividade,
            nome,

            CASE
                WHEN chave_atividade BETWEEN 10 AND 33
                    THEN 'Detalhada com correspondência'

                WHEN chave_atividade IN (1, 2, 3)
                    OR chave_atividade IS NULL
                    THEN 'Agregada ou sem código'

                ELSE 'Exclusiva do consumo'
            END AS tipo_atividade

        FROM ordenadas
        WHERE ordem = 1
    """)

    # ========================================================
    # 3. FATO PRODUÇÃO
    # ========================================================

    con.execute("""
        CREATE OR REPLACE TABLE ouro.fato_producao AS

        SELECT
            t.tempo_id,
            a.atividade_id,

            p.Valor AS valor_producao,
            p.VariacaoPctProducao AS variacao_pct_producao

        FROM prata.producao_industria_enriquecida p

        JOIN ouro.dim_tempo t
            ON CAST(p.Data AS DATE) = t.data

        JOIN ouro.dim_atividade a
            ON COALESCE(
                p.ChaveAtividade,
                TRY_CAST(
                    regexp_extract(
                        p.Atividade,
                        '^[[:space:]]*([0-9]+[.])?0*([0-9]+)',
                        2
                    ) AS INTEGER
                )
            ) = a.chave_atividade
    """)

    # ========================================================
    # 4. FATO CONSUMO
    # ========================================================

    con.execute("""
        CREATE OR REPLACE TABLE ouro.fato_consumo AS

        SELECT
            t.tempo_id,
            a.atividade_id,

            c.Consumo AS consumo,
            c.RegioesRegistradas AS regioes_registradas,

            e.VariacaoPctConsumo AS variacao_pct_consumo

        FROM prata.consumo_industrial c

        JOIN ouro.dim_tempo t
            ON CAST(c.Data AS DATE) = t.data

        JOIN ouro.dim_atividade a
            ON (
                c.ChaveAtividade IS NOT NULL
                AND c.ChaveAtividade = a.chave_atividade
            )
            OR (
                c.ChaveAtividade IS NULL
                AND c.SetorIndustrial = a.nome
            )

        LEFT JOIN (
            SELECT
                CAST(Data AS DATE) AS data,
                ChaveAtividade,
                VariacaoPctConsumo

            FROM prata.producao_industria_enriquecida
            WHERE ChaveAtividade IS NOT NULL

        ) e
            ON CAST(c.Data AS DATE) = e.data
            AND c.ChaveAtividade = e.ChaveAtividade
    """)

    # ========================================================
    # 5. VIEW COMPARATIVA
    # ========================================================

    con.execute("""
        CREATE OR REPLACE VIEW ouro.vw_industria_completa AS

        SELECT
            COALESCE(fp.tempo_id, fc.tempo_id) AS tempo_id,
            COALESCE(fp.atividade_id, fc.atividade_id) AS atividade_id,

            t.data,
            t.ano,
            t.mes,

            a.chave_atividade,
            a.nome AS atividade,
            a.tipo_atividade,

            fp.valor_producao,
            fc.consumo,

            fp.variacao_pct_producao,
            fc.variacao_pct_consumo,

            fc.regioes_registradas,

            e.DiferencaVariacaoPct AS diferenca_variacao_pct

        FROM ouro.fato_producao fp

        FULL OUTER JOIN ouro.fato_consumo fc
            ON fp.tempo_id = fc.tempo_id
            AND fp.atividade_id = fc.atividade_id

        JOIN ouro.dim_tempo t
            ON t.tempo_id = COALESCE(fp.tempo_id, fc.tempo_id)

        JOIN ouro.dim_atividade a
            ON a.atividade_id = COALESCE(
                fp.atividade_id,
                fc.atividade_id
            )

        LEFT JOIN (
            SELECT
                CAST(Data AS DATE) AS data,
                ChaveAtividade,
                DiferencaVariacaoPct

            FROM prata.producao_industria_enriquecida
            WHERE ChaveAtividade IS NOT NULL

        ) e
            ON e.data = t.data
            AND e.ChaveAtividade = a.chave_atividade
    """)

    print("Camada Ouro construída.")


def conferir():
    consultas = {

        "Duplicatas na fato_producao": """
            SELECT tempo_id, atividade_id, COUNT(*) AS quantidade
            FROM ouro.fato_producao
            GROUP BY tempo_id, atividade_id
            HAVING COUNT(*) > 1
        """,

        "Duplicatas na fato_consumo": """
            SELECT tempo_id, atividade_id, COUNT(*) AS quantidade
            FROM ouro.fato_consumo
            GROUP BY tempo_id, atividade_id
            HAVING COUNT(*) > 1
        """,

        "Fatos órfãos na produção": """
            SELECT COUNT(*) AS orfaos
            FROM ouro.fato_producao f
            LEFT JOIN ouro.dim_tempo t USING (tempo_id)
            LEFT JOIN ouro.dim_atividade a USING (atividade_id)
            WHERE t.tempo_id IS NULL
               OR a.atividade_id IS NULL
        """,

        "Fatos órfãos no consumo": """
            SELECT COUNT(*) AS orfaos
            FROM ouro.fato_consumo f
            LEFT JOIN ouro.dim_tempo t USING (tempo_id)
            LEFT JOIN ouro.dim_atividade a USING (atividade_id)
            WHERE t.tempo_id IS NULL
               OR a.atividade_id IS NULL
        """,

        "Quantidade de registros": """
            SELECT
                (SELECT COUNT(*) FROM ouro.dim_tempo) AS meses,
                (SELECT COUNT(*) FROM ouro.dim_atividade) AS atividades,
                (SELECT COUNT(*) FROM ouro.fato_producao) AS producao,
                (SELECT COUNT(*) FROM ouro.fato_consumo) AS consumo,
                (SELECT COUNT(*) FROM ouro.vw_industria_completa) AS view_completa
        """
    }

    for nome, sql in consultas.items():

        print(f"\\n--- {nome} ---")

        print(
            con.execute(sql).fetchdf()
        )


def main():
    try:
        carregar_prata()
        construir_ouro()
        conferir()

    finally:
        con.close()


if __name__ == "__main__":
    main()
