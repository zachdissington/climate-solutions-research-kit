# Phase 1 — Data-Acquisition Spike: Findings

> Started 2026-06-03. Goal: prove the three inputs (OSM power infra, EDGAR/GAINS benchmark grids,
> factor tables) are obtainable before committing to the full model. Exit gate: surface anything
> materially harder than the stress test assumed, and re-scope before Phase 2.

## Environment

- **Python 3.14 is too new** for the geospatial stack on this machine — built the pipeline on a
  **Python 3.13 venv** (`.venv/`, gitignored). `earth-osm 3.0.2`, `geopandas 1.1.3`, `shapely 2.1.2`,
  `pyogrio 0.12.1` all installed from wheels, no GDAL compile.

## Input 1 — OSM power substations: FEASIBLE, with one approach change

- **earth-osm CLI is broken on Windows** — `earth_osm/args.py` does a Unix-only `import resource` at
  module top, so every CLI invocation crashes. **Workaround: use the Python API directly**
  (`earth_osm.eo.get_osm_data(region, "power", "substation")`), which never imports `resource`.
  This is what `src/extract_substations.py` does. (Worth a one-line upstream issue/PR later.)
- Extraction works end-to-end: downloads the geofabrik `.osm.pbf`, returns a flattened DataFrame with
  `tags.*` columns (incl. `tags.voltage`, `tags.substation`, `tags.location`, `tags.gas_insulated`).

### The material finding — voltage is NOT the classifier (Luxembourg proof region)

| Tag | Coverage (823 substations) | Verdict |
|---|---|---|
| `tags.substation` (type) | **64.0%** | the usable classifier |
| `tags.voltage` | 4.7% | far too sparse — the plan's assumed voltage-driven filter does not hold |
| `tags.location` (indoor⇒GIS proxy) | 1.1% | unusable |
| `tags.gas_insulated` (direct GIS) | 0.2% | unusable (matches the stress test's ~3,996-worldwide finding) |

`tags.substation` value counts (LU): `minor_distribution 492`, `<none> 296`, `traction 16`,
`transmission 7`, `distribution 4`, `subtransmission 1`, `industrial 2`.

**Implications (carry into Phase 2):**
1. **Primary filter = `substation` type, not voltage.** Keep `transmission` + `subtransmission`;
   drop `minor_distribution` / `distribution` / `traction` (no high-voltage SF6 GIS). The raw
   `power=substation` count is ~60% distribution noise — counting all substations would massively
   over-count the SF6 universe.
2. **Voltage is a sparse secondary signal**, not the backbone. Where present, parse it (multi-voltage
   `;`-separated, kV-vs-V heuristic — handled in `parse_voltage()`); where absent (~95%), impute from
   type + operator (TSO operators like Amprion/TenneT/Creos ⇒ transmission) + geometry/area.
3. **GIS status must be modeled probabilistically** — confirmed, since the direct tag is ~0.2%.
   GIS share rises with voltage and is higher in space-constrained (urban/indoor) sites; that becomes
   the `P(GIS)` layer, never an assumption.
4. Luxembourg (tiny, grid-edge) yields ~8 transmission-class substations. Germany — the SW-Germany
   hotspot validation litmus — is the next real extract (a ~4 GB pbf; deferred until Phase 2/3 model
   exists so the download buys validation, not just a count).

## Input 2 — EDGAR v8 / GAINS benchmark grids: NOT YET PULLED

Next. EDGAR v8 publishes gridded F-gas emissions at 0.1° (free, CC-BY); GAINS/IIASA a second grid.
To do: confirm the SF6 layer is separable and load both onto a common raster for cell-by-cell
comparison (needs `rasterio`/`xarray`/`netCDF4` — install deferred to when this input is handled).

## Input 3 — Charge/leak factor tables: NOT YET BUILT

Next. SF6 nameplate-charge-by-voltage + leak-rate factors from EPA / IEC / IPCC 2019 Refinement, plus
EPA GHGRP Subpart DD for the US calibration set. These are load-bearing scientific numbers — source
each from the authoritative document and commit to `factors/` with citations (no agent-estimated
values).

## Premise verification (2026-06-03) — added after the OSM spike

Before continuing, the existential kill-test was run (record: `premise-verification.md`). It **passed**:
EDGAR grids SF6 by **population** (verified at source), GAINS by **population+nightlights**, Climate
TRACE national-only, no OSM↔SF6 prior art, and the inversion community explicitly wants a better prior.
Two consequences for the build:
- **The verified baseline to beat is population/nightlights gridding** (EDGAR + GAINS) — a real method,
  not a strawman. Phase 3's "more accurate" claim is measured cell-by-cell against these.
- **Two-layer model required:** Layer 1 (grid switchgear, this spike) + Layer 2 (industrial point
  sources). The German inversion's dominant hotspot was industrial production/recycling, not switchgear.

## Benchmark grids ingested (2026-06-03) — `src/benchmarks.py`

Both population-proxy baselines load and pass sanity (global ~9 kt/yr, East-Asia-dominant):

| Grid | Sector | Global SF6 2020 | East Asia | N. America | Europe |
|---|---|---|---|---|---|
| GAINS (0.5°) | power only (`A_PublicPower`) | 9.5 kt/yr | 8,263 (87%) | 243 | 358 |
| EDGAR v8 (0.1°) | TOTALS (all) | 9.2 kt/yr | 5,451 (59%) | 1,515 | 517 |
| EDGAR v8 (0.1°) | PRU_SOL (product use) | 8.8 kt/yr | 5,149 | 1,462 | 509 |

- **EDGAR SF6 IS separable** — per-substance × per-sector × per-year `.nc` inside the 1 GB bundle
  (`SF6/{TOTALS,PRU_SOL,NFE}/`). PRU_SOL ≈ 96% of EDGAR's SF6 (product use / switchgear dominates);
  `NFE` (non-ferrous / magnesium) is the small remainder — a Layer-2-relevant industrial sector EDGAR
  already isolates.
- **Key finding: the two baselines disagree materially on spatial allocation.** GAINS 87% East Asia /
  243 t N. America vs EDGAR 59% / 1,515 t N. America (6×). Both are "the population/nightlights proxy,"
  yet they can't agree where SF6 is. That divergence is direct evidence the spatial allocation is
  uncertain — and an argument *for* a physically-grounded prior. (EDGAR's 59% East Asia is closer to the
  literature's ~57%-China figure; GAINS appears to over-concentrate.)

## Layer-2 industrial point sources ingested (2026-06-03) — `src/point_sources.py`

751 geocoded SF6 point sources, all validated (T1–T6 gates passed; `src/validate_point_sources.py`):
- **US (EPA GHGRP, Envirofacts):** 667 facilities. Top emitters are exactly the right archetypes —
  magnesium (Advanced Magnesium Alloys 9.1, MagRetech, Spartan), semiconductor (Wolfspeed 8.9), and
  utility grid SF6 (AEP/Duke/PSE&G, tagged `grid_use`, separated from the 588 `industrial`).
- **EU (E-PRTR via EEA discodata `[IED].[latest]`):** 480 SF6 air-release records → 84 facilities
  (latest year). Fetched programmatically (SQL API) — no manual download; dated snapshots committed to
  `factors/snapshots/` for reproducible provenance.
- **Validation:** T1 raw 480 == 480 kept, **0 silently dropped**; T2 mass conserved exactly
  (317,901 kg); T3 all 751 geocoded; T4 no dupes; T6 source-tagged. The build refuses to write the CSV
  on any hard-gate FAIL.
- **Honest nuance (T5 SW-Germany):** 3 German SF6 facilities fall in the hotspot box, but the largest
  is only ~0.6 t/yr — i.e. E-PRTR's reported point sources do **not** capture the large
  production/recycling hotspot the German inversion inferred (~1/3 of national SF6). This *confirms*
  the inversion paper's own conclusion that the industrial source is under-reported bottom-up — and it
  flags that Layer 2 (reported point sources) will under-weight that hotspot. A real limitation to
  carry into Phase 2, not hidden.

## Phase-1 gate status — COMPLETE

- OSM input (Layer 1 base): **PASS** (feasible; approach refined from voltage-driven to type-driven).
- Premise verification: **PASS** (gap real, unoccupied).
- Benchmark grids (EDGAR + GAINS): **PASS** (both load, sane magnitude; EDGAR SF6 separable).
- Factor tables: leak/emission **DONE**; nameplate charge **PARTLY SOURCED** (72.5/145 kV real, higher MODELLED).
- Layer-2 industrial point sources: **DONE** (751 facilities, US+EU, validated).
- **All model inputs locked — Phase 2 (combine layers → gridded prior) can begin.**

## Phase 2a — Layer 1 gridded model, Germany proof (2026-06-03) — `src/layer1_model.py`

First model output. **8,835 DE transmission-class substations** (Overpass, transmission-type OR
voltage≥110 kV); only **1% needed imputed voltage** (Overpass returned well-tagged data — far better
than the 95%-untagged LU bulk extract, because the query targets voltage/type-tagged substations).
Per-substation weight = `gis_charge(voltage) × P(GIS) × leak_rate`, gridded to 0.1°.

- **earth-osm abandoned for extraction.** Its geofabrik index is stale — it requested a dated DE pbf
  (`germany-260524.osm.pbf`) that 404s, on top of the Windows CLI bug. DE extraction now uses a **direct
  Overpass query** (UA required — bare curl gets 406). Lighter, controllable, no 4 GB download.
- **All gates pass:** G1 no-drops (8835==8835 gridded), G2 valid model (P(GIS)∈[0,1], no bad weights),
  G3 spatial sanity (top-cell/median ratio **1041** — sharply non-uniform), G4 1% imputed.
- **Spatial result is right:** top weighted cells are Rhine-Ruhr (peak), Berlin, SW-Germany/upper-Rhine,
  Hamburg, Cologne — real grid/industrial hubs, not population-uniform. The SW-Germany cell (48.3N,7.8E)
  overlaps the inversion hotspot region. This is the core thesis visible: emissions follow the grid.
- Output: `outputs/layer1_de_<date>.nc` (relative, uncalibrated; gitignored). P(GIS) is a MODELLED prior
  (`factors/gis_probability.csv`) — the weakest input, flagged for CIGRE firm-up.

**Next (2b):** Layer-2 point placement + combine + calibrate to national total + skill-score vs
EDGAR/GAINS (the "beats the proxy" test) + Germany hotspot comparison.

## Phase 2b verdict — Germany (2026-06-03): thesis NOT supported here — `outputs/validation_report_de.md`

Honest negative result. The rigorous skill score was impossible (inversion posterior is figures-only, no
downloadable array — not fabricated). Directional test against the inversion's published ~1/3-in-SW-focus
figure:
- **Ours 0.175, EDGAR 0.190, GAINS 0.175** SW-focus fraction vs truth ~0.33 — **all three badly miss the
  hotspot; ours did not beat the proxies** (tied with GAINS, marginally worse than EDGAR).
- Our prior IS structurally different (corr ours↔EDGAR 0.55, ours↔GAINS 0.34) — different ≠ better.
- **Root cause:** DE's dominant SF6 source is an under-reported industrial hotspot; our Layer-2 (E-PRTR)
  captures only **1.82 t of ~100 t**, so ours ≈ Layer-1 (grid) ≈ population-like concentration in
  Ruhr/Berlin, not the SW industrial region. No bottom-up method we have reproduces the truth in DE.
- **Implication:** Germany is plausibly a worst case (hotspot-dominated). The "infrastructure beats
  population" thesis is unproven; it may only hold where SF6 is grid-distributed — untested. Premise
  (gap real/unoccupied) still holds; *value over the proxy* is unproven. Decision needed before more build.

## Phase 2c verdict — France best case: directional POSITIVE — `validation_report_fr.md`

Tested the thesis' best case (grid-distributed country). Still no posterior, so directional not metric.
- **France: our prior is orthogonal to population** — corr(ours,EDGAR)=**-0.03**, corr(ours,GAINS)=**-0.02**,
  while the two population proxies agree at 0.69. Spatial sanity: top cells = Toulouse(#1), Lyon, Paris,
  Lorraine, Besançon — real RTE grid hubs, spread, Toulouse above Paris. L2 share 3.8% (grid-distributed,
  no hotspot). This is exactly the "SF6 ≠ population" direction the inversion literature endorses.
- **FR-vs-DE contrast (the payoff):** divergence from population is **maximal in FR (corr≈0)** vs
  **moderate in DE (0.55)**. The prior's value is **country-conditional** — promising where SF6 is
  grid-distributed (FR), absent where a hidden industrial hotspot dominates (DE).
- **Honest verdict:** consistent-with the thesis in the best case; NOT proof of "beats the proxy" (corr≈0
  = different-from-population, necessary not sufficient). Caveat: FR OSM over-tags sub-transmission as
  transmission (48,642 vs DE 8,835), so part of the low corr is granularity. Real metric still needs an
  inversion posterior (author collaboration). Net: a defensible **conditional** methods contribution.

## Posterior-discovery sweep (2026-06-03): a usable truth EXISTS — `posterior_catalog.md`

3-agent sweep + self-verified download. **Found + obtained one downloadable gridded SF6 posterior:
PANGAEA 880251 (Brunner 2017, InGOS)** — `posterior_flux`+`prior_flux`, 4 inversion systems
(NILU/EMPA/EMPA2/UKMO-InTEM), **Europe, 2011 only**, variable 405-cell grid, CC-BY-3.0. Verified by
loading `GRID_MEAN_INGOS_EMPA2_ASIM_H13v4_FLEXPART.nc`. Everything else (Vojta 2024/2025, Bristol,
NOAA, AGAGE, NIES) deposits only mole-fractions/code/national-totals; the two Zenodo "gridded SF6" are
GAINS **priors**. So the "structural ceiling" was half wrong: **a real metric 'beats the proxy' test is
now possible (FR+DE, 2011) without outreach** — caveats: single year 2011 (predates our 2020 priors),
coarse 405-cell grid, 4-system ensemble. Next build (2d): run the real metric test against InGOS 2011.

## Phase 2d verdict — REAL metric test: thesis NOT supported — `validation_report_metric.md`

Scored ours/EDGAR/GAINS vs the InGOS 2011 posterior (spatial correlation, normalized), FR+DE:
- **Germany: ours 0.637 vs EDGAR 0.900 / GAINS 0.899 (InGOS-prior 0.953).** Ours LOSES.
- **France: ours 0.121 vs EDGAR 0.915 / GAINS 0.911 (InGOS-prior 0.951).** Ours LOSES badly.
- **Overturns 2c:** "orthogonal to population" (which 2c called good) = orthogonal to the truth, because
  the posterior correlates ~0.90 WITH population. At testable scale, **population is a decent SF6 proxy;
  our infra prior is worse.** Founding premise ("population misplaces SF6") not supported quantitatively.
- Caveats: 2011 posterior is prior-dominated (0.95 corr with its own population prior → weakly
  constraining → partly circular); 2011 vs 2020/current; France OSM over-tagging noise — BUT clean-data
  Germany still loses, so not just an artifact.
- **Bottom line:** value-over-population is unproven AND now has a negative signal. Honest place to
  STOP/PIVOT the core claim, not scale. The verified pipeline + this honest negative ("OSM-substation
  prior does not improve on population for SF6 at testable scales") is itself the publishable result.
- **SUPERSEDED by 2e** (the 2011 test was weak/prior-dominated; a recent trustworthy posterior was found).

## Phase 2e verdict — REAL test vs ICOS 2020 posterior: thesis REFUTED — `validation_report_icos.md`

The "unchecked stone" (ICOS PARIS F-gas collection) turned out to hold **recent (2017-2024), fine
(0.23°), multi-system gridded SF6 posteriors with country masks** — the trustworthy truth we thought
didn't exist (both sweeps had misclassified it as national-only; user insisted on verifying → found it).
Ran the legitimate test (2020, FRA+DEU, 4-member ensemble, `country_fraction` masks):
- **FRA: ours 0.090 vs EDGAR 0.195 / GAINS 0.140.** Ours LOSES.
- **DEU: ours 0.002 vs EDGAR 0.139 / GAINS 0.034.** Ours LOSES (≈ uncorrelated).
- Caveats gone (recent, well-constrained, fine, ensemble, clean masks) AND consistent with 2011 →
  **robust negative.** Honest calibration: at 0.23° ALL priors correlate weakly (EDGAR 0.14-0.20);
  population is modestly-but-consistently better; ours is the worst.
- **CONCLUSION: the core thesis (infrastructure prior beats population for SF6) is REFUTED on the best
  public evidence.** Premise stands; value-over-proxy does not. STOP/bank. The verified pipeline + this
  multi-dataset negative is the real, publishable contribution. Outreach no longer needed — data settled it.
