# Climate TRACE Coverage Gaps — Self-Serve Research Record

> Researched 2026-06-02 (task `T-2026-06-02-008`), fully self-serve from public data — no outreach,
> no permission, no waiting on anyone (Zach's correction: TRACE's data is public; their role is a
> distribution channel chosen later, not an information source).
> Raw data + sources: `.tmp/validation/coverage/*.json` · Method: 2 sequential workflows
> (gap discovery → occupancy/feasibility verification) with deterministic Python joins between them.

## The result

**Target for the v1 open-source artifact: Fluorinated Gases (F-gases) — starting with SF6 from the
electrical grid.** Final score 7.5/10, the only candidate that is simultaneously orphaned, structurally
protected from satellite competitors, and solo-buildable from public data.

## How the ranking was derived

**Step 1 — coverage audit (public TRACE inventory + methodology docs):** 10 sectors rated by coverage
type (asset-level-observed vs modeled) and quality. **Step 2 — coalition ownership map:** which sectors
have named member organizations vs orphans. **Step 3 — external gap signals:** academic/IPCC literature
on monitoring gaps. **Step 4 — deterministic join** (`scripts/join_coverage_gaps.py`): coverage weakness
× orphan status × external confirmation × EO-detectability × Drawdown Gt-relevance (impact numbers from
solution frontmatter, never agent-estimated). **Step 5 — adversarial occupancy + feasibility verification**
of the top 4 (one agent each, kill-test standard).

### The join ranking (step 4)

| Score | TRACE Sector | Coverage | Orphaned? | Drawdown Gt/yr (published) |
|---|---|---|---|---|
| 13 | **Fluorinated Gases** | WEAK (national estimates only) | **YES — no lead org** | 2.7 |
| 9 | Waste | WEAK | No (RMI/JHU, weak) | 6.23 |
| 7 | Transportation | Moderate | No (JHU APL) | 2.3 |
| 6 | Mineral Extraction | Moderate | YES | 0.12 |
| 6 | Forestry & Land Use | **STRONG (CTrees)** | No | 8.31 |

Notable: **forestry — the capability cluster the impact-path analysis pointed at — is TRACE's strength,
not its gap** (CTrees owns it). The gap analysis redirected the artifact target away from forests and
toward F-gases. The Protection & Enforcement *capability* thesis still stands; its first application
just isn't forests.

### The verification verdict (step 5)

| Score | Candidate | Occupancy | Solo-feasible? | Why |
|---|---|---|---|---|
| **7.5** | **Fluorinated Gases** | **THIN** | **YES** | See below |
| 4.5 | Waste (landfill methane) | OCCUPIED | With partners | Most occupied sub-sector: RMI leads it + Carbon Mapper/GHGSat/MethaneSAT all image landfill plumes. (Residual gap noted in **wastewater** CH4/N2O — backup option.) |
| 2.5 | Mineral extraction | OCCUPIED | No | GEM/Ember/UNEP IMEO crowded in 2025–26; abandoned-mine emissions are below satellite detection thresholds. |
| 2.5 | Maritime/fishing | OCCUPIED | With partners | JHU APL (coalition) + Global Fishing Watch own it with proprietary AIS/SAR pipelines. |

## Why Fluorinated Gases won

**The gap is real and structurally protected:**
- Climate TRACE reports F-gases at national level only, with NO named coalition lead — the only
  major sector in that state
- No company does global asset-level F-gas work — and **none ever can via satellites**: F-gas
  atmospheric concentrations are parts-per-trillion and form no detectable plume. GHGSat, Carbon
  Mapper, Kayrros are all locked out by physics. The competitors that killed every other candidate
  cannot enter this one.
- The science world (AGAGE/NOAA networks, Bristol/EMPA inverse modeling) produces national/regional
  numbers only — nobody produces a facility-resolved global map
- Drawdown relevance: Alternative Refrigerants (2.5–2.7 Gt/yr, Emergency Brake) + Refrigerant
  Management (Drawdown legacy estimate ~96.5 Gt cumulative 2020–2050)

**The v1 artifact is solo-buildable from public data (verified):**
- **SF6 from the electrical grid** — the cleanest first slice. SF6 has GWP ~23,500 (the most potent
  greenhouse gas regulated); electrical switchgear is its dominant use.
- Inputs: OpenStreetMap power infrastructure (~1M substations + 125k plants, voltage-tagged, CC0,
  extractable via the `earth-osm` Python tool — verified active, v3.0.2 Nov 2025) × published SF6
  nameplate-charge-by-voltage and leak-rate factors (EPA/IEC, IPCC 2019 Refinement)
- Output: per-asset annual SF6 kg + CO2e, GeoJSON/CSV, Climate-TRACE-compatible schema
- Validation: national rollups vs UNFCCC inventories and AGAGE/EMPA top-down inversions; trend
  sanity-check vs NOAA HATS global SF6 data (public domain)
- v2: HFCs from refrigeration/AC via UN Comtrade trade flows + IPCC vintaging model
- The methods are published and reproducible (IPCC Tier 2; EU/China Comtrade gap studies; NY State
  vintaging inventory) — the operator extends them globally, doesn't invent physics

**Stated honestly — the kill risk:**
Asset-level F-gas figures are model-based disaggregation, not per-asset measurement (no plume = no
ground truth per asset). Validation works only in aggregate. A skeptic can argue it "adds resolution
without adding measurement." Counter-argument: that is exactly what the IPCC Tier 2 standard of
practice is, it materially upgrades TRACE's national-only line, and the same critique applies to most
of TRACE's non-plume sectors.

## The full-circle observation

The F-gas/refrigerant domain has now appeared three times in this project:
1. **Wedge ranking #2** (Refrigerant Management, 23/24) → falsified: RefriComply sells SMB compliance
   software at $23/mo — the obvious play was taken
2. **Feasibility shortlist** → refrigerant compliance was the strongest SMB instance, still occupied
3. **Coverage-gap research** → at the *global emissions monitoring* level, the same domain is the #1
   orphaned gap that no incumbent (SMB SaaS or satellite company) can reach

Same domain, three altitudes: the SMB-software altitude is crowded, the satellite altitude is
physically impossible, and the modeling/aggregation altitude in between is empty. That middle altitude
is exactly the shape of work AI agents + public data are good at — which is the macro thesis in miniature.

## Channel options (decided later, after the prototype exists)

| Channel | Fit for the SF6/F-gas artifact |
|---|---|
| Climate TRACE coalition | Best fit — they have the orphaned sector and a verified contributor-funding precedent (SLU, $409K) |
| Prize competitions | No current F-gas-specific prize found; generic AI-for-climate competitions apply |
| Carbon registries (Verra methodology) | Weak fit for v1 (F-gas destruction credits exist but are a different niche) |
| Academic co-publication | Strong secondary: the Bristol/EMPA groups are the natural validators |

## Next step

T-2026-06-02-009 (artifact scoping) now has its named target: **the global SF6-from-grid emissions
layer.** Scoping = pinning the exact OSM extraction, the charge/leak factor tables, the validation
datasets, and the output schema. After that: build.
