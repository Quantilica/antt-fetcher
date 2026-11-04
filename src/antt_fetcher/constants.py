"""Constants and endpoint definitions for antt-fetcher."""

from __future__ import annotations

ANTT_CKAN_URL = "https://dados.antt.gov.br"

GROUPS_LIST = [
    "rodovias",
    "cargas",
    "passageiros",
    "ferrovias",
    "fiscalizacao",
    "ouvidoria",
    "tecnologia",
    "visualizacoes",
    "govbr",
]

# Página do gov.br com a produção ferroviária origem-destino (fora do CKAN). O
# nome do XLSX muda a cada mês (``...-2006-setembro-2026.xlsx``): a URL é
# resolvida pela página. O gov.br recusa HEAD (403) mas aceita GET com Range.
GOVBR_FERROVIAS_PAGE = (
    "https://www.gov.br/antt/pt-br/assuntos/ferrovias/"
    "dados-de-producao-do-transporte-de-carga-origem-destino"
)

# Pacotes CKAN do R1 (35), por grupo. A URL de download é descoberta por
# `package_show` — o portal não publica um arquivo por pacote.
DATASETS_BY_GROUP: dict[str, list[str]] = {
    "rodovias": [
        "volume-trafego-praca-pedagio",
        "volume-trafego-equivalente-praca-pedagio",
        "volume-radar",
        "volume-sat",
        "quantidade-possiveis-infratores",
        "acidentes-rodovias",
        "acidentes-quilometro-rodovias",
        "receita-por-praca",
        "receita-pedagio",
        "praca-de-pedagio",
        "investimentos",
    ],
    "cargas": [
        "rntrc",
        "ciot",
        "vale-pedagio-obrigatorio",
    ],
    "passageiros": [
        "monitriip-servico-regular-paradas",
        "monitriip-servico-regular-viagens",
        "monitriip-servico-fretado-paradas",
        "monitriip-servico-fretado-viagens",
        "monitriip-bilhetes-de-passagem",
        "monitriip-indicadores",
        "monitriip-semiurbano",
        "gerenciamento-de-autorizacoes",
        "gerenciamento-de-autorizacoes-2021-2024",
        "licencas-operacionais",
        "licencas-de-viagem-nacional-servico-fretado",
        "licencas-de-viagem-internacional-servico-fretado",
        "autorizacoes-de-viagem-fretado-continuo",
        "autorizacoes-de-viagem-internacional-servico-fretado-continuo",
    ],
    "ferrovias": [
        "relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf",
        "material-rodante",
    ],
    "fiscalizacao": [
        "sifama-autos-de-infracao-passageiros",
        "sifama-autos-de-infracao-transito",
        "sifama-autos-de-infracao-cargas",
        "sismultas-autos-de-infracao-de-passageiros",
        "sismultas-autos-de-infracao-de-cargas",
    ],
    "ouvidoria": [],
    "tecnologia": [],
    "visualizacoes": [],
    "govbr": [],
}

R1_DATASETS = [slug for slugs in DATASETS_BY_GROUP.values() for slug in slugs]
