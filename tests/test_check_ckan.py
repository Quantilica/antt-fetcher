"""Check com validadores do CKAN e descoberta paralela (sem rede)."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import pytest

from antt_fetcher import catalog, plugin
from antt_fetcher.plugin import fetcher

URL_A = "https://dados.antt.gov.br/dataset/x/resource/a/download/radar-a.csv"
URL_B = "https://dados.antt.gov.br/dataset/x/resource/b/download/radar-b.csv"


def _entry(url: str = URL_A, **extra: Any) -> dict[str, Any]:
    return {
        "id": "volume-radar-a",
        "base_id": "volume-radar",
        "name": "Radar A",
        "url": url,
        "ext": "csv",
        "group": "rodovias",
        "slug": "volume-radar",
        "remote_size": 100,
        "remote_modified": "2026-06-28T16:01:55.000000",
        **extra,
    }


def _sidecar(out: Path, name: str, url: str, size: int) -> Path:
    target = out / "rodovias" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    side = Path(f"{target}.manifest.json")
    side.write_text(json.dumps({"url": url, "size_bytes": size}), encoding="utf-8")
    return target


@pytest.fixture
def no_head(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Falha o teste se o check fizer HEAD/GET de metadados."""
    calls: list[str] = []

    def boom(url: str, *a: Any, **k: Any) -> Any:
        calls.append(url)
        raise AssertionError(f"HEAD inesperado: {url}")

    monkeypatch.setattr(fetcher.client, "head", boom)
    return calls


def test_skip_sem_head_quando_manifesto_da_mesma_url_tem_o_mesmo_tamanho(
    tmp_path: Path, no_head: list[str]
) -> None:
    target = _sidecar(tmp_path, "volume-radar@20260628.csv", URL_A, 100)
    item = fetcher.check_entry(_entry(), tmp_path)
    assert item.action == "skip-up-to-date"
    assert item.reason == "ckan-fresh"
    assert item.local_path == str(target)
    assert item.local_exists is True
    assert item.remote_size == 100
    assert not no_head


def test_manifesto_de_outra_url_no_mesmo_caminho_nao_vale(
    tmp_path: Path, no_head: list[str]
) -> None:
    """Colisão de nomes: o dono do caminho é outra URL; baixa, sem HEAD."""
    _sidecar(tmp_path, "volume-radar@20260628.csv", URL_B, 100)
    item = fetcher.check_entry(_entry(), tmp_path)
    assert item.action == "download"
    assert item.reason == "ckan-not-present"
    assert item.local_path == str(tmp_path / "rodovias" / "volume-radar@20260628.csv")
    assert item.remote_size == 100
    assert item.remote_last_modified == "2026-06-28T16:01:55+00:00"


def test_tamanho_diferente_baixa(tmp_path: Path, no_head: list[str]) -> None:
    _sidecar(tmp_path, "volume-radar@20260101.csv", URL_A, 90)
    item = fetcher.check_entry(_entry(), tmp_path)
    assert item.action == "download"
    assert item.reason == "ckan-changed"
    assert item.local_exists is True


def test_url_com_carimbo_diferente_do_ckan_continua_fresca(
    tmp_path: Path, no_head: list[str]
) -> None:
    """O índice é por URL: a data do CKAN pode divergir do Last-Modified."""
    target = _sidecar(tmp_path, "volume-radar@20260701.csv", URL_A, 100)
    item = fetcher.check_entry(_entry(), tmp_path)
    assert item.action == "skip-up-to-date"
    assert item.local_path == str(target)


def test_sem_validadores_usa_o_head_do_sdk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[str] = []

    def fake_generic(self: Any, entry: dict[str, Any], out: Path) -> str:
        seen.append(entry["url"])
        return "generico"

    monkeypatch.setattr(plugin.FetcherApp, "check_entry", fake_generic)
    entry = _entry()
    entry.pop("remote_size")
    assert fetcher.check_entry(entry, tmp_path) == "generico"
    assert seen == [URL_A]


def test_caminho_do_download_nao_muda(tmp_path: Path) -> None:
    """Sem HEAD, o carimbo vem do CKAN, igual ao Last-Modified quando coincide."""
    import datetime as dt

    path = plugin.path_builder(tmp_path, _entry(), dt.date(2026, 6, 28))
    assert path == tmp_path / "rodovias" / "volume-radar@20260628.csv"


def test_descoberta_paralela_mantem_ordem_e_carrega_validadores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slugs = [
        "acidentes-rodovias",
        "receita-pedagio",
        "investimentos",
        "praca-de-pedagio",
    ]
    threads: set[int] = set()
    barrier = threading.Barrier(2, timeout=5)

    def package_show(self: Any, package_id: str) -> dict[str, Any]:
        threads.add(threading.get_ident())
        if package_id in slugs[:2]:
            barrier.wait()  # só passa se duas chamadas forem simultâneas
        return {
            "resources": [
                {
                    "id": f"id-{package_id}",
                    "name": f"Recurso {package_id}",
                    "format": "CSV",
                    "url": f"https://x/{package_id}.csv",
                    "size": "123",
                    "last_modified": "2026-05-01T10:00:00.5",
                }
            ]
        }

    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(
        catalog, "DATASETS_BY_GROUP", {"rodovias": slugs}, raising=False
    )
    monkeypatch.setattr(catalog.AnttClient, "package_show", package_show)
    monkeypatch.setattr(
        catalog.AnttClient,
        "pick_package_resources",
        lambda self, package, prefer=("CSV", "JSON", "ZIP"): package["resources"],
    )
    entries = catalog.list_datasets("rodovias")
    assert [e["slug"] for e in entries] == slugs
    assert len(threads) > 1
    assert entries[0]["remote_size"] == 123
    assert entries[0]["remote_modified"] == "2026-05-01T10:00:00.5"


def _sidecar_com_data(
    out: Path, name: str, url: str, size: int, fetched_at: str | None
) -> Path:
    target = out / "rodovias" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {"url": url, "size_bytes": size}
    if fetched_at is not None:
        data["fetched_at"] = fetched_at
    Path(f"{target}.manifest.json").write_text(json.dumps(data), encoding="utf-8")
    return target


def test_mesmo_tamanho_mas_ckan_modificado_depois_do_download_baixa(
    tmp_path: Path, no_head: list[str]
) -> None:
    """Arquivo corrigido com o mesmo número de bytes: o ``last_modified`` entrega."""
    _sidecar_com_data(
        tmp_path, "volume-radar@20260601.csv", URL_A, 100, "2026-06-01T03:00:00+00:00"
    )
    # _entry(): remote_modified 2026-06-28, bem depois do download de 06-01.
    item = fetcher.check_entry(_entry(), tmp_path)
    assert item.action == "download"
    assert item.reason == "ckan-modified-after-download"
    assert item.local_exists is True
    assert item.remote_size == 100
    assert not no_head


def test_mesmo_tamanho_e_ckan_anterior_ao_download_continua_fresco(
    tmp_path: Path, no_head: list[str]
) -> None:
    target = _sidecar_com_data(
        tmp_path, "volume-radar@20260628.csv", URL_A, 100, "2026-06-29T03:00:00+00:00"
    )
    item = fetcher.check_entry(_entry(), tmp_path)
    assert item.action == "skip-up-to-date"
    assert item.reason == "ckan-fresh"
    assert item.local_path == str(target)


def test_manifesto_sem_data_de_download_vale_o_tamanho(
    tmp_path: Path, no_head: list[str]
) -> None:
    _sidecar_com_data(tmp_path, "volume-radar@20260101.csv", URL_A, 100, None)
    assert fetcher.check_entry(_entry(), tmp_path).action == "skip-up-to-date"


def test_data_de_download_ilegivel_vale_o_tamanho(
    tmp_path: Path, no_head: list[str]
) -> None:
    _sidecar_com_data(tmp_path, "volume-radar@20260101.csv", URL_A, 100, "ontem")
    assert fetcher.check_entry(_entry(), tmp_path).action == "skip-up-to-date"


def test_tamanho_diferente_continua_sendo_ckan_changed(
    tmp_path: Path, no_head: list[str]
) -> None:
    _sidecar_com_data(
        tmp_path, "volume-radar@20260101.csv", URL_A, 90, "2026-12-01T00:00:00+00:00"
    )
    assert fetcher.check_entry(_entry(), tmp_path).reason == "ckan-changed"


def test_item_do_plano_traz_o_momento_do_ckan_em_utc(
    tmp_path: Path, no_head: list[str]
) -> None:
    """O reclassificador compara ``remote_last_modified`` com o da versão guardada."""
    novo = fetcher.check_entry(
        _entry(remote_modified="2026-06-28T16:01:55.5"), tmp_path / "a"
    )
    assert novo.action == "download"
    assert novo.remote_last_modified == "2026-06-28T16:01:55.500000+00:00"
    _sidecar(tmp_path / "b", "volume-radar@20260628.csv", URL_A, 100)
    fresco = fetcher.check_entry(_entry(), tmp_path / "b")
    assert fresco.action == "skip-up-to-date"
    assert fresco.remote_last_modified == "2026-06-28T16:01:55+00:00"
