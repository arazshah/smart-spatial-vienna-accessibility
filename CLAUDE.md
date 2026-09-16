# CLAUDE.md

Guidance for Claude Code when working in this repository. Read this first,
every session — it is written so a fresh session needs no re-briefing.

## What this is

A reproducibility case study built on [Smart Spatial System](https://github.com/arazshah/smart_spatial_system)
(a separate, independently-developed repository — **never edit its code
from here**; if a bug in it blocks this experiment, fix it in that repo,
release a new version there, then bump the pin in `requirements.txt` here).

Scoring Vienna's 23 municipal districts by accessibility to public
amenities (metro, schools, parks), comparing a **rule-based** query
planner (deterministic by construction) against an **LLM-backed** one
(same question, run N times) to measure how much the LLM's plan and
final ranking vary across runs. This is the experiment behind a paper —
see `paper/PLAN.md` for the working title and full phase plan, and
`paper/comparison_metric.md` for the exact three-layer metric (Plan
Agreement Rate, parametric variance, Rank Stability via pairwise Spearman
correlation) before writing any comparison code — don't re-derive it,
it was deliberately designed, not improvised.

## Current state

**Phases 1-3 are done and verified. Phase 4 has now had THREE consecutive
full N=20 runs (2026-09-12, 2026-09-13 x2) come back completely
DEGENERATE — three DIFFERENT root causes in a row. The first two are
fixed and CONFIRMED working (upstream `smart_spatial_system` 0.2.2
correctly chains distance ops now). The third (a CRS-mismatch bug) is
fixed locally, NOT YET RE-RUN.** All three degenerate batches are
preserved, don't touch any of them:
`results/llm_runs/diagnostic_2026-09-12_wiring_bug/`,
`diagnostic_2026-09-13_wiring_bug_round2/`, and
`diagnostic_2026-09-13_crs_mismatch_round3/`. `results/llm_runs/run_*.json`
(the live location) still holds the Round-3 CRS-mismatch batch and isn't
real phase-4 data until a run comes back with `degenerate_ranking: False`.
Full history in the project doc `claude/phase-4-llm-arm.md`. Check
`paper/PLAN.md`'s phase table to confirm before assuming, this file will
not be updated every session.

**Short version:** after two `smart_spatial_system` package bugs got fixed
upstream (0.2.1) and a local `extract_ranking()` bug got fixed here (both
2026-09-12), the full N=20 loop ran clean (`execution_success: True`,
20/20) but every run's `score_features` was wired to the *pre-distance*
sites vector, never to any actual distance computation — every score came
out 0.0. A generic hint didn't fix it (re-ran 2026-09-13, still 20/20
degenerate); a concrete hint grounded in
`results/rule_based_query_spec.json` was added as a local safety net, AND
the user (who maintains `smart_spatial_system` themselves) fixed the real
root cause upstream, releasing `0.2.2` (worked chaining example + a new
validation check — `claude/smart-spatial-system-upstream-bugs.md` Bug 4).
**Re-ran under 0.2.2: chaining is now CONFIRMED correct in all 20/20 runs
— Bug 4 is genuinely fixed.** But that same batch was STILL 20/20
degenerate, for a third reason: every plan's `crs_transform` reprojected
`'sites'` but never `'metro'`/`'schools'`/`'parks'`, so `spatial_nearest`
silently computed a nonsensical, nearly-constant "distance" dominated by
the CRS mismatch instead of erroring (documented as upstream candidate Bug
5). Fixed locally: `SYSTEM_HINTS` requirement (5) now explicitly requires
reprojecting all four layers individually, same grounding technique as
before. **Next step: run the smoke-test cells before trusting a fourth
full N=20 batch.**

**A `ranking_is_degenerate()` check now runs automatically** in both the
smoke test and the full loop (`degenerate_ranking` column in
`manifest.csv`, separate from `execution_success`), so this exact failure
mode can never again hide behind a clean "100% success rate."

**When resuming this phase: run ONLY the smoke-test cells (2, 6, 8, 9)
first** — three rounds have now each spent a full N=20 (~19 API calls) on
a mistake a 1-call smoke test would have caught for 1/20th the cost. Check
the printed operation sequence actually chains, that every layer used in a
distance call was individually reprojected, and that no degenerate-ranking
warning fires before running the full
`N_RUNS=20` loop again.

As of the last update to this file (2026-09-12): `data/raw/` has the four
Overpass exports (23 districts, 109 metro, 211 schools, 1063 parks - see
phase 1 note below). `data/processed/` has been produced by running
`notebooks/01_data_and_problem.ipynb` locally (env: `smart_spatial_system
0.2.0`, `geopandas 1.1.4`, `shapely 2.1.2` - matches `requirements.txt`'s
pin) and verified by reading the actual output files: `districts.geojson`
(23 `Polygon`, `ref` 1-23), `metro.geojson`/`schools.geojson`/
`parks.geojson` (109/211/1063 `Point` - parks correctly reduced from
Polygon to centroid), and `amenity_specs.json` (metro 800m/weight 3.0,
schools 1000m/weight 2.0, parks 1500m/weight 1.0, matching the notebook's
justified decision).

`notebooks/02_rule_based_arm.ipynb` (phase 3) ran clean after one fix
(extraction bug, see below) and is verified by reading the actual
outputs: `results/rule_based_ranking.csv` (23 rows, ranks exactly 1-23)
and `results/rule_based_query_spec.json` (`par: 1.0`, `rank_stability:
1.0`, and the 10-op sequence: 4x `crs_transform`, 3x `nearest_neighbor`,
`score_features`, `rank_features`, `build_report` - matches
`comparison_metric.md`'s Layer 1 definition exactly). Result: 21 of 23
districts tie at `accessibility_score=100.0` (contain an amenity of
every type, so all three distances are `0.0`); Währing and Hernals score
99.2 (13m/14m to the nearest metro station just outside their border).
Not a bug - `nearest_neighbor` is polygon-to-point - but worth a sentence
in the paper's discussion (a centroid- or population-weighted distance
would differentiate the top of the ranking more).

**`DagExecutor.execute(...)`'s result, confirmed on a real run (useful
for phase 4/5 too):** `result.success` (bool), `result.outputs` (dict)
with keys `sites_metric`, `metro_metric`, `schools_metric`,
`parks_metric`, `sites_with_metro`, `sites_with_schools`,
`sites_with_parks`, `sites_scored`, `sites_ranked`, `sites_report`.
`outputs["sites_ranked"]` is an opaque `geochat_sdk.types.vector.
VectorOut` - don't use it (this was the phase 3 extraction bug: it can't
go through `pd.DataFrame()` directly). `outputs["sites_report"]` is a
`ReportOut` dataclass with plain-dict `.meta` / `.summary` / `.table`
fields; `.table["rows"]` is a list of per-district dicts with `rank`,
`name`, `accessibility_score`, and `distance_to_{metro,school,park}_m` -
use that for phase 4's LLM-arm ranking extraction too.

`notebooks/03_llm_arm.ipynb` (phase 4) has been written - user confirmed
the go-ahead and resolved the temperature open decision (single 0.1, not
a sweep; see `paper/PLAN.md`). It calls `smart_spatial_system`'s
`LLMQuerySpecGenerator` (module: `orchestrator.planning.
llm_spec_generator` - not the similarly-named `llm_query_spec` module,
which is a different, lower-level thing) N=20 times on the *same*
`RAW_QUERY` phase 3 used (deliberately without the weight/`max_distance_m`
numbers - the LLM has to choose those itself, that's the point), reuses
phase 3's confirmed `DeterministicPlanner`/`DagExecutor`/
`sites_report.table["rows"]` extraction pipeline, and saves every run
(success or failure - a failure is data, per comparison_metric.md's
"Success rate" reliability metric) to `results/llm_runs/run_{i:02d}.json`
+ a `manifest.csv` index. **It has a smoke-test cell (1 API call) before
the full N=20 loop on purpose - run that first and read its output before
running the full loop**, since this is the first time this repo's LLM
integration has run anywhere, more uncertain than phases 1-3 (the exact
`context`/`system_hints` behavior of `generate()` was not verifiable
ahead of time). **Fixed in passing:** `.env.example` had the wrong base
URL variable name (`OPENAI_BASE_URL` instead of the real `LLM_BASE_URL`)
and the wrong key-priority order - both confirmed and corrected from
source; no `.env` existed yet on disk, so nothing needed retroactive
fixing.

**The first real smoke-test run (2026-09-12) found two bugs, both now
fixed in the notebook — see `claude/phase-4-llm-arm.md` (project doc) for
the full diagnosis.** (1) The LLM's generated plan used the `distance_to`
operation but omitted one of its two required input roles (`target`) —
a genuine LLM planning mistake; `smart_spatial_system`'s own source notes
`nearest_neighbor`/`spatial_nearest` as the usually-better operation for
this pattern. (2) More seriously, `smart_spatial_system`'s own
`normalize_llm_query_spec_for_planning()` unconditionally overwrites any
`score_features` op lacking a full `scoring_spec`/`factors` with a
hardcoded **real-estate** default (`investment_score`/`buildable_zone`/
`flood_risk`/...) regardless of domain — a bug in the vendored package
itself, not patched there (see "two things this repo is NOT" below).
Fixed locally in the notebook only: `SYSTEM_HINTS` gained two
schema-safety sentences (supply every input role an operation needs;
give `score_features` a real `scoring_spec`/`factors`, not a bare
`score_expression`) — deliberately not prescribing which operations or
weights to pick, since that's what this phase measures — and
`extract_ranking()` now falls back to any unambiguous `*_score` column
if the expected one was renamed out from under it by the package's own
normalization, so a future run doesn't KeyError on this again.

Not yet re-executed since the fix. Check `results/llm_runs/` directly
rather than trusting this paragraph.

**Network note for the next session:** this repo's Claude Code sandbox
had no route to `overpass-api.de` *or* `pypi.org` (org egress policy),
so neither "export GeoJSON from Overpass Turbo in a browser" nor
"`pip install osm2geojson`" worked directly. Worked around both: ran the
Overpass queries via `fetch()` executed inside the user's real desktop
browser (bypasses the sandbox's network policy entirely, no manual
Overpass Turbo steps needed), then converted the raw Overpass JSON to
GeoJSON with `scripts/overpass_to_geojson.py`, a small pure-stdlib
converter (nodes -> Point, closed ways -> Polygon, boundary relations ->
Polygon/MultiPolygon via standard OSM multipolygon ring assembly) written
because `osm2geojson`/`shapely` weren't installable here. If `data/raw/`
ever needs regenerating and this sandbox still can't reach Overpass or
PyPI, that script + the same browser-fetch approach is the fallback.

## Two things this repository is NOT

- **Not a place to modify `smart_spatial_system`'s code.** It is a pinned
  dependency (`requirements.txt`), installed like any other package. If
  something in it looks wrong while running an experiment here, that is a
  finding to report/fix upstream, not to patch in a local vendored copy.
- **Not a place for invented/synthetic data as final results.** The whole
  point of this case study is real, citable data (OpenStreetMap via
  Overpass — see `data/README.md` and `scripts/download_vienna_data.md`)
  and a real LLM, run for real, N times. Synthetic data is fine only for
  smoke-testing a notebook's code path before the real run.

## Network and secrets

- Data download (Overpass/OSM) and the LLM arm (AvalAI/OpenAI-compatible)
  both need a normal internet connection. If this session's network
  policy blocks them (test with e.g. `curl -sS -o /dev/null -w '%{http_code}\n' --max-time 8 https://overpass-api.de/api/status`),
  say so explicitly rather than silently skipping — the user needs to
  know to run that phase locally or open a session with a wider policy,
  not have it fail quietly. If a desktop browser is available in the
  session, fetching Overpass from inside it (see the network note above)
  is another way around a sandboxed cloud session's own network policy.
- LLM key goes in `.env` (copy from `.env.example`), never hardcoded,
  never committed. Only phase 4 (the LLM arm) needs it — don't ask for it
  or fail earlier phases for its absence.

## Working style for this repo

- Notebooks are numbered and run in order (`notebooks/01_...` through
  `05_...`); each phase's notebook is the deliverable for that phase, not
  a scratch file — keep them clean enough that the advisor could open and
  read them.
- Every phase's output that later phases depend on gets committed
  (`data/processed/`, `results/llm_runs/`, `results/metrics.csv`) so nobody
  has to re-run an expensive step (especially the LLM arm) to reproduce a
  later one.
- When a phase is finished, update the "Current state" section above with
  what's done and what's next, in the same commit — this file is how the
  next session (yours or the user's) picks up without a re-briefing.
- Keep `paper/PLAN.md`'s "Open decisions" section current — resolve an
  item there when it's decided, don't leave it stale once settled.
