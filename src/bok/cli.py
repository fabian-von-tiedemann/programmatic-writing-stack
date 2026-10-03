"""Kommandoraden: bok <kommando>."""

from __future__ import annotations

import argparse
import sys

from bok import __version__
from bok.rot import BokFel


def _moduler() -> list:
    from bok import graf, init, mallar

    return [init, mallar, graf]


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


def run() -> None:
    sys.exit(main())
