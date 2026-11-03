"""Tests for antt-fetcher catalog (sem rede)."""

from __future__ import annotations

import pytest

from antt_fetcher import catalog
from antt_fetcher.catalog import GROUP_ALIASES, GROUPS, list_datasets

FAKE_RESOURCES = {
    "volume-trafego-praca-pedagio": [
        {
            "name": "Volume de Tráfego 2024",
            "format": "CSV",
            "url": "https://x/dataset/abc/resource/1/download/volume-2024.csv",
        },
        {
            "name": "Dicionário",
            "format": "PDF",
            "url": "https://x/dicionario.pdf",
        },
    ],
    "acidentes-rodovias": [
        {
            "name": "Acidentes 2024",
            "format": "CSV",
            "url": "https://x/dataset/abc/resource/2/download/acidentes-2024.csv",
        }
    ],
}


@pytest.fixture(autouse=True)
def fake_ckan(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a descoberta CKAN por pacotes fixos e limpa o cache."""
    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(
        catalog,
        "DATASETS_BY_GROUP",
        {
            "rodovias": list(FAKE_RESOURCES),
            "cargas": [],
            "passageiros": [],
            "ferrovias": [],
            "fiscalizacao": [],
        },
        raising=False,
    )
    monkeypatch.setattr(
        catalog.AnttClient,
        "package_show",
        lambda self, package_id: {"resources": FAKE_RESOURCES[package_id]},
    )
    monkeypatch.setattr(
        catalog.AnttClient,
        "pick_package_resources",
        lambda self, package, prefer=("CSV", "JSON", "ZIP"): package["resources"],
    )


def test_expande_recursos_e_ignora_pdf() -> None:
    """Um recurso por CSV real; PDF de dicionário fica de fora."""
    entries = list_datasets("rodovias")
    assert len(entries) == 2
    assert all(e["url"].endswith(".csv") for e in entries)
    assert all(e["group"] == "rodovias" for e in entries)


def test_list_datasets_por_grupo_e_alias() -> None:
    """Grupos e aliases válidos respondem; inválido levanta ValueError."""
    for group in GROUPS:
        assert isinstance(list_datasets(group), list)
    for alias in GROUP_ALIASES:
        assert isinstance(list_datasets(alias), list)
    with pytest.raises(ValueError, match="Grupo desconhecido"):
        list_datasets("grupo_inexistente_xyz")
