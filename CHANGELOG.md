# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido
- `sync` expande os pacotes CKAN em um recurso por arquivo, em vez de baixar o
  JSON de metadados do pacote.
- `ANTT_CKAN_URL` aponta para a raiz do portal (o `CkanClient` já acrescenta
  `/api/3`).

## [0.1.0] - 2026-11-01

### Adicionado
- Versão inicial do pacote `antt-fetcher` (`quantilica antt`).
- Suporte a `list`, `check`, `sync` e verificação de frescor via SDK `FetcherApp`.

- Conversor Universal Hive Parquet Lake com `DatasetSpec` em `lake.py`.

