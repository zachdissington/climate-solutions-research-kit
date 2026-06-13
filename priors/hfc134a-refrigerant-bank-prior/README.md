# HFC-134a refrigerant-bank spatial prior — kill-test (NO-GO)

A cheapest-decisive-test of whether a **population × climatological cooling-degree-days** refrigerant-bank
prior beats the population proxy (EDGAR) as a spatial prior for European HFC-134a atmospheric inversions.

**Result: NO-GO** (v2, 2026-06-12 — a year-selection bug in v1 was found and fixed in an adversarial
audit; corrected numbers below, qualitative verdict unchanged; changelog in
`validation_report_killtest.md`). The bank prior beats population in 0 of 11 scoreable countries
(unscoreable — zero variance — in 4 more); pooled corr 0.237 (BANK) vs 0.616 (population) vs 0.655
(EDGAR), exact-2020. The climatological-CDD weighting *degrades* the population baseline. HFC-134a is a
diffuse, population-coupled source (the SF6 failure mode), not a point source (the CF4 success mode).
Full verdict, prior-anchoring caveat, and what-would-overturn-this list:
`validation_report_killtest.md`.

## Layout
- `src/fetch_posteriors.py` — fetch + crack the 6-member ICOS PARIS HFC-134a posterior ensemble.
- `src/benchmarks.py` — EDGAR HFC-134a baseline loader (reuses the cached f-gases bundle).
- `src/build_bank_prior.py` — build the pop, CDD, and pop×CDD priors over Europe.
- `src/hfc134a_killtest.py` — the one correlation (per-country + pooled vs the posterior; exact-2020
  selection asserted).
- `src/audit_year_bug.py` — the 2026-06-12 audit script (time-axis check, shipped-vs-corrected diff,
  output regeneration check).
- `data/` — posteriors (ICOS), EDGAR extract, inputs (WorldClim tavg, GHSL population).
- `outputs/` — the gridded priors (NetCDF).

## Run
```
../sf6-spatial-prior/.venv/Scripts/python.exe src/fetch_posteriors.py
../sf6-spatial-prior/.venv/Scripts/python.exe src/build_bank_prior.py
../sf6-spatial-prior/.venv/Scripts/python.exe src/hfc134a_killtest.py
```

## Data and licenses
- Posterior: ICOS PARIS F-gas collection `n8myDc-I-gbHkdt3ajIYLLDe` (DOI 10.18160/GR1Q-6SK4),
  CC-BY-4.0; cite Ganesan et al. (2026). HFC-134a, Europe, 2013/2017–2024, grid 0.234°×0.352°.
  NB: EDGAR-prior inversion (anchoring caveat in the verdict).
- EDGAR v8.0 HFC-134a (Crippa et al. 2024, ESSD 16, 2811–2830; dataset
  doi:10.2905/b54d8149-2864-4fb9-96b9-5fd3a020c224).
- Population: GHSL GHS-POP 2020 30ss WGS84, JRC R2023A (Schiavina et al. 2023,
  doi:10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE), CC-BY-4.0.
- Temperature: WorldClim 2.1 10-arcmin monthly tavg climatology (Fick & Hijmans 2017).
  **License note:** WorldClim is free for academic/non-commercial use and may not be redistributed
  without permission. The derived files `outputs/cdd_europe.nc` and
  `outputs/prior_hfc134a_europe_bank.nc` embed WorldClim-derived values and therefore carry WorldClim's
  restrictions, NOT this project's CC-BY license — regenerate them locally via
  `src/build_bank_prior.py` for any use beyond academic/non-commercial. The population-only prior and
  all code remain CC-BY/MIT respectively.
