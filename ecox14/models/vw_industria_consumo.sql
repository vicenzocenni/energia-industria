{{ config(materialized='view') }}

SELECT
    *,
    CASE
        WHEN Consumo IS NULL THEN 'sem_correspondencia'
        ELSE 'com_correspondencia'
    END AS status_correspondencia_consumo

FROM {{ ref('fato_industria_consumo') }}