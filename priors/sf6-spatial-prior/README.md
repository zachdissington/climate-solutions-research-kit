# SF6-from-Grid Spatial Prior

An open, infrastructure-gridded **spatial prior** for sulfur hexafluoride (SF6) emissions from
electrical grid switchgear — a better disaggregation method than the population/nightlights proxy that
emissions inventories (EDGAR) and the atmospheric-inversion community currently use to grid F-gases.

**Status:** v1 in progress (started 2026-06-03). Impact/research artifact — not a product, not a business.

## What this is — and what it deliberately is NOT

This artifact was scoped by a pre-build adversarial stress test
(`../analysis/sf6-artifact-stress-test.md`, verdict MODIFY). Two tempting claims were falsified and are
**banned from this repo**:

- ❌ "First global gridded F-gas layer" — false. EDGAR v8 already publishes gridded F-gas emissions at
  0.1° (free, CC-BY); GAINS/IIASA publishes a second grid. We benchmark *against* them.
- ❌ "Facility-resolved per-asset SF6 emissions" — unsupportable. The `gas_insulated` OSM tag exists on
  only ~3,996 objects worldwide; GIS-vs-AIS status is unknowable for >99% of assets. We model it
  probabilistically and never publish bare per-asset kg claims.

What it **is**: a relative spatial prior — *where SF6 is likely concentrated* — built from grid
infrastructure location, calibrated to national totals, with explicit uncertainty bands and per-region
confidence scores. Offered to the inversion/inventory community as an upgrade, not a rival.

## The five guardrails (acceptance criteria)

1. Spatial prior, not an emissions ledger — uncertainty bands + confidence on every cell/asset.
2. Transmission-class substations only (filtered by the OSM `substation=` *type* tag, not voltage —
   voltage is only ~5% populated; see `phase1-findings.md`); GIS probability is an explicit layer.
3. Validation = beating the population/nightlights proxy cell-by-cell vs EDGAR + GAINS; calibrate to
   national totals; flag the manufacturing term; never claim UNFCCC agreement as success (UNFCCC ~2× low).
4. Geography honesty — US = calibration set (EPA GHGRP); EU = proof it beats population gridding;
   China/India/Africa = the value, labeled low-confidence model output.
5. **Two-layer model** — Layer 1 (grid switchgear from OSM substations) + Layer 2 (known industrial
   point sources). A pure substation map misses the dominant industrial hotspot the German inversion
   found. See `premise-verification.md`.

## Inputs

- **Layer 1 — OpenStreetMap** power infrastructure (substations + type/voltage tags), via `earth-osm`.
- **Layer 2 — industrial point sources** — SF6 producers, reclaimers/recyclers, magnesium producers,
  semiconductor fabs, switchgear OEMs; geocoded from E-PRTR / EPA GHGRP / company disclosures.
- **SF6 charge-by-voltage + leak-rate factors** — EPA / IEC / IPCC 2019 Refinement (in `factors/`).
- **Benchmarks/validation:** EDGAR v8 (0.1° gridded F-gas, population proxy — the baseline to beat),
  GAINS/IIASA grid, EPA GHGRP Subpart DD (US calibration), NOAA HATS global SF6 (trend sanity-check).

## Output

Gridded SF6 spatial prior in **NetCDF/GeoTIFF on a standard grid** (the format inversion modelers
ingest) plus a Climate-TRACE-compatible GeoJSON/CSV, every cell carrying uncertainty + confidence.

## Layout

```
factors/   committed factor tables (with citations)
src/       extraction -> model -> validation pipeline
data/      downloaded inputs (gitignored)
outputs/   spatial prior + validation reports (gitignored / sampled)
```

## Pointers

- Build plan: `../plans/2026-06-03-sf6-spatial-prior.md`
- Decision (reopened as impact project): `../decisions/2026-06-03-sf6-artifact-reopened-as-impact.md`
- Modified-scope spec: `../analysis/sf6-artifact-stress-test.md`
- v1 target + inputs: `../analysis/climate-trace-coverage-gaps.md`
