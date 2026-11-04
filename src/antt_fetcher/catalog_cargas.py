"""Catálogo ANTT do domínio ``cargas`` — Transporte Rodoviário de Cargas.

Gerado a partir do ``package_search`` do CKAN da ANTT (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset

GROUP = "cargas"
NAME = "Transporte Rodoviário de Cargas"

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="ciot",
        group=GROUP,
        title="Código identificador da operação de transporte - CIOT",
        tier="r1",
        n_csv=81,
        n_json=79,
        note="",
    ),
    AnttDataset(
        slug="rntrc",
        group=GROUP,
        title="Registro Nacional de Transportadores Rodoviários de Cargas - RNTRC",
        tier="r1",
        n_csv=73,
        n_json=0,
        note="",
    ),
    AnttDataset(
        slug="vale-pedagio-obrigatorio",
        group=GROUP,
        title="VPO-Vale Pedágio Obrigatório",
        tier="r1",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="empresas-brasil-peru",
        group=GROUP,
        title="Empresas Brasileiras Habilitadas para o Peru",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="empresas-habilitadas-tric",
        group=GROUP,
        title="Empresas habilitadas ao transporte rodoviário internacional de cargas (TRIC).",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="empresas-impedidas-tric",
        group=GROUP,
        title="Transportadores Impedidos de Operar no Transporte Internacional",
        tier="listed",
        n_csv=2,
        n_json=2,
        note="",
    ),
    AnttDataset(
        slug="operador-transporte-multimodal",
        group=GROUP,
        title="Empresas Habilitadas como Operador de Transporte Multimodal",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="produtos-perigosos",
        group=GROUP,
        title="Certificados de Produtos Perigosos",
        tier="listed",
        n_csv=11,
        n_json=11,
        note="",
    ),
    AnttDataset(
        slug="rntrc-historico",
        group=GROUP,
        title="RNTRC – Histórico dos Transportadores e Veículos Ativos",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
    AnttDataset(
        slug="rntrc-veiculos",
        group=GROUP,
        title="RNTRC-Dados de Veículos",
        tier="listed",
        n_csv=1,
        n_json=1,
        note="",
    ),
)
