"""Tests for antt-fetcher lake converter."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import polars as pl
from quantilica.analytics.lake import check_dataset

from antt_fetcher.lake import converter

_FIXTURES = Path(__file__).parent / "fixtures" / "lake"


def _raw(tmp_path: Path, group: str) -> Path:
    raw_dir = tmp_path / "raw" / group
    raw_dir.mkdir(parents=True)
    return raw_dir


def test_converter_metadata() -> None:
    """Verify converter source_id and dataset list."""
    assert converter.source_id == "antt"
    datasets = converter.datasets()
    assert "volume-trafego-praca-pedagio" in datasets
    assert "acidentes-rodovias" in datasets
    assert "rntrc" in datasets


def test_converter_empty_dir(tmp_path: Path) -> None:
    """Test convert with empty input directory."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    res = converter.convert(raw_dir, lake_dir)
    assert res.converted == 0
    assert not res.errors


def test_convert_volume_pedagio_and_acidentes(tmp_path: Path) -> None:
    """Test converting ANTT CSVs with embedded tabs in headers to Hive Lake."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    # CSV with trailing tab in header
    csv_pedagio = (
        "concessionaria;mes_ano\t;sentido;volume_total\n"
        "AUTOPISTA REGIS;10/2024;NORTE;15000\n"
    )
    (raw_dir / "volume_pedagio_2024@20261101.csv").write_text(
        csv_pedagio, encoding="latin-1"
    )

    csv_acidentes = "data;tipo_de_ocorrencia;km;mortos\n12/05/2024;COLISAO;120;0\n"
    zip_acidentes = raw_dir / "acidentes_2024@20261101.zip"
    with zipfile.ZipFile(zip_acidentes, "w") as zf:
        zf.writestr("acidentes_rodovias_2024.csv", csv_acidentes.encode("utf-8"))

    res = converter.convert(raw_dir.parent, lake_dir)
    assert res.converted == 2
    assert not res.errors

    ds_pedagio = lake_dir / "antt" / "volume-trafego-praca-pedagio"
    errors_pedagio = check_dataset(ds_pedagio)
    assert not errors_pedagio, f"check_dataset pedagio: {errors_pedagio}"
    assert (ds_pedagio / "ano=2024").is_dir()

    parquet_pedagio = list((ds_pedagio / "ano=2024").glob("*.parquet"))[0]
    df_pedagio = pl.read_parquet(parquet_pedagio)
    assert "concessionaria" in df_pedagio.columns
    assert "mes_ano" in df_pedagio.columns
    assert "\t" not in "".join(df_pedagio.columns)

    ds_acidentes = lake_dir / "antt" / "acidentes-rodovias"
    errors_acidentes = check_dataset(ds_acidentes)
    assert not errors_acidentes, f"check_dataset acidentes: {errors_acidentes}"
    assert (ds_acidentes / "ano=2024").is_dir()


def test_convert_antt_utf8_encoding(tmp_path: Path) -> None:
    """Test converting ANTT CSV encoded in UTF-8 preserves accents without mojibake."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    csv_utf8 = (
        "concessionaria;mes_ano;sentido;volume_total\n"
        "RODOVIA DOS TAMOIOS - LITORAL NORTE;10/2024;SÃO PAULO;25000\n"
    )
    (raw_dir / "volume_pedagio_2024@20261101.csv").write_text(
        csv_utf8, encoding="utf-8"
    )

    res = converter.convert(raw_dir.parent, lake_dir)
    assert res.converted == 1
    assert not res.errors

    ds = lake_dir / "antt" / "volume-trafego-praca-pedagio" / "ano=2024"
    df = pl.read_parquet(list(ds.glob("*.parquet"))[0])
    assert df["sentido"][0] == "SÃO PAULO"
    assert df["concessionaria"][0] == "RODOVIA DOS TAMOIOS - LITORAL NORTE"


def _partitions(ds_dir: Path) -> dict[str, int]:
    """Linhas por diretório de partição ``ano=...``."""
    return {
        d.name: sum(pl.read_parquet(f).height for f in d.glob("*.parquet"))
        for d in sorted(ds_dir.glob("ano=*"))
    }


def test_multi_year_csv_is_split_per_row(tmp_path: Path) -> None:
    """Regressão A4: CSV multi-ano ia inteiro para a partição da 1ª linha."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    csv = (
        "data;tipo_de_ocorrencia;km\n"
        "12/05/2019;COLISAO;1\n03/01/2020;TOMBAMENTO;2\n"
        "30/12/2020;COLISAO;3\n01/02/2021;INCENDIO;4\n"
    )
    (raw_dir / "acidentes_rodovias@20261101.csv").write_text(csv, "utf-8")

    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    assert res.converted == 3
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert not check_dataset(ds)
    assert _partitions(ds) == {"ano=2019": 1, "ano=2020": 2, "ano=2021": 1}


def test_row_without_valid_year_goes_to_quarantine(tmp_path: Path, caplog) -> None:
    """Sem fallback silencioso 2024: linha sem ano vai para a quarentena."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    csv = "data;km\n12/05/2019;1\n;2\nlixo;3\n"
    (raw_dir / "acidentes_rodovias@20261101.csv").write_text(csv, "utf-8")

    with caplog.at_level("WARNING"):
        res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    parts = _partitions(tmp_path / "lake" / "antt" / "acidentes-rodovias")
    assert parts["ano=2019"] == 1
    assert parts["ano=__HIVE_DEFAULT_PARTITION__"] == 2
    assert "2 linha(s) sem ano valido" in caplog.text


def test_no_year_anywhere_is_an_error_not_2024(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    (raw_dir / "acidentes_rodovias@20261101.csv").write_text(
        "tipo;km\nCOLISAO;1\n", "utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert res.converted == 0
    assert len(res.errors) == 1
    assert not list((tmp_path / "lake").rglob("ano=*"))


def test_rntrc_snapshot_partitions_by_declared_period(tmp_path: Path) -> None:
    """RNTRC é retrato mensal: o ano vem do nome, não da data de cadastro."""
    raw_dir = tmp_path / "raw" / "cargas"
    raw_dir.mkdir(parents=True)
    csv = "nome_transportador;data;cep\nA;15/03/1998;01000\nB;02/07/2011;02000\n"
    (raw_dir / "transportadores_rntrc_12_2024@20261101.csv").write_text(csv, "utf-8")

    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "rntrc") == {"ano=2024": 2}


def test_zip_with_multiple_members_writes_all(tmp_path: Path) -> None:
    """Cada membro do ZIP é origem própria (o sha256 do ZIP é o mesmo)."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    with zipfile.ZipFile(raw_dir / "acidentes@20261101.zip", "w") as zf:
        zf.writestr(
            "acidentes_rodovias_2022.csv", "data;km\n01/01/2022;1\n01/02/2022;2\n"
        )
        zf.writestr("acidentes_rodovias_2023.csv", "data;km\n01/01/2023;3\n")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _partitions(ds) == {"ano=2022": 2, "ano=2023": 1}


def test_latin1_decodes_and_reconversion_is_idempotent(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    (raw_dir / "acidentes_rodovias@20261101.csv").write_bytes(
        "data;local\n01/01/2020;SÃO JOSÉ\n01/01/2021;AÇAÍ\n".encode("latin-1")
    )
    converter.convert(raw_dir.parent, tmp_path / "lake")
    p = tmp_path / "lake" / "antt" / "acidentes-rodovias" / "ano=2020"
    assert pl.read_parquet(next(p.glob("*.parquet")))["local"][0] == "SÃO JOSÉ"
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert res.converted == 0
    assert res.skipped == 2


# --- Falhas reais do build do lake (nov/2026) -------------------------------
def _write_manifest(raw: Path, url: str) -> None:
    import json

    Path(str(raw) + ".manifest.json").write_text(
        json.dumps({"url": url}), encoding="utf-8"
    )


def test_monitriip_particiona_por_data_parada(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "passageiros"
    raw_dir.mkdir(parents=True)
    (raw_dir / "monitriip-servico-regular-paradas@20210105.csv").write_text(
        "codigo_viagem;data_parada;data_viagem_progamada\n"
        "1;01-12-2019 07:20:53;2019-12-01\n"
        "2;02-01-2020 08:00:00;2019-12-31\n",
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "monitriip-servico-regular-paradas"
    assert _partitions(ds) == {"ano=2019": 1, "ano=2020": 1}


def test_rntrc_snapshot_usa_periodo_do_nome_original_no_manifest(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw" / "cargas"
    raw_dir.mkdir(parents=True)
    raw = raw_dir / "rntrc@20201101.csv"
    raw.write_text("rntrc;cadastro\n1;01/01/1999\n2;05/05/2010\n", encoding="utf-8")
    _write_manifest(raw, "https://x/download/transportadores_rntrc_10_2020.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "rntrc") == {"ano=2020": 2}


def test_rntrc_sem_manifesto_particiona_pelo_ano_do_carimbo(
    tmp_path: Path, caplog
) -> None:
    """Sem periodo no nome (manifesto ausente, como no Drive), a fotografia
    cai no ano do carimbo @AAAAMMDD, sem descartar linhas, e avisa no log."""
    raw_dir = _raw(tmp_path, "cargas")
    shutil.copy(_FIXTURES / "rntrc.csv", raw_dir / "rntrc@20261010.csv")
    with caplog.at_level("WARNING"):
        res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "rntrc"
    assert _partitions(ds) == {"ano=2026": 2}
    assert "ano do carimbo (2026)" in caplog.text
    assert not check_dataset(ds)


def test_rntrc_manifesto_com_periodo_vence_o_carimbo(tmp_path: Path) -> None:
    """O periodo do nome original (09_2026) manda; o carimbo e so o ultimo recurso."""
    raw_dir = _raw(tmp_path, "cargas")
    raw = raw_dir / "rntrc@20210101.csv"
    shutil.copy(_FIXTURES / "rntrc.csv", raw)
    _write_manifest(raw, "https://x/download/transportadores_rntrc_12_2020.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "rntrc") == {"ano=2020": 2}


def test_conjuntos_sem_conversor_nao_caem_em_volume_pedagio(tmp_path: Path) -> None:
    """Slugs catalogados fora do lake (vale-pedagio, praca-de-pedagio, radar...)
    são ignorados, não classificados por substring como volume de praça."""
    raw_dir = tmp_path / "raw" / "x"
    raw_dir.mkdir(parents=True)
    for slug in (
        "volume-radar",
        "volume-sat",
        "volume-trafego-equivalente-praca-pedagio",
        "receita-por-praca",
        "acidentes-quilometro-rodovias",
        "rntrc-veiculos",
    ):
        (raw_dir / f"{slug}@20261101.csv").write_text("a;b\n1;2\n", encoding="utf-8")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert res.converted == 0
    assert not list((tmp_path / "lake").rglob("*.parquet"))


def test_acidentes_concessionaria_com_coluna_de_data_diferente(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    (raw_dir / "acidentes-rodovias@20261028.csv").write_text(
        "data_do_acidente;km\n11/11/2013;1\n02/03/2014;2\n", encoding="utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _partitions(ds) == {"ano=2013": 1, "ano=2014": 1}


def test_cp1252_com_bytes_indefinidos_nao_quebra(tmp_path: Path) -> None:
    """Bytes 0x8d/0x90 (indefinidos no cp1252) não derrubam a conversão."""
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    (raw_dir / "acidentes-rodovias@20261028.csv").write_bytes(
        b"data;local\n01/01/2020;S\xc3O \x8d\n01/01/2020;A\x90\n"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _partitions(ds) == {"ano=2020": 2}


# --- inventory() -------------------------------------------------------------
def test_inventory_classifica_arquivos(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "cargas")
    (raw_dir / "rntrc@20260901.csv").write_text("a\n1\n", encoding="utf-8")
    (raw_dir / "rntrc@20261001.csv").write_text("a\n1\n", encoding="utf-8")
    (raw_dir / "rntrc@20261001.csv.manifest.json").write_text("{}", encoding="utf-8")
    (raw_dir / "dicionario@20261001.pdf").write_bytes(b"%PDF")
    (raw_dir / "receita-por-praca@20261001.csv").write_text("a\n1\n", "utf-8")

    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert "rntrc@20261001.csv.manifest.json" not in plan
    assert plan["rntrc@20260901.csv"].skip_reason == "superado"
    assert plan["rntrc@20261001.csv"].dataset == "rntrc"
    assert plan["rntrc@20261001.csv"].skip_reason is None
    assert plan["dicionario@20261001.pdf"].skip_reason == "nao_tabular"
    # Sem conversor: lacuna de cobertura, nao exclusao deliberada.
    assert plan["receita-por-praca@20261001.csv"].dataset is None
    assert plan["receita-por-praca@20261001.csv"].skip_reason is None


def test_inventory_zip_e_diretorio_inexistente(tmp_path: Path) -> None:
    assert converter.inventory(tmp_path / "nao-existe") == []
    raw_dir = _raw(tmp_path, "rodovias")
    with zipfile.ZipFile(raw_dir / "acidentes_2024@20261101.zip", "w") as zf:
        zf.writestr("acidentes_rodovias_2024.csv", "data\n01/01/2024\n")
    (raw_dir / "quebrado@20261101.zip").write_bytes(b"PK\x03\x04lixo")
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["acidentes_2024@20261101.zip"].dataset == "acidentes-rodovias"
    assert plan["quebrado@20261101.zip"].dataset is None


# --- ciot -------------------------------------------------------------------
def test_ciot_particiona_pelo_periodo_do_nome_original(tmp_path: Path) -> None:
    """CIOT e agregado mensal por origem/destino, sem data: o ano vem do periodo
    do nome original (09_2026_ciots.csv) e o texto cp1252 e preservado."""
    raw_dir = _raw(tmp_path, "cargas")
    raw = raw_dir / "ciot@20261010.csv"
    shutil.copy(_FIXTURES / "ciot.csv", raw)
    _write_manifest(raw, "https://x/download/09_2026_ciots.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "ciot"
    assert _partitions(ds) == {"ano=2026": 4}
    assert not check_dataset(ds)
    df = pl.read_parquet(next(ds.rglob("*.parquet")))
    assert df.columns[:3] == ["municipio_origem", "uf_origem", "municipio_destino"]
    assert "Paulínia" in df["municipio_destino"].to_list()
    assert df.schema["quantidade_ciots"] == pl.String


def test_ciot_sem_manifesto_usa_o_carimbo_e_inventory_o_lista(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "cargas")
    shutil.copy(_FIXTURES / "ciot.csv", raw_dir / "ciot@20261010.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "ciot") == {"ano=2026": 4}
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "ciot"


# --- vale-pedagio-obrigatorio ----------------------------------------------
def test_vale_pedagio_particiona_por_ano_de_emissao(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "cargas")
    shutil.copy(
        _FIXTURES / "vale-pedagio-obrigatorio.csv",
        raw_dir / "vale-pedagio-obrigatorio@20261006.csv",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "vale-pedagio-obrigatorio"
    assert _partitions(ds) == {"ano=2025": 3, "ano=2026": 1}
    assert not check_dataset(ds)
    df = pl.read_parquet(next((ds / "ano=2025").glob("*.parquet")))
    assert "mes_de_emissao" in df.columns
    assert df["valor_dos_vpos"].to_list()[0] == "2083658.08"
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "vale-pedagio-obrigatorio"


# --- investimentos ----------------------------------------------------------
def test_investimentos_particiona_pela_coluna_ano(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(_FIXTURES / "investimentos.csv", raw_dir / "investimentos@20260522.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "investimentos"
    assert _partitions(ds) == {"ano=2010": 3, "ano=2025": 1}
    assert not check_dataset(ds)
    df = pl.read_parquet(next((ds / "ano=2010").glob("*.parquet")))
    assert {"concessionaria", "valor"} <= set(df.columns)
    assert "AUTOPISTA FERNÃO DIAS" in df["concessionaria"].to_list()
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "investimentos"


# --- praca-de-pedagio -------------------------------------------------------
def test_praca_de_pedagio_cadastro_particiona_pelo_carimbo(tmp_path: Path) -> None:
    """Cadastro de pracas: ano_do_pnv_snv (2019) e versao do mapa, nao o ano do
    registro; o ano e o da fotografia (carimbo), sem descartar linhas."""
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(
        _FIXTURES / "praca-de-pedagio.csv", raw_dir / "praca-de-pedagio@20261103.csv"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "praca-de-pedagio"
    assert _partitions(ds) == {"ano=2026": 3}
    assert not check_dataset(ds)
    df = pl.read_parquet(next(ds.rglob("*.parquet")))
    assert df["ano_do_pnv_snv"].to_list() == ["2019"] * 3
    assert df["latitude"].to_list()[0] == "-21.552594"
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "praca-de-pedagio"
