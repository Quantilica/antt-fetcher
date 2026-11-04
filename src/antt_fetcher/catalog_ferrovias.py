"""Catálogo ANTT do domínio ``ferrovias`` — Transporte Ferroviário.

Gerado a partir do ``package_search`` do CKAN da ANTT (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset

GROUP = "ferrovias"
NAME = "Transporte Ferroviário"

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="material-rodante",
        group=GROUP,
        title="Material Rodante",
        tier="r1",
        n_csv=3,
        n_json=3,
        note="",
    ),
    AnttDataset(
        slug="relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf",
        group=GROUP,
        title="Acidentes Ferroviários",
        tier="r1",
        n_csv=5,
        n_json=5,
        note="",
    ),
    AnttDataset(
        slug="controle-de-penalidades-aplicadas",
        group=GROUP,
        title="Penalidades",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="projeto-concessao-ferrovias",
        group=GROUP,
        title="Projetos de Concessão de Ferrovias",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="projetos-autorizados",
        group=GROUP,
        title="Investimentos Autorizados GEPEF - PIC",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="sistema-de-acompanhamento-do-desempenho-operacional-das-concessionarias-siade",
        group=GROUP,
        title="Sistema de Acompanhamento do Desempenho Operacional das Concessionárias - SIADE",
        tier="listed",
        n_csv=21,
        n_json=21,
        note="",
    ),
)
