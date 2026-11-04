"""Catálogo completo da ANTT: 106 pacotes + gov.br, tiers e aliases (sem rede)."""

from __future__ import annotations

import pytest

from antt_fetcher.catalog import (
    CATALOG,
    GROUP_ALIASES,
    GROUPS,
    MACRO_ALIASES,
    catalog_rows,
    expand_group,
    resolve_govbr_url,
)
from antt_fetcher.constants import DATASETS_BY_GROUP, R1_DATASETS


def test_catalogo_cobre_os_106_pacotes_mais_govbr() -> None:
    """106 pacotes do CKAN + 1 conjunto do gov.br."""
    ckan = [d for d in CATALOG.values() if d.group != "govbr"]
    assert len(ckan) == 106
    assert len(CATALOG) == 107
    assert len(GROUPS) == 9


def test_fiscalizacao_preenchida_e_govbr_presente() -> None:
    """Fiscalização deixa de ser vazia; govbr existe como grupo."""
    assert len(catalog_rows("fiscalizacao")) == 8
    assert len(catalog_rows("fiscalizacao", tier="r1")) == 5
    assert [r["slug"] for r in catalog_rows("govbr")] == [
        "producao-ferroviaria-origem-destino"
    ]


def test_r1_tem_35_pacotes_e_bate_com_as_constantes() -> None:
    """Tier r1 do catálogo == DATASETS_BY_GROUP (35 do CKAN) + 1 do gov.br."""
    r1 = {r["slug"] for r in catalog_rows(tier="r1")}
    assert len(R1_DATASETS) == 35
    assert r1 == set(R1_DATASETS) | {"producao-ferroviaria-origem-destino"}
    for group, slugs in DATASETS_BY_GROUP.items():
        assert {r["slug"] for r in catalog_rows(group, tier="r1")} >= set(slugs)
        assert all(CATALOG[s].group == group for s in slugs)


def test_pacotes_sem_dados_marcados_nao_baixaveis() -> None:
    """Pacotes só com PDF/KMZ/painel ficam listados, sem download."""
    sem_dados = [d for d in CATALOG.values() if not d.downloadable]
    assert {d.slug for d in sem_dados} >= {"pontes-similares"}
    assert all(d.tier == "listed" for d in sem_dados)


def test_aliases_e_macro_aliases() -> None:
    for alias in GROUP_ALIASES:
        assert set(expand_group(alias)) <= set(GROUPS)
    assert set(MACRO_ALIASES) <= set(GROUP_ALIASES)
    assert expand_group("infraestrutura") == ["rodovias", "ferrovias"]
    with pytest.raises(ValueError, match="Grupo desconhecido"):
        expand_group("nada")


def test_resolve_govbr_url_acompanha_a_troca_mensal_do_nome() -> None:
    html = (
        '<a href="https://www.gov.br/antt/x/transporte-de-carga-origem-destino-'
        '2006-setembro-2026.xlsx">baixar</a>'
    )
    assert resolve_govbr_url(html).endswith("2006-setembro-2026.xlsx")
    assert resolve_govbr_url("<html>Request Rejected</html>") is None
