"""Builds assets/img/world-map.svg (clickable countries, grouped by continent) and assets/data/countries.json
from Natural Earth 1:50m countries (public domain). Run once; output is committed.

Usage: python tools/make_world_map.py <path to ne_50m_admin_0_countries.geojson>
"""
import json
import math
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
W, H = 1000, 500
CONTINENTS = {"Africa": "africa", "Asia": "asia", "Europe": "europe", "North America": "north-america",
              "South America": "south-america", "Oceania": "oceania"}


def project(lon, lat):
    """Equirectangular, cropped to 60S-84N so the map isn't mostly Antarctica."""
    x = (lon + 180) / 360 * W
    y = (84 - lat) / 144 * H
    return x, y


def simplify(ring, tol=1.8):
    """Drops points closer than `tol` px to the last kept one - keeps the file small."""
    out = [ring[0]]
    for p in ring[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) >= tol:
            out.append(p)
    return out if len(out) >= 4 else []


def path_d(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    parts = []
    for poly in polys:
        for ring in poly[:1]:                      # outer rings only - holes are invisible at this size
            pts = simplify([project(lon, max(-60, lat)) for lon, lat in ring])
            if pts:
                parts.append("M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z")
    if not parts:                                  # tiny island nations (Samoa, Tonga...) become a clickable dot
        ring = polys[0][0]
        x, y = project(sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))
        parts.append(f"M{x - 3:.1f},{y:.1f}a3,3 0 1,0 6,0a3,3 0 1,0 -6,0Z")
    return "".join(parts)


def main(src):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    paths, countries = {k: [] for k in CONTINENTS.values()}, []
    for f in data["features"]:
        p = f["properties"]
        cont = CONTINENTS.get(p.get("CONTINENT"))
        if not cont:
            continue
        name = p.get("NAME_EN") or p.get("NAME")
        code = (p.get("ADM0_A3") or p.get("ISO_A3")).lower()
        d = path_d(f["geometry"])
        if not d:
            continue
        paths[cont].append(f'<path id="c-{code}" data-name="{name}" d="{d}"/>')
        countries.append({"code": code, "name": name, "continent": cont})
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="World map - choose a continent or country">']
    for cont, items in paths.items():
        svg.append(f'<g class="continent" data-continent="{cont}">' + "".join(items) + "</g>")
    svg.append("</svg>")
    (SITE / "assets" / "img").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "img" / "world-map.svg").write_text("".join(svg), encoding="utf-8")
    countries.sort(key=lambda c: c["name"])
    (SITE / "assets" / "data" / "countries.json").write_text(json.dumps(countries, ensure_ascii=False, indent=0),
                                                              encoding="utf-8")
    print(len(countries), "countries;", (SITE / "assets" / "img" / "world-map.svg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
