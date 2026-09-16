# Experiment and paper plan

Working title: *Reproducibility and Determinism in LLM-Generated vs.
Rule-Based Spatial Query Plans: A Vienna Accessibility Case Study*

## Research question

Given the same natural-language accessibility question, how much does an
LLM-backed query planner's output vary across repeated runs — structurally
(the operation plan), parametrically (the weights/thresholds it chooses),
and in the final result (the ranking it produces) — compared to a
rule-based planner that is deterministic by construction? See
[`comparison_metric.md`](comparison_metric.md) for the precise definitions.

## Phases

| # | Phase | Notebook / output | Needs network? | Needs LLM key? |
|---|---|---|---|---|
| 0 | Repository skeleton | this repo | no | no |
| 1 | Vienna data acquisition | `data/raw/`, `data/processed/`, `data/README.md` | yes (OSM/Vienna open data) | no |
| 2 | Problem definition + data exploration | `notebooks/01_data_and_problem.ipynb` | no (uses `data/processed/`) | no |
| 3 | Rule-based arm | `notebooks/02_rule_based_arm.ipynb` | no | no |
| 4 | LLM arm (N repeated runs) | `notebooks/03_llm_arm.ipynb`, `results/llm_runs/` | yes | **yes** |
| 5 | Comparison metric computation | `notebooks/04_comparison_metric.ipynb`, `results/metrics.csv` — **DONE (2026-09-16)** | no | no |
| 6 | Results and figures | `notebooks/05_results.ipynb`, `results/figures/` — **DONE (2026-09-16)** | no | no |
| 7 | Paper writing | `paper/paper.md` (or LaTeX) | no | no |
| 8 | Final reproducibility check + release | tag, Zenodo DOI | no | no |

Phases 2, 3, 5, 6 can run entirely offline once `data/processed/` and
`results/llm_runs/` exist, using only the pinned `smart-spatial-system`
package. Phase 4 is the only phase that must run somewhere with both
network access and an LLM key configured (see the repo README).

## Units of analysis ("sites")

Vienna's 23 municipal districts (*Gemeindebezirke*), by official boundary.
Chosen over arbitrary points because they are a fixed, citable, small
(N=23) set that needs no invented data, and this framing (accessibility by
administrative unit) is standard in the "15-minute city" literature.

## Amenities

Defined in `notebooks/01_data_and_problem.ipynb`, currently:

- Metro (U-Bahn) stations — weight highest, shortest cutoff
- Schools — medium weight
- Parks — lowest weight, longest cutoff

Exact weights and `max_distance_m` values are a modeling decision made and
justified in that notebook, not assumed here.

## Open decisions to revisit together

- N (number of repeated LLM runs) - 20 as a starting point, revisit once
  we see early variance and API cost. **Resolved for this pass (2026-09-16):**
  phase 4's real N=20 batch came back with zero variance (PAR=1.0, Rank
  Stability=1.0 among LLM runs — see phase 5 findings below), so N=20 was
  more than enough to characterize this setup; a larger N would mostly
  spend API budget confirming the same zero-variance result. Worth
  revisiting only if a future temperature sweep (below) reintroduces
  variance.
- Target journal/venue and its required format, once the advisor weighs in.
- A temperature sweep beyond the single 0.1 value used here, now that a
  clean baseline exists to compare against (see "Resolved decisions"
  below) — still a reasonable follow-up, not ruled out.

## Resolved decisions

- **Temperature (2026-09-12):** single temperature, 0.1 (not a sweep) -
  matches `.env.example`'s default. Keeps phase 4 to one N-run experiment
  rather than doubling API cost and the phase-5/6 analysis surface for a
  first pass. A temperature sweep is still a reasonable follow-up once
  the single-temperature results are in, not ruled out permanently.

## Findings to fold into the paper's discussion/limitations section

- **The rule-based ranking ties 21 of 23 districts at
  `accessibility_score = 100.0`.** Checked (2026-09-16) whether this was
  a bug in `smart_spatial_system`'s distance calculation rather than a
  real result: read `plugins/nearest_neighbor.py` and
  `plugins/distance_calculator.py` directly (both the shapely path and
  the pure-python fallback correctly return `0.0` when a point lies
  inside a polygon - standard GIS behaviour, not a shortcut), then wrote
  an independent point-in-polygon check from scratch (no shared code with
  the library under test - see `scripts/verify_zero_distances.py`) and
  ran it directly against `data/processed/*.geojson`. Result: every one
  of the 23 districts contains at least 4 schools and at least 9 parks
  (211 schools / 1063 parks averaging ~9 and ~46 per district), so
  `distance_to_school_m`/`distance_to_park_m` are genuinely `0.0`
  everywhere; exactly 2 districts (Waehring, Hernals) contain zero of the
  109 metro stations, matching `results/rule_based_ranking.csv`'s only
  two non-tied rows exactly. **Not a bug** - a real consequence of
  Vienna's amenity density - but worth a sentence in the discussion: a
  centroid- or population-weighted distance (rather than polygon-to-point
  "0 if any instance falls inside the boundary") would differentiate the
  top of the ranking more than this framing does, and this ceiling effect
  should be named explicitly rather than left for a reader to wonder
  about. See `claude/phase-3-rule-based-arm.md` for the fuller writeup.

- **Once every upstream precondition was enforced (phase 4, `0.2.4`), the
  LLM arm's reliability at N=20 was effectively perfect: PAR = 1.0 and
  Rank Stability = 1.0 among the 20 LLM runs** (computed in phase 5, see
  `notebooks/04_comparison_metric.ipynb` and `results/metrics.csv`).
  Every run built the identical 9-op plan shape and produced the
  identical final ranking. This is the resolution of phase 4's headline
  finding: six earlier rounds of 20/20-degenerate batches were about
  missing/weak validation in the underlying framework (chaining, CRS
  handling, factor-type defaults), not about a capability ceiling in the
  model itself — worth reporting as a paired finding (the failure mode,
  then its resolution), not just the eventual success.

- **Reliability is not the same as matching the rule-based arm's
  judgment.** All 20 LLM runs invent the same *flat* weighting scheme
  (`weight=1`, `max_distance=800` for metro/schools/parks alike — `sd=0.0`
  across all 20), whereas the rule-based arm uses a deliberately unequal
  one (metro weight=3/cutoff 800m, schools weight=2/cutoff 1000m, parks
  weight=1/cutoff 1500m — a considered modeling decision, see "Amenities"
  above). The raw query given to the LLM never specifies these numbers
  (by design, see phase 4), so this isn't an LLM error - it is what a
  reasonable planner invents to fill a genuinely under-specified gap, and
  it's a different choice than the domain-informed one the rule-based arm
  was simply given. Worth naming directly: the LLM arm is maximally
  *reliable* here but not equivalent in domain-informed *judgment*.

- **The two arms' rankings still agree almost perfectly despite the
  different weighting** (ρ = 0.998966, LLM arm vs. the rule-based
  reference) - because the 21/23-way tie at the top dominates both
  rankings regardless of the exact weights chosen; the weighting only
  really matters for the bottom two districts (Waehring, Hernals), which
  is exactly where the small ρ gap comes from. That gap itself turned out
  to be a rounding artifact, not a real disagreement: `rule_based_ranking.csv`
  stores both districts' scores rounded to `99.2`, which ties them (average
  rank) under `scipy.stats.spearmanr`, while the LLM arm's higher-precision
  scores (which agree on the *same* underlying 13m/14m metro distances)
  rank them 22nd/23rd distinctly. Worth a footnote in the paper rather
  than being read as noise or a real limitation.
