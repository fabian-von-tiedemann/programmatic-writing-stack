import json
import sqlite3
from unittest.mock import patch

import pytest

from bok import annotations, boktoml
from bok.annotations import AnnotationsFel, hamta, render_md
from bok.cli import main

TITEL = "Livets 'gåta'"


@pytest.fixture
def dbs(tmp_path):
    lib = tmp_path / "BKLibrary-1.sqlite"
    anno = tmp_path / "AEAnnotation_1.sqlite"
    with sqlite3.connect(lib) as c:
        c.execute("CREATE TABLE ZBKLIBRARYASSET (ZASSETID TEXT, ZTITLE TEXT)")
        c.execute("INSERT INTO ZBKLIBRARYASSET VALUES ('A1', ?)", (TITEL,))
    with sqlite3.connect(anno) as c:
        c.execute("CREATE TABLE ZAEANNOTATION (ZANNOTATIONASSETID TEXT, ZANNOTATIONCREATIONDATE REAL, "
                  "ZANNOTATIONSTYLE INTEGER, ZANNOTATIONSELECTEDTEXT TEXT, ZANNOTATIONNOTE TEXT, "
                  "ZANNOTATIONLOCATION TEXT, ZANNOTATIONDELETED INTEGER)")
        c.execute("INSERT INTO ZAEANNOTATION VALUES ('A1', 800000000, 3, 'Fin mening', 'Mer sånt', 'loc1', 0)")
        c.execute("INSERT INTO ZAEANNOTATION VALUES ('A1', 800000100, 1, 'Raderad', NULL, '', 1)")
    return anno, lib


def test_hamta(dbs):
    anno, lib = dbs
    noter = hamta(TITEL, anno_db=anno, lib_db=lib)
    assert len(noter) == 1
    assert noter[0]["markerat"] == "Fin mening" and noter[0]["stil"] == "gul"


def test_okand_titel(dbs):
    anno, lib = dbs
    with pytest.raises(AnnotationsFel, match="Hittar ingen bok"):
        hamta("Annan", anno_db=anno, lib_db=lib)


def test_render_md():
    md = render_md("X", [{"datum": "2026-01-01 10:00", "stil": "gul", "markerat": "a", "not": "b", "plats": ""}])
    assert "> a" in md and "**Not:** b" in md and "Totalt: 1" in md


def test_cli_json(bok, dbs, capsys):
    anno, lib = dbs
    assert main(["annotations", "--titel", TITEL, "--json", "--anno-db", str(anno), "--lib-db", str(lib)]) == 0
    assert json.loads(capsys.readouterr().out)[0]["not"] == "Mer sånt"


def test_invalid_sqlite(tmp_path):
    lib = tmp_path / "BKLibrary-1.sqlite"
    anno = tmp_path / "AEAnnotation_1.sqlite"
    lib.write_bytes(b"inte en databas")
    with sqlite3.connect(anno) as c:
        c.execute("CREATE TABLE ZAEANNOTATION (ZANNOTATIONASSETID TEXT, ZANNOTATIONCREATIONDATE REAL, "
                  "ZANNOTATIONSTYLE INTEGER, ZANNOTATIONSELECTEDTEXT TEXT, ZANNOTATIONNOTE TEXT, "
                  "ZANNOTATIONLOCATION TEXT, ZANNOTATIONDELETED INTEGER)")
    with pytest.raises(AnnotationsFel, match="Kunde inte läsa Apple Böckers databas"):
        hamta(TITEL, anno_db=anno, lib_db=lib)


def test_permission_error(dbs):
    anno, lib = dbs
    with patch("bok.annotations.shutil.copy2", side_effect=PermissionError("Access denied")):
        with pytest.raises(AnnotationsFel, match="Fullständig skivåtkomst"):
            hamta(TITEL, anno_db=anno, lib_db=lib)


def test_cli_without_titel_uses_bok_toml(bok, dbs, capsys):
    anno, lib = dbs
    # Update the fixture book's bok.toml to have TITEL
    boktoml_path = bok / "bok.toml"
    content = boktoml_path.read_text()
    content = content.replace('titel = "Testbok"', f'titel = "{TITEL}"')
    boktoml_path.write_text(content)
    # Now the CLI should work without --titel
    assert main(["annotations", "--json", "--anno-db", str(anno), "--lib-db", str(lib)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output[0]["markerat"] == "Fin mening"


def test_cli_empty_titel_error(bok, capsys):
    # Set empty titel in bok.toml
    boktoml_path = bok / "bok.toml"
    content = boktoml_path.read_text()
    content = content.replace('titel = "Testbok"', 'titel = ""')
    boktoml_path.write_text(content)
    ret = main(["annotations"])
    assert ret == 2
    assert "Ange bokens titel i Böcker med --titel" in capsys.readouterr().err
