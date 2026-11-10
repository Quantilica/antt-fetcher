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
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 9}
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
| Colunas | 9 |
| Unidades de medida | `volume_total`: veículos |
| Dados pessoais | nenhum |
| Eras | 2024: `categoria` dá lugar a `categoria_eixo`; passam a existir, além dos arquivos mensais consolidados, arquivos diários por concessionária com 3,3 milhões de linhas por ano |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os recursos CSV do pacote `volume-trafego-praca-pedagio` do portal de dados abertos da ANTT (`https://dados.antt.gov.br/dataset/volume-trafego-praca-pedagio`), que tem um CSV (e um JSON gêmeo) por ano de 2010 em diante e, desde 2024, versões diárias e mensais consolidadas.
- No bruto, os arquivos novos se chamam `volume-trafego-praca-pedagio_<recurso>-<id>@AAAAMMDD.csv`, em que o sufixo é a data da última modificação na fonte; os mais antigos têm o nome nu `volume-trafego-praca-pedagio@AAAAMMDD.csv`. O fetcher descarta documentação (PDF) e o painel; os JSON do pacote não são convertidos.
- Conferido em 2026-11-10 pela listagem do bruto: 23 arquivos de dados, 19 pela regra do arquivo mais recente. Anos 2010 a 2022 (um arquivo por ano), 2024 e 2025 em versão mensal consolidada e em versão diária, 2026 em versão diária e um arquivo de nome nu (mensal). **O ano de 2023 não está entre os arquivos vigentes** (veja os cuidados de uso).

## Conteúdo

- Unidade de análise: o volume de uma combinação concessionária, praça, sentido, tipo de cobrança, categoria e tipo de veículo em um mês (ou dia). Chave não verificada.
- Cobertura anunciada pela fonte: 2010 em diante, cobertura temporal "Anual" e atualização "Mensal". O que veio: 2010 a 2022, 2024, 2025 e 2026 (até o mês do arquivo `@20260930`).
- Eras: de 2010 a 2022 a categoria vem em `categoria`; de 2024 em diante em `categoria_eixo` (código numérico). O dicionário anterior a 2023 usa `categoria`; o de 2023 usa `categoria_eixo` e `Tipo de Cobrança`. A `mes_ano` varia de formato conforme o arquivo (dia ou mês).
- Nulos (amostra de 5 arquivos, 429.634 linhas: 2010, 2020, 2021, 2024 mensal e o arquivo de nome nu de 2026): `categoria` é nula em 60,2% (as linhas dos arquivos de 2024 e 2026) e `categoria_eixo` em 39,8% (as dos arquivos até 2021), porque cada era usa uma das duas colunas. Os demais campos não têm nulo na amostra.

## Variáveis

Descrições do dicionário de dados da ANTT (dois PDFs, o de 2010 a 2022 e o de 2023). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `concessionaria` | `concessionaria` | texto | Nome da concessionária que prestou as informações | — | todo |
| `mes_ano` | `mes_ano` | texto | Data de referência. A fonte dá o formato `jan-17`; nos arquivos conferidos vem como `01/01/2010` (dia) nos arquivos diários e `01/2024` (mês) nos mensais consolidados | `dd/mm/aaaa` ou `mm/aaaa` | todo |
| `sentido` | `sentido` | texto | Orientação de direção geral da praça | `Crescente`, `Decrescente` | todo |
| `praca` | `praca` | texto | Nome dado para a praça de pedágio; o formato é livre (por exemplo `2 (Vargem)`, `1 Sul (Mairiporã)`) | — | todo |
| `tipo_cobranca` | `tipo_cobranca` | texto | Tipo de cobrança. O dicionário de 2023 a chama `Tipo de Cobrança` | `Manual`, `Automática`, `OCR/PLACA`, `N/I` (conferido) | todo |
| `categoria` | `categoria` | texto | Representação veicular na tabela de tarifas (dicionário anterior a 2023). Valores livres, como `Categoria 6` ou `Veículo Comercial 3 eixos` | — | 2010 a 2022 |
| `tipo_de_veiculo` | `tipo_de_veiculo` | texto | Classificação veicular | `Comercial`, `Passeio`, `Moto`, `Veículo Pequeno` (conferido) | todo |
| `volume_total` | `volume_total` | texto | Volume total de veículos que passaram na praça. Texto com vírgula decimal e `,00` (por exemplo `13,00`) | veículos | todo |
| `categoria_eixo` | `categoria_eixo` | texto | Categoria por número de eixos ou da tabela de tarifas (dicionário de 2023, `categoria_eixo`); nos arquivos conferidos é um código numérico de 1 a 20 como texto | 1 a 20, como texto (conferido) | 2024 em diante |

## No lake

- Dataset `antt/volume-trafego-praca-pedagio`, particionado por `ano`, um Parquet por arquivo de origem.
- `ano` vem da coluna `mes_ano` (qualquer grupo de 4 dígitos na linha, entre 1900 e 2100); linha sem ano válido iria para a partição `ano=__HIVE_DEFAULT_PARTITION__` (não houve na amostra).
- Todas as colunas são texto, com nomes normalizados (minúsculas, sem acento). Arquivos UTF-8 e Windows-1252 são lidos com decodificação própria; aspas internas soltas são reparadas.
- Esquema de referência (`volume-trafego-praca-pedagio.schema.json`): 9 colunas, gerado de uma conversão de 5 arquivos de amostra (2010, 2020, 2021, 2024 e o arquivo de nome nu de 2026).

## Cuidados de uso

- **Dupla contagem entre arquivos diário e mensal.** Em 2024, o arquivo mensal consolidado e o arquivo diário somam o mesmo total: 834.732.408 veículos nos dois (143.377 linhas no mensal, 3.312.763 no diário; conferido em 2026-11-10). Os dois caem em `ano=2024`, então somar a partição conta o tráfego duas vezes. Use só um dos dois por concessionária e ano. O mesmo padrão (diário e `_mensal_consolidado`) vale para 2025 e 2026 pelos nomes de recurso; não foi comparado numericamente.
- **Arquivos de meses ou anos diferentes colidem no nome e só o mais recente é convertido.** O bruto tem arquivos com nome nu (`volume-trafego-praca-pedagio@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote, ao lado dos arquivos com chave de recurso (`volume-trafego-praca-pedagio_<recurso>-<id>@AAAAMMDD.csv`). `select_current` agrupa por nome sem a data e fica só com o mais novo de cada nome; os outros nomes nus ficam de fora do lake. Aqui, `volume-trafego-praca-pedagio@20241203.csv` (recurso `volume-trafego-praca-pedagio-2023.csv`, 15,3 MB) perde para o nome nu mais novo `@20260930`; por isso 2023 não está no lake. Conferido: 2 dos 23 arquivos de dados do bruto têm conteúdo (URL e hash) ausente do conjunto vigente (2023 e o JSON de 2013).
- **Manifesto sem arquivo.** Um manifesto de 2026 (`...concession-b475d3ac@20260930`) não tem o CSV correspondente no bruto conferido.
- **Volume é texto com vírgula decimal** (`13,00`); troque a vírgula por ponto antes de somar.
- **`mes_ano` muda de formato** entre arquivos diários (`dd/mm/aaaa`) e mensais (`mm/aaaa`); extraia o mês com cuidado.
- **Categorias.** Os valores de `categoria` e `categoria_eixo` são livres e variam entre concessionárias (`Categoria 6`, `Veículo Comercial 3 eixos`, `10`); não há tabela de códigos publicada.

## Exemplos

Volume mensal de veículos por concessionária em 2024, usando só o arquivo mensal consolidado (o diário repetiria o total):

```python
import polars as pl

vol = pl.scan_parquet("lake/antt/volume-trafego-praca-pedagio/ano=2024/*.parquet")
mensal = (
    vol.filter(pl.col("mes_ano").str.len_chars() == 7)  # mm/aaaa: arquivo mensal
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
