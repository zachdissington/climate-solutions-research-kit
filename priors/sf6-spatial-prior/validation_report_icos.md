# Phase 2e Verdict — REAL Metric Test vs ICOS 2020 SF6 Posterior: thesis NOT supported

> Run 2026-06-03. The legitimate, trustworthy test — recent (2020, matched to our priors), fine grid
> (293×391, ~0.23°×0.35°), well-constrained modern network, 4-member ensemble (InTEM/ELRIS ×
> FLEXPART/NAME), clean per-country masks. **Result: the infrastructure prior does NOT beat population
> gridding for SF6. It is worse, in both France and Germany.** This is the real conclusion; it
> supersedes the InGOS-2011 test and confirms its direction.

## Result — spatial correlation vs the ICOS 2020 posterior (ensemble mean ± sd; normalized)

| Country | OURS (infra) | EDGAR (pop) | GAINS (pop+night) | ICOS own prior | N cells |
|---|---|---|---|---|---|
| France (FRA) | 0.090 ± 0.03 | **0.195 ± 0.07** | 0.140 ± 0.04 | 0.497 ± 0.12 | 1,266 |
| Germany (DEU) | 0.002 ± 0.02 | **0.139 ± 0.03** | 0.034 ± 0.03 | 0.176 ± 0.07 | 645 |

Ours loses to EDGAR (population) in both; in Germany ours ≈ 0 (uncorrelated with the truth).

## Why this is now decisive (the caveats are gone)

- **Recent:** 2020 truth vs our 2020 EDGAR/GAINS + current OSM — no 15-year mismatch.
- **Well-constrained:** modern dense network, not the prior-dominated 2011 inversion.
- **Fine + clean:** 0.23° regular grid, country masks from the dataset's own `country_fraction`.
- **Ensemble:** 4 inversion system/model combos; the loss holds across all (low sd).
- **Consistent with 2011:** ours lost there too. The negative is robust across old/recent and
  weak/strong truth — the "2011 is unreliable" caveat does not rescue the thesis.

## Honest calibration (what the numbers do and don't say)

At this fine 0.23° resolution **every** bottom-up method correlates only weakly with the posterior
(EDGAR best at 0.14–0.20; even the inversion's own prior is 0.18–0.50) — fine-scale SF6 allocation is
genuinely hard for all priors, because real SF6 is concentrated at a few specific sites the inversion
resolves. So this is not "population is great." It is: **population is modestly but consistently better
than our infrastructure prior, and our prior is the worst of the options** (near-random in Germany).
Spreading SF6 across all transmission substations by voltage class does not match where SF6 actually
concentrates.

## Verdict

**The founding thesis — an OSM-substation infrastructure prior beats population gridding for SF6 — is
NOT supported, on the best evidence obtainable.** Tested against the most recent, well-constrained,
multi-system public posterior, the infrastructure prior underperforms the existing population proxy in
both test countries. Combined with the 2011 result, this is a robust negative.

## What this means for the project (clean closure)

- **Premise** (gap real, unoccupied) — still true.
- **Core value claim** (better than population) — **refuted** by the real test. Not unproven anymore —
  measured, and it loses.
- **Recommendation: stop.** Bank this as a completed, honest negative. Community outreach is no longer
  needed to settle it — the public ICOS data settled it. Global scale-out is not justified.

## What survives as a genuine contribution

A verified, reproducible pipeline + a clean, multi-dataset **negative result**: *"an open OSM-substation
spatial prior does not improve on population gridding for SF6 at country/sub-national scale; tested vs
InGOS 2011 and ICOS 2017–2024 posteriors."* That is a real, publishable finding — it tells the
inversion/inventory community that infrastructure-proxy gridding is not the easy SF6 improvement one
might assume. Negative, but honestly earned and useful.
