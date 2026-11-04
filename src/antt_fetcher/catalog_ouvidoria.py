"""Catálogo ANTT do domínio ``ouvidoria`` — Ouvidoria e Pesquisas de Satisfação.

Gerado a partir do ``package_search`` do CKAN da ANTT (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset

GROUP = "ouvidoria"
NAME = "Ouvidoria e Pesquisas de Satisfação"

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="pesquisa-de-satisfacao-dos-usuarios-2017-2018",
        group=GROUP,
        title="Pesquisa de Satisfação dos Usuários 2017/2018",
        tier="listed",
        n_csv=9,
        n_json=0,
        note="",
    ),
    AnttDataset(
        slug="sistema-de-ouvidoria-sou",
        group=GROUP,
        title="Sistema de Ouvidoria - SOU",
        tier="listed",
        n_csv=19,
        n_json=0,
        note="Arquivos grandes (GB).",
    ),
)
