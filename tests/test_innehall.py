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
