"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import typer
from quantilica.cli.sdk import FetcherApp, make_resolve_groups
from quantilica.cli.ui import get_console
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, catalog_rows, list_datasets
from .storage import DataRepository

console = get_console()


def _out(text: str) -> None:
    """Imprime texto literal no console Rich compartilhado (sem markup/quebra)."""
    console.print(text, markup=False, highlight=False, emoji=False, soft_wrap=True)


# O SDK espera ``alias -> lista de grupos`` (string crua viraria ``list("x")``).
ALIASES: dict[str, list[str]] = GROUP_ALIASES
resolve_groups = make_resolve_groups(GROUPS, ALIASES)


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Build local storage path for a dataset entry."""
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


fetcher = FetcherApp(
    name="antt",
    help="Coletor e conversor Lake Hive de dados abertos da ANTT",
    groups_dict=GROUPS,
    aliases_dict=ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/antt"),
    freshness_policy=FreshnessPolicy.HEAD_FALLBACK_GET,
)


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte arquivos brutos de antt para o lake Hive (Parquet)."""
    try:
        from antt_fetcher import lake
    except ImportError as exc:
        raise ImportError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install antt --extra analysis"
        ) from exc
    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


def catalogo(
    grupo: str | None = typer.Argument(None, help="Grupo, alias ou macro-alias"),
    tier: str | None = typer.Option(None, help="r1 (baixa hoje) ou listed"),
    as_json: bool = typer.Option(False, "--json", help="Saída em JSON"),
) -> None:
    """Mostra o catálogo completo de pacotes (R1 e listados, sem rede)."""
    rows = catalog_rows(grupo, tier)
    if as_json:
        _out(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for row in rows:
        _out(
            f"{row['group']:<13} {row['tier']:<6} csv={row['n_csv']:<4} "
            f"json={row['n_json']:<4} {row['slug']}"
        )
    n_r1 = sum(1 for r in rows if r["tier"] == "r1")
    _out(f"\n{len(rows)} conjunto(s): {n_r1} R1, {len(rows) - n_r1} listados.")


def discover_cmd(
    as_json: bool = typer.Option(False, "--json", help="Saída em JSON"),
    fail_on_change: bool = typer.Option(
        False, "--fail-on-change", help="Sai com código 1 se houver novidade"
    ),
) -> None:
    """Detecta pacotes novos, removidos ou crescidos no CKAN da ANTT."""
    from .discover import discover

    report = discover()
    if as_json:
        _out(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        _out(f"{report.known} pacote(s) do catálogo encontrados no CKAN.")
        for pkg in report.new_packages:
            _out(f"NOVO     {pkg['slug']}: {pkg['title']}")
        for slug in report.removed_packages:
            _out(f"REMOVIDO NA FONTE {slug} (bruto mantido)")
        for slug, info in report.grown_packages.items():
            _out(
                f"CRESCEU  {slug}: csv {info['n_csv_catalogo']} -> "
                f"{info['n_csv_atual']}, json {info['n_json_catalogo']} -> "
                f"{info['n_json_atual']}"
            )
        if not report.has_changes:
            _out("Sem novidades em relação ao catálogo.")
    if fail_on_change and report.has_changes:
        raise typer.Exit(1)


fetcher.attach_command(catalogo, name="catalogo")
fetcher.attach_command(discover_cmd, name="discover")
fetcher.command_convert(convert)
fetcher.command_pipeline(convert)


app = fetcher.app
