"""Tests for AnttClient."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import httpx2
import pytest
from quantilica.core.exceptions import CorruptPayloadError
from quantilica.core.http import HttpClient

from antt_fetcher.client import AnttClient


def test_client_init() -> None:
    client = AnttClient()
    assert client.client is not None
    assert "antt.gov.br" in client.base_url


def test_package_show() -> None:
    client = AnttClient()
    mock_pkg = {"id": "pkg-1", "title": "Rodovias", "resources": []}
    with patch.object(client.ckan, "package_show", return_value=mock_pkg):
        res = client.package_show("pkg-1")
        assert res["id"] == "pkg-1"


def test_search_packages() -> None:
    client = AnttClient()
    mock_pkgs = [{"id": "pkg-1"}, {"id": "pkg-2"}]
    with patch.object(client.ckan, "iter_packages", return_value=iter(mock_pkgs)):
        res = client.search_packages("rodovias")
        assert len(res) == 2


def test_pick_package_resources() -> None:
    client = AnttClient()
    pkg = {
        "resources": [
            {"name": "volume_2024", "format": "JSON", "url": "https://.../1.json"},
            {"name": "volume_2024", "format": "CSV", "url": "https://.../1.csv"},
        ]
    }
    picked = client.pick_package_resources(pkg)
    assert len(picked) == 1
    assert picked[0]["format"] == "CSV"


def _client_with(handler) -> AnttClient:
    http = HttpClient(
        attempts=1, retry_base_delay=0.0, transport=httpx2.MockTransport(handler)
    )
    return AnttClient(client=http)


def test_download_resource_real_sem_mock_do_core(tmp_path: Path) -> None:
    """A assinatura chama o ``download_with_manifest`` de verdade (sem mock)."""
    body = b"col1;col2\n1;2\n"
    client = _client_with(
        lambda request: httpx2.Response(
            200,
            content=body,
            headers={"Last-Modified": "Wed, 01 Jan 2025 00:00:00 GMT"},
        )
    )
    target = tmp_path / "dados_2024.csv"
    path = client.download_resource(
        "https://dados.antt.test/dados_2024.csv", target, dataset_id="radar"
    )
    assert path == target
    assert target.read_bytes() == body
    manifest = json.loads((tmp_path / "dados_2024.csv.manifest.json").read_text())
    assert manifest["source_id"] == "antt"
    assert manifest["dataset_id"] == "radar"
    assert manifest["producer"] == "antt-fetcher"
    assert manifest["url"] == "https://dados.antt.test/dados_2024.csv"


def test_download_resource_rejeita_pagina_do_waf(tmp_path: Path) -> None:
    """HTML de bloqueio com HTTP 200 não vira arquivo nem manifesto."""
    html = b"<html><head><title>Request Rejected</title></head></html>"
    client = _client_with(
        lambda request: httpx2.Response(
            200, content=html, headers={"Content-Type": "text/html"}
        )
    )
    target = tmp_path / "dados_rejeitados.csv"
    with pytest.raises(CorruptPayloadError):
        client.download_resource(
            "https://dados.antt.test/test.csv", target, dataset_id="radar"
        )
    assert not target.exists()
    assert not (tmp_path / "dados_rejeitados.csv.manifest.json").exists()


def test_cliente_padrao_respeita_ambiente(monkeypatch: pytest.MonkeyPatch) -> None:
    """O cliente de catálogo vem do cliente padrão do host (``QUANTILICA_HTTP_*``)."""
    monkeypatch.setenv("QUANTILICA_HTTP_TIMEOUT", "12")
    monkeypatch.setenv("QUANTILICA_HTTP_ATTEMPTS", "2")
    client = AnttClient()
    assert client.client.timeout == 12.0
    assert client.client.attempts == 2


def test_pick_package_resources_nao_funde_arquivos_de_mesmo_name() -> None:
    """Mesmo ``name`` do CKAN em arquivos distintos não pode colapsar numa entrada."""
    client = AnttClient()
    pkg = {
        "resources": [
            {"name": "radar", "format": "CSV", "url": "https://x/a/radar_a.csv"},
            {"name": "radar", "format": "CSV", "url": "https://x/b/radar_b.csv"},
            {"name": "radar", "format": "JSON", "url": "https://x/b/radar_b.json"},
            {"name": "so-json", "format": "JSON", "url": "https://x/c/so_json.json"},
        ]
    }
    picked = client.pick_package_resources(pkg)
    assert sorted(r["url"].rsplit("/", 1)[-1] for r in picked) == [
        "radar_a.csv",
        "radar_b.csv",
        "so_json.json",
    ]
