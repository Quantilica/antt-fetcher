---
dataset:
  id: "monitriip-servico-regular-paradas"
  fonte: "antt"
  titulo: "Monitriip — serviço regular, paradas"
  resumo: "Paradas das viagens do transporte rodoviário regular interestadual e internacional de passageiros, registradas pelo equipamento embarcado do Monitriip, uma linha por parada."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/monitriip-servico-regular-paradas"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal, a partir da segunda quinzena do mês, segundo o portal"
  cobertura: {inicio: "2019", fim: em-curso}
  unidade: "uma parada de uma viagem do serviço regular, com posição e horário"
  granularidade: {espacial: "ponto de parada (latitude e longitude)", temporal: "instante da parada (data e hora)"}
  formato_bruto: "CSV por mês (um recurso por mês), UTF-8, separador ponto e vírgula"
  lake: {estado: convertido, particoes: ["ano"], chave: [], colunas: 14}
  unidades_de_medida: null
  dados_pessoais:
    - {coluna: "placa", categoria: "placa do veículo (identifica o veículo e, indiretamente, o motorista)"}
    - {coluna: "numero_imei", categoria: "identificador do equipamento"}
    - {coluna: "latitude", categoria: "localização"}
    - {coluna: "longitude", categoria: "localização"}
    - {coluna: "codigo_viagem", categoria: "identificador da viagem"}
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Monitriip — serviço regular, paradas

## Resumo

Paradas das viagens do serviço regular de transporte rodoviário interestadual e internacional coletivo de passageiros, coletadas pelo Monitriip (Sistema de Monitoramento do Transporte Rodoviário Interestadual e Internacional Coletivo de Passageiros) da ANTT. Cada linha é uma parada com posição, motivo e horário.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/monitriip-servico-regular-paradas` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/monitriip-servico-regular-paradas |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal, a partir da segunda quinzena do mês, segundo o portal |
| Cobertura | 2019 a em-curso |
| Unidade (uma linha) | uma parada de uma viagem do serviço regular, com posição e horário |
| Granularidade | espacial: ponto de parada (latitude e longitude); temporal: instante da parada (data e hora) |
| Formato bruto | CSV por mês (um recurso por mês), UTF-8, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 14 |
| Unidades de medida | — |
| Dados pessoais | `placa` (placa do veículo (identifica o veículo e, indiretamente, o motorista)); `numero_imei` (identificador do equipamento); `latitude` (localização); `longitude` (localização); `codigo_viagem` (identificador da viagem) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa os CSV do pacote `monitriip-servico-regular-paradas` (`https://dados.antt.gov.br/dataset/monitriip-servico-regular-paradas`), um recurso por mês desde janeiro de 2019 (71 CSV).
- No bruto: `monitriip-servico-regular-paradas_<mês>---viagens-do-servico-regular---par-<id>@AAAAMMDD.csv`; os arquivos antigos têm o nome nu `monitriip-servico-regular-paradas@AAAAMMDD.csv`, que recebeu meses diferentes ao longo do tempo.
- Conferido em 2026-11-10 pela listagem do bruto: 72 arquivos (cerca de 8 GB), 25 vigentes (2,4 GB): janeiro de 2019 a novembro de 2020, abril de 2021 e dezembro de 2024 (este com nome nu).

## Conteúdo

- Unidade de análise: uma parada. Chave não verificada.
- Cobertura anunciada pela fonte: anual a partir de 2019, atualização mensal. **O que o lake tem: 2019-01 a 2020-11, 2021-04 e 2024-12.** Faltam dezembro de 2020, janeiro a março de 2021 e maio de 2021 a novembro de 2024, e tudo depois de dezembro de 2024.
- Layout: 14 colunas no arquivo conferido (2 arquivos de abril e maio de 2020 abertos; os cabeçalhos dos 25 vigentes coincidem). O dicionário lista 14 campos com `data_viagem_programada`; o arquivo traz `data_viagem_progamada`.
- Nulos (amostra de 102.874 linhas de 2 arquivos): nenhum. Coordenadas: a longitude chega a `0.0` e a latitude a `2.80` em linhas isoladas, valores que não condizem com o território das linhas (não investigado).

## Variáveis

Descrições do dicionário de dados da ANTT ("Dicionário de Dados - Viagens do Serviço Regular - Paradas"). Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `codigo_viagem` | `codigo_viagem` | texto | Código de identificação da viagem | — | todo |
| `cnpj` | `cnpj` | texto | CNPJ da transportadora | 14 dígitos | todo |
| `placa` | `placa` | texto | Placa do veículo | — | todo |
| `motivo_parada` | `motivo_parada` | texto | Motivo da parada. O dicionário não lista os códigos (não informado pela fonte) | códigos `0` a `10` na amostra | todo |
| `latitude` | `latitude` | texto | Latitude do ponto de parada | graus decimais, com até 20 casas | todo |
| `longitude` | `longitude` | texto | Longitude do ponto de parada | graus decimais | todo |
| `pdop` | `pdop` | texto | Número correspondente ao PDOP (Position Dilution of Precision) | — | todo |
| `data_parada` | `data_parada` | texto | Data e hora da parada | `dd-mm-aaaa hh:mm:ss` nos arquivos conferidos (o dicionário diz `DD/MM/AAAA HH:MM:SS`) | todo |
| `numero_imei` | `numero_imei` | texto | Número correspondente ao IMEI do equipamento de transmissão | — | todo |
| `nu_linha` | `nu_linha` | texto | Número da linha | — | todo |
| `tipo_viagem` | `tipo_viagem` | texto | Tipo da viagem (regular ou extra) | `Regular`, `Extra01`, `Extra02` (conferido) | todo |
| `data_viagem_progamada` | `data_viagem_progamada` | texto | Data programada da viagem (a fonte grafa "progamada"; o dicionário usa `data_viagem_programada`) | `aaaa-mm-dd` | todo |
| `hora_viagem_progamada` | `hora_viagem_progamada` | texto | Hora programada da viagem (grafia "progamada" da fonte) | `hh:mm:ss` | todo |
| `sentido_linha` | `sentido_linha` | texto | Sentido da linha | `0` ida, `1` volta | todo |

## No lake

- Dataset `antt/monitriip-servico-regular-paradas`, particionado por `ano`, um Parquet por arquivo.
- `ano` vem de `data_parada` (grupo de 4 dígitos, aqui `dd-mm-aaaa hh:mm:ss`).
- Todas as colunas são texto.
- Esquema de referência (`monitriip-servico-regular-paradas.schema.json`): 14 colunas, gerado de 2 arquivos de amostra (abril e maio de 2020).

## Cuidados de uso

- **Arquivos de meses ou anos diferentes colidem no nome e só o mais recente é convertido.** O bruto tem arquivos com nome nu (`monitriip-servico-regular-paradas@AAAAMMDD.csv`), gravados por versões antigas do fetcher que davam o mesmo nome a recursos diferentes do pacote, ao lado dos arquivos com chave de recurso (`monitriip-servico-regular-paradas_<recurso>-<id>@AAAAMMDD.csv`). `select_current` agrupa por nome sem a data e fica só com o mais novo de cada nome; os outros nomes nus ficam de fora do lake. Aqui, 45 dos 72 arquivos do bruto têm conteúdo (URL e hash) ausente do conjunto vigente: todos os meses de 2021 a novembro de 2024 e os de 2025 em diante.
- **Cópia do mesmo mês com nome nu e com chave.** `monitriip-servico-regular-paradas@20210105.csv` e o recurso de novembro de 2020 têm o mesmo hash no manifesto (96.359.391 bytes), mas o arquivo de nome nu tem 79.364.096 bytes no bruto conferido; a divergência de tamanho não foi investigada.
- **Manifesto sem arquivo.** O mês de maio de 2021 tem manifesto e não tem o CSV no bruto conferido.
- **Dado pessoal indireto.** Placa, IMEI e coordenadas por horário permitem seguir um veículo.
- **Datas mistas.** `data_parada` usa `dd-mm-aaaa hh:mm:ss` e `data_viagem_progamada` usa `aaaa-mm-dd`.

## Exemplos

Paradas por motivo em abril de 2020 (partição `ano=2020`; a coluna `data_parada` filtra o mês):

```python
import polars as pl

p = pl.scan_parquet("lake/antt/monitriip-servico-regular-paradas/ano=2020/*.parquet")
resumo = (
    p.filter(pl.col("data_parada").str.slice(3, 7) == "04-2020")
    .group_by("motivo_parada")
    .agg(pl.len().alias("paradas"))
    .sort("paradas", descending=True)
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/monitriip-servico-regular-paradas
- Dicionário de dados (PDF), no pacote: "Dicionário de Dados - Viagens do Serviço Regular - Paradas"
