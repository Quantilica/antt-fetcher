---
dataset:
  id: "volume-sat"
  fonte: "antt"
  titulo: "Tráfego de veículos nos equipamentos de contagem veicular (SAT)"
  resumo: "Volume de veículos registrado pelos equipamentos de contagem veicular (SAT) das concessionárias, por equipamento, período, sentido, faixa, faixa de velocidade e tipo de veículo."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/volume-sat"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal"
  cobertura: {inicio: "2024", fim: em-curso}
  unidade: "o volume de veículos de um tipo em uma faixa de velocidade, equipamento, sentido e faixa em um dia (arquivos diários e JSON) ou mês (mensais consolidados)"
  granularidade: {espacial: "equipamento (SAT), com rodovia, km e município", temporal: "dia ou mês"}
  formato_bruto: "CSV por concessionária (diário e mensal consolidado), separador ponto e vírgula, Windows-1252 ou UTF-8, mais um JSON ({\"volume_sat\":[...]}, um registro por linha, UTF-8)"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 16}
  unidades_de_medida: {volume_total: "veículos"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Tráfego de veículos nos equipamentos de contagem veicular (SAT)

## Resumo

Tráfego de veículos nos equipamentos de contagem veicular (SAT) das concessionárias, registrado no Sistema de Informação de Rodovias (SIR) da ANTT. É o maior dos conjuntos de tráfego do fetcher (alguns GB de CSV).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/volume-sat` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/volume-sat |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal |
| Cobertura | 2024 a em-curso |
| Unidade (uma linha) | o volume de veículos de um tipo em uma faixa de velocidade, equipamento, sentido e faixa em um dia (arquivos diários e JSON) ou mês (mensais consolidados) |
| Granularidade | espacial: equipamento (SAT), com rodovia, km e município; temporal: dia ou mês |
| Formato bruto | CSV por concessionária (diário e mensal consolidado), separador ponto e vírgula, Windows-1252 ou UTF-8, mais um JSON ({"volume_sat":[...]}, um registro por linha, UTF-8) |
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

- O fetcher baixa os CSV e o JSON do pacote `volume-sat` (`https://dados.antt.gov.br/dataset/volume-sat`): por concessionária, um CSV diário e um mensal consolidado (59 CSV e 47 JSON no catálogo).
- No bruto: `volume-sat_<recurso>-<id>@AAAAMMDD.csv` e `volume-sat@AAAAMMDD.json` (275 MB, 719.856 registros diários de 4 concessionárias).
- O JSON repete concessionárias que têm CSV diário. O CSV manda: a linha do JSON só fica de fora se o CSV diário vigente da mesma concessionária cobre o mesmo mês (nomes comparados sem acento, pontuação nem `S.A.`/`S/A`), e um JSON inteiramente coberto não gera Parquet (`gemeo` no `inventory()`). No bruto conferido o JSON está inteiramente coberto, então o lake não carrega nada dele.

## Conteúdo

- Unidade de análise: uma contagem por equipamento, período, sentido, faixa, faixa de velocidade e tipo de veículo.
- Cobertura anunciada pela fonte: a partir de 2024, mensal. O que veio: 2024 a 2026 (amostra de 11 arquivos; o JSON vai de 2024-01-01 a 2026-10-27).
- Layout: 15 colunas na fonte, as mesmas dos CSV e do JSON, mais `granularidade` no lake; difere do radar por `data_de_passagem` e `faixa_de_velocidade`.
- Nulos (amostra de 12.554 linhas de 5 CSV): nenhum. O JSON tem 719.856 registros de 4 concessionárias e todos já estão nos CSV diários, com a mesma contagem (Nova Rota do Oeste 568.467, Motiva Minas SP 61.373, EPR Via Mineira 51.387, Elovias 38.629; no CSV da Motiva Minas esses registros são os de 2024 em diante, de 113.595 desde 2022).

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Tráfego de Veículos SAT"). Todos os valores chegam ao lake como texto, inclusive os números do JSON. A coluna de partição `ano` não está nos arquivos.

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
| `data_de_passagem` | `data_de_passagem` | texto | Data da passagem; nos CSV vem como `dd/mm/aaaa` (arquivo diário) ou `mm/aaaa` (mensal consolidado) e, no JSON, como `aaaa-mm-dd`. O dicionário dá `22/02/2002` | `dd/mm/aaaa`, `mm/aaaa` ou `aaaa-mm-dd` | todo |
| `sentido_da_passagem` | `sentido_da_passagem` | texto | Sentido da passagem | `Crescente`, `Decrescente`, `Crescente_Decrescente` (conferido) | todo |
| `faixa_da_passagem` | `faixa_da_passagem` | texto | Número da faixa | 1, 2, 3 ou 4 | todo |
| `faixa_de_velocidade` | `faixa_de_velocidade` | texto | Faixa de velocidade do veículo, em km/h. O dicionário a chama `Velocidade` e dá o exemplo `80km/h`; os arquivos trazem faixas (`21 - 50 KM/h`, `> 160 KM/h`) | faixas em km/h | todo |
| `tipo_de_veiculo` | `tipo_de_veiculo` | texto | Tipo de veículo | `Moto`, `Veículo leve`, `Veículo pesado`, `Não identificado` (varia entre arquivos: `Passeio`, `Comercial`, `Ônibus`…) | todo |
| `volume_total` | `volume_total` | texto | Total de veículos (volume de passagem) | veículos | todo |
| `granularidade` | — | texto | Granularidade do arquivo de origem, calculada pelo conversor; não existe na fonte | `dia`, `mes` ou nulo (arquivo sem data) | todo |

## No lake

- Dataset `antt/volume-sat`, particionado por `ano`, um Parquet por arquivo e ano.
- `ano` vem de `data_de_passagem` (`dd/mm/aaaa`, `mm/aaaa` ou `aaaa-mm-dd`).
- `granularidade` (`dia` ou `mes`) é do arquivo, igual em todas as linhas dele: o arquivo diário e o mensal consolidado do mesmo período caem na mesma partição `ano`, e a coluna os separa. Vale o que o nome do recurso diz (`_mensal_consolidado`); sem isso, o arquivo é `mes` quando pelo menos 90% das linhas têm `mm/aaaa` ou o dia 01, e `dia` no resto.
- O JSON é lido por streaming linha a linha e convertido para texto (`101.42`, `2`), menos as concessionárias que já têm CSV diário. Linha fora do formato de um registro por linha é erro.
- Esquema de referência (`volume-sat.schema.json`): 16 colunas, gerado da conversão de 5 CSV de amostra (diário e mensal consolidado) e dos primeiros 3 MB do JSON.

## Cuidados de uso

- **Dupla contagem entre arquivos diário e mensal.** Para cada concessionária o pacote tem um arquivo diário e um mensal consolidado. Conferido (Autopista Fluminense, `...flum-53725139` diário, 58.553 linhas, e `...flum-2789ddd0` mensal, 2.862 linhas): os totais mensais de `volume_total` são idênticos nos dois; o mesmo vale para Elovias, EPR Via Mineira e Nova Rota do Oeste (52.232.405, 80.409.293 e 323.911.139 veículos nos dois). Os dois caem na mesma partição `ano`: **filtre `granularidade = "dia"` (ou `"mes"`) antes de somar**, senão o tráfego é contado duas vezes.
- **O JSON repete concessionárias que também têm CSV, e não entra.** O JSON traz Nova Rota do Oeste, Motiva Minas SP, EPR Via Mineira e Elovias em registros diários, e as quatro têm CSV diário vigente com as mesmas contagens de registros. O conversor não carrega as linhas do JSON dessas concessionárias nos meses que o CSV diário cobre; o que fica é o CSV. Uma concessionária que tenha só CSV mensal consolidado não cobre o JSON diário, e um mês que só o JSON traz (um CSV que começa depois) continua vindo do JSON.
- **Recursos de nome nu se somam aos demais.** O bruto tem arquivos de nome nu (`volume-sat@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote (Ecovias Minas Goiás, MS Via, Via Bahia, Eco101, entre outros). A versão vigente é escolhida por recurso (URL do manifesto ao lado), então todos entram, cada um no seu Parquet (`volume-sat_<id8>.parquet`). Um arquivo de nome nu sem manifesto ao lado segue a regra do nome (só o mais recente); um de mesmo carimbo, tamanho e `sha256` de um arquivo com chave (como o `volume-sat@AAAAMMDD.csv` que repete o CSV da Via040) é tratado como cópia.
- **Data mista.** `dd/mm/aaaa` (diário), `mm/aaaa` (mensal) e `aaaa-mm-dd` (JSON) na mesma coluna.
- **`faixa_de_velocidade` é faixa** (`21 - 50 KM/h`), não velocidade medida.

## Exemplos

Volume mensal de veículos por concessionária em 2025, só nos arquivos mensais consolidados (o diário repetiria o total):

```python
import polars as pl

s = pl.scan_parquet("lake/antt/volume-sat/ano=2025/*.parquet")
mensal = (
    s.filter(pl.col("granularidade") == "mes")
    .group_by("concessionaria", "data_de_passagem")
    .agg(pl.col("volume_total").cast(pl.Int64).sum().alias("veiculos"))
    .sort("concessionaria", "data_de_passagem")
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/volume-sat
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Tráfego de Veículos SAT"
