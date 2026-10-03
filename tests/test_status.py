import json
import os

import pytest

from bok.cli import main
from bok.status import compute, kapitelplan
from helpers import BRA_RED, BRA_SPRAK, fyll_forberedelse, rapport, skriv, skriv_graf


def ja_pa_forberedelse(root):
    rapport(root, omfang="forberedelse", roll="forfattare", utfall="godkand")


def scenkort(root, nr, godkand=True):
    skriv(root, f"bok/plot/kapitel/kapitel-{nr:02d}.md",
          f"---\nkapitel: {nr}\npov: anna\nkaraktarer: [anna]\nplatser: []\nbagar: [t-arvet]\n"
          f"godkand: {'true' if godkand else 'false'}\n---\n\n# Kapitel {nr}\n")


def granska(root, nr, runda, red="godkand", sprak="godkand", red_betyg=None):
    rapport(root, omfang="kapitel", kapitel=nr, roll="redaktor", runda=runda,
            betyg=red_betyg or BRA_RED, utfall=red)
    rapport(root, omfang="kapitel", kapitel=nr, roll="sprakgranskare", runda=runda,
            betyg=BRA_SPRAK, utfall=sprak)


def klart_kapitel(root, nr):
    scenkort(root, nr)
    skriv(root, f"manuskript/kapitel-{nr:02d}.md", "Text.\n")
    granska(root, nr, 1)
    skriv(root, f"bok/sammanfattningar/kapitel-{nr:02d}.md", "Sammanfattning.\n")
    rapport(root, omfang="kapitel", kapitel=nr, roll="forfattare", runda=1, utfall="godkand")


def test_tom_bok(bok):
    s = compute(bok)
    assert s["titel"] == "Testbok"
    assert s["nasta"] == "Förberedelse: Koncept – premiss.md är inte ifylld."
    assert [d["namn"] for d in s["forberedelse"]] == ["Koncept", "Karaktärer", "Plot", "Röst", "Kapitelplan"]


def test_karaktar_utan_pov(bok):
    fyll_forberedelse(bok)
    skriv(bok, "bok/karaktarer/anna.md", "---\nid: anna\nnamn: Anna\npov: false\n---\n")
    assert "ingen POV-karaktär" in compute(bok)["nasta"]


def test_trasig_karaktarsfil_kraschar_inte(bok):
    fyll_forberedelse(bok)
    skriv(bok, "bok/karaktarer/erik.md", "---\nid: erik\n")
    assert "erik.md har trasig frontmatter" in compute(bok)["nasta"]


def test_forberedelse_klar_vantar_pa_ja(bok):
    fyll_forberedelse(bok)
    s = compute(bok)
    assert all(d["klar"] for d in s["forberedelse"])
    assert s["nasta"].startswith("Förberedelsen är klar")


def test_kapitelplan(bok):
    fyll_forberedelse(bok)
    assert kapitelplan(bok) == {1: 1, 2: 1, 3: 2}


def test_loopen_for_ett_kapitel(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    assert compute(bok)["nasta"] == "Kapitel 1: Plot-arkitekten gör scenkortet."
    scenkort(bok, 1, godkand=False)
    assert compute(bok)["nasta"] == "Kapitel 1: visa scenkortet och be om ja."
    scenkort(bok, 1)
    assert compute(bok)["nasta"] == "Kapitel 1: Writer skriver utkastet."
    skriv(bok, "manuskript/kapitel-01.md", "Text.\n")
    assert "Redaktör och Språkgranskare (runda 1)" in compute(bok)["nasta"]
    granska(bok, 1, 1, red="revidera", red_betyg={**BRA_RED, "tema": 6})
    assert compute(bok)["nasta"].startswith("Kapitel 1: Writer reviderar efter fynden i runda 1")
    granska(bok, 1, 2)
    assert compute(bok)["nasta"].startswith("Kapitel 1: Kontinuitet")
    skriv(bok, "bok/sammanfattningar/kapitel-01.md", "Sammanfattning.\n")
    assert compute(bok)["nasta"].startswith("Kapitel 1: be henne läsa manuskript/kapitel-01.md")
    rapport(bok, omfang="kapitel", kapitel=1, roll="forfattare", runda=2, utfall="godkand")
    s = compute(bok)
    assert s["kapitel"][0]["klart"] is True
    assert s["kapitel"][0]["betyg"]["tema"] == 8
    assert s["nasta"] == "Kapitel 2: Plot-arkitekten gör scenkortet."


def test_en_granskare_saknas(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    scenkort(bok, 1)
    skriv(bok, "manuskript/kapitel-01.md", "Text.\n")
    rapport(bok, omfang="kapitel", kapitel=1, roll="redaktor", runda=1, betyg=BRA_RED, utfall="godkand")
    assert compute(bok)["nasta"] == "Kapitel 1: Språkgranskaren ska granska runda 1."


def test_eskalering_efter_tre_rundor(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    scenkort(bok, 1)
    skriv(bok, "manuskript/kapitel-01.md", "Text.\n")
    for r in (1, 2, 3):
        granska(bok, 1, r, sprak="revidera")
    assert "inte nöjda efter runda 3" in compute(bok)["nasta"]


def test_tillbaka_fran_forfattaren(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    scenkort(bok, 1)
    skriv(bok, "manuskript/kapitel-01.md", "Text.\n")
    granska(bok, 1, 1)
    skriv(bok, "bok/sammanfattningar/kapitel-01.md", "S.\n")
    rapport(bok, "Mer värme.", omfang="kapitel", kapitel=1, roll="forfattare", runda=1, utfall="tillbaka")
    assert compute(bok)["nasta"].startswith("Kapitel 1: Writer reviderar efter dina kommentarer")


def test_inaktuell_sammanfattning(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    scenkort(bok, 1)
    manus = skriv(bok, "manuskript/kapitel-01.md", "Text.\n")
    sammanf = skriv(bok, "bok/sammanfattningar/kapitel-01.md", "S.\n")
    os.utime(sammanf, (1_000_000, 1_000_000))
    os.utime(manus, (2_000_000, 2_000_000))
    granska(bok, 1, 1)
    assert compute(bok)["nasta"].startswith("Kapitel 1: Kontinuitet")


def test_aktgrans_och_slut(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    klart_kapitel(bok, 1)
    klart_kapitel(bok, 2)
    assert compute(bok)["nasta"] == "Akt 1 är skriven: Förläggaren läser akten."
    rapport(bok, omfang="akt", akt=1, roll="forlaggare", utfall="atgarda")
    assert compute(bok)["nasta"] == "Akt 1 är skriven: Förläggaren läser akten."
    rapport(bok, omfang="akt", akt=1, roll="forlaggare", utfall="fortsatt")
    assert compute(bok)["nasta"] == "Kapitel 3: Plot-arkitekten gör scenkortet."
    klart_kapitel(bok, 3)
    rapport(bok, omfang="akt", akt=2, roll="forlaggare", utfall="fortsatt")
    assert compute(bok)["nasta"].startswith("Alla planerade kapitel är klara")
    rapport(bok, omfang="bok", roll="forlaggare", utfall="A")
    assert compute(bok)["nasta"].startswith("Boken är klar")


def test_kapitelfil_med_en_siffra(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    scenkort(bok, 1)
    skriv(bok, "manuskript/kapitel-1.md", "Text.\n")
    assert "runda 1" in compute(bok)["nasta"]


def test_ofyllt_scenkort_raknas_som_saknat(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    skriv(bok, "bok/plot/kapitel/kapitel-01.md", (bok / "bok/plot/kapitel/MALL.md").read_text())
    assert compute(bok)["nasta"] == "Kapitel 1: Plot-arkitekten gör scenkortet."


def test_bagar(bok):
    fyll_forberedelse(bok)
    skriv(bok, "bok/plot/bagar.md",
          "# Bågar\n\n## Arvet\nid: t-arvet\ntyp: intrig\nstart: kapitel 1\n\nText.\n\n"
          "## Kärleken\nid: t-karlek\ntyp: karaktar\nstart: kapitel 2\n\nText.\n")
    ja_pa_forberedelse(bok)
    skriv_graf(bok)
    for nr in (1, 2):
        klart_kapitel(bok, nr)
    b = compute(bok)["bagar"]
    assert b["ej_paborjade"] == ["t-karlek"]
    assert b["olosta_planteringar"] == [{"bage": "t-arvet", "vad": "Nyckeln i ladan", "kapitel": 1}]


def test_trasig_graf_visas_men_kraschar_inte(bok):
    skriv(bok, "bok/story-graph/events.json", "{")
    assert "events.json" in compute(bok)["bagar"]["fel"]


def test_rapportfil_som_inte_ar_utf8_kraschar_inte(bok):
    fyll_forberedelse(bok)
    ja_pa_forberedelse(bok)
    sokvag = bok / "bok/rapporter/kapitel-01/redaktor-r1.md"
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    sokvag.write_bytes("---\nroll: redaktor\n---\nVärme och själ.\n".encode("latin-1"))
    assert compute(bok)["nasta"] == "Kapitel 1: Plot-arkitekten gör scenkortet."


def test_cli_text_och_json(bok, capsys):
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# Testbok\n") and "Nästa steg: " in out and "✗ Koncept" in out
    assert main(["status", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["titel"] == "Testbok"
