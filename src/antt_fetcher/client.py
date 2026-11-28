"""HTTP and CKAN client for ANTT open data."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from quantilica.core.ckan import CkanClient
from quantilica.core.http import HttpClient, resolve_verify_from_env
from quantilica.core.logging import get_logger
from quantilica.core.storage import ExpectedFormat, expected_format_for_path

from .constants import ANTT_CKAN_URL

logger = get_logger(__name__)


def _default_http_client() -> HttpClient:
    """Cliente padrão do host (``QUANTILICA_HTTP_*``, SSL, CA), com plano B do core."""
    try:
        from quantilica.cli.sdk import default_client
    except ImportError:  # CLI autônoma, sem o host instalado
        return HttpClient(verify=resolve_verify_from_env(), emulate_browser=True)
    return default_client()


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
        self.client = client or _default_http_client()
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
        dataset_id: str,
        source_id: str = "antt",
        producer: str = "antt-fetcher",
        force: bool = False,
        expected_format: ExpectedFormat | None = None,
    ) -> Path:
        """Baixa um recurso com manifesto lateral (``<dest>.manifest.json``).

        O formato esperado sai da extensão de ``dest`` quando não é informado, e
        a assinatura do conteúdo é conferida antes de gravar: página de erro ou de
        bloqueio do WAF com HTTP 200 levanta ``CorruptPayloadError`` e não deixa
        arquivo nem manifesto.

        Returns:
            Path: O caminho do arquivo baixado (ou já em dia).
        """
        return self.client.download_with_manifest(
            url,
            dest,
            source_id=source_id,
            dataset_id=dataset_id,
            producer=producer,
            force=force,
            expected_format=expected_format or expected_format_for_path(dest),
        )
