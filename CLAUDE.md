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

**Phase 0 (repository skeleton) is done.** Check `paper/PLAN.md`'s phase
table for what's next — do not assume phase 1 is next without checking,
this file will not be updated every session.

As of the last update to this file: phase 1 (Vienna data acquisition) is
next. Raw GeoJSON for districts/metro/schools/parks either doesn't exist
yet under `data/raw/`, or was added locally and needs to be reviewed and
turned into `data/processed/` (phase 2). Check `data/raw/` and
`data/processed/` directly rather than trusting this paragraph.

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
  not have it fail quietly.
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
