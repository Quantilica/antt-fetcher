"""Catálogo ANTT do domínio ``tecnologia`` — Tecnologia da Informação e Agenda Regulatória.

Gerado a partir do ``package_search`` do CKAN da ANTT (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset

GROUP = "tecnologia"
NAME = "Tecnologia da Informação e Agenda Regulatória"

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="base_agendaregulatoria",
        group=GROUP,
        title="Agenda Regulatória da ANTT",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="solucoes-ti-gerenciadas",
        group=GROUP,
        title="Soluções de TI gerenciadas pela ANTT",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
)
