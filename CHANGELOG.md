# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido
- `check`: com tamanho e `last_modified` do CKAN na entrada, o veredito de frescor sai do manifesto local da mesma URL, sem um HEAD por recurso (o portal leva cerca de 20 s por HEAD em horário de carga, 1453 entradas por rodada). Tamanho igual ao do manifesto é `skip-up-to-date` (`ckan-fresh`); senão é `download` (`ckan-changed` ou `ckan-not-present`). Sem validadores (ex.: o XLSX do gov.br), segue o HEAD do SDK. Nomes e caminhos locais não mudam.
- Descoberta no CKAN: os `package_show` do grupo rodam em paralelo (4 chamadas), mantendo a ordem e os ids das entradas.

### Alterado
- A saída do CLI passa a usar o console Rich em vez de `typer.echo`.

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

