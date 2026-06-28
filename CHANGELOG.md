# Changelog

Notable changes to this repository. The gridded CF4 prior dataset is versioned separately on Zenodo (concept DOI [10.5281/zenodo.20617485](https://doi.org/10.5281/zenodo.20617485) — resolves to the latest version, currently v3); dataset releases are noted here too. Format loosely follows [Keep a Changelog](https://keepachangelog.com/); releases are calendar-anchored.

## [1.2.0] — 2026-06-13

### Changed
- CF4 validation figures re-derived on exact-2020 fields after a year-selection bug fix (some ensemble members had been scored against 2019). The corrected dataset is published as Zenodo v3 under the same concept DOI; these figures **supersede** the validation numbers quoted in the 1.0.0 and 1.1.0 entries below. Iceland (RHIME-only) was unaffected.
- C2F6 (second PFC leg) validation report corrected to exact-2020: pooled correlation now slightly favours EDGAR while the smelter-cell enrichment percentile rose above EDGAR; verdict unchanged (weak, low-confidence companion to CF4).

### Added
- `.zenodo.json` controlling the metadata for the Zenodo-archived code release (creator + ORCID, MIT license, links to the dataset DOIs).

### Notes
- This release is cut to mint a citable code-archive DOI (via the Zenodo–GitHub integration) for the CF4 data descriptor's code-availability requirement.

## [1.1.0] — 2026-06-11

### Added
- Fifth worked case study under `priors/`: **HFC-134a (refrigerant banks)** — a deliberate negative result. A cooling-demand-weighted refrigerant-bank prior (population × cooling-degree-days) does *not* improve on the population proxy for European HFC-134a; it loses by 2.3× (pooled spatial correlation 0.270 vs 0.634 for population vs 0.671 for EDGAR), winning 0 of 16 countries. HFC-134a is a diffuse, population-coupled source with no point-source structure to resolve — the SF6 failure mode, the structural opposite of CF4.
- HFC-134a published as a citable Zenodo deposit (concept DOI 10.5281/zenodo.20652491, CC-BY-4.0).

### Notes
- Reinforces the selection rule: a facility/infrastructure prior only beats population for sources that are point-like **and** sited away from population.

## [1.0.0] — 2026-06-09

First public release.

### Added
- Spatial-prior method and playbook (`methodology/spatial-prior-artifact-playbook.md`): a cheapest-decisive-test-first approach to building point-source-resolved priors for orphaned high-GWP gases.
- Four worked kill-test case studies under `priors/`: PFC-CF4 (aluminium smelters), SF6 (electricity grid), HFC-23 (HCFC-22 plants), NF3 (semiconductor fabs), each with `src/`, `factors/`, and validation reports.
- CF4 smelter-resolved spatial prior published as a citable dataset on Zenodo (concept DOI 10.5281/zenodo.20617485, CC-BY-4.0): global capacity / presence / production-rescaled fields, 0.1° Europe fields, FLEXINVERT+ drop-in (CF-1.8) variants, the 94-smelter open registry (`smelters_global.csv`), `SOURCES.md`, and the method note (Rev 2).
- Bring-your-own-export Project Drawdown solutions-database tooling (`scripts/`).

### Validation (CF4)
- Europe (ICOS PARIS 2020, 6-member flat-prior ensemble, block-bootstrap + spatial-permutation significance): the smelter prior beats the EDGAR population/built-up proxy at Iceland (spatial correlation 0.25 vs ~0, statistically significant, RHIME members) and in the pooled smelter-country aggregate (0.057 vs 0.015; direction-consistent in all 6 members, not per-member significant). France was dropped from public claims after stricter significance testing.
- The observation-driven posterior places the 22 in-domain smelter cells at a mean 60th percentile; EDGAR places them at the 26th.
- China placement rests on 12 registered major clusters; the decisive China test is collaboration-gated. The field is a *relative* prior for the aluminium sector only (~60–80% of global CF4), never a per-asset emissions ledger.

### Notes
- Operating principle: publish the algorithm, keep the time series. Code and methods live in this repository; the gridded prior fields are archived and versioned on Zenodo.
