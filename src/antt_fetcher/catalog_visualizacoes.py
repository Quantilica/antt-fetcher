"""Catálogo ANTT do domínio ``visualizacoes`` — Painéis e Visualizações Gráficas.

Gerado a partir do ``package_search`` do CKAN da ANTT (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset

GROUP = "visualizacoes"
NAME = "Painéis e Visualizações Gráficas"

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="infraestrutura-rodoviaria",
        group=GROUP,
        title="Infraestrutura Rodoviária",
        tier="listed",
        n_csv=0,
        n_json=0,
        note="Sem CSV/JSON: apenas PDF, KMZ ou painel.",
    ),
    AnttDataset(
        slug="transporte-rodoviario-de-cargas",
        group=GROUP,
        title="Transporte Rodoviário de Cargas",
        tier="listed",
        n_csv=0,
        n_json=0,
        note="Sem CSV/JSON: apenas PDF, KMZ ou painel.",
    ),
    AnttDataset(
        slug="transporte-rodoviario-de-passageiros",
        group=GROUP,
        title="Transporte Rodoviário de Passageiros",
        tier="listed",
        n_csv=0,
        n_json=0,
        note="Sem CSV/JSON: apenas PDF, KMZ ou painel.",
    ),
)
