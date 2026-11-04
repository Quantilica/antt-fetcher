# antt-fetcher

[![CI](https://github.com/Quantilica/antt-fetcher/actions/workflows/test.yml/badge.svg)](https://github.com/Quantilica/antt-fetcher/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Coletor e conversor Lake Hive para dados abertos de **Agência Nacional de Transportes Terrestres (ANTT)** (`antt`), parte do ecossistema [Quantilica](https://quantilica.com).

## Instalação

### Via CLI Quantilica (recomendado)

```bash
quantilica install antt
```

Para instalar com suporte à conversão Parquet Lake:

```bash
quantilica install antt --extra analysis
```

### Como biblioteca Python

```bash
uv add antt-fetcher --index https://index.quantilica.com/simple/
```

Com o extra de análise analítica:

```bash
uv add 'antt-fetcher[analysis]' --index https://index.quantilica.com/simple/
```

## Uso via CLI

```bash
# Listar os arquivos dos pacotes R1 (os que baixam hoje)
quantilica antt list

# Catálogo completo (R1 + listados) e descoberta de novidades na fonte
quantilica antt catalogo fiscalizacao
quantilica antt discover

# Verificar novos arquivos e frescor
quantilica antt check

# Sincronizar arquivos para o diretório local bruto
quantilica antt sync -o /data/antt

# Converter acervo bruto para o Universal Hive Parquet Lake
quantilica antt convert /data/antt /data/lake
```

## Cobertura do catálogo

O CKAN da ANTT publica 106 pacotes (2026-11-03); o catálogo cobre os 106 mais o
XLSX do gov.br.

| Grupo | Pacotes | R1 (baixa) | Listado |
|---|---:|---:|---:|
| rodovias | 53 | 11 | 42 |
| cargas | 10 | 3 | 7 |
| passageiros | 22 | 14 | 8 |
| ferrovias | 6 | 2 | 4 |
| fiscalizacao | 8 | 5 | 3 |
| ouvidoria | 2 | 0 | 2 |
| tecnologia | 2 | 0 | 2 |
| visualizacoes | 3 | 0 | 3 |
| govbr | 1 | 1 | 0 |

`list` e `sync` operam só no tier R1 (35 pacotes do CKAN + o XLSX do gov.br).
Quatro pacotes não têm CSV nem JSON (só PDF, KMZ ou painel) e ficam apenas
listados. O portal está atrás de um WAF (F5): respostas "Request Rejected" são
tratadas como falha transitória, nunca como arquivo.

## Licença

Distribuído sob licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.
