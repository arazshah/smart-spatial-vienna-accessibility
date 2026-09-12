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
| 5 | Comparison metric computation | `notebooks/04_comparison_metric.ipynb`, `results/metrics.csv` | no | no |
| 6 | Results and figures | `notebooks/05_results.ipynb`, `results/figures/` | no | no |
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

- Whether to run the LLM arm at a single temperature or sweep it
  (e.g. 0.1 vs 0.7) to show variance as a function of temperature.
- N (number of repeated LLM runs) - 20 as a starting point, revisit once
  we see early variance and API cost.
- Target journal/venue and its required format, once the advisor weighs in.
