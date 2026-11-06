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

import logging
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
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

# Chamadas simultâneas ao CKAN na descoberta (o portal fica atrás de um WAF).
CKAN_WORKERS = 4
_FORMATOS = {"CSV", "JSON", "ZIP", "PARQUET"}
_CACHE: dict[str, list[dict[str, Any]]] = {}
_GOVBR_XLSX_RE = re.compile(r'href="([^"]+origem-destino[^"]*\.xlsx)"', re.IGNORECASE)


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


def resolve_govbr_url(html: str) -> str | None:
    """Extrai a URL do XLSX origem-destino da página do gov.br (ou ``None``)."""
    match = _GOVBR_XLSX_RE.search(html)
    return match.group(1) if match else None


def _resource_size(resource: dict[str, Any]) -> int | None:
    """Tamanho do recurso no CKAN, ou ``None`` se ausente, zero ou inválido."""
    try:
        size = int(resource.get("size"))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return size if size > 0 else None


def _show_packages(
    client: AnttClient, slugs: list[str]
) -> dict[str, dict[str, Any] | None]:
    """``package_show`` de vários pacotes em paralelo (o CKAN leva ~6 s por chamada).

    O resultado é indexado por slug; a ordem de uso fica a cargo de quem chama,
    então os ids e a ordem das entradas não dependem do paralelismo. Pacote
    indisponível vira ``None`` (não derruba o grupo).
    """

    def one(slug: str) -> dict[str, Any] | None:
        try:
            return client.package_show(slug)
        except Exception as exc:  # noqa: BLE001 - pacote removido não derruba o grupo
            logger.warning("Pacote %s indisponível no CKAN: %s", slug, exc)
            return None

    if len(slugs) <= 1:
        return {slug: one(slug) for slug in slugs}
    with ThreadPoolExecutor(max_workers=CKAN_WORKERS) as pool:
        return dict(zip(slugs, pool.map(one, slugs), strict=True))


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
    slugs = DATASETS_BY_GROUP.get(group, [])
    packages = _show_packages(client, slugs)
    for package_slug in slugs:
        package = packages.get(package_slug)
        if package is None:
            continue
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
                    remote_size=_resource_size(resource),
                    remote_modified=str(resource.get("last_modified") or "") or None,
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
