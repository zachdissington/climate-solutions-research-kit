# Factor & Input Sources — PFC-CF4 prior

*Rev 2026-06-12 (adversarial audit): China weight corrected to 27.5%; GEM coordinate count corrected
to 4; Tan et al. EF figures explicitly tagged unverified; non-deposited file pointers annotated.*

## Kill-test (gate) inputs — provenance + confidence

### CF4 inversion posterior (the ground truth)
- **ICOS PARIS F-gas inversion collection**, DOI 10.18160/GR1Q-6SK4 (collection URI
  `meta.icos-cp.eu/collections/n8myDc-I-gbHkdt3ajIYLLDe`). CC-BY-4.0.
- 6 CF4 members downloaded (object IDs): ELRIS×{FLEXPART `Y6dWqMGLwjtsU-Hup-HPJSIX`, NAME
  `CTLyibdOgwZx7MFmv5DhJyoD`}, InTEM×{FLEXPART `YjZ3lH2o_GSZqUI0uG1r3UoL`, NAME
  `YvaN2detryM0WUM35R3dLT4M`}, RHIME×{FLEXPART `GB9UGW2D4Erm7IxxElpkamkX`, NAME
  `3jC--jBn_uzddEF-k7SQI1bR`}. Europe domain, 391×293, yearly (incl. 2020), **FLAT prior**
  (so the posterior is observation-driven, not prior-dominated). Variables match the SF6 build
  (`flux_total_posterior` / `flux_total_prior` / `country_fraction`). Download = ICOS cookie
  mechanism (`curl -L -b "CpLicenseAcceptedFor=<id>" .../objects/<id>` → unzip the `_yearly_flux.nc`).

### EDGAR CF4 baseline (the population/built-up proxy to beat)
- **EDGAR v8.0_FT2022_GHG F-gases** bundle (reused from the SF6 build cache at
  `../sf6-spatial-prior/data/benchmarks/EDGAR_f-gases_emi_nc.zip`). CC-BY-4.0; Crippa et al.,
  ESSD 16:2811 (2024). CF4 is a separable substance folder (146 members), 0.1°, 1970–2022. CF4's
  aluminium emissions fall to the NFE sector; EDGAR allocates F-gas emissions spatially by population
  and built-up proxies (Crippa et al. 2024) rather than smelter coordinates — that is the proxy this
  prior aims to beat. (The specific backup-proxy mechanism for the NFE sector was characterized in a
  pre-build stress test from EDGAR documentation and has not been independently re-verified.)

### European smelter list (`smelters_europe_killtest.csv`, in the code repository, not this deposit) — GATE-GRADE, ROUGH
- **Locations**: verified public facts (operator sites / well-documented smelter coordinates),
  good to ~0.05°. These are the load-bearing input (a spatial prior is about *where*).
- **Capacities (ktpa)**: APPROXIMATE, gate-grade only — compiled from operator/industry figures
  (Hydro, Alcoa, Rio Tinto, Century, Trimet, Speira, Alro, Mytilineos, RUSAL, etc.). NOT a rigorous
  registry. The robustness check is a **presence-only** variant (each operating smelter = equal
  weight) reported alongside the capacity-weighted one — if smelter presence alone beats population,
  the verdict does not hinge on these capacity estimates.
- `status_2020`: operating vs idle in 2020 (idle: Trimet Voerde, RUSAL Nadvoitsy, Portovesme, KAP
  Podgorica, Aluminij Mostar). The primary prior uses operating smelters only.
- **The rigorous global registry** (USGS MCS + IAI + GEM gem.wiki, capacity + IPCC Tier-2 technology
  factors) is deep-build work (task T-002), not gate work.

## Global smelter registry (`smelters_global.csv`) — China INCOMPLETE (T-002 Phase A)
- **94** operating primary smelters worldwide with sourced coordinates + capacity (per-row `source`):
  GEM exact coords (4 rows: Weiqiao, Pingguo, Angul, EGA Jebel Ali), Wikipedia "List of aluminium
  smelters" (capacity/owner/status), and facility-specific coord sources (latitude.to / wikimapia /
  industryabout / company; some European rows use town centroids).
  At the Püschel **1° grid** (~111 km/cell), town-centroid coordinates are adequate.
- **Europe subset completed 2026-06-09** (holistic validation): the registry was missing 6 of the 27
  validated European smelters (Alcoa San Ciprian / Aviles / A Coruna ESP, Slovalco SVK, Talum SVN,
  Aldel NLD) — merged in from `smelters_europe_killtest.csv`, so the global field now contains the
  full Europe-validated configuration (25/25 one-degree cells).
- **Production-rescaled variant** (`outputs/prior_cf4_global_production.nc`, recommended for global
  use): country totals rescaled to USGS Mineral Commodity Summaries Jan 2021, "Aluminum", World
  Smelter Production 2020e (China 37,000 kt of world 65,200 kt = 56.7%; listed countries used
  directly; the 9,000 kt "Other countries" pool distributed across unlisted registry countries by
  registry capacity). Fixes the first-order country-share bias of the raw capacity field (China 27.5% of registry
  capacity — 11,765 of 42,822 ktpa, post-Europe-repair — vs 56.7% of 2020 production). Built by
  `src/production_rescale.py`.
- **China is badly under-represented: ~12 of ~120 smelters** (GEM rate-limited the registry agent after
  3 facilities; Wikipedia gives no usable China coords). The major clusters are present (Shandong/
  Weiqiao, Inner Mongolia, Xinjiang, Yunnan, Gansu, Ningxia, Henan, Guangxi) but the long tail is
  missing. This makes the China test in `validation_report_china.md` (in the code repository, not
  this deposit) unfair to the smelter prior — a fair China test needs a near-complete China registry
  (GEM full pull / Antaike / CNIA).
- **Cell technology: not obtained** (Tan et al. 2025 smelter-level xlsx is paywalled / 403; only its
  EF table was partially retrievable: China PFC EF ~0.25 vs RoW 0.61→0.27 tCO2e/t Al — China is modern
  PFPB, low per-tonne CF4. **These EF figures are from an incomplete retrieval of a paywalled source
  and have not been independently verified; they drive no published claim.**) Tier-2 technology
  weighting deferred; the registry's technology column ships unpopulated.

## Provenance discipline
No agent-estimated numbers in any committed factor that drives a published claim. Kill-test capacities
are explicitly flagged approximate and are stress-tested by the presence-only variant; the deep build
replaces them with sourced figures.
