"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
import functools
import json
import logging
import threading
from pathlib import Path
from typing import Any

import typer
from quantilica.cli.sdk import (
    LISTING_ERROR_REASON,
    CheckPlanItem,
    FetcherApp,
    make_resolve_groups,
)
from quantilica.cli.ui import get_console
from quantilica.core.registry import FetcherInfo
from quantilica.core.sync import FreshnessPolicy

from .catalog import (
    GROUP_ALIASES,
    GROUPS,
    catalog_rows,
    expand_group,
    group_failure_records,
    list_datasets,
)
from .storage import DataRepository

console = get_console()
logger = logging.getLogger(__name__)

# Grupos só de catálogo (sem pacote para baixar): vazios por desenho. ``govbr`` e os
# grupos que baixam ficam de fora: se esvaziarem, é falha da fonte.
EXPECTED_EMPTY_GROUPS = ("ouvidoria", "tecnologia", "visualizacoes")
# Quantas causas a mensagem de erro de um grupo cita (o log traz todas).
MAX_CAUSAS_NO_ERRO = 5

LISTING_ERROR_TYPE = "listing-error"
# Verdadeiro só dentro do ``check`` (ver ``_tolerar_falha_de_descoberta``): lá cada
# pacote cuja descoberta falhou vira uma entrada sentinela, que o ``check_entry``
# devolve como ``skip-unavailable``/``listing-error``. No ``sync`` direto a falha
# vira o erro ``descoberta:<grupo>`` do ``download_datasets``.
_TOLERANT_LISTING = False


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


class AnttApp(FetcherApp):
    """``FetcherApp`` da ANTT.

    Faz a falha de descoberta (``package_show`` que falha, página do gov.br fora do
    ar ou sem o link) aparecer: sem isso o pacote sumia da lista só com um aviso e
    o ``sync`` saía 0 com menos arquivos, ou com nenhum.

    - ``sync`` direto: soma ao resultado um erro ``descoberta:<grupo>`` com as causas.
    - ``check``: cada falha vira um item ``skip-unavailable``/``listing-error`` do
      plano (o ``check`` sai 0 e grava o plano dos demais); o ``sync --from-plan``
      do host conta o item como erro.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        #: grupo -> falhas de descoberta vistas ao listar os grupos pedidos.
        self._falhas_descoberta: dict[str, list[str]] = {}
        self.list_datasets = self.listar_grupo

    def listar_grupo(self, group: str) -> list[dict[str, Any]]:
        """``list_datasets`` que registra as falhas de descoberta do grupo pedido."""
        entries = list_datasets(group)
        for canon in expand_group(group):
            registros = group_failure_records(canon)
            if not registros:
                self._falhas_descoberta.pop(canon, None)
                continue
            for registro in registros:
                logger.error("ANTT: descoberta do grupo %s falhou: %s", canon, registro)
            if _TOLERANT_LISTING:
                entries = [*entries, *(_sentinela(canon, r) for r in registros)]
            else:
                self._falhas_descoberta[canon] = [str(r) for r in registros]
        return entries

    def download_datasets(
        self,
        entries: list[dict[str, Any]],
        output_dir: Path,
        workers: int = 4,
        *,
        force: bool = False,
    ) -> tuple[int, int, list[tuple[str, str]]]:
        """Baixa as entradas e soma, aos erros, as falhas de descoberta pendentes.

        Cada grupo com falha de descoberta entra como um erro ``descoberta:<grupo>``
        com as causas: o ``sync`` sai 3 (algo baixou) ou 1 (nada baixou) e o
        ``--summary-json`` traz o grupo e a causa.
        """
        falhas, self._falhas_descoberta = self._falhas_descoberta, {}
        downloaded, total, errors = super().download_datasets(
            entries, output_dir, workers, force=force
        )
        erros_descoberta = [
            (f"descoberta:{grupo}", _resumir_causas(causas))
            for grupo, causas in sorted(falhas.items())
        ]
        return downloaded, total + len(erros_descoberta), errors + erros_descoberta


def _sentinela(grupo: str, falha: Any) -> dict[str, Any]:
    """Entrada sentinela de uma descoberta que falhou (vai ao plano do ``check``)."""
    return {
        "id": f"{LISTING_ERROR_TYPE}:{grupo}:{falha.item}",
        "group": grupo,
        "dataset": grupo,
        "url": falha.url,
        "type": LISTING_ERROR_TYPE,
        "error": falha.error,
        "error_class": falha.error_class,
    }


def _resumir_causas(causas: list[str]) -> str:
    """As primeiras causas, separadas por ``; ``, e quantas ficaram de fora."""
    texto = "; ".join(causas[:MAX_CAUSAS_NO_ERRO])
    resto = len(causas) - MAX_CAUSAS_NO_ERRO
    return f"{texto}; (+{resto} falha(s))" if resto > 0 else texto


fetcher = AnttApp(
    name="antt",
    help="Coletor e conversor Lake Hive de dados abertos da ANTT",
    info=FetcherInfo(
        id="antt",
        nome="ANTT - Dados Abertos",
        orgao="Agência Nacional de Transportes Terrestres (ANTT)",
        licenca="Creative Commons Atribuição (CC BY)",
        homepage="https://dados.antt.gov.br",
        cadencia="monthly",
        dominio="transporte",
    ),
    groups_dict=GROUPS,
    aliases_dict=ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/antt"),
    freshness_policy=FreshnessPolicy.HEAD_FALLBACK_GET,
    expected_empty_groups=EXPECTED_EMPTY_GROUPS,
)


def _ckan_validators(entry: dict[str, Any]) -> tuple[int, dt.datetime] | None:
    """Tamanho e ``last_modified`` do recurso no CKAN (UTC), ou ``None``."""
    try:
        size = int(entry.get("remote_size"))  # type: ignore[arg-type]
        moment = dt.datetime.fromisoformat(str(entry.get("remote_modified")))
    except (TypeError, ValueError):
        return None
    if size <= 0:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.UTC)
    return size, moment.astimezone(dt.UTC)


_index_lock = threading.Lock()
_IndexEntry = tuple[int, Path, dt.datetime | None]
_index_cache: dict[tuple[str, str], dict[str, _IndexEntry]] = {}


def _parse_moment(raw: Any) -> dt.datetime | None:
    """ISO 8601 em UTC (sem fuso vale UTC), ou ``None`` se ausente ou ilegível."""
    try:
        moment = dt.datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.UTC)
    return moment.astimezone(dt.UTC)


def _local_index(output_dir: Path, group: str) -> dict[str, _IndexEntry]:
    """``url -> (tamanho, caminho do bruto, momento do download)`` dos manifestos.

    Um manifesto por arquivo baixado; o bruto pode já ter sido removido pelo
    ingest, mas o manifesto fica (o SDK trata como "manifest-fresh"). O momento
    do download é o ``fetched_at`` do manifesto (``None`` se faltar). Montado
    uma vez por (pasta, grupo) e processo: o ``check`` roda em um processo só.
    """
    key = (str(output_dir), group)
    with _index_lock:
        index = _index_cache.get(key)
        if index is None:
            index = {}
            for sidecar in sorted((output_dir / group).glob("*.manifest.json")):
                try:
                    data = json.loads(sidecar.read_text(encoding="utf-8"))
                    url, size = str(data["url"]), int(data["size_bytes"])
                except (OSError, ValueError, KeyError, TypeError):
                    continue
                index[url] = (
                    size,
                    sidecar.with_name(sidecar.name[: -len(".manifest.json")]),
                    _parse_moment(data.get("fetched_at")),
                )
            _index_cache[key] = index
        return index


def _antt_check_entry(entry: dict[str, Any], output_dir: Path) -> CheckPlanItem:
    """Veredito de frescor sem HEAD quando o CKAN traz tamanho e data.

    O HEAD do portal leva ~20 s por recurso em horário de carga (1453 entradas
    por rodada). Com ``remote_size`` e ``remote_modified`` na entrada, vale o
    manifesto local da mesma URL: tamanho igual **e** ``last_modified`` do CKAN
    não posterior ao download é ``skip-up-to-date``; senão é ``download``, e o
    caminho usa a data do CKAN (o download recalcula o carimbo pelo
    ``Last-Modified``). Só o tamanho não basta: um arquivo corrigido com o mesmo
    número de bytes mudaria o ``last_modified`` do recurso e nunca seria
    rebaixado. Sem ``fetched_at`` no manifesto a data não pode ser comparada e
    vale o tamanho. Sem validadores, cai no check do SDK (HEAD).
    """
    if entry.get("type") == LISTING_ERROR_TYPE:
        # Sobrevive à reclassificação do plano (``skip-unavailable`` é mantido) e é
        # contado como erro pelo ``sync --from-plan``.
        return CheckPlanItem(
            dataset=str(entry.get("group") or "datasets"),
            id=str(entry.get("id", "unknown")),
            url=str(entry.get("url", "")),
            partition=None,
            local_path="",
            remote_etag=None,
            remote_last_modified=None,
            remote_size=None,
            local_exists=False,
            action="skip-unavailable",
            reason=LISTING_ERROR_REASON,
            entry=dict(entry),
        )
    validators = _ckan_validators(entry)
    if validators is None:
        return FetcherApp.check_entry(fetcher, entry, output_dir)
    size, moment = validators
    group = str(entry.get("group") or "default")
    known = _local_index(output_dir, group).get(str(entry["url"]))
    modified_after_download = (
        known is not None and known[2] is not None and moment > known[2]
    )
    if known is not None and known[0] == size and not modified_after_download:
        local, action, reason, exists = known[1], "skip-up-to-date", "ckan-fresh", True
    else:
        local = path_builder(output_dir, entry, moment.date())
        exists = known is not None
        action = "download"
        if not exists:
            reason = "ckan-not-present"
        elif known is not None and known[0] != size:
            reason = "ckan-changed"
        else:
            reason = "ckan-modified-after-download"
    return CheckPlanItem(
        dataset=str(entry.get("group") or entry.get("id") or "datasets"),
        id=str(entry.get("id", "unknown")),
        url=str(entry["url"]),
        partition=None,
        local_path=str(local),
        remote_etag=None,
        # Só quando este ``check`` concluiu ``ckan-modified-after-download``: aí o
        # momento do CKAN (UTC) segue no plano para a regra do reclassificador que
        # compara o tamanho com o da versão guardada não desfazer um reenvio de mesmo
        # tamanho. Nos demais casos fica ``None``: o ``Last-Modified`` HTTP guardado
        # tem precisão de segundos e a data do CKAN, de microssegundos, e uns décimos
        # de diferença (ou uma edição de metadados no CKAN depois do envio) fariam um
        # recurso inalterado ser rebaixado todo dia.
        remote_last_modified=(
            moment.isoformat() if reason == "ckan-modified-after-download" else None
        ),
        remote_size=size,
        local_exists=exists,
        action=action,
        reason=reason,
        entry=dict(entry),
    )


fetcher.check_entry = _antt_check_entry  # type: ignore[method-assign]


def _tolerar_falha_de_descoberta(callback: Any) -> Any:
    """Roda o ``check`` do host com a falha de descoberta tolerada.

    O ``check`` é a primeira etapa da coleta em modo de plano: se um pacote que
    responde 404 para sempre derrubasse o ``check``, não haveria plano e a coleta
    cairia no ``sync`` completo (milhares de requisições à fonte, todo dia). Com a
    tolerância, a falha vira um item ``skip-unavailable``/``listing-error`` e uma
    linha ERROR no log; o plano dos demais pacotes é gravado e o
    ``sync --from-plan`` conta a falha nos erros (saída 3 ou 1).
    """

    @functools.wraps(callback)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        global _TOLERANT_LISTING
        anterior, _TOLERANT_LISTING = _TOLERANT_LISTING, True
        try:
            return callback(*args, **kwargs)
        finally:
            _TOLERANT_LISTING = anterior

    return _wrapper


for _info in fetcher.app.registered_commands:
    if _info.name == "check" and _info.callback is not None:
        _info.callback = _tolerar_falha_de_descoberta(_info.callback)


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


# O conversor escolhe a versão vigente pelo recurso do manifesto, não pelo nome:
# o quantilica-cli deve entregar a pasta do bruto, sem montar a visão por nome.
convert.selects_versions = True  # type: ignore[attr-defined]


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
