# CF4 China/Global Test vs the Püschel Posterior — Verdict: INCONCLUSIVE (not refuted)

> Run 2026-06-06 (T-002 Phase A). Truth attempted = Püschel et al. 2025 global CF4 posterior
> (`emis_post`, 1°, 2006–2023; deposit phaidra.751, CC-BY-NC, **preprint**). Candidate = global
> smelter prior (88 operating smelters). Baseline = EDGAR CF4. Scripts: `src/puschel_killtest.py`,
> `src/global_prior.py`. Years 2018–2023 mean.

## Result (as computed)

| Region | OURS-cap | OURS-pres | EDGAR | ours vs EDGAR-correction | N |
|---|---|---|---|---|---|
| **CHINA** | 0.092 | — | **0.294** | −0.056 | 1810 |
| GLOBAL | 0.080 | — | 0.252 | −0.044 | 19782 |
| EUROPE | 0.156 | 0.150 | 0.550 | −0.136 | 1556 |
| GULF | 0.879 | — | 0.952 | −0.450 | 162 |
| INDIA | −0.008 | — | 0.541 | −0.121 | 329 |
| RUSSIA | 0.441 | — | 0.466 | +0.267 | 3535 |
| CANADA | 0.052 | — | 0.009 | — | 1415 |

Taken at face value, the smelter prior loses to EDGAR in China and globally. **But these numbers are
not a valid test of the thesis**, for two independent reasons — both data problems, neither a thesis
problem.

## Why this is INCONCLUSIVE, not a refutation

**1. The Püschel posterior is EDGAR-prior-dominated (circularity).** Püschel's prior was EDGAR
F-gases v2024, and a globally weakly-constrained inversion at 1° stays close to its prior. The evidence
is direct: EDGAR correlates 0.25–0.95 with this "posterior" (Gulf 0.95 — physically implausible for a
population/built-up proxy against a real posterior), and Püschel-Europe says ours *loses* to EDGAR
(0.16 vs 0.55) while the **clean flat-prior ICOS European posterior says ours *beats* EDGAR** (T-001).
Two posteriors for the same region give opposite answers — the EDGAR-priored one is grading EDGAR
against itself. Scoring the artifact against it would be the exact prior-dominated-truth mistake the SF6
post-mortem exists to prevent.

**2. The China smelter registry is badly incomplete.** The registry agent obtained ~12 of China's
~120 primary smelters (GEM rate-limited it after 3 facilities). China is ~57% of global CF4, so "ours"
is missing the large majority of the Chinese signal — it is handicapped by missing input data, not by
being spatially wrong. A fair China test needs a near-complete China registry.

**3. The de-confounded metric can't be computed cleanly in China.** Püschel hand-adjusted its China
prior (Guo et al. 2023), so "posterior − EDGAR-v8" is not the inversion's true observation-driven
correction in China — it conflates the Guo adjustment with the obs correction. (Russia is the one region
with a positive correction-direction, +0.267 — a small hint the method tracks the inversion's departure
from EDGAR where the prior baseline is clean and big smelters exist, e.g. RUSAL Siberia.)

## What the clean evidence actually says (unchanged)

- **ICOS Europe (T-001), flat-prior, no circularity:** the smelter prior **beats** EDGAR in aggregate
  and decisively where the inversion resolves (Iceland 0.25 vs 0; France 0.22 vs 0.14). Qualified win.
- **Kim et al. 2021 (published):** a 127-smelter China point-source prior improved the CF4 inversion.
- So CF4 is **not refuted** — it is the opposite of SF6. What is missing is an *independent, clean,
  China-scale confirmation*, which the only downloadable China-resolved posterior (Püschel) cannot
  provide, and which the non-downloadable clean China inversion (Liang 2024) could.

## Verdict

**INCONCLUSIVE for China from public data.** The decisive China test is not cleanly runnable today: the
one downloadable China-resolved CF4 posterior is EDGAR-prior-dominated, and our China registry is
incomplete. This mirrors the SF6 finding that fine-scale F-gas-prior validation is structurally
collaborative — but with the crucial difference that CF4's *clean* evidence (ICOS Europe + Kim 2021)
**supports** the prior rather than refuting it.

## Options (Zach's call — accuracy-first)

1. **Get a clean China test** — request the Liang 2024 gridded China posterior (Minde An
   / Bo Yao) AND complete the China smelter registry (~120 smelters; needs a GEM
   pull that isn't rate-limited, or Antaike/CNIA data). Then run the same harness. This is the path to a
   definitive China GO/NO-GO.
2. **Build on the clean evidence we have** — proceed to a Europe-scoped deep build (ICOS-validated,
   honest, modest) + cite Kim 2021 for China; defer the China-scale claim to option 1.
3. **Pause** the artifact at "promising, Europe-validated, China-pending" and bank it — re-engage when
   a clean China posterior is obtainable (or via an OSSE with the Vienna/Bristol groups).

Recommendation: **option 1 or 2, not the full global deep build yet.** Under the accuracy-first bar, do
not ship a global China-scale CF4 product on a test that the data can't clean. The artifact is alive and
the opposite of SF6 — but its China claim is not yet earned.

## Update 2026-06-06 — public data exhausted, outreach drafted
A 3-angle exhaustive scrape (Western repos; Chinese repositories + Chinese-language; Püschel deposit
forensic) confirmed no clean China-resolved gridded CF4 posterior is publicly downloadable, and that
Püschel deposited no prior/uncertainty field to de-confound the global test. The ideal tests exist but
are figures-only (Kim 2021 smelter-prior East-Asia inversion; An/Liang 2024 nightlights-prior China).
Clean China verdict is collaboration-gated. Drafted (Zach to send): data request to An/Yao + Kim, and an
OSSE feeler to Püschel/Stohl — `outreach/2026-06-06-*.md`.

## Reproducibility
- `src/puschel_killtest.py` (correction-direction + plain corr, regional), `src/global_prior.py`
  (88-smelter global prior), `src/benchmarks.py` (EDGAR CF4). Posterior + grids gitignored.
- Smelter registry: `factors/smelters_global.csv` (China incomplete — flagged in `factors/SOURCES.md`).
