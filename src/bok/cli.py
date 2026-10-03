"""Kommandoraden: bok <kommando>."""

from __future__ import annotations

import argparse
import sys

from bok import __version__
from bok.rot import BokFel


def _moduler() -> list:
    from bok import annotations, graf, init, mallar, rapport, status, tics, validera

    return [init, status, mallar, graf, tics, validera, rapport, annotations]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bok", description="Skrivharness för romaner i Claude Code."
    )
    parser.add_argument("--version", action="version", version=f"bok {__version__}")
    sub = parser.add_subparsers(dest="kommando", metavar="<kommando>")
    for modul in _moduler():
        modul.register(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0
    try:
        return func(args) or 0
    except BokFel as exc:
        print(f"bok: {exc}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("bok: en fil är inte sparad som UTF-8. Spara om den som UTF-8 och försök igen.", file=sys.stderr)
        return 2
    except OSError as exc:
        var = f" {exc.filename}" if exc.filename else " en fil"
        print(f"bok: kunde inte läsa eller skriva{var}: {exc.strerror or exc}", file=sys.stderr)
        return 2


def run() -> None:
    sys.exit(main())
