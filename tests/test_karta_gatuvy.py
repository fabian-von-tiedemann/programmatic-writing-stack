import os
import stat
import tempfile
import time
from datetime import date
from pathlib import Path

import pytest

from bok import bild
from bok.cli import main
from helpers import skriv_graf
from test_karta import NYCKEL, PLATSER, FalskGoogle, falsk  # noqa: F401  (fixturen)

KM_NORRUT = [(59.0, 18.0), (59.0 + 1000 / 111194.93, 18.0)]


def koda(punkter):
    ut, forra = [], (0, 0)
    for lat, lng in punkter:
        nu = (round(lat * 1e5), round(lng * 1e5))
        for v, f in zip(nu, forra):
            d = v - f
            d = ~(d << 1) if d < 0 else d << 1
            while d >= 0x20:
                ut.append(chr((0x20 | (d & 0x1F)) + 63))
                d >>= 5
            ut.append(chr(d + 63))
        forra = nu
    return "".join(ut)


def _mappar():
    return sorted(Path(tempfile.gettempdir()).glob("bok-gatuvy-*"))


def _rutt(falsk, linje=KM_NORRUT, lage="WALK"):
    falsk.rutter = {lage: {"routes": [{"polyline": {"encodedPolyline": koda(linje)}}]}}


def test_gatuvy_langs_en_rutt(bok, falsk, capsys):
    skriv_graf(bok, PLATSER)
    _rutt(falsk)
    fore = sorted(p.relative_to(bok) for p in bok.rglob("*"))
    assert main(["karta", "gatuvy", "hemmet", "fabriken", "--antal", "4"]) == 0
    ut = capsys.readouterr().out
    [mapp] = _mappar()
    assert sorted(p.name for p in mapp.iterdir()) == ["01.jpg", "02.jpg", "03.jpg", "04.jpg"]
    assert stat.S_IMODE(os.stat(mapp).st_mode) == 0o700
    assert not mapp.resolve().is_relative_to(bok)
    assert sorted(p.relative_to(bok) for p in bok.rglob("*")) == fore
    assert "Gatubilder (Google Street View) längs Lägenheten → Fabriken" in ut
    assert "01.jpg  fotograferat 2023-08" in ut and "mot norr" in ut and "start" in ut and "mål" in ut
    assert f"Fotograferat: 2023-08. Hämtat {date.today().isoformat()}. Dagens värld, inte bokens tid." in ut
    assert "map_action=pano&viewpoint=59.3%2C18.07" in ut
    assert "bok karta stada" in ut
    assert NYCKEL not in ut
    routes = [a for a in falsk.anrop if a[0] == "routes"]
    assert routes[0][1]["travelMode"] == "WALK" and routes[0][2] == "routes.polyline.encodedPolyline"
    assert [a[1]["heading"] for a in falsk.anrop if a[0] == "bild"] == ["0", "0", "0", "0"]


def test_gatuvy_hoppar_over(bok, falsk, capsys):
    _rutt(falsk)
    svar = iter([{"status": "ZERO_RESULTS"},
                 {"status": "OK", "pano_id": "samma", "date": "2023-08"},
                 {"status": "OK", "pano_id": "samma", "date": "2023-08"},
                 {"status": "OK", "pano_id": "sista", "date": "2019"}])
    falsk.metadata = lambda plats: next(svar)
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2", "--antal", "4"]) == 0
    ut = capsys.readouterr().out
    [mapp] = _mappar()
    assert sorted(p.name for p in mapp.iterdir()) == ["01.jpg", "02.jpg"]
    assert "ingen gatubild" in ut
    assert "Fotograferat: 2019 – 2023-08." in ut


def test_gatuvy_bild_saknas(bok, falsk, capsys):
    _rutt(falsk)
    falsk.bilder = {f"p-{59.0:.6f},{18.0:.6f}": 404}
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2", "--antal", "2"]) == 0
    ut = capsys.readouterr().out
    assert ut.count("ingen gatubild") == 1 and "01.jpg" in ut


def test_gatuvy_inga_bilder_alls(bok, falsk, capsys):
    _rutt(falsk)
    falsk.metadata = lambda plats: {"status": "ZERO_RESULTS"}
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2"]) == 0
    assert "Inga gatubilder hittades." in capsys.readouterr().out
    assert _mappar() == []


def test_gatuvy_en_plats(bok, falsk, capsys):
    assert main(["karta", "gatuvy", "Storgatan 1, Exempelstad"]) == 0
    ut = capsys.readouterr().out
    assert [a[1]["location"] for a in falsk.anrop if a[0] == "metadata"] == ["Storgatan 1, Exempelstad"]
    assert [a[1]["heading"] for a in falsk.anrop if a[0] == "bild"] == ["0", "90", "180", "270"]
    for riktning in ("mot norr", "mot öst", "mot söder", "mot väst"):
        assert riktning in ut
    assert "runt Storgatan 1, Exempelstad" in ut


def test_gatuvy_en_plats_utan_bild(bok, falsk, capsys):
    falsk.metadata = lambda plats: {"status": "ZERO_RESULTS"}
    assert main(["karta", "gatuvy", "Storgatan 1, Exempelstad"]) == 2
    assert "ingen gatubild inom 50 meter" in capsys.readouterr().err
    assert _mappar() == []


def test_gatuvy_okant_fotodatum(bok, falsk, capsys):
    falsk.metadata = lambda plats: {"status": "OK", "pano_id": "p"}
    assert main(["karta", "gatuvy", "Storgatan 1, Exempelstad"]) == 0
    ut = capsys.readouterr().out
    assert "fotograferat okänt" in ut and "Fotograferat: okänt." in ut and "Öppna i webbläsaren" not in ut


def test_gatuvy_ingen_rutt(bok, falsk, capsys):
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2"]) == 2
    assert "Ingen rutt hittades" in capsys.readouterr().err


@pytest.mark.parametrize("extra", [["--antal", "0"], ["--antal", "21"], ["--mellanrum", "5"]])
def test_gatuvy_fel_antal(bok, falsk, capsys, extra):
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2", *extra]) == 2
    assert falsk.anrop == []


def test_gatuvy_rensar_gamla_och_stada(bok, falsk, capsys):
    gammal = bild.ny_mapp("bok-gatuvy-")
    os.utime(gammal, (time.time() - 2 * 86400, time.time() - 2 * 86400))
    assert main(["karta", "gatuvy", "Storgatan 1, Exempelstad"]) == 0
    assert not gammal.exists() and len(_mappar()) == 1
    bild.ny_mapp("bok-bild-")
    assert main(["karta", "stada"]) == 0
    assert "Rensade 2 tillfälliga mappar." in capsys.readouterr().out
    assert _mappar() == []


def test_gatuvy_ingen_bild_har_parentes(bok, falsk, capsys):
    _rutt(falsk)
    falsk.metadata = lambda plats: {"status": "ZERO_RESULTS"} if plats.startswith("59.000000") else \
        {"status": "OK", "pano_id": plats, "date": "2023"}
    main(["karta", "gatuvy", "A gatan 1", "B gatan 2", "--antal", "2"])
    assert "ingen gatubild           (start)" in capsys.readouterr().out


def test_gatuvy_fel_mitt_i_visar_mappen(bok, falsk, capsys):
    _rutt(falsk)
    falsk.metadata = lambda plats: {"status": "OK", "date": "2023",
                                     "pano_id": "forsta" if plats.startswith("59.000000") else "andra"}
    falsk.bilder = {"andra": 429}
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2", "--antal", "2"]) == 2
    [mapp] = _mappar()
    assert str(mapp) in capsys.readouterr().out
    assert [p.name for p in mapp.iterdir()] == ["01.jpg"]


def test_gatuvy_nan(bok, falsk, capsys):
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2", "--mellanrum", "nan"]) == 2
    assert falsk.anrop == []


def test_gatuvy_udda_svar(bok, falsk, capsys):
    falsk.rutter = {"WALK": {"routes": [{"polyline": "x"}]}}
    assert main(["karta", "gatuvy", "A gatan 1", "B gatan 2"]) == 2
    assert "Ingen rutt hittades" in capsys.readouterr().err
    falsk.metadata = lambda plats: {"status": "OK", "pano_id": "p", "location": "x"}
    assert main(["karta", "gatuvy", "A gatan 1"]) == 0
    assert "Öppna i webbläsaren" not in capsys.readouterr().out