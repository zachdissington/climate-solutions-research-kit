# A cooling-demand refrigerant-bank prior does not improve population for HFC-134a inversions: a negative result

*Open research note for the F-gas atmospheric-inversion and inventory community.*
*2026-06-11; **v2, 2026-06-12** (adversarial audit revision — a year-selection bug was found and fixed;
all numbers below are the corrected exact-2020 values; the qualitative verdict is unchanged. Changelog
in `validation_report_killtest.md`.) Published: Zenodo concept DOI 10.5281/zenodo.20652491,
CC-BY-4.0 (data-source licenses vary — see README). Companion to the smelter-resolved CF4 prior
(DOI 10.5281/zenodo.20617486); this is the deliberate negative result from the same spatial-prior
program.*

## One-sentence finding

For spatial disaggregation of European HFC-134a, a refrigerant-bank prior weighted by **population ×
climatological cooling-degree-days (CDD)** is *worse* than the plain population proxy already used by
EDGAR — the multiplicative CDD weighting adds no signal and actively degrades the fit — because
HFC-134a is a diffuse, population-coupled source with no point-source structure to resolve.

This is the structural opposite of CF4: where the smelter prior beat population because aluminium
smelters sit *away* from people, the refrigerant bank co-locates *with* people, so the demand-shaped
re-weighting tested here does not help.

## Why publish a negative

It saves the next person the re-discovery. The intuition "refrigerant emissions should track air-
conditioning demand, so a CDD-weighted bank prior should beat a flat population proxy" is reasonable
and untested in the open literature; the cheapest decisive test settles it in the wrong direction. The
result is also a clean worked example of the selection rule the CF4 work implies: an infrastructure /
demand prior only wins for sources that are **point-like and sited away from population**.

## What it is

A cheapest-decisive-test (per the spatial-prior playbook): build a crude in-use-stock proxy, correlate
it against an observation-driven inversion posterior, compare to the population/EDGAR baseline, and stop
at the go/no-go. No production build. The candidate prior is **bank ∝ population × CDD** — population as
the stock carrier, CDD as a cooling-demand weight. This is the b→∞ extreme of the family
pop × (a + b·CDD); milder mixed weightings were not run.

## Method (deliberately simple, fully reproducible)

1. **Posterior (truth):** ICOS PARIS HFC-134a inversion posterior, exact-2020 fields, Europe, 6-member
   ensemble (RHIME / InTEM / ELRIS × NAME / FLEXPART), grid 0.234° lat × 0.352° lon, masked to
   `country_fraction ≥ 0.5`, per-region normalized.
2. **Candidate prior:** population (GHSL GHS-POP 2020) × CDD (WorldClim 2.1 monthly mean-temperature
   climatology 1970–2000, CDD = Σ months max(0, T − 18 °C) × days), rasterized to the comparison grid.
   Note: *monthly-mean* climatological CDD evaluates to zero across maritime/Nordic Europe even though
   true daily-basis CDD there is small but nonzero — a construction property that drives the
   degeneracy discussed under Result.
3. **Baselines:** population alone; EDGAR v8.0 HFC-134a TOTALS (itself population-weighted).
4. **Metric:** per-country and pooled spatial correlation of each prior against the posterior, with the
   inversion's own prior correlated alongside as the anchoring reference.

## Result

| Prior | Pooled corr vs posterior (mean ± sd, 6 members) | Reading |
|---|---|---|
| **BANK** (population × CDD) | **0.237 ± 0.06** | the candidate — worst of the four |
| **POP** (population only) | **0.616 ± 0.09** | beats the bank prior by ~2.6× |
| **EDGAR** HFC-134a totals | **0.655 ± 0.09** | population-weighted; wins |
| PRIOR (inversion's own) | 0.687 ± 0.10 | anchoring reference (see caveat) |

**0 of 11 scoreable countries** had the bank prior beat population or EDGAR; in 4 more (UK, Netherlands,
Sweden, Norway) the monthly-climatology CDD weighting drives the prior to a constant zero — no spatial
variance, correlation undefined — even though those countries hold large HFC-134a banks (car A/C,
cold-chain). Excluding those four countries from the pool entirely, the bank prior still loses 0.262 to
0.579 — the deficit is real cross-country misallocation, not a zero-cell artifact. Even in the warm
south (Iberia, Greece) where CDD varies, the bank prior adds nothing over population. Per-country
detail: `validation_report_killtest.md`.

## Honest scope and conservative-test caveat

- **One proxy was tested, not "all infrastructure priors" — and not even all cooling-demand
  weightings.** The claim is specifically that a *multiplicative climatological-CDD* bank weighting
  degrades the population baseline for HFC-134a. We expect, on the per-capita-bank argument, that any
  cooling-demand weighting fails the same way, but daily-resolution CDD, mixed pop × (a + b·CDD)
  weightings, and non-climate stock proxies (vehicle-fleet density, commercial-refrigeration floor
  space) were not run, and the negative is not claimed for them.
- **The posterior is prior-anchored, which limits the test's power.** This inversion used an
  EDGAR/population-weighted prior; the posterior correlates with its own prior at 0.687 pooled
  (Greece 0.999), so population-shaped candidates earn part of their correlation mechanically wherever
  observations are weak. Anchoring of this strength could produce a gap of the observed order even
  against a bank-shaped truth, so the margin alone is not decisive. The negative rests instead on:
  zero positive evidence for the candidate anywhere (including the least-anchored countries and the
  CDD-resolved south), the burden of proof sitting with the challenger prior, and the companion CF4
  test showing this harness detects real prior improvements when they exist.
- **Europe only**, 2020. This is an HFC-134a refrigerant result; it does not generalize to other F-gases.

## Named consumer

The European HFC atmospheric-inversion community — ICOS PARIS / the multi-model HFC inversion groups
(UK InTEM/Bristol, Empa), the same channel as the CF4 prior. The useful takeaway for them: keep the
population/EDGAR proxy for HFC-134a spatial priors; a multiplicative climatological-CDD weighting is a
dead end, and we expect (but did not test) the same for milder cooling-demand weightings.

## Deposit contents

- This note (`method-note.md`) + the full verdict (`validation_report_killtest.md`).
- Code: `src/fetch_posteriors.py`, `src/benchmarks.py`, `src/build_bank_prior.py`,
  `src/hfc134a_killtest.py` (runs on the `sf6-spatial-prior/.venv` interpreter).
- Gridded priors (`outputs/`, NetCDF) — see README for the per-file license note on the
  WorldClim-derived files.
- Data provenance and formal citations: `validation_report_killtest.md` "Data citations" (ICOS PARIS
  collection DOI 10.18160/GR1Q-6SK4, CC-BY-4.0; EDGAR v8.0; WorldClim 2.1; GHSL GHS-POP 2020 — each
  under its own license; WorldClim is non-commercial/no-redistribution, which constrains the derived
  CDD and bank NetCDFs, see README).
- License: CC-BY-4.0 for the original content. ORCID 0009-0007-0196-1371.
