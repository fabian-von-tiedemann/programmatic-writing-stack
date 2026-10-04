"""Geometri för rutter: Googles polyline-format, avstånd, bäring och punkter längs en linje."""

from __future__ import annotations

import math

Punkt = tuple[float, float]  # (lat, lng) i grader
JORDRADIE_M = 6_371_000.0
VADERSTRECK = ("norr", "nordost", "öst", "sydost", "söder", "sydväst", "väst", "nordväst")


def avkoda_polyline(text: str) -> list[Punkt]:
    """Googles Encoded Polyline Algorithm Format."""
    punkter: list[Punkt] = []
    i = lat = lng = 0
    while i < len(text):
        delta = []
        for _ in range(2):
            skift = resultat = 0
            while True:
                if i >= len(text):
                    raise ValueError("trasig polyline")
                b = ord(text[i]) - 63
                i += 1
                resultat |= (b & 0x1F) << skift
                skift += 5
                if b < 0x20:
                    break
            delta.append(~(resultat >> 1) if resultat & 1 else resultat >> 1)
        lat += delta[0]
        lng += delta[1]
        punkter.append((lat / 1e5, lng / 1e5))
    return punkter


def avstand_m(a: Punkt, b: Punkt) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * JORDRADIE_M * math.asin(math.sqrt(h))


def baring(a: Punkt, b: Punkt) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return math.degrees(math.atan2(y, x)) % 360


def punkter_langs(linje: list[Punkt], mellanrum: float, antal: int) -> list[tuple[Punkt, float, float]]:
    """Punkter var `mellanrum` meter, högst `antal` (då jämnt spridda). Start och mål är alltid med.
    Blickriktningen är framåt längs linjen."""
    if not linje:
        return []
    kum = [0.0]
    for a, b in zip(linje, linje[1:]):
        kum.append(kum[-1] + avstand_m(a, b))
    total = kum[-1]
    if total == 0:
        return [(linje[0], 0.0, 0.0)]
    mal = [k * mellanrum for k in range(int(total // mellanrum) + 1)]
    if total - mal[-1] > 1:
        mal.append(total)
    if len(mal) > antal:
        mal = [total * k / (antal - 1) for k in range(antal)] if antal > 1 else [0.0]
    ut = []
    i = 0
    for t in mal:
        while i < len(linje) - 2 and kum[i + 1] < t:
            i += 1
        j = i
        while j < len(linje) - 2 and kum[j + 1] == kum[j]:
            j += 1
        langd = kum[i + 1] - kum[i]
        andel = (t - kum[i]) / langd if langd else 0.0
        a, b = linje[i], linje[i + 1]
        punkt = (a[0] + (b[0] - a[0]) * andel, a[1] + (b[1] - a[1]) * andel)
        ut.append((punkt, t, baring(linje[j], linje[j + 1])))
    return ut


def vaderstreck(grader: float) -> str:
    return VADERSTRECK[int((grader % 360 + 22.5) // 45) % 8]
