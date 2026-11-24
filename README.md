Alertas da producao da industria:
Local tem constante Brasil em todos, pode ser descartada.
Atividade é distribuída uniformemente

Alertas do consumo mensal:
DataVersao tem um valor constante "2026-07-17 00:00:00" que pode ser retirado.
Consumidores tem alta correlação com Consumo
Regiao e Sistema tem alta correlação

Os dados começam em 2004, mas os dados da fonte primária começam em 2012. Pode-se apagar os dados anteriores a 2012.
Além disso, na produção da indústria não há o ano de 2020. Pode-se também retirar o deste ano.
E no consumo há o ano de 2026, que não existe na producao.
Como os dados da producao não estão separados por estado, as colunas Regiao e Sistema serão retiradas.
Data e DataExcel de consumo também fornecem as mesmas informações, assim, DataExcel será removida.

Atributos derivados

Durante a etapa de transformação dos dados, foram criados atributos derivados para representar a variação temporal das variáveis analisadas.

VariacaoPct

Representa a variação percentual do valor em relação à observação temporal anterior dentro de cada grupo.

Consumo de energia:
Calculada sobre a coluna Consumo, agrupando as observações por Classe e TipoConsumidor.

Produção industrial:
Calculada sobre a coluna Valor, agrupando as observações por Atividade.

A fórmula utilizada é:

VariacaoPct = ((valor_atual / valor_anterior) - 1) × 100

A primeira observação de cada grupo não possui uma observação anterior e, portanto, não possui uma variação percentual calculável.

O atributo foi criado para permitir a análise da evolução temporal do consumo de energia elétrica e da produção industrial, contribuindo posteriormente para a investigação da relação entre essas duas fontes de dados.

### Enriquecimento

A produção industrial foi enriquecida com dados de
consumo de energia elétrica por setor industrial.

A junção utilizou o mês de referência e o código da
atividade industrial como chaves.

O consumo das cinco regiões foi agregado para
representar o consumo nacional de cada setor.

Foi utilizada uma junção left, preservando todas
as observações da produção industrial.

#### Validação da junção

- Linhas na produção: 4.212
- Linhas no resultado: 4.212
- Registros com correspondência: 3.744
- Registros sem correspondência: 468

Os 468 registros sem correspondência pertencem
às atividades agregadas:
- Indústria geral: 156 registros.
- Indústrias extrativas: 156 registros.
- Indústrias de transformação: 156 registros.

Essas atividades não possuem correspondência direta
com os setores industriais detalhados do consumo.

A fonte de consumo possui ainda 13 setores que
não encontram correspondência na produção.

#### Atributo derivado após a junção

DiferencaVariacaoPct:

Representa a diferença entre a variação percentual
da produção industrial e a variação percentual do
consumo de energia elétrica do mesmo setor.

O cálculo utiliza observações mensais consecutivas.
Quando não existe observação no mês anterior,
a variação não é calculada.

Esse atributo permite investigar se as variações
da produção industrial acompanham as variações
do consumo de energia elétrica.

## Camada Ouro

A Camada Ouro é armazenada no banco DuckDB
projeto.duckdb, dentro dos esquemas dimensionais
e de fatos.

### Dimensões

- dim_tempo: uma linha por mês.
- dim_atividade: uma linha por atividade industrial.

### Tabelas fato

- fato_producao: uma linha por atividade e mês,
  contendo os indicadores de produção.

- fato_consumo: uma linha por atividade e mês,
  contendo os indicadores de consumo.

### View

- vw_industria_completa: reúne as informações
  das duas tabelas fato, preservando registros
  sem correspondência entre as fontes.

### Integridade

- 156 meses analisados.
- 40 atividades identificadas.
- 4.212 registros de produção.
- 5.742 registros de consumo.
- Nenhuma duplicata nas chaves das fatos.
- Nenhum registro órfão.