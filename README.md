# Smart Spatial Vienna Accessibility

Case study and reproducibility experiment for **Smart Spatial System**
([arazshah/smart_spatial_system](https://github.com/arazshah/smart_spatial_system)):
scoring Vienna's 23 municipal districts by accessibility to public amenities
(metro, schools, parks), and comparing two ways of turning a natural-language
question into an executable plan:

- **Rule-based**: `build_accessibility_query_spec` — the operation chain
  follows mechanically from the amenity list. Deterministic by construction.
- **LLM-backed**: `LLMQuerySpecGenerator` — the same question, answered by an
  LLM, N times.

The question this repository answers: **how much does the LLM-generated plan
vary across repeated runs of the same question, and does that variation
change the final ranking?** See [`paper/comparison_metric.md`](paper/comparison_metric.md)
for the precise metric.

This repository does not modify `smart_spatial_system` — it depends on a
**pinned released version** of it (see `requirements.txt`), so results here
stay reproducible even as that project keeps developing. If running this
experiment surfaces a bug in the library itself, the fix goes to
`smart_spatial_system`, a new version is released, and this repository's
pin is bumped deliberately — never the other way around.

## Status

Phase 0 — repository skeleton. See [`paper/PLAN.md`](paper/PLAN.md) for the
full phase-by-phase plan.

## Structure

```text
notebooks/          Jupyter notebooks, one per phase (numbered, run in order)
data/raw/            Downloaded source data (OSM/Vienna open data) - gitignored, large files
data/processed/      Cleaned GeoJSON actually fed into the system - committed, small
results/             Generated tables, figures, and the raw per-run plan/output logs
paper/               Paper drafts and supporting notes (metric definition, plan)
scripts/             Small standalone scripts (data download, repeated LLM runs)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in OPENAI_API_KEY (or AVALAI_API_KEY / LLM_API_KEY) for the LLM arm.
# The rule-based arm and all data-preparation notebooks need no key at all.

jupyter lab
```

The LLM arm calls an external API (AvalAI/OpenAI-compatible) and downloading
the source data reaches OpenStreetMap/Vienna open-data servers - both need a
normal internet connection. Neither is required to explore the rule-based
arm or the codebase itself.

## Data

See [`data/README.md`](data/README.md) for exact sources, download steps and
licensing for everything under `data/`.

## Citing

If you use this case study, please cite both this repository and
[Smart Spatial System](https://github.com/arazshah/smart_spatial_system)
(see its `CITATION.cff` once published). A `CITATION.cff` for this
repository will be added once the paper is submitted.

## License

MIT - see [LICENSE](LICENSE).
