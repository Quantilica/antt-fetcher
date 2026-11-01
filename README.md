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
# Listar conjuntos disponíveis
quantilica antt list

# Verificar novos arquivos e frescor
quantilica antt check

# Sincronizar arquivos para o diretório local bruto
quantilica antt sync -o /data/antt

# Converter acervo bruto para o Universal Hive Parquet Lake
quantilica antt convert /data/antt /data/lake
```

## Licença

Distribuído sob licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.
