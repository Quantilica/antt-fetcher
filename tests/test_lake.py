"""Tests for antt-fetcher lake converter."""

from __future__ import annotations

import zipfile
from pathlib import Path

import polars as pl
from quantilica.analytics.lake import check_dataset

from antt_fetcher.lake import converter


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
