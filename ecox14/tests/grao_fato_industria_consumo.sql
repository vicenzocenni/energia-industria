-- Verifica se cada combinação de Data e Atividade
-- aparece uma única vez na tabela fato.

SELECT
    Data,
    Atividade,
    COUNT(*) AS quantidade

FROM {{ ref('fato_industria_consumo') }}

GROUP BY
    Data,
    Atividade

HAVING COUNT(*) > 1