# PFC-CF4-from-Aluminium-Smelters Spatial Prior

Second artifact in the free-value spatial-prior portfolio. An open, smelter-resolved spatial prior for
primary-aluminium **PFCs** — **CF4 lead, C2F6 secondary/low-confidence** — a better disaggregation than
the population/built-up proxy EDGAR and the PFC atmospheric-inversion community (AGAGE/Bristol/MIT) use
today.

**Status (2026-06-18):** Published and citable. The dataset is on Zenodo under the **concept DOI
[10.5281/zenodo.20617485](https://doi.org/10.5281/zenodo.20617485)** (CC-BY-4.0; always cite the concept
DOI — it resolves to the latest version, currently v3 with the exact-2020 corrections), and the code is
archived at [10.5281/zenodo.20683507](https://doi.org/10.5281/zenodo.20683507) (MIT). An ESSD data
descriptor is in preparation. Claims are recalibrated (Iceland = the one significant Europe win; pooled =
consistent direction in 5 of 6 members, not per-member significant; **France not claimed**); the registry
is Europe-complete at 94 smelters with a production-rescaled global variant (fixes China 28%→56.7% weight
share). Validation re-verified 2026-06-18 — see `validation_report_holistic_2026-06-18.md` +
`../decisions/2026-06-09-holistic-validation-verdict.md`. China validation stays collaboration-gated.
C2F6 leg = **WEAK / QUALIFIED** (ships low-confidence with CF4): `../decisions/2026-06-07-c2f6-killtest.md`.

## Why this one (the accuracy-first pick)

Selected as the portfolio lead because it is the rare candidate that is high-impact AND already proven
accurate. CF4 inversions run ~2.6× over EDGAR (China-dominant); the ~150 finite primary smelters sit
away from population peaks; and Kim et al. 2021 already demonstrated a smelter point-source prior
improves the inversion. This is the structural opposite of SF6 (which failed because its substation
proxy was diffuse).

## Scope guardrails

1. Spatial prior with uncertainty bands, not an emissions ledger.
2. CF4 is the deliverable; C2F6 ships low-confidence and caveated (aluminium is a minority C2F6 source).
3. Validation = beat the population/built-up proxy vs a CF4 inversion posterior; calibrate to totals.
4. Geography honesty: China = the value (low-confidence where smelter tech data is partial).

## Pointers

- C2F6 leg — ship-ready caveat + gate (low-confidence companion, **not** a separate build): `C2F6-COMPANION.md`
- Build plan + phasing + reuse map: `plans/2026-06-06-pfc-cf4-build.md`
- Authorizing decision: `../decisions/2026-06-06-frame-committed-pfc-cf4-lead.md`
- Method (how to build one): `../analysis/spatial-prior-artifact-playbook.md`
- Why this gas survives (sources): `../analysis/free-value-stress-tests/pfc-aluminium.md`
- Portfolio context: `../plans/2026-06-06-free-value-portfolio-plan.md`
- Code to reuse: `../sf6-spatial-prior/src/` (kill-test harness `icos_metric.py` / `phase2b.py` are
  gas-agnostic; see the build plan's reuse map)

## Layout (mirrors sf6-spatial-prior/; populated during the build)

`src/` · `factors/` (+ `SOURCES.md`) · `data/` (gitignored) · `outputs/` (gitignored) · `tasks/` ·
`plans/` · validation reports at the root.

## Running

Install pinned deps first: `pip install -r requirements.txt` (numpy / xarray / netCDF4 / matplotlib;
built + validated against those versions).

Run every script **as `python src/<script>.py` from the prior root** (this directory). The scripts use
bare intra-package imports (`import benchmarks`, `from cf4_killtest import ...`), which only resolve when
`src/` is on `sys.path` — running `python src/<script>.py` puts `src/` there automatically, so no install
or `PYTHONPATH` is needed. (Equivalently, `cd src && python <script>.py`.) They are deliberately NOT a
package, so `python -m src.<script>` does **not** work.

Inputs (both large + gitignored, regenerated on a clean clone):

- CF4 posteriors — `python src/fetch_cf4_posteriors.py` (the six ICOS CF4 members; writes
  `data/posteriors/icos/*cf4_yearly_flux.nc`, which the validation scripts glob for).
- C2F6 posteriors — `python src/fetch_posteriors.py` (the C2F6 leg).
- EDGAR v8.0 F-gases baseline — see `src/benchmarks.py` docstring for retrieval (DOI
  10.2905/b54d8149-2864-4fb9-96b9-5fd3a020c224); resolved via `$EDGAR_ZIP` / local cache / SF6 cache.

Validation entry points (after inputs are present): `python src/cf4_killtest.py`,
`python src/holistic_significance.py`, `python src/enrichment_v2.py`.
