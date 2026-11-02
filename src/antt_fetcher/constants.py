"""Constants and endpoint definitions for antt-fetcher."""

from __future__ import annotations

ANTT_CKAN_URL = "https://dados.antt.gov.br"

GROUPS_LIST = [
    "rodovias",
    "cargas",
    "passageiros",
    "ferrovias",
    "fiscalizacao",
]

# Pacotes CKAN do R1, por grupo. A URL de download é descoberta por
# `package_show` — o portal não publica um arquivo por pacote.
DATASETS_BY_GROUP: dict[str, list[str]] = {
    "rodovias": [
        "volume-trafego-praca-pedagio",
        "acidentes-rodovias",
    ],
    "cargas": ["rntrc"],
    "passageiros": ["monitriip-servico-regular-paradas"],
    "ferrovias": ["relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf"],
    "fiscalizacao": ["sismultas-autos-de-infracao-lavrados"],
}

R1_DATASETS = [
    slug for slugs in DATASETS_BY_GROUP.values() for slug in slugs
]
