---
dataset:
  id: "quantidade-possiveis-infratores"
  fonte: "antt"
  titulo: "Quantidade de possíveis infratores por excesso de velocidade nos radares"
  resumo: "Contagem de veículos passando acima da velocidade permitida nos radares das concessionárias, por equipamento, dia, sentido, faixa, faixa de velocidade e tipo de veículo."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/quantidade-possiveis-infratores"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal"
  cobertura: {inicio: "2022", fim: em-curso}
  unidade: "a contagem de veículos de um tipo em uma faixa de velocidade, equipamento, sentido e faixa em um dia"
  granularidade: {espacial: "equipamento (radar), com rodovia, km e município", temporal: "dia"}
  formato_bruto: "CSV por concessionária, separador ponto e vírgula, Windows-1252 ou UTF-8"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 15}
  unidades_de_medida: {volume_total: "veículos"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Quantidade de possíveis infratores por excesso de velocidade nos radares

## Resumo

Quantidade de possíveis infratores por excesso de velocidade nos radares de controle das concessionárias, registrada no Sistema de Informação de Rodovias (SIR) da ANTT. Cada concessionária publica o seu arquivo.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/quantidade-possiveis-infratores` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/quantidade-possiveis-infratores |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal |
| Cobertura | 2022 a em-curso |
| Unidade (uma linha) | a contagem de veículos de um tipo em uma faixa de velocidade, equipamento, sentido e faixa em um dia |
| Granularidade | espacial: equipamento (radar), com rodovia, km e município; temporal: dia |
| Formato bruto | CSV por concessionária, separador ponto e vírgula, Windows-1252 ou UTF-8 |
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

- O fetcher baixa os CSV do pacote `quantidade-possiveis-infratores` (`https://dados.antt.gov.br/dataset/quantidade-possiveis-infratores`): um recurso por concessionária (21 CSV e 21 JSON).
- No bruto: `quantidade-possiveis-infratores_<recurso>-<id>@AAAAMMDD.csv`; arquivos antigos têm o nome nu.

## Conteúdo

- Unidade de análise: uma contagem diária por equipamento, sentido, faixa, faixa de velocidade e tipo de veículo. Chave não verificada.
- Cobertura anunciada pela fonte: a partir de 2022, mensal. O que veio: partições 2022, 2024, 2025 e 2026 na amostra de 3 arquivos (Via Cristais, Concebra e Transbrasiliana), pelos arquivos vigentes.
- Layout: 15 colunas em todos os arquivos conferidos.
- Nulos (amostra de 20.493 linhas de 3 arquivos): nenhum.

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Quantidade de Possíveis Infratores"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

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

## No lake

- Dataset `antt/quantidade-possiveis-infratores`, particionado por `ano`, um Parquet por arquivo.
- `ano` vem de `data_da_passagem` (grupo de 4 dígitos).
- Todas as colunas são texto.
- Esquema de referência (`quantidade-possiveis-infratores.schema.json`): 15 colunas, gerado de 3 arquivos de amostra.

## Cuidados de uso

- **Recursos de nome nu se somam aos demais.** O bruto tem arquivos de nome nu (`quantidade-possiveis-infratores@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote (Eco050, Rodovia do Aço, Autopista Fluminense, MS Via, Eco101 e Ecoponte, entre outros). A versão vigente é escolhida por recurso (URL do manifesto ao lado), então todos entram, cada um no seu Parquet (`quantidade-possiveis-infratores_<id8>.parquet`). Um arquivo de nome nu sem manifesto ao lado segue a regra do nome (só o mais recente de cada nome).
- **Cópia sob dois nomes.** `quantidade-possiveis-infratores@20260828.csv` (Autopista Fluminense) e o recurso `...aut-ae4f9bef@20260828` têm a mesma URL e o mesmo hash. O conversor trata como um só: entra o de nome com chave, e o de nome nu aparece como `gemeo` no `inventory()`. O mesmo vale, sem manifesto, para um arquivo de nome nu de mesmo carimbo, tamanho e `sha256` de um de nome com chave.
- **Velocidade é faixa.** `velocidade` traz faixas como `81 - 100 KM/h`, não a velocidade medida.

## Exemplos

Possíveis infratores por faixa de velocidade nos arquivos de 2022:

```python
import polars as pl

q = pl.scan_parquet("lake/antt/quantidade-possiveis-infratores/ano=2022/*.parquet")
resumo = (
    q.group_by("velocidade")
    .agg(pl.col("volume_total").cast(pl.Int64).sum().alias("veiculos"))
    .sort("veiculos", descending=True)
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/quantidade-possiveis-infratores
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Quantidade de Possíveis Infratores"
