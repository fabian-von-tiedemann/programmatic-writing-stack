import re
from pathlib import Path

import pytest

from bok.init import DATA

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


@pytest.mark.xfail(reason="README skrivs om i Task 14", strict=True)
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
