"""Tests for antt-fetcher Typer plugin."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from antt_fetcher import catalog
from antt_fetcher.plugin import app


@pytest.fixture(autouse=True)
def fake_ckan(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita rede: injeta um recurso no cache do catálogo."""
    monkeypatch.setattr(
        catalog,
        "_CACHE",
        {
            "rodovias": [
                {
                    "id": "volume-trafego-praca-pedagio-volume-2024",
                    "base_id": "volume-trafego-praca-pedagio",
                    "name": "Volume de Tráfego 2024",
                    "url": "https://x/volume-2024.csv",
                    "ext": "csv",
                    "group": "rodovias",
                    "slug": "volume-trafego-praca-pedagio",
                }
            ],
            "cargas": [],
            "passageiros": [],
            "ferrovias": [],
            "fiscalizacao": [],
        },
    )


def test_cli_list() -> None:
    """Test quantilica antt list."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "rodovias" in result.output


def test_cli_convert_help() -> None:
    """Test quantilica antt convert --help."""
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "--lake" in result.output
