# Holistic Validation — CF4 smelter prior, pre-Vienna-handoff stress test (2026-06-09)

> Run 2026-06-09 (task T-2026-06-09-023), against the staged Zenodo draft (20617486) and the reply
> email to Stohl/Püschel/Vojta. Mandate: treat "smelter prior beats EDGAR" as a hypothesis to break;
> test whether the validated claim transfers to the artifact actually being handed over; and test
> whether the spatial→sectoral-attribution link in the outreach is real. Scripts:
> `src/holistic_significance.py` (A1), `src/resolution_transfer.py` (A2),
> `src/production_rescale.py` (A3 fix). All stats numpy-only, seeded, printed with inputs.

## Headline

**The artifact survives, with materially narrowed claims.** The kill-test's headline numbers
reproduce exactly, but spatial-significance testing shows the only individually significant win is
Iceland; the pooled win is a consistent direction across all 6 ensemble members without per-member
significance; and **France — claimed as a decisive win in every public-facing document — does not
survive** (system-dependent, and a near-tie at the 1° resolution actually shipped). Separately, the
audit found the deposited global field was **not the validated configuration** (6 validated European
smelters missing, including all of Spain) and carried **China at 28% of weight vs its 57% production
share**. Both defects are now fixed in the draft deposit; all public claims have been recalibrated.
Recommendation: **GO (revised)** — publish the updated deposit and send the v2 email.

## A1 — Is the Europe win statistically real? (ICOS native grid, 0.234°×0.352°)

Method: per ensemble member and region, Δr = r(ours-capacity) − r(EDGAR-TOT) vs the 2020 flat-prior
posterior; moving-block bootstrap (blocks 10 and 25 cells, 1000 reps) for a 95% CI on Δr; toroidal-
shift permutation null (1000 shifts) for each candidate's own correlation; Spearman rank correlation
as robustness; smelter-cell enrichment percentile as a second metric. Note the grid: the ICOS
posterior is **0.234° lat × 0.352° lon** (293×391) — earlier docs that said "0.1°" were wrong.

| Region | finding |
|---|---|
| **ISL** | **The one significant win.** Δr ≈ +0.25; 95% CI excludes 0 at both block sizes; ours beats its shift-null (p≈0.01–0.03), EDGAR does not. BUT only 2 of 6 members cover Iceland (RHIME×2) — "consistent across the 6-member ensemble" never applied here. Spearman is a tie (~0.21 both): the Pearson win is carried by the smelter point cells aligning with the posterior's mass, which is the point-source claim, stated honestly. |
| **POOL** | Δr > 0 in **6/6 members** (range +0.013 to +0.076) — direction fully consistent — but **no member's 95% CI excludes 0** at either block size. Ours beats its shift-null in 6/6 members (the field is spatially informative), EDGAR in 5/6. Spearman favors EDGAR (ours −0.24 to +0.20 vs EDGAR 0.26–0.40): EDGAR's smooth field tracks the low-emission background ranking; ours predicts where the flux mass is. |
| **FRA** | **Does not survive.** 0/6 members significant; InTEM members strongly positive (+0.23, +0.26) but both RHIME members show ours **significantly losing** (CI fully negative). Spearman: EDGAR clearly better (0.28–0.65 vs ours ≈ 0). The killtest's "France 0.22 vs 0.14" was a mean over heterogeneous members. |
| **DEU** | Consistent direction 6/6, never significant at native grid. Suggestive only. |
| **NOR / ESP / GBR** | Losses confirmed (as the killtest reported). |

**Enrichment (new second metric):** across the 6 members, the observation-driven posterior places the
22 in-domain smelter cells at a mean **60.1st percentile** of the pooled domain; EDGAR places them at
**26.0** (zero CF4 at 14 of 22 smelter cells, incl. all of Norway and Iceland). Star case: Alcoa
Fjardaal (Iceland) 99.5th. This is a clean, assumption-light statement of the premise: observations
put CF4 at smelters; EDGAR's proxy actively doesn't.

**The "~4×" framing:** a ratio of two near-zero correlations (0.057/0.015) overstates near-noise
arithmetic. Defensible phrasing is the difference + consistency ("ahead in all 6 members; not
individually significant against spatial autocorrelation"). The "non-overlapping ensemble bands"
claim was true as member spread but is not a significance statement.

## A2 — Does the win transfer to the shipped artifact (1° global field)?

Method: aggregate posterior (cos-lat-weighted), EDGAR (sum) and priors onto the deposit's 1° grid;
same correlation + significance machinery (blocks 3 and 6 cells).

**Registry-subset audit first — the shipped field was NOT the validated configuration.** 6 of the 25
validated European 1°-cells were missing from `smelters_global.csv`: Alcoa San Ciprián / Avilés /
A Coruña (all of Spain), Slovalco (SVK), Talum (SVN), Aldel (NLD). **Fixed 2026-06-09** by merging the
validated rows in (registry now 94 smelters; 25/25 cells present; field regenerated).

At 1° (after the fix), correlations rise for all candidates (coarser is easier):

| Region | ours (1°) | EDGAR (1°) | reading |
|---|---|---|---|
| ISL | **0.554** | −0.003 | strengthens at 1°; shift-null p≈0.02–0.03; bootstrap CI marginal (few blocks) |
| POOL | **0.141** (prod variant 0.131) | 0.072 | ahead in 5/6 members; still not per-member significant |
| DEU | **0.368** | 0.096 | consistent 6/6; block=6 CIs exclude 0 in 6/6 but only ~4 blocks — treat as suggestive |
| FRA | 0.296 | 0.286 | **near-tie at 1° — the native-grid France edge vanishes at the shipped resolution** |
| NOR | 0.109 | 0.156 | EDGAR ahead |
| ESP | −0.009 | 0.121 | EDGAR ahead (was literally NaN pre-fix: the field had no Spanish smelters) |
| GBR | 0.010 | 0.066 | EDGAR ahead |

**Verdict:** the relative-win direction transfers to the shipped 1° field (pooled and where
constrained), with the same significance caveats. France must not be claimed at any resolution.

## A3 — Global-field integrity where it matters (China)

Registry country shares vs USGS MCS 2021 production (2020e, world 65,200 kt): the raw capacity field
carried **China at 28.0%** of global weight vs **56.7%** of world production (37,000 kt) — a ~2×
under-weight of the country that Püschel et al. estimate emits 56% of global CF4. Ex-China the
registry tracks USGS well (CAN 3,127 ktpa registry vs 3,100 kt production; RUS 4,064 vs 3,600; NOR
1,418 vs 1,400; ISL 863 vs 840).

**Fix (within guardrails — no new China facilities):** a third variant,
`prior_cf4_global_production.nc` — country totals rescaled to USGS 2020 production (listed countries
direct; the 9,000 kt "Other" pool distributed across unlisted registry countries by capacity),
distributed within each country by registered capacity. China now carries 56.7% of field weight,
placed on its 12 registered major clusters (disclosed in attrs, SOURCES.md, method note, and the
Zenodo description). This is the **recommended global variant**; the deep China registry build stays
parked per the standing decision. Europe behavior is unchanged (PROD ≈ SHIPPED in every European
region; POOL 0.131 vs EDGAR 0.072).

**What Europe-validation licenses for China: only the mechanism, not the magnitude.** The validated
claim is "where observations resolve point sources, the smelter prior beats the population proxy."
China has different observational constraint (weak), different technology (PFPB, low EF), and our
within-China placement rests on 12 clusters. Kim et al. 2021 (127-smelter East-Asia prior improved
the inversion) remains the published China-side evidence; our own China-scale claim stays unearned
until a clean China posterior / OSSE exists.

## A4 — The crux: does the artifact address Referee 1's sectoral-attribution point?

**Verified at source** (preprint Sect. 2.4/3.4 + RC1, fetched 2026-06-09): Püschel et al. attribute
sectors with the Kim et al. (2014) **C2F6/CF4 emission-ratio mixing model** (r_al = 0.10 ± 0.01,
r_el = 0.40 ± 0.19 kg/kg), applied to their co-inverted CF4+C2F6 posteriors at country and grid-cell
level (headline: 81% aluminium share of CF4). RC1's concern is that these **ratio constants** are
late-2000s values that technology change may have shifted, and asks for "an analysis of temporal
changes in sectoral emission fractions."

**Honest verdict: the previously drafted link was oversold.** A spatial prior does not bear on the
ratio constants at all — the old reply draft's claim that citing the prior is "the physically-grounded
alternative to the fixed Kim et al. (2014) sectoral fractions" was wrong on mechanism, and the sent
2026-06-08 email's "that is the specific gap I think I can help with" overstated it.

**What survives is real but different:** the paper's own Sect. 3.4 (i) sanity-checks attribution by
co-locating emission cells with "known industry locations" informally, and (ii) states EDGAR's
location proxy is "difficult to confirm due to the lack of detailed documentation." The smelter
registry is exactly the documented, citable location layer for that analysis — including carrying
zero primary smelters in South Korea/Taiwan, where the authors themselves call their attribution
"unrealistic." And the prior remains a physically-documented **aluminium-sector component** for any
prior-sensitivity run (their inversion runs on a variable 8°→1° internal grid, so "drop-in, no
regridding" was also softened — the 1° match is to their *deposited* fields).

The v2 reply email states the negative explicitly ("it does not bear on the Kim et al. (2014)
emission-ratio constants themselves") and offers the two true uses.

## A5 — Claims audit (public-facing surfaces)

| Claim (pre-audit) | Status | Action |
|---|---|---|
| Pooled "beats ~4×" (0.057 vs 0.015) | direction holds 6/6; not per-member significant; ratio framing inflated | reworded everywhere to consistency + significance caveat |
| "decisively where the inversion resolves (Iceland 0.25, **France 0.22**)" | Iceland yes (RHIME only); **France fails** | France removed from method note, deposit description, email |
| "consistent across all 6 ensemble members, non-overlapping bands" | true for POOL member spread; NOT true for Iceland (2 members); not spatial significance | qualified |
| Kill-test ran at "0.1°" (handoff/docs) | wrong — ICOS grid is 0.234°×0.352° | corrected here; killtest report annotated |
| Deposited global field = validated configuration | **false** (6 European cells missing) | registry repaired, field regenerated, re-validated |
| Global field usable globally as-is | misleading (China 28% vs 57%) | production-rescaled variant added + disclosures |
| "relative weights, not absolute flux" | held for the 2 flexinvert files; the 4 original NetCDFs had **no attrs at all** | attrs added to all variants (units "1", rescale note, China caveat) |
| Spatial prior addresses RC1's sectoral-fraction point | **oversold** (see A4) | email v2 states the negative + the two true uses |
| EDGAR-NFE ≈ EDGAR-TOT (premise: EDGAR grids aluminium CF4 by proxy) | reproduced | unchanged |
| Consistency with Kim et al. 2021 | direction consistent; kept with "regional, published" framing | unchanged |

## What changed in the artifacts (all in the unpublished draft / unsent email)

- `factors/smelters_global.csv` — +6 validated European smelters (94 total); SOURCES.md updated.
- `outputs/prior_cf4_global_{capacity,presence}.nc` — regenerated (repaired registry) + honest attrs.
- `outputs/prior_cf4_global_production[_flexinvert].nc` — NEW recommended global variant (USGS 2020
  production rescale; `src/production_rescale.py`).
- `outputs/prior_cf4_europe_*.nc` — regenerated with attrs (values unchanged).
- `outputs/*_flexinvert.nc` — regenerated (incl. new production variant; `src/cf_reformat_for_flexinvert.py`).
- Method note (md + PDF, `src/make_method_note_pdf.py`) — Rev 2, recalibrated claims.
- **Zenodo draft 20617486** — all 11 files replaced/added, description recalibrated. Still UNPUBLISHED.
- `outreach/2026-06-09-cf4-vienna-reply.md` — v2 rewrite (honest attribution framing, sector-component
  framing, production-variant recommendation). Still UNSENT. anti_slop: clean.

## Recommendation for Zach: GO (revised)

Publish the updated Zenodo draft and send the v2 reply. Rationale: the core thesis survives its
hardest available test (Iceland significant; pooled direction consistent in all 6 members; smelter
cells at 60th vs EDGAR's 26th percentile under observation-driven truth; premise confirmed), and the
deposit is now strictly more honest and more useful than what was staged this morning (validated
configuration restored, country shares fixed, every claim significance-calibrated, misuse-as-absolute-
flux foreclosed in every file's attrs). The outreach value claim is smaller than the 2026-06-08 email
implied — the v2 reply repairs that explicitly, which costs some shine but is the right trade with a
group that can check everything. If instead you want zero overstatement risk with Benjamin, the
fallback is publishing the deposit and sending a shorter reply that only links it — but the v2 text
already says the limiting things out loud.

What you'd be approving: (1) Zenodo publish (mints DOI 10.5281/zenodo.20617486, public, CC-BY); (2)
reply-all send of `outreach/2026-06-09-cf4-vienna-reply.md` body.
