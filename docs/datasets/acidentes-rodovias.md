---
dataset:
  id: "acidentes-rodovias"
  fonte: "antt"
  titulo: "Acidentes nas rodovias concedidas (demonstrativos de acidentes)"
  resumo: "Ocorrências de acidentes registradas pelas concessionárias de rodovias federais, uma linha por ocorrência, com tipo, local, veículos envolvidos e vítimas."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/acidentes-rodovias"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "trimestral segundo o portal"
  cobertura: {inicio: "2015", fim: em-curso}
  unidade: "uma ocorrência de acidente registrada por uma concessionária"
  granularidade: {espacial: "quilômetro da rodovia (trecho e sentido), por concessionária", temporal: "ocorrência (data e hora)"}
  formato_bruto: "CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 24}
  unidades_de_medida: {automovel: "veículos", bicicleta: "veículos", caminhao: "veículos", moto: "veículos", onibus: "veículos", outros: "veículos", tracao_animal: "veículos", transporte_de_cargas_especiais: "veículos", trator_maquinas: "veículos", utilitarios: "veículos", ilesos: "pessoas", levemente_feridos: "pessoas", moderadamente_feridos: "pessoas", gravemente_feridos: "pessoas", mortos: "pessoas"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Acidentes nas rodovias concedidas (demonstrativos de acidentes)

## Resumo

Registros de acidentes informados pelas concessionárias de rodovias federais à ANTT (Superintendência de Infraestrutura Rodoviária). Cada concessionária publica o seu CSV, e o dataset reúne todos num só layout. Serve para contar ocorrências, vítimas e veículos por trecho, tipo de acidente e período.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/acidentes-rodovias` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/acidentes-rodovias |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | trimestral segundo o portal |
| Cobertura | 2015 a em-curso |
| Unidade (uma linha) | uma ocorrência de acidente registrada por uma concessionária |
| Granularidade | espacial: quilômetro da rodovia (trecho e sentido), por concessionária; temporal: ocorrência (data e hora) |
| Formato bruto | CSV (cada recurso do pacote é um arquivo), Windows-1252 na maior parte (alguns UTF-8), separador ponto e vírgula, texto entre aspas só em parte dos arquivos |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 24 |
| Unidades de medida | `automovel`: veículos; `bicicleta`: veículos; `caminhao`: veículos; `moto`: veículos; `onibus`: veículos; `outros`: veículos; `tracao_animal`: veículos; `transporte_de_cargas_especiais`: veículos; `trator_maquinas`: veículos; `utilitarios`: veículos; `ilesos`: pessoas; `levemente_feridos`: pessoas; `moderadamente_feridos`: pessoas; `gravemente_feridos`: pessoas; `mortos`: pessoas |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os CSV do pacote `acidentes-rodovias` do portal de dados abertos da ANTT (`https://dados.antt.gov.br/dataset/acidentes-rodovias`): um recurso por concessionária (44 CSV), mais o dicionário de dados e o painel.
- No bruto: `acidentes-rodovias_<recurso>-<id>@AAAAMMDD.csv` (data da última modificação na fonte); alguns arquivos antigos têm o nome nu `acidentes-rodovias@AAAAMMDD.csv`.
- Conferido em 2026-11-10 pela listagem do bruto: 44 arquivos de dados (133 MB), 43 vigentes, um por recurso (o que fica de fora é um arquivo de nome nu sem manifesto, superado pela regra do nome); 2 manifestos (`nova-rota`, `elovias` entre outros) sem arquivo no bruto conferido.

## Conteúdo

- Unidade de análise: uma ocorrência de uma concessionária. Chave não verificada (o `n_da_ocorrencia` é controle da concessionária, não único entre elas).
- Cobertura: as partições vão de 2015 a 2026 (amostra de 6 arquivos; 2015 é o ano mais antigo visto, o resto da cobertura depende do arquivo de cada concessionária).
- Layout: 24 colunas em quase todos os arquivos; dois arquivos de nome nu (`@20251128` e `@20260628`) têm 23, sem `tipo_de_pista`. Nenhuma outra quebra foi vista (cabeçalho conferido nos 43 vigentes).
- Nulos (amostra de 14.854 linhas de 6 arquivos): `tipo_de_pista` é nulo em 28,2% (os arquivos que a trazem em branco) e `sentido` em 1 linha; os demais campos não têm nulo. Sem perda de linhas: o lake tem as linhas dos CSV menos o cabeçalho.

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Acidentes"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `data` | `data` | texto | Data de referência da ocorrência. O dicionário dá o formato `DD/MM/AA`; nos arquivos conferidos vem `dd/mm/aaaa` | `dd/mm/aaaa` | todo |
| `horario` | `horario` | texto | Horário de registro da ocorrência | `hh:mm:ss` | todo |
| `n_da_ocorrencia` | `n_da_ocorrencia` | texto | Número de controle da ocorrência da concessionária | — | todo |
| `tipo_de_ocorrencia` | `tipo_de_ocorrencia` | texto | Informação se houve ou não vítima na ocorrência. Nas amostras vem com 10 valores distintos (`com vítima`, `sem vítima` e códigos como `AC03 - Aci...`), conforme a concessionária | — | todo |
| `km` | `km` | texto | Marco quilométrico de onde ocorreu o fato. Formato livre (`334`, `334,5`) | km | todo |
| `trecho` | `trecho` | texto | Representação da rodovia e do estado do trecho, `BR-116/SP` segundo o dicionário; nas amostras também vem como `317/PR` ou códigos como `N04` | — | todo |
| `sentido` | `sentido` | texto | Orientação de direção geral que indica o sentido da pista; nas amostras: `Norte`, `Sul`, `Crescente`, `Todos` e outros (6 valores) | — | todo |
| `tipo_de_acidente` | `tipo_de_acidente` | texto | Classificação que indica o tipo de acidente; 60 valores distintos na amostra, sem lista padronizada | — | todo |
| `automovel` | `automovel` | texto | Quantidade de automóveis envolvidos na ocorrência | veículos | todo |
| `bicicleta` | `bicicleta` | texto | Quantidade de bicicletas envolvidas | veículos | todo |
| `caminhao` | `caminhao` | texto | Quantidade de caminhões envolvidos | veículos | todo |
| `moto` | `moto` | texto | Quantidade de motocicletas envolvidas | veículos | todo |
| `onibus` | `onibus` | texto | Quantidade de ônibus envolvidos | veículos | todo |
| `outros` | `outros` | texto | Quantidade de outros veículos envolvidos | veículos | todo |
| `tracao_animal` | `tracao_animal` | texto | Quantidade de veículos de tração animal envolvidos | veículos | todo |
| `transporte_de_cargas_especiais` | `transporte_de_cargas_especiais` | texto | Quantidade de veículos de transporte de cargas especiais envolvidos | veículos | todo |
| `trator_maquinas` | `trator_maquinas` | texto | Quantidade de tratores e máquinas envolvidos | veículos | todo |
| `utilitarios` | `utilitarios` | texto | Quantidade de utilitários envolvidos | veículos | todo |
| `ilesos` | `ilesos` | texto | Número de ilesos (sem lesão ou ferimentos) | pessoas | todo |
| `levemente_feridos` | `levemente_feridos` | texto | Número de pessoas com lesão ou ferimentos leves | pessoas | todo |
| `moderadamente_feridos` | `moderadamente_feridos` | texto | Número de pessoas com lesão ou ferimentos moderados | pessoas | todo |
| `gravemente_feridos` | `gravemente_feridos` | texto | Número de pessoas com lesão ou ferimentos graves | pessoas | todo |
| `mortos` | `mortos` | texto | Número de óbitos da ocorrência | pessoas | todo |
| `tipo_de_pista` | `tipo_de_pista` | texto | Tipo da pista. Não consta do dicionário da ANTT (não informado pela fonte); nas amostras vale `Principal` ou `Marginal`, e a coluna falta em um dos arquivos de nome nu | `Principal`, `Marginal` | quase todos os arquivos |

## No lake

- Dataset `antt/acidentes-rodovias`, particionado por `ano`, um Parquet por arquivo de origem (um por concessionária). O nome do Parquet é `acidentes-rodovias_<id8>.parquet`, em que `<id8>` são os 8 primeiros caracteres do id do recurso na URL do manifesto (a chave vem do recurso, não do nome do arquivo).
- `ano` vem de `data` (grupo de 4 dígitos). Data com ano de 2 dígitos (o dicionário fala em `DD/MM/AA`) não gera ano e a linha iria para a partição `__HIVE_DEFAULT_PARTITION__`; não houve nas amostras.
- Todas as colunas são texto; arquivos com aspas internas soltas são reparados (`"barreira ou "submarino"`), com aviso no log.
- Esquema de referência (`acidentes-rodovias.schema.json`): 24 colunas, gerado de 6 arquivos de amostra.

## Cuidados de uso

- **Recursos de nome nu se somam aos demais.** O bruto tem arquivos de nome nu (`acidentes-rodovias@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote (aqui, `@20251128` é o recurso `demostrativo_acidentes_eco101.csv`, 5,7 MB, e `@20260628` o `demostrativo_acidentes_viamineira.csv`). A versão vigente é escolhida por recurso (URL do manifesto ao lado), então os dois entram, cada um no seu Parquet (`acidentes-rodovias_<id8>.parquet`). Um arquivo de nome nu sem manifesto ao lado segue a regra do nome (só o mais recente de cada nome); no bruto conferido, `acidentes-rodovias@20260928.csv` está nesse caso.
- **Manifestos sem arquivo.** Dois manifestos do pacote não têm o CSV correspondente no bruto conferido (Nova Rota do Oeste, entre outros).
- **Valores livres entre concessionárias.** `tipo_de_ocorrencia`, `trecho`, `km` e `sentido` não seguem um padrão comum (códigos `AC03 - ...`, `N04`, `334,5`); normalize antes de agregar entre concessionárias.
- **Dicionário diverge dos dados.** O dicionário diz `DD/MM/AA` para `data` e os arquivos trazem ano de 4 dígitos; `tipo_de_pista` existe nos arquivos e não no dicionário.

## Exemplos

Ocorrências e mortos por ano e concessionária-arquivo (a coluna de concessionária não existe; use o nome do arquivo de origem se precisar):

```python
import polars as pl

ac = pl.scan_parquet("lake/antt/acidentes-rodovias/ano=*/*.parquet", include_file_paths="arquivo")
resumo = (
    ac.with_columns(mortos=pl.col("mortos").cast(pl.Int64))
    .group_by("arquivo")
    .agg(pl.len().alias("ocorrencias"), pl.col("mortos").sum())
    .collect()
)
```

O exemplo mostra o padrão de leitura; foi validado sobre a conversão de amostra de 2026-11-10 (14.854 linhas).

## Referências

- Pacote: https://dados.antt.gov.br/dataset/acidentes-rodovias
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Acidentes"
