# Data

Nothing under `data/` is committed as raw source data (see
`.gitignore` — `data/raw/` is excluded). This file is the record of where
it comes from and how to regenerate it; `data/processed/` (small, derived
GeoJSON actually fed into the system) *is* committed once phase 1
produces it.

## Sources

All three amenity layers plus the district boundaries come from
OpenStreetMap via the [Overpass API](https://overpass-api.de/), run
through [Overpass Turbo](https://overpass-turbo.eu/) in a browser and
exported as GeoJSON. See `scripts/download_vienna_data.md` for the exact
queries.

| Layer | Source | OSM tags |
|---|---|---|
| District boundaries (23 *Gemeindebezirke*) | OSM via Overpass | `boundary=administrative`, `admin_level=9`, within Vienna (`admin_level=4`) |
| Metro (U-Bahn) stations | OSM via Overpass | `railway=station`, `station=subway` |
| Schools | OSM via Overpass | `amenity=school` |
| Parks | OSM via Overpass | `leisure=park` |

An alternative/cross-check source for the district boundaries specifically
is Vienna's official open data portal
([data.wien.gv.at](https://data.wien.gv.at)), which publishes authoritative
*Bezirksgrenzen* — use it if the OSM boundaries look imprecise for any
district; the exact dataset name and export link should be confirmed on
the portal directly rather than assumed here.

## Regenerating `data/processed/`

1. Run the Overpass queries in `scripts/download_vienna_data.md`, save
   each result under `data/raw/<layer>.geojson`.
2. Run `notebooks/01_data_and_problem.ipynb` end to end — it reads
   `data/raw/`, does the minimal cleaning (dropping features with null
   geometry, reprojecting to check validity, keeping only the fields the
   analysis needs), and writes `data/processed/`.

## License

OpenStreetMap data is © OpenStreetMap contributors, available under the
[Open Database License (ODbL)](https://www.openstreetmap.org/copyright).
Any output derived from it and redistributed here (`data/processed/`)
carries the same attribution requirement — retained in each processed
file's metadata and repeated here for the paper's Data Availability
section.
