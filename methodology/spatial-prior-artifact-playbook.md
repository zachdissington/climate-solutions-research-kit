# Spatial-Prior Artifact Playbook

Living methodology doc. **Open this before starting any free-value spatial-prior artifact** — PFC from
aluminium smelters, HFC-23 from HCFC-22 plants, or any of the 41 free-value survivors
(`analysis/free-value-artifacts.md`). It exists because the first one (SF6) was built end-to-end and
then refuted in a measurement that could have run on day one. Post-mortem:
`decisions/2026-06-06-sf6-spatial-prior-postmortem.md`.

These artifacts all share one shape: *a potent non-CO2 gas (or orphaned point source) gridded by
facility/infrastructure location instead of a population proxy, validated against an atmospheric
inversion posterior.* The whole value claim of every one of them reduces to a single number: **does
our spatial prior correlate with the best gridded inversion posterior better than the population proxy
(EDGAR/GAINS) does?** That number is cheap. Compute it first.

---

## The one rule: cheapest decisive test first

Invert the SF6 build order. Before building any production pipeline, run the kill-test:

1. **Find and CRACK the ground-truth posterior.** Locate the best gridded inversion **posterior** for
   this gas and region. Then *open the actual data objects* — do not accept any collection-level or
   blurb-level classification. The SF6 build nearly died here: the decisive ICOS dataset was twice
   labelled "national totals" off its description and only revealed gridded posteriors when the files
   were opened. A dataset misread as useless closes the search with false confidence, which is worse
   than not having looked. Match the posterior's **year** to the year of the priors you will compare
   (a temporal mismatch is a caveat that lets a real result get rationalized away).
2. **Pull the baseline.** Download the population-proxy grid you must beat (EDGAR v8 per-gas at 0.1°,
   and GAINS where available). Confirm the gas is separable per-sector/per-year.
3. **Rough-build the proposed prior.** Build a deliberately crude version of the infrastructure/
   facility prior — enough to grid, not production quality. Skip uncertainty bands, skip global
   coverage, skip calibration. One or two test countries where the posterior exists is enough.
4. **Run the one correlation that is the value claim.** Regrid all of {ours, EDGAR, GAINS,
   inversion-own-prior} onto the posterior's grid, take the spatial correlation against the posterior
   per country (reuse `sf6-spatial-prior/src/icos_metric.py` as the template). Go/no-go in hours.

Only if the rough prior is competitive with or beats population do you build for real (full coverage,
uncertainty propagation, calibration, write-up). If it loses, bank the negative and move to the next
survivor. The expensive build is the **reward** for passing the cheap test, never the path to it.

---

## Two gates, kept separate

The SF6 build conflated these. They are different questions and one does not authorize skipping the
other.

- **Premise gate** — *does the gap exist?* Do existing products grid this gas by a crude proxy
  (population/nightlights), is the slot unoccupied (no prior art linking infrastructure to this gas),
  and do the intended users want a better prior? Verify at source. SF6 passed this cleanly
  (`premise-verification.md` is the template: read the EDGAR supplement Table S1 for the actual proxy,
  quote the inversion papers' own statements of need). **Passing the premise gate authorizes the cheap
  value test — not a full build.**
- **Value gate** — *does our method fill the gap better than the baseline?* This is the kill-test
  above. A real, unoccupied gap can still be one where no infrastructure proxy beats population. SF6
  was exactly that. The premise being true tells you nothing about whether the value claim is true.

---

## The diffuse-vs-point-source distinction (read before judging the next gas)

This is the most important forward lesson and the one most likely to be mis-applied.

SF6 failed **because its proxy was diffuse.** SF6 sits in thousands of transmission substations with
no single dominant site, so any substation-weighted grid smears the signal across the country and
misses the few specific hotspots the inversion resolves. Population, which clusters with electrical
load, beat it.

Do **not** generalize "infrastructure priors don't beat population" from SF6 to the family. The
discriminating question for each candidate gas is: **how concentrated are the real emitters?**

| Source structure | Example | Expected prior performance |
|---|---|---|
| Diffuse (thousands of sites, none dominant) | SF6 in switchgear | Population hard to beat — SF6 lost here |
| Concentrated point sources (tens–hundreds of named facilities) | PFC from aluminium smelters; HFC-23 from HCFC-22 plants | A facility prior should *crush* population — this is the favorable case the inversion resolves |

PFC-from-smelters and HFC-23-from-HCFC-22-plants are genuine point sources. They are structurally the
*opposite* of SF6 and are plausibly the strong members of the family, not the weak one. The cheap
test still decides it, but go in expecting these to be the cases where the prior wins.

A practical screen before even running the kill-test: count the dominant emitters. If a handful of
named facilities produce most of the gas, the facility prior is well-motivated. If the gas is spread
across a large diffuse infrastructure class, treat it as SF6-like and be skeptical.

---

## Data-truth discovery checklist

Where the gridded inversion posteriors live, and the traps:

- **ICOS Carbon Portal** (data.icos-cp.eu) — the ICOS PARIS F-gas collection holds recent
  (2017–2024), fine (0.23°), multi-system gridded posteriors for several gases (SF6 via InTEM/ELRIS ×
  FLEXPART/NAME; **CF4/PFC via RHIME**, plus other gases). Download needs the cookie mechanism
  (`-b CpLicenseAcceptedFor=<id>` → `data.icos-cp.eu/objects/<id>`). CC-BY-4.0.
- **PANGAEA** — e.g. Brunner et al. 2017 InGOS halocarbon inter-comparison (880251/880252): gridded
  `posterior_flux` + `prior_flux`, multiple systems, Europe, but **2011 only** (old, coarse,
  prior-dominated — use as a secondary check, not the decider).
- **Zenodo / journal SI / inversion-group portals** (Bristol/ACRG, EMPA, NILU, Vojta/Stohl, NOAA
  HATS, AGAGE, NIES) — most deposit only mole-fraction observations, model code, or national totals.
- **The mis-grab trap:** "gridded SF6/F-gas" on Zenodo is often a **prior** (GAINS population grid),
  not a posterior. Priors are not ground truth. Confirm the file carries a `posterior`/`flux_total_posterior`
  field before trusting it.
- **Crack every stone.** Open the data objects of anything plausibly relevant, even if its description
  says "national totals." That single step is what saved (and then settled) the SF6 build.
- **If no usable posterior exists for current years**, the value claim is only testable via author
  collaboration / an OSSE with the inversion groups (EYE-CLIMA, Vojta/Stohl run FLEXINVERT+ with a
  pluggable prior). That is a real cost — surface it before building, do not build hoping truth appears.

---

## Pre-build gate checklist (run verbatim)

A future session should be able to answer all of these before writing a production line of code:

- [ ] **Premise verified at source** — named proxy the existing products use (read the supplement,
      don't infer); slot confirmed unoccupied; user-need quoted from the literature.
- [ ] **Source-structure screen** — are the dominant emitters concentrated (point sources) or diffuse?
      State the expectation this sets.
- [ ] **Posterior located AND cracked** — actual gridded posterior file opened, fields confirmed
      (`*_posterior`, per-cell, country mask), year noted.
- [ ] **Year match** — posterior year aligns with the baseline/prior year, or the mismatch is stated.
- [ ] **Baseline pulled** — EDGAR (and GAINS) per-gas grid loaded, gas separable.
- [ ] **Rough prior built** — crude facility/infrastructure weighting on the test country/countries.
- [ ] **Kill-test run** — spatial correlation of {ours, EDGAR, GAINS, inversion-prior} vs the
      posterior, per country. **Decision recorded.**
- [ ] **Go only if ours is competitive or better.** Otherwise bank the negative and stop.

Conventions: provenance numbers from `scripts/query_solutions.py`, never agent-estimated; deterministic
arithmetic in Python; hard validation gates on any ingest (the SF6 point-source T1–T6 pattern); record
the decision in `decisions/` and the negative-or-positive verdict in a `validation_report_*.md`.

---

## Worked example — PFC (CF4/C2F6) from aluminium smelters (next candidate)

Apply the playbook without building yet:

- **Premise** — EDGAR grids PFCs (CF4/C2F6) by the same population/product-use proxy as SF6; the
  free-value analysis flagged the western-China CF4 hotspot as currently mislocated. Confirm the
  EDGAR PFC proxy at source (Table S1) before proceeding.
- **Source-structure screen** — aluminium smelting is a few hundred named smelters worldwide; PFC
  (anode-effect) emissions are concentrated at them. **This is the favorable point-source case** — go
  in expecting a facility prior to beat population, unlike SF6.
- **Posterior (candidate, must be cracked)** — the ICOS PARIS F-gas collection's **RHIME CF4/PFC**
  members are the first place to open; confirm gridded posterior fields and the available years.
  Secondary: search PANGAEA/Zenodo/Vojta for any CF4 posterior, applying the priors-not-posteriors
  trap.
- **Baseline** — EDGAR v8 CF4/C2F6 grid at 0.1° (+ GAINS if it grids PFCs).
- **Rough prior** — a global smelter location list weighted by smelter capacity × PFC intensity
  factor, gridded to the posterior's resolution. Verify a public source (industry/IAI or USGS smelter
  datasets) and confirm coverage by opening it; do not assume.
- **Kill-test** — correlation vs the RHIME posterior over the country/region with smelters and
  inversion coverage. If a capacity-weighted smelter map beats population (expected for a point-source
  gas), proceed to the full build; if not, bank the negative — but a loss here would be far more
  surprising than it was for SF6.
