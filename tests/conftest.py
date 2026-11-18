"""Pytest configuration and fixtures for antt-fetcher."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _cache_fora_do_lake(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Cache de cobertura num diretorio de teste (nunca o ``~/.cache`` real).

    Vale para todas as suites: qualquer conversao do lake grava o cache de
    cobertura do ``volume-sat`` aqui, e nao no ``~/.cache`` de quem roda.
    """
    cache = tmp_path / "cache"
    monkeypatch.setenv("QUANTILICA_LAKE_CACHE_DIR", str(cache))
    return cache
