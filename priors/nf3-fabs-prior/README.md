# NF3-from-Semiconductor-Fabs Spatial Prior

Tier-2 candidate in the free-value spatial-prior portfolio. An open, fab-resolved spatial prior for
**NF3** (GWP ~16,100), used in semiconductor/display/solar manufacturing, gridded by fab location
instead of EDGAR's population/built-up proxy.

**Status: KILL-TEST RUN → NO-GO, 2026-06-07.** Cleaner negative than HFC-23. Do not deep-build.
Verdict + diagnostics: `validation_report_killtest.md`. Decision: `../decisions/2026-06-07-nf3-killtest.md`.

## One-paragraph outcome

The ICOS PARIS collection carries a free 6-member European NF3 posterior. EDGAR grids NF3 by population
(premise confirmed — top cells at Vienna/Graz/Linz, not fabs). But the inversion places **no NF3
enrichment at the fab cells**: mean posterior percentile at the 11 fabs is 47.7 (below median), and the
Dresden cluster — the hoped-for tight-clustering win — sits at the 50th percentile. European NF3 is a
tiny, heavily-abated residual (Crolles substituted F2; Intel/ST run point-of-use abatement), so it isn't
fab-proportional; the real signal (73% of global growth) is East-Asian and outside the testable domain.
**This completes the Tier-1/2 sweep: CF4 GO, HFC-23 NO-GO, NF3 NO-GO** — CF4 is the lone clean win and
the only gas whose favorable structure lives in Europe.

## Reproduce

```
PY=../sf6-spatial-prior/.venv/Scripts/python.exe
$PY src/fetch_posteriors.py   # 6-member NF3 posterior ensemble
$PY src/benchmarks.py         # EDGAR NF3 (cached F-gas bundle)
$PY src/fab_prior.py          # 11-fab presence-only prior
$PY src/nf3_killtest.py       # Result 1: correlation (1/7)
$PY src/diagnose.py           # constraint + premise + Result 2 enrichment (POST 47.7 < EDGAR 84.2)
```

## Pointers

- Method: `../analysis/spatial-prior-artifact-playbook.md`
- Pre-build stress test: `../analysis/free-value-stress-tests/` (NF3 is Tier-2 in the portfolio plan)
- Sibling negatives/positives: `../hfc23-hcfc22-prior/` (NO-GO), `../pfc-aluminium-prior/` (GO, China-gated)
- Portfolio plan: `../plans/2026-06-06-free-value-portfolio-plan.md`
