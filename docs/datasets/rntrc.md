---
dataset:
  id: "rntrc"
  fonte: "antt"
  titulo: "RNTRC — Registro Nacional de Transportadores Rodoviários de Cargas"
  resumo: "Cadastro dos transportadores rodoviários de cargas habilitados a fazer transporte remunerado, uma linha por transportador, com situação, categoria e município."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/rntrc"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal"
  cobertura: {inicio: "2020", fim: em-curso}
  unidade: "um transportador inscrito no RNTRC, na data do arquivo mensal"
  granularidade: {espacial: "município do transportador (com UF e CEP)", temporal: "instantâneo mensal (um arquivo por mês)"}
  formato_bruto: "CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos; campos entre aspas, com aspas simples duplas no nome em alguns casos"
  lake: {estado: convertido, particoes: ["ano"], chave: ["ano", "numero_rntrc"], colunas: 12}
  unidades_de_medida: null
  dados_pessoais:
    - {coluna: "nome_transportador", categoria: "nome (pessoa física no caso de TAC)"}
    - {coluna: "cpfcnpjtransportador", categoria: "CPF mascarado ou CNPJ"}
    - {coluna: "cep", categoria: "endereço (CEP)"}
    - {coluna: "municipio", categoria: "endereço (município)"}
    - {coluna: "uf", categoria: "endereço (UF)"}
    - {coluna: "numero_rntrc", categoria: "identificador do transportador"}
  eras:
    - {desde: "2024-05", mudanca: "o layout passa de 5 para 11 colunas: saem `validade_rntrc` e ficam `nome_transportador`, `numero_rntrc`, `data_primeiro_cadastro` e `situacao_rntrc`; entram `cpfcnpjtransportador`, `categoria_transportador`, `cep`, `municipio`, `uf`, `equiparado` e `data_situacao_rntrc`"}
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# RNTRC — Registro Nacional de Transportadores Rodoviários de Cargas

## Resumo

Fotografia mensal do Registro Nacional de Transportadores Rodoviários de Cargas (RNTRC), mantido pela ANTT. Cada arquivo traz todos os transportadores inscritos naquele mês. Serve para contar transportadores por categoria, situação e município.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/rntrc` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/rntrc |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal |
| Cobertura | 2020 a em-curso |
| Unidade (uma linha) | um transportador inscrito no RNTRC, na data do arquivo mensal |
| Granularidade | espacial: município do transportador (com UF e CEP); temporal: instantâneo mensal (um arquivo por mês) |
| Formato bruto | CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos; campos entre aspas, com aspas simples duplas no nome em alguns casos |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `ano`, `numero_rntrc` |
| Colunas | 12 |
| Unidades de medida | — |
| Dados pessoais | `nome_transportador` (nome (pessoa física no caso de TAC)); `cpfcnpjtransportador` (CPF mascarado ou CNPJ); `cep` (endereço (CEP)); `municipio` (endereço (município)); `uf` (endereço (UF)); `numero_rntrc` (identificador do transportador) |
| Eras | 2024-05: o layout passa de 5 para 11 colunas: saem `validade_rntrc` e ficam `nome_transportador`, `numero_rntrc`, `data_primeiro_cadastro` e `situacao_rntrc`; entram `cpfcnpjtransportador`, `categoria_transportador`, `cep`, `municipio`, `uf`, `equiparado` e `data_situacao_rntrc` |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os CSV mensais do pacote `rntrc` (`https://dados.antt.gov.br/dataset/rntrc`), que tem um recurso `transportadores_rntrc_MM_AAAA.csv` por mês desde agosto de 2020 (73 CSV).
- No bruto o nome é `rntrc@AAAAMMDD.csv` (data da última modificação na fonte), com manifesto ao lado que guarda a URL de origem.
- O pacote tem 71 recursos mensais, de 08/2020 a 09/2026, sem os meses 11/2022, 07/2024 e 02/2025. Cada recurso é um mês, não uma versão do outro: todos são vigentes e cada um vira o seu Parquet. No bruto os arquivos antigos têm todos o mesmo nome nu (`rntrc@AAAAMMDD.csv`), e é o manifesto, com a URL de cada mês, que os distingue.

## Conteúdo

- Unidade de análise: um transportador (`numero_rntrc` é único no arquivo conferido: 1.189.325 distintos em 1.189.325 linhas).
- Cobertura anunciada pela fonte: agosto de 2020 em diante, mensal. O que chega ao lake: as **71 fotografias mensais** de 08/2020 a 09/2026, cada uma no `ano` do seu mês (veja os cuidados de uso).
- Layout: 5 colunas (`nome_transportador`, `numero_rntrc`, `data_primeiro_cadastro`, `validade_rntrc`, `situacao_rntrc`) nos 44 arquivos de 08/2020 a 04/2024 e 11 colunas nos 27 de 05/2024 em diante (conferido pelo cabeçalho dos 71 arquivos); o lake tem a união, 12 colunas.
- Nulos (arquivo de setembro de 2026 inteiro, 1.189.325 linhas; os arquivos até 04/2024 não têm essas colunas): `municipio` e `uf` nulos em 127 linhas; nenhum outro campo nulo. `cep` tem 354 valores de 1 caractere (vazios na prática). 912.543 `ATIVO` e 276.782 `PENDENTE`.

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - RNTRC", cujo cabeçalho ainda traz o texto-modelo "Nome da Base de Dados"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `nome_transportador` | `nome_transportador` | texto | Nome do transportador | — | todo |
| `numero_rntrc` | `numero_rntrc` | texto | Número do RNTRC do transportador | 9 dígitos; único no arquivo conferido | todo |
| `data_primeiro_cadastro` | `data_primeiro_cadastro` | texto | Data em que o transportador efetuou o primeiro cadastro no RNTRC | `dd/mm/aaaa` | todo |
| `validade_rntrc` | `validade_rntrc` | texto | Data de validade do RNTRC (pelo nome da coluna; não consta do dicionário de 11 colunas conferido) | `dd/mm/aaaa` | até 04/2024 |
| `situacao_rntrc` | `situacao_rntrc` | texto | Situação do RNTRC (ex.: Ativo, Pendente) | `ATIVO`, `PENDENTE` (conferido) | todo |
| `cpfcnpjtransportador` | `cpfcnpjtransportador` | texto | Número de inscrição no CPF (anonimizado, segundo o dicionário) ou no CNPJ do transportador | CNPJ completo (`99.999.999/9999-99`) ou CPF mascarado (`999.***.***-99`) | 05/2024 em diante |
| `categoria_transportador` | `categoria_transportador` | texto | Categoria do transportador | `ETC` Empresa de Transporte Rodoviário de Cargas; `CTC` Cooperativa de Transporte Rodoviário de Cargas; `TAC` Transportador Autônomo de Cargas | 05/2024 em diante |
| `cep` | `cep` | texto | Código postal | `99999-999` | 05/2024 em diante |
| `municipio` | `municipio` | texto | Nome do município | — | 05/2024 em diante |
| `uf` | `uf` | texto | Sigla da unidade federativa | sigla de 2 letras | 05/2024 em diante |
| `equiparado` | `equiparado` | texto | Transportador ETC com até 3 veículos automotores na frota | `Sim`, `Não` (o dicionário diz `SIM`/`NÃO`) | 05/2024 em diante |
| `data_situacao_rntrc` | `data_situacao_rntrc` | texto | Data da última atualização da situação no RNTRC | `dd/mm/aaaa` | 05/2024 em diante |

## No lake

- Dataset `antt/rntrc`, particionado por `ano`, um Parquet por arquivo de origem (um por mês). O nome do Parquet é `rntrc_<id8>.parquet`, em que `<id8>` são os 8 primeiros caracteres do id do recurso na URL do manifesto (por exemplo `rntrc_c77e6837.parquet` para setembro de 2026).
- Dataset de fotografia (`SNAPSHOT_DATASETS`): o `ano` vem do período no nome original do recurso na URL do manifesto (`transportadores_rntrc_09_2026.csv` dá 2026), não de uma coluna. Sem manifesto, a conversão falha em vez de inventar o ano.
- Todas as colunas são texto. Arquivos sem campos entre aspas no início são lidos sem aspas; aspas soltas no dado (`D"AVILA`) são reparadas.
- Esquema de referência (`rntrc.schema.json`): 12 colunas, gerado da conversão do cabeçalho e das primeiras linhas dos 71 arquivos (os dois layouts); o arquivo de setembro de 2026 foi convertido inteiro à parte.

## Cuidados de uso

- **Uma fotografia por mês, sem coluna de mês.** Cada Parquet é o retrato de um mês inteiro e o `ano` da partição vem do período do arquivo (não de uma coluna), então uma partição `ano` reúne até 12 retratos do mesmo universo de transportadores: um transportador aparece uma vez por mês, e somar ou contar a partição inteira conta cada um várias vezes. O mês só aparece no arquivo de origem (nome do Parquet e metadados do arquivo), não como coluna: para uma fotografia só, leia um Parquet (`rntrc_<id8>.parquet`) e não a partição.
- **Meses ausentes e arquivos pequenos.** Faltam no pacote os meses 11/2022, 07/2024 e 02/2025. O recurso de 08/2023 tem só o cabeçalho (85 bytes, nenhuma linha, então não gera Parquet) e o de 07/2022 tem 10 MB, contra 75 a 78 MB nos vizinhos (conteúdo não investigado).
- **Dado pessoal.** `nome_transportador` é o nome da pessoa física quando a categoria é `TAC`, e o CPF vem mascarado (`999.***.***-99`; 846.664 linhas), mas nome, CEP e município juntos identificam a pessoa. Nove linhas `TAC` têm CNPJ truncado (`99.999.999/999 -`).
- **Situação `PENDENTE`.** 23% dos registros (276.782) estão pendentes; filtre `situacao_rntrc = "ATIVO"` para transportadores ativos.
- **Texto do nome.** Há nomes com aspas simples duplicadas (`'' DPS LOGISTICA LTDA ''`).

## Exemplos

Transportadores ativos por categoria e UF no instantâneo de setembro de 2026 (um Parquet, não a partição inteira):

```python
import polars as pl

r = pl.scan_parquet("lake/antt/rntrc/ano=2026/rntrc_c77e6837.parquet")
resumo = (
    r.filter(pl.col("situacao_rntrc") == "ATIVO")
    .group_by("categoria_transportador", "uf")
    .agg(pl.len().alias("transportadores"))
    .sort("transportadores", descending=True)
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/rntrc
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - RNTRC"
