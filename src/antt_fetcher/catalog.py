"""Dataset catalog for antt-fetcher.

Os pacotes do CKAN da ANTT agrupam vários recursos (CSV/JSON/ZIP) e o `sync`
genérico do SDK baixaria apenas o JSON do pacote. O catálogo expande cada
pacote em uma entrada por recurso real, com a URL de download.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from ._catalog_base import DatasetEntry, GroupInfo
from .client import AnttClient
from .constants import DATASETS_BY_GROUP

__all__ = [
    "DatasetEntry",
    "GroupInfo",
    "GROUPS",
    "GROUP_ALIASES",
    "list_datasets",
]

GROUP_NAMES: dict[str, str] = {
    "rodovias": "Rodovias Federais Concedidas",
    "cargas": "Transporte Rodoviário de Cargas",
    "passageiros": "Transporte de Passageiros",
    "ferrovias": "Transporte Ferroviário",
    "fiscalizacao": "Fiscalização e Autos de Infração",
}

_FORMATOS = {"CSV", "JSON", "ZIP", "PARQUET"}
_CACHE: dict[str, list[dict[str, Any]]] = {}


def _slugify(value: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^\w-]+", "-", normalized).strip("-").lower()


def _ext(url: str, fmt: str) -> str:
    filename = url.rsplit("/", 1)[-1].split("?", 1)[0]
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return fmt.lower()


def _entries_for_group(group: str) -> list[dict[str, Any]]:
    """Expande os pacotes do grupo em uma entrada por recurso."""
    if group in _CACHE:
        return _CACHE[group]

    client = AnttClient()
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for package_slug in DATASETS_BY_GROUP.get(group, []):
        package = client.package_show(package_slug)
        for resource in client.pick_package_resources(package):
            fmt = str(resource.get("format") or "").strip().upper()
            if fmt not in _FORMATOS:
                continue
            url = str(resource.get("url") or "")
            if not url:
                continue
            name = str(resource.get("name") or resource.get("id") or package_slug)
            ident = _slugify(f"{package_slug}-{name}")[:80]
            if ident in seen:
                ident = _slugify(f"{ident}-{resource.get('id')}")[:80]
            seen.add(ident)
            entries.append(
                DatasetEntry(
                    id=ident,
                    base_id=package_slug,
                    name=name,
                    url=url,
                    ext=_ext(url, fmt),
                    group=group,
                    slug=package_slug,
                ).to_dict()
            )
    _CACHE[group] = entries
    return entries


GROUPS: dict[str, dict[str, Any]] = {
    grp: {"name": name, "entries": []} for grp, name in GROUP_NAMES.items()
}

GROUP_ALIASES: dict[str, str] = {
    "padrao": "rodovias",
    "principal": "rodovias",
}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Lista recursos reais dos pacotes CKAN, por grupo."""
    if group is None:
        entries: list[dict[str, Any]] = []
        for group_id in GROUPS:
            entries.extend(_entries_for_group(group_id))
        return entries

    canon = GROUP_ALIASES.get(group, group)
    if canon not in GROUPS:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    return list(_entries_for_group(canon))
