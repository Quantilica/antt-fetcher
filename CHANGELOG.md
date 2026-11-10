# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- `docs/`: documentação dos dados conforme a norma, com uma página por dataset (12) e o esquema de referência dos doze. `tests/test_docs.py` verifica a pasta.

### Corrigido
- `lake`: arquivos de nome nu (`<slug>@AAAAMMDD.csv`), gravados por versões antigas do fetcher para recursos diferentes do mesmo pacote, se sobrepunham: a seleção da versão vigente guardava só o mais recente de cada nome e descartava os demais recursos (no `rntrc`, 70 dos 71 meses; no `monitriip-servico-regular-paradas`, 45 dos 72 arquivos; também `ciot`, `volume-sat`, `volume-radar`, `quantidade-possiveis-infratores`, `acidentes-rodovias` e o ano de 2023 do `volume-trafego-praca-pedagio`). A identidade do arquivo passa a ser o recurso da fonte (URL do manifesto ao lado): versões do mesmo recurso continuam se substituindo (vale o carimbo mais novo) e recursos diferentes coexistem. Arquivo sem manifesto segue a regra do nome.
- `lake`: o mesmo recurso sob dois nomes no mesmo carimbo (o nome nu e o nome com chave de recurso, mesma URL e mesmo conteúdo, como `quantidade-possiveis-infratores@20260828.csv` e `..._ae4f9bef@20260828.csv`) entrava duas vezes. Fica um só (o de nome com chave) e o outro aparece no `inventory()` como `gemeo`. Sem manifesto (sem URL para comparar), um arquivo de nome nu com o mesmo carimbo, tamanho e `sha256` de um arquivo de nome com chave do mesmo conjunto também é `gemeo` (o caso de `volume-sat@20261103.csv`, igual ao CSV da Via040).
- `lake`: a chave do Parquet de um arquivo de nome nu ganha o sufixo `_<id8>` do recurso (os 8 primeiros caracteres do id do recurso na URL); se o recurso tem também um nome com chave, vale a chave desse nome. Recursos diferentes de nome nu deixam de compartilhar (e sobrescrever) o mesmo Parquet.
- `lake`: o `relatorio-acompanhamento-acidentes-ferroviarios-raaf` convertia 0 linhas: os arquivos do bruto usam o slug do pacote (`relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf`) e o conversor procurava o id do conjunto, diferente. O slug do pacote passa a alimentar o conjunto (`PACKAGE_DATASETS`). O arquivo de nome nu que repete, no mesmo carimbo, o conteúdo de um arquivo de nome com chave deixa de derrubar o nome nu mais antigo (outro recurso) pela regra do nome.
- `lake`: `volume-trafego-praca-pedagio`, `volume-radar` e `volume-sat` publicam o mesmo tráfego em arquivos diários e em arquivos mensais consolidados (conferido: 834.732.408 veículos nos dois arquivos de 2024 das praças; totais mensais idênticos no radar da CRT e da Via040 e no SAT da Autopista Fluminense), e os dois caíam na mesma partição `ano`, de modo que somar a partição contava o tráfego duas vezes. Os três conjuntos ganham a coluna `granularidade` (`dia` ou `mes`), que é do arquivo e não da linha: vale o que o nome do recurso diz (`_diario`, `_mensal_consolidado`) e, sem isso, o arquivo é `mes` quando pelo menos 90% das linhas têm data `mm/aaaa` ou dia 01 (os mensais antigos das praças trazem `01/MM/AAAA`, e o de 2023 tem 734 linhas em outras datas) e `dia` no resto; nula se o arquivo não tem coluna de data. Para somar o tráfego, filtre uma só granularidade. O esquema público de cada um ganha uma coluna; as partições não mudam.
- `lake`: o JSON do `volume-sat` repete concessionárias que têm CSV diário (Nova Rota do Oeste, Motiva Minas SP, EPR Via Mineira e Elovias, 719.856 registros, com as mesmas contagens de registros dos CSV), e a regra de "gêmeo" só ignorava o CSV de mesmo nome e carimbo, de modo que o resto era contado de novo. Agora o CSV diário manda: do JSON entram só as linhas de concessionárias sem CSV diário vigente (comparação pelo nome normalizado, lido do início de cada CSV), e um JSON inteiramente coberto aparece no `inventory()` como `gemeo`. O CSV de mesmo nome e carimbo do JSON deixa de ser tratado como gêmeo dele (no bruto real é outro recurso, a Via040).

### Como reconverter
Estas correções mudam a chave do Parquet dos arquivos de nome nu (sufixo `_<id8>` do recurso), acrescentam a coluna `granularidade` a três datasets e tiram do `volume-sat` as linhas do JSON. O `LakeWriter` só remove Parquets órfãos de uma mesma chave de arquivo, então reconverter por cima (mesmo com `--force`) deixaria os Parquets antigos ao lado dos novos e duplicaria linhas. **Antes de reconverter com esta versão, apague no lake** as pastas abaixo e converta de novo (`antt/` é a pasta da fonte no lake):

- `antt/volume-trafego-praca-pedagio/`, `antt/volume-radar/`, `antt/volume-sat/`: coluna nova `granularidade` e chaves novas dos arquivos de nome nu; no `volume-sat`, também o Parquet antigo do JSON (`volume-sat.parquet`), cujas linhas agora vêm dos CSV.
- `antt/rntrc/`, `antt/ciot/`, `antt/monitriip-servico-regular-paradas/`, `antt/acidentes-rodovias/`, `antt/quantidade-possiveis-infratores/`: o Parquet antigo do arquivo de nome nu (`<dataset>.parquet`) ganha chave nova (`<dataset>_<id8>.parquet`) e os meses, anos e concessionárias que estavam de fora passam a entrar.
- `antt/investimentos/`, `antt/vale-pedagio-obrigatorio/`, `antt/praca-de-pedagio/`: o único arquivo de cada um tem nome nu e ganha o sufixo `_<id8>` na chave.
- `antt/relatorio-acompanhamento-acidentes-ferroviarios-raaf/`: dataset novo; se alguém converteu os arquivos à mão com outro id, apague a pasta que tenha criado.

Para não reconverter o que não mudou nos cinco datasets do segundo item (o `monitriip-servico-regular-paradas` e o `rntrc` são os grandes), basta apagar os Parquets cuja chave é só o nome do dataset: `antt/<dataset>/ano=*/<dataset>.parquet` e `<dataset>-NNN.parquet`; os Parquets de arquivos com chave de recurso mantêm a chave e são pulados. Nos demais, apague a pasta inteira.

## [0.3.2] - 2026-11-06

### Corrigido
- `lake`: os manifestos (`.manifest.json`) ao lado do bruto entravam na conversão; no `volume-sat`, que aceita JSON, cada manifesto virava um erro. A conversão ignora manifestos e `.tmp`, como o `inventory` já fazia.
- `lake`: CSV com campos entre aspas e uma aspa interna sem escape (`"barreira ou "submarino";` no `acidentes-rodovias` da Autopista, out/2026) falhava com `CSV malformed`. Linhas com número ímpar de aspas têm a aspa que não abre nem fecha campo escapada (`""`) antes da leitura, com aviso no log; as demais linhas não mudam.

## [0.3.1] - 2026-11-06

### Corrigido
- `lake`: CSV sem campos entre aspas com uma aspa solta no dado (`D"AVILA`, `SANT"ANA` nos arquivos antigos do `rntrc`) falhava com `CSV malformed`, porque a aspa abria um campo e engolia as linhas seguintes. Sem campo que comece com aspas nas primeiras linhas, o arquivo é lido sem quoting.
- `lake`: arquivos do `volume-radar` publicados sem a linha de cabeçalho (algumas concessionárias) falhavam com "partição por ano indeterminada"; agora recebem o cabeçalho dos demais arquivos do conjunto.

## [0.3.0] - 2026-11-06

### Adicionado
- `lake`: sete conjuntos passam a ser convertidos, um a um, com particao Hive `ano`: `ciot` (agregado mensal origem/destino), `vale-pedagio-obrigatorio` (ano de emissao), `investimentos` (coluna `ano`), `praca-de-pedagio` (cadastro das pracas), `quantidade-possiveis-infratores` (data da passagem), `volume-radar` (data da passagem, aceita `dd/mm/aaaa` e `mm/aaaa`) e `volume-sat` (CSV e JSON).
- `lake`: o JSON do `volume-sat` (varios documentos `{"volume_sat":[...]}` num arquivo, um registro por linha) e lido por streaming; linha fora desse formato e erro. Com CSV e JSON do mesmo carimbo, o JSON e convertido e o CSV e tratado como gemeo (o JSON ja traz as mesmas passagens), para nao duplicar volumes.
- `lake`: `inventory()` informa, para cada arquivo bruto, o conjunto que ele alimenta ou o motivo de ficar de fora (`superado`, `nao_tabular`, `gemeo`); arquivo de conjunto ainda sem conversor aparece sem conjunto e sem motivo.

### Alterado
- A saída do CLI passa a usar o console Rich em vez de `typer.echo`.

### Corrigido
- Pacotes com varios recursos (um por concessionaria: `volume-radar`, `volume-sat`, `quantidade-possiveis-infratores`, `ciot`, `volume-trafego-equivalente-praca-pedagio`...) davam o mesmo nome local a recursos diferentes, e cada download sobrescrevia o anterior (so o ultimo sobrevivia). Agora esses arquivos tem nome unico por recurso: `<pacote>_<nome-do-recurso>-<id8>@AAAAMMDD.<ext>`. Pacote com um unico recurso mantem o nome de sempre. Os arquivos antigos de nome coincidente nao sao migrados automaticamente: o conteudo que ja foi sobrescrito precisa ser baixado de novo.
- `lake`: o conjunto passa a ser reconhecido pelo prefixo do slug no nome local (com ou sem o identificador do recurso).
- `check`: com tamanho e `last_modified` do CKAN na entrada, o veredito de frescor sai do manifesto local da mesma URL, sem um HEAD por recurso (o portal leva cerca de 20 s por HEAD em horário de carga, 1453 entradas por rodada). Tamanho igual ao do manifesto é `skip-up-to-date` (`ckan-fresh`); senão é `download` (`ckan-changed` ou `ckan-not-present`). Sem validadores (ex.: o XLSX do gov.br), segue o HEAD do SDK. Nomes e caminhos locais não mudam.
- Descoberta no CKAN: os `package_show` do grupo rodam em paralelo (4 chamadas), mantendo a ordem e os ids das entradas.
- `lake`: o `rntrc` e o `ciot` (fotografias/agregados sem data de evento) continuam particionando pelo periodo do nome original da URL, lido do manifesto (`.manifest.json`) ao lado do arquivo. Sem o manifesto (ou sem periodo nele) o erro e explicito e diz que o manifesto precisa estar ao lado do arquivo; nenhum ano e inventado. Foi o que fez `rntrc@20261010.csv` falhar quando o bruto estava sozinho no Drive.
- `lake`: `praca-de-pedagio` (cadastro das pracas, sem periodo no nome nem na URL) particiona pelo ano do carimbo `@AAAAMMDD`, com aviso no log e sem descartar linhas; `ano_do_pnv_snv` e a versao do mapa e nao serve de ano.

## [0.2.1] - 2026-11-04

### Corrigido
- `lake`: CSV em cp1252 com bytes indefinidos (0x8d, 0x90...) converte em vez de falhar com `'charmap' codec can't decode`; o tratador de erros não reconhecia o encoding que o Python reporta (`charmap`).
- `lake`: o conjunto vem do slug do nome local (`<slug>@AAAAMMDD`); conjuntos catalogados sem conversor (`vale-pedagio-obrigatorio`, `praca-de-pedagio`, `volume-radar`, `volume-sat`, `receita-por-praca`, `rntrc-veiculos`...) deixam de ser tomados por volume de praça ou acidentes por substring do nome e são ignorados sem erro.
- `lake`: `monitriip-servico-regular-paradas` particiona por `data_parada`; acidentes por concessionária aceita cabeçalhos de data diferentes (`data_do_acidente` etc.); o `rntrc` (fotografia) lê o período do nome original da URL no manifesto vizinho. Sem coluna nem período conhecido, segue o erro explícito, sem ano inventado.

## [0.2.0] - 2026-11-04

### Adicionado
- Catálogo completo por domínio (`catalog_<dominio>.py`, 9 grupos): os 106 pacotes do CKAN (2026-11-03) mais o conjunto `govbr`, com `tier` (`r1` baixa hoje; `listed` = listado, download em release futura). R1 passa de 5 para 35 pacotes do CKAN (+ o XLSX do gov.br); `fiscalizacao` deixa de ser vazia (8 pacotes, 5 em R1) e entram `ouvidoria`, `tecnologia`, `visualizacoes` e `govbr`.
- `govbr`: produção ferroviária origem-destino (XLSX de 9,1 MB). O nome do arquivo muda a cada mês, então a URL é resolvida pela página; o gov.br recusa HEAD (403) mas aceita GET com Range.
- `MACRO_ALIASES` (`infraestrutura`, `transporte-rodoviario`, `gestao`); `GROUP_ALIASES` agora mapeia para listas.
- `quantilica antt catalogo [grupo] [--tier]` e `quantilica antt discover [--json] [--fail-on-change]` (`antt_fetcher.discover.discover()`): pacotes novos, removidos na fonte (bruto mantido) e crescidos; resposta vazia/WAF vira erro, nunca "tudo removido".
- O `lake` continua convertendo só os 5 conjuntos originais; os demais R1 ficam como bruto.

### Corrigido
- Ids de entrada truncados em 80 caracteres perdiam o ano e colidiam (ex.: `sifama-autos-de-infracao-passageiros` gerava 1 id para 9 arquivos); o sufixo agora vem depois do corte.
- `pick_package_resources` agrupava por `name` do CKAN e fundia arquivos distintos com o mesmo nome (`radar`, `trecho-concedido`, `sat`...); agora agrupa pelo arquivo da URL, preferindo CSV a JSON e o maior `size`.
- Pacote removido do CKAN deixa de derrubar o grupo inteiro no `list`.
- Sem o extra `analysis`, o comando `convert` termina com código 1 e a instrução de instalação (`quantilica install antt --extra analysis`), sem traceback.
### Corrigido
- Política de frescor volta a F2 (`HEAD_FALLBACK_GET`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.
- Aliases de grupo (`sync padrao` etc.): o `FetcherApp` recebia `alias -> str` e o
  SDK fazia `list("teses")`, resolvendo para `['t', 'e', 's', ...]` ("Grupo
  desconhecido: 't'"). O plugin agora passa `alias -> [grupo]`.
- `lake`: a partição `ano` agora é por linha (coluna de data do conjunto), não o
  ano da primeira linha do arquivo; CSV multi-ano gera uma partição por ano.
  Linha sem ano válido vai para `ano=__HIVE_DEFAULT_PARTITION__` com aviso de
  contagem (antes recebia 2024 em silêncio). `rntrc` (retrato mensal) usa o
  período declarado no nome do arquivo; sem coluna de ano nem ano único no nome
  o arquivo vira erro contado.
- `lake`: cada membro de ZIP é uma origem própria (`composite_file_key`);
  leitura em streaming (transcodificação em blocos para UTF-8/cp1252 explícito +
  `scan_csv` lazy), sem `read_bytes`/`StringIO`/`errors="replace"`; colunas
  lidas como texto. Marcador `network` registrado (fora do `pytest -q`).
- `sync` expande os pacotes CKAN em um recurso por arquivo, em vez de baixar o
  JSON de metadados do pacote.
- `ANTT_CKAN_URL` aponta para a raiz do portal (o `CkanClient` já acrescenta
  `/api/3`).

## [0.1.0] - 2026-11-01

### Adicionado
- Versão inicial do pacote `antt-fetcher` (`quantilica antt`).
- Suporte a `list`, `check`, `sync` e verificação de frescor via SDK `FetcherApp`.

- Conversor Universal Hive Parquet Lake com `DatasetSpec` em `lake.py`.

