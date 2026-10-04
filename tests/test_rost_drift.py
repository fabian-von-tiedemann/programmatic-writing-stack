import json

from bok.cli import main
from bok.mallar import lagg_till
from bok.rost import delta, drift, pastisch, profil, utanfor, matt
from helpers import skriv

ROST = [
    "Hon tog kaffet och gick ut och det regnade och det var kallt och att gå var svårt.",
    "Han satt kvar och det var tyst och hon visste att det var över och att han visste.",
    "Det var morgon och det luktade järn och hon tänkte att det fick vara så.",
]
KONTROLL = [
    "När hon kom hem hade han redan gått, som om han hade vetat när hon skulle komma.",
    "Rummet som hon hade hyrt var tomt när hon kom, som alltid när det hade regnat.",
]


def labb(root, rost=ROST, kontroll=KONTROLL):
    lagg_till(root, "rostlabb")
    for i, t in enumerate(rost):
        skriv(root, f"bok/stil/provbank/r{i}.md", f"---\nlage: stilla\n---\n{t}\n")
    for i, t in enumerate(kontroll):
        skriv(root, f"bok/stil/kontroll/k{i}.md", f"---\nlage: stilla\n---\n{t}\n")


def test_delta_riktning():
    d_rost, d_kontroll = delta(ROST[0] + " " + ROST[1], ROST, KONTROLL)
    assert d_rost < d_kontroll
    d_rost, d_kontroll = delta(" ".join(KONTROLL), ROST, KONTROLL)
    assert d_kontroll < d_rost


def test_utanfor_spridningen():
    prof = profil(["Hon gick. Han stod.", "Det var sent. Hon sov."])  # median 2 ord per mening
    lang = matt("Det var sent på kvällen när hon äntligen kom hem till det tomma huset vid vattnet.")
    namn = [u[0] for u in utanfor(lang, prof)]
    assert "meningslangd_median" in namn
    assert utanfor(matt("Hon gick. Han stod."), prof) == []


def test_utanfor_nollspann_anvander_medianen():
    prof = profil(["Hon gick. Han stod.", "Hon sov. Han åt."])  # spannet för meningslängd är noll
    assert utanfor(matt("Hon gick. Han stod."), prof) == []


def test_pastisch_slar_ihop_sekvenser_och_anger_kalla():
    kalla = "Han räknade stolarna två gånger innan han satte sig vid bordet."
    text = "Det var kväll. Han räknade stolarna två gånger innan han satte sig ner."
    assert pastisch(text, [("bok/stil/provbank/a.md", kalla)]) == [
        ("han räknade stolarna två gånger innan han satte sig", "bok/stil/provbank/a.md")]
    assert pastisch("Han räknade stolarna en gång.", [("a", kalla)]) == []


def test_drift_varnar_nar_kapitlet_ar_kontroll(bok):
    labb(bok)
    kap = skriv(bok, "manuskript/kapitel-01.md", "# Kapitel 1\n\n" + " ".join(KONTROLL) + "\n")
    d = drift(bok, kap)
    assert d["underlag"] == {"provbank": 3, "kontroll": 2}
    assert d["delta"]["narmare_kontroll"] is True


def test_drift_lugn_nar_kapitlet_ar_rosten(bok):
    labb(bok)
    kap = skriv(bok, "manuskript/kapitel-01.md", ROST[0] + " " + ROST[2] + "\n")
    assert drift(bok, kap)["delta"]["narmare_kontroll"] is False


def test_drift_pastisch_mot_exempel(bok):
    labb(bok)
    skriv(bok, "bok/stil/exempel/forebild.md", "Varför: tonen.\n\nHon stod länge vid fönstret och såg på regnet.\n")
    kap = skriv(bok, "manuskript/kapitel-01.md", "Sedan stod hon länge vid fönstret och såg på regnet igen.\n")
    kallor = [p["kalla"] for p in drift(bok, kap)["pastisch"]]
    assert kallor == ["bok/stil/exempel/forebild.md"]


def test_drift_for_lite_underlag(bok):
    labb(bok, rost=ROST[:2])
    kap = skriv(bok, "manuskript/kapitel-01.md", "Hon gick.\n")
    d = drift(bok, kap)
    assert d["delta"] is None and d["utanfor"] == []


def test_drift_tomt_kapitel(bok):
    labb(bok)
    kap = skriv(bok, "manuskript/kapitel-01.md", "# Kapitel 1\n")
    d = drift(bok, kap)
    assert d["pastisch"] == []
    assert isinstance(d["delta"]["rost"], float)


def test_cli_drift(bok, capsys):
    labb(bok)
    skriv(bok, "manuskript/kapitel-01.md", " ".join(KONTROLL) + "\n")
    assert main(["rost", "drift", "manuskript/kapitel-01.md"]) == 0
    out = capsys.readouterr().out
    assert "närmare AI-genomsnittet" in out and "3 provstycken, 2 kontrollvarianter" in out
    assert main(["rost", "drift", "manuskript/kapitel-01.md", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["delta"]["narmare_kontroll"] is True


def test_cli_drift_fel(bok, capsys):
    skriv(bok, "manuskript/kapitel-01.md", "Hon gick.\n")
    assert main(["rost", "drift", "manuskript/kapitel-01.md"]) == 2  # modulen saknas
    lagg_till(bok, "rostlabb")
    assert main(["rost", "drift", "manuskript/kapitel-09.md"]) == 2  # filen saknas
    assert main(["rost", "drift", "manuskript/kapitel-01.md"]) == 0
    assert "För lite underlag" in capsys.readouterr().out
