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
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 15}
  unidades_de_medida: {volume_total: "veículos"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Tráfego de veículos nos equipamentos de contagem veicular (SAT)

## Resumo

Tráfego de veículos nos equipamentos de contagem veicular (SAT) das concessionárias, registrado no Sistema de Informação de Rodovias (SIR) da ANTT. É o maior dos conjuntos de tráfego do fetcher (cerca de 1,7 GB vigentes).

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
| Colunas | 15 |
| Unidades de medida | `volume_total`: veículos |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os CSV e o JSON do pacote `volume-sat` (`https://dados.antt.gov.br/dataset/volume-sat`): por concessionária, um CSV diário e um mensal consolidado (59 CSV e 47 JSON no catálogo).
- No bruto: `volume-sat_<recurso>-<id>@AAAAMMDD.csv` e `volume-sat@AAAAMMDD.json` (275 MB, 719.856 registros diários de 4 concessionárias). Conferido em 2026-11-10 pela listagem do bruto: 46 arquivos de dados, 39 vigentes (1,7 GB); 9 manifestos sem arquivo no bruto conferido.
- Quando o CSV tem um JSON do mesmo carimbo (`volume-sat@20261103.csv` e `.json`), o conversor lê o JSON e ignora o CSV.

## Conteúdo

- Unidade de análise: uma contagem por equipamento, período, sentido, faixa, faixa de velocidade e tipo de veículo.
- Cobertura anunciada pela fonte: a partir de 2024, mensal. O que veio: 2024 a 2026 (amostra de 11 arquivos; o JSON vai de 2024-01-01 a 2026-10-27).
- Layout: 15 colunas, as mesmas dos CSV e do JSON; difere do radar por `data_de_passagem` e `faixa_de_velocidade`.
- Nulos (amostra de 12.554 linhas de 5 CSV): nenhum. O JSON tem 719.856 registros e o lake os mantém todos (719.856 linhas de arquivo, 719.856 registros).

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

## No lake

- Dataset `antt/volume-sat`, particionado por `ano`, um Parquet por arquivo e ano.
- `ano` vem de `data_de_passagem` (`dd/mm/aaaa`, `mm/aaaa` ou `aaaa-mm-dd`).
- O JSON é lido por streaming linha a linha e convertido para texto (`101.42`, `2`). Linha fora do formato de um registro por linha é erro.
- Esquema de referência (`volume-sat.schema.json`): 15 colunas, gerado de 5 CSV de amostra; os 3.000 primeiros registros do JSON, convertidos à parte, têm as mesmas 15 colunas.

## Cuidados de uso

- **Dupla contagem entre arquivos diário e mensal.** Para cada concessionária o pacote tem um arquivo diário e um mensal consolidado. Conferido (Autopista Fluminense, `...flum-53725139` diário, 58.553 linhas, e `...flum-2789ddd0` mensal, 2.862 linhas): os totais mensais de `volume_total` são idênticos nos dois. Os dois estão vigentes e caem na mesma partição `ano`.
- **O JSON repete concessionárias que também têm CSV.** O JSON traz Nova Rota do Oeste, Motiva Minas SP, EPR Via Mineira e Elovias em registros diários, e as quatro também têm CSV diário e mensal vigentes (`..._df087189`, `..._e6bd3035`, `..._c70cb118`, `..._254b448e`, entre outros). A regra de "gêmeo" só ignora o CSV de mesmo nome e carimbo, então o resto é contado de novo.
- **Arquivos de meses ou anos diferentes colidem no nome e só o mais recente é convertido.** O bruto tem arquivos com nome nu (`volume-sat@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote, ao lado dos arquivos com chave de recurso (`volume-sat_<recurso>-<id>@AAAAMMDD.csv`). `select_current` agrupa por nome sem a data e fica só com o mais novo de cada nome; os outros nomes nus ficam de fora do lake. Aqui, 6 dos 53 arquivos do bruto têm conteúdo (URL e hash) ausente do conjunto vigente (por exemplo Ecovias Minas Goiás, MS Via, Via Bahia e Eco101).
- **Manifestos sem arquivo.** Nove manifestos do pacote não têm o CSV no bruto conferido.
- **Data mista.** `dd/mm/aaaa` (diário), `mm/aaaa` (mensal) e `aaaa-mm-dd` (JSON) na mesma coluna.
- **`faixa_de_velocidade` é faixa** (`21 - 50 KM/h`), não velocidade medida.

## Exemplos

Volume mensal de veículos por concessionária em 2025, só nos arquivos mensais consolidados (`mm/aaaa`):

```python
import polars as pl

s = pl.scan_parquet("lake/antt/volume-sat/ano=2025/*.parquet")
mensal = (
    s.filter(pl.col("data_de_passagem").str.len_chars() == 7)
    .group_by("concessionaria", "data_de_passagem")
    .agg(pl.col("volume_total").cast(pl.Int64).sum().alias("veiculos"))
    .sort("concessionaria", "data_de_passagem")
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/volume-sat
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Tráfego de Veículos SAT"
