# NF3 Kill-Test Verdict — semiconductor-fab prior vs population proxy, vs the ICOS 2020 NF3 posterior

> Run 2026-06-07 (NF3 gate). Cheapest decisive test, run before any build (method:
> `../analysis/spatial-prior-artifact-playbook.md`). Truth = ICOS PARIS NF3 posterior, 2020, Europe,
> **6-member ensemble** (ELRIS/InTEM/RHIME × NAME/FLEXPART), FLAT prior. Candidate = presence-only
> European fab prior (11 sites). Baseline = EDGAR NF3 (`PRU_SOL` ≡ `TOTALS`).
> Scripts: `src/nf3_killtest.py`, `src/fab_prior.py`, `src/diagnose.py`, `src/fetch_posteriors.py`,
> `src/benchmarks.py`.

## Verdict: NO-GO (a cleaner negative than HFC-23)

A fab-location prior does not beat EDGAR's population proxy for European NF3 — and worse than HFC-23,
the inversion places **no NF3 enrichment at the fab cells at all**. The fab prior points at the wrong
locations. Bank the negative. With this, the Tier-1/2 sweep is complete: **CF4 GO, HFC-23 NO-GO,
NF3 NO-GO.**

## Result 1 — spatial correlation vs the ICOS 2020 posterior (ensemble mean)

| Region | OURS-pres | EDGAR-TOT | beats pop? |
|---|---|---|---|
| **POOL** (6 fab countries) | 0.023 | **0.100** | no |
| DEU (incl. Dresden cluster) | −0.000 | 0.106 | no |
| FRA | 0.010 | 0.135 | no |
| ITA | 0.003 | 0.160 | no |
| IRL (Intel Leixlip) | 0.223 | 0.321 | no |
| NLD | 0.058 | 0.128 | no |
| AUT | 0.058 | −0.118 | yes (only region; both ≈ 0) |

**1/7** — and absolute skill is near-zero for both priors (European NF3 is hard for *any* prior,
consistent with "not significantly different from zero", Park/Rigby 2024). EDGAR is merely less wrong.

## Result 2 — fab-cell percentile rank within the pooled fab-country domain (mean of 6 members)

| Fab | POSTERIOR | PRIOR | EDGAR |
|---|---|---|---|
| Intel Leixlip (IE) | 74.9% | 59.5% | 99.8% |
| Bosch Reutlingen (DE) | 61.8% | 53.0% | 95.2% |
| ST Agrate (IT) | 61.0% | 56.8% | 99.5% |
| Infineon Villach (AT) | 53.6% | 62.1% | 98.5% |
| Infineon / GF Dresden (DE) | 50.1% | 63.6% | 83.0% |
| ST Crolles (FR) | 45.2% | 62.2% | 89.1% |
| ST Rousset (FR) | 26.1% | 58.9% | 88.0% |
| ST Catania (IT) | 0.0% | 0.0% | 99.9% |
| **MEAN** | **47.7%** | 54.7% | **84.2%** |

The decisive reading:

- **The inversion does NOT concentrate NF3 at the fabs.** Mean posterior percentile at fab cells is
  47.7 — *below median*. The flat prior was ~55th and observations pushed it slightly **down**, not up.
  Contrast HFC-23, where the posterior *rose* to the 77th percentile at the plants. For NF3 the fab
  locations carry essentially no posterior signal — including the Dresden cluster (both Dresden fabs
  sit at the 50th percentile; the "tight clustering will win" hypothesis is refuted by the data).
- **EDGAR is high at the fabs (84th) only because fabs are urban and EDGAR is population/built-up** —
  but EDGAR's overall correlation with the posterior is also weak (0.10). Population is a poor proxy
  here too; the fab prior is just poorer.

## Premise gate (confirmed at source, this run)

- EDGAR NF3 is **population/built-up shaped**: its top European cells are Austrian population centres
  (Vienna 48.15/16.35, Graz 47.05/15.45, Linz 48.25/14.25) — *not* the fabs (not even Villach, the
  actual Austrian fab). EDGAR's v8 point-source layer covers power/steel/coal/flaring, not semiconductor
  fabs (Crippa et al. ESSD 2024), so NF3 falls to the built-up/population backup proxy. Gap is real;
  the fab prior just doesn't fill it in Europe.
- EDGAR NF3 global 2020 = 142.6 t/yr — and the inversion literature finds EDGAR NF3 is >10× too low
  (Park/Rigby 2024). EDGAR is both under-counted and spatially smeared.

## Why NF3 fails (and what it adds to the portfolio thesis)

European NF3 is a tiny, **heavily-abated residual**: Crolles replaced NF3 with on-site F2 (~2017), and
Intel Leixlip / STMicro run point-of-use abatement. So the little NF3 Europe emits is not fab-throughput
proportional, and the inversion sees no fab signal. The real NF3 signal — 73% of global growth — is in
**East Asia** (Korea/Taiwan/China display + semiconductor), outside the ICOS European domain, with no
public gridded posterior (Park/Rigby 2024 treat Europe as one aggregated near-zero region; no facility
grid exists).

This sharpens the 2026-06-07 portfolio lesson (`../decisions/2026-06-07-hfc23-killtest.md`): not only
must a candidate be **point-source AND away from population**, the **emitting signal must actually live
in the testable (European) domain.** NF3 fails on the last clause — abatement + East-Asia concentration
leave Europe with no fab-shaped signal to test.

## Decision

**NO-GO. Do not deep-build NF3.** The Tier-1/2 sweep is complete. The free ICOS Europe test engine has
yielded exactly one clean GO (CF4), which is also the one gas whose favorable structure (smelters away
from population) lives in Europe. HFC-23 and NF3 both have their real signal in East-Asia, gated behind
the same data wall as CF4-China. **Recommendation: stop mining Europe-domain gates; treat CF4 as the
portfolio's asset; let next week's CF4 outreach drive.** A returned East-Asia F-gas posterior would
unlock CF4 and let HFC-23 + NF3 be re-tested in China at near-zero marginal cost on this same harness.

## Caveats

- Presence-only weighting (per-site NF3 unsourced; abatement decouples emission from throughput —
  see `factors/SOURCES.md`). Coordinates are address/town-level (research-grade for a kill-test).
- Edge effects: ST Catania (Sicily) and the NLD EDGAR cell sit at domain edges / near-zero EDGAR
  allocation; they do not change the POOL result (ours 0.023 vs EDGAR 0.100) or the mean enrichment.
- The European NF3 posterior IS constrained (moved 60–112% off the flat prior), so this is a real test,
  not an unconstrained-relaxation artifact.
