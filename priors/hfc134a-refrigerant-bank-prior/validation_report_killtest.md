# HFC-134a refrigerant-bank prior — kill-test verdict: NO-GO

Date: 2026-06-11. **v2, 2026-06-12** — adversarial audit revision; see "v1 → v2 changes" at the end.
Gas: HFC-134a (the dominant refrigerant: mobile A/C, commercial + domestic refrigeration)
Candidate prior: **bank ∝ population × cooling-degree-days (CDD)** — a crude in-use-stock proxy.
Truth: ICOS PARIS HFC-134a inversion posterior, 2020, Europe, 6-member ensemble
(RHIME / InTEM / ELRIS × NAME / FLEXPART).

## VERDICT: NO-GO. The population×CDD bank prior loses to population everywhere it is defined — and the climatological-CDD weighting makes it *worse* than population alone.

Pooled spatial correlation vs the posterior (ensemble mean ± sd across the 6 members), masked by
`country_fraction ≥ 0.5`, per-region normalized, exact-2020 fields:

| Prior | Pooled corr | Reading |
|---|---|---|
| **BANK** (pop × CDD) | **0.237 ± 0.06** | our candidate — worst of the four |
| **POP** (population only) | **0.616 ± 0.09** | population alone beats the bank prior by ~2.6× |
| **EDGAR** HFC-134a TOTALS | **0.655 ± 0.09** | EDGAR (population-weighted) wins |
| PRIOR (inversion's own EDGAR prior) | **0.687 ± 0.10** | the anchoring reference — see the caveat section |

**0 of 11 scoreable countries** had the bank prior beat population or EDGAR; in **4 more** (GBR, NLD,
SWE, NOR) the bank prior is unscoreable (identically zero → no spatial variance → correlation
undefined); including the pooled domain, 0 of 16 regions.

### Per-country (BANK / POP / EDGAR / PRIOR), corr vs 2020 posterior, mean ± sd

```
  FRA: BANK 0.516±0.06  POP 0.674±0.11  EDGAR 0.759±0.04  PRIOR 0.801±0.05   (N=1266)
  ESP: BANK 0.566±0.05  POP 0.576±0.07  EDGAR 0.625±0.11  PRIOR 0.629±0.12   (N=1897)
  DEU: BANK 0.359±0.08  POP 0.651±0.09  EDGAR 0.724±0.09  PRIOR 0.753±0.11   (N=650)
  ITA: BANK 0.463±0.08  POP 0.493±0.05  EDGAR 0.605±0.05  PRIOR 0.618±0.04   (N=1096)
  GBR: BANK   nan       POP 0.712±0.03  EDGAR 0.748±0.06  PRIOR 0.774±0.04   (N=1730)
  NLD: BANK   nan       POP 0.635±0.12  EDGAR 0.744±0.14  PRIOR 0.812±0.14   (N=165)
  BEL: BANK 0.445±0.07  POP 0.634±0.08  EDGAR 0.751±0.05  PRIOR 0.789±0.05   (N=52)
  POL: BANK 0.451±0.07  POP 0.720±0.03  EDGAR 0.809±0.14  PRIOR 0.836±0.16   (N=553)
  GRC: BANK 0.638±0.03  POP 0.668±0.02  EDGAR 0.960±0.03  PRIOR 0.999±0.00   (N=752)
  PRT: BANK 0.326±0.09  POP 0.544±0.07  EDGAR 0.702±0.07  PRIOR 0.691±0.07   (N=1919)
  CHE: BANK 0.115±0.19  POP 0.317±0.24  EDGAR 0.323±0.30  PRIOR 0.378±0.25   (N=57)
  AUT: BANK 0.266±0.27  POP 0.446±0.24  EDGAR 0.639±0.20  PRIOR 0.654±0.22   (N=122)
  ROU: BANK 0.463±0.04  POP 0.532±0.04  EDGAR 0.597±0.04  PRIOR 0.629±0.04   (N=374)
  SWE: BANK   nan       POP 0.613±0.15  EDGAR 0.778±0.11  PRIOR 0.806±0.17   (N=1259)
  NOR: BANK   nan       POP 0.742±0.19  EDGAR 0.794±0.15  PRIOR 0.861±0.19   (N=6485)
  POOL: BANK 0.237±0.06 POP 0.616±0.09  EDGAR 0.655±0.09  PRIOR 0.687±0.10   (N=18377)
```

The four `nan` countries are a property of the proxy **construction**, not of the climate: CDD here is
computed from the WorldClim 1970–2000 *monthly-mean* climatology, and monthly means in maritime/Nordic
Europe never cross the 18 °C base even though daily temperatures routinely do (true daily-basis CDD for
the UK is small but nonzero, on the order of 30–100 K·day/yr, and higher by 2020 than in the 1970–2000
baseline). Multiplying population by this climatological CDD drives the bank prior to a constant zero
across maritime/Nordic Europe — no spatial variance, correlation undefined. A daily-resolution CDD would
remove the degeneracy (while still down-weighting northern banks heavily against comparable per-capita
stocks). The four unscoreable countries remain inside the pooled domain (52% of pooled cells); excluding
them entirely, BANK 0.262 / POP 0.579 / EDGAR 0.625 — the verdict is unchanged, so the pooled loss is
real cross-country misallocation (climatological CDD over-weights Iberia/Greece against
population-scale northern emissions), not an artifact of the zero cells.

## Why it failed (the diffuse-source / wrong-proxy mode)

1. **Climatological CDD is the wrong stock weight.** The HFC-134a refrigerant bank is *not*
   concentrated where cooling demand is highest. The installed stock — mobile A/C in every car fleet,
   supermarket and cold-chain refrigeration, domestic fridges — tracks population and economic
   activity, and runs in cold countries as much as warm ones. Weighting by climatological CDD throws
   away the cold-country bank entirely and over-weights the warm south, both of which move the prior
   *away* from the posterior. POP alone (0.616) cleanly beats BANK (0.237): the CDD multiplier is pure
   degradation. Even in the warm south where CDD is large and varying (ESP, ITA, GRC), the bank prior
   adds nothing over population — near-ties at best.

2. **HFC-134a is a diffuse, population-coupled source — the SF6 failure mode, not the CF4 success
   mode.** This was the a-priori risk flagged in the portfolio plan ("HFC refrigerant-bank … parked,
   diffuse/area candidate"). The kill-test confirms it: there are no point sources to resolve. The gas
   is emitted from millions of distributed appliances that co-locate with people. Population is very
   hard to beat, exactly as it was for SF6 in switchgear. A facility/infrastructure prior only wins
   when the real emitters are concentrated *away* from population (CF4 smelters); refrigerant banks
   are the opposite.

## Conservative-test caveat — what the prior anchoring can and cannot explain

Unlike HFC-23 (FLAT prior), this HFC-134a inversion used an **EDGAR/population-weighted prior** — the
posterior files carry `EDGAR` in their names (`*_EUROPE_EDGAR_PARISNID2026_*`). The PRIOR column above
measures the anchoring directly: the posterior correlates with its own prior at 0.687 pooled, with a
median around 0.75 across countries and essentially total anchoring in Greece (0.999) and strong
anchoring across Scandinavia (0.81–0.86). That has two consequences, stated symmetrically:

- **It inflates POP's and EDGAR's correlations mechanically.** Wherever observations are weak, the
  posterior *is* the population-shaped prior, and a population-shaped candidate gets free correlation.
  Quantitatively, anchoring of this strength could produce a gap of roughly the observed order against
  a non-population-shaped candidate even if the truth were bank-shaped — so the v1 claim that the
  margin is one "the prior bias cannot explain" was wrong and is withdrawn. The per-country rows for
  strongly anchored countries (GRC especially) should be read as prior-dominated, not observational.
- **What the negative actually rests on:** (i) the burden of proof sits with the candidate prior, and
  it produced zero positive evidence anywhere — including in the least-anchored countries (CHE,
  anchoring 0.378: BANK 0.115 vs POP 0.317) and in the warm south where its CDD signal is
  well-defined; (ii) the companion CF4 test demonstrates this harness *can* detect a real prior
  improvement when one exists; (iii) the bank prior sits at or below even what a bank-shaped-truth
  scenario would predict for it under this anchoring. The honest summary is "no evidence of
  improvement under a test with reduced but nonzero power," not "decisively refuted against an
  unbiased truth."

## Data-cracking confirmation (playbook rule 2)

Opened the actual NetCDFs, did not trust descriptions:

- **Posterior:** `*_EUROPE_EDGAR_PARISNID2026_hfc134a_yearly_flux.nc`, 6 members fetched + extracted
  from ICOS collection `n8myDc-I-gbHkdt3ajIYLLDe` (hashes enumerated via the ICOS metadata API,
  `CpLicenseAcceptedFor` cookie). Grid **0.234° lat × 0.352° lon** (293 × 391), time 2017–2024
  (FLEXPART) / 2013–2024 (NAME), **exact-2020 fields selected by slice with an assertion** (see
  "v1 → v2 changes"). Fields confirmed present: `flux_total_posterior`, `flux_total_prior`,
  `country_fraction`.
- **EDGAR baseline:** `v8.0_FT2022_GHG_HFC-134a_2020_TOTALS_emi.nc`, 0.1° (1800 × 3600), global
  279.7 kt/yr. Sectors present: TOTALS, PRU_SOL (identical values — HFC-134a is entirely product-use).
- **Population:** GHSL GHS-POP 2020, 30-arcsec WGS84 (JRC R2023A), sum-aggregated onto the WorldClim
  grid; 941 M people in the Europe box.
- **CDD:** computed from WorldClim 2.1 10-arcmin monthly mean-temperature climatology (1970–2000),
  EPSG:4326, CDD = Σ_months max(0, T_month − 18 °C) × days_in_month. Range 0–2769 °C·day. Crude,
  uncalibrated, Europe-only — as the playbook prescribes; see the degeneracy note above for what
  "monthly climatological CDD" does and does not measure.

## Decision

**NO-GO. Bank the negative.** Do not build the production HFC-134a artifact. The portfolio's prior
expectation (refrigerant-bank = diffuse/area = population-hard-to-beat) is confirmed by measurement,
within the scope tested. A multiplicative climatological-CDD weighting is not merely uncompetitive; it
degrades the population baseline. This stays in the diffuse/parked bin with SF6.

**What would overturn this negative** (none tested here; listed for the next person):
1. A **daily-resolution CDD** (removes the monthly-climatology degeneracy — the most direct falsifier).
2. A **mixed weighting** pop × (a + b·CDD) with small b (this test ran only the b→∞ extreme).
3. A **non-climate stock proxy** (vehicle-fleet density + commercial-refrigeration floor space) — though
   there is no strong reason to expect it to separate from population.
4. A **flat-prior or non-EDGAR-prior HFC-134a posterior** (removes the anchoring limitation entirely).

## Reproduce

```
cd hfc134a-refrigerant-bank-prior
../sf6-spatial-prior/.venv/Scripts/python.exe src/fetch_posteriors.py   # fetch + crack the 6-member posterior
../sf6-spatial-prior/.venv/Scripts/python.exe src/build_bank_prior.py   # build pop, CDD, pop×CDD priors
../sf6-spatial-prior/.venv/Scripts/python.exe src/hfc134a_killtest.py   # the one correlation
```
(Uses the `sf6-spatial-prior/.venv` interpreter — xarray / numpy / rasterio / netCDF4.)

## Data citations

- ICOS PARIS inversion collection: Ganesan, A., Manning, A., Henne, S., De Longueville, H., Ramsden, A.,
  Brito Melo, D., Danjou, A., Andrews, P., Murphy, B., Redington, A., Pitt, J. (2026): Inverse modelling
  results for European non-CO2 greenhouse gas emissions. ICOS ERIC — Carbon Portal.
  https://doi.org/10.18160/GR1Q-6SK4 (CC-BY-4.0).
- EDGAR v8.0: Crippa, M., et al. (2024): Insights into the spatial distribution of global, national, and
  subnational greenhouse gas emissions in EDGAR v8.0. Earth Syst. Sci. Data 16, 2811–2830,
  doi:10.5194/essd-16-2811-2024; gridmaps dataset doi:10.2905/b54d8149-2864-4fb9-96b9-5fd3a020c224.
- Population: Schiavina, M., Freire, S., Carioli, A., MacManus, K. (2023): GHS-POP R2023A. European
  Commission JRC [dataset], doi:10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE (CC-BY-4.0).
- Temperature climatology: Fick, S.E. and Hijmans, R.J. (2017): WorldClim 2: new 1-km spatial resolution
  climate surfaces for global land areas. Int. J. Climatol. 37(12), 4302–4315. **WorldClim 2.1 is
  free for academic/non-commercial use and may not be redistributed without permission — see the
  license note in README.md regarding the derived CDD/bank NetCDFs.**

## v1 → v2 changes (adversarial audit, 2026-06-12)

1. **Year-selection bug fixed; all numbers recomputed.** v1 selected the posterior year with
   `sel(time="2020", method="nearest")`; the ELRIS and InTEM members carry mid-year time stamps
   equidistant between 2020-01-01 and the 2019/2020 fields, and the tie resolved to **2019** — so v1's
   numbers (pooled BANK 0.270 / POP 0.634 / EDGAR 0.671) were computed from a 4×2019 + 2×2020 mixture
   while labeled "2020". v2 selects exact-2020 with an assertion; corrected pooled values are
   **0.237 / 0.616 / 0.655**. Every per-country value shifted in the second decimal; the qualitative
   verdict (0 wins anywhere; bank loses pooled by ~2.6×) is unchanged.
2. **Northern-zero re-attributed.** v1 presented zero CDD in GBR/NLD/SWE/NOR as a climate fact ("not a
   bug — it is the failure mechanism"); it is a property of monthly-climatology CDD, stated as such, with
   the pool-excluding-degenerates robustness check (0.262 / 0.579 / 0.625) added.
3. **"Margin the prior bias cannot explain" withdrawn.** The PRIOR anchoring column is now published;
   anchoring of the measured strength could produce a gap of the observed order. The negative now rests
   on burden-of-proof, zero positive evidence anywhere (including least-anchored countries), and the
   companion CF4 positive control.
4. **"0 of 16 scored countries" corrected** to 0 of 11 scoreable countries + 4 unscoreable + pool.
5. Ensemble ± sd values filled in; "what would overturn this" list added; formal data citations added;
   WorldClim license restriction flagged.
