---
dataset:
  id: "relatorio-acompanhamento-acidentes-ferroviarios-raaf"
  fonte: "antt"
  titulo: "Acidentes ferroviários (RAAF)"
  resumo: "Registros de acidentes nos trechos concedidos às operadoras ferroviárias (Relatório de Acompanhamento de Acidentes Ferroviários) e índice anual de acidentes por concessionária."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "semestral segundo o portal"
  cobertura: {inicio: "2004", fim: em-curso}
  unidade: "um acidente ferroviário (tabela de acidentes) ou o índice anual de uma concessionária (tabela de índice)"
  granularidade: {espacial: "linha ferroviária, município e UF", temporal: "ocorrência (data e hora); ano no índice"}
  formato_bruto: "CSV, Windows-1252, separador ponto e vírgula, campos de texto entre aspas e números sem aspas"
  lake: {estado: so-bruto, particoes: ["ano"], chave: [], colunas: null}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras:
    - {desde: "2020-12", mudanca: "o layout de acidentes ganha `Quilômetro_Final`, `Causa_contibutiva`, `N_Trem`, `Double_Stack` e `Prejuízo_Financeiro` (27 colunas, antes 22)"}
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Acidentes ferroviários (RAAF)

## Resumo

Registros de acidentes ocorridos nos trechos concedidos às operadoras ferroviárias, com o processo de monitoramento e análise do Sistema de Acompanhamento de Fiscalização do Transporte Ferroviário (SAFF), mais o índice anual de acidentes por milhão de trem-km. **O conversor declara este dataset, mas hoje nenhuma linha chega ao lake**: os arquivos do bruto usam o slug do pacote (`relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf`) e o conversor procura outro id (`relatorio-acompanhamento-acidentes-ferroviarios-raaf`).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/relatorio-acompanhamento-acidentes-ferroviarios-raaf` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | semestral segundo o portal |
| Cobertura | 2004 a em-curso |
| Unidade (uma linha) | um acidente ferroviário (tabela de acidentes) ou o índice anual de uma concessionária (tabela de índice) |
| Granularidade | espacial: linha ferroviária, município e UF; temporal: ocorrência (data e hora); ano no índice |
| Formato bruto | CSV, Windows-1252, separador ponto e vírgula, campos de texto entre aspas e números sem aspas |
| Estado no lake | so-bruto |
| Partições | `ano` |
| Chave | — |
| Colunas | — |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | 2020-12: o layout de acidentes ganha `Quilômetro_Final`, `Causa_contibutiva`, `N_Trem`, `Double_Stack` e `Prejuízo_Financeiro` (27 colunas, antes 22) |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os recursos CSV do pacote `relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf` (`https://dados.antt.gov.br/dataset/relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf`): "Índice de Acidentes Ferroviários de 2006 a 2019" e "Acidentes Ferroviários - Dezembro de 2020 em diante" (5 CSV e 5 JSON no catálogo).
- No bruto: `relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf@AAAAMMDD.csv` (nome nu) e `..._<recurso>-<id>@AAAAMMDD.csv`. Conferido em 2026-11-10 pela listagem do bruto: 7 arquivos.
- O nome nu foi usado por recursos diferentes: `@20231130` (acidentes de 2004 a nov/2020, 22 colunas, 10.824 linhas), `@20250710` e `@20260410` (acidentes de dez/2020 em diante, 27 colunas, 3.305 e 3.710 linhas).

## Conteúdo

- Unidade de análise: um acidente (tabela de acidentes) ou um par concessionária e ano (índice, 182 linhas na versão de julho de 2025). O arquivo de índice de 2026 (`...8f8f2a80@20260410`) tem só o cabeçalho, sem linhas.
- Cobertura: acidentes de 2004 a nov/2020 no arquivo de 2023 e de dez/2020 em diante nos de 2025 e 2026; índice de 2006 a 2019.
- Eras: 22 colunas até nov/2020 e 27 a partir de dez/2020 (o dicionário também tem duas versões).
- Nada foi convertido pelo lake real. Para testar o layout, os arquivos foram copiados com o id esperado pelo conversor, sob outro nome, numa conversão local; mesmo assim só o nome nu mais recente (`@20260410`) é lido (as partições de 2020 a 2026), porque o arquivo de 2004 a 2020 (`@20231130`) tem o mesmo nome nu e é considerado superado.

## Variáveis

Colunas dos CSV do bruto (normalizadas como o conversor faria) e descrições do dicionário de dados da ANTT (dois PDFs de acidentes; o PDF do índice repete o texto do de 2004 a 2020 e não descreve as colunas do índice). O dataset não está no lake, então a tabela não é verificada contra um esquema de referência.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `gravidade` | `Gravidade` | texto | Descreve a magnitude ou seriedade do acidente ferroviário | `Sim`/`Não` nas linhas conferidas (a fonte não define os valores) | todas as tabelas de acidentes |
| `concessionaria` | `Concessionaria` | texto | Abreviação do nome da empresa responsável pela operação da ferrovia (no índice, a concessionária do índice) | `FCA`, `FTL`, `EFC`… (conferido) | todas |
| `data_ocorrencia` | `Data_Ocorrencia` | texto | A data em que o acidente ferroviário ocorreu | `dd/mm/aaaa` | acidentes |
| `hora_ocorrencia` | `Hora_Ocorrencia` | texto | O horário exato em que o acidente ferroviário ocorreu | `hh:mm` | acidentes |
| `uf` | `UF` | texto | O estado ou unidade federativa em que o acidente ocorreu | sigla de 2 letras | acidentes |
| `municipio` | `Municipio` | texto | Município (o dicionário diz "a região geográfica onde o acidente ocorreu") | — | acidentes |
| `linha` | `Linha` | texto | Indica a linha da ferrovia em que o acidente ocorreu | — | acidentes |
| `quilometro_inicial` | `Quilômetro_Inicial` | texto | Localização do ponto de início do acidente na linha, em quilômetros a partir do ponto de referência | km | acidentes |
| `quilometro_final` | `Quilômetro_Final` | texto | Ponto final do acidente na linha, em quilômetros a partir do ponto de referência | km | acidentes a partir de dez/2020 |
| `estacao_anterior` | `Estação_Anterior` | texto | Nome da estação ferroviária antes do local do acidente | — | acidentes |
| `estacao_posterior` | `Estação_Posterior` | texto | Nome da estação para a qual os trens se dirigiam a partir do ponto do acidente | — | acidentes |
| `perimetro_urbano` | `Perímetro_Urbano` | texto | Indica se o acidente ocorreu em área urbana | `Sim`/`Não` | acidentes |
| `causa_direta` | `Causa_direta` | texto | A razão primária que levou ao acidente | — | acidentes |
| `causa_contibutiva` | `Causa_contibutiva` | texto | Detalhes adicionais sobre a causa do acidente (grafia "contibutiva" da fonte) | — | acidentes a partir de dez/2020 |
| `natureza` | `Natureza` | texto | A classificação que descreve a natureza do acidente | — | acidentes |
| `interrupcao` | `Interrupção` | texto | Se o acidente resultou na paralisação total ou parcial do tráfego (o dicionário a trata como numérica) | — | acidentes |
| `n_trem` | `N_Trem` | texto | Quantos trens estiveram envolvidos diretamente no acidente | trens | acidentes a partir de dez/2020 |
| `prefixo` | `Prefixo` | texto | Composição ou comboio de trens envolvidos, por código ou prefixo | — | acidentes |
| `double_stack` | `Double_Stack` | texto | Se os vagões eram do tipo Double Stack | — | acidentes a partir de dez/2020 |
| `servico_transporte` | `Serviço_Transporte` | texto | Tipo de serviço ferroviário (carga, passageiros ou outro) | — | acidentes |
| `n_feridos` | `N_feridos` | texto | Número de pessoas que sofreram ferimentos | pessoas | acidentes |
| `n_obitos` | `N_obitos` | texto | Número de vítimas fatais | pessoas | acidentes |
| `mercadoria` | `Mercadoria` | texto | Tipo de carga ou mercadoria transportada no momento do acidente | — | acidentes |
| `equipagem` | `Equipagem` | texto | O dicionário diz "o nome do maquinista ou condutor"; nas linhas conferidas o campo vem vazio | — | acidentes |
| `outra_ferrovia` | `Outra_Ferrovia` | texto | Concessionária da outra ferrovia, quando a linha é compartilhada (direito de passagem ou tráfego mútuo) | — | acidentes |
| `pn` | `PN` | texto | Se o acidente ocorreu em Passagem em Nível | `Sim`/`Não` | acidentes |
| `prejuizo_financeiro` | `Prejuízo_Financeiro` | texto | Estimativa do dano financeiro do acidente (infraestrutura, limpeza, perda de mercadoria, despesas médicas etc.) | texto com vírgula decimal (`918,00`); unidade não informada pela fonte | acidentes a partir de dez/2020 |
| `ano` | `ano` | texto | Ano do índice de acidentes | ano de 4 dígitos | índice de acidentes |
| `indice_de_acidentes_por_milhao_de_trem_km` | `indice_de_acidentes_por_milhao_de_trem_km` | texto | Índice de acidentes por milhão de trem-km (nome da coluna; o dicionário publicado não cobre esta tabela) | acidentes por milhão de trem-km | índice de acidentes |

## No lake

- Estado: `so-bruto`. Não há dataset `antt/relatorio-acompanhamento-acidentes-ferroviarios-raaf` no lake e não há esquema de referência.
- Causa: `_detect_dataset_id` devolve `None` para todo nome com slug de pacote do catálogo que não seja um id do lake (`relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf` está no catálogo e não está em `DATASETS`). O `inventory()` lista os 7 arquivos sem conjunto e sem motivo (lacuna de cobertura).
- Se os arquivos fossem lidos, o conversor os particionaria por `ano` a partir de `data_ocorrencia`, tudo em texto. Três tabelas de layouts diferentes (22, 27 e 3 colunas) cairiam no mesmo dataset.

## Cuidados de uso

- **Nenhuma linha chega ao lake.** Evidência (versão 0.3.2, 2026-11-10): os 7 arquivos do bruto não têm conjunto no `inventory()`; os mesmos arquivos, renomeados para o id do conversor, geram 7 partições (2020 a 2026) só do arquivo mais novo.
- **Três tabelas num dataset.** Acidentes até nov/2020, acidentes de dez/2020 em diante e índice teriam esquemas distintos (22, 27 e 3 colunas).
- **Índice vazio em 2026.** O recurso do índice na versão de abril de 2026 tem só o cabeçalho.
- **Dicionário imperfeito.** O dicionário descreve `Municipio` como "a região geográfica", `Interrupção` como numérica e `Equipagem` como nome do maquinista; nas linhas conferidas `Interrupção` é um número decimal (por exemplo `20.0`) e `Equipagem` vem vazio.
- **Pessoais.** O campo `Equipagem` seria nome de maquinista segundo o dicionário; vem vazio nas linhas conferidas.

## Exemplos

Ainda não há dados no lake para este dataset. Com o arquivo bruto aberto diretamente, acidentes por concessionária desde dezembro de 2020 (exemplo de leitura do CSV da fonte, não do lake):

```python
import polars as pl

ac = pl.read_csv(
    "relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf@20260410.csv",
    separator=";", encoding="cp1252", infer_schema=False,
)
resumo = ac.group_by("Concessionaria").agg(pl.len().alias("acidentes")).sort("acidentes", descending=True)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf
- Dicionários de dados (PDF), no pacote: "Índice de Acidentes Ferroviários de 2006 a 2019", "Acidentes Ferroviários - 2004 a novembro de 2020" e "Acidentes Ferroviários - Dezembro de 2020 a julho de 2024"
