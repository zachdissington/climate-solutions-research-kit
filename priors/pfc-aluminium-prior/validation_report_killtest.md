# CF4 Kill-Test Verdict — smelter prior vs population proxy, vs the ICOS 2020 CF4 posterior

> **2026-06-09 — interpretation narrowed by the holistic significance re-test**
> (`validation_report_holistic_2026-06-09.md`, canonical: `../decisions/2026-06-09-holistic-validation-verdict.md`).
> The numbers below reproduce exactly, but: Iceland is the only *statistically significant* win (block
> bootstrap + shift-null; and only the 2 RHIME members cover Iceland); the pooled win is consistent in
> direction across all 6 members but not per-member significant vs spatial autocorrelation; **the France
> "win" does not survive** (RHIME members show a significant loss; near-tie at 1°). Grid correction: the
> ICOS posterior is 0.234°×0.352°, not 0.1°. Do not quote France or the "~4×" ratio from this report.

> Run 2026-06-06 (task T-001). The cheap, decisive accuracy gate. Truth = ICOS PARIS CF4 posterior,
> year 2020, Europe, **6-member ensemble** (RHIME/InTEM/ELRIS × NAME/FLEXPART), **FLAT prior** (so the
> posterior is observation-driven, not prior-dominated). Candidates: our European smelter prior
> (capacity-weighted + presence-only) and EDGAR CF4 (TOTALS + the NFE/aluminium sector). Metric =
> spatial correlation vs `flux_total_posterior`, normalized per region. Scripts: `src/cf4_killtest.py`,
> `src/smelter_prior.py`, `src/benchmarks.py`.

## Result — corr vs ICOS 2020 CF4 posterior (ensemble mean ± sd)

| Region | OURS-cap | OURS-pres | EDGAR-TOT | EDGAR-NFE | N cells | ours beats pop? |
|---|---|---|---|---|---|---|
| **POOL (all smelter countries)** | **0.057 ± 0.02** | 0.046 ± 0.01 | 0.015 ± 0.01 | 0.012 ± 0.01 | 17,493 | **yes (~4×)** |
| **ISL** (Iceland) | **0.252 ± 0.00** | 0.217 | -0.001 | -0.001 | 1,984 | **yes (decisive)** |
| **FRA** | **0.217 ± 0.13** | 0.186 | 0.143 | 0.133 | 1,266 | **yes** |
| **DEU** | **0.048 ± 0.04** | 0.043 | 0.005 | 0.003 | 650 | **yes** |
| NOR | 0.012 | 0.015 | 0.085 | 0.085 | 6,485 | no |
| ESP | -0.006 | -0.001 | 0.030 | 0.030 | 1,897 | no |
| GBR | 0.006 | 0.006 | 0.027 | 0.022 | 1,730 | no |
| SWE / ROU / GRC | ~0.00–0.07 (ours ≈ EDGAR; one smelter each, degenerate) | | | | | tie |
| ITA | nan | nan | 0.149 | 0.040 | 1,096 | n/a (no operating smelter 2020) |

## Verdict: QUALIFIED GO — the opposite of SF6

On the claim that actually matters — *does a smelter prior disaggregate CF4 better than the
population/built-up proxy?* — **CF4 passes where SF6 failed.** Ours beats EDGAR in the pooled aggregate
(~4×, consistent across all 6 ensemble members, non-overlapping bands) and decisively where the
inversion is well-constrained (Iceland 0.25 vs ~0; France 0.22 vs 0.14; Germany 0.05 vs 0.005). This is
the structural prediction confirmed: a **point-source** gas behaves the opposite of SF6's diffuse one.

Three honest qualifiers:
1. **Absolute skill is low everywhere** (corr ~0.05–0.25). Fine-scale CF4 allocation is hard for *all*
   priors — the same ceiling SF6 hit, and exactly what the pre-build stress test predicted
   ("single-station inversions cannot reliably resolve fine spatial patterns regardless of prior").
   The win is *relative* (better than the proxy), not high absolute accuracy.
2. **Noisy where the inversion is weakly constrained.** Norway and Spain lose — not a masking artifact
   (verified: all 27 smelters sit in their own country mask, own-fraction = 1.00). Over Norway's vast,
   sparsely-observed domain the FLAT-prior posterior stays diffuse, so a point prior cannot correlate
   and a smooth field scores marginally higher by accident. The wins cluster where observations
   resolve point sources (island Iceland; dense-network France/Germany).
3. **Europe is a minor CF4 theatre.** The global CF4 signal is ~57% China; the decisive high-signal
   test is China (Liang et al. 2024), which is the deep build's job, not this European gate's.

## The premise is independently confirmed

**EDGAR-NFE ≈ EDGAR-TOT in every region** (e.g. POOL 0.012 vs 0.015; FRA 0.133 vs 0.143; ISL both
−0.001). EDGAR's *aluminium* sector is no better-correlated with the truth than its total — confirming
EDGAR grids even aluminium CF4 by the built-up/population backup proxy, **not** by smelter location.
That is precisely the gap this artifact fills, and our actual-smelter-location prior beats it.

## Consistency with prior art

Matches Kim et al. 2021 (a 127-smelter China point-source prior improved the CF4 inversion) — the
published proof-of-method that made CF4 the accuracy-first lead. The European gate independently
reproduces the direction on a 6-member modern ensemble.

## Decision

**GO to the deep build (T-002), qualified.** The relative thesis holds; proceed to the global smelter
registry + the **China validation against the Liang 2024 posterior** (the decisive high-signal test).
Gate the deep build's final ship on that China result: if China does not show a clearer win than this
noisy European theatre, reconsider. Data caveat: the European CF4 posterior is in hand (ICOS); a
**downloadable gridded China/global CF4 posterior is not yet confirmed** (Liang 2024 deposit
unverified) — sourcing it is the first step of T-002, with author request / OSSE as fallback.

## What ran (reproducible)
- `src/cf4_killtest.py` — 6-member ensemble, per-country + pooled, capacity + presence variants.
- `src/smelter_prior.py` — 27 operating-2020 European smelters → 0.1° grid (capacity + presence).
- `src/benchmarks.py` — EDGAR CF4 (TOTALS/NFE) from the cached v8.0 F-gas bundle.
- Posteriors: 6 ICOS CF4 objects (IDs in `factors/SOURCES.md`), `data/posteriors/icos/` (gitignored).

---

# C2F6 (PFC-116) leg — second PFC from the same smelters

> Run 2026-06-07 (task T-2026-06-07-003), while CF4-China is collaboration-gated. **Reuses the exact CF4
> smelter prior** (`outputs/prior_cf4_europe_{capacity,presence}.nc` — smelter locations are gas-agnostic).
> Truth = ICOS PARIS **C2F6 (pfc218)** posterior, 2020, Europe, 6-member ensemble, FLAT prior. Baseline =
> EDGAR C2F6 (TOTALS 778 t/yr; **NFE/aluminium = 450 t/yr, ~58% — aluminium is the MAJORITY EDGAR C2F6
> sector**, contrary to the pre-run "minority source" worry). Scripts: `src/c2f6_killtest.py`,
> `src/enrichment_test.py`, `src/fetch_posteriors.py`.

## Verdict: WEAK / QUALIFIED — ships low-confidence with CF4, not standalone

C2F6 is neither CF4's clean GO nor HFC-23/NF3's clean NO-GO. The smelter prior is *structurally right*
for C2F6 (it wins decisively where the inversion is well-constrained and smelters are remote — Iceland
0.252 vs ~0, same as CF4), but Europe's tiny C2F6 flux is too low-SNR to validate it cleanly pooled —
exactly the "C2F6 ships low-confidence, caveated" status the portfolio plan anticipated.

> **2026-06-13 correction:** numbers below re-derived with the exact-2020 `sel_year` fix (the
> 2026-06-07 figures had mixed 2019 into the ELRIS/InTEM members). Verdict unchanged (WEAK/QUALIFIED);
> pooled correlation now slightly favours EDGAR and the enrichment percentile reversed upward. See
> `../decisions/2026-06-07-c2f6-killtest.md` for the full correction note.

### Result 1 — spatial correlation vs the ICOS 2020 C2F6 posterior (ensemble mean, exact-2020)

| Region | OURS (best) | EDGAR-TOT | beats pop? |
|---|---|---|---|
| **ISL** (Iceland — remote, well-constrained) | **0.252** | −0.001 | **yes (decisive, as CF4)** |
| DEU | 0.120 | 0.099 | yes |
| ESP | 0.056 | 0.016 | yes |
| **POOL** | 0.013 | 0.023 | no (EDGAR edges ahead; both ≈ 0) |
| FRA | 0.026 | 0.134 | no |
| GBR | −0.003 | 0.072 | no |
| ITA | nan | 0.186 | n/a (no operating smelter 2020) |
| NOR / SWE / ROU / GRC | ≈ EDGAR (degenerate single-smelter ties) | | tie |

4/11 regions ours beats EDGAR, but the pooled correlation now goes to EDGAR; the real signal is the
decisive ISL/DEU/ESP wins against a pooled loss — **far weaker than CF4's pooled 4× (0.057 vs 0.015).**

### Result 2 — smelter-cell percentile within the pooled smelter-country domain (mean of members, exact-2020)

MEAN: **POSTERIOR 70.2% · PRIOR 68.3% · EDGAR 59.8%** (22 in-domain smelters). The C2F6 posterior now
ranks smelter cells *above* EDGAR's population proxy and slightly above its own flat-ish prior — a modest
positive smelter enrichment (the exact-2020 fix reversed the buggy POST 58.5% ≈ EDGAR reading). Individual
remote smelters rank high (Alcoa Fjardaal IS 96th, Trimet/Speira DEU 95-98th, Alcoa Spain 85-86th),
consistent with the ISL/DEU/ESP correlation wins. The enrichment metric (smelters above EDGAR) and the
pooled correlation (EDGAR edges ahead) disagree at the margin; the correlation is the primary metric.

## Why C2F6 is weaker than CF4 (honest)

C2F6 global EDGAR is only 778 t/yr (vs CF4's far larger flux), so the European C2F6 signal is even
lower-SNR; the FLAT-prior inversion can barely constrain it, leaving a noisy posterior. Aluminium *is*
the majority EDGAR C2F6 sector (58%), so the premise is sound — but the ~42% non-aluminium C2F6
(semiconductor/other, population-coincident) plus the tiny absolute flux dilute the smelter signal so the
pooled correlation lands at or just below EDGAR. The smelter prior is correct (Iceland proves it, and the
enrichment percentile now sits above EDGAR); Europe just can't validate it cleanly on the primary metric.

## Decision (C2F6 leg)

**Ship C2F6 as a LOW-CONFIDENCE companion to CF4, not a standalone GO.** Same smelter prior, decisive
only in the best-constrained remote theatres (Iceland). The clean high-signal test would be
China/East-Asia (gated). Fold C2F6 into the CF4 outreach ask (a returned East-Asia PFC posterior tests
both at once); do not build a separate C2F6 deep registry. Record: `../decisions/2026-06-07-c2f6-killtest.md`.

## What ran (C2F6 leg, reproducible)
- `src/fetch_posteriors.py` — 6 ICOS C2F6 (pfc218) objects → `data/posteriors/icos/` (gitignored).
- `src/c2f6_killtest.py` — reuses `outputs/prior_cf4_europe_*.nc`; EDGAR C2F6 TOTALS+NFE; per-country + POOL.
- `src/enrichment_test.py` — smelter-cell percentile (posterior/prior/EDGAR), operating-2020 smelters.
