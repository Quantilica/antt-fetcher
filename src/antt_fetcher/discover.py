"""Descoberta de pacotes novos, removidos e crescidos da ANTT frente ao catálogo.

Compara o ``package_search`` do CKAN com :data:`antt_fetcher.catalog.CATALOG`:

- pacotes novos no CKAN, ainda fora do catálogo;
- pacotes do catálogo que sumiram do CKAN ("removido na fonte"; o bruto já
  baixado é mantido);
- pacotes com mais recursos CSV/JSON que o snapshot (novos meses/anos).

O portal fica atrás de um WAF (F5 ASM): resposta HTML ("Request Rejected") não
é lista de pacotes e vira ``RuntimeError``, nunca "tudo removido".
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any

from .catalog import CATALOG
from .client import AnttClient

__all__ = ["DiscoverReport", "discover"]


@dataclass
class DiscoverReport:
    """Resultado de :func:`discover`."""

    new_packages: list[dict[str, Any]] = field(default_factory=list)
    removed_packages: list[str] = field(default_factory=list)
    grown_packages: dict[str, dict[str, int]] = field(default_factory=dict)
    regrouped_packages: dict[str, dict[str, str]] = field(default_factory=dict)
    known: int = 0

    @property
    def has_changes(self) -> bool:
        """Indica se há algo novo, removido ou crescido em relação ao catálogo."""
        return bool(
            self.new_packages
            or self.removed_packages
            or self.grown_packages
            or self.regrouped_packages
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte o relatório em dict serializável."""
        data = asdict(self)
        data["has_changes"] = self.has_changes
        return data


def _formats(package: dict[str, Any]) -> Counter[str]:
    return Counter(
        str(r.get("format") or "").strip().upper()
        for r in package.get("resources") or []
    )


def discover(
    packages: Iterable[dict[str, Any]] | None = None,
    *,
    client: AnttClient | None = None,
) -> DiscoverReport:
    """Compara o CKAN da ANTT com o catálogo estático.

    Args:
        packages: Pacotes do ``package_search``; se ``None``, consulta o CKAN.
        client: Cliente da ANTT (usado só quando ``packages`` é ``None``).

    Returns:
        DiscoverReport: Pacotes novos/removidos/crescidos.

    Raises:
        RuntimeError: Se a consulta ao CKAN não devolver pacotes (portal fora do
            ar ou página de erro do WAF).
    """
    if packages is None:
        packages = (client or AnttClient()).search_packages(rows=1000)
    by_slug = {str(p["name"]): p for p in packages}
    if not by_slug:
        raise RuntimeError("CKAN da ANTT não devolveu pacotes (portal ou WAF?).")

    report = DiscoverReport()
    for slug, package in sorted(by_slug.items()):
        dataset = CATALOG.get(slug)
        fmts = _formats(package)
        if dataset is None:
            report.new_packages.append(
                {
                    "slug": slug,
                    "title": package.get("title", slug),
                    "groups": sorted({g["name"] for g in package.get("groups") or []}),
                    "n_csv": fmts.get("CSV", 0),
                    "n_json": fmts.get("JSON", 0),
                }
            )
            continue
        report.known += 1
        if fmts.get("CSV", 0) > dataset.n_csv or fmts.get("JSON", 0) > dataset.n_json:
            report.grown_packages[slug] = {
                "n_csv_catalogo": dataset.n_csv,
                "n_csv_atual": fmts.get("CSV", 0),
                "n_json_catalogo": dataset.n_json,
                "n_json_atual": fmts.get("JSON", 0),
            }
    report.removed_packages = sorted(
        ds.slug
        for ds in CATALOG.values()
        if ds.group != "govbr" and ds.slug not in by_slug
    )
    return report
