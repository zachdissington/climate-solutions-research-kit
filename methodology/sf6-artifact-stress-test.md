# SF6 Artifact Stress Test — Pre-Build Gate

> Run 2026-06-02 (gate on `T-2026-06-02-009`), at Zach's direction: stress-test the SF6-from-grid
> artifact against prior art and technical reality BEFORE writing code.
> Method: 5 adversarial agents (each instructed to kill the artifact) + synthesis. Load-bearing claims
> spot-verified by direct fetch (EDGAR portal, OSM taginfo API).
> Raw data: `.tmp/validation/stress/*.json` (with sources per finding).

## Verdict: MODIFY

The artifact as originally specced is broken on two independent counts. A reframed version survives,
is still unoccupied, still solo-buildable, and is more scientifically defensible — but it is a more
modest product than "the first global facility-level F-gas map."

### Attack results

| Attack angle | Damage | What it killed |
|---|---|---|
| Gridded-inventory prior art | **SEVERE** | The existence claim. **EDGAR v8.0 publishes global gridded F-gas emissions at 0.1°** (1970–2022, free, CC-BY — spot-verified). GAINS/IIASA publishes a second grid at 0.5° (Vojta et al. 2024). "First global gridded F-gas layer" is false. |
| OSM data quality | **SEVERE** | The "facility-resolved" claim. The `gas_insulated` tag exists on **3,996 OSM objects worldwide** (spot-verified via taginfo API) vs a gas-insulated-switchgear base of hundreds of thousands. 47% of substations lack voltage tags. For >99% of assets, whether a substation contains ANY SF6 must be guessed. |
| Accuracy chain | **SEVERE** | The validation strategy. Manufacturing/OEM emissions (28–50% of SF6 consumption per IPCC) are invisible to a substation map. UNFCCC inventories — the proposed validation target — are themselves known to be ~2× low vs atmospheric measurements (US ~56% low). Per-asset uncertainty exceeds an order of magnitude. |
| Regulatory reporting coverage | WEAK | Almost nothing — confirmed the US already has facility-level SF6 (EPA GHGRP Subpart DD, ~93 reporters), so the US should be a calibration set, not a target. **>85% of global grid SF6 (China alone 57%) has no facility data and no path to it except bottom-up modeling.** |
| Climate TRACE deconfliction | WEAK | Nothing — confirmed the F-gas slot is genuinely orphaned: a flat 137.71 Mt CO2e carry-forward, unchanged month over month, no sector lead, no member activity. |

## Direct answers to Zach's two questions

### 1. "Is there truly nothing like this?"

**No — the literal claim was false.** EDGAR and GAINS/IIASA both publish global gridded F-gas/SF6
emissions, free. The US EPA publishes genuinely facility-resolved SF6 for ~93 US operators.

**What does NOT exist** (the real, narrower gap):
- Global SF6 gridded by **power-infrastructure location** instead of population density/nightlights —
  and the literature itself shows the population proxy misplaces SF6 (a documented SW-Germany hotspot
  "cannot be explained" by population)
- Any asset-level attribution for the **~85% of global grid SF6 outside the US** — China (57% of
  global, zero reporting), India, Africa, South America
- Any active work on Climate TRACE's F-gas line (verified orphaned)

### 2. "What is the real technical feasibility and accuracy?"

**Buildable solo from public data — but the honest accuracy ceiling is far below "facility-resolved":**
- Per-asset numbers would carry order-of-magnitude error bars (charge varies ~10× by design, leak
  rates 0.1–3%/yr = 30×, GIS/AIS status unknowable for >99% of assets)
- The largest emission term (manufacturing) is structurally invisible to this method
- A skeptical atmospheric scientist would reject per-asset kg claims outright
- **What IS defensible:** a relative spatial prior — "where is SF6 likely concentrated" — calibrated
  to national totals, with explicit uncertainty bands and per-region confidence scores

## The modified artifact (what survives)

**"An open, infrastructure-gridded spatial prior for SF6 emissions"** — a better disaggregation
method than the population/nightlights proxy that EDGAR and the atmospheric-inversion community use
today, offered to that community as an upgrade, not a rival.

The four modifications (from the synthesis verdict):

1. **Positioning:** drop "first" and "facility-resolved." The product is a *methods contribution*:
   infrastructure-based gridding as a better spatial prior, intended for correction by atmospheric
   inversion. The pitch audience is EDGAR/JRC, the Bristol/EMPA inversion groups, and Climate TRACE.
2. **Validation:** benchmark cell-by-cell against EDGAR and GAINS grids (beat the population proxy —
   that's the whole claim); calibrate to national totals; never claim agreement with UNFCCC as success
   (UNFCCC is known-wrong).
3. **Data honesty:** restrict to transmission-class substations (~6% of OSM substations — the real
   universe); model GIS-probability as an explicit probabilistic layer; label China/India/Africa rows
   as low-confidence model output; flag (never silently omit) the manufacturing term.
4. **Geography strategy:** US = calibration set (defer to EPA GHGRP), EU = proof the proxy beats
   population gridding, China/India = the actual value (explicitly modeled, low confidence). Partner
   with the MapYourGrid / open-energy-transition community (they own the OSM power-topology pipeline)
   rather than rebuilding it.

## The strongest argument against proceeding (stated plainly, per the gate's purpose)

The two original value claims are killed by two findings that cannot both be repaired: reframe to
infrastructure-gridding and you compete on proxy quality against EDGAR/IIASA on their home turf —
hardest to win exactly where it matters (China/India/Africa, where OSM is sparsest); keep
facility-resolution and the per-asset numbers are unfalsifiable and likely wrong. The danger is
shipping confident per-asset GeoJSON that passes a national-total check by compensating errors while
being wrong at every individual asset. The modified artifact avoids this only by being more modest:
a spatial prior with uncertainty bands, not an emissions ledger.

## What this means for the dual-track strategy

The strategy (`decisions/2026-06-02-dual-track-strategy.md`) survives unchanged — but the artifact's
nature is now clear: it is a **scientific methods contribution**, not a standalone data product. The
credibility it builds is with the emissions-science community (which is exactly who Climate TRACE,
EDGAR, and the inversion groups are). The Track 2 compounding asset is still real: whoever maintains
the best infrastructure-based SF6 prior, continuously updated as OSM and grid data improve, owns
something that gets more valuable every year. But the timeline to anything Thiel-shaped runs through
scientific credibility first.

## Decision required from Zach

- **Proceed with the modified scope** → T-2026-06-02-009 re-scopes to the spatial-prior artifact
- **Don't proceed** → fall back to the ranked gap list (wastewater CH4/N2O was the flagged backup) or
  return to strategy
