# Factor & Input Sources — PFC-CF4 prior

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
  aluminium emissions fall to the NFE sector; per the pre-build stress test EDGAR grids these by the
  GHSL built-up backup proxy, not smelter coordinates — that is the proxy this prior aims to beat.

### European smelter list (`smelters_europe_killtest.csv`) — GATE-GRADE, ROUGH
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
- ~88 operating primary smelters worldwide with sourced coordinates + capacity (per-row `source`):
  GEM exact coords (Weiqiao, Pingguo, Angul), Wikipedia "List of aluminium smelters" (capacity/owner/
  status), and facility-specific coord sources (latitude.to / wikimapia / industryabout / company).
  At the Püschel **1° grid** (~111 km/cell), town-centroid coordinates are adequate.
- **China is badly under-represented: ~12 of ~120 smelters** (GEM rate-limited the registry agent after
  3 facilities; Wikipedia gives no usable China coords). The major clusters are present (Shandong/
  Weiqiao, Inner Mongolia, Xinjiang, Yunnan, Gansu, Ningxia, Henan, Guangxi) but the long tail is
  missing. This makes the China test in `validation_report_china.md` unfair to the smelter prior — a
  fair China test needs a near-complete China registry (GEM full pull / Antaike / CNIA).
- **Cell technology: not obtained** (Tan et al. 2025 smelter-level xlsx is paywalled / 403; only its
  EF table was retrievable: China PFC EF ~0.25 vs RoW 0.61→0.27 tCO2e/t Al — China is modern PFPB, low
  per-tonne CF4). Tier-2 technology weighting deferred.

## Provenance discipline
No agent-estimated numbers in any committed factor that drives a published claim. Kill-test capacities
are explicitly flagged approximate and are stress-tested by the presence-only variant; the deep build
replaces them with sourced figures.
