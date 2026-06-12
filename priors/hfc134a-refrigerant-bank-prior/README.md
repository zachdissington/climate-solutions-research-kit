# HFC-134a refrigerant-bank spatial prior — kill-test (NO-GO)

A cheapest-decisive-test of whether a **population × cooling-degree-days** refrigerant-bank prior beats
the population proxy (EDGAR) as a spatial prior for European HFC-134a atmospheric inversions.

**Result: NO-GO.** The bank prior loses to population in 0/16 countries; pooled corr 0.270 (BANK) vs
0.634 (population) vs 0.671 (EDGAR). CDD *degrades* the population baseline. HFC-134a is a diffuse,
population-coupled source (the SF6 failure mode), not a point source (the CF4 success mode). Full
verdict + honest conservative-test caveat: `validation_report_killtest.md`.

## Layout
- `src/fetch_posteriors.py` — fetch + crack the 6-member ICOS PARIS HFC-134a posterior ensemble.
- `src/benchmarks.py` — EDGAR HFC-134a baseline loader (reuses the cached f-gases bundle).
- `src/build_bank_prior.py` — build the pop, CDD, and pop×CDD priors over Europe.
- `src/hfc134a_killtest.py` — the one correlation (per-country + pooled vs the posterior).
- `data/` — posteriors (ICOS), EDGAR extract, inputs (WorldClim tavg, GHSL population).
- `outputs/` — the gridded priors (NetCDF).

## Run
```
../sf6-spatial-prior/.venv/Scripts/python.exe src/fetch_posteriors.py
../sf6-spatial-prior/.venv/Scripts/python.exe src/build_bank_prior.py
../sf6-spatial-prior/.venv/Scripts/python.exe src/hfc134a_killtest.py
```

## Data
- Posterior: ICOS PARIS F-gas collection `n8myDc-I-gbHkdt3ajIYLLDe` (DOI 10.18160/GR1Q-6SK4),
  CC-BY-4.0. HFC-134a, Europe, 2017–2024, grid 0.234°×0.352°. NB: EDGAR-prior inversion.
- EDGAR v8.0 HFC-134a (cached in `sf6-spatial-prior/data/benchmarks/`).
- WorldClim 2.1 10-arcmin monthly tavg (CDD). GHSL GHS-POP 2020 30ss WGS84 (population).
