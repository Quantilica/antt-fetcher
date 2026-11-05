# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- `lake`: sete conjuntos passam a ser convertidos, um a um, com particao Hive `ano`: `ciot` (agregado mensal origem/destino), `vale-pedagio-obrigatorio` (ano de emissao), `investimentos` (coluna `ano`), `praca-de-pedagio` (cadastro das pracas), `quantidade-possiveis-infratores` (data da passagem), `volume-radar` (data da passagem, aceita `dd/mm/aaaa` e `mm/aaaa`) e `volume-sat` (CSV e JSON).
- `lake`: o JSON do `volume-sat` (varios documentos `{"volume_sat":[...]}` num arquivo, um registro por linha) e lido por streaming; linha fora desse formato e erro. Com CSV e JSON do mesmo carimbo, o JSON e convertido e o CSV e tratado como gemeo (o JSON ja traz as mesmas passagens), para nao duplicar volumes.
- `lake`: `inventory()` informa, para cada arquivo bruto, o conjunto que ele alimenta ou o motivo de ficar de fora (`superado`, `nao_tabular`, `gemeo`); arquivo de conjunto ainda sem conversor aparece sem conjunto e sem motivo.

### Corrigido
- Pacotes com varios recursos (um por concessionaria: `volume-radar`, `volume-sat`, `quantidade-possiveis-infratores`, `ciot`, `volume-trafego-equivalente-praca-pedagio`...) davam o mesmo nome local a recursos diferentes, e cada download sobrescrevia o anterior (so o ultimo sobrevivia). Agora esses arquivos tem nome unico por recurso: `<pacote>_<nome-do-recurso>-<id8>@AAAAMMDD.<ext>`. Pacote com um unico recurso mantem o nome de sempre. Os arquivos antigos de nome coincidente nao sao migrados automaticamente: o conteudo que ja foi sobrescrito precisa ser baixado de novo.
- `lake`: o conjunto passa a ser reconhecido pelo prefixo do slug no nome local (com ou sem o identificador do recurso).
- `lake`: `rntrc@AAAAMMDD.csv` falhava com "particao por ano indeterminada" quando o manifesto vizinho nao estava presente (o Drive guarda so o arquivo bruto). Para fotografias/cadastros (`rntrc`, `ciot`, `praca-de-pedagio`), sem periodo no nome original, o ano passa a ser o do carimbo `@AAAAMMDD`, com aviso no log e sem descartar linhas. O periodo do nome original continua tendo preferencia. Limite conhecido: fotografia tirada em janeiro costuma retratar dezembro do ano anterior. Conjunto de eventos sem coluna de data continua dando erro.

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

