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


def test_rntrc_sem_manifesto_da_erro_explicito(tmp_path: Path) -> None:
    """Sem manifesto (periodo do nome original), nao ha ano inventado nem
    fallback no carimbo: erro dizendo que o manifesto precisa estar ao lado."""
    raw_dir = _raw(tmp_path, "cargas")
    shutil.copy(_FIXTURES / "rntrc.csv", raw_dir / "rntrc@20261010.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1
    assert "particao por ano indeterminada" in res.errors[0]
    assert "manifesto" in res.errors[0] and "ao lado do arquivo" in res.errors[0]
    assert not list((tmp_path / "lake").rglob("*.parquet"))


def test_rntrc_manifesto_com_periodo_define_o_ano(tmp_path: Path) -> None:
    """O periodo do nome original (12_2020) manda, mesmo com carimbo de 2021."""
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


def test_ciot_sem_manifesto_da_erro_e_inventory_o_lista(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "cargas")
    shutil.copy(_FIXTURES / "ciot.csv", raw_dir / "ciot@20261010.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1
    assert "ao lado do arquivo" in res.errors[0]
    assert not list((tmp_path / "lake").rglob("*.parquet"))
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


# --- quantidade-possiveis-infratores ---------------------------------------
def test_possiveis_infratores_particiona_por_data_da_passagem(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    raw = raw_dir / "quantidade-possiveis-infratores@20261028.csv"
    shutil.copy(_FIXTURES / "quantidade-possiveis-infratores.csv", raw)
    # Uma passagem de dez/2025 junto das de jan/2026: cada linha no seu ano.
    with open(raw, "ab") as fh:
        fh.write(
            b'"VIA CRISTAIS";"D0880";"BR-40";"MG";462.950;"Sete Lagoas";"Principal";'
            b'-19.420795;-44.339028;"31/12/2025";"Crescente";1;"101 - 120 ";'
            b'"Comercial";2\r\n'
        )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "quantidade-possiveis-infratores"
    assert _partitions(ds) == {"ano=2025": 1, "ano=2026": 3}
    assert not check_dataset(ds)
    df = pl.read_parquet(next((ds / "ano=2026").glob("*.parquet")))
    assert "Veículo Médio" in df["tipo_de_veiculo"].to_list()
    assert df["velocidade"].to_list()[0] == "101 - 120 "
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "quantidade-possiveis-infratores"


# --- volume-radar -----------------------------------------------------------
def test_volume_radar_particiona_por_data_da_passagem(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    raw = raw_dir / "volume-radar@20260928.csv"
    shutil.copy(_FIXTURES / "volume-radar.csv", raw)
    with open(raw, "ab") as fh:  # mesmo conjunto, passagem de outro ano
        fh.write(
            b'"ECOVIAS DO ARAGUAIA";"X";"BR-80";"GO";94.500;"Vila";"Principal";'
            b'-15.2;-48.7;"31/12/2025";"Crescente/Decrescente";1;"21 - 50 KM";'
            b'"Carro";5\r\n'
        )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-radar"
    assert _partitions(ds) == {"ano=2024": 3, "ano=2025": 1}
    assert not check_dataset(ds)
    df = pl.read_parquet(next((ds / "ano=2024").glob("*.parquet")))
    assert "Vila Propício" in df["municipio"].to_list()
    assert "Ônibus" in df["tipo_de_veiculo"].to_list()
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "volume-radar"


def test_volume_radar_mes_ano_extrai_o_ano(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-radar@20260928.csv").write_text(
        "concessionaria;mes_ano;volume_total\nA;02/2025;15\nA;09/2025;423\n",
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "volume-radar") == {"ano=2025": 2}


def test_volume_radar_sem_cabecalho_da_erro_em_vez_de_inventar_ano(
    tmp_path: Path,
) -> None:
    """Copia truncada, sem a linha de cabecalho: a 1a linha de dados viraria o
    cabecalho. Sem coluna de data nao ha ano e o evento nao cai no carimbo."""
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-radar@20260928.csv").write_text(
        '"AUTOPISTA LITORAL SUL";"ALS090";"BR-101";"SC";"Sao Jose";"Principal";15\n'
        '"AUTOPISTA LITORAL SUL";"ALS138";"BR-376";"PR";"Guaratuba";"Principal";423\n',
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1
    assert "particao por ano indeterminada" in res.errors[0]
    assert not list((tmp_path / "lake").rglob("*.parquet"))


# --- volume-sat (JSON e CSV gemeo) -----------------------------------------
def test_volume_sat_json_multidocumento_particiona_por_ano(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(_FIXTURES / "volume-sat.json", raw_dir / "volume-sat@20261103.json")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert _partitions(ds) == {"ano=2024": 1, "ano=2025": 2, "ano=2026": 2}
    assert not check_dataset(ds)
    df = pl.read_parquet(next((ds / "ano=2025").glob("*.parquet")))
    assert df.schema["volume_total"] == pl.String  # tudo texto, como no CSV
    assert "ELOVIAS" in df["concessionaria"].to_list()
    assert "Duque de Caxias" in df["municipio"].to_list()
    # Reconversao idempotente.
    again = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert again.converted == 0 and again.skipped == 3


_SAT_CAB = "concessionaria;data_de_passagem;volume_total\n"


def _sat_json(*docs: tuple[str, list[tuple[str, int]]]) -> str:
    """JSON do SAT: um documento ``{"volume_sat":[...]}`` por concessionaria, um
    registro por linha."""
    out = []
    for nome, registros in docs:
        linhas = [
            f'{{"concessionaria":"{nome}","data_de_passagem":"{d}","volume_total":{v}}}'
            for d, v in registros
        ]
        out.append('{"volume_sat":[' + ",\n".join(linhas) + "]}")
    return "\n".join(out) + "\n"


def test_volume_sat_json_nao_repete_concessionaria_com_csv_diario(
    tmp_path: Path,
) -> None:
    """O JSON junta concessionarias que tambem tem CSV diario (com outro nome de
    recurso e outro carimbo): o CSV manda e o JSON so traz as que nao tem CSV."""
    raw_dir = _raw(tmp_path, "rodovias")
    (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-nova-rota-aaaa1111@20261102.csv"
    ).write_text(
        _SAT_CAB
        + "NOVA ROTA DO OESTE;25/03/2025;10\nNOVA ROTA DO OESTE;26/03/2025;20\n",
        encoding="utf-8",
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(
            ("NOVA ROTA DO OESTE", [("2025-03-25", 10), ("2025-03-26", 20)]),
            ("ELOVIAS", [("2025-10-30", 7)]),
        ),
        encoding="utf-8",
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason is None
    assert all(p.skip_reason is None for p in plan.values())
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    df = pl.concat([pl.read_parquet(f) for f in ds.rglob("*.parquet")], how="diagonal")
    contagem = dict(df.group_by("concessionaria").agg(pl.len()).iter_rows())
    assert contagem == {"NOVA ROTA DO OESTE": 2, "ELOVIAS": 1}


def test_volume_sat_json_todo_coberto_por_csv_e_gemeo(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    csv = raw_dir / "volume-sat_trafego-de-veiculos-sat-motiva-bbbb2222@20260628.csv"
    csv.write_text(
        _SAT_CAB + "MOTIVA MINAS SP;01/01/2024;5\nMOTIVA MINAS SP;02/01/2024;6\n",
        encoding="utf-8",
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("MOTIVA MINAS SP", [("2024-01-01", 5), ("2024-01-02", 6)])),
        encoding="utf-8",
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason == "gemeo"
    assert plan[csv.name].skip_reason is None
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert _partitions(ds) == {"ano=2024": 2}
    assert len(_parquets(ds)) == 1  # so o do CSV


def test_volume_sat_csv_mensal_nao_cobre_o_json_diario(tmp_path: Path) -> None:
    """Concessionaria so com CSV mensal consolidado: o JSON e a unica fonte
    diaria dela e entra (a granularidade separa os dois)."""
    raw_dir = _raw(tmp_path, "rodovias")
    (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-mensal-cccc3333@20261103.csv"
    ).write_text(_SAT_CAB + "ELOVIAS;10/2025;7\n", encoding="utf-8")
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("ELOVIAS", [("2025-10-30", 7)])), encoding="utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert _granularidades(ds) == {"dia": 1, "mes": 1}


def test_volume_sat_nome_com_acento_e_comparado_normalizado(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-goias-dddd4444@20261103.csv"
    ).write_bytes(
        (_SAT_CAB + "ECOVIAS MINAS GOI\xc1S;10/08/2022;3\n").encode("latin-1")
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("ECOVIAS MINAS GOIÁS", [("2022-08-10", 3)])), encoding="utf-8"
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason == "gemeo"


def test_volume_sat_ignora_o_manifesto_ao_lado(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(_FIXTURES / "volume-sat.csv", raw_dir / "volume-sat@20261103.csv")
    (raw_dir / "volume-sat@20261103.csv.manifest.json").write_text(
        '{"url": "https://x.invalid/volume-sat.csv", "sha256": "0"}',
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "volume-sat") == {"ano=2025": 3}


def test_volume_sat_csv_sozinho_converte_por_data_de_passagem(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(_FIXTURES / "volume-sat.csv", raw_dir / "volume-sat@20261103.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert _partitions(ds) == {"ano=2025": 3}
    (plan,) = converter.inventory(raw_dir.parent)
    assert plan.dataset == "volume-sat" and plan.skip_reason is None


def test_volume_sat_json_fora_do_formato_da_erro(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-sat@20261103.json").write_text(
        '{"volume_sat":[{"data_de_passagem":"2025-01-01"},\nlixo\n]}\n',
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1
    assert "um registro por linha" in res.errors[0]
    assert not list((tmp_path / "lake").rglob("*.parquet"))


# --- conjunto pelo prefixo do slug -----------------------------------------
def test_conjunto_reconhecido_com_e_sem_identificador_de_recurso() -> None:
    from antt_fetcher.lake import _detect_dataset_id, _slug_of

    assert _detect_dataset_id("ciot@20261010.csv") == "ciot"
    assert _detect_dataset_id("ciot_09-2026-ciots-1a2b3c4d@20261010.csv") == "ciot"
    assert (
        _detect_dataset_id("volume-radar_radar-x-1a2b3c4d@20260928.csv")
        == "volume-radar"
    )
    assert _detect_dataset_id("receita-por-praca_x-1a2b3c4d@20260928.csv") is None
    assert _slug_of("volume-radar_radar-x-1a2b3c4d@20260928.csv") == "volume-radar"
    assert _slug_of("rntrc_2024@20261010.csv") == "rntrc"
    assert _slug_of("volume-radar@20260928.csv") == "volume-radar"
    # maior prefixo: nao confunde com outro conjunto de prefixo comum
    assert (
        _slug_of("volume-trafego-equivalente-praca-pedagio_a-12345678@20260928.csv")
        == "volume-trafego-equivalente-praca-pedagio"
    )
    # sem slug conhecido, segue o comportamento antigo
    assert _slug_of("qualquer@20260101.csv") == "qualquer"
    assert _slug_of("sem-carimbo.csv") == ""
    # equivalente-praca-pedagio nao cai na heuristica de "volume"/"pedagio"
    assert (
        _detect_dataset_id(
            "volume-trafego-equivalente-praca-pedagio_a-12345678@20260928.csv"
        )
        is None
    )


def test_ciot_com_identificador_converte_e_recursos_nao_colidem(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "cargas")
    a = raw_dir / "ciot_09-2026-ciots-aaaa1111@20261010.csv"
    b = raw_dir / "ciot_08-2026-ciots-bbbb2222@20261010.csv"
    shutil.copy(_FIXTURES / "ciot.csv", a)
    shutil.copy(_FIXTURES / "ciot.csv", b)
    plans = converter.inventory(raw_dir.parent)
    assert {p.dataset for p in plans} == {"ciot"}
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "antt" / "ciot") == {"ano=2026": 8}


def test_equivalente_praca_pedagio_com_identificador_e_ignorado(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(
        _FIXTURES / "ciot.csv",
        raw_dir / "volume-trafego-equivalente-praca-pedagio_a-12345678@20260928.csv",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert not (tmp_path / "lake" / "antt" / "volume-trafego-praca-pedagio").exists()


def test_rntrc_sem_aspas_com_aspa_solta_nao_engole_linhas(tmp_path: Path) -> None:
    """rntrc antigo: campos sem aspas e `D"AVILA` no nome (aspa no lugar do
    apostrofo). Lido com aspas, o campo abria e engolia as linhas seguintes."""
    raw_dir = _raw(tmp_path, "cargas")
    raw = raw_dir / "rntrc@20210501.csv"
    linhas = [
        "nome_transportador;numero_rntrc;data_primeiro_cadastro;situacao_rntrc",
        'JOSE CLOVIS D"AVILA ISER;008731039;06/10/2006;ATIVO',
        "TRANSPORTADORA EXEMPLO;000000002;07/12/2022;ATIVO",
        'MARCO AURELIO SANT"ANA;012726016;06/08/2010;ATIVO',
        "OUTRA EXEMPLO;000000004;01/01/2015;ATIVO",
    ]
    raw.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    _write_manifest(raw, "https://x/download/transportadores_rntrc_04_2021.csv")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "rntrc"
    assert _partitions(ds) == {"ano=2021": 4}
    df = pl.read_parquet(next((ds / "ano=2021").glob("*.parquet")))
    assert 'JOSE CLOVIS D"AVILA ISER' in df["nome_transportador"].to_list()


def test_csv_com_aspas_e_aspa_interna_sem_escape_e_reparado(tmp_path: Path) -> None:
    """acidentes-rodovias (autopista, out/2026): campos entre aspas e uma linha
    com `"barreira ou "submarino";`, que o leitor rejeitava (CSV malformed)."""
    raw_dir = _raw(tmp_path, "rodovias")
    raw = raw_dir / "acidentes-rodovias@20261028.csv"
    linhas = [
        "data;horario;tipo_de_acidente;mortos",
        '"01/01/2023";"00:05:00";"Saida de Pista";0',
        '"02/09/2023";"18:40:00";"Choque - Defensa, barreira ou "submarino";0',
        '"03/09/2023";"10:00:00";"Ja ""escapada"" certa";1',
        '"04/09/2023";"11:00:00";"campo com\nquebra de linha";0',
    ]
    raw.write_text("\r\n".join(linhas) + "\r\n", encoding="utf-8")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    df = pl.read_parquet(next((ds / "ano=2023").glob("*.parquet")))
    tipos = df["tipo_de_acidente"].to_list()
    assert len(tipos) == 4
    assert 'Choque - Defensa, barreira ou "submarino' in tipos
    assert 'Ja "escapada" certa' in tipos
    assert "campo com\nquebra de linha" in tipos


def test_volume_radar_sem_cabecalho_usa_o_cabecalho_do_conjunto(
    tmp_path: Path,
) -> None:
    """Arquivo de concessionaria publicado sem a linha de cabecalho."""
    raw_dir = _raw(tmp_path, "rodovias")
    raw = raw_dir / "volume-radar_trafego-autopista-dea1a5ed@20260428.csv"
    raw.write_bytes(
        b'"AUTOPISTA";"ARAFD6094";"BR-381";"MG";493.290;"Betim";"Principal";'
        b'-19.96;-44.17;"01/2022";"Crescente";1;"101 - 120 ";"Moto";650\r\n'
        b'"AUTOPISTA";"ARAFD6102";"BR-381";"MG";886.250;"Estiva";"Principal";'
        b'-22.51;-46.01;"05/2024";"Decrescente";2;"21 - 50 KM";"Carro";16911\r\n'
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-radar"
    assert _partitions(ds) == {"ano=2022": 1, "ano=2024": 1}
    df = pl.read_parquet(next((ds / "ano=2022").glob("*.parquet")))
    assert df["concessionaria"].to_list() == ["AUTOPISTA"]
    assert df["volume_total"].to_list() == ["650"]


# --- identidade por recurso (URL do manifesto) -------------------------------
_RES = "https://dados.antt.gov.br/dataset/pkg/resource/{rid}/download/{nome}"
_RID_A = "aaaa1111-0000-4000-8000-000000000001"
_RID_B = "bbbb2222-0000-4000-8000-000000000002"
_RID_C = "cccc3333-0000-4000-8000-000000000003"


def _raw_com_manifesto(
    raw_dir: Path, name: str, rid: str, nome_fonte: str, linhas: str, sha: str = ""
) -> Path:
    """Arquivo bruto sintético com o manifesto do recurso ``rid`` ao lado."""
    import json

    raw = raw_dir / name
    raw.write_text("data;km\n" + linhas, encoding="utf-8")
    Path(str(raw) + ".manifest.json").write_text(
        json.dumps({"url": _RES.format(rid=rid, nome=nome_fonte), "sha256": sha}),
        encoding="utf-8",
    )
    return raw


def _parquets(ds: Path) -> list[str]:
    return sorted(p.name for p in ds.rglob("*.parquet"))


def test_nome_nu_de_recursos_diferentes_nao_se_sobrepoe(tmp_path: Path) -> None:
    """Versoes antigas do fetcher davam o nome nu a recursos diferentes; cada
    recurso (URL do manifesto) e um arquivo vigente, nao so o mais recente."""
    raw_dir = _raw(tmp_path, "rodovias")
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20251128.csv", _RID_A, "eco101.csv",
        "01/01/2024;1\n01/02/2024;2\n",
    )  # fmt: skip
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20260628.csv", _RID_B, "viamineira.csv",
        "01/01/2025;3\n",
    )  # fmt: skip
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert {p.skip_reason for p in plan.values()} == {None}
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _partitions(ds) == {"ano=2024": 2, "ano=2025": 1}
    assert not check_dataset(ds)


def test_versoes_do_mesmo_recurso_se_substituem(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20251128.csv", _RID_A, "eco101.csv",
        "01/01/2024;1\n",
    )  # fmt: skip
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20260628.csv", _RID_A, "eco101.csv",
        "01/01/2024;1\n01/02/2024;2\n",
    )  # fmt: skip
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["acidentes-rodovias@20251128.csv"].skip_reason == "superado"
    assert plan["acidentes-rodovias@20260628.csv"].skip_reason is None
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _partitions(ds) == {"ano=2024": 2}


def test_chave_do_parquet_vem_do_recurso_e_a_reconversao_e_idempotente(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20251128.csv", _RID_A, "eco101.csv",
        "01/01/2024;1\n",
    )  # fmt: skip
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20260628.csv", _RID_B, "viamineira.csv",
        "01/01/2024;2\n",
    )  # fmt: skip
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _parquets(ds) == [
        "acidentes-rodovias_aaaa1111.parquet",
        "acidentes-rodovias_bbbb2222.parquet",
    ]
    again = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert again.converted == 0 and again.skipped == 2
    # A versao nova do mesmo recurso reaproveita a chave (sem Parquet orfao).
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20260928.csv", _RID_A, "eco101.csv",
        "01/01/2024;1\n01/03/2024;5\n",
    )  # fmt: skip
    converter.convert(raw_dir.parent, tmp_path / "lake")
    assert _parquets(ds) == [
        "acidentes-rodovias_aaaa1111.parquet",
        "acidentes-rodovias_bbbb2222.parquet",
    ]
    assert _partitions(ds) == {"ano=2024": 3}


def test_mesmo_recurso_sob_dois_nomes_entra_uma_vez(tmp_path: Path) -> None:
    """O nome nu e o nome com chave de recurso, com o mesmo URL e hash, sao o
    mesmo conteudo: nunca entram os dois, e a chave e a do nome com chave."""
    raw_dir = _raw(tmp_path, "rodovias")
    linhas = "01/01/2024;1\n01/02/2024;2\n"
    _raw_com_manifesto(
        raw_dir, "quantidade-possiveis-infratores@20260828.csv", _RID_A, "af.csv",
        linhas, sha="ab" * 32,
    )  # fmt: skip
    _raw_com_manifesto(
        raw_dir,
        "quantidade-possiveis-infratores_quantidade-de-possiveis-aaaa1111@20260828.csv",
        _RID_A, "af.csv", linhas, sha="ab" * 32,
    )  # fmt: skip
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["quantidade-possiveis-infratores@20260828.csv"].skip_reason == "gemeo"
    assert sum(p.skip_reason is None for p in plan.values()) == 1
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "quantidade-possiveis-infratores"
    assert _partitions(ds) == {"ano=2024": 2}
    assert _parquets(ds) == ["quantidade-possiveis-infratores_aaaa1111.parquet"]


def test_chave_do_parquet_nao_muda_quando_o_recurso_ganha_nome_com_chave(
    tmp_path: Path,
) -> None:
    """Um recurso que so existia com nome nu e depois chega com nome com chave
    continua no mesmo Parquet (a chave vem so do recurso, nao do nome)."""
    raw_dir = _raw(tmp_path, "rodovias")
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20250101.csv", _RID_A, "way153.csv",
        "01/01/2024;1\n",
    )  # fmt: skip
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _parquets(ds) == ["acidentes-rodovias_aaaa1111.parquet"]
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias_way-153-aaaa1111@20250201.csv", _RID_A,
        "way153.csv", "01/01/2024;1\n01/02/2024;2\n",
    )  # fmt: skip
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _parquets(ds) == ["acidentes-rodovias_aaaa1111.parquet"]
    assert _partitions(ds) == {"ano=2024": 2}  # sem linhas em dobro


def test_nome_nu_mais_novo_mantem_a_chave_do_recurso(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    _raw_com_manifesto(
        raw_dir, "volume-radar_radar-x-aaaa1111@20260728.csv", _RID_A, "x.csv",
        "01/01/2024;1\n",
    )  # fmt: skip
    converter.convert(raw_dir.parent, tmp_path / "lake")
    _raw_com_manifesto(
        raw_dir, "volume-radar@20260928.csv", _RID_A, "x.csv",
        "01/01/2024;1\n01/02/2024;2\n",
    )  # fmt: skip
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "volume-radar"
    assert _parquets(ds) == ["volume-radar_aaaa1111.parquet"]
    assert _partitions(ds) == {"ano=2024": 2}


def test_colisao_de_id8_no_conjunto_e_erro_explicito(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias@20250101.csv", _RID_A, "a.csv", "01/01/2024;1\n"
    )
    outro = "aaaa1111-ffff-4fff-8fff-ffffffffffff"  # mesmos 8 primeiros caracteres
    _raw_com_manifesto(
        raw_dir, "acidentes-rodovias_b-aaaa1111@20250201.csv", outro, "b.csv",
        "01/01/2024;2\n",
    )  # fmt: skip
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1 and "colisao" in res.errors[0]
    assert not list((tmp_path / "lake").rglob("*.parquet"))


def test_url_sem_id_de_recurso_e_normalizada_antes_do_hash(tmp_path: Path) -> None:
    import json

    raw_dir = _raw(tmp_path, "rodovias")
    for nome, url in (
        ("acidentes-rodovias@20250101.csv", "https://Dados.ANTT.gov.br/x/a.csv?v=1"),
        ("acidentes-rodovias@20250201.csv", "https://dados.antt.gov.br/x/a.csv/"),
    ):
        (raw_dir / nome).write_text("data;km\n01/01/2024;1\n", encoding="utf-8")
        Path(str(raw_dir / nome) + ".manifest.json").write_text(
            json.dumps({"url": url}), encoding="utf-8"
        )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["acidentes-rodovias@20250101.csv"].skip_reason == "superado"
    assert plan["acidentes-rodovias@20250201.csv"].skip_reason is None


def test_arquivos_sem_manifesto_seguem_a_regra_do_nome(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "acidentes-rodovias@20251128.csv").write_text(
        "data;km\n01/01/2024;1\n", encoding="utf-8"
    )
    (raw_dir / "acidentes-rodovias@20260628.csv").write_text(
        "data;km\n01/01/2025;2\n", encoding="utf-8"
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["acidentes-rodovias@20251128.csv"].skip_reason == "superado"
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "acidentes-rodovias"
    assert _parquets(ds) == ["acidentes-rodovias.parquet"]
    assert _partitions(ds) == {"ano=2025": 1}


def test_mesmo_conteudo_sob_dois_nomes_sem_manifesto_entra_uma_vez(
    tmp_path: Path,
) -> None:
    """Sem manifesto nao ha URL; o mesmo carimbo e o mesmo conteudo bastam para
    nao ler duas vezes (nome nu e nome com chave de recurso)."""
    raw_dir = _raw(tmp_path, "rodovias")
    conteudo = "data;km\n01/01/2024;1\n01/02/2024;2\n"
    nu = raw_dir / "volume-sat@20261103.csv"
    com_chave = (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-via040-061f7512@20261103.csv"
    )
    for f in (nu, com_chave):
        f.write_text(conteudo, encoding="utf-8")
    outro = raw_dir / "volume-sat_trafego-de-veiculos-sat-viasul-2178030c@20261103.csv"
    outro.write_text("data;km\n01/01/2024;9\n", encoding="utf-8")
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan[nu.name].skip_reason == "gemeo"
    assert plan[com_chave.name].skip_reason is None
    assert plan[outro.name].skip_reason is None
    converter.convert(raw_dir.parent, tmp_path / "lake")
    assert _partitions(tmp_path / "lake" / "antt" / "volume-sat") == {"ano=2024": 3}


# --- RAAF: slug do pacote x id do conjunto -----------------------------------
_RAAF = "relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf"


def test_raaf_slug_do_pacote_alimenta_o_conjunto_do_lake(tmp_path: Path) -> None:
    from antt_fetcher.lake import _detect_dataset_id

    ds_id = "relatorio-acompanhamento-acidentes-ferroviarios-raaf"
    assert ds_id in converter.datasets()
    assert _detect_dataset_id(f"{_RAAF}@20260410.csv") == ds_id
    assert (
        _detect_dataset_id(f"{_RAAF}_acidentes-dezembro-b3851bf8@20260410.csv") == ds_id
    )

    raw_dir = _raw(tmp_path, "ferrovias")
    (raw_dir / f"{_RAAF}@20231130.csv").write_bytes(
        "Gravidade;Concessionaria;Data_Ocorrencia;Munic\xedpio\n"
        '"Sim";"FCA";"02/01/2004";"Mimoso"\n'
        '"N\xe3o";"FCA";"03/01/2010";"Itumirim"\n'.encode("latin-1")
    )
    (raw_dir / f"{_RAAF}_indice-de-acidentes-a78db647@20250710.csv").write_text(
        "concessionaria;ano;indice\nEFC;2006;7,43\nEFC;2007;4,49\n", encoding="utf-8"
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert {p.dataset for p in plan.values()} == {ds_id}
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / ds_id
    assert _partitions(ds) == {
        "ano=2004": 1,
        "ano=2006": 1,
        "ano=2007": 1,
        "ano=2010": 1,
    }
    assert not check_dataset(ds)


def test_nome_nu_que_repete_um_nome_com_chave_nao_derruba_o_nu_antigo(
    tmp_path: Path,
) -> None:
    """RAAF: o nome nu mais novo e copia do recurso com chave; o nome nu antigo
    (outro recurso, outro layout) nao pode ser dado como superado por ele."""
    raw_dir = _raw(tmp_path, "ferrovias")
    antigo = raw_dir / f"{_RAAF}@20231130.csv"
    antigo.write_text("Data_Ocorrencia;Linha\n02/01/2004;A\n", encoding="utf-8")
    novo = "Data_Ocorrencia;Linha;N_Trem\n12/01/2020;B;1\n13/01/2020;C;2\n"
    (raw_dir / f"{_RAAF}@20260410.csv").write_text(novo, encoding="utf-8")
    (raw_dir / f"{_RAAF}_acidentes-dezembro-b3851bf8@20260410.csv").write_text(
        novo, encoding="utf-8"
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan[antigo.name].skip_reason is None
    assert plan[f"{_RAAF}@20260410.csv"].skip_reason == "gemeo"
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = (
        tmp_path
        / "lake"
        / "antt"
        / "relatorio-acompanhamento-acidentes-ferroviarios-raaf"
    )
    assert _partitions(ds) == {"ano=2004": 1, "ano=2020": 2}


# --- granularidade (arquivo diario x mensal consolidado) --------------------
def _granularidades(ds: Path) -> dict[str, int]:
    df = pl.concat([pl.read_parquet(f) for f in ds.rglob("*.parquet")], how="diagonal")
    contagem = df.group_by("granularidade").agg(pl.len().alias("n"))
    return {str(g): n for g, n in contagem.iter_rows()}


def test_volume_sat_diario_e_mensal_se_distinguem_por_granularidade(
    tmp_path: Path,
) -> None:
    """O arquivo diario e o mensal consolidado do mesmo periodo caem na mesma
    particao `ano`; a coluna `granularidade` os separa (nao e preciso adivinhar
    pelo formato da data)."""
    raw_dir = _raw(tmp_path, "rodovias")
    cab = "concessionaria;data_de_passagem;volume_total\n"
    (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-flum-aaaa1111@20261103.csv"
    ).write_text(cab + "X;26/02/2025;10\nX;27/02/2025;20\n", encoding="utf-8")
    (
        raw_dir / "volume-sat_trafego-de-veiculos-sat-flum-mensal-bbbb2222@20261103.csv"
    ).write_text(cab + "X;02/2025;30\n", encoding="utf-8")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert _partitions(ds) == {"ano=2025": 3}
    assert _granularidades(ds) == {"dia": 2, "mes": 1}
    total_dia = (
        pl.concat([pl.read_parquet(f) for f in ds.rglob("*.parquet")], how="diagonal")
        .filter(pl.col("granularidade") == "dia")["volume_total"]
        .cast(pl.Int64)
        .sum()
    )
    assert total_dia == 30  # igual ao total do mensal: um so deles conta o trafego


def test_volume_sat_json_e_dia(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    shutil.copy(_FIXTURES / "volume-sat.json", raw_dir / "volume-sat@20261103.json")
    converter.convert(raw_dir.parent, tmp_path / "lake")
    assert _granularidades(tmp_path / "lake" / "antt" / "volume-sat") == {"dia": 5}


def _praca(raw_dir: Path, name: str, datas: list[str], url: str | None = None) -> Path:
    raw = raw_dir / name
    raw.write_text(
        "concessionaria;mes_ano;volume_total\n" + "".join(f"A;{d};1\n" for d in datas),
        encoding="utf-8",
    )
    if url:
        _write_manifest(raw, url)
    return raw


def test_granularidade_e_do_arquivo_mensal_antigo_com_dia_01(tmp_path: Path) -> None:
    """Praca 2010 a 2022: o mes vem como `01/MM/AAAA`. E mensal, nao diario."""
    raw_dir = _raw(tmp_path, "rodovias")
    _praca(
        raw_dir,
        "volume-trafego-praca-pedagio_volume-de-trafego-por-praca-aaaa1111@20241203.csv",
        [f"01/{m:02d}/2010" for m in range(1, 13)],
        "https://x/resource/aaaa1111-0000-4000-8000-000000000001/download/praca-2010.csv",
    )
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "volume-trafego-praca-pedagio"
    assert _granularidades(ds) == {"mes": 12}


def test_granularidade_arquivo_mensal_com_poucas_datas_de_outro_dia(
    tmp_path: Path,
) -> None:
    """Praca 2023: ~99,5% das linhas no dia 01 e umas poucas em 31/01, 02/12 e
    dias de janeiro (a concessionaria mandou o mes com outra data, ou o diario de
    um mes). O arquivo todo e mensal."""
    raw_dir = _raw(tmp_path, "rodovias")
    datas = [f"01/{m:02d}/2023" for m in range(1, 13)] * 20
    datas += ["31/01/2023", "02/12/2023", "03/01/2023"]
    _praca(raw_dir, "volume-trafego-praca-pedagio@20241203.csv", datas)
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "volume-trafego-praca-pedagio"
    assert _granularidades(ds) == {"mes": 243}


def test_granularidade_diaria_por_conteudo_e_por_nome(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    # Sem pista no nome: datas de varios dias => diario, ainda que comece no dia 01.
    _praca(
        raw_dir,
        "volume-trafego-praca-pedagio@20260930.csv",
        ["01/01/2026", "02/01/2026", "03/01/2026", "04/01/2026"],
    )
    # O nome do recurso manda: `_diario` com todas as datas no dia 01 continua diario.
    _praca(
        raw_dir,
        "volume-trafego-praca-pedagio_volume-de-trafego-bbbb2222@20260519.csv",
        ["01/01/2025", "01/02/2025"],
        "https://x/resource/bbbb2222-0000-4000-8000-000000000002/download/praca-2025_diario.csv",
    )
    # E `_mensal_consolidado` com `mm/aaaa`.
    _praca(
        raw_dir,
        "volume-trafego-praca-pedagio_volume-de-trafego-cccc3333@20260519.csv",
        ["01/2025", "02/2025"],
        "https://x/resource/cccc3333-0000-4000-8000-000000000003/download/praca-2025_mensal_consolidado.csv",
    )
    converter.convert(raw_dir.parent, tmp_path / "lake")
    ds = tmp_path / "lake" / "antt" / "volume-trafego-praca-pedagio"
    assert _granularidades(ds) == {"dia": 6, "mes": 2}


def test_volume_radar_granularidade_por_arquivo_e_sem_data(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-radar@20260928.csv").write_text(
        "concessionaria;data_da_passagem;volume_total\n"
        "A;16/01/2026;1\nA;17/01/2026;2\nA;sem data;3\n",
        encoding="utf-8",
    )
    (raw_dir / "volume-radar_radar-x-aaaa1111@20260728.csv").write_text(
        "concessionaria;data_da_passagem;volume_total\nA;01/2026;1\nA;02/2026;2\n",
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-radar"
    assert _granularidades(ds) == {"dia": 3, "mes": 2}


def test_outros_conjuntos_nao_ganham_granularidade(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "acidentes-rodovias@20260928.csv").write_text(
        "data;km\n01/01/2024;1\n", encoding="utf-8"
    )
    converter.convert(raw_dir.parent, tmp_path / "lake")
    f = next((tmp_path / "lake" / "antt" / "acidentes-rodovias").rglob("*.parquet"))
    assert "granularidade" not in pl.read_parquet(f).columns


# --- JSON do SAT depende dos CSV: a escrita nao pode ficar velha -------------
def _linhas_por_concessionaria(ds: Path) -> dict[str, int]:
    df = pl.concat([pl.read_parquet(f) for f in ds.rglob("*.parquet")], how="diagonal")
    return dict(df.group_by("concessionaria").agg(pl.len()).iter_rows())


def test_volume_sat_csv_que_chega_depois_tira_do_parquet_antigo_do_json(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    lake = tmp_path / "lake"
    ds = lake / "antt" / "volume-sat"
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(
            ("NOVA ROTA DO OESTE", [("2025-03-25", 10), ("2025-03-26", 20)]),
            ("ELOVIAS", [("2025-10-30", 7)]),
        ),
        encoding="utf-8",
    )
    converter.convert(raw_dir.parent, lake)
    assert _linhas_por_concessionaria(ds) == {"NOVA ROTA DO OESTE": 2, "ELOVIAS": 1}

    # Chega o CSV diario da Nova Rota: as linhas dela saem do Parquet do JSON.
    (raw_dir / "volume-sat_trafego-nova-rota-aaaa1111@20261104.csv").write_text(
        _SAT_CAB
        + "NOVA ROTA DO OESTE;25/03/2025;10\nNOVA ROTA DO OESTE;26/03/2025;20\n",
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, lake)
    assert not res.errors, res.errors
    assert _linhas_por_concessionaria(ds) == {"NOVA ROTA DO OESTE": 2, "ELOVIAS": 1}
    nomes = _parquets(ds)
    assert (
        sum(n.startswith("volume-sat_cov") for n in nomes) == 1
    )  # JSON, nova identidade
    assert "volume-sat.parquet" not in nomes  # o Parquet antigo do JSON sumiu
    # Estavel: a terceira execucao nao reescreve nada.
    again = converter.convert(raw_dir.parent, lake)
    assert again.converted == 0


def test_volume_sat_json_que_fica_todo_coberto_perde_o_parquet(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    lake = tmp_path / "lake"
    ds = lake / "antt" / "volume-sat"
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("ELOVIAS", [("2025-10-30", 7), ("2024-01-02", 3)])),
        encoding="utf-8",
    )
    converter.convert(raw_dir.parent, lake)
    assert _linhas_por_concessionaria(ds) == {"ELOVIAS": 2}
    (raw_dir / "volume-sat_trafego-elovias-bbbb2222@20261104.csv").write_text(
        _SAT_CAB + "ELOVIAS;30/10/2025;7\nELOVIAS;02/01/2024;3\n", encoding="utf-8"
    )
    for force in (False, True):  # com --force o JSON coberto tambem nao volta
        res = converter.convert(raw_dir.parent, lake, force=force)
        assert not res.errors, res.errors
        assert _linhas_por_concessionaria(ds) == {"ELOVIAS": 2}
        assert not any(n.startswith("volume-sat.") for n in _parquets(ds))
        assert len(_parquets(ds)) == 2  # os dois anos do CSV, nada do JSON


# --- cobertura do JSON por (concessionaria, mes) -----------------------------
def test_volume_sat_csv_diario_so_cobre_os_meses_que_traz(tmp_path: Path) -> None:
    """Um CSV diario que comeca em 2025 nao elimina do JSON as linhas de 2024 da
    mesma concessionaria."""
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-sat_trafego-nova-rota-aaaa1111@20261104.csv").write_text(
        _SAT_CAB
        + "NOVA ROTA DO OESTE;25/03/2025;10\nNOVA ROTA DO OESTE;26/03/2025;20\n",
        encoding="utf-8",
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(
            (
                "NOVA ROTA DO OESTE",
                [("2024-05-02", 1), ("2025-03-25", 10), ("2025-03-26", 20)],
            )
        ),
        encoding="utf-8",
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason is None  # nao esta coberto
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert _partitions(ds) == {"ano=2024": 1, "ano=2025": 2}  # 2024 vem do JSON


def test_volume_sat_cobertura_le_o_csv_inteiro_nao_so_o_inicio(
    tmp_path: Path,
) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    linhas = "".join(f"OUTRA;{d:02d}/01/2025;1\n" for d in range(1, 29)) * 700
    linhas += "ELOVIAS;30/10/2025;7\n"  # depois de mais de 256 KB
    csv = raw_dir / "volume-sat_trafego-x-aaaa1111@20261104.csv"
    csv.write_text(_SAT_CAB + linhas, encoding="utf-8")
    assert csv.stat().st_size > 256 * 1024
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("ELOVIAS", [("2025-10-30", 7)])), encoding="utf-8"
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason == "gemeo"


def test_volume_sat_nomes_com_sa_acento_e_espaco_sao_o_mesmo(tmp_path: Path) -> None:
    from antt_fetcher.lake import _norm_conc

    assert (
        _norm_conc("  Ecovias  Minas Goiás S.A. ")
        == _norm_conc("ECOVIAS MINAS GOIAS S/A")
        == _norm_conc("ecovias minas goias")
        == "ecovias_minas_goias"
    )
    assert _norm_conc("VIA 040") != _norm_conc("VIA 04")
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-sat_trafego-goias-aaaa1111@20261104.csv").write_text(
        _SAT_CAB + "ECOVIAS MINAS GOIAS S/A;10/08/2022;3\n", encoding="utf-8"
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("Ecovias Minas Goiás S.A.", [("2022-08-10", 3)])),
        encoding="utf-8",
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason == "gemeo"


def test_mes_em_python_e_em_polars_concordam() -> None:
    from antt_fetcher.lake import _month_expr, _month_of

    valores = [
        "25/03/2025", "5/3/2025", "2025-03-25", "2025-3-5", "03/2025", "3/2025",
        "2025-03", "13/2025", "31/13/2025", "sem data", "", " 25/03/2025 ",
    ]  # fmt: skip
    df = pl.DataFrame({"d": valores})
    em_polars = df.select(_month_expr("d").alias("m"))["m"].to_list()
    assert em_polars == [_month_of(v) for v in valores]
    assert _month_of("25/03/2025") == "2025-03" and _month_of("13/2025") is None


# --- robustez: falha de leitura nao derruba convert nem inventory -------------
def test_json_sem_chave_de_concessionaria_nao_e_gemeo(tmp_path: Path) -> None:
    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-sat_trafego-elovias-aaaa1111@20261104.csv").write_text(
        _SAT_CAB + "ELOVIAS;30/10/2025;7\n", encoding="utf-8"
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        '{"volume_sat":[{"data_de_passagem":"2025-10-30","volume_total":7},\n'
        '{"concessionaria":"ELOVIAS","data_de_passagem":"2025-10-30","volume_total":7}]}\n',
        encoding="utf-8",
    )
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason is None
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "antt" / "volume-sat"
    assert sum(_partitions(ds).values()) == 2  # nada do JSON foi dado como coberto


def test_cobertura_ilegivel_vai_para_errors_e_inventory_segue(
    tmp_path: Path, monkeypatch
) -> None:
    import antt_fetcher.lake as lake

    raw_dir = _raw(tmp_path, "rodovias")
    (raw_dir / "volume-sat_trafego-elovias-aaaa1111@20261104.csv").write_text(
        _SAT_CAB + "ELOVIAS;30/10/2025;7\n", encoding="utf-8"
    )
    (raw_dir / "volume-sat@20261103.json").write_text(
        _sat_json(("ELOVIAS", [("2025-10-30", 7)])), encoding="utf-8"
    )

    def falha(_path, _ds):
        raise ValueError("csv ilegivel")

    monkeypatch.setattr(lake, "_csv_pairs", falha)
    plan = {p.path.name: p for p in converter.inventory(raw_dir.parent)}
    assert plan["volume-sat@20261103.json"].skip_reason is None
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1 and "volume-sat@20261103.json" in res.errors[0]
    # O CSV continua sendo convertido.
    assert sum(_partitions(tmp_path / "lake" / "antt" / "volume-sat").values()) == 1


def test_hash_ilegivel_nao_derruba_a_selecao(tmp_path: Path, monkeypatch) -> None:
    import antt_fetcher.lake as lake

    raw_dir = _raw(tmp_path, "rodovias")
    for nome in (
        "volume-sat@20261103.csv",
        "volume-sat_trafego-via040-aaaa1111@20261103.csv",
    ):
        (raw_dir / nome).write_text(_SAT_CAB + "VIA 040;05/01/2024;2\n", "utf-8")

    def falha(_path):
        raise OSError("sem permissao")

    monkeypatch.setattr(lake, "sha256_file", falha)
    plan = converter.inventory(raw_dir.parent)
    assert all(p.skip_reason is None for p in plan)  # sem hash, nao ha gemeo
