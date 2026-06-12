# A cooling-demand refrigerant-bank prior does not improve population for HFC-134a inversions: a negative result

*Open, non-commercial research note for the F-gas atmospheric-inversion and inventory community.*
*2026-06-11. Published: Zenodo concept DOI 10.5281/zenodo.20652491 (version 10.5281/zenodo.20652492),
CC-BY-4.0. Companion to the smelter-resolved CF4 prior (DOI 10.5281/zenodo.20617486); this is the
deliberate negative result from the same spatial-prior program.*

## One-sentence finding

For spatial disaggregation of European HFC-134a, a refrigerant-bank prior weighted by **population ×
cooling-degree-days (CDD)** is *worse* than the plain population proxy already used by EDGAR — the
cooling-demand weighting adds no signal and actively degrades the fit — because HFC-134a is a diffuse,
population-coupled source with no point-source structure to resolve.

This is the structural opposite of CF4: where the smelter prior beat population because aluminium
smelters sit *away* from people, the refrigerant bank co-locates *with* people, so no demand-shaped
re-weighting helps.

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
the stock carrier, CDD as a cooling-demand weight.

## Method (deliberately simple, fully reproducible)

1. **Posterior (truth):** ICOS PARIS HFC-134a inversion posterior, 2020, Europe, 6-member ensemble
   (RHIME / InTEM / ELRIS × NAME / FLEXPART), grid 0.234° lat × 0.352° lon, masked to `country_fraction
   ≥ 0.5`, per-region normalized.
2. **Candidate prior:** population (GHSL GHS-POP 2020) × CDD (WorldClim 2.1 monthly mean-temperature
   climatology, CDD = Σ months max(0, T − 18 °C) × days), rasterized to the comparison grid.
3. **Baselines:** population alone; EDGAR v8.0 HFC-134a TOTALS (itself population-weighted).
4. **Metric:** per-country and pooled spatial correlation of each prior against the posterior.

## Result

| Prior | Pooled corr vs posterior | Reading |
|---|---|---|
| **BANK** (population × CDD) | **0.270** | the candidate — worst of the four |
| **POP** (population only) | **0.634** | beats the bank prior by 2.3× |
| **EDGAR** HFC-134a totals | **0.671** | population-weighted; wins |

**0 of 16 scored countries** had the bank prior beat both population and EDGAR. CDD weighting drives the
prior to a constant zero across maritime/Nordic Europe (UK / Norway / Sweden mean CDD ≈ 0), where car
A/C and cold-chain refrigeration still hold large HFC-134a banks — so the prior has no spatial variance
there (correlation undefined), and even in the warm south (Iberia, Greece) where CDD varies, the bank
prior still loses. Per-country detail: `validation_report_killtest.md`.

## Honest scope and conservative-test caveat

- **One proxy was tested, not "all infrastructure priors."** The claim is specifically that a
  *cooling-demand-weighted* bank prior degrades the population baseline for HFC-134a. Untested non-
  climate stock proxies (vehicle-fleet density, commercial-refrigeration floor space) are not expected
  to separate from population either, since HFC-134a has no point-source structure to resolve. They were
  not run, and the negative is not claimed for them.
- **The test was conservative and the prior still lost decisively.** This HFC-134a inversion used an
  EDGAR/population-weighted prior (the posterior files carry `EDGAR` in their names), so the truth is
  partly pulled toward population, giving population an unfair edge. Even so, the bank prior loses to
  *plain population* (0.270 vs 0.634) by a margin the prior bias cannot explain, and CDD hurts
  regardless of the truth's prior.
- **Europe only**, 2020. This is an HFC-134a refrigerant result; it does not generalize to other F-gases.

## Named consumer

The European HFC atmospheric-inversion community — ICOS PARIS / the multi-model HFC inversion groups
(UK InTEM/Bristol, Empa), the same channel as the CF4 prior. The useful takeaway for them: keep the
population/EDGAR proxy for HFC-134a spatial priors; a cooling-demand weighting is a dead end.

## Deposit contents (staged)

- This note (`method-note.md`) + the full verdict (`validation_report_killtest.md`).
- Code: `src/fetch_posteriors.py`, `src/benchmarks.py`, `src/build_bank_prior.py`,
  `src/hfc134a_killtest.py` (runs on the `sf6-spatial-prior/.venv` interpreter).
- The gridded priors produced (`outputs/`, NetCDF).
- Data provenance: ICOS PARIS F-gas collection `n8myDc-I-gbHkdt3ajIYLLDe` (DOI 10.18160/GR1Q-6SK4,
  CC-BY-4.0); EDGAR v8.0; WorldClim 2.1; GHSL GHS-POP 2020 (each under its own license — see `README.md`).
- License: CC-BY. ORCID 0009-0007-0196-1371.
