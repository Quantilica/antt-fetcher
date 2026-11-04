"""Testes do ``discover`` da ANTT com amostra gravada do package_search."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from antt_fetcher.discover import discover

FIXTURE = Path(__file__).parent / "fixtures" / "package_search_amostra.json"


def _packages() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["packages"]


def test_amostra_conhecida_sem_pacotes_novos() -> None:
    report = discover(_packages())
    assert report.new_packages == []
    assert report.known == 7
    # o resto do catálogo não está na amostra: aparece como removido
    assert "rntrc" not in report.removed_packages
    assert "area-escape" in report.removed_packages


def test_detecta_novo_e_crescimento() -> None:
    packages = _packages()
    rntrc = next(p for p in packages if p["name"] == "rntrc")
    rntrc["resources"] = rntrc["resources"] * 40  # muito mais CSV que o snapshot
    packages.append(
        {
            "name": "pacote-inedito",
            "title": "Pacote inédito",
            "groups": [{"name": "rodovias"}],
            "resources": [{"name": "x", "format": "CSV", "url": "https://x/x.csv"}],
        }
    )
    report = discover(packages)
    assert [p["slug"] for p in report.new_packages] == ["pacote-inedito"]
    assert report.new_packages[0]["n_csv"] == 1
    assert report.grown_packages["rntrc"]["n_csv_atual"] == 80
    assert report.has_changes


def test_resposta_vazia_do_waf_nao_vira_tudo_removido() -> None:
    with pytest.raises(RuntimeError, match="não devolveu pacotes"):
        discover([])
