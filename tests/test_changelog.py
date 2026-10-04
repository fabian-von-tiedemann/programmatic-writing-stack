import importlib.util
import re
from pathlib import Path

from bok import __version__

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

_spec = importlib.util.spec_from_file_location("changelog", ROOT / "scripts" / "changelog.py")
changelog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(changelog)


def test_unreleased_finns_overst():
    rubriker = re.findall(r"(?m)^## \[([^\]]+)\]", CHANGELOG)
    assert rubriker[0] == "Unreleased"


def test_aktuell_version_har_ett_avsnitt():
    assert changelog.avsnitt(CHANGELOG, __version__), f"CHANGELOG saknar avsnittet [{__version__}]"


def test_varje_version_har_lank():
    versioner = re.findall(r"(?m)^## \[([^\]]+)\]", CHANGELOG)
    for v in versioner:
        assert re.search(rf"(?m)^\[{re.escape(v)}\]: https://", CHANGELOG), f"länk saknas för [{v}]"


def test_avsnitt_extraheras():
    text = "# CHANGELOG\n\n## [Unreleased]\n\n## [1.1.0] — 2026-01-02\n\n### Lagt till\n- A\n\n## [1.0.0] — 2026-01-01\n\n- B\n\n[1.1.0]: https://x\n"
    assert changelog.avsnitt(text, "1.1.0") == "### Lagt till\n- A"
    assert changelog.avsnitt(text, "1.0.0") == "- B"
    assert changelog.avsnitt(text, "9.9.9") is None
