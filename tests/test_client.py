"""Tests for AnttClient."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from quantilica.core.manifests import DownloadManifest

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


def test_download_resource_success(tmp_path) -> None:
    client = AnttClient()
    target = tmp_path / "dados_2024.csv"
    target.write_bytes(b"col1;col2\n1;2\n")
    mock_manifest = MagicMock(spec=DownloadManifest)
    with patch.object(
        client.client, "download_with_manifest", return_value=mock_manifest
    ):
        res = client.download_resource("https://example.com/test.csv", target)
        assert res == mock_manifest


def test_download_resource_waf_rejection(tmp_path) -> None:
    client = AnttClient()
    target = tmp_path / "dados_rejeitados.csv"
    target.write_bytes(b"<html><head><title>Request Rejected</title></head></html>")
    manifest_path = tmp_path / "dados_rejeitados.csv.manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    mock_manifest = MagicMock(spec=DownloadManifest)
    with patch.object(
        client.client, "download_with_manifest", return_value=mock_manifest
    ):
        with pytest.raises(ValueError, match="rejeitado pelo WAF"):
            client.download_resource(
                "https://example.com/test.csv", target, manifest_path=manifest_path
            )
    assert not target.exists()
    assert not manifest_path.exists()
