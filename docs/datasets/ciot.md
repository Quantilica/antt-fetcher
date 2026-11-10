---
dataset:
  id: "ciot"
  fonte: "antt"
  titulo: "CIOT — Código Identificador da Operação de Transporte"
  resumo: "Quantidade mensal de CIOTs emitidos, agregada por município de origem, município de destino e natureza da carga (NCM)."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/ciot"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal"
  cobertura: {inicio: "2020", fim: em-curso}
  unidade: "os CIOTs de um mês para um par origem e destino e uma natureza de carga"
  granularidade: {espacial: "par município de origem e município de destino", temporal: "mês (um arquivo por mês)"}
  formato_bruto: "CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 8}
  unidades_de_medida: {quantidade_ciots: "CIOTs", quantidade_trc: "transportadores", quantidade_contratantes: "contratantes"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# CIOT — Código Identificador da Operação de Transporte

## Resumo

Quantidade mensal de Códigos Identificadores da Operação de Transporte (CIOT) emitidos para o transporte rodoviário de cargas, agregada por origem, destino e natureza da carga, publicada pela ANTT (Superintendência de Cargas). Serve para mapear fluxos de carga entre municípios.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/ciot` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/ciot |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal |
| Cobertura | 2020 a em-curso |
| Unidade (uma linha) | os CIOTs de um mês para um par origem e destino e uma natureza de carga |
| Granularidade | espacial: par município de origem e município de destino; temporal: mês (um arquivo por mês) |
| Formato bruto | CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 8 |
| Unidades de medida | `quantidade_ciots`: CIOTs; `quantidade_trc`: transportadores; `quantidade_contratantes`: contratantes |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os CSV do pacote `ciot` (`https://dados.antt.gov.br/dataset/ciot`): um recurso por mês desde janeiro de 2020 (81 CSV, mais 79 JSON que o conversor não lê).
- No bruto: `ciot_<mês><ano>---ciots-<id>@AAAAMMDD.csv`; os arquivos antigos têm o nome nu `ciot@AAAAMMDD.csv`.
- Conferido em 2026-11-10 pela listagem do bruto: 81 arquivos, 57 vigentes (537 MB): 12 meses em cada ano de 2020 a 2023, 7 em 2024, 1 em 2025 e 1 em 2026; 4 manifestos sem arquivo no bruto conferido.

## Conteúdo

- Unidade de análise: a agregação mensal por município de origem, município de destino e NCM. Chave não verificada.
- Cobertura anunciada pela fonte: mensal. O que o lake tem: janeiro de 2020 a dezembro de 2023, sete meses de 2024 e um de 2025 e de 2026 (veja os cuidados de uso).
- Layout: 8 colunas, igual nos 4 arquivos abertos (janeiro a maio de 2020).
- Nulos (amostra de 525.037 linhas de 4 arquivos): nenhum. `ncm_carga` tem 1.107 valores distintos, de `00.01` a `97.06`.

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Ciot"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `municipio_origem` | `municipio_origem` | texto | Nome do município de origem | — | todo |
| `uf_origem` | `uf_origem` | texto | UF do município de origem | sigla de 2 letras | todo |
| `municipio_destino` | `municipio_destino` | texto | Nome do município de destino | — | todo |
| `uf_destino` | `uf_destino` | texto | UF do município de destino | sigla de 2 letras | todo |
| `ncm_carga` | `ncm_carga` | texto | Quatro primeiros dígitos da natureza da carga, conforme a Nomenclatura Comum do Mercosul (NCM) | 4 dígitos; nos arquivos conferidos vem como `72.04` (com ponto) | todo |
| `quantidade_ciots` | `quantidade_ciots` | texto | Quantidade de CIOTs emitidos no período | CIOTs | todo |
| `quantidade_trc` | `quantidade_trc` | texto | Quantidade de transportadores distintos contratados no período | transportadores | todo |
| `quantidade_contratantes` | `quantidade_contratantes` | texto | Quantidade de contratantes distintos no período | contratantes | todo |

## No lake

- Dataset `antt/ciot`, particionado por `ano`, um Parquet por arquivo. É um dataset de fotografia (`SNAPSHOT_DATASETS`): o `ano` vem do período no nome do arquivo ou da URL do manifesto (`01_2020_ciots.csv` dá 2020), sem coluna de data; sem período no nome e sem manifesto a conversão falha.
- Todas as colunas são texto.
- Esquema de referência (`ciot.schema.json`): 8 colunas, gerado de 4 arquivos de amostra (janeiro a maio de 2020).

## Cuidados de uso

- **Arquivos de meses ou anos diferentes colidem no nome e só o mais recente é convertido.** O bruto tem arquivos com nome nu (`ciot@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote, ao lado dos arquivos com chave de recurso (`ciot_<recurso>-<id>@AAAAMMDD.csv`). `select_current` agrupa por nome sem a data e fica só com o mais novo de cada nome; os outros nomes nus ficam de fora do lake. Aqui, 20 dos 81 arquivos do bruto têm conteúdo (URL e hash) ausente do conjunto vigente: meses de 2026 gravados com nome nu (`ciot@20260410` a `ciot@20260910`, por exemplo março a agosto de 2026).
- **Manifestos sem arquivo.** Quatro manifestos do pacote não têm o CSV no bruto conferido.
- **Mês não está numa coluna.** O mês só existe no nome do arquivo e na URL do manifesto; o lake guarda apenas o ano. Para somar por mês, o caminho do Parquet é o único rastro, e só enquanto cada mês for um arquivo.
- **NCM com ponto.** `ncm_carga` vem como `72.04`, não como 4 dígitos corridos.

## Exemplos

CIOTs emitidos em 2020 por UF de origem:

```python
import polars as pl

c = pl.scan_parquet("lake/antt/ciot/ano=2020/*.parquet")
resumo = (
    c.with_columns(n=pl.col("quantidade_ciots").cast(pl.Int64))
    .group_by("uf_origem")
    .agg(pl.col("n").sum().alias("ciots"))
    .sort("ciots", descending=True)
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/ciot
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Ciot"
