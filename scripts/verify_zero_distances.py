"""
Independent sanity check for a question raised while reviewing
results/rule_based_ranking.csv: distance_to_school_m and
distance_to_park_m are exactly 0.0 for all 23 districts, and
distance_to_metro_m is 0.0 for 21 of 23 (only Waehring and Hernals are
nonzero). Is that a real result, or a bug in how distances are computed?

This script answers that independently of smart_spatial_system's own
distance-calculation code (plugins/distance_calculator.py,
plugins/nearest_neighbor.py): it re-implements point-in-polygon from
scratch (a different ray-casting implementation, not a copy) and applies
it directly to the committed data/processed/*.geojson files, with no
shared code path with the library under test.

Usage:
    python3 scripts/verify_zero_distances.py

Expected output (matches results/rule_based_ranking.csv exactly):
    - 0/23 districts have zero schools inside their polygon
    - 0/23 districts have zero parks inside their polygon
    - exactly 2/23 districts (Waehring, Hernals) have zero metro
      stations inside their polygon

A point inside a polygon has geometric distance 0.0 to it - both
shapely's Geometry.distance() (used when available) and
distance_calculator.py's own pure-python fallback return 0.0 in that
case, which is standard GIS behaviour, not a shortcut or a bug. Vienna's
211 schools and 1063 parks average ~9 and ~46 per district respectively,
so "every district contains at least one of each" is expected; its 109
metro stations are sparse enough that two districts (both small,
inner-ring) contain none, which is exactly what makes their accessibility
score (99.2 instead of the tied 100.0) the only source of variation in
the rule-based ranking. See claude/phase-3-rule-based-arm.md for the
methodological discussion this motivates (a centroid- or
population-weighted distance would differentiate the top of the ranking
more than polygon-to-point does).
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def load_features(name: str) -> list[dict]:
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)["features"]


def _point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    """Standard ray-casting point-in-ring test."""
    n = len(ring)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y):
            x_intersect = (xj - xi) * (y - yi) / ((yj - yi) or 1e-15) + xi
            if x < x_intersect:
                inside = not inside
        j = i
    return inside


def point_in_polygon(x: float, y: float, geometry: dict) -> bool:
    """Point-in-polygon test supporting Polygon and MultiPolygon, with holes."""
    if geometry["type"] == "Polygon":
        rings_list = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        rings_list = geometry["coordinates"]
    else:
        return False

    for rings in rings_list:
        if not rings:
            continue
        outer, holes = rings[0], rings[1:]
        if not _point_in_ring(x, y, outer):
            continue
        if any(_point_in_ring(x, y, hole) for hole in holes):
            continue
        return True
    return False


def main() -> None:
    districts = load_features("districts.geojson")
    schools = load_features("schools.geojson")
    parks = load_features("parks.geojson")
    metro = load_features("metro.geojson")

    header = f"{'district':<25} {'#schools':>10} {'#parks':>10} {'#metro':>10}"
    print(header)
    print("-" * len(header))

    zero_schools = zero_parks = zero_metro = 0
    for d in districts:
        name = d["properties"]["name"]
        geom = d["geometry"]
        n_schools = sum(
            1 for s in schools if point_in_polygon(*s["geometry"]["coordinates"], geom)
        )
        n_parks = sum(
            1 for p in parks if point_in_polygon(*p["geometry"]["coordinates"], geom)
        )
        n_metro = sum(
            1 for m in metro if point_in_polygon(*m["geometry"]["coordinates"], geom)
        )
        print(f"{name:<25} {n_schools:>10} {n_parks:>10} {n_metro:>10}")
        zero_schools += n_schools == 0
        zero_parks += n_parks == 0
        zero_metro += n_metro == 0

    print()
    print(f"districts with ZERO schools inside: {zero_schools}/{len(districts)}")
    print(f"districts with ZERO parks inside:   {zero_parks}/{len(districts)}")
    print(f"districts with ZERO metro inside:   {zero_metro}/{len(districts)}")


if __name__ == "__main__":
    main()
