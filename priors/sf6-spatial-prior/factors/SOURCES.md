# Factor Sources — SF6 Emission & Charge Parameters

All load-bearing numbers in this folder are sourced from authoritative documents and quoted verbatim.
No values are agent-estimated. Sourced 2026-06-03.

## Leak / use-phase emission factors (`leak_emission_factors.csv`) — SOURCED

The annual use-phase leak rate (as % of installed nameplate SF6 capacity per year) has a defensible
range, not a single value. Use a central ~0.5%/yr with the range below as the uncertainty band:

| Factor | Value | Source (verbatim) |
|---|---|---|
| Modern GIS/CB, leakage only | **0.5 %/yr** | IPCC GPG: *"leakage rates only (i.e. excluding maintenance losses) are of the order of 0.5% per year"* |
| IEC 694 newer (>=1980) max | **1 %/yr** | *"for newer equipment this value is 1%"* |
| IEC 694 pre-1980 max | **3 %/yr** | *"equipment manufactured before 1980 has a maximum leakage rate of 3%"* |
| EPA US fleet weighted-avg (lower bound) | **0.2 %/yr** | EPA: *"the weighted-average circuit breaker leak rate is approximately 0.2 percent per year"* |

Sources:
- IPCC Good Practice Guidance — *SF6 from Electrical Equipment and Other Uses*:
  <https://www.ipcc-nggip.iges.or.jp/public/gp/bgp/3_5_SF6_Electrical_Equipment_Other_Uses.pdf>
- EPA — *SF6 Leak Rates from High Voltage Circuit Breakers* (Blackman, field study of 2,300+ breakers
  manufactured 1998–2002): <https://www.epa.gov/system/files/documents/2022-05/leakrates_circuitbreakers.pdf>

Context worth carrying: ~10% of circuit-breaker populations may leak (EPA). The IPCC end-of-life
convention historically counted *"1% of the total quantity contained plus 70% of the quantity of
equipment manufactured 30 years prior"* as emissions — relevant to a disposal/end-of-life term if the
model adds one.

## Nameplate charge by voltage (`nameplate_charge_by_voltage.csv`) — PARTLY SOURCED (2026-06-03)

**Sourced per-breaker values** (Krondorfer, *Impact of high-voltage SF6 circuit breakers on global
warming*, EPA-hosted; data from the Solvay/ÖKOBILANZ life-cycle study, Hannover 1999):

| Equipment | Voltage | SF6 charge |
|---|---|---|
| GIS circuit breaker, 40 kA | 72.5 kV | **16 kg** |
| GIS circuit breaker, 40 kA | 145 kV | **15 kg** |
| AIS circuit breaker, 31.5 kA | 145 kV | **8 kg** |
| AIS circuit breaker, 63 kA | 145 kV | **10 kg** |

Source: <https://www.epa.gov/sites/default/files/2016-02/documents/conf00_krondorfer.pdf> (Table 1).

**Key finding — per-breaker charge is ~voltage-independent.** GIS holds ~15–16 kg whether 72.5 or
145 kV; GIS holds ~1.5–2× the AIS charge at the same voltage. So per-*substation* SF6 is driven by
**bay count + busbar extent** (which grow with voltage/importance), NOT by per-breaker charge. This is a
Phase-2 modelling decision: substation charge = charge_per_bay × n_bays, with bay-count the voltage scaler.

**Dead-end recorded:** EPA GHGRP Subpart DD publishes **no** default charge values — facilities use OEM
nameplate. Do not re-chase it for defaults.

**Higher-voltage scaling anchor:** lifecycle SF6 *loss* ≈ 3.4 kg (245 kV) / 7.5 kg (420 kV) per breaker
over 40 yr (EPA search result) — emissions, not charge, but fixes a ~2.2× 245→420 relative scaling.

**Still MODELLED_LOWCONF (245/420/550/765 kV):** extrapolated with ±50% bands. Firm up with **CIGRE
TB 430** and a **national inventory NIR** (UK NAEI / German / Swiss). Because Layer 1 calibrates to
national totals, only the *relative* cross-class scaling matters for v1 — but these rows should carry
their wide bands into the uncertainty layer until sourced.

## GWP

SF6 GWP100 is assessment-dependent: AR5 = 23,500; AR6 = 25,200; some recent studies use 24,700.
Pick ONE, state which, and apply consistently. (The model defaults to AR6 GWP100 = 25,200 unless changed.)

## Layer-2 point sources (`point_sources.csv` + `snapshots/`) — pull date 2026-06-03

- **US — EPA GHGRP** via Envirofacts REST (<https://data.epa.gov/efservice>). SF6 = `gas_id 6`.
  Facilities pulled for SF6-relevant subparts SS (manufacture), I (electronics), T (magnesium) =
  `industrial`; DD (T&D use) = `grid_use`. CO2e→mass via SF6 GWP above. Snapshot:
  `snapshots/ghgrp_sf6_2026-06-03.csv` (667 facilities).
- **EU — E-PRTR** via EEA **discodata** SQL API (<https://discodata.eea.europa.eu/sql>). Filter:
  `[IED].[latest].[PollutantRelease]` WHERE `pollutant='SF6' AND mediumCode='AIR'` (480 records,
  317,901 kg). Coordinates from `[IED].[latest].[FacilitiesPerSite]` (`x_4326`/`y_4326`, WGS84).
  **Join key (verified):** `PollutantRelease.facilityReportId → ProductionFacilityReport.Id`, then
  `FacilitiesPerSite` on `facilityLocalId = localId AND facilityNamespace = namespace AND
  facilityReportingYear = reportingYear`. Snapshot: `snapshots/eprtr_sf6_2026-06-03.csv` (84 facilities).
- **Recurring refresh:** re-run `src/point_sources.py` (same query) for updated data; each run writes a
  new dated snapshot. Validation gates (`src/validate_point_sources.py`) fail loud on any silent drop.
- **Coverage gap:** EU + US only. China (~57% of global SF6) and most of Asia have no facility-level
  reporting — a labeled gap, not silently omitted.

## P(GIS) gas-insulated probability (`gis_probability.csv`) — MODELLED, not measured

No clean published per-voltage GIS market-share figure exists (verified 2026-06-03 — vendor/CIGRE
sources give qualitative drivers, not percentages). The table is a **monotonic-in-voltage prior** with
wide bands, sourced from the qualitative facts: GIS spans 72.5–1200 kV, uses ~70% less space than AIS,
and is chosen where land is constrained (urban) / top reliability needed — so GIS share rises with
voltage and density (Hitachi Energy + Siemens Energy GIS product pages). Because Layer 1 calibrates to
national totals, the *relative* shape matters more than the absolute level. Firm up with CIGRE
GIS-population data. All rows flagged `MODELLED_LOWCONF`.
