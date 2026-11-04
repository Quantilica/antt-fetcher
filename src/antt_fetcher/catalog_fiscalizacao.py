"""Catálogo ANTT do domínio ``fiscalizacao`` — Fiscalização e Autos de Infração.

Gerado a partir do ``package_search`` do CKAN da ANTT (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset

GROUP = "fiscalizacao"
NAME = "Fiscalização e Autos de Infração"

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="sifama-autos-de-infracao-cargas",
        group=GROUP,
        title="SIFAMA - Autos de Infração de Transporte Rodoviário de Cargas",
        tier="r1",
        n_csv=11,
        n_json=11,
        note="",
    ),
    AnttDataset(
        slug="sifama-autos-de-infracao-passageiros",
        group=GROUP,
        title="SIFAMA - Autos de Infração de Transporte Rodoviário Interestadual e Internacional de Passageiros",
        tier="r1",
        n_csv=9,
        n_json=9,
        note="",
    ),
    AnttDataset(
        slug="sifama-autos-de-infracao-transito",
        group=GROUP,
        title="SIFAMA -  Autos de Infração de Trânsito",
        tier="r1",
        n_csv=15,
        n_json=15,
        note="",
    ),
    AnttDataset(
        slug="sismultas-autos-de-infracao-de-cargas",
        group=GROUP,
        title="SISMULTAS - Autos de Infração de Transporte Rodoviário de Cargas",
        tier="r1",
        n_csv=28,
        n_json=28,
        note="",
    ),
    AnttDataset(
        slug="sismultas-autos-de-infracao-de-passageiros",
        group=GROUP,
        title="SISMULTAS - Autos de Infração de Transporte Rodoviário Interestadual e Internacional de Passageiros",
        tier="r1",
        n_csv=28,
        n_json=28,
        note="",
    ),
    AnttDataset(
        slug="posto-pesagem-veicular",
        group=GROUP,
        title="Operação dos Postos de Pesagem Veicular",
        tier="listed",
        n_csv=18,
        n_json=18,
        note="",
    ),
    AnttDataset(
        slug="registro-fiscalizacao-passageiros",
        group=GROUP,
        title="Registro de Fiscalizações do Transporte Rodoviário de Passageiros",
        tier="listed",
        n_csv=9,
        n_json=9,
        note="",
    ),
    AnttDataset(
        slug="sif",
        group=GROUP,
        title="Registros do Sistema Integrado de Fiscalizações - SIF",
        tier="listed",
        n_csv=15,
        n_json=15,
        note="",
    ),
)
