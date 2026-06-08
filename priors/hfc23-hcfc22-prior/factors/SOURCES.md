# Factor & Input Sources — HFC-23 / HCFC-22 prior (kill-test gate)

## HFC-23 inversion posterior (the ground truth)
- **ICOS PARIS F-gas inversion collection**, DOI 10.18160/GR1Q-6SK4 (collection
  `meta.icos-cp.eu/collections/n8myDc-I-gbHkdt3ajIYLLDe`). CC-BY-4.0. Same collection as the CF4 build.
- The collection's 112 members carry **6 HFC-23 ensemble members** (confirmed by enumerating the
  collection): ELRIS/InTEM/RHIME × FLEXPART/NAME. Object hashes are in `src/fetch_posteriors.py`.
  Europe domain, 293×391, yearly 2017–2024 (incl. 2020), **FLAT prior** (so the posterior is
  observation-driven). Variables match the CF4/SF6 builds (`flux_total_posterior` / `flux_total_prior`
  / `country_fraction`). Download = ICOS cookie mechanism (`Cookie: CpLicenseAcceptedFor=<hash>` →
  `data.icos-cp.eu/objects/<hash>`, unzip the `_yearly_flux.nc`).
- The collection also holds 6-member ensembles for **NF3** (the Tier-2 portfolio candidate) and CH4,
  HFC-125/134a/143a/152a/32, N2O, CF4, pfc218 — all free for future gates.

## EDGAR HFC-23 baseline (the population proxy to beat)
- **EDGAR v8.0_FT2022_GHG F-gases** bundle (reused from the SF6 build cache at
  `../sf6-spatial-prior/data/benchmarks/EDGAR_f-gases_emi_nc.zip`). CC-BY-4.0; Crippa et al., ESSD
  16:2811 (2024). HFC-23 is a separable substance folder, 0.1°, single sector `PRU_SOL` ≡ `TOTALS`
  (9.30 kt/yr global 2020). Verified population-shaped this run: top European cells at Moscow / St.
  Petersburg / Voronezh, not at plants (see `validation_report_killtest.md` premise gate).

## European HCFC-22 plant registry (`hcfc22_plants_europe.csv`) — GATE-GRADE
- **The authoritative plant-level European source: Rüdel et al. 2024**, *Environ. Sci.: Processes
  Impacts*, DOI 10.1039/D3EM00426K — the EU/UK fluoropolymer emission inventory. It lists every site
  and which ones report **HCFC-22 + HFC-23 in their air permits** (the discriminator: HFC-23 in the
  permit ⇒ on-site HCFC-22 manufacture, not just downstream HFC use). 5 sites qualify:
  - Chemours **Dordrecht** (NL) 51.8177, 4.7294 — HFC-23 ~40 t/yr (2022 permit).
  - Arkema/Daikin **Pierre-Bénite** (FR) 45.7082, 4.8261 — HFC-23 6.5–15.4 t/yr (2015–2018).
  - Solvay/Syensqo **Spinetta Marengo** (IT) 44.8856, 8.6775 — dedicated HFC-23 incinerator;
    Italy flagged for 10–20× HFC-23 under-reporting (Chemistry World 3004163). Coord = village centroid.
  - AGC Chemicals **Thornton-Cleveleys / Hillhouse** (UK) 53.8831, -3.0009 — 2017 permit HCFC-22+HFC-23.
  - Dyneon (3M) **Gendorf / Burgkirchen** (DE) ~48.16, 12.66 — permit HCFC-22+HFC-23; **coord
    MEDIUM confidence** (chemical-park, town-level); 3M exiting PFAS by end-2025 (site winding down).
- **Excluded / out-of-domain:** HaloPolymer Kirovo-Chepetsk (~50.0°E) and Perm (~56.2°E) — confirmed
  HCFC-22/HFC-23 producers but EAST of the +39° domain bound. Mexichem/Orbia Runcorn (UK) — HFC site,
  no HCFC-22 production. Solvay Tavaux (FR) — in-domain FP site but permit lists HCFC-141b/142b/143a,
  NOT HCFC-22/HFC-23 → not an HFC-23 source. Gujarat Fluorochemicals (India) — out of domain.

## Weighting choice — provenance discipline
- **PRESENCE-ONLY is the primary (and only) prior.** Capacity-weighting was NOT used:
  - per-site HCFC-22 production capacity (t/yr) is **UNSOURCED — do not use** (only fluoropolymer
    output and two HFC-23 emission figures are public);
  - fluoropolymer-output as a proxy would push the likely-dominant, under-reported Spinetta Marengo
    toward zero (its FP output is unquantified) — actively misleading;
  - mandated HFC-23 incineration (EU F-gas Regulation) decouples emitted HFC-23 from throughput.
- No agent-estimated coordinates or capacities drive any committed claim. `hfc23_emission_tpy` is
  populated only where Rüdel et al. document it (Dordrecht, Pierre-Bénite); blank elsewhere.

## Published European HFC-23 references (for context)
- Stanley/Say/Mühle/Simmonds et al. 2018, ACP 18, 4153 — global AGAGE HFC-23 inversion; EU ~1.5% of
  global 2010–2016; does not name plants.
- Graziosi/Arduini et al. 2015, Atmos. Environ. 112, 196 — European HCFC-22 emissions, 11-yr inversion.
- Park et al. ACP 2023; Western/Stanley et al. Comms Earth & Env 2024 — East-Asia HFC-23, **figures-only**
  (no public gridded posterior — the decisive-region data wall).
