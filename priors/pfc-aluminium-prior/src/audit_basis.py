"""Audit (2026-06-12): quantify the mass-vs-density basis mismatch in the published
native-grid CF4 correlations (holistic_significance.py correlates candidate per-cell MASS
against posterior flux DENSITY; cell area varies ~2.4x across the pooled domain).

Recompute per-member, per-region Pearson r for ours-capacity and EDGAR under:
  A. shipped basis  (posterior density, candidates mass)  -- must reproduce published
  B. mass basis     (posterior x cos(lat), candidates mass) -- the consistent basis
plus, on the mass basis, the Iceland fixed-tile bootstrap CI on dr and shift-null p
(same machinery, seeded) to check the published significance claim survives.
"""
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")

import benchmarks as B
from cf4_killtest import COUNTRIES, MIN_CELLS, YEAR, country_labels, edges, flux_files, regrid
from holistic_significance import block_bootstrap_dr, clip0, pearson, shift_null

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
REGIONS = ["ISL", "FRA", "DEU", "NOR", "ESP", "GBR", "POOL"]


def main():
    edgar_tot = B.load_edgar("CF4", YEAR, "TOTALS")
    ours_cap = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_capacity.nc"))
    files = flux_files()

    for mode in ("A-shipped-density", "B-mass-basis"):
        res = {r: [] for r in REGIONS}
        isl_sig = []
        for f in files:
            member = os.path.basename(f).split("_EUROPE")[0]
            ds = xr.open_dataset(f)
            lat, lon = ds.latitude.values, ds.longitude.values
            lat_e, lon_e = edges(lat), edges(lon)
            post = clip0(ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values)
            if mode == "B-mass-basis":
                post = post * np.cos(np.deg2rad(lat))[:, None]
            labels = country_labels(ds)
            ours = clip0(regrid(ours_cap, lat_e, lon_e))
            edgar = clip0(regrid(edgar_tot, lat_e, lon_e))
            masks = {}
            pool = np.zeros_like(post, bool)
            for code in COUNTRIES:
                if code not in labels:
                    continue
                m = ds.country_fraction.isel(country=labels.index(code)).values >= 0.5
                if m.sum() < MIN_CELLS:
                    continue
                pool |= m
                if code in REGIONS:
                    masks[code] = m
            masks["POOL"] = pool
            for rg, m in masks.items():
                res[rg].append((member, pearson(ours[m], post[m]), pearson(edgar[m], post[m])))
            if mode == "B-mass-basis" and "ISL" in masks:
                m = masks["ISL"]
                tm = post[m]
                r_o = pearson(ours[m], tm)
                null_o = shift_null(ours, tm, m)
                p_o = (1 + (null_o >= r_o).sum()) / (1 + len(null_o))
                cis = {bs: block_bootstrap_dr(ours, edgar, post, m, bs)[0] for bs in (10, 25)}
                isl_sig.append((member, p_o, cis))
            ds.close()
        print(f"\n=== {mode} ===")
        for rg in REGIONS:
            if not res[rg]:
                continue
            o = [x[1] for x in res[rg]]
            e = [x[2] for x in res[rg]]
            d6 = sum(1 for a, b in zip(o, e) if a > b)
            print(f"  {rg:5s} ours mean {np.nanmean(o):+.3f} (range {np.nanmin(o):+.3f}..{np.nanmax(o):+.3f})"
                  f" | EDGAR mean {np.nanmean(e):+.3f} | dr>0 in {d6}/{len(o)}")
        for member, p_o, cis in isl_sig:
            ci_s = "  ".join(f"b{bs}=[{lo:+.3f},{hi:+.3f}]" for bs, (lo, hi) in cis.items())
            print(f"  [ISL sig, mass basis] {member}: shift-null p={p_o:.3f}  drCI {ci_s}")


if __name__ == "__main__":
    main()
