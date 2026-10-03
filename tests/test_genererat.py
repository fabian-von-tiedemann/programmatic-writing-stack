from pathlib import Path

from bok.genererat import render, version_of, write_generated


def test_render_utan_frontmatter():
    out = render("# Hej\n", "2.0.0")
    assert out.startswith("<!-- bok-version: 2.0.0 ")
    assert out.endswith("\n# Hej\n")


def test_render_lagger_huvudet_efter_frontmatter():
    out = render("---\nname: x\n---\n\n# Hej\n", "2.0.0")
    assert out.startswith("---\nname: x\n---\n<!-- bok-version: 2.0.0 ")
    assert version_of(out) == "2.0.0"


def test_version_of_utan_huvud():
    assert version_of("# Hej\n") is None


def test_skapar_fil(tmp_path):
    msg = write_generated(tmp_path, Path(".claude/bok/a.md"), "A\n", "2.0.0")
    assert msg == "Skapade .claude/bok/a.md."
    assert (tmp_path / ".claude/bok/a.md").read_text().endswith("A\n")


def test_samma_version_ror_inget(tmp_path):
    write_generated(tmp_path, Path("a.md"), "A\n", "2.0.0")
    assert write_generated(tmp_path, Path("a.md"), "B\n", "2.0.0") is None
    assert (tmp_path / "a.md").read_text().endswith("A\n")


def test_aldre_version_uppgraderas(tmp_path):
    write_generated(tmp_path, Path("a.md"), "A\n", "1.0.0")
    msg = write_generated(tmp_path, Path("a.md"), "B\n", "2.0.0")
    assert msg == "Uppgraderade a.md (1.0.0 → 2.0.0)."
    assert (tmp_path / "a.md").read_text().endswith("B\n")


def test_nyare_version_nedgraderas_inte(tmp_path):
    write_generated(tmp_path, Path("a.md"), "A\n", "3.0.0")
    assert write_generated(tmp_path, Path("a.md"), "B\n", "2.0.0") is None


def test_fil_utan_huvud_lamnas(tmp_path):
    (tmp_path / "a.md").write_text("egen\n")
    msg = write_generated(tmp_path, Path("a.md"), "B\n", "2.0.0")
    assert msg.startswith("VARNING: a.md")
    assert (tmp_path / "a.md").read_text() == "egen\n"
