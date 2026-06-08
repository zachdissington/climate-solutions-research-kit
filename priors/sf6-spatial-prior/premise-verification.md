# Premise Verification — Should the SF6 Spatial Prior Exist At All?

> Run 2026-06-03, before committing further build effort. Method: three adversarial research agents
> (each tasked to *prove the artifact redundant*) + direct source-verification of the single
> load-bearing fact by reading the EDGAR supplement PDF locally. **Verdict: the premise holds — the
> gap is real and unoccupied. Build justified.**

## The existential question

The artifact's only claim to value is that it disaggregates national SF6 emission totals to grid cells
*better* than the spatial proxy existing inventories use. If existing inventories already grid SF6 by
electrical-grid / infrastructure location, the artifact is redundant. So the whole project hinges on
one fact: **what proxy do the existing products actually use for SF6?**

## Finding 1 — EDGAR grids SF6 by population (VERIFIED AT SOURCE)

The full chain, confirmed directly (not inferred):

- **IPCC → sector mapping:** `2D3+2E+2F+2G` → EDGAR sector **"Solvents and products use" (PRU_SOL)**.
  SF6's electrical-equipment emissions (IPCC 2G) and ODS-substitute F-gases (2F) both live here.
  Source: <https://edgar.jrc.ec.europa.eu/dataset_ghg50>
- **Sector → proxy** (EDGAR v8.0 supplement, Table S1 — read verbatim from the PDF):
  - `PRU` *"Production and use of other products"* → proxy **"Urban population"** ("In-house EDGAR
    proxy based on http://sedac.ciesin.columbia.edu/")
  - `SOL` *"Application of solvents"* → proxy **"Urban population, rural population"** (same CIESIN/SEDAC source)
  Source: <https://essd.copernicus.org/articles/16/2811/2024/essd-16-2811-2024-supplement.pdf> (Table S1)
- **Still current for v8.0:** the v8.0 paper lists the sectors that received revised proxies (power
  plants, iron & steel, coal mines, flaring, livestock, industrial facilities, shipping, residential).
  PRU/SOL/F-gases are **not** in that list, so the population proxy stands.
  Source: <https://essd.copernicus.org/articles/16/2811/2024/>

**The sharp point:** the *same* Table S1 shows EDGAR uses infrastructure proxies elsewhere — roads via
*"In-house EDGAR proxy based on OpenStreetMap"*, power plants via *CARMA v3* — but it deliberately does
**not** extend any infrastructure proxy to F-gases. SF6, which physically sits in substations, is
smeared across where people live. This is a gap EDGAR could have filled with data it already uses, and
didn't.

## Finding 2 — GAINS/IIASA: population + nightlights (same crude proxy)

Vojta et al. 2024, the main gridded SF6 reanalysis. Verbatim:

> "the attributed total national SF6 emissions are further distributed within the respective borders of
> each country according to two different proxy data sets, (1) the gridded population density
> (CIESIN, 2018) (UP) and (2) night light remote sensing data (Elvidge et al., 2021) (UN)"

Source: <https://acp.copernicus.org/articles/24/12465/2024/>. The companion IIASA "global emission
fields" product (0.1°, F-gases) uses the same population/nightlights approach.

## Finding 3 — Climate TRACE: national-only

The one organization doing asset-level emissions has **not** spatially resolved F-gases — they sit in
the "implicitly estimated" national-residual bucket (F-gases ≈ 2.4% of their database).
Sources: <https://climatetrace.org/data> · <https://github.com/climatetracecoalition/methodology-documents>

## Finding 4 — No OSM-power ↔ SF6 linkage exists anywhere

The open grid-data layer the artifact would build on (OpenStreetMap power infrastructure, OpenInfraMap,
MapYourGrid) is mature — but the curated master list of grid-mapping datasets/tools contains **zero**
SF6/F-gas/emissions-from-infrastructure entries. Nobody has connected the two.
Source: <https://github.com/open-energy-transition/Awesome-Electrical-Grid-Mapping>

## Finding 5 — The intended users explicitly need a better prior

Atmospheric-inversion groups all use crude priors for SF6, and several flag it as a limitation:

- **Bristol / ACP 2023 (the load-bearing quote):**
  > "For other compounds, such as SF6, used as insulator gas in high-voltage installations, the choice
  > of the a priori is not as obvious since their emissions may be more dominated by individual emission
  > hotspots."
  > "the uncertainty of the mole fraction baseline and the spatial distribution of the a priori
  > emissions have the largest impact on the a posteriori total emission estimates and their spatial
  > distribution."
  Source: <https://acp.copernicus.org/articles/23/14159/2023/>
- **European ensemble / ACP 2025:** distributes national totals by *"(1) gridded population density … or
  (2) nightlight remote sensing data."* Source: <https://acp.copernicus.org/articles/25/15197/2025/>
- **German InTEM / ACS ES&T Air 2025:** *"The EDGAR v8 … country totals were evenly distributed across
  each country as the prior emission value"* (flat-within-country).
  Source: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12706706/>
- **Global re-analysis / ACP 2024:** *"the choice of the a priori emission inventory … showed the
  biggest influence on the inversion results"*, and large under-observed regions (South America,
  southern Africa, India) are weakly constrained — there the **posterior ≈ the prior**, so a better
  prior matters *most* exactly where atmospheric monitoring is thin.
  Source: <https://acp.copernicus.org/articles/24/12465/2024/>

## The honest catch — refines the design, does not kill it

SF6 is **hotspot-dominated, and not all hotspots are substations.** The German inversion found its
single biggest source was an industrial SF6 *production/recycling* region (≈1/3 of national SF6), not
distributed switchgear — concluding window-disposal sources are overestimated and industrial sources
underestimated in the bottom-up inventory. Source: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12706706/>

Implications carried into the build:

1. **Two-layer model is mandatory:** Layer 1 = grid switchgear (OSM substations); Layer 2 = known
   industrial point sources (SF6 producers, reclaimers/recyclers, magnesium, semiconductor fabs, OEMs).
   A pure substation map would miss the dominant German hotspot. (Roughly two-thirds to three-quarters
   of *US* SF6 is electrical T&D per EPA — so the switchgear layer carries most of the signal in
   T&D-dominated countries, but not universally.)
2. **Geography/coverage tension:** the prior matters most where atmospheric data is sparse (Global
   South, India) — which is exactly where OSM grid coverage is weakest. Highest-value regions,
   lowest-confidence inputs. Must be labeled, not hidden.

## Caveats on this verification (stated honestly)

- EDGAR Table S1 is labeled v4.3.2; the link to v8.0 is inferential (v8.0 paper says the F-gas proxy
  was not revised) — solid, but not a single v8.0 sentence reading "SF6 = urban population."
- The German paper's full text is paywalled; the flat-prior quote is from the PMC mirror. Two specific
  strings cited elsewhere ("200% prior uncertainty", "southwest Germany cannot be explained") were not
  re-confirmed in the open abstract — treat as likely-but-unconfirmed until the full text is read.
- "No prior art" (Findings 3–4) is a negative result from targeted search, strong but not exhaustive of
  grey literature or utility-internal work.

## Verdict

The infrastructure-gridded SF6 spatial prior is **unoccupied**; every existing gridded product uses
population/nightlights — a proxy the inversion literature shows is physically wrong for SF6 — and the
intended users explicitly want better. The premise holds. Build proceeds, with the two-layer design and
geography-honesty baked in as acceptance criteria.
