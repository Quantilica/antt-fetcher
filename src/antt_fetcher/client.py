"""HTTP and CKAN client for ANTT open data."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from quantilica.core.ckan import CkanClient, pick_resources
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
        """Pick best resources from package, prioritizing CSV over JSON."""
        return pick_resources(package, prefer=prefer, dedupe_by_name=True)

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
