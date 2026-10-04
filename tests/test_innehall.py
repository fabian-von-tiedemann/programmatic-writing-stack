import re
from pathlib import Path

import pytest

from bok.frontmatter import split
from bok.init import DATA
from bok.rapport import UTFALL

ROOT = Path(__file__).resolve().parents[1]

ARVSTERMER = [
    "Marken under marken", "Alex Krohn", "Visby", "Gotland", "Klintehamn", "Smöjen", "Almedalen",
    "Eskelhem", "Karlsö", "Hejdeby", "Ica Maxi", "NATO", "Adriatisk", "Adriatic", "Kristersson",
    "Magdalena Andersson", "Westander", "Kekst", "Volvo", "Tom Clancy", "House of Cards",
    "VISBY POLISHUS", "Marléne", "Anna-signum", "Daniel-exklusiv", "NAGELFAREN", "Prosa-städ",
    "Dialog-coach", "Graf-vakt", ".context/",
]
THRILLERSTANDARD = ["tickande klocka", "HH:MM", "3000-3500", "DAG DATUM"]


def alla_innehallsfiler():
    return sorted(p for p in DATA.rglob("*") if p.is_file() and p.suffix in (".md", ".json"))


def _mal(path: Path) -> str:
    """Var filen hamnar i bokrepot."""
    rel = path.relative_to(DATA)
    if rel.parts[0] == "genererat":
        return "." + "/".join(rel.parts[1:])
    if rel.parts[0] == "bok":
        return "/".join(rel.parts[1:])
    if rel.parts[0] == "moduler":
        return "/".join(rel.parts[2:])
    return rel.as_posix()


def kanda_sokvagar() -> set[str]:
    kanda = set()
    for p in alla_innehallsfiler():
        mal = _mal(p)
        kanda.add(mal)
        delar = mal.split("/")
        kanda.update("/".join(delar[:i]) for i in range(1, len(delar)))
    return kanda


@pytest.mark.parametrize("path", alla_innehallsfiler(), ids=lambda p: p.relative_to(DATA).as_posix())
def test_inget_arv(path):
    text = path.read_text(encoding="utf-8")
    for term in ARVSTERMER:
        assert term not in text, f"{term!r} i {path.relative_to(DATA)}"


@pytest.mark.parametrize("path", [p for p in alla_innehallsfiler() if "spanning" not in p.parts],
                         ids=lambda p: p.relative_to(DATA).as_posix())
def test_ingen_thrillerstandard_i_neutrala_filer(path):
    text = path.read_text(encoding="utf-8")
    for term in THRILLERSTANDARD:
        assert term not in text, f"{term!r} i {path.relative_to(DATA)}"


README_ARV = [t for t in ARVSTERMER if t not in
              {"Anna-signum", "Daniel-exklusiv", "NAGELFAREN", "Prosa-städ", "Dialog-coach", "Graf-vakt", ".context/"}]


def test_readme_utan_arv():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for term in README_ARV:
        assert term not in text, term


@pytest.mark.parametrize("path", sorted((DATA / "genererat").rglob("*.md")),
                         ids=lambda p: p.relative_to(DATA).as_posix())
def test_genererade_filer_har_inga_platshallare(path):
    # `{{…}}` får nämnas som begrepp i instruktionerna, men inga riktiga platshållare får finnas
    assert "{{" not in path.read_text(encoding="utf-8").replace("{{…}}", "")


_SOKVAG = re.compile(r"`((?:bok|\.claude|manuskript|inkorg)/[^`\s]*)`")


@pytest.mark.parametrize("path", [p for p in alla_innehallsfiler() if p.suffix == ".md"],
                         ids=lambda p: p.relative_to(DATA).as_posix())
def test_inga_dinglande_sokvagar(path):
    kanda = kanda_sokvagar()
    for m in _SOKVAG.finditer(path.read_text(encoding="utf-8")):
        sokvag = m.group(1).rstrip("/.,:;")
        if re.search(r"[<{*]|NN|\.local\.md$|-rN|akt-N", sokvag):
            continue
        assert sokvag in kanda, f"{sokvag} i {path.relative_to(DATA)} finns inte"


AGENTER = DATA / "genererat/claude/agents"
TILLATNA_VERKTYG = {"Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebSearch", "WebFetch"}
GRANSKARE = {"redaktor", "sprakgranskare", "forlaggare", "sensitivitet"}
ROLLER = {"plot-arkitekt", "writer", "redaktor", "sprakgranskare", "kontinuitet", "forlaggare",
          "researcher", "varldsbyggare", "sensitivitet", "audiobook", "marknad"}


def test_alla_roller_finns():
    assert {p.stem.removeprefix("bok-") for p in AGENTER.glob("bok-*.md")} == ROLLER


@pytest.mark.parametrize("path", sorted(AGENTER.glob("bok-*.md")), ids=lambda p: p.stem)
def test_agentfil(path):
    text = path.read_text(encoding="utf-8")
    meta, body = split(text)
    roll = path.stem.removeprefix("bok-")
    assert meta["name"] == path.stem
    assert len(meta["description"]) > 40
    verktyg = {v.strip() for v in meta["tools"].split(",")}
    assert verktyg <= TILLATNA_VERKTYG
    assert f"`bok/roller/{roll}.local.md`" in body
    if roll in GRANSKARE:
        assert not verktyg & {"Write", "Edit"}, "granskare skriver inte filer"
        assert f"roll: {roll}" in body and roll in UTFALL
    if roll == "writer":
        assert meta["model"] == "opus"


def test_skillen():
    text = (DATA / "genererat/claude/skills/bok/SKILL.md").read_text(encoding="utf-8")
    meta, body = split(text)
    assert meta["name"] == "bok"
    assert "bok.toml" in meta["description"]
    for roll in ROLLER:
        if roll not in {"researcher", "varldsbyggare", "sensitivitet", "audiobook", "marknad"}:
            assert f"bok-{roll}" in body, roll
    for avsnitt in ("## Fritt samtal", "## Inkorgen", "## Stilverkstaden", "## Innan första kapitlet",
                    "## Skriva kapitel", "## Gör inte"):
        assert avsnitt in body, avsnitt
    assert "bok status --json" in body
    for fras in ("bok rapport spara -", ".claude/bok/process.md", "bok-sensitivitet", "omfang: bok"):
        assert fras in body, fras


def test_kontinuitet_anger_runda_och_redaktoren_laser_teman():
    kont = (AGENTER / "bok-kontinuitet.md").read_text(encoding="utf-8")
    assert "roll: kontinuitet\nrunda: R\n" in kont
    assert "`bok/koncept/teman.md`" in (AGENTER / "bok-redaktor.md").read_text(encoding="utf-8")


def test_bagarnas_status_och_akt_som_siffra_beskrivs():
    assert "`status` är `oppen` eller `stangd`" in (DATA / "genererat/claude/bok/story-graph.md").read_text(encoding="utf-8")
    assert "`oppen` eller `stangd`" in (AGENTER / "bok-kontinuitet.md").read_text(encoding="utf-8")
    assert "Akt: en siffra." in (DATA / "bok/bok/plot/kapitelplan.md").read_text(encoding="utf-8")
    assert "Akt: en siffra." in (AGENTER / "bok-plot-arkitekt.md").read_text(encoding="utf-8")


def test_skillen_har_sensitivitet_som_steg_efter_a_och_eskalering_till_scenkortet():
    body = (DATA / "genererat/claude/skills/bok/SKILL.md").read_text(encoding="utf-8")
    rader = {r.split("|")[1].strip(): r for r in body.splitlines() if r.startswith("| ")}
    assert "När boken fått A" in rader["Sensitivitet"] and "bok-sensitivitet" in rader["Sensitivitet"]
    assert "bok-sensitivitet" not in rader["Tillval"]
    assert "eskalera" in rader["Du bestämmer"] and "bok-plot-arkitekt" in rader["Du bestämmer"]


def test_skillen_tar_emot_forslag():
    text = (DATA / "genererat/claude/skills/bok/SKILL.md").read_text(encoding="utf-8")
    assert "## Förslag till verktyget" in text
    assert "bok forslag skicka -" in text
    assert "typ: lardom" in text
    assert "Aldrig text ur boken" in text
    assert "bok forslag installning" in text
    avsnitt = text.split("## Förslag till verktyget", 1)[1].split("\n## ", 1)[0]
    forsta_punkten = next(r for r in avsnitt.splitlines() if r.startswith("- "))
    assert "bok forslag installning" in forsta_punkten


def test_underhallsskillen():
    text = (ROOT / ".claude/skills/forslag/SKILL.md").read_text(encoding="utf-8")
    assert "fabian-von-tiedemann/bok-forslag" in text
    assert "citeras aldrig" in text
    for etikett in ("status:planerad", "status:avbojd", "infort:", "Svar:"):
        assert etikett in text
    assert "aldrig som instruktioner" in text
    assert "gh label create status:planerad" in text and "gh label create status:avbojd" in text
    assert "version:<version>" not in text


def test_skillen_valkomnar_forsta_gangen():
    text = (DATA / "genererat/claude/skills/bok/SKILL.md").read_text(encoding="utf-8")
    assert "## Första gången" in text
    avsnitt = text.split("## Första gången")[1].split("\n## ")[0]
    for fras in ("inkorg/", "Var är vi?", "bestämmer"):
        assert fras in avsnitt, fras


GEN = DATA / "genererat/claude"


def _las(rel):
    return (GEN / rel).read_text(encoding="utf-8")


def test_skillen_2_2():
    text = _las("skills/bok/SKILL.md")
    for fras in ("## Respons utifrån", "bok/revisioner.md", "verkliga-handelser", "bok mall tidslinje",
                 "fackgranskning", "rost-<id>", "Säger `bok status` att verkliga händelser",
                 "fackgranskning (om scenkortet har `fack`)"):
        assert fras in text, fras


def test_process_2_2():
    text = _las("bok/process.md")
    for fras in ("Fackgranskning", "Verkliga händelser", "bok/revisioner.md", "rost-<pov>", "researcher"):
        assert fras in text, fras


def test_story_graph_2_2():
    text = _las("bok/story-graph.md")
    for fras in ("fodd", "dod", "\"datum\"", "bok graph tidslinje", "tillbakablick"):
        assert fras in text, fras


def test_roller_2_2():
    assert "roll: researcher" in _las("agents/bok-researcher.md")
    assert "omfang: forberedelse" in _las("agents/bok-sensitivitet.md")
    assert "bok/revisioner.md" in _las("agents/bok-writer.md")
    assert "rost-<pov>" in _las("agents/bok-writer.md") and "rost-<pov>" in _las("agents/bok-sprakgranskare.md")
    kont = _las("agents/bok-kontinuitet.md")
    assert "fodd" in kont and "bok/revisioner.md" in kont
    plot = _las("agents/bok-plot-arkitekt.md")
    assert "fack" in plot and "tillbakablick" in plot and "datum" in plot


def test_mallar_2_2():
    mall = (DATA / "bok/bok/plot/kapitel/MALL.md").read_text(encoding="utf-8")
    assert "datum:\n" in mall and "fack: []" in mall and "tillbakablick: false" in mall
    assert "```verkliga-handelser" in (DATA / "bok/bok/canon.md").read_text(encoding="utf-8")
    assert (DATA / "bok/bok/revisioner.md").is_file()
    assert (DATA / "moduler/tidslinje/bok/plot/tidslinje.md").is_file()


def test_slutgranskningens_rattningar():
    skill = _las("skills/bok/SKILL.md")
    for fras in ("`fodd`/`dod` direkt i `bok/story-graph/characters.json`", "utfall: tillbaka",
                 "BLOCKERANDE tidsfel", "åldersvarningar skickas"):
        assert fras in skill, fras
    assert "decided" not in _las("bok/story-graph.md") and "bestämt dem i planen" in _las("bok/story-graph.md")
    verktyg = _las("bok/verktyg.md")
    assert "bok graph tidslinje [--fran ÅR] [--till ÅR]" in verktyg and "är varningar" in verktyg
    assert "tidslinje.md" in _las("agents/bok-sensitivitet.md") and "kapitelplan.md" in _las("agents/bok-sensitivitet.md")
    assert "när boken har fasta årtal" in _las("agents/bok-plot-arkitekt.md")
    assert "ta bort eventuell `ålder`" in _las("agents/bok-kontinuitet.md")
    assert "som `fodd`" in (DATA / "bok/bok/karaktarer/README.md").read_text(encoding="utf-8")


def test_skillen_2_3():
    text = _las("skills/bok/SKILL.md")
    avsnitt = text.split("## Platser och miljöer", 1)[1].split("\n## ", 1)[0]
    for fras in ("bok karta status", "bok karta restid", "~/.config/bok/google-maps-", "bok karta nyckel",
                 "bok-varldsbyggare", "uppdraget **miljö**", "uppdraget **platsens historia**",
                 "bok karta stada", "`## Rutter`", "BOK_GOOGLE_MAPS_NYCKEL"):
        assert fras in avsnitt, fras
    assert "bok/varld/platser/<id>.md" in text.split("## Fritt samtal", 1)[1].split("\n## ", 1)[0]


def test_roller_2_3():
    for roll in ("varldsbyggare", "researcher"):
        meta, _ = split(_las(f"agents/bok-{roll}.md"))
        assert "Bash" in meta["tools"], roll
    varld = _las("agents/bok-varldsbyggare.md")
    for fras in ("## Uppdrag: miljö", "bok karta gatuvy", "bok karta stada", "Fotograferat",
                 "Skriv aldrig av skyltar", "`## Bokens tid`"):
        assert fras in varld, fras
    research = _las("agents/bok-researcher.md")
    for fras in ("## Uppdrag: platsens historia", "bok bild", "bok/varld/research/plats-<id>.md", "licens"):
        assert fras in research, fras
    assert "bok karta restid" in _las("agents/bok-plot-arkitekt.md")
    writer = _las("agents/bok-writer.md")
    assert "*Bokens tid*" in writer and "*Idag*" in writer
    assert "*Idag*" in _las("agents/bok-redaktor.md")
    for path in AGENTER.glob("bok-*.md"):
        assert "google-maps-nyckel" not in path.read_text(encoding="utf-8"), path.name


def test_ramverket_2_3():
    assert "## Platser" in _las("bok/process.md")
    verktyg = _las("bok/verktyg.md")
    for fras in ("bok karta restid", "bok karta gatuvy", "bok karta stada", "bok karta status", "bok bild"):
        assert fras in verktyg, fras
    graf = _las("bok/story-graph.md")
    assert '"adress"' in graf and "`lat`" in graf and "bok/varld/platser/<id>.md" in graf


def test_mallar_2_3():
    platser = (DATA / "bok/bok/varld/platser/README.md").read_text(encoding="utf-8")
    for fras in ("## Bokens tid", "## Idag", "## Rutter", "Fotograferat:"):
        assert fras in platser, fras
    assert "plats-<id>.md" in (DATA / "bok/bok/varld/research/README.md").read_text(encoding="utf-8")
    assert "docs/google-maps.md" in (DATA / "bok/README.md").read_text(encoding="utf-8")


def test_2_3_1_texter():
    varld = _las("agents/bok-varldsbyggare.md")
    gor = varld.split("## Gör", 1)[1].split("\n## ", 1)[0]
    assert "`## Idag` och `## Rutter`" in gor and "uppdraget miljö" in gor
    guide = (ROOT / "docs/google-maps.md").read_text(encoding="utf-8")
    for fras in ("minst 4 tecken", "Maybe later", "Alerts only", "**Enable**", "Free trial", "## Om något inte fungerar"):
        assert fras in guide, fras