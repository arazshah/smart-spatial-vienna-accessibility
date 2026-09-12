# Comparison metric

How "similar" two runs of the planner are is measured at three layers,
because each answers a different question. All three are computed over the
same N repeated runs of each arm (rule-based and LLM), on the same
question and the same input data.

## Layer 1 — Structural agreement: Plan Agreement Rate (PAR)

Does the planner build the same *shape* of plan every time?

For a run *r*, its **operation sequence** is the ordered list of operation
names in its `QuerySpec` (`crs_transform`, `nearest_neighbor`,
`score_features`, ...), stripped of node ids and parameter values - only
the sequence of operation *names* and their input/output wiring topology.

1. Take the mode (most frequent) operation sequence across all N runs of an
   arm, call it the reference sequence.
2. `PAR = (number of runs whose sequence exactly equals the reference) / N`

The rule-based arm has `PAR = 1.0` by construction (every run produces an
identical `QuerySpec`, asserted directly in
`smart_spatial_system`'s test suite). This is the baseline, not a result
to compute - it is the point the LLM arm is measured against.

## Layer 2 — Parametric agreement

Among the runs that share the reference sequence, how much do their
*parameters* vary? For each amenity's `weight` and `max_distance_m`
(the values an LLM run chooses, versus the values a rule-based run is
simply given), report mean and standard deviation across runs.

A structurally-identical plan with high parameter variance is still an
unreliable plan - this layer catches that case, which PAR alone would
miss.

## Layer 3 — Outcome agreement: Rank Stability

Does the *answer the user sees* change, even when the plan looks similar?

For each run, take the final ranking of the 23 districts by accessibility
score. For every pair of runs within an arm, compute Spearman's rank
correlation coefficient (ρ) between their rankings. **Rank Stability** is
the mean ρ across all pairs (± standard deviation).

Also compute ρ between each LLM run and the rule-based reference ranking,
to say how close the LLM arm gets to the deterministic baseline, not just
how internally consistent it is.

`ρ = 1.0` for two identical rankings; the rule-based arm's Rank Stability
is `1.0` by construction, same reasoning as PAR.

## Reliability metrics (not similarity, but reported alongside)

- **Success rate**: fraction of the N runs that executed without error
  (`DagExecutionResult.success`).
- **Latency**: median and IQR of wall-clock time per run.

## Reporting format

One row per arm (and per LLM configuration, if temperature is swept):

| Arm | N | PAR | Weight σ (per amenity) | Rank Stability (ρ, mean ± sd) | ρ vs. rule-based | Success rate | Median latency |
|---|---|---|---|---|---|---|---|

## Implementation notes

- Plan comparison operates on `QuerySpec.operations` (see
  `orchestrator/planning/spec.py` in `smart_spatial_system`), not on the
  executed `DagPlan` - the QuerySpec is the more direct output of the
  planning step being compared.
- Rank Stability uses `scipy.stats.spearmanr`.
- All raw per-run QuerySpecs and rankings are kept in
  `results/llm_runs/` (see phase 4) so the metric computation notebook
  (phase 5) is reproducible from stored data without re-calling the LLM.
