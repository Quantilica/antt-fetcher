---
dataset:
  id: "investimentos"
  fonte: "antt"
  titulo: "Investimentos nas rodovias federais concedidas"
  resumo: "Investimentos anuais realizados pelas concessionárias nas rodovias federais concedidas."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/investimentos"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "anual segundo o portal"
  cobertura: {inicio: "2010", fim: em-curso}
  unidade: "o investimento realizado em um ano por uma concessionária"
  granularidade: {espacial: "concessionária", temporal: "ano"}
  formato_bruto: "CSV único, Windows-1252, separador ponto e vírgula"
  lake: {estado: convertido, particoes: ["ano"], chave: ["ano", "concessionaria"], colunas: 2}
  unidades_de_medida: {valor: "R$"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Investimentos nas rodovias federais concedidas

## Resumo

Total anual de investimentos que cada concessionária de rodovia federal informa à ANTT (Superintendência de Infraestrutura Rodoviária). Serve para acompanhar o investimento por concessão e ano.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/investimentos` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/investimentos |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | anual segundo o portal |
| Cobertura | 2010 a em-curso |
| Unidade (uma linha) | o investimento realizado em um ano por uma concessionária |
| Granularidade | espacial: concessionária; temporal: ano |
| Formato bruto | CSV único, Windows-1252, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `ano`, `concessionaria` |
| Colunas | 2 |
| Unidades de medida | `valor`: R$ |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa o CSV `investimentos.csv` do pacote `investimentos` (`https://dados.antt.gov.br/dataset/investimentos`).
- No bruto: `investimentos@AAAAMMDD.csv`, com manifesto. Conferido em 2026-11-10: 1 arquivo, `@20260522` (10 KB).

## Conteúdo

- Unidade de análise: um par ano e concessionária (único nas 393 linhas conferidas).
- Cobertura: 2010 a 2025 (o ano é a coluna `ano` do CSV, que vira a partição).
- Layout: 3 colunas no CSV (`concessionaria`, `ano`, `Valor`); no lake `ano` é partição e fica `concessionaria` e `valor`.
- Nulos (arquivo inteiro): `valor` é nulo em 58 das 393 linhas (14,8%), principalmente nos primeiros anos e concessões novas.

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Investimentos"). Todos os valores chegam ao lake como texto. A coluna `ano` do CSV vira a partição.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `concessionaria` | `concessionaria` | texto | Nome da concessionária que prestou as informações | 40 nomes distintos (inclui nomes de concessões encerradas) | todo |
| `valor` | `Valor` | texto | Total de investimentos realizados no ano pela concessionária, segundo o dicionário (que dá o exemplo "R$ 865.467,89"). No arquivo vem como número inteiro, sem separadores (`176811000`) e vazio em 14,8% das linhas | R$ (a unidade é a do dicionário; o arquivo não a repete) | todo |

## No lake

- Dataset `antt/investimentos`, particionado por `ano` (da coluna `ano` do CSV, que é removida dos dados), um Parquet por ano.
- Todas as colunas são texto.
- Esquema de referência (`investimentos.schema.json`): 2 colunas, gerado da conversão do arquivo inteiro.

## Cuidados de uso

- **Vazio não é zero.** `valor` vazio (14,8% das linhas) significa que a fonte não informou; não some como zero sem avaliar.
- **Valor sem unidade no arquivo.** A unidade em reais vem do dicionário; os valores aparecem arredondados (`176811000`).
- **Conjunto de concessionárias muda** com o tempo (40 nomes distintos), incluindo concessões encerradas e rebatizadas; não compare séries sem tratar os nomes.

## Exemplos

Investimento total por ano:

```python
import polars as pl

i = pl.scan_parquet("lake/antt/investimentos/ano=*/*.parquet", include_file_paths="arquivo")
total = (
    i.with_columns(
        ano=pl.col("arquivo").str.extract(r"ano=(\d{4})").cast(pl.Int32),
        v=pl.col("valor").cast(pl.Float64),
    )
    .group_by("ano")
    .agg(pl.col("v").sum().alias("investimento_r$"))
    .sort("ano")
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/investimentos
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Investimentos"
