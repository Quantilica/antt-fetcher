"""Dataset catalog for antt-fetcher."""

from __future__ import annotations

from typing import Any

from ._catalog_base import DatasetEntry, GroupInfo, static_dataset
from .constants import ANTT_CKAN_URL

__all__ = [
    "DatasetEntry",
    "GroupInfo",
    "GROUPS",
    "GROUP_ALIASES",
    "list_datasets",
]

GROUPS: dict[str, dict[str, Any]] = {
    "rodovias": {
        "name": "Rodovias Federais Concedidas",
        "entries": [
            static_dataset(
                "rodovias",
                id="volume-trafego-praca-pedagio",
                name="Volume de Tráfego por Praça de Pedágio",
                url=f"{ANTT_CKAN_URL}/action/package_show?id=volume-trafego-praca-pedagio",
                ext="csv",
            ).to_dict(),
            static_dataset(
                "rodovias",
                id="acidentes-rodovias",
                name="Acidentes em Rodovias Concedidas",
                url=f"{ANTT_CKAN_URL}/action/package_show?id=acidentes-rodovias",
                ext="csv",
            ).to_dict(),
        ],
    },
    "cargas": {
        "name": "Transporte Rodoviário de Cargas",
        "entries": [
            static_dataset(
                "cargas",
                id="rntrc",
                name="Registro Nacional de Transportadores Rodoviários de Cargas",
                url=f"{ANTT_CKAN_URL}/action/package_show?id=rntrc",
                ext="csv",
            ).to_dict(),
        ],
    },
    "passageiros": {
        "name": "Transporte de Passageiros",
        "entries": [
            static_dataset(
                "passageiros",
                id="monitriip-servico-regular-paradas",
                name="MONITRIIP - Serviço Regular - Paradas",
                url=f"{ANTT_CKAN_URL}/action/package_show?id=monitriip-servico-regular-paradas",
                ext="csv",
            ).to_dict(),
        ],
    },
    "ferrovias": {
        "name": "Transporte Ferroviário",
        "entries": [
            static_dataset(
                "ferrovias",
                id="relatorio-acompanhamento-acidentes-ferroviarios-raaf",
                name="Relatório de Acompanhamento de Acidentes Ferroviários (RAAF)",
                url=f"{ANTT_CKAN_URL}/action/package_show?id=relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf",
                ext="csv",
            ).to_dict(),
        ],
    },
    "fiscalizacao": {
        "name": "Fiscalização e Autos de Infração",
        "entries": [
            static_dataset(
                "fiscalizacao",
                id="autos-de-infracao",
                name="Autos de Infração da ANTT",
                url=f"{ANTT_CKAN_URL}/action/package_show?id=sismultas-autos-de-infracao-lavrados",
                ext="csv",
            ).to_dict(),
        ],
    },
}

GROUP_ALIASES: dict[str, str] = {
    "padrao": "rodovias",
    "principal": "rodovias",
}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """List datasets for a group or all groups."""
    if group is None:
        entries: list[dict[str, Any]] = []
        for g_data in GROUPS.values():
            entries.extend(g_data["entries"])
        return entries

    canon = GROUP_ALIASES.get(group, group)
    if canon not in GROUPS:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    return list(GROUPS[canon]["entries"])
