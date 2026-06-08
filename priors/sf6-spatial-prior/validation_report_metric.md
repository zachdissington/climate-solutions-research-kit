# Phase 2d — InGOS 2011 Metric Test (SUPERSEDED by the ICOS 2020 test in Phase 2e)

> **SUPERSEDED 2026-06-03:** this test scored against the InGOS **2011** posterior, which is old AND
> prior-dominated (corr 0.95 with its own population prior → weakly constraining → partly circular). A
> recent, well-constrained, fine, multi-system gridded posterior was subsequently found (ICOS PARIS
> 2017–2024, `validation_report_icos.md`). Treat **2e/ICOS as the real verdict**; the 2011 result below
> is retained as an audit trail, NOT as the conclusion. Original (over-stated) framing follows.
>
> Run 2026-06-03. **Result vs the 2011 posterior: ours scored worse than population (DE 0.64 vs 0.90,
> FR 0.12 vs 0.91) — but against an unreliable, prior-dominated reference, so this is inconclusive, not
> a verdict.** (I over-called it as "thesis not supported"; corrected.)

## Result (spatial correlation with the 2011 InGOS posterior; normalized; higher = better)

| Region | OURS (infra) | EDGAR (pop) | GAINS (pop+night) | InGOS own prior | N cells |
|---|---|---|---|---|---|
| Germany | 0.637 | 0.900 | 0.899 | 0.953 | 21 |
| France | 0.121 | 0.915 | 0.911 | 0.951 | 141 |

Ours loses to both population proxies everywhere; in France it is nearly uncorrelated with the truth.

## What this overturns

The 2c "France looks good" reading is **wrong, and this corrects it.** 2c saw ours ≈ orthogonal to
population (corr≈0) and called it the right direction. But the inversion truth correlates **~0.90 with
population** — so orthogonal-to-population = orthogonal-to-truth. At the scale we can test, **population
is a good SF6 proxy and our grid-infrastructure prior is a worse one.** The project's founding premise
("population gridding misplaces SF6") — which rested on the literature's qualitative SW-Germany anecdote
— does not hold up quantitatively here.

## Honest caveats (calibration, not excuses)

- **The test is weak because the 2011 posterior is prior-dominated:** it correlates 0.95 with its *own*
  (population-based) prior, i.e. the 2011 station network barely constrained it. So the test substantially
  rewards "agreement with the population prior," which is partly circular. It does **not** strongly prove
  population is correct — only that ours diverges from the population-based consensus. A
  well-constrained, higher-resolution posterior *could* differ.
- **Temporal mismatch:** truth 2011 vs our current OSM / 2020 EDGAR-GAINS.
- **France data quality:** French OSM over-tags sub-transmission as transmission (48,642 cells), so the
  French prior is noisy — likely part of the 0.121. BUT **Germany, with clean data (8,835), still loses
  (0.637 < 0.90)** — so the loss is not just a France artifact.
- Coarse variable grid; small N (21 DE / 141 FR cells); EMPA2 system only.

## Verdict

**No positive evidence the infrastructure prior beats population; the only real test available leans
against it, and even the clean-data case (Germany) loses.** Combined with the earlier findings:
- Premise (gap real, unoccupied) — still true.
- Value over the population proxy — **unproven, and now with a negative signal.**

The strong-form thesis ("infrastructure beats population for SF6") has no support and some
counter-evidence. The only thing that could overturn this is a recent, well-constrained,
high-resolution posterior (outreach / EYE-CLIMA) — but that is a long shot given population scored ~0.90
here. This is an honest place to **stop or pivot** the core value claim, not to scale globally.

## What remains genuinely valuable (not nothing)

- The verified, reproducible pipeline + the honest negative finding ("at testable scales, population is a
  reasonable SF6 proxy; an OSM-substation prior does not improve on it") is itself a publishable,
  community-useful result — it tells the inversion community what does NOT help.
- The premise/landscape research and the methods scaffold stand.
