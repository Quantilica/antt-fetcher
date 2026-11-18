"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import zipfile
from pathlib import Path

import polars as pl
import pytest
import quantilica.core.manifests as manifests_mod
from quantilica.analytics.lake import LakeWriter

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

    original_io_open = io.open
    original_path_open = Path.open

    def io_open_espiado(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        texto = str(file)
        if texto.startswith(raiz) and not texto.endswith(".manifest.json"):
            vistas.append(f"io.open:{texto}")
        return original_io_open(file, *args, **kwargs)

    def path_open_espiado(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if str(self).startswith(raiz) and not self.name.endswith(".manifest.json"):
            vistas.append(f"Path.open:{self}")
        return original_path_open(self, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espiado)
    monkeypatch.setattr(io, "open", io_open_espiado)
    monkeypatch.setattr(Path, "open", path_open_espiado)
    monkeypatch.setattr(zipfile, "ZipFile", espia("zipfile", zipfile.ZipFile))
    for nome in (
        "_member_as_text",
        "_csv_member_names",
        "_scan_text",
        "_json_pairs",
        "_csv_pairs_cached",
    ):
        monkeypatch.setattr(lake_mod, nome, espia(nome, getattr(lake_mod, nome)))
    monkeypatch.setattr(pl, "scan_csv", espia("scan_csv", pl.scan_csv))
    monkeypatch.setattr(
        manifests_mod, "sha256_file", espia("hash", manifests_mod.sha256_file)
    )
    return vistas


def _so_lista_zip(leituras: list[str]) -> None:
    """Nada alem de ler o diretorio central do ZIP de nome antigo (o rotulo do
    membro pode mandar no conjunto): sem extrair, varrer nem ler CSV/JSON."""
    assert set(leituras) <= {"_csv_member_names", "zipfile"} | {
        v
        for v in leituras
        if v.startswith(("open:", "io.open:")) and v.endswith(".zip")
    }


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
    if dataset == "acidentes-rodovias":
        assert leituras == []  # tudo completo no lake: nem o ZIP e aberto
    else:
        _so_lista_zip(leituras)  # o ZIP antigo pode ter membro deste conjunto


def test_um_dataset_nao_toca_o_bruto_de_outro(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    leituras.clear()  # a montagem do bruto de teste le os arquivos
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
    leituras.clear()
    r = converter.convert(raw, lake, datasets=["volume-trafego-praca-pedagio"])
    assert not r.errors
    assert not any("ciot@" in v for v in leituras)


def test_chave_registrada_diferente_da_atual_pede_conversao() -> None:
    """Rodape com chave que o conversor nao daria hoje (regra de chaves mudou)
    nao vale como em dia: o caminho completo decide, como antes."""
    ok = lake_mod._chaves_do_bruto
    assert ok(["acidentes", "acidentes__membro"], "acidentes")
    assert not ok(["acidentes", "acidentes_2"], "acidentes")
    assert not ok(["outra_chave"], "acidentes")
    assert not ok([None], "acidentes")


def _writer(lake: Path, dataset: str) -> LakeWriter:
    from quantilica.core.lake import DatasetDescriptor, partition_types_for

    return LakeWriter(
        lake / "antt" / dataset,
        DatasetDescriptor(
            source_id="antt",
            dataset_id=dataset,
            alias=dataset,
            partition_keys=["ano"],
            partition_types=partition_types_for(["ano"]),
        ),
    )


def _parquets(lake: Path, dataset: str) -> list[Path]:
    return sorted((lake / "antt" / dataset).rglob("*.parquet"))


def _falha_no_ano_do_zip(monkeypatch: pytest.MonkeyPatch, ano: int) -> None:
    """A escrita do ``ano`` a partir de um ZIP falha, como um disco cheio."""
    original = LakeWriter.write_polars

    def write(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if kwargs["src"].suffix == ".zip" and kwargs["partitions"] == {"ano": ano}:
            raise OSError("disco cheio")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(LakeWriter, "write_polars", write)


def test_conversao_interrompida_no_ano_k_completa_na_rodada_seguinte(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Falha no 2o ano do ZIP: o ZIP nao vira pulo permanente."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    ds = ["acidentes-rodovias"]
    with monkeypatch.context() as m:
        _falha_no_ano_do_zip(m, 2025)
        r1 = converter.convert(raw, lake, datasets=ds)
    assert len(r1.errors) == 1
    assert "disco cheio" in r1.errors[0]
    assert (r1.converted, r1.skipped) == (3, 0)  # CSV solto (2) e o ano 2024 do ZIP

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=ds)
    assert r2.errors == []
    assert (r2.converted, r2.skipped) == (1, 3)
    assert "_member_as_text" in leituras  # o ZIP foi reaberto
    assert len(_parquets(lake, ds[0])) == 4

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=ds)
    assert (r3.converted, r3.skipped, r3.errors) == (0, 4, [])
    assert leituras == []


def _zip_de_dois_membros(raw: Path) -> None:
    with zipfile.ZipFile(raw / "rodovias" / "pacote@20261101.zip", "w") as zf:
        zf.writestr("acidentes_rodovias_a.csv", _ACID)
        zf.writestr("acidentes_rodovias_b.csv", _ACID.replace("COL", "ABA"))


def test_zip_de_varios_membros_declara_a_uniao_e_completa_apos_falha(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    _zip_de_dois_membros(raw)
    _sidecars(raw)
    ds = ["acidentes-rodovias"]
    with monkeypatch.context() as m:
        # 2o membro (b): sua escrita de 2025 falha; o membro a ja foi gravado.
        original = LakeWriter.write_polars

        def write(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
            if "rodovias_b" in kwargs["file_key_name"] and (
                kwargs["partitions"] == {"ano": 2025}
            ):
                raise OSError("disco cheio")
            return original(self, *args, **kwargs)

        m.setattr(LakeWriter, "write_polars", write)
        r1 = converter.convert(raw, lake, datasets=ds)
    assert len(r1.errors) == 1

    pacote = raw / "rodovias" / "pacote@20261101.zip"
    # A declaracao dos Parquets ja gravados e a uniao das saidas dos dois membros.
    saidas = _writer(lake, ds[0]).origin_outputs(pacote)
    assert saidas is not None and len(saidas) == 4  # 2 membros x 2 anos
    assert not _writer(lake, ds[0]).origin_complete(pacote)

    r2 = converter.convert(raw, lake, datasets=ds)
    assert r2.errors == []
    assert _writer(lake, ds[0]).origin_complete(pacote)
    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=ds)
    assert (r3.converted, r3.errors) == (0, [])
    assert r3.skipped == 8  # 2 do CSV solto, 2 do ZIP antigo e 4 do pacote
    assert leituras == []


def test_lake_antigo_sem_declaracao_reconverte_uma_vez(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    original = LakeWriter.write_polars

    def sem_declaracao(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        kwargs.pop("origin_outputs", None)
        return original(self, *args, **kwargs)

    ds = ["acidentes-rodovias"]
    with monkeypatch.context() as m:
        m.setattr(LakeWriter, "write_polars", sem_declaracao)
        r0 = converter.convert(raw, lake, datasets=ds)
    assert (r0.converted, r0.errors) == (4, [])

    leituras.clear()
    r1 = converter.convert(raw, lake, datasets=ds)
    assert (r1.converted, r1.skipped, r1.errors) == (4, 0, [])
    assert "_member_as_text" in leituras

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=ds)
    assert (r2.converted, r2.skipped, r2.errors) == (0, 4, [])
    assert leituras == []


def test_zip_de_nome_antigo_de_outro_conjunto_vale_pelo_rotulo_do_membro(
    tmp_path: Path,
) -> None:
    """ZIP fora do catalogo, nomeado para pedagio, com um membro de acidentes: o
    rotulo do membro manda (como no main), entao a tarefa de acidentes o abre."""
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    (raw / "rodovias").mkdir(parents=True)
    with zipfile.ZipFile(raw / "rodovias" / "pedagio_2024@20261101.zip", "w") as zf:
        zf.writestr("acidentes_rodovias_2024.csv", _ACID)
    _sidecars(raw)

    r1 = converter.convert(raw, lake, datasets=["acidentes-rodovias"])
    assert (r1.converted, r1.skipped, r1.errors) == (2, 0, [])
    r2 = converter.convert(raw, lake, datasets=["acidentes-rodovias"])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    r3 = converter.convert(raw, lake, datasets=["volume-trafego-praca-pedagio"])
    assert (r3.converted, r3.skipped, r3.errors) == (0, 0, [])


def test_erro_deterministico_de_membro_reaparece_a_cada_build(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    (raw / "rodovias").mkdir(parents=True)
    with zipfile.ZipFile(raw / "rodovias" / "pacote@20261101.zip", "w") as zf:
        zf.writestr("acidentes_rodovias_a.csv", _ACID)
        zf.writestr("acidentes_rodovias_sem_data.csv", "tipo;km\nCOLISAO;1\n")
    _sidecars(raw)

    r1 = converter.convert(raw, lake, datasets=["acidentes-rodovias"])
    assert (r1.converted, len(r1.errors)) == (2, 1)
    r2 = converter.convert(raw, lake, datasets=["acidentes-rodovias"])
    assert (r2.converted, r2.skipped, len(r2.errors)) == (0, 2, 1)
    assert "sem coluna de ano" in r2.errors[0]


# --- volume-sat: cobertura do JSON em cache ----------------------------------
_SAT_CSV = "volume-sat_trafego-de-veiculos-sat-nova-rota-aaaa1111@20261102.csv"
_SAT_JSON = (
    '{"volume_sat":[{"concessionaria":"NOVA ROTA DO OESTE",'
    '"data_de_passagem":"2025-03-25","volume_total":10}]}\n'
    '{"volume_sat":[{"concessionaria":"ELOVIAS",'
    '"data_de_passagem":"2025-10-30","volume_total":7}]}\n'
)


def _bruto_sat(tmp_path: Path) -> Path:
    raw_dir = tmp_path / "raw" / "rodovias"
    raw_dir.mkdir(parents=True)
    (raw_dir / _SAT_CSV).write_text(
        _SAT_CAB + "NOVA ROTA DO OESTE;25/03/2025;10\n", encoding="utf-8"
    )
    (raw_dir / "volume-sat@20261103.json").write_text(_SAT_JSON, encoding="utf-8")
    _sidecars(raw_dir.parent)
    return raw_dir.parent


def test_json_do_sat_nao_le_csv_diario_nem_json_sem_mudanca(
    tmp_path: Path, leituras: list[str]
) -> None:
    """A cobertura do JSON vem do cache de pares (por sha do sidecar): a segunda
    rodada nao le nenhum CSV diario nem o JSON, e da as mesmas contagens."""
    raw, lake = _bruto_sat(tmp_path), tmp_path / "lake"
    ds = ["volume-sat"]
    r1 = converter.convert(raw, lake, datasets=ds)
    assert not r1.errors
    assert (r1.converted, r1.skipped) == (2, 0)
    cache = lake / "antt" / "volume-sat" / ".cobertura-pares.json"
    assert cache.is_file()

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=ds)
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    assert leituras == []


def test_json_do_sat_sem_cache_relê_uma_vez_e_refaz_o_cache(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto_sat(tmp_path), tmp_path / "lake"
    ds = ["volume-sat"]
    converter.convert(raw, lake, datasets=ds)
    cache = lake / "antt" / "volume-sat" / ".cobertura-pares.json"
    cache.write_text("{ nao e json", encoding="utf-8")

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=ds)
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    assert "_json_pairs" in leituras and "_csv_pairs_cached" in leituras
    assert json.loads(cache.read_text(encoding="utf-8"))["version"] == 1

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=ds)
    assert (r3.converted, r3.skipped, r3.errors) == (0, 2, [])
    assert leituras == []


def test_json_do_sat_com_csv_diario_novo_recalcula_a_cobertura(
    tmp_path: Path, leituras: list[str]
) -> None:
    """Um CSV diario novo cobre mais do JSON: o JSON e regravado sem as linhas
    cobertas, a identidade antiga sai e o CSV novo e o unico lido."""
    raw, lake = _bruto_sat(tmp_path), tmp_path / "lake"
    ds = ["volume-sat"]
    converter.convert(raw, lake, datasets=ds)

    novo = (
        raw
        / "rodovias"
        / "volume-sat_trafego-de-veiculos-sat-elovias-bbbb2222@20261104.csv"
    )
    novo.write_text(_SAT_CAB + "ELOVIAS;30/10/2025;7\n", encoding="utf-8")
    _sidecars(raw)
    leituras.clear()

    r = converter.convert(raw, lake, datasets=ds)
    assert not r.errors
    # O JSON ficou todo coberto (nada dele e escrito) e o CSV novo e convertido.
    assert r.converted == 1
    nomes = {p.name for p in _parquets(lake, "volume-sat")}
    assert not any("volume-sat_" in n and "cov" in n for n in nomes)
    abertos = [v for v in leituras if v.startswith(("open:", "io.open:"))]
    assert all("elovias" in v for v in abertos)

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=ds)
    assert (r3.converted, r3.errors) == (0, [])
    assert leituras == []


def test_espiao_do_hash_pega_a_leitura_quando_nao_ha_sidecar(
    tmp_path: Path, leituras: list[str]
) -> None:
    """Controle do espiao: sem sidecar o hash do bruto sai da leitura dele (e o
    espiao de ``sha256_file`` registra), o que as outras rodadas provam nao
    acontecer com o sidecar ao lado."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    ds = ["volume-trafego-praca-pedagio"]
    converter.convert(raw, lake, datasets=ds)
    for sidecar in raw.rglob("*.manifest.json"):
        sidecar.unlink()
    leituras.clear()
    r = converter.convert(raw, lake, datasets=ds)
    assert (r.converted, r.skipped, r.errors) == (0, 1, [])
    assert "hash" in leituras
