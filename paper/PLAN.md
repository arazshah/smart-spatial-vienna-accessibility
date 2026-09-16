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
| 6 | Results and figures | `notebooks/05_results.ipynb`, `results/figures/` | no | no |
| 7 | Paper writing | `paper/paper.md` — **full draft delivered (2026-09-16)**, ready for the advisor meeting; still open to revision after feedback | no | no |
| 8 | Final reproducibility check + release | tag, Zenodo DOI | no | no |
| 9 | Robustness pilot: alternative models + prompt phrasings | `notebooks/06_robustness_pilot.ipynb`, `results/robustness_pilot/` — **DONE, closed (2026-09-16)**: 7/9 conditions clean (PAR=1.0, RS=1.0, ρ=0.998966, N=5 each) across `gpt-4o`, `grok-3-mini-fast-beta`, `grok-3-fast`, and all 4 prompt paraphrases, once a second harness gap (`rank_features`' real parameter is `rank_field`, not `ranking_field`) was found and closed with a new `EXTENDED_SYSTEM_HINTS`; 2/9 (`model_weak_legacy`, `model_frontier_other_vendor`) remain blocked after three rounds of model-id substitution — accepted as a final, named limitation rather than left open, since no further AvalAI ids are available to try | yes | **yes** |

Phase 9 is a small, separate follow-up requested after the phase 7 draft:
does perfect reliability (PAR=1.0, Rank Stability=1.0 at N=20) generalize
beyond the one model and one exact phrasing phase 4 tested, or is it an
artifact of both being held fixed? Two axes, N=5 pilot each (escalate to
N=20 only where the pilot shows any deviation): (A) 5 alternative models
via AvalAI, same question, same schema-safety `SYSTEM_HINTS`; (B) 4
paraphrases of the same question, same model as phase 4. See
`claude/phase-9-robustness-pilot.md` for the full design rationale, the
literature motivating it, and the final real-run numbers.

**Outcome (2026-09-16), folded into `paper/paper.md` §5.5/§6.1/§7.4/§8:**
once the `rank_field` harness gap was fixed, reliability held perfectly
(PAR=1.0, RS=1.0, ρ=0.998966) across every condition that actually
produced a plan — `gpt-4o` (same vendor as phase 4), two Grok models
reached through a different vendor, and all four prompt paraphrasings
(including a second, independent harness gap in the `formal`/`distractor`
phrasings, where the planner inserted an unwanted PDF-report step — also
fixed via the same extended hints). Two gaps remain, both accepted as
final rather than left open: (1) neither attempt to include a genuinely
small/open-weight model succeeded — every id tried for that slot was
either dead on AvalAI or, when it worked, turned out to be another
capable commercial model (Grok), not small/open-weight; (2) the
"frontier model, other vendor" slot's substitute (`qwen3.8-2.4t-a95b`)
surfaced a *third*, independent harness-completeness bug on its 2/5
successful generations — it applied `rank_features`' `score_field`
parameter to `score_features`, which doesn't accept it — a fresh,
model-specific confusion opened by the very hint fix that made `gpt-4o`
reliable. Both are named explicitly as limitations in the paper rather
than glossed over; a third round of user-supplied model-id substitutions
(2026-09-16) did not resolve either, and the user decided not to pursue
further substitutions, so the pilot is closed with 7/9 conditions clean.

**Data-integrity fix (2026-09-16):** the third (partial/interrupted) run
also exposed a real notebook bug — the manifest/metrics cells built their
tables from the current kernel session's in-memory records only, so
re-running the loop for just the two still-broken conditions silently
overwrote the other six conditions' correct results in `metrics_pilot.csv`
with blanks, even though their `run_*.json` files were untouched on disk.
Recomputed both files directly from every condition's on-disk `run_*.json`
(independently, not trusting the corrupted CSV) and confirmed the 7 clean
conditions' numbers were unaffected; patched the notebook's manifest/metrics
cells to always read from disk going forward.

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
