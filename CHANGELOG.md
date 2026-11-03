# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido
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

