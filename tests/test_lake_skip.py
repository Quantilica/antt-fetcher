"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import builtins
import hashlib
import json
import zipfile
from pathlib import Path

import polars as pl
import pytest
import quantilica.core.manifests as manifests_mod

import antt_fetcher.lake as lake_mod
from antt_fetcher.lake import converter

_ACID = "data;tipo_de_ocorrencia;km\n12/05/2024;COLISAO;120\n03/01/2025;TOMBAMENTO;7\n"
_PED = "concessionaria;mes_ano;volume_total\nAUTOPISTA;10/2024;15000\n"
_SAT_CAB = "concessionaria;data_de_passagem;volume_total\n"


def _sidecars(raiz: Path) -> None:
    """Sidecar ``.manifest.json`` com o sha256 de cada bruto, como o fetcher grava:
    o hash do bruto sai dele, sem ler o arquivo."""
    for f in sorted(raiz.rglob("*")):
        if f.is_file() and not f.name.endswith(".manifest.json"):
            Path(f"{f}.manifest.json").write_text(
                json.dumps(
                    {
                        "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                        "size_bytes": f.stat().st_size,
                    }
                ),
                encoding="utf-8",
            )


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw" / "rodovias"
    raw.mkdir(parents=True)
    # Nome do catalogo (``<slug>@AAAAMMDD``), nome antigo solto e ZIP antigo.
    (raw / "acidentes-rodovias@20261101.csv").write_text(_ACID, encoding="utf-8")
    (raw / "volume_pedagio_2024@20261101.csv").write_text(_PED, encoding="utf-8")
    with zipfile.ZipFile(raw / "acidentes_2024@20261101.zip", "w") as zf:
        zf.writestr("acidentes_rodovias_2024.csv", _ACID.replace("COL", "ABA"))
    _sidecars(raw.parent)
    return raw.parent


@pytest.fixture
def leituras(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[str]:
    """Registra toda abertura/leitura do bruto: ZIP, open, transcodificação, scan.

    Sidecars (``.manifest.json``) podem ser lidos; o resto, não.
    """
    vistas: list[str] = []
    raiz = str(tmp_path / "raw")

    def espia(nome: str, original):  # noqa: ANN001, ANN202
        def _f(*args, **kwargs):  # noqa: ANN002, ANN003
            vistas.append(nome)
            return original(*args, **kwargs)

        return _f

    original_open = builtins.open

    def open_espiado(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        texto = str(file)
        if texto.startswith(raiz) and not texto.endswith(".manifest.json"):
            vistas.append(f"open:{texto}")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espiado)
    monkeypatch.setattr(zipfile, "ZipFile", espia("zipfile", zipfile.ZipFile))
    for nome in ("_member_as_text", "_csv_member_names", "_scan_text"):
        monkeypatch.setattr(lake_mod, nome, espia(nome, getattr(lake_mod, nome)))
    monkeypatch.setattr(pl, "scan_csv", espia("scan_csv", pl.scan_csv))
    monkeypatch.setattr(
        manifests_mod, "sha256_file", espia("hash", manifests_mod.sha256_file)
    )
    return vistas


@pytest.mark.parametrize(
    ("dataset", "convertidos"),
    [("acidentes-rodovias", 4), ("volume-trafego-praca-pedagio", 1)],
)
def test_segunda_rodada_nao_le_o_bruto(
    tmp_path: Path, leituras: list[str], dataset: str, convertidos: int
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"

    r1 = converter.convert(raw, lake, datasets=[dataset])
    assert not r1.errors
    assert (r1.converted, r1.skipped) == (convertidos, 0)
    assert leituras  # a primeira rodada le o bruto

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=[dataset])
    assert (r2.converted, r2.skipped, r2.errors) == (0, convertidos, [])
    assert leituras == []


def test_um_dataset_nao_toca_o_bruto_de_outro(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["volume-trafego-praca-pedagio"])
    assert not any("acidentes-rodovias@" in v for v in leituras)


def test_todos_os_datasets_em_dia_nao_extrai_nem_le_o_csv(
    tmp_path: Path, leituras: list[str]
) -> None:
    """Sem ``datasets``, o ZIP de nome antigo (sem conjunto no nome) so tem o
    diretorio listado: nenhum membro e extraido nem varrido."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    r1 = converter.convert(raw, lake)
    assert not r1.errors
    leituras.clear()

    r2 = converter.convert(raw, lake)
    assert (r2.converted, r2.skipped, r2.errors) == (0, r1.converted, [])
    assert "_member_as_text" not in leituras
    assert "_scan_text" not in leituras
    assert "scan_csv" not in leituras
    assert not any(v.startswith("open:") and not v.endswith(".zip") for v in leituras)


def test_force_reconverte(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["acidentes-rodovias"])
    leituras.clear()

    r = converter.convert(raw, lake, datasets=["acidentes-rodovias"], force=True)
    assert (r.converted, r.skipped, r.errors) == (4, 0, [])
    assert "_member_as_text" in leituras


def test_bruto_novo_converte_e_o_antigo_segue_em_dia(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    ds = "acidentes-rodovias"
    converter.convert(raw, lake, datasets=[ds])

    novo = raw / "rodovias" / "acidentes-rodovias@20261201.csv"
    novo.write_text(_ACID + "01/02/2025;QUEDA;9\n", encoding="utf-8")
    _sidecars(raw)
    leituras.clear()

    r = converter.convert(raw, lake, datasets=[ds])
    assert not r.errors
    # A versao nova substitui a antiga (2 anos) e o ZIP segue em dia (2 anos).
    assert (r.converted, r.skipped) == (2, 2)
    abertos = [v for v in leituras if v.startswith("open:")]
    assert abertos
    assert all("@20261201" in v for v in abertos)

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=[ds])
    assert (r3.converted, r3.skipped, r3.errors) == (0, 4, [])
    assert leituras == []


def test_bruto_alterado_no_lugar_reconverte(tmp_path: Path) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    ds = "volume-trafego-praca-pedagio"
    converter.convert(raw, lake, datasets=[ds])

    (raw / "rodovias" / "volume_pedagio_2024@20261101.csv").write_text(
        _PED + "AUTOPISTA;11/2024;1\n", encoding="utf-8"
    )
    r = converter.convert(raw, lake, datasets=[ds])
    assert (r.converted, r.skipped, r.errors) == (1, 0, [])


def test_zip_ilegivel_de_outro_conjunto_nao_e_aberto(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    (raw / "rodovias" / "ciot@20261101.csv").write_bytes(b"PK\x03\x04lixo")
    r = converter.convert(raw, lake, datasets=["volume-trafego-praca-pedagio"])
    assert not r.errors
    assert not any("ciot@" in v for v in leituras)


def test_json_do_sat_segue_cobertura_e_contagem(tmp_path: Path) -> None:
    """O JSON depende dos CSV diarios (cobertura): nao e pulado pelos rodapes, mas
    a segunda rodada da as mesmas contagens, e os CSV em dia sao pulados."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-nova-rota-aaaa1111@20261102.csv"
    ).write_text(_SAT_CAB + "NOVA ROTA DO OESTE;25/03/2025;10\n", encoding="utf-8")
    (raw_dir / "volume-sat@20261103.json").write_text(
        '{"volume_sat":[{"concessionaria":"NOVA ROTA DO OESTE",'
        '"data_de_passagem":"2025-03-25","volume_total":10}]}\n'
        '{"volume_sat":[{"concessionaria":"ELOVIAS",'
        '"data_de_passagem":"2025-10-30","volume_total":7}]}\n',
        encoding="utf-8",
    )
    lake = tmp_path / "lake"
    ds = ["volume-sat"]
    r1 = converter.convert(raw_dir.parent, lake, datasets=ds)
    r2 = converter.convert(raw_dir.parent, lake, datasets=ds)
    assert not r1.errors and not r2.errors
    assert (r1.converted, r1.skipped) == (2, 0)
    assert (r2.converted, r2.skipped) == (0, 2)


def test_chave_registrada_diferente_da_atual_pede_conversao() -> None:
    """Rodape com chave que o conversor nao daria hoje (regra de chaves mudou)
    nao vale como em dia: o caminho completo decide, como antes."""
    ok = lake_mod._chaves_do_bruto
    assert ok(["acidentes", "acidentes__membro"], "acidentes")
    assert not ok(["acidentes", "acidentes_2"], "acidentes")
    assert not ok(["outra_chave"], "acidentes")
    assert not ok([None], "acidentes")
