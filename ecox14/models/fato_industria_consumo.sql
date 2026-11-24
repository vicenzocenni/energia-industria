SELECT
    Data,
    Ano,
    Mes,
    Atividade,
    ChaveAtividade,
    Valor,
    VariacaoPctProducao,
    Consumo,
    VariacaoPctConsumo,
    DiferencaVariacaoPct

FROM {{ source('prata', 'producao_industria_enriquecida') }}