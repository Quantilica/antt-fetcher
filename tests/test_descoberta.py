"""Falha de descoberta do catálogo vira erro do ``sync`` e do ``check`` (sem rede)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pytest
from quantilica.cli.sdk import FetcherApp
from typer.testing import CliRunner

from antt_fetcher import catalog
from antt_fetcher.plugin import EXPECTED_EMPTY_GROUPS, app, fetcher

runner = CliRunner()

PACOTES = ["pacote-bom", "pacote-fora"]


def _recurso(slug: str) -> dict[str, Any]:
    return {
        "id": f"id-{slug}",
        "name": f"Recurso {slug}",
        "format": "CSV",
        "url": f"https://x/{slug}.csv",
        "size": "100",
        "last_modified": "2026-05-01T10:00:00",
    }


@pytest.fixture(autouse=True)
def ckan_falso(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """CKAN falso: ``pacote-fora`` falha; ``estado['fora']`` liga/desliga a falha."""
    estado: dict[str, Any] = {"fora": {"pacote-fora"}, "chamadas": []}

    def package_show(self: Any, package_id: str) -> dict[str, Any]:
        estado["chamadas"].append(package_id)
        if package_id in estado["fora"]:
            raise RuntimeError("HTTP 503 do CKAN")
        return {"resources": [_recurso(package_id)]}

    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(catalog, "_FAILURES", {})
    monkeypatch.setattr(
        catalog,
        "DATASETS_BY_GROUP",
        {
            "rodovias": list(PACOTES),
            "cargas": ["pacote-fora"],
            "ouvidoria": [],
            "govbr": [],
        },
        raising=False,
    )
    monkeypatch.setattr(catalog.AnttClient, "package_show", package_show)
    monkeypatch.setattr(
        catalog.AnttClient,
        "pick_package_resources",
        lambda self, package, prefer=("CSV", "JSON", "ZIP"): package["resources"],
    )
    fetcher._falhas_descoberta.clear()
    return estado


@pytest.fixture(autouse=True)
def download_simulado(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Sem rede: o download de cada entrada dá certo e anota o id."""
    baixados: list[str] = []

    def baixa(self: Any, entry: dict, output_dir: Path, **kw: Any) -> Path:
        baixados.append(entry["id"])
        return output_dir / entry["id"]

    monkeypatch.setattr(FetcherApp, "download_entry", baixa)
    return baixados


def _sync(tmp_path: Path, *grupos: str):
    resumo = tmp_path / "resumo.json"
    res = runner.invoke(
        app,
        ["sync", *grupos, "-o", str(tmp_path / "bruto"), "--summary-json", str(resumo)],
    )
    dados = json.loads(resumo.read_text()) if resumo.exists() else None
    return res, dados


def test_pacote_que_falha_conta_como_falha_do_grupo() -> None:
    entries = catalog.list_datasets("rodovias")
    assert [e["slug"] for e in entries] == ["pacote-bom"]  # o outro segue baixando
    (falha,) = catalog.group_failures("rodovias")
    assert falha.startswith("pacote-fora: RuntimeError: ")
    assert "503" in falha
    assert catalog.group_failures("cargas") == []  # grupo não listado


def test_falha_nao_vai_para_o_cache(ckan_falso: dict[str, Any]) -> None:
    """A próxima listagem tenta de novo; com o CKAN de volta, a falha some."""
    catalog.list_datasets("rodovias")
    assert "rodovias" not in catalog._CACHE
    ckan_falso["fora"] = set()
    entries = catalog.list_datasets("rodovias")
    assert [e["slug"] for e in entries] == PACOTES
    assert catalog.group_failures("rodovias") == []
    assert "rodovias" in catalog._CACHE
    chamadas = len(ckan_falso["chamadas"])
    catalog.list_datasets("rodovias")  # agora do cache
    assert len(ckan_falso["chamadas"]) == chamadas


def test_falha_vai_ao_log_em_error(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="antt_fetcher"):
        fetcher.listar_grupo("rodovias")
    mensagens = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("pacote-fora" in m and "503" in m for m in mensagens)
    assert any("grupo rodovias" in m for m in mensagens)


def test_sync_com_um_pacote_fora_sai_3(
    tmp_path: Path, download_simulado: list[str]
) -> None:
    res, resumo = _sync(tmp_path, "rodovias")
    assert res.exit_code == 3
    assert download_simulado  # o pacote bom baixou
    assert resumo is not None
    assert resumo["exit_code"] == 3
    (erro,) = resumo["errors"]
    assert erro["id"] == "descoberta:rodovias"
    assert "pacote-fora" in erro["message"] and "503" in erro["message"]
    assert resumo["failed"] == 1
    assert resumo["total"] == resumo["succeeded"] + 1


def test_sync_com_todos_os_pacotes_fora_sai_1_com_a_causa(tmp_path: Path) -> None:
    res, resumo = _sync(tmp_path, "cargas")
    assert res.exit_code == 1
    assert resumo is not None
    assert resumo["exit_code"] == 1
    assert "catálogo vazio" in resumo["error"]
    assert [e["id"] for e in resumo["errors"]] == ["descoberta:cargas"]
    assert "503" in resumo["errors"][0]["message"]


def test_falha_so_vale_para_o_grupo_pedido(
    tmp_path: Path, ckan_falso: dict[str, Any]
) -> None:
    """A falha de ``rodovias`` não vaza para um ``sync`` só de ``cargas``."""
    res, resumo = _sync(tmp_path, "rodovias")
    assert res.exit_code == 3
    ckan_falso["fora"] = {"outro"}  # o CKAN volta; ``cargas`` é sadio
    catalog._CACHE.clear()
    catalog._FAILURES.clear()
    fetcher._falhas_descoberta.clear()
    res, resumo = _sync(tmp_path, "cargas")
    assert res.exit_code == 0
    assert resumo is not None and resumo["errors"] == []


def test_grupo_so_de_catalogo_vazio_sai_0(tmp_path: Path) -> None:
    """``ouvidoria`` é vazio por desenho: sem aviso de catálogo vazio nem erro."""
    res, resumo = _sync(tmp_path, "ouvidoria")
    assert res.exit_code == 0
    assert resumo is not None
    assert resumo["errors"] == []
    assert resumo.get("empty_groups", []) == []


def test_grupos_vazios_por_desenho() -> None:
    assert set(EXPECTED_EMPTY_GROUPS) == {"ouvidoria", "tecnologia", "visualizacoes"}
    assert fetcher.expected_empty_groups == frozenset(EXPECTED_EMPTY_GROUPS)
    # Só grupos sem pacote R1 e sem descoberta própria.
    from antt_fetcher.constants import DATASETS_BY_GROUP

    sem_pacote = {g for g, slugs in DATASETS_BY_GROUP.items() if not slugs}
    assert set(EXPECTED_EMPTY_GROUPS) <= sem_pacote
    assert sem_pacote - set(EXPECTED_EMPTY_GROUPS) == {"govbr"}


def test_falha_nao_vaza_para_o_download_seguinte(tmp_path: Path) -> None:
    fetcher.listar_grupo("rodovias")
    assert fetcher._falhas_descoberta
    fetcher.download_datasets([], tmp_path)
    assert fetcher._falhas_descoberta == {}
    assert fetcher.download_datasets([], tmp_path) == (0, 0, [])


def test_erro_cita_so_as_primeiras_causas(tmp_path: Path) -> None:
    fetcher._falhas_descoberta["rodovias"] = [f"p{i}: erro" for i in range(8)]
    _, total, erros = fetcher.download_datasets([], tmp_path)
    assert total == 1
    ((eid, msg),) = erros
    assert eid == "descoberta:rodovias"
    assert "p4: erro" in msg and "p5: erro" not in msg
    assert "(+3 falha(s))" in msg


def test_check_com_falha_de_descoberta_sai_1_e_nao_grava_plano(
    tmp_path: Path,
) -> None:
    """Modo de plano: sem isto o ``check`` saía 0 e o ``sync --from-plan`` também."""
    plano = tmp_path / "plano.json"
    res = runner.invoke(
        app, ["check", "rodovias", "-o", str(tmp_path / "bruto"), "--out", str(plano)]
    )
    assert res.exit_code == 1
    assert not plano.exists()
    assert fetcher._falhas_descoberta == {}  # consumidas


def test_check_sem_falha_grava_o_plano(
    tmp_path: Path, ckan_falso: dict[str, Any]
) -> None:
    ckan_falso["fora"] = set()
    plano = tmp_path / "plano.json"
    res = runner.invoke(
        app, ["check", "rodovias", "-o", str(tmp_path / "bruto"), "--out", str(plano)]
    )
    assert res.exit_code == 0
    assert plano.exists()
    itens = json.loads(plano.read_text())["items"]
    assert [i["entry"]["slug"] for i in itens] == PACOTES


def test_govbr_fora_do_ar_e_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Cliente:
        def get(self, url: str) -> Any:
            raise ConnectionError("sem rota")

    monkeypatch.setattr(catalog.AnttClient, "__init__", lambda self: None)
    monkeypatch.setattr(catalog.AnttClient, "client", _Cliente(), raising=False)
    entries = catalog.list_datasets("govbr")
    assert entries == []
    (falha,) = catalog.group_failures("govbr")
    assert "ConnectionError" in falha and "sem rota" in falha
    assert "govbr" not in catalog._CACHE


def test_govbr_sem_o_link_do_xlsx_e_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resposta:
        text = "<html>pagina sem o arquivo</html>"

    class _Cliente:
        def get(self, url: str) -> Any:
            return _Resposta()

    monkeypatch.setattr(catalog.AnttClient, "__init__", lambda self: None)
    monkeypatch.setattr(catalog.AnttClient, "client", _Cliente(), raising=False)
    assert catalog.list_datasets("govbr") == []
    (falha,) = catalog.group_failures("govbr")
    assert "não encontrado" in falha


def test_govbr_saudavel_nao_tem_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resposta:
        text = '<a href="https://x/origem-destino-2026.xlsx">xlsx</a>'

    class _Cliente:
        def get(self, url: str) -> Any:
            return _Resposta()

    monkeypatch.setattr(catalog.AnttClient, "__init__", lambda self: None)
    monkeypatch.setattr(catalog.AnttClient, "client", _Cliente(), raising=False)
    entries = catalog.list_datasets("govbr")
    assert len(entries) == 1
    assert catalog.group_failures("govbr") == []
