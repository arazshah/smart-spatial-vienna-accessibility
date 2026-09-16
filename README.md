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
for the precise metric, and [`paper/paper.md`](paper/paper.md) for the full
write-up.

This repository does not modify `smart_spatial_system` — it depends on a
**pinned released version** of it (see `requirements.txt`), so results here
stay reproducible even as that project keeps developing. If running this
experiment surfaces a bug in the library itself, the fix goes to
`smart_spatial_system`, a new version is released, and this repository's
pin is bumped deliberately — never the other way around.

## Status

**All phases (0–6) are done.** The full experiment has been run end to end
and independently re-verified: rule-based arm (N=5, deterministic), LLM arm
(N=20 runs at temperature 0.1), the three-layer comparison metric, and the
results figures/tables. Phase 7 (this paper) is in progress at
[`paper/paper.md`](paper/paper.md); phase 8 (final tag + release) is not yet
done. See [`paper/PLAN.md`](paper/PLAN.md) for the full phase-by-phase plan
and status table.

### Headline results

| Arm | N | Plan Agreement Rate | Rank Stability (within-arm) | ρ vs. rule-based | Success rate | Median latency |
|---|---|---|---|---|---|---|
| Rule-based | 5 | 1.0 | 1.0 | — | 1.0 | — |
| LLM | 20 | 1.0 | 1.0 | 0.9990 | 1.0 | 20.01 s |

Once known validation gaps in `smart_spatial_system` were fixed (now
released as `0.2.4`, pinned below), the LLM arm was perfectly reliable
across all 20 runs — same plan shape, same final ranking, every time — and
agreed with the deterministic rule-based reference almost exactly. The one
real difference between the two arms is a modeling choice, not noise: the
LLM invents a flat weighting across amenity types where the rule-based arm
was given a deliberately unequal one (see `paper/paper.md` §5.3–5.4 and
`paper/PLAN.md`'s findings section for the full detail, including why that
difference barely shows up in this particular ranking).

Tables and figures backing these numbers live in `results/` (see
`results/metrics.csv`, `results/figures/`, `results/figures/table1_reporting.md`).

## Structure

```text
notebooks/          Jupyter notebooks, one per phase (numbered, run in order)
data/raw/            Downloaded source data (OSM/Vienna open data) - gitignored, large files
data/processed/      Cleaned GeoJSON actually fed into the system - committed, small
results/             Generated tables, figures, and the raw per-run plan/output logs
paper/               Paper draft, metric definition, and the experiment plan
scripts/             Small standalone scripts (data download, repeated LLM runs)
```

## Running this repository

You do **not** need to set up anything locally to read the results — the
notebooks' outputs, `results/`, and `paper/paper.md` are all committed and
readable directly on GitHub. Local setup (or a cloud option below) is only
needed to *re-run* the analysis yourself.

### Option A — no local install (GitHub Codespaces)

This repository includes a [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json).
From the repository's GitHub page: **Code → Codespaces → Create codespace on
main**. This opens a browser-based VS Code with Python already set up and
`pip install -r requirements.txt` run automatically — no local Python,
virtualenv, or Jupyter install required. Once it's ready, open any notebook
under `notebooks/` and run it (the Jupyter extension is preinstalled).

Phases 2, 3, 5, and 6 (everything except the initial OSM data download and
the LLM arm itself) run fully offline from the data and run logs already
committed in this repository — no network access or API key needed even
inside the Codespace. To run phase 4 (the LLM arm) yourself inside a
Codespace, add your API key as a Codespaces secret (or a `.env` file, not
committed) the same way as described in Option B below.

### Option B — local install

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

### Option C — Google Colab (single notebook, no repo clone needed on disk)

To open just one notebook (e.g. to show a specific figure) without setting
up a full environment: open a blank notebook at
[colab.research.google.com](https://colab.research.google.com), and in the
first cell run:

```python
!git clone https://github.com/arazshah/smart-spatial-vienna-accessibility.git
%cd smart-spatial-vienna-accessibility
!pip install -q -r requirements.txt
```

then open the specific notebook file from the Colab file browser (left
sidebar → the cloned folder → `notebooks/`) and run its cells. This is a
convenience path for browsing one notebook interactively; Option A
(Codespaces) is the recommended way to work with the whole repository.

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
