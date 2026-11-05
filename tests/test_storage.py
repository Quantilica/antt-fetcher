"""Tests for antt-fetcher storage."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from antt_fetcher.storage import DataRepository


def test_path_for_entry_fallback_timestamp(tmp_path: Path) -> None:
    """When last_modified is None, filename gets today's @YYYYMMDD timestamp."""
    repo = DataRepository(tmp_path)
    entry = {
        "group": "test",
        "ext": "csv",
        "base_id": "test-dataset",
    }
    today = dt.date.today()
    expected_suffix = f"@{today:%Y%m%d}.csv"

    path = repo.path_for_entry(entry, last_modified=None)

    assert path.name.endswith(expected_suffix)
    assert path.parent.name == "test"


def test_path_for_entry_with_explicit_timestamp(tmp_path: Path) -> None:
    """When last_modified is provided, filename uses that timestamp."""
    repo = DataRepository(tmp_path)
    entry = {
        "group": "test",
        "ext": "csv",
        "base_id": "test-dataset",
    }
    explicit_date = dt.date(2024, 1, 15)
    expected_suffix = "@20240115.csv"

    path = repo.path_for_entry(entry, last_modified=explicit_date)

    assert path.name.endswith(expected_suffix)


def test_path_for_entry_with_year_month(tmp_path: Path) -> None:
    """Path includes year-month partition when year and month provided."""
    repo = DataRepository(tmp_path)
    entry = {
        "group": "rodovias",
        "ext": "csv",
        "base_id": "volume-trafego",
        "year": 2024,
        "month": 3,
    }
    explicit_date = dt.date(2024, 3, 15)

    path = repo.path_for_entry(entry, last_modified=explicit_date)

    assert "2024-03" in path.name
    assert path.name.endswith("@20240315.csv")


def test_path_for_entry_with_year_quarter(tmp_path: Path) -> None:
    """Path includes year-quarter partition when year and quarter provided."""
    repo = DataRepository(tmp_path)
    entry = {
        "group": "ferrovias",
        "ext": "csv",
        "base_id": "carga-ferroviaria",
        "year": 2024,
        "quarter": 1,
    }
    explicit_date = dt.date(2024, 3, 31)

    path = repo.path_for_entry(entry, last_modified=explicit_date)

    assert "2024-T01" in path.name
    assert path.name.endswith("@20240331.csv")


def test_path_for_entry_with_year_only(tmp_path: Path) -> None:
    """Path includes year partition when only year provided."""
    repo = DataRepository(tmp_path)
    entry = {
        "group": "cargas",
        "ext": "csv",
        "base_id": "pesos-brutos",
        "year": 2024,
    }
    explicit_date = dt.date(2024, 12, 31)

    path = repo.path_for_entry(entry, last_modified=explicit_date)

    assert "2024" in path.name
    assert path.name.endswith("@20241231.csv")


def test_path_for_entry_with_slug(tmp_path: Path) -> None:
    """Path includes slug in partition when provided."""
    repo = DataRepository(tmp_path)
    entry = {
        "group": "rodovias",
        "ext": "csv",
        "base_id": "volume-trafego",
        "year": 2024,
        "month": 3,
        "slug": "praca-pedagio-1",
    }
    explicit_date = dt.date(2024, 3, 15)

    path = repo.path_for_entry(entry, last_modified=explicit_date)

    assert "2024-03_praca-pedagio-1" in path.name


def _entry(**kw):
    base = {"group": "rodovias", "ext": "csv", "base_id": "volume-radar"}
    base.update(kw)
    return base


def test_recursos_distintos_do_mesmo_pacote_nao_colidem(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path)
    dia = dt.date(2026, 9, 28)
    a = repo.path_for_entry(
        _entry(resource_key="radar-concessionaria-a-1a2b3c4d"), last_modified=dia
    )
    b = repo.path_for_entry(
        _entry(resource_key="radar-concessionaria-b-5e6f7a8b"), last_modified=dia
    )
    assert a != b
    assert a.name == "volume-radar_radar-concessionaria-a-1a2b3c4d@20260928.csv"


def test_recurso_unico_mantem_o_nome_atual(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path)
    dia = dt.date(2026, 9, 28)
    assert repo.path_for_entry(_entry(resource_key=None), last_modified=dia).name == (
        "volume-radar@20260928.csv"
    )
    assert repo.path_for_entry(_entry(), last_modified=dia).name == (
        "volume-radar@20260928.csv"
    )
    # entradas govbr (sem pacote CKAN) e particionadas seguem iguais
    govbr = {"group": "govbr", "ext": "xlsx", "base_id": "producao-ferroviaria-od"}
    assert repo.path_for_entry(govbr, last_modified=dia).name == (
        "producao-ferroviaria-od@20260928.xlsx"
    )
    part = _entry(year=2024, month=3, slug="s")
    assert repo.path_for_entry(part, last_modified=dia).name == (
        "volume-radar_2024-03_s@20260928.csv"
    )


def test_resource_key_com_particao(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path)
    dia = dt.date(2026, 9, 28)
    name = repo.path_for_entry(
        _entry(resource_key="k-12345678", year=2024), last_modified=dia
    ).name
    assert name == "volume-radar_k-12345678_2024@20260928.csv"
