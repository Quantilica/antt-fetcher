"""HTTP and CKAN client for ANTT open data."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from quantilica.core.ckan import CkanClient
from quantilica.core.http import HttpClient
from quantilica.core.logging import get_logger
from quantilica.core.manifests import DownloadManifest

from .constants import ANTT_CKAN_URL

logger = get_logger(__name__)


class AnttClient:
    """Client for discovering and downloading ANTT datasets via CKAN."""

    def __init__(
        self,
        *,
        base_url: str = ANTT_CKAN_URL,
        client: HttpClient | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or HttpClient(timeout=120.0)
        self.logger = logger or get_logger(__name__)
        self.ckan = CkanClient(base_url, client=self.client, logger=self.logger)

    def package_show(self, package_id: str) -> dict[str, Any]:
        """Fetch package details from ANTT CKAN."""
        return self.ckan.package_show(package_id)

    def search_packages(
        self, q: str | None = None, rows: int = 1000
    ) -> list[dict[str, Any]]:
        """Search ANTT CKAN packages."""
        return list(self.ckan.iter_packages(q=q, rows=rows))

    def pick_package_resources(
        self,
        package: dict[str, Any],
        *,
        prefer: Sequence[str] = ("CSV", "JSON", "ZIP"),
    ) -> list[dict[str, Any]]:
        """Escolhe um recurso por arquivo, preferindo CSV a JSON.

        Agrupa pelo nome do arquivo da URL (sem extensão), e não pelo ``name``
        do CKAN: o portal reaproveita o mesmo ``name`` em arquivos distintos
        (ex.: vários ``radar`` de concessionárias), o que fundia arquivos
        diferentes. Em duplicatas do mesmo arquivo, vence o formato preferido e
        depois o maior ``size`` (cópias vazias, só com cabeçalho, perdem).
        """
        ranks = {fmt.upper(): rank for rank, fmt in enumerate(prefer)}
        groups: dict[str, list[dict[str, Any]]] = {}
        for resource in package.get("resources") or []:
            url = str(resource.get("url") or "")
            filename = url.rsplit("/", 1)[-1].split("?", 1)[0]
            stem = filename.rsplit(".", 1)[0].strip().lower()
            key = stem or str(resource.get("name") or resource.get("id") or "").strip()
            groups.setdefault(key, []).append(resource)

        def order(resource: dict[str, Any]) -> tuple[int, int]:
            fmt = str(resource.get("format") or "").strip().upper()
            try:
                size = int(resource.get("size") or 0)
            except (TypeError, ValueError):
                size = 0
            return ranks.get(fmt, 999), -size

        return [min(candidates, key=order) for candidates in groups.values()]

    def download_resource(
        self,
        url: str,
        dest: Path,
        *,
        manifest_path: Path | None = None,
    ) -> DownloadManifest:
        """Download single resource with manifest sidecar and WAF validation."""
        manifest = self.client.download_with_manifest(
            url,
            dest,
            manifest_path=manifest_path,
        )

        # Validate that response was not an HTML error or WAF rejection
        if dest.exists() and dest.stat().st_size < 10000:
            sample = dest.read_bytes().lower()
            if b"<html" in sample or b"request rejected" in sample:
                dest.unlink(missing_ok=True)
                if manifest_path and manifest_path.exists():
                    manifest_path.unlink(missing_ok=True)
                raise ValueError(
                    f"Download rejeitado pelo WAF ou devolveu HTML de erro: {url}"
                )

        return manifest
