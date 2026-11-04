"""Shared types and helper constructors for antt-fetcher catalogs."""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass
from typing import Any, Literal

Tier = Literal["r1", "listed"]


@dataclass(frozen=True)
class DatasetEntry:
    """Represents a single dataset entry to be downloaded."""

    id: str
    base_id: str
    name: str
    url: str
    ext: str
    group: str
    source: str = "antt"
    year: int | None = None
    quarter: int | None = None
    month: int | None = None
    slug: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dict."""
        return asdict(self)


@dataclass(frozen=True)
class GroupInfo:
    """Represents a logical group of dataset entries."""

    name: str
    entries: list[DatasetEntry]

    def to_dict(self) -> dict[str, Any]:
        """Convert group to dict."""
        return {
            "name": self.name,
            "entries": [e.to_dict() for e in self.entries],
        }


def static_dataset(
    group: str,
    *,
    id: str,
    name: str,
    url: str,
    ext: str = "csv",
) -> DatasetEntry:
    """Construct a static (single-file) dataset entry."""
    return DatasetEntry(
        id=id,
        base_id=id,
        name=name,
        url=url,
        ext=ext,
        group=group,
    )


def annual_datasets(
    group: str,
    *,
    base_id: str,
    name_template: str,
    url_template: str,
    start_year: int,
    end_year: int | None = None,
    ext: str = "csv",
) -> list[DatasetEntry]:
    """Construct annual dataset entries."""
    end = end_year or dt.date.today().year
    return [
        DatasetEntry(
            id=f"{base_id}_{y}",
            base_id=base_id,
            name=name_template.format(year=y),
            url=url_template.format(year=y),
            ext=ext,
            group=group,
            year=y,
        )
        for y in range(start_year, end + 1)
    ]


@dataclass(frozen=True)
class AnttDataset:
    """Descritor estático de um pacote do CKAN da ANTT.

    Attributes:
        slug: Nome do pacote no CKAN (``base_id`` das entradas).
        group: Grupo (domínio) canônico.
        title: Título do pacote.
        tier: ``r1`` (baixa hoje) ou ``listed`` (listado; download em release futura).
        n_csv: Recursos CSV no snapshot de 2026-11-03.
        n_json: Recursos JSON no snapshot de 2026-11-03.
        n_other: Arquivos de dados fora do CKAN (ex.: XLSX do gov.br).
        note: Observação (volume, ausência de CSV/JSON etc.).
    """

    slug: str
    group: str
    title: str
    tier: Tier
    n_csv: int = 0
    n_json: int = 0
    n_other: int = 0
    note: str = ""

    @property
    def downloadable(self) -> bool:
        """Indica se há CSV, JSON ou outro arquivo de dados para baixar."""
        return bool(self.n_csv or self.n_json or self.n_other)

    def to_dict(self) -> dict[str, Any]:
        """Converte o descritor em dict."""
        data = asdict(self)
        data["downloadable"] = self.downloadable
        return data
