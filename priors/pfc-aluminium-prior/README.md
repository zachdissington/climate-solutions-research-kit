# PFC-CF4-from-Aluminium-Smelters Spatial Prior

Second artifact in the free-value spatial-prior portfolio. An open, smelter-resolved spatial prior for
primary-aluminium **PFCs** — **CF4 lead, C2F6 secondary/low-confidence** — a better disaggregation than
the population/built-up proxy EDGAR and the PFC atmospheric-inversion community (AGAGE/Bristol/MIT) use
today.

**Status (2026-06-09):** Holistic pre-handoff validation DONE — claims recalibrated (Iceland = the
one significant Europe win; pooled = consistent direction 6/6 members, not per-member significant;
**France no longer claimed**), deposit repaired (registry Europe-complete at 94 smelters; new
production-rescaled global variant fixes China 28%→56.7% weight share; attrs on every NetCDF), email
v2 rewritten honest on the attribution link. Zenodo draft 20617486 synced (11 files) — **publish +
send gated on Zach**. See `validation_report_holistic_2026-06-09.md` +
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
