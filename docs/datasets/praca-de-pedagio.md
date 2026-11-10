---
dataset:
  id: "praca-de-pedagio"
  fonte: "antt"
  titulo: "Praças de pedágio"
  resumo: "Cadastro das praças de pedágio das rodovias federais concedidas, com localização, sentido e situação."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/praca-de-pedagio"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal (a cobertura temporal é anual)"
  cobertura: {inicio: "2026", fim: 2026}
  unidade: "uma praça de pedágio (por concessionária, rodovia, quilômetro e sentido)"
  granularidade: {espacial: "praça de pedágio (coordenadas, com UF e município)", temporal: "instantâneo; sem série temporal"}
  formato_bruto: "CSV único, Windows-1252, separador ponto e vírgula"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 13}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Praças de pedágio

## Resumo

Cadastro das praças de pedágio das rodovias federais concedidas, registrado no Sistema de Informação de Rodovias da ANTT. Serve para localizar as praças e ligar o tráfego (dataset `volume-trafego-praca-pedagio`) à rodovia e ao quilômetro.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/praca-de-pedagio` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/praca-de-pedagio |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal (a cobertura temporal é anual) |
| Cobertura | 2026 a 2026 |
| Unidade (uma linha) | uma praça de pedágio (por concessionária, rodovia, quilômetro e sentido) |
| Granularidade | espacial: praça de pedágio (coordenadas, com UF e município); temporal: instantâneo; sem série temporal |
| Formato bruto | CSV único, Windows-1252, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 13 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa o CSV `dados-dos-praas-de-pedgio.csv` do pacote `praca-de-pedagio` (`https://dados.antt.gov.br/dataset/praca-de-pedagio`); o pacote traz também um KMZ, não baixado.
- No bruto: `praca-de-pedagio@AAAAMMDD.csv`, com manifesto. Conferido em 2026-11-10: 1 arquivo, `@20261103` (35 KB).

## Conteúdo

- Unidade de análise: uma praça (a combinação concessionária, praça, rodovia, quilômetro e sentido é única nas 289 linhas).
- Cobertura: instantâneo de 2026-11-03. O campo `ano_do_pnv_snv` vai de 1996 a 2025 e não é o ano do registro.
- Layout: 13 colunas.
- Nulos (arquivo inteiro): `data_da_inativacao` nula em 285 das 289 linhas (98,6%); as 4 preenchidas estão em linhas com `situacao = Ativo`, contradizendo o dicionário (inativação com situação inativa).

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Dados dos Praças de Pedágio"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `concessionaria` | `concessionaria` | texto | Nome da concessionária que prestou as informações | — | todo |
| `praca_de_pedagio` | `praca_de_pedagio` | texto | Nome da praça de pedágio (o dicionário usa `praça_de_pedágio`) | — | todo |
| `ano_do_pnv_snv` | `ano_do_pnv_snv` | texto | Ano que representa as informações no Plano Nacional de Viação e Sistema Nacional de Viação (versão do mapa da malha, não o ano do registro) | `aaaa`; 1996 a 2025 | todo |
| `rodovia` | `rodovia` | texto | Rodovia responsável pela concessionária | `BR-116`; também `Saída para BR-153` (valor livre) | todo |
| `uf` | `uf` | texto | Sigla do estado da rodovia | sigla de 2 letras | todo |
| `km_m` | `km_m` | texto | Quilômetro mais a metragem. O dicionário dá `317,940`; o arquivo traz ponto decimal (`40.5`) | km | todo |
| `municipal` | `Município` | texto | Município da localização. A coluna se chama `municipal` no arquivo (o dicionário a chama `Município`) | — | todo |
| `tipo_de_pista` | `tipo_de_pista` | texto | Tipo da pista onde a praça está localizada | `Principal` (único valor conferido) | todo |
| `sentido` | `sentido` | texto | Ordem crescente ou decrescente, ou ambas | `Crescente`, `Decrescente`, `Crescente/Decrescente` | todo |
| `situacao` | `situacao` | texto | Situação atual | `Ativo` (único valor conferido; o dicionário prevê `inativo`) | todo |
| `data_da_inativacao` | `data_da_inativacao` | texto | Data de registro, caso a situação seja inativo | ISO com fuso (`2026-05-07T00:00:00-03:00`) | todo |
| `latitude` | `latitude` | texto | Latitude | graus decimais com ponto | todo |
| `longitude` | `longitude` | texto | Longitude | graus decimais com ponto | todo |

## No lake

- Dataset `antt/praca-de-pedagio`, particionado por `ano`, um Parquet (`praca-de-pedagio_<id8>.parquet`, em que `<id8>` são os 8 primeiros caracteres do id do recurso na URL do manifesto).
- Dataset de fotografia sem período no nome: o `ano` é o do carimbo `@AAAAMMDD` do nome do arquivo (2026), com aviso no log, e não descarta linhas. `ano_do_pnv_snv` não serve de partição.
- Todas as colunas são texto.
- Esquema de referência (`praca-de-pedagio.schema.json`): 13 colunas, gerado da conversão do arquivo inteiro.

## Cuidados de uso

- **`ano` do lake é o da coleta**, não de uma data do dado; uma nova fotografia cairá em outro `ano` ou substituirá esta, conforme o carimbo.
- **Inativação em praça ativa.** Quatro praças com `situacao = Ativo` têm `data_da_inativacao` preenchida (2024-07-26, 2026-05-07 e 2026-05-22); a fonte não explica.
- **Rodovia livre.** `rodovia` tem valores como `Saída para BR-153`; não é só `BR-nnn`.
- **Coluna `municipal`.** O dicionário diz `Município`; o arquivo traz `municipal`.

## Exemplos

Praças por UF e concessionária:

```python
import polars as pl

p = pl.scan_parquet("lake/antt/praca-de-pedagio/ano=2026/*.parquet")
resumo = (
    p.group_by("uf", "concessionaria")
    .agg(pl.len().alias("pracas"))
    .sort("uf", "concessionaria")
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/praca-de-pedagio
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Dados dos Praças de Pedágio"
