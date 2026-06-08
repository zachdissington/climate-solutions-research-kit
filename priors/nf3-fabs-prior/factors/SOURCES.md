# Factor & Input Sources — NF3 / semiconductor-fab prior (kill-test gate)

## NF3 inversion posterior (the ground truth)
- **ICOS PARIS F-gas inversion collection**, DOI 10.18160/GR1Q-6SK4 (collection
  `meta.icos-cp.eu/collections/n8myDc-I-gbHkdt3ajIYLLDe`). CC-BY-4.0. Same collection as CF4/HFC-23.
- **6 NF3 ensemble members** (ELRIS/InTEM/RHIME × FLEXPART/NAME), Europe 293×391, yearly 2017–2024
  (incl. 2020), FLAT prior. Object hashes in `src/fetch_posteriors.py`. Download = ICOS cookie
  mechanism (`Cookie: CpLicenseAcceptedFor=<hash>` → `data.icos-cp.eu/objects/<hash>`).

## EDGAR NF3 baseline (the population/built-up proxy to beat)
- **EDGAR v8.0_FT2022_GHG F-gases** bundle (cached at `../sf6-spatial-prior/data/benchmarks/`).
  CC-BY-4.0; Crippa et al. ESSD 16:2811 (2024). NF3 single sector `PRU_SOL` ≡ `TOTALS`, 142.6 t/yr
  global 2020. EDGAR's v8 point-source layer (GEM: power/steel/coal/flaring) does NOT include
  semiconductor fabs, so NF3 falls to the built-up/population backup proxy — confirmed population-shaped
  this run (top European cells at Vienna/Graz/Linz, not fabs). EDGAR NF3 is also >10× below top-down
  (Park/Rigby 2024).

## European semiconductor-fab registry (`nf3_fabs_europe.csv`) — GATE-GRADE
- 11 operating-2020 European fabs that plausibly use NF3 (CVD chamber-clean / etch), from company /
  registry primary sources. Coordinates address/town-level (research-grade for a kill-test; geocode
  before any production use). Dominant NF3-intensity in the Dresden cluster (Infineon + GlobalFoundries),
  STMicro Crolles, Intel Leixlip. Excluded: Bosch Dresden (opened 2021), TSMC/ESMC Dresden (construction
  2024). **No European display fab at scale; no EU thin-film-solar (First Solar) fab** — both verified
  near-absent in-domain.
- **NF3-abatement note (load-bearing for the negative):** STMicro Crolles replaced NF3 with on-site F2
  (~2017, fabtech.org / ST Sustainability Report 2024); Intel Leixlip + STMicro run point-of-use
  abatement. So fab presence over-states emitted NF3.
- Sources per row are in the CSV `source` column (infineon.com, gf.com, bosch-semiconductors.com,
  xfab.com, st.com, exploreintel.com, nxp.com, silicon-saxony.de).

## Weighting choice — provenance discipline
- **PRESENCE-ONLY** (each operating fab = 1). Per-site NF3 emissions are **UNSOURCED — do not use**
  (fab-level F-gas data is corporate-confidential; E-PRTR did not break out NF3 by species/site in the
  2017–2024 window — also UNSOURCED). Node/throughput weighting rejected because Crolles (a top fab) is
  NF3-abated, which would invert the ranking.

## Published European NF3 references
- Park/Rigby et al. 2024, ES&T (DOI 10.1021/acs.est.4c04507; PMC11295121) — global NF3 inversion; Europe
  "not significantly different from zero" 2015–2021, ~12% of growth vs East Asia ~73%; names no European
  facilities; EDGAR >10× too low.
- Arnold et al. 2013, PNAS 110:2029 — seminal NF3 top-down; global only.
- PARIS project (horizoneurope-paris.eu) — the European F-gas inversion network these posteriors come
  from; added continuous NF3 at Taunus Observatory (DE) from Feb 2023. No facility-named NF3 grid.
- **No published European NF3 inversion or gridded inventory names individual fabs** — the gap is real;
  the fab prior just does not beat population in the European posterior.
