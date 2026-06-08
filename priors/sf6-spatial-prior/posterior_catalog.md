# SF6 Inversion Posterior — Availability Catalog (discovery sweep 2026-06-03)

> Sweeps (5 research agents over journals, Zenodo/PANGAEA, inversion-group portals, CEDA/national,
> operational services, SI deep-checks) + self-verification by download. Goal: downloadable gridded SF6
> inversion POSTERIOR fields for validation truth.

> **UPDATE 2026-06-03 — CORRECTION (the better find):** the agents twice misclassified the **ICOS PARIS
> F-gas collection** (DOI 10.18160/GR1Q-6SK4) as "national totals" off its blurb. A manual crack of that
> "unchecked stone" found it actually contains **recent (2017–2024), fine (293×391, ~0.23°×0.35°),
> multi-system gridded SF6 posteriors** (`flux_total_posterior` + `flux_total_prior` + `country_fraction`
> per cell), CC-BY-4.0, downloadable via the ICOS cookie mechanism (`-b CpLicenseAcceptedFor=<id>` →
> `data.icos-cp.eu/objects/<id>`). Members: InTEM/ELRIS × FLEXPART/NAME (SF6) + RHIME (cf4/pfc218, other
> gases). **This is the real validation truth and supersedes InGOS 2011.** Verdict run: `validation_report_icos.md`.
> Lesson: don't trust an agent's collection-level classification — open the data objects.

> Below = the original sweep conclusion (InGOS 2011 was thought to be the only one). Retained as record.

## The one usable posterior (OBTAINED + VERIFIED)

**PANGAEA 880251 / 880252 — Brunner et al. 2017, InGOS halocarbon inversion inter-comparison.**
- TYPE: **posterior-gridded** (`posterior_flux` + `prior_flux` in the same files). SF6 = species code `H13`.
- Systems: **4 independent inversions** — NILU/FLEXINVERT, EMPA, EMPA2, UKMO/InTEM (an ensemble → spread = uncertainty).
- Coverage: **Europe** (includes FR, DE). Year: **2011 only**. Grid: variable/unstructured — e.g. the
  EMPA2 NetCDF is **405 cells**, each with `lon/lat/dlon/dlat` + `prior_flux`/`posterior_flux`.
- Format: NetCDF (`.nc`, EMPA2/NILU) + ASCII `.dat` (EMPA/UKMO). License: **CC-BY-3.0**. Downloadable: **YES**.
- Obtain: <https://store.pangaea.de/Publications/Brunner-etal_2017/ingos_halocarbon_inversions.zip>
  (landing <https://doi.pangaea.de/10.1594/PANGAEA.880251>). Verified locally: 57 H13 files, 12 posterior
  NetCDFs; opened `GRID_MEAN_INGOS_EMPA2_ASIM_H13v4_FLEXPART.nc` → `prior_flux`, `posterior_flux` present.

## Everything else — NOT a usable posterior (sourced)

| Source | What it is | Why not usable |
|---|---|---|
| Vojta 2024 global re-analysis (ACP 24/12465) | mole-fraction fields (`phaidra.489`) + FLEXINVERT+ code (`phaidra.488`) | posterior *emissions* not deposited — only concentrations + code; emissions are figures/national totals |
| Vojta 2025 European ensemble (ACP 25/15197) | code (`phaidra.736`) + mole fractions | posterior gridded emissions **not deposited**; reported as country/EU-27 totals only |
| German SF6 (ACS, Meixner) | data-availability = observations only | InTEM/FLEXINVERT posterior grids are figures (SI); not deposited |
| Swiss F-gas (ACP 23/14159) | observations on Zenodo | inversion results "available from corresponding authors upon request" |
| Bristol ACRG / InTEM (UK DECC) | national totals → NAEI/UNFCCC; portal = observations | no gridded posterior published |
| NOAA GML/HATS | mole-fraction observations | not emissions, not gridded |
| AGAGE (Western 2025, ESSD) | 12-box semihemispheric global totals | top-down but **not spatially gridded** |
| NIES Japan | SF6 = transport-eval tracer; GOSAT = CO2/CH4 | no SF6 gridded posterior; login-gated |
| Zenodo 12708771 / 11032177 | **GAINS PRIORS** (population-gridded) | priors, not posteriors (the easy mis-grab) |

## Verdict

The structural-ceiling claim was **half wrong**: modern multi-year posteriors are indeed unpublished
(figures/totals only — outreach would be needed for those), BUT a genuine **multi-system gridded SF6
posterior exists for Europe 2011** (InGOS) and is now in hand. So a **real metric "beats the proxy"
test is possible now** for European countries (incl. FR + DE), against 2011, without author outreach.

**Caveats for the metric test (next build):** (1) single year **2011** — predates our 2020 EDGAR/GAINS
priors and current OSM, a temporal mismatch to state honestly; (2) coarse **variable 405-cell** grid —
our prior + EDGAR/GAINS must be mapped onto those cells to compare; (3) it's a 4-system ensemble — use
the spread, don't treat any one as absolute truth.

**Collaboration note (for later):** EYE-CLIMA (IIASA+NILU+Vienna+Bristol) and Vojta/Stohl run
FLEXINVERT+ with a *pluggable gridded prior* and already do prior-sensitivity/OSSE experiments — the
natural home for testing our infrastructure prior on *current* years if 2011 proves out.
