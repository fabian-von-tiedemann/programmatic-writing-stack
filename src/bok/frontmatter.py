"""Frontmatter överst i markdown: en liten, förutsägbar delmängd av YAML.

Stöder `nyckel: värde` per rad med heltal, decimaltal, true/false, text,
listor `[a, "b, c"]` och dictar `{a: 8, b: 7}`. Värden som börjar med `{{`
är oifyllda platshållare och lämnas som text."""

from __future__ import annotations

from bok.rot import BokFel


class FrontmatterFel(BokFel):
    pass


def split(text: str) -> tuple[dict, str]:
    normal = text.lstrip("﻿").replace("\r\n", "\n")
    s = normal.lstrip()
    if not s.startswith("---\n"):
        return {}, normal
    end = s.find("\n---\n", 3)
    if end != -1:
        head, body = s[4:end], s[end + 5 :]
    elif s.endswith("\n---"):
        head, body = s[4:-4], ""
    else:
        raise FrontmatterFel("Frontmatter saknar avslutande '---'.")
    return parse(head), body


def parse(head: str) -> dict:
    out: dict = {}
    for n, raw in enumerate(head.splitlines(), 1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")) or ":" not in line:
            raise FrontmatterFel(f"Rad {n}: förväntade 'nyckel: värde', fick {raw!r}.")
        key, _, value = line.partition(":")
        out[key.strip()] = _value(value.strip(), n)
    return out


def _value(s: str, n: int):
    if s == "":
        return None
    if s.startswith("{{"):
        return s
    if s.startswith("["):
        if not s.endswith("]"):
            raise FrontmatterFel(f"Rad {n}: listan saknar ']'.")
        inner = s[1:-1].strip()
        return [_scalar(x) for x in _items(inner, n)] if inner else []
    if s.startswith("{"):
        if not s.endswith("}"):
            raise FrontmatterFel(f"Rad {n}: saknar '}}'.")
        out = {}
        for item in _items(s[1:-1].strip(), n):
            k, sep, v = item.partition(":")
            if not sep:
                raise FrontmatterFel(f"Rad {n}: {item!r} saknar ':'.")
            out[k.strip()] = _scalar(v.strip())
        return out
    return _scalar(s)


def _items(s: str, n: int) -> list[str]:
    items, cur, quote = [], [], None
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            cur.append(ch)
        elif ch == ",":
            items.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if quote:
        raise FrontmatterFel(f"Rad {n}: citattecken som inte stängs.")
    last = "".join(cur).strip()
    if last:
        items.append(last)
    return items


def _scalar(s: str):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    for typ in (int, float):
        try:
            return typ(s)
        except ValueError:
            pass
    return s
