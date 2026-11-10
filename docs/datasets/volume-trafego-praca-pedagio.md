---
dataset:
  id: "volume-trafego-praca-pedagio"
  fonte: "antt"
  titulo: "Volume de tráfego nas praças de pedágio"
  resumo: "Quantidade de veículos que passaram em cada praça de pedágio das rodovias federais concedidas, por concessionária, mês (ou dia), sentido, tipo de cobrança, categoria e tipo de veículo."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/volume-trafego-praca-pedagio"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal (a cobertura temporal declarada é anual)"
  cobertura: {inicio: "2010", fim: em-curso}
  unidade: "o volume de veículos de uma praça, sentido, tipo de cobrança e categoria em um mês (arquivos mensais) ou em um dia (arquivos diários)"
  granularidade: {espacial: "praça de pedágio, com concessionária e sentido", temporal: "mês, ou dia nos arquivos diários de 2024 em diante"}
  formato_bruto: "CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 10}
  unidades_de_medida: {volume_total: "veículos"}
  dados_pessoais: nenhum
  eras:
    - {desde: "2024", mudanca: "`categoria` dá lugar a `categoria_eixo`; passam a existir, além dos arquivos mensais consolidados, arquivos diários por concessionária com 3,3 milhões de linhas por ano"}
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Volume de tráfego nas praças de pedágio

## Resumo

Volume de tráfego por praça de pedágio informado pelas concessionárias de rodovias federais à ANTT (Superintendência de Infraestrutura Rodoviária). Cada linha é o total de veículos de uma categoria numa praça e sentido em um período. Serve para acompanhar o tráfego pedagiado por rodovia, praça e tipo de veículo.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/volume-trafego-praca-pedagio` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/volume-trafego-praca-pedagio |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal (a cobertura temporal declarada é anual) |
| Cobertura | 2010 a em-curso |
| Unidade (uma linha) | o volume de veículos de uma praça, sentido, tipo de cobrança e categoria em um mês (arquivos mensais) ou em um dia (arquivos diários) |
| Granularidade | espacial: praça de pedágio, com concessionária e sentido; temporal: mês, ou dia nos arquivos diários de 2024 em diante |
| Formato bruto | CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 10 |
| Unidades de medida | `volume_total`: veículos |
| Dados pessoais | nenhum |
| Eras | 2024: `categoria` dá lugar a `categoria_eixo`; passam a existir, além dos arquivos mensais consolidados, arquivos diários por concessionária com 3,3 milhões de linhas por ano |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os recursos CSV do pacote `volume-trafego-praca-pedagio` do portal de dados abertos da ANTT (`https://dados.antt.gov.br/dataset/volume-trafego-praca-pedagio`), que tem um CSV (e um JSON gêmeo) por ano de 2010 em diante e, desde 2024, versões diárias e mensais consolidadas.
- No bruto, os arquivos novos se chamam `volume-trafego-praca-pedagio_<recurso>-<id>@AAAAMMDD.csv`, em que o sufixo é a data da última modificação na fonte; os mais antigos têm o nome nu `volume-trafego-praca-pedagio@AAAAMMDD.csv`. O fetcher descarta documentação (PDF) e o painel; os JSON do pacote não são convertidos.
- Conferido em 2026-11-10 pela listagem do bruto: 23 arquivos de dados (1,3 GB), 22 vigentes e um por recurso: anos 2010 a 2022 (um arquivo por ano), 2023 (`volume-trafego-praca-pedagio@20241203.csv`, nome nu), dois arquivos diários de 2024, o mensal consolidado de 2024, 2025 em versão mensal consolidada e em versão diária, 2026 em versão diária e um arquivo de nome nu (mensal), mais o JSON de 2013 (nome nu; os JSON não são convertidos). O que fica de fora é um arquivo de nome nu sem manifesto (`@20260519`) que repete o mensal consolidado de 2024.

## Conteúdo

- Unidade de análise: o volume de uma combinação concessionária, praça, sentido, tipo de cobrança, categoria e tipo de veículo em um mês (ou dia). Chave não verificada.
- Cobertura anunciada pela fonte: 2010 em diante, cobertura temporal "Anual" e atualização "Mensal". O que veio: 2010 a 2026 (até o mês do arquivo `@20260930`), com 2023 inclusive.
- Eras: de 2010 a 2022 a categoria vem em `categoria`; de 2024 em diante em `categoria_eixo` (código numérico). O dicionário anterior a 2023 usa `categoria`; o de 2023 usa `categoria_eixo` e `Tipo de Cobrança`. A `mes_ano` varia de formato conforme o arquivo: `01/MM/AAAA` (dia 01) nos mensais de 2010 a 2023, `dd/mm/aaaa` nos diários e `mm/aaaa` nos mensais consolidados de 2024 em diante.
- Nulos (amostra de 5 arquivos, 429.634 linhas: 2010, 2020, 2021, 2024 mensal e o arquivo de nome nu de 2026, medida antes da coluna `granularidade`): `categoria` é nula em 60,2% (as linhas dos arquivos de 2024 e 2026) e `categoria_eixo` em 39,8% (as dos arquivos até 2021), porque cada era usa uma das duas colunas. Os demais campos não têm nulo na amostra.

## Variáveis

Descrições do dicionário de dados da ANTT (dois PDFs, o de 2010 a 2022 e o de 2023). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `concessionaria` | `concessionaria` | texto | Nome da concessionária que prestou as informações | — | todo |
| `mes_ano` | `mes_ano` | texto | Data de referência. A fonte dá o formato `jan-17`; nos arquivos conferidos vem como `01/MM/AAAA` (sempre o dia 01) nos mensais de 2010 a 2023, como `dd/mm/aaaa` nos arquivos diários e como `mm/aaaa` nos mensais consolidados de 2024 em diante | `dd/mm/aaaa` ou `mm/aaaa` | todo |
| `sentido` | `sentido` | texto | Orientação de direção geral da praça | `Crescente`, `Decrescente` | todo |
| `praca` | `praca` | texto | Nome dado para a praça de pedágio; o formato é livre (por exemplo `2 (Vargem)`, `1 Sul (Mairiporã)`) | — | todo |
| `tipo_cobranca` | `tipo_cobranca` | texto | Tipo de cobrança. O dicionário de 2023 a chama `Tipo de Cobrança` | `Manual`, `Automática`, `OCR/PLACA`, `N/I` (conferido) | todo |
| `categoria` | `categoria` | texto | Representação veicular na tabela de tarifas (dicionário anterior a 2023). Valores livres, como `Categoria 6` ou `Veículo Comercial 3 eixos` | — | 2010 a 2022 |
| `tipo_de_veiculo` | `tipo_de_veiculo` | texto | Classificação veicular | `Comercial`, `Passeio`, `Moto`, `Veículo Pequeno` (conferido) | todo |
| `volume_total` | `volume_total` | texto | Volume total de veículos que passaram na praça. Texto com vírgula decimal e `,00` (por exemplo `13,00`) | veículos | todo |
| `granularidade` | — | texto | Granularidade do arquivo de origem, calculada pelo conversor; não existe na fonte | `dia`, `mes` ou nulo (arquivo sem data) | todo |
| `categoria_eixo` | `categoria_eixo` | texto | Categoria por número de eixos ou da tabela de tarifas (dicionário de 2023, `categoria_eixo`); nos arquivos conferidos é um código numérico de 1 a 20 como texto | 1 a 20, como texto (conferido) | 2024 em diante |

## No lake

- Dataset `antt/volume-trafego-praca-pedagio`, particionado por `ano`, um Parquet por arquivo de origem.
- `ano` vem da coluna `mes_ano` (qualquer grupo de 4 dígitos na linha, entre 1900 e 2100); linha sem ano válido iria para a partição `ano=__HIVE_DEFAULT_PARTITION__` (não houve na amostra).
- `granularidade` (`dia` ou `mes`) é do arquivo, igual em todas as linhas dele: o arquivo diário e o mensal consolidado do mesmo período caem na mesma partição `ano`, e a coluna os separa. Vale o que o nome do recurso diz (`_diario`, `_mensal_consolidado`); sem isso, o arquivo é `mes` quando pelo menos 90% das linhas têm `mm/aaaa` ou o dia 01, e `dia` no resto. Os mensais de 2010 a 2022 (`01/MM/AAAA`) saem `mes`. O de 2023 também (99,5% das linhas no dia 01), embora tenha 734 linhas em outras datas: `31/01` e `31/03/2023` (CRO, o mês inteiro com data do último dia), `02/12/2023` (CONCER, idem) e 226 linhas diárias de janeiro da Ecovias do Araguaia; essas linhas ficam `mes` como o resto do arquivo.
- Todas as colunas são texto, com nomes normalizados (minúsculas, sem acento). Arquivos UTF-8 e Windows-1252 são lidos com decodificação própria; aspas internas soltas são reparadas.
- Esquema de referência (`volume-trafego-praca-pedagio.schema.json`): 10 colunas, gerado de uma conversão de 6 arquivos de amostra (2010, 2020, 2021, 2024 mensal, o arquivo de nome nu de 2026 e o início do diário de 2026).

## Cuidados de uso

- **Dupla contagem entre arquivos diário e mensal.** Em 2024, o arquivo mensal consolidado e o arquivo diário (`2024 Diário`) somam o mesmo total: 834.732.408 veículos nos dois (143.377 linhas no mensal, 3.312.763 no diário; conferido em 2026-11-10). Os dois caem em `ano=2024`, então somar a partição conta o tráfego duas vezes. **Filtre `granularidade = "mes"` (ou `"dia"`) antes de somar.** O mesmo padrão (diário e `_mensal_consolidado`) vale para 2025 e 2026 pelos nomes de recurso; não foi comparado numericamente.
- **Dois arquivos diários de 2024.** O portal lista, além do `2024 Diário` (maio de 2026), o recurso `2024` de maio de 2025 (`volume-trafego-praca-pedagio-2024.csv`, nome nu no bruto): 3.358.858 linhas e 848.941.037 veículos, contra 3.312.763 e 834.732.408 do diário novo. São revisões do mesmo período, os dois são vigentes no lake (cada um no seu Parquet) e somar `granularidade = "dia"` de 2024 conta o ano duas vezes: use um só deles (o `2024 Diário` é o mais recente).
- **Recursos de nome nu se somam aos demais.** O bruto tem arquivos de nome nu (`volume-trafego-praca-pedagio@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote (2023, 2024 e o mensal de 2026, entre outros). A versão vigente é escolhida por recurso (URL do manifesto ao lado), então todos entram, cada um no seu Parquet (`volume-trafego-praca-pedagio_<id8>.parquet` para os de nome nu); o ano de 2023 passa a existir no lake. Um arquivo de nome nu sem manifesto ao lado segue a regra do nome (só o mais recente de cada nome).
- **Manifesto sem arquivo.** Um manifesto de 2026 (`...concession-b475d3ac@20260930`) não tem o CSV correspondente no bruto conferido.
- **Volume é texto com vírgula decimal** (`13,00`); troque a vírgula por ponto antes de somar.
- **`mes_ano` muda de formato** entre os mensais de 2010 a 2023 (`01/MM/AAAA`), os diários (`dd/mm/aaaa`) e os mensais consolidados (`mm/aaaa`); extraia o mês com cuidado. No arquivo de 2023 algumas linhas têm outra data (ver `granularidade`): para o mês, use sempre a data inteira, não só a granularidade.
- **Categorias.** Os valores de `categoria` e `categoria_eixo` são livres e variam entre concessionárias (`Categoria 6`, `Veículo Comercial 3 eixos`, `10`); não há tabela de códigos publicada.

## Exemplos

Volume mensal de veículos por concessionária em 2024, usando só o arquivo mensal consolidado (o diário repetiria o total):

```python
import polars as pl

vol = pl.scan_parquet("lake/antt/volume-trafego-praca-pedagio/ano=2024/*.parquet")
mensal = (
    vol.filter(pl.col("granularidade") == "mes")  # só o arquivo mensal consolidado
    .with_columns(v=pl.col("volume_total").str.replace(",", ".").cast(pl.Float64))
    .group_by("concessionaria", "mes_ano")
    .agg(pl.col("v").sum().alias("veiculos"))
    .sort("concessionaria", "mes_ano")
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/volume-trafego-praca-pedagio
- Dicionários de dados (PDF), no pacote: "Volume de Tráfego por Praça" (2010 a 2022) e "Volume de Tráfego por Praça 2023"
- Painel da ANTT (Visualização Gráfica), no pacote
