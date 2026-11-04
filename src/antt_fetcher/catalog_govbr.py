"""Catálogo ANTT do domínio ``govbr`` — dados publicados só no portal gov.br.

A produção de transporte ferroviário de carga (origem-destino, 2006 em diante)
não está no CKAN: é um XLSX na página de ferrovias do gov.br, cujo nome muda a
cada atualização mensal. O catálogo guarda a página; a URL do arquivo é
resolvida em :func:`antt_fetcher.catalog.resolve_govbr_url`.
"""

from __future__ import annotations

from ._catalog_base import AnttDataset
from .constants import GOVBR_FERROVIAS_PAGE

GROUP = "govbr"
NAME = "Dados no portal gov.br (fora do CKAN)"

PAGES: dict[str, str] = {
    "producao-ferroviaria-origem-destino": GOVBR_FERROVIAS_PAGE,
}

DATASETS: tuple[AnttDataset, ...] = (
    AnttDataset(
        slug="producao-ferroviaria-origem-destino",
        group=GROUP,
        title="Produção do transporte ferroviário de carga - origem e destino",
        tier="r1",
        n_other=1,
        note="XLSX único no gov.br (9,1 MB); HEAD recusado (403), GET com Range ok.",
    ),
)
