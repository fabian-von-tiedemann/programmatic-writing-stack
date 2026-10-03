"""bok init: gör en mapp till ett bokrepo, eller uppgradera ramverket i det."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from bok import __version__, boktoml
from bok.genererat import write_generated
from bok.rot import MARKER, BokFel

DATA = Path(__file__).parent / "data"
BLOCK_START = "<!-- bok:start -->"
BLOCK_END = "<!-- bok:end -->"


def _generated_files():
    base = DATA / "genererat"
    for src in sorted(base.rglob("*.md")):
        rel = src.relative_to(base)
        yield Path("." + rel.parts[0], *rel.parts[1:]), src.read_text(encoding="utf-8")


def _book_files():
    base = DATA / "bok"
    for src in sorted(p for p in base.rglob("*") if p.is_file()):
        yield src.relative_to(base), src


def _block() -> str:
    body = (DATA / "claude-block.md").read_text(encoding="utf-8").strip()
    return f"{BLOCK_START}\n{body}\n{BLOCK_END}"


def _check_claude_md(root: Path) -> None:
    path = root / "CLAUDE.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    starter, slut = text.count(BLOCK_START), text.count(BLOCK_END)
    if (starter, slut) == (0, 0):
        return
    if (starter, slut) != (1, 1) or text.find(BLOCK_END) < text.find(BLOCK_START):
        raise BokFel(
            f"CLAUDE.md har ett trasigt bok-block ({BLOCK_START} och {BLOCK_END} måste finnas "
            "en gång var, i den ordningen). Rätta filen och kör bok init igen."
        )


# Kommandon som skillen kör hela tiden; utan dem frågar Claude Code om lov vid varje steg.
TILLSTAND = (
    "Bash(bok:*)",
    "Bash(git add:*)",
    "Bash(git commit:*)",
)


def _ensure_settings(root: Path) -> str | None:
    path = root / ".claude" / "settings.json"
    rel = ".claude/settings.json"
    data: dict = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = None
        permissions = data.get("permissions", {}) if isinstance(data, dict) else None
        if not isinstance(permissions, dict) or not isinstance(permissions.get("allow", []), list):
            return f"VARNING: {rel} går inte att läsa som inställningar och lämnas orörd."
    allow = data.setdefault("permissions", {}).setdefault("allow", [])
    nya = [t for t in TILLSTAND if t not in allow]
    if not nya:
        return None
    allow.extend(nya)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"Tillät bok- och git-kommandon i {rel}."


def _ensure_claude_md(root: Path, titel: str) -> str | None:
    path = root / "CLAUDE.md"
    block = _block()
    if not path.exists():
        mall = (DATA / "claude-md.md").read_text(encoding="utf-8")
        path.write_text(
            mall.replace("{{BOK_TITEL}}", titel).replace("{{BOK_BLOCK}}", block), encoding="utf-8"
        )
        return "Skapade CLAUDE.md."
    text = path.read_text(encoding="utf-8")
    start = text.find(BLOCK_START)
    end = text.find(BLOCK_END, start) if start != -1 else -1
    if end != -1:
        new = text[:start] + block + text[end + len(BLOCK_END) :]
    else:
        new = text.rstrip("\n") + "\n\n" + block + "\n"
    if new == text:
        return None
    path.write_text(new, encoding="utf-8")
    return "Uppdaterade bok-blocket i CLAUDE.md."


def _in_git(root: Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], cwd=root, capture_output=True, text=True
        )
    except OSError:
        return False
    return r.returncode == 0 and r.stdout.strip() == "true"


def _git_init(root: Path) -> str:
    try:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        # `git init -b` kräver git 2.28; symbolic-ref fungerar överallt
        subprocess.run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=root, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "VARNING: git saknas eller git init misslyckades; mappen är inte versionshanterad."
    subprocess.run(["git", "add", "-A"], cwd=root, check=False)
    r = subprocess.run(["git", "commit", "-q", "-m", "bok init"], cwd=root, capture_output=True)
    if r.returncode != 0:
        return "Initierade git. Första commit misslyckades (är git user.name och user.email satta?)."
    return "Initierade git och gjorde första commit."


def init_repo(path: Path, titel: str | None = None, git: bool = True) -> list[str]:
    root = Path(path).resolve()
    for mapp in root.parents:
        if (mapp / MARKER).is_file():
            raise BokFel(f"Mappen ligger redan i boken {mapp}. Kör bok init där i stället.")
    root.mkdir(parents=True, exist_ok=True)
    toml = root / "bok.toml"
    befintlig = boktoml.read(root) if toml.exists() else None  # validerar innan något skrivs
    _check_claude_md(root)
    titel = titel or (befintlig or {}).get("titel") or root.name
    var_git = _in_git(root) if git else True
    actions: list[str] = []

    if befintlig is None:
        toml.write_text(boktoml.render_new(titel, __version__), encoding="utf-8")
        actions.append("Skapade bok.toml.")
    elif boktoml.set_ramverk(root, __version__):
        actions.append(f"Uppdaterade ramverksversionen i bok.toml till {__version__}.")

    skapade = 0
    for rel, src in _book_files():
        target = root / rel
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(src.read_bytes())
        skapade += 1
    if skapade:
        actions.append(f"Skapade {skapade} filer för boken (bok/, manuskript/, inkorg/).")

    if msg := _ensure_settings(root):
        actions.append(msg)

    if msg := _ensure_claude_md(root, titel):
        actions.append(msg)

    for rel, content in _generated_files():
        if msg := write_generated(root, rel, content, __version__):
            actions.append(msg)

    if any(a.startswith("Uppgraderade ") for a in actions):
        from bok import forslag

        actions += forslag.nyheter()

    if not var_git:
        actions.append(_git_init(root))
    return actions


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("init", help="gör en mapp till ett bokrepo, eller uppgradera ramverket")
    p.add_argument("mapp", nargs="?", default=".", help="bokens mapp (standard: den här)")
    p.add_argument("--titel", help="bokens arbetstitel (standard: mappens namn)")
    p.add_argument("--no-git", action="store_true", help="kör inte git init")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    for rad in init_repo(Path(args.mapp), titel=args.titel, git=not args.no_git):
        print(rad)
    print("Klart. Öppna mappen i Claude Code eller Conductor och berätta om din bok.")
    return 0
