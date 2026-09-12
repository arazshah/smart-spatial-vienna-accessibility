# Downloading the Vienna source data

Run each query in [Overpass Turbo](https://overpass-turbo.eu/) (Run ▶,
then Export ▸ GeoJSON ▸ save). Requires a normal internet connection - not
available from a network-restricted session.

## 1. District boundaries (23 *Gemeindebezirke*)

```
[out:json][timeout:60];
area["name"="Wien"]["boundary"="administrative"]["admin_level"="4"]->.vienna;
relation["boundary"="administrative"]["admin_level"="9"](area.vienna);
out geom;
```

Save as `data/raw/districts.geojson`. Expect 23 relations.

## 2. Metro (U-Bahn) stations

```
[out:json][timeout:60];
area["name"="Wien"]["boundary"="administrative"]["admin_level"="4"]->.vienna;
node["railway"="station"]["station"="subway"](area.vienna);
out geom;
```

Save as `data/raw/metro.geojson`.

## 3. Schools

```
[out:json][timeout:60];
area["name"="Wien"]["boundary"="administrative"]["admin_level"="4"]->.vienna;
node["amenity"="school"](area.vienna);
out geom;
```

Save as `data/raw/schools.geojson`. This returns several hundred points;
`notebooks/01_data_and_problem.ipynb` is where any filtering (e.g. by
`isced:level` if we decide to restrict to a specific school type) happens
— keep the raw export unfiltered.

## 4. Parks

```
[out:json][timeout:60];
area["name"="Wien"]["boundary"="administrative"]["admin_level"="4"]->.vienna;
way["leisure"="park"](area.vienna);
out geom;
```

Save as `data/raw/parks.geojson`. Ways, not nodes - `nearest_neighbor`
needs point geometry, so these get reduced to centroids in the processing
notebook.

## Cross-check for district boundaries

Vienna's official open data portal (https://data.wien.gv.at) publishes
authoritative *Bezirksgrenzen*. If the OSM boundaries above look
imprecise for any district when plotted, search the portal for that
dataset and compare — do this manually, the exact dataset URL isn't
assumed here (see `data/README.md`).
