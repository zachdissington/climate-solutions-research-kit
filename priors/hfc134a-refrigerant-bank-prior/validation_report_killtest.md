# HFC-134a refrigerant-bank prior — kill-test verdict: NO-GO

Date: 2026-06-11
Gas: HFC-134a (the dominant refrigerant: mobile A/C, commercial + domestic refrigeration)
Candidate prior: **bank ∝ population × cooling-degree-days (CDD)** — a crude in-use-stock proxy.
Truth: ICOS PARIS HFC-134a inversion posterior, 2020, Europe, 6-member ensemble
(RHIME / InTEM / ELRIS × NAME / FLEXPART).

## VERDICT: NO-GO. The cooling-demand bank prior loses to population everywhere — and CDD makes it *worse* than population alone.

Pooled spatial correlation vs the posterior (ensemble mean ± sd across the 6 members), masked by
`country_fraction ≥ 0.5`, per-region normalized:

| Prior | Pooled corr | Reading |
|---|---|---|
| **BANK** (pop × CDD) | **0.270 ± —** | our candidate — worst of the four |
| **POP** (population only) | **0.634** | population alone beats the bank prior by 2.3× |
| **EDGAR** HFC-134a TOTALS | **0.671** | EDGAR (population-weighted) wins |
| PRIOR (inversion's own EDGAR prior) | (≈EDGAR, per-member) | reference floor |

**0 of 16 scored countries** had the bank prior beat both population and EDGAR. Not a single region.

### Per-country (BANK / POP / EDGAR), corr vs posterior

```
  FRA: BANK 0.546  POP 0.709  EDGAR 0.761
  ESP: BANK 0.578  POP 0.621  EDGAR 0.674
  DEU: BANK 0.423  POP 0.612  EDGAR 0.716
  ITA: BANK 0.540  POP 0.565  EDGAR 0.597
  GBR: BANK  nan   POP 0.676  EDGAR 0.718
  NLD: BANK  nan   POP 0.632  EDGAR 0.749
  BEL: BANK 0.475  POP 0.638  EDGAR 0.791
  POL: BANK 0.495  POP 0.741  EDGAR 0.822
  GRC: BANK 0.638  POP 0.668  EDGAR 0.960
  PRT: BANK 0.430  POP 0.609  EDGAR 0.758
  CHE: BANK 0.260  POP 0.490  EDGAR 0.551
  AUT: BANK 0.546  POP 0.663  EDGAR 0.801
  ROU: BANK 0.463  POP 0.532  EDGAR 0.597
  SWE: BANK  nan   POP 0.694  EDGAR 0.839
  NOR: BANK  nan   POP 0.810  EDGAR 0.847
  POOL: BANK 0.270 POP 0.634  EDGAR 0.671
```

`nan` for GBR / NLD / SWE / NOR is **not a bug** — it is the failure mechanism. Those countries have
~zero cooling-degree-days (UK mean CDD 0, Norway/Sweden 0, Netherlands 2; verified: `frac of cells
with CDD>0` is 0.00–0.11). Multiplying population by CDD drives the bank prior to a constant zero
across maritime/Nordic Europe, so it has no spatial variance there and its correlation is undefined.
Even in the warm south (ESP, ITA, GRC) where CDD is large and varying, the bank prior still loses —
CDD adds noise, not signal.

## Why it failed (the diffuse-source / wrong-proxy mode)

1. **CDD is the wrong stock proxy.** The HFC-134a refrigerant bank is *not* concentrated where cooling
   demand is highest. The installed stock — mobile A/C in every car fleet, supermarket and cold-chain
   refrigeration, domestic fridges — tracks population and economic activity, and runs in cold
   countries as much as warm ones. Weighting by CDD throws away the cold-country bank entirely (the
   N. Europe zero-out) and over-weights the warm south, both of which move the prior *away* from the
   posterior. POP alone (0.634) cleanly beats BANK (0.270): the CDD multiplier is pure degradation.

2. **HFC-134a is a diffuse, population-coupled source — the SF6 failure mode, not the CF4 success
   mode.** This was the a-priori risk flagged in the portfolio plan ("HFC refrigerant-bank … parked,
   diffuse/area candidate"). The kill-test confirms it: there are no point sources to resolve. The gas
   is emitted from millions of distributed appliances that co-locate with people. Population is very
   hard to beat, exactly as it was for SF6 in switchgear. A facility/infrastructure prior only wins
   when the real emitters are concentrated *away* from population (CF4 smelters); refrigerant banks
   are the opposite.

## Conservative-test caveat (stated honestly)

Unlike HFC-23 (FLAT prior), this HFC-134a inversion used an **EDGAR/population-weighted prior** — the
posterior files literally carry `EDGAR` in their names (`*_EUROPE_EDGAR_PARISNID2026_*`) and the
inversion's own `flux_total_prior` ≈ EDGAR. So the posterior is partly pulled toward population, and
part of POP's and EDGAR's high correlation is mechanical (a population-biased truth rewards a
population prior). This makes the test **conservative**: it was always going to be easy for population
to look good. **But the bank prior does not lose narrowly to a biased truth — it loses to a 2.3×
margin, and it loses to plain population (0.270 vs 0.634), which is the part of the result the prior
bias cannot explain.** CDD actively hurts regardless of the truth's prior. The conclusion is robust to
the caveat: even granting population an unfair edge, the cooling-demand idea adds no signal.

## Data-cracking confirmation (playbook rule 2)

Opened the actual NetCDFs, did not trust descriptions:

- **Posterior:** `*_EUROPE_EDGAR_PARISNID2026_hfc134a_yearly_flux.nc`, 6 members fetched + extracted
  from ICOS collection `n8myDc-I-gbHkdt3ajIYLLDe` (hashes enumerated via the ICOS metadata API,
  `CpLicenseAcceptedFor` cookie). Grid **0.234° lat × 0.352° lon** (293 × 391), 22 countries, time
  **2017–2024 (2020 present, used)**. Fields confirmed present: `flux_total_posterior`,
  `flux_total_prior`, `country_fraction`. (`flux_total_prior` ≈ EDGAR — the bias caveat above.)
- **EDGAR baseline:** `v8.0_FT2022_GHG_HFC-134a_2020_TOTALS_emi.nc`, 0.1° (1800 × 3600), global
  279.7 kt/yr. Sectors present: TOTALS, PRU_SOL (identical — HFC-134a is entirely product-use). Loaded
  from the cached EDGAR f-gases bundle (`sf6-spatial-prior/data/benchmarks/EDGAR_f-gases_emi_nc.zip`).
- **Population:** GHSL GHS-POP 2020, 30-arcsec WGS84 (JRC R2023A), sum-aggregated onto the WorldClim
  grid; 941 M people in the Europe box.
- **CDD:** computed from WorldClim 2.1 10-arcmin monthly mean-temperature climatology, EPSG:4326,
  CDD = Σ_months max(0, T_month − 18 °C) × days_in_month. Range 0–2769 °C·day (0 across N. Europe,
  ~1000–2800 across Iberia/Greece). Crude, uncalibrated, Europe-only — as the playbook prescribes.

## Decision

**NO-GO. Bank the negative.** Do not build the production HFC-134a artifact. The portfolio's prior
expectation (refrigerant-bank = diffuse/area = population-hard-to-beat) is confirmed by measurement.
A cooling-demand weighting is not merely uncompetitive; it degrades the population baseline. If HFC-134a
is ever revisited, the only plausible angle is a non-climate stock proxy (vehicle-fleet density +
commercial-refrigeration floor space), but there is no reason to expect it to separate from population
either — the gas has no point-source structure to resolve. This stays in the diffuse/parked bin with SF6.

## Reproduce

```
cd hfc134a-refrigerant-bank-prior
../sf6-spatial-prior/.venv/Scripts/python.exe src/fetch_posteriors.py   # fetch + crack the 6-member posterior
../sf6-spatial-prior/.venv/Scripts/python.exe src/build_bank_prior.py   # build pop, CDD, pop×CDD priors
../sf6-spatial-prior/.venv/Scripts/python.exe src/hfc134a_killtest.py   # the one correlation
```
(Uses the `sf6-spatial-prior/.venv` interpreter — xarray / numpy / rasterio / netCDF4.)
