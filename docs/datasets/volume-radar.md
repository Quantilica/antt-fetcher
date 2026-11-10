---
dataset:
  id: "volume-radar"
  fonte: "antt"
  titulo: "Tráfego de veículos nos radares de controle de velocidade"
  resumo: "Volume de veículos registrado pelos radares de controle de velocidade das concessionárias, por equipamento, período, sentido, faixa, faixa de velocidade e tipo de veículo."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/volume-radar"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal"
  cobertura: {inicio: "2022", fim: em-curso}
  unidade: "o volume de veículos de um tipo em uma faixa de velocidade, equipamento, sentido e faixa em um dia (arquivos diários) ou mês (mensais consolidados)"
  granularidade: {espacial: "equipamento (radar), com rodovia, km e município", temporal: "dia ou mês"}
  formato_bruto: "CSV por concessionária (parte dos arquivos sem a linha de cabeçalho), separador ponto e vírgula, Windows-1252 ou UTF-8"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 16}
  unidades_de_medida: {volume_total: "veículos"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Tráfego de veículos nos radares de controle de velocidade

## Resumo

Tráfego de veículos nos radares de controle de velocidade das concessionárias, registrado no Sistema de Informação de Rodovias (SIR) da ANTT. Para cada concessionária há um arquivo diário e um mensal consolidado.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/volume-radar` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/volume-radar |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal |
| Cobertura | 2022 a em-curso |
| Unidade (uma linha) | o volume de veículos de um tipo em uma faixa de velocidade, equipamento, sentido e faixa em um dia (arquivos diários) ou mês (mensais consolidados) |
| Granularidade | espacial: equipamento (radar), com rodovia, km e município; temporal: dia ou mês |
| Formato bruto | CSV por concessionária (parte dos arquivos sem a linha de cabeçalho), separador ponto e vírgula, Windows-1252 ou UTF-8 |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 16 |
| Unidades de medida | `volume_total`: veículos |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os CSV do pacote `volume-radar` (`https://dados.antt.gov.br/dataset/volume-radar`): um recurso por concessionária e por granularidade (44 CSV e 44 JSON, estes não convertidos).
- No bruto: `volume-radar_<recurso>-<id>@AAAAMMDD.csv`; arquivos antigos têm o nome nu.
- Parte dos arquivos foi publicada **sem a linha de cabeçalho** (todos os 5 mensais abertos); o conversor aplica o cabeçalho do dicionário quando a primeira linha tem 15 campos e não é um nome de coluna.

## Conteúdo

- Unidade de análise: uma contagem por equipamento, período, sentido, faixa, faixa de velocidade e tipo de veículo. Chave não verificada.
- Cobertura anunciada pela fonte: a partir de 2022, mensal. O que veio nos 5 arquivos mensais abertos: 2022, 2025 e 2026; a cobertura de cada concessionária não foi levantada.
- Layout: 15 colunas na fonte, mais `granularidade` no lake. Os 5 arquivos abertos são mensais consolidados (`mm/aaaa` em `data_da_passagem`) e sem cabeçalho.
- Nulos (amostra de 5.297 linhas de 5 arquivos): `tipo_de_veiculo` nulo em 960 (18,1%), de uma concessionária que deixa o campo vazio; sem outro nulo. O lake tem exatamente as linhas do CSV, porque não há cabeçalho a descontar.

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Tráfego de Veículos nos Radares"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `concessionaria` | `concessionaria` | texto | Nome da concessionária que prestou as informações | — | todo |
| `identificador` | `identificador` | texto | Nome do equipamento | — | todo |
| `rodovia` | `rodovia` | texto | Rodovia responsável pela concessionária | `BR-116` | todo |
| `uf` | `uf` | texto | Sigla do estado da rodovia | sigla de 2 letras | todo |
| `km_m` | `km_m` | texto | Quilômetro mais a metragem. O dicionário dá `317,940`; os arquivos trazem ponto decimal (`317.940`) | km | todo |
| `municipio` | `municipio` | texto | Município da localização do equipamento de sensoriamento de tráfego | — | todo |
| `tipo_de_pista` | `tipo_de_pista` | texto | Tipo da pista onde a sinalização está localizada | `Principal`, `Marginal` | todo |
| `latitude` | `latitude` | texto | Latitude do equipamento | graus decimais com ponto | todo |
| `longitude` | `longitude` | texto | Longitude do equipamento | graus decimais com ponto | todo |
| `data_da_passagem` | `data_da_passagem` | texto | Data da passagem; nos arquivos diários vem como `dd/mm/aaaa` e nos mensais consolidados como `mm/aaaa`. O dicionário dá `22/02/2002` | `dd/mm/aaaa` ou `mm/aaaa` | todo |
| `sentido_da_passagem` | `sentido_da_passagem` | texto | Sentido da passagem | `Crescente`, `Decrescente`, `Crescente_Decrescente` (conferido) | todo |
| `faixa_da_passagem` | `faixa_da_passagem` | texto | Número da faixa | 1, 2, 3 ou 4 | todo |
| `velocidade` | `velocidade` | texto | Velocidade do veículo em km/h. O dicionário dá o exemplo `80km/h`; os arquivos trazem faixas (`81 - 100 KM/h`, `> 160 KM/h`, `<= 20 KM/h`), não a velocidade medida | faixas em km/h | todo |
| `tipo_de_veiculo` | `tipo_de_veiculo` | texto | Tipo de veículo | `Moto`, `Veículo leve`, `Veículo pesado`, `Não identificado` (varia entre arquivos: `Passeio`, `Comercial`, `Ônibus`…) | todo |
| `volume_total` | `volume_total` | texto | Total de veículos (volume de passagem) | veículos | todo |
| `granularidade` | — | texto | Granularidade do arquivo de origem, calculada pelo conversor; não existe na fonte | `dia`, `mes` ou nulo (arquivo sem data) | todo |

## No lake

- Dataset `antt/volume-radar`, particionado por `ano`, um Parquet por arquivo.
- `ano` vem de `data_da_passagem` (`dd/mm/aaaa` ou `mm/aaaa`).
- `granularidade` (`dia` ou `mes`) é do arquivo, igual em todas as linhas dele: o arquivo diário e o mensal consolidado do mesmo período caem na mesma partição `ano`, e a coluna os separa. Vale o que o nome do recurso diz (`_mensal_consolidado`); sem isso, o arquivo é `mes` quando pelo menos 90% das linhas têm `mm/aaaa` ou o dia 01, e `dia` no resto.
- Arquivo sem cabeçalho: a primeira linha com 15 campos que não é o cabeçalho recebe os nomes do dicionário, na ordem. Se a ordem real das colunas diferisse, as colunas ficariam trocadas; nos 5 arquivos abertos a ordem coincide com a do dicionário.
- Todas as colunas são texto.
- Esquema de referência (`volume-radar.schema.json`): 16 colunas, gerado de 6 arquivos de amostra (diários e mensais consolidados, com e sem cabeçalho).

## Cuidados de uso

- **Dupla contagem entre arquivos diário e mensal.** O pacote traz, por concessionária, um arquivo diário (`volume-radar-<c>.csv`) e um mensal consolidado (`volume-radar-<c>_mensal_consolidado.csv`) para quase todas; os dois estão vigentes no bruto e caem na mesma partição `ano`. Conferido (2026-11-10) na CRT e na Via040: o total mensal de `volume_total` é idêntico nos dois arquivos (7.297.396 e 558.649 veículos). **Filtre `granularidade = "dia"` (ou `"mes"`) antes de somar**, senão o tráfego é contado duas vezes.
- **Recursos de nome nu se somam aos demais.** O bruto tem arquivos de nome nu (`volume-radar@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote (MS Via, Autopista Fluminense mensal, Ecoponte, Eco101 e outros). A versão vigente é escolhida por recurso (URL do manifesto ao lado), então todos entram, cada um no seu Parquet (`volume-radar_<id8>.parquet`). Um arquivo de nome nu sem manifesto ao lado segue a regra do nome (só o mais recente de cada nome).
- **Velocidade é faixa e data pode ser só mês** (`mm/aaaa`) nos arquivos mensais consolidados; `granularidade` registra se o arquivo é diário ou mensal.
- **Volume por linha é agregado** (até 892.624 veículos por linha nos mensais).

## Exemplos

Volume mensal por concessionária em 2025, só nos arquivos mensais consolidados (o diário repetiria o total):

```python
import polars as pl

r = pl.scan_parquet("lake/antt/volume-radar/ano=2025/*.parquet")
mensal = (
    r.filter(pl.col("granularidade") == "mes")
    .group_by("concessionaria", "data_da_passagem")
    .agg(pl.col("volume_total").cast(pl.Int64).sum().alias("veiculos"))
    .sort("concessionaria", "data_da_passagem")
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/volume-radar
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Tráfego de Veículos nos Radares"
