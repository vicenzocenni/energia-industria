## Executar o projeto em um computador novo

Este passo a passo executa o pipeline completo, constrói as camadas de dados e
abre o dashboard. Os arquivos-fonte necessários já estão versionados na pasta
`bronze/`.

### 1. Instalar os pré-requisitos

Instale o Git e o Python 3.13. No Windows, confirme que o comando `py` está
disponível no PowerShell:

```powershell
py --version
git --version
```

### 2. Baixar o projeto e instalar as dependências

Clone o repositório e entre na pasta criada:

```powershell
git clone https://github.com/vicenzineo/gastos_jundiai.git
cd gastos_jundiai
```

Crie e ative um ambiente virtual e instale as dependências Python:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação do ambiente, permita scripts somente nesta
sessão e ative-o novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Configurar o perfil do dbt

O dbt precisa de um perfil local, fora do repositório. Crie a pasta de
configuração e abra o arquivo:

```powershell
New-Item -ItemType Directory -Force "$HOME\.dbt"
notepad "$HOME\.dbt\profiles.yml"
```

Cole o conteúdo abaixo em `profiles.yml`. Para obter o caminho absoluto do
clone, execute este comando na raiz do repositório:

```powershell
(Resolve-Path .).Path -replace '\\', '/'
```

Use o resultado no caminho do banco, acrescentando
`/ouro/projeto.duckdb` (use barras `/`):

```yaml
ecox14:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "C:/CAMINHO/ABSOLUTO/gastos_jundiai/ouro/projeto.duckdb"
      schema: ouro
      threads: 1
```

Salve o arquivo. O caminho deve apontar para `ouro/projeto.duckdb` dentro deste
clone, e o nome do perfil `ecox14` e o schema `ouro` devem permanecer como
estão. Esse perfil é específico do computador e não deve ser commitado.

Com o ambiente virtual ativado e na raiz do repositório, valide a configuração:

```powershell
dbt debug --project-dir ecox14
```

### 4. Executar o pipeline

Ainda na raiz do repositório e com o ambiente virtual ativado, execute:

```powershell
python src\pipeline.py
```

O pipeline formata as fontes, transforma e enriquece os dados, carrega as
tabelas no DuckDB e executa os modelos dbt. A execução termina com erro se
alguma etapa falhar; consulte a mensagem no terminal ou `pipeline.log`.

### 5. Abrir o dashboard

Depois que o pipeline terminar com sucesso, inicie o Streamlit:

```powershell
python -m streamlit run dashboard\painel.py
```

O navegador abrirá o dashboard. Se não abrir automaticamente, acesse
`http://localhost:8501`. O painel consulta `ouro/projeto.duckdb`, portanto
execute-o a partir deste clone, que deve ser o mesmo usado para configurar o
perfil do dbt.

### macOS e Linux

Os comandos equivalentes para criar e ativar o ambiente virtual são:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Use os mesmos passos para configurar `~/.dbt/profiles.yml`, apontando `path`
para o caminho absoluto `ouro/projeto.duckdb`, e execute na raiz do repositório:

```bash
dbt debug --project-dir ecox14
python src/pipeline.py
python -m streamlit run dashboard/painel.py
```

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