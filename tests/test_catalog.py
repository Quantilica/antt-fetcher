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


def test_ids_longos_nao_colidem(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regressão: id truncado em 80 caracteres perdia o ano e colidia."""
    slug = "sifama-autos-de-infracao-passageiros"
    resources = [
        {
            "id": f"res-{ano}",
            "name": f"SIFAMA - Autos de Infração de Passageiros {ano}",
            "format": "CSV",
            "url": f"https://x/sifama_{ano}.csv",
        }
        for ano in (2021, 2022, 2023)
    ]
    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(
        catalog, "DATASETS_BY_GROUP", {"fiscalizacao": [slug]}, raising=False
    )
    monkeypatch.setattr(
        catalog.AnttClient,
        "package_show",
        lambda self, package_id: {"resources": resources},
    )
    ids = [e["id"] for e in list_datasets("fiscalizacao")]
    assert len(ids) == 3
    assert len(set(ids)) == 3


def _entradas(monkeypatch: pytest.MonkeyPatch, grupo: str, slug: str, resources):
    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(catalog, "DATASETS_BY_GROUP", {grupo: [slug]}, raising=False)
    monkeypatch.setattr(
        catalog.AnttClient,
        "package_show",
        lambda self, package_id: {"resources": resources},
    )
    return list_datasets(grupo)


def _nomes(entries) -> list[str]:
    import datetime as dt
    import tempfile
    from pathlib import Path

    from antt_fetcher.storage import DataRepository

    repo = DataRepository(Path(tempfile.gettempdir()) / "x")
    return [
        repo.path_for_entry(e, last_modified=dt.date(2026, 9, 28)).name for e in entries
    ]


def test_pacote_multirecurso_gera_nomes_unicos_e_estaveis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resources = [
        {
            "id": "aaaa1111-x",
            "name": "Radar Concessionária A",
            "format": "CSV",
            "url": "https://x/a.csv",
        },
        {
            "id": "bbbb2222-x",
            "name": "Radar Concessionaria A",
            "format": "CSV",
            "url": "https://x/b.csv",
        },
        {
            "id": "cccc3333-x",
            "name": "Radar concessionária-A",
            "format": "CSV",
            "url": "https://x/c.csv",
        },
        {"id": "dddd4444-x", "name": "", "format": "CSV", "url": "https://x/d.csv"},
    ]
    run1 = _entradas(monkeypatch, "rodovias", "volume-radar", resources)
    run2 = _entradas(monkeypatch, "rodovias", "volume-radar", resources)
    assert len({e["id"] for e in run1}) == 4
    n1, n2 = _nomes(run1), _nomes(run2)
    assert len(set(n1)) == 4
    assert n1 == n2
    assert all(n.isascii() and n.startswith("volume-radar_") for n in n1)
    assert all(e["resource_key"] for e in run1)


@pytest.mark.parametrize(
    ("grupo", "slug"),
    [
        ("cargas", "ciot"),
        ("rodovias", "volume-trafego-equivalente-praca-pedagio"),
        ("rodovias", "quantidade-possiveis-infratores"),
        ("rodovias", "volume-sat"),
    ],
)
def test_multirecurso_cobre_pacotes_do_ledger(
    monkeypatch: pytest.MonkeyPatch, grupo: str, slug: str
) -> None:
    resources = [
        {
            "id": f"id{i}abcdef",
            "name": f"Conc {i}",
            "format": "CSV",
            "url": f"https://x/{i}.csv",
        }
        for i in range(3)
    ]
    ent = _entradas(monkeypatch, grupo, slug, resources)
    nomes = _nomes(ent)
    assert len(set(nomes)) == 3
    assert all(n.startswith(f"{slug}_") for n in nomes)


def test_pacote_de_recurso_unico_mantem_o_nome(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resources = [
        {"id": "z", "name": "Único", "format": "CSV", "url": "https://x/u.csv"},
        {"id": "p", "name": "Dic", "format": "PDF", "url": "https://x/d.pdf"},
    ]
    ent = _entradas(monkeypatch, "rodovias", "volume-radar", resources)
    assert ent[0]["resource_key"] is None
    assert _nomes(ent) == ["volume-radar@20260928.csv"]
