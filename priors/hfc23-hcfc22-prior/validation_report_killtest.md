# HFC-23 Kill-Test Verdict — HCFC-22-plant prior vs population proxy, vs the ICOS 2020 HFC-23 posterior

> Run 2026-06-07 (HFC-23 gate). The cheap, decisive accuracy test, run before any deep build
> (method: `../analysis/spatial-prior-artifact-playbook.md`). Truth = ICOS PARIS HFC-23 posterior,
> year 2020, Europe, **6-member ensemble** (ELRIS/InTEM/RHIME × NAME/FLEXPART), FLAT prior (so the
> posterior is observation-driven). Candidate = our presence-only HCFC-22-plant prior (5 permit-confirmed
> European producers). Baseline = EDGAR HFC-23 (its only sector `PRU_SOL` ≡ `TOTALS`).
> Scripts: `src/hfc23_killtest.py`, `src/plant_prior.py`, `src/enrichment_test.py`, `src/diagnose.py`,
> `src/fetch_posteriors.py`, `src/benchmarks.py`.

## Verdict: NO-GO (informative negative) — the opposite of CF4

On the claim that matters — *does an HCFC-22-plant prior disaggregate HFC-23 better than EDGAR's
population proxy?* — **HFC-23 fails in the only publicly testable region (Europe).** A plant-location
prior does not beat population there. This is not a degenerate/untestable result: the posterior is
genuinely constrained and the diagnostics explain *why* the prior loses. Bank the negative.

## Result 1 — spatial correlation vs the ICOS 2020 posterior (ensemble mean ± sd)

| Region | OURS-pres | EDGAR-TOT | N cells | ours beats pop? |
|---|---|---|---|---|
| **POOL** (5 plant countries) | 0.081 | **0.288** | — | **no** |
| NLD | 0.136 | 0.533 | — | no |
| FRA | 0.035 | 0.136 | — | no |
| ITA | 0.139 | 0.223 | — | no |
| GBR | 0.004 | 0.130 | — | no |
| DEU | 0.057 | 0.160 | — | no |

**0/6 plant-regions** — EDGAR wins everywhere. (The correlation metric under-scores a one-hot prior:
each European country has exactly ONE HCFC-22 plant, so OURS is a near-delta — the degenerate
"one site per country" case the CF4 report flagged. Result 2 is the fair, decisive metric.)

## Result 2 — plant-cell percentile rank within the pooled European plant-country domain (mean of 6 members)

| Plant | POSTERIOR | PRIOR | EDGAR |
|---|---|---|---|
| Spinetta Marengo (IT) | **99.1%** | 58.0% | 98.7% |
| Dordrecht (NL) | **91.8%** | 58.7% | 98.9% |
| Gendorf (DE) | 85.1% | 59.6% | 88.9% |
| Pierre-Bénite (FR) | 78.3% | 60.0% | 94.0% |
| Thornton-Cleveleys (UK) | 30.4% | 58.1% | 87.2% |
| **MEAN** | **76.9%** | 58.9% | **93.5%** |

Two readings, both load-bearing:

1. **The inversion DOES localize HFC-23 to our plants — and it's observation-driven, not circular.**
   The FLAT prior sits at a uniform ~59th percentile at every plant; the posterior rises to a mean
   77th (Spinetta 99th, Dordrecht 92nd). Observations moved mass *to* the plant cells. The physical
   premise — HFC-23 is concentrated at HCFC-22 plants — is independently confirmed by the inversion.
   The posterior's single highest European cell (44.9, 8.4) is Spinetta Marengo; #2–4 cluster on
   Dordrecht.

2. **But population already predicts the plants, so the prior adds nothing.** EDGAR's percentile at the
   plants (93.5) is *higher* than the posterior's (76.9). European HCFC-22 plants are integrated
   chemical complexes inside populated/industrial regions (Randstad, Lyon, the Milan corridor, the
   Munich axis), so a population proxy puts high values there already — and additionally captures the
   diffuse, abated residual. The plant prior has no disaggregation skill to add over population.

## Why this is the structural opposite of CF4 (the portfolio lesson)

CF4 passed because aluminium smelters are deliberately sited **away from population** — remote
cheap-power locations (Iceland, Norway, western China) — so a smelter prior relocated mass off the
population proxy and beat EDGAR (Iceland 0.25 vs ~0). HCFC-22 plants do the opposite: they sit **inside**
populated industrial regions, so plant-location ≈ population and the proxy is already good.

**"Point-source" was necessary but not sufficient. The real discriminator is "point-source AND
sited away from population."** This refines the portfolio's selection axis (`free-value-portfolio-plan.md`
§3): add a population-coincidence screen, not just diffuse-vs-point. The pre-build stress test's two
WOUNDS (`../analysis/free-value-stress-tests/hfc23-hcfc22.md`) are now empirically confirmed: in the one
region we can test, population is hard to beat for this gas.

## Premise gate (confirmed at source, this run)

- EDGAR HFC-23 is a **population/industrial proxy**, not plant-located: its top European cells are at
  Russian population centres (Moscow 55.75/37.75, St. Petersburg 59.85/30.35, Voronezh 51.65/39.15),
  not at fluorochemical plants; top-10 cells = 6.0% of the European total (diffuse). So the artifact's
  target proxy is real — EDGAR does grid HFC-23 by population. The gap exists; the prior just doesn't
  beat it in Europe.
- EDGAR HFC-23 has a single sector (`PRU_SOL` ≡ `TOTALS`, 9.30 kt/yr global 2020) — no aluminium-style
  sector split to exploit.

## What this gate cannot settle — and the decisive region

The region where a plant prior *might* still beat population is **China / East Asia**: many HCFC-22
plants, the large top-down−bottom-up gap (~11–13 Gg/yr, eastern China), and plausibly less
population-coincidence. But there is **no public gridded HFC-23 posterior for East Asia** — Park et al.
ACP 2023 and Western/Stanley 2024 are figures-only (the same wall CF4 hit on China). Unlike CF4, HFC-23
has **no clean positive region** (Europe is a loss, not a GO) to anchor a deep build.

## Decision

**NO-GO. Do not deep-build HFC-23.** Bank the informative negative; it saves the community the
reassembly chore by showing population is competitive for this gas in Europe. Deprioritise HFC-23 in
the portfolio. The only cheap re-test path: if the CF4 outreach (`../pfc-aluminium-prior/outreach/`)
opens an East-Asia F-gas posterior channel, HFC-23 can be re-run in China at near-zero marginal cost on
this same harness — fold it into that ask rather than a separate build.

## Honest ceiling / caveats

- Europe is ~0.2–1.5% of global HFC-23 (Stanley et al. 2018) — low absolute signal; "sporadic, highly
  localized, difficult to capture" at current network density. The test is relative, not high-SNR.
- Presence-only weighting was deliberate: per-site HCFC-22 capacity is unsourced and mandated
  incineration decouples emitted HFC-23 from throughput (see `factors/SOURCES.md`). A capacity-weighted
  variant was not built because fluoropolymer-output as a proxy would mis-rank the likely-dominant,
  under-reported Spinetta Marengo toward zero.
- 5-plant European registry, one plant per country — the correlation metric is unfair to it (Result 1);
  Result 2's percentile test is the appropriate metric and is what the verdict rests on.
