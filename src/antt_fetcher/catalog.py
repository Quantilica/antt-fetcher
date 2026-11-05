"""Dataset catalog for antt-fetcher.

Os pacotes do CKAN da ANTT agrupam vários recursos (CSV/JSON/ZIP) e o `sync`
genérico do SDK baixaria apenas o JSON do pacote. O catálogo expande cada
pacote em uma entrada por recurso real, com a URL de download.

O catálogo é em duas camadas, com um módulo ``catalog_<dominio>.py`` por grupo
(``CATALOG`` traz os 106 pacotes do CKAN mais o conjunto do gov.br):

- ``tier="r1"``: baixa hoje; é o que :func:`list_datasets` expande;
- ``tier="listed"``: catalogado, com download em release futura; visível em
  :func:`catalog_rows` e no comando ``catalogo``.
"""

from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from typing import Any

from . import (
    catalog_cargas,
    catalog_ferrovias,
    catalog_fiscalizacao,
    catalog_govbr,
    catalog_ouvidoria,
    catalog_passageiros,
    catalog_rodovias,
    catalog_tecnologia,
    catalog_visualizacoes,
)
from ._catalog_base import AnttDataset, DatasetEntry, GroupInfo
from .client import AnttClient
from .constants import DATASETS_BY_GROUP

__all__ = [
    "DatasetEntry",
    "GroupInfo",
    "AnttDataset",
    "GROUPS",
    "GROUP_ALIASES",
    "MACRO_ALIASES",
    "CATALOG",
    "catalog_rows",
    "expand_group",
    "list_datasets",
    "resolve_govbr_url",
]

logger = logging.getLogger(__name__)

_MODULES = [
    catalog_rodovias,
    catalog_cargas,
    catalog_passageiros,
    catalog_ferrovias,
    catalog_fiscalizacao,
    catalog_ouvidoria,
    catalog_tecnologia,
    catalog_visualizacoes,
    catalog_govbr,
]

GROUP_NAMES: dict[str, str] = {mod.GROUP: mod.NAME for mod in _MODULES}

# slug -> descritor, de todos os conjuntos catalogados (R1 e listados).
CATALOG: dict[str, AnttDataset] = {
    ds.slug: ds for mod in _MODULES for ds in mod.DATASETS
}

_FORMATOS = {"CSV", "JSON", "ZIP", "PARQUET"}
_CACHE: dict[str, list[dict[str, Any]]] = {}
_GOVBR_XLSX_RE = re.compile(r'href="([^"]+origem-destino[^"]*\.xlsx)"', re.IGNORECASE)


def _slugify(value: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^\w-]+", "-", normalized).strip("-").lower()


def _resource_keys(
    usable: list[tuple[dict[str, Any], str, str]],
) -> dict[int, str]:
    """Identificador estavel e unico por recurso de um pacote com varios recursos.

    ``<slug do nome, ate 40 caracteres>-<8 primeiros caracteres do id do CKAN>``;
    sem id, usa um hash da URL. Deterministico, ASCII e sem data. Se duas chaves
    ainda coincidirem, o hash da URL desempata.
    """
    keys: dict[int, str] = {}
    used: set[str] = set()
    for index, (resource, _fmt, url) in enumerate(usable):
        name = str(resource.get("name") or "")
        rid = _slugify(str(resource.get("id") or ""))[:8]
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()  # noqa: S324
        tail = rid or digest[:8]
        key = "-".join(p for p in (_slugify(name)[:40].strip("-"), tail) if p)
        if key in used:
            key = f"{key}-{digest[:6]}"
        used.add(key)
        keys[index] = key
    return keys


def _ext(url: str, fmt: str) -> str:
    filename = url.rsplit("/", 1)[-1].split("?", 1)[0]
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return fmt.lower()


def resolve_govbr_url(html: str) -> str | None:
    """Extrai a URL do XLSX origem-destino da página do gov.br (ou ``None``)."""
    match = _GOVBR_XLSX_RE.search(html)
    return match.group(1) if match else None


def _govbr_entries() -> list[dict[str, Any]]:
    """Entrada do XLSX do gov.br, com a URL resolvida pela página."""
    client = AnttClient()
    entries: list[dict[str, Any]] = []
    for slug, page in catalog_govbr.PAGES.items():
        try:
            url = resolve_govbr_url(client.client.get(page).text)
        except Exception as exc:  # noqa: BLE001 - gov.br fora do ar não derruba o grupo
            logger.warning("gov.br indisponível (%s): %s", page, exc)
            continue
        if not url:
            logger.warning("XLSX origem-destino não encontrado em %s", page)
            continue
        entries.append(
            DatasetEntry(
                id=slug,
                base_id=slug,
                name=CATALOG[slug].title,
                url=url,
                ext="xlsx",
                group="govbr",
                slug=slug,
            ).to_dict()
        )
    return entries


def _entries_for_group(group: str) -> list[dict[str, Any]]:
    """Expande os pacotes R1 do grupo em uma entrada por recurso."""
    if group in _CACHE:
        return _CACHE[group]
    if group == "govbr":
        _CACHE[group] = _govbr_entries()
        return _CACHE[group]

    client = AnttClient()
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for package_slug in DATASETS_BY_GROUP.get(group, []):
        try:
            package = client.package_show(package_slug)
        except Exception as exc:  # noqa: BLE001 - pacote removido não derruba o grupo
            logger.warning("Pacote %s indisponível no CKAN: %s", package_slug, exc)
            continue
        usable: list[tuple[dict[str, Any], str, str]] = []
        for resource in client.pick_package_resources(package):
            fmt = str(resource.get("format") or "").strip().upper()
            if fmt not in _FORMATOS:
                continue
            url = str(resource.get("url") or "")
            if not url:
                continue
            usable.append((resource, fmt, url))
        # Pacote com varios recursos (um por concessionaria, por exemplo): o nome
        # local precisa distinguir os recursos, senao todos viram ``<pacote>@data``.
        keys = _resource_keys(usable) if len(usable) > 1 else {}
        for index, (resource, fmt, url) in enumerate(usable):
            name = str(resource.get("name") or resource.get("id") or package_slug)
            ident = _slugify(f"{package_slug}-{name}")[:80]
            if ident in seen:
                # sufixo depois do corte: o truncamento em 80 caracteres comia o
                # ano e o id do recurso, e as entradas colidiam.
                rid = _slugify(str(resource.get("id") or len(seen)))[:8]
                ident = f"{ident[:70].rstrip('-')}-{rid}"
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
                    resource_key=keys.get(index),
                ).to_dict()
            )
    _CACHE[group] = entries
    return entries


GROUPS: dict[str, dict[str, Any]] = {
    grp: {"name": name, "entries": []} for grp, name in GROUP_NAMES.items()
}

# Macro-aliases: um apelido que engloba vários grupos canônicos.
MACRO_ALIASES: dict[str, list[str]] = {
    "infraestrutura": ["rodovias", "ferrovias"],
    "transporte-rodoviario": ["rodovias", "cargas", "passageiros"],
    "gestao": ["ouvidoria", "tecnologia", "visualizacoes"],
}

GROUP_ALIASES: dict[str, list[str]] = {
    **MACRO_ALIASES,
    "padrao": ["rodovias"],
    "principal": ["rodovias"],
    "ferroviario": ["ferrovias"],
    "multas": ["fiscalizacao"],
    "autos": ["fiscalizacao"],
}


def expand_group(key: str) -> list[str]:
    """Expande um grupo, alias ou macro-alias em ids canônicos de grupo.

    Raises:
        ValueError: Se ``key`` não for grupo nem alias.
    """
    if key in GROUPS:
        return [key]
    targets = GROUP_ALIASES.get(key)
    if targets is None:
        raise ValueError(f"Grupo desconhecido: {key!r}")
    return [t for t in targets if t in GROUPS]


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Lista recursos reais dos pacotes CKAN R1, por grupo.

    Só o tier ``r1`` baixa hoje; os demais pacotes aparecem em
    :func:`catalog_rows`.
    """
    groups = list(GROUPS) if group is None else expand_group(group)
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for group_id in groups:
        for entry in _entries_for_group(group_id):
            if entry["id"] not in seen:
                seen.add(entry["id"])
                entries.append(entry)
    return entries


def catalog_rows(
    group: str | None = None, tier: str | None = None
) -> list[dict[str, Any]]:
    """Linhas do catálogo estático (um pacote por linha), sem rede."""
    groups = set(GROUPS if group is None else expand_group(group))
    return [
        ds.to_dict()
        for ds in CATALOG.values()
        if ds.group in groups and (tier is None or ds.tier == tier)
    ]
