# Phase 2b Verdict — Germany Proof: Does the Infrastructure Prior Beat the Population Proxy?

> Run 2026-06-03. Honest result: **NO — not on the test we could run for Germany.** Our prior neither
> captures the inversion's hotspot better than the population proxies nor clearly diverges in a
> demonstrably-better direction. Stated plainly because that is what the numbers say.

## What we could (and could not) test

The rigorous plan was a cell-by-cell skill score of each candidate against the German SF6 **inversion
posterior** (truth). **That posterior is not publicly available as a gridded array** — it exists only as
figures in the paper SI, no Zenodo/repository deposit (verified 2026-06-03). We did **not** fabricate
one. So this is a *directional* test against the inversion's published quantitative anchor, not a metric
skill score.

Truth anchor used: the inversion found a SW/focus region holding **~1/3 of national German SF6**
(an industrial production/recycling source), a pattern that population gridding "cannot explain."

## Result A — focus-region (SW Germany) mass fraction vs published ~0.33

| Candidate | SW fraction | |dev from 0.33| |
|---|---|---|
| **Ours** (grid + point sources) | 0.175 | 0.155 |
| EDGAR (population) | 0.190 | 0.140 |
| GAINS (population + nightlights) | 0.175 | 0.155 |

**All three badly under-represent the focus region (~0.17–0.19 vs the true ~0.33), and ours is tied with
GAINS and marginally worse than EDGAR.** Ours did not win.

## Result B — structural divergence from the proxies (DE, 0.5°)

`corr(ours, EDGAR) = 0.55`, `corr(ours, GAINS) = 0.34`, `corr(EDGAR, GAINS) = 0.62`. Our prior **is**
spatially different from population gridding (lower mutual correlation, esp. vs GAINS) — but being
different is necessary, not sufficient, for being better, and Result A shows it is not better here.

## Why (and what it means)

This is the honest-risk outcome flagged before the build, now confirmed:
1. **Germany's dominant SF6 source is an under-reported industrial hotspot.** Our DE Layer-2 (E-PRTR
   reported point sources) sums to just **1.82 t of the ~100 t national total** — the big SW
   production/recycling source is below E-PRTR reporting, so Layer 2 cannot place it.
2. With Layer 2 near-empty, our prior is essentially Layer 1 (the grid), which — like population —
   concentrates in grid-dense/populous regions (Rhine-Ruhr, Berlin), **not** the SW industrial hotspot.
3. So for Germany specifically, **no bottom-up spatial method we have (grid OR population) reproduces the
   truth** — which is exactly the gap the inversion exists to fill.

## Honest implication for the artifact

Germany is plausibly a **worst case** for an infrastructure prior: SF6 here is dominated by one
under-reported industrial point source, so a grid-based prior has no structural advantage over
population. The thesis "infrastructure beats population" is **not supported in the hotspot-dominated
case**, and may only hold where SF6 is genuinely grid-distributed (no single dominant industrial
source) — which this build did not demonstrate and would require testing elsewhere.

Caveats (do not over-read the negative either): single coarse metric, not a cell-by-cell score; SW box
approximates the paper's region; no posterior array; one country. But the direction is clear and the
mechanism (under-reported industrial hotspot) is real.

## Recommendation

Do not declare success. Before any further build, decide deliberately: (a) test a country where SF6 is
grid-distributed rather than hotspot-dominated (does the prior win *there*?), (b) pursue the actual
inversion posterior (author contact / SI) for a real metric test, or (c) conclude the prior's edge over
population is unproven and stop. The artifact's premise (gap is real, unoccupied) still holds; its
*value over the existing proxy* is, as of this test, unproven.
