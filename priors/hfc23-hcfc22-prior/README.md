# HFC-23-from-HCFC-22-Plants Spatial Prior

Third artifact attempted in the free-value spatial-prior portfolio (`../plans/2026-06-06-free-value-portfolio-plan.md`).
An open, plant-resolved spatial prior for **HFC-23** (GWP ~12,400), an unavoidable by-product of
HCFC-22 manufacture, gridded by HCFC-22 production-plant location instead of EDGAR's population proxy.

**Status: KILL-TEST RUN → NO-GO (informative negative), 2026-06-07.** Do not deep-build.
Verdict + full diagnostics: `validation_report_killtest.md`. Decision record:
`../decisions/2026-06-07-hfc23-killtest.md`.

## One-paragraph outcome

The ICOS PARIS collection turned out to carry a free 6-member European **HFC-23 posterior** (no
collaboration wall for the Europe gate, unlike CF4-China). The inversion independently localizes HFC-23
to our plant cells (Spinetta Marengo 99th percentile, Dordrecht 92nd — observation-driven, not inherited
from the prior), confirming the physical premise. **But a plant-location prior does not beat EDGAR's
population proxy in Europe**, because European HCFC-22 plants are integrated chemical complexes sited
*inside* populated industrial regions — population already predicts them. This is the structural
opposite of CF4, whose aluminium smelters sit *away* from population. The portfolio lesson: the real
selection axis is "point-source **and sited away from population**," not point-source alone. The only
region where a plant prior might still win (East-Asia / China, the 5× gap) has no public gridded
posterior (Park 2023 / Western 2024 are figures-only).

## Layout

`src/` (fetch_posteriors · benchmarks · plant_prior · hfc23_killtest · diagnose · enrichment_test) ·
`factors/` (+ `SOURCES.md`, `hcfc22_plants_europe.csv`) · `data/` (posteriors + EDGAR, gitignored) ·
`outputs/` (gitignored) · `validation_report_killtest.md`.

## Reproduce

```
PY=../sf6-spatial-prior/.venv/Scripts/python.exe   # reuses the SF6/CF4 venv (numpy, xarray, netCDF4)
$PY src/fetch_posteriors.py     # download + crack the 6-member HFC-23 posterior ensemble
$PY src/benchmarks.py           # confirm EDGAR HFC-23 loads (cached F-gas bundle)
$PY src/plant_prior.py          # grid the 5-plant presence-only prior
$PY src/hfc23_killtest.py       # Result 1: spatial correlation (0/6, metric under-scores one-hot prior)
$PY src/enrichment_test.py      # Result 2: plant-cell percentile rank — the decisive metric
$PY src/diagnose.py             # premise + constraint diagnostics
```

## Pointers

- Method: `../analysis/spatial-prior-artifact-playbook.md`
- Pre-build stress test (predicted both WOUNDS): `../analysis/free-value-stress-tests/hfc23-hcfc22.md`
- Sibling artifact (the CF4 GO this is contrasted against): `../pfc-aluminium-prior/`
- Build plan: `../plans/2026-06-07-hfc23-killtest.md`
