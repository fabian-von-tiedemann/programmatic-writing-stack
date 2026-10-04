import subprocess
import tomllib

import pytest

from bok import __version__
from bok.boktoml import BokTomlFel
from bok.cli import main
from bok.init import init_repo
from bok.rot import BokFel
from helpers import skriv


def _alla_filer(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and ".git" not in p.parts
    }


def test_tom_mapp(tmp_path):
    root = tmp_path / "ny"
    actions = init_repo(root, titel="Testbok", git=False)
    assert tomllib.loads((root / "bok.toml").read_text())["bok"]["titel"] == "Testbok"
    for rel in [
        "bok/koncept/premiss.md",
        "bok/karaktarer/MALL.md",
        "bok/plot/kapitel/MALL.md",
        "bok/stil/rost.md",
        "bok/story-graph/threads.json",
        "bok/canon.md",
        "manuskript/README.md",
        "inkorg/README.md",
    ]:
        assert (root / rel).is_file(), rel
    skill = (root / ".claude/skills/bok/SKILL.md").read_text()
    assert f"<!-- bok-version: {__version__} " in skill
    claude = (root / "CLAUDE.md").read_text()
    assert claude.startswith("# Testbok\n")
    assert claude.count("<!-- bok:start -->") == 1
    assert any(a.startswith("Skapade ") and "filer för boken" in a for a in actions)


def test_tva_korningar_andrar_inget(tmp_path):
    root = tmp_path / "ny"
    init_repo(root, titel="Testbok", git=False)
    fore = _alla_filer(root)
    assert init_repo(root, git=False) == []
    assert _alla_filer(root) == fore


def test_befintlig_claude_md_far_bara_blocket(tmp_path):
    skriv(tmp_path, "CLAUDE.md", "# Mitt repo\n\nEgen text\n")
    init_repo(tmp_path, titel="X", git=False)
    init_repo(tmp_path, git=False)
    text = (tmp_path / "CLAUDE.md").read_text()
    assert text.startswith("# Mitt repo\n\nEgen text\n")
    assert text.count("<!-- bok:start -->") == 1


def test_blocket_aterstalls_men_resten_ror_inte(tmp_path):
    init_repo(tmp_path, titel="X", git=False)
    path = tmp_path / "CLAUDE.md"
    text = path.read_text()
    start = text.index("<!-- bok:start -->") + len("<!-- bok:start -->")
    end = text.index("<!-- bok:end -->")
    path.write_text(text[:start] + "\nförstört\n" + text[end:] + "\nMin regel\n")
    init_repo(tmp_path, git=False)
    ny = path.read_text()
    assert "förstört" not in ny
    assert ny.endswith("\nMin regel\n")


def test_bokens_filer_skrivs_aldrig_over(tmp_path):
    init_repo(tmp_path, titel="X", git=False)
    skriv(tmp_path, "bok/koncept/premiss.md", "Min premiss\n")
    init_repo(tmp_path, git=False)
    assert (tmp_path / "bok/koncept/premiss.md").read_text() == "Min premiss\n"


def test_aldre_genererad_fil_uppgraderas(tmp_path):
    init_repo(tmp_path, titel="X", git=False)
    path = tmp_path / ".claude/skills/bok/SKILL.md"
    path.write_text(path.read_text().replace(f"bok-version: {__version__}", "bok-version: 1.0.0"))
    actions = init_repo(tmp_path, git=False)
    assert f"bok-version: {__version__}" in path.read_text()
    assert any(a.startswith("Uppgraderade .claude/skills/bok/SKILL.md") for a in actions)


def test_handredigerad_genererad_fil_lamnas(tmp_path):
    skriv(tmp_path, ".claude/skills/bok/SKILL.md", "egen\n")
    actions = init_repo(tmp_path, titel="X", git=False)
    assert (tmp_path / ".claude/skills/bok/SKILL.md").read_text() == "egen\n"
    assert any(a.startswith("VARNING: .claude/skills/bok/SKILL.md") for a in actions)


def test_andra_agenter_ror_inte(tmp_path):
    skriv(tmp_path, ".claude/agents/granskare.md", "min agent\n")
    init_repo(tmp_path, titel="X", git=False)
    assert (tmp_path / ".claude/agents/granskare.md").read_text() == "min agent\n"


def test_ogiltig_boktoml_avbryter_innan_skrivning(tmp_path):
    skriv(tmp_path, "bok.toml", "[bok\n")
    with pytest.raises(BokTomlFel):
        init_repo(tmp_path, git=False)
    assert not (tmp_path / "bok").exists()


def test_titel_med_aao_och_citattecken(tmp_path):
    root = tmp_path / "Min bok"
    init_repo(root, titel='Hösten på "Ön"', git=False)
    assert tomllib.loads((root / "bok.toml").read_text())["bok"]["titel"] == 'Hösten på "Ön"'
    assert (root / "CLAUDE.md").read_text().startswith('# Hösten på "Ön"\n')


def test_titel_far_mappnamnet_som_standard(tmp_path):
    root = tmp_path / "skogen"
    init_repo(root, git=False)
    assert tomllib.loads((root / "bok.toml").read_text())["bok"]["titel"] == "skogen"


@pytest.fixture
def git_env(monkeypatch):
    for key in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(key, "Test")
    for key in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(key, "test@example.com")


def test_git_init_och_forsta_commit(tmp_path, git_env):
    root = tmp_path / "ny"
    actions = init_repo(root, titel="X")
    log = subprocess.run(["git", "log", "--oneline"], cwd=root, capture_output=True, text=True)
    assert log.stdout.count("\n") == 1
    assert "Initierade git och gjorde första commit." in actions
    gren = subprocess.run(["git", "symbolic-ref", "--short", "HEAD"], cwd=root, capture_output=True, text=True)
    assert gren.stdout.strip() == "main"


def test_befintligt_repo_far_ingen_commit(tmp_path, git_env):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    init_repo(tmp_path, titel="X")
    log = subprocess.run(["git", "log", "--oneline"], cwd=tmp_path, capture_output=True, text=True)
    assert log.stdout == ""


def test_cli_init(tmp_path, capsys):
    assert main(["init", str(tmp_path / "b"), "--titel", "X", "--no-git"]) == 0
    assert "Klart." in capsys.readouterr().out


@pytest.mark.parametrize(
    "text",
    [
        "# Mitt\n<!-- bok:start -->\nhalv\n\nMin regel\n",
        "# Mitt\n<!-- bok:end -->\nMin regel\n<!-- bok:start -->\n",
        "# Mitt\n<!-- bok:start -->\na\n<!-- bok:start -->\nMin regel\n<!-- bok:end -->\n",
        "# Mitt\n<!-- bok:start -->\na\n<!-- bok:end -->\nMin regel\n<!-- bok:end -->\n",
        "# Mitt\nMin regel\n<!-- bok:end -->\n",
    ],
)
def test_trasigt_block_avbryter_utan_att_skriva(tmp_path, text):
    path = skriv(tmp_path, "CLAUDE.md", text)
    with pytest.raises(BokFel, match="trasigt bok-block"):
        init_repo(tmp_path, titel="X", git=False)
    assert path.read_text() == text
    assert not (tmp_path / "bok").exists()
    assert not (tmp_path / "bok.toml").exists()


def test_init_i_en_undermapp_till_en_bok_avbryts(tmp_path):
    root = tmp_path / "bok"
    init_repo(root, titel="Testbok", git=False)
    under = root / "manuskript" / "ny"
    with pytest.raises(BokFel) as fel:
        init_repo(under, git=False)
    assert str(fel.value) == f"Mappen ligger redan i boken {root.resolve()}. Kör bok init där i stället."
    assert not under.exists()


def test_init_i_bokens_egen_mapp_uppgraderar(tmp_path):
    root = tmp_path / "bok"
    init_repo(root, titel="Testbok", git=False)
    assert init_repo(root, git=False) == []


def test_tillstand_for_claude_code(tmp_path):
    import json
    init_repo(tmp_path, titel="X", git=False)
    allow = json.loads((tmp_path / ".claude/settings.json").read_text())["permissions"]["allow"]
    assert "Bash(bok:*)" in allow and "Bash(git commit:*)" in allow


def test_befintliga_installningar_behalls(tmp_path):
    import json
    skriv(tmp_path, ".claude/settings.json",
          json.dumps({"model": "opus", "permissions": {"allow": ["Bash(ls:*)"], "deny": ["Bash(rm:*)"]}}))
    init_repo(tmp_path, titel="X", git=False)
    data = json.loads((tmp_path / ".claude/settings.json").read_text())
    assert data["model"] == "opus"
    assert data["permissions"]["deny"] == ["Bash(rm:*)"]
    assert data["permissions"]["allow"][0] == "Bash(ls:*)"
    assert "Bash(bok:*)" in data["permissions"]["allow"]


def test_trasiga_installningar_lamnas(tmp_path):
    skriv(tmp_path, ".claude/settings.json", "{ inte json")
    actions = init_repo(tmp_path, titel="X", git=False)
    assert (tmp_path / ".claude/settings.json").read_text() == "{ inte json"
    assert any(a.startswith("VARNING: .claude/settings.json") for a in actions)


def test_installningar_som_lista_lamnas(tmp_path):
    skriv(tmp_path, ".claude/settings.json", "[]")
    actions = init_repo(tmp_path, titel="X", git=False)
    assert (tmp_path / ".claude/settings.json").read_text() == "[]"
    assert any(a.startswith("VARNING: .claude/settings.json") for a in actions)


def test_bokens_las_mig_for_forfattaren(tmp_path):
    init_repo(tmp_path, titel="X", git=False)
    text = (tmp_path / "README.md").read_text(encoding="utf-8")
    for fras in ("Var är vi?", "Gå igenom inkorgen", "uv tool upgrade bok", "bok forslag av"):
        assert fras in text, fras
    assert "{{" not in text


def test_befintlig_readme_rors_inte(tmp_path):
    skriv(tmp_path, "README.md", "# Mitt repo\n")
    init_repo(tmp_path, titel="X", git=False)
    assert (tmp_path / "README.md").read_text() == "# Mitt repo\n"


NYA_BOKFILER = ("bok/karaktarer/forlagor/README.md", "bok/karaktarer/forlagor/MALL.md",
                "bok/karaktarer/prov/README.md", "bok/vagval/README.md")


def test_uppgradering_skapar_nya_bokfiler_men_ror_inte_mallen(tmp_path):
    root = tmp_path / "bok"
    init_repo(root, titel="T", git=False)
    for rel in NYA_BOKFILER:
        (root / rel).unlink()
    (root / "bok/karaktarer/MALL.md").write_text("gammal mall\n", encoding="utf-8")
    init_repo(root, git=False)
    for rel in NYA_BOKFILER:
        assert (root / rel).is_file(), rel
    assert (root / "bok/karaktarer/MALL.md").read_text(encoding="utf-8") == "gammal mall\n"
