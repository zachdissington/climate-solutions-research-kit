# Changelog

Notable changes to this repository. The gridded CF4 prior dataset is versioned separately on Zenodo (DOI [10.5281/zenodo.20617486](https://doi.org/10.5281/zenodo.20617486)); dataset releases are noted here too. Format loosely follows [Keep a Changelog](https://keepachangelog.com/); releases are calendar-anchored.

## [1.0.0] — 2026-06-09

First public release.

### Added
- Spatial-prior method and playbook (`methodology/spatial-prior-artifact-playbook.md`): a cheapest-decisive-test-first approach to building point-source-resolved priors for orphaned high-GWP gases.
- Four worked kill-test case studies under `priors/`: PFC-CF4 (aluminium smelters), SF6 (electricity grid), HFC-23 (HCFC-22 plants), NF3 (semiconductor fabs), each with `src/`, `factors/`, and validation reports.
- CF4 smelter-resolved spatial prior published as a citable dataset on Zenodo (DOI 10.5281/zenodo.20617486, CC-BY-4.0): global capacity / presence / production-rescaled fields, 0.1° Europe fields, FLEXINVERT+ drop-in (CF-1.8) variants, the 94-smelter open registry (`smelters_global.csv`), `SOURCES.md`, and the method note (Rev 2).
- Bring-your-own-export Project Drawdown solutions-database tooling (`scripts/`).

### Validation (CF4)
- Europe (ICOS PARIS 2020, 6-member flat-prior ensemble, block-bootstrap + spatial-permutation significance): the smelter prior beats the EDGAR population/built-up proxy at Iceland (spatial correlation 0.25 vs ~0, statistically significant, RHIME members) and in the pooled smelter-country aggregate (0.057 vs 0.015; direction-consistent in all 6 members, not per-member significant). France was dropped from public claims after stricter significance testing.
- The observation-driven posterior places the 22 in-domain smelter cells at a mean 60th percentile; EDGAR places them at the 26th.
- China placement rests on 12 registered major clusters; the decisive China test is collaboration-gated. The field is a *relative* prior for the aluminium sector only (~60–80% of global CF4), never a per-asset emissions ledger.

### Notes
- Operating principle: publish the algorithm, keep the time series. Code and methods live in this repository; the gridded prior fields are archived and versioned on Zenodo.
