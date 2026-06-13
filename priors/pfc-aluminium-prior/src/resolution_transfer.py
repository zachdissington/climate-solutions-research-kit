"""A2 — Does the validated Europe win transfer to the artifact actually shipped (1-degree global field)?

The kill-test ran on the ICOS native grid (0.234 x 0.352 deg) with the 27-smelter European registry.
The Zenodo deposit offers prior_cf4_global_*_flexinvert.nc: 1-degree global, built from the GLOBAL
registry (whose European subset may differ). This script:

1. Compares the Europe crop of the deposited global field against the validated European registry
   (which smelter cells are missing/extra).
2. Aggregates {ICOS posterior (area-weighted), EDGAR 0.1deg (sum), validated Europe prior (sum)} onto
   the deposit's 1-degree grid and recomputes per-region + pooled correlations for:
     SHIPPED-cap  = the deposited global capacity field, cropped to Europe
     VALID-1deg   = the validated Europe prior aggregated to 1 degree
     EDGAR-TOT    = EDGAR aggregated to 1 degree
   This separates the resolution effect from the registry-subset effect.
3. Runs the same significance checks at 1 degree (toroidal-shift null + block bootstrap on delta_r).

numpy-only. Run:  <sf6 venv python> src/resolution_transfer.py
"""
import csv
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")

import benchmarks as B
from cf4_killtest import COUNTRIES, YEAR, country_labels, flux_files, sel_year
from holistic_significance import block_bootstrap_dr, clip0, pearson, shift_null

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
EU_CSV = os.path.join(ROOT, "factors", "smelters_europe_killtest.csv")

REGIONS = ["ISL", "FRA", "DEU", "NOR", "ESP", "GBR", "POOL"]
MIN_CELLS_1DEG = 4
N_BOOT = 1000
BLOCKS_1DEG = (3, 6)  # 1-deg cells per block side


def grid_to_1deg_sum(da):
    """Aggregate a field carrying per-cell totals (EDGAR t/cell, prior weights) onto the deposit's
    1-deg global grid (centers lat -90..89, lon -180..179) by summing."""
    latn = "lat" if "lat" in da.coords else "latitude"
    lonn = "lon" if "lon" in da.coords else "longitude"
    la, lo = da[latn].values, da[lonn].values
    LA, LO = np.meshgrid(la, lo, indexing="ij")
    w = clip0(da.values).ravel()
    lat_e = np.arange(-90.5, 90.5 + 1e-9, 1.0)
    lon_e = np.arange(-180.5, 180.5 + 1e-9, 1.0)
    H, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[lat_e, lon_e], weights=w)
    return H  # 181 x 361 -> trim to 180x360 below


def trim(H):
    return H[:180, :360]


def post_to_1deg(post, lat, lon):
    """Aggregate posterior flux density (per m2) to 1-deg cells, cos(lat)-area-weighted sum (relative
    mass per cell; absolute scale is irrelevant for correlation)."""
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    w = (clip0(post) * np.cos(np.deg2rad(LA))).ravel()
    lat_e = np.arange(-90.5, 90.5 + 1e-9, 1.0)
    lon_e = np.arange(-180.5, 180.5 + 1e-9, 1.0)
    H, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[lat_e, lon_e], weights=w)
    return trim(H)


def cfrac_to_1deg(cf, lat, lon):
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    lat_e = np.arange(-90.5, 90.5 + 1e-9, 1.0)
    lon_e = np.arange(-180.5, 180.5 + 1e-9, 1.0)
    w = np.cos(np.deg2rad(LA)).ravel()
    num, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[lat_e, lon_e],
                               weights=np.nan_to_num(cf).ravel() * w)
    den, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[lat_e, lon_e], weights=w)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(den > 0, num / den, 0.0)
    return trim(frac)


def registry_cells_1deg(csv_path):
    """Expected nonzero 1-deg cells (i=lat+90, j=lon+180) from the operating-2020 European registry."""
    cells = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["status_2020"].strip().lower() != "operating":
                continue
            la, lo = float(r["lat"]), float(r["lon"])
            i, j = int(round(la + 90)), int(round(lo + 180))
            cells.setdefault((i, j), []).append(r["name"])
    return cells


def main():
    # ---- 1. registry-subset check: deposited global field vs validated Europe registry ----
    shipped = xr.open_dataset(os.path.join(OUT, "prior_cf4_global_capacity_flexinvert.nc"))["emis_prior"]
    sv = np.nan_to_num(shipped.values)  # 180 x 360, lat -90..89, lon -180..179
    eu_cells = registry_cells_1deg(EU_CSV)
    print("=== A2.1 registry-subset check: validated Europe smelter cells in the SHIPPED global field ===")
    missing, present = [], []
    for (i, j), names in sorted(eu_cells.items()):
        has = sv[i, j] > 0
        (present if has else missing).append((i, j, names, float(sv[i, j])))
    print(f"  validated Europe registry: {sum(len(n) for n in eu_cells.values())} operating smelters"
          f" -> {len(eu_cells)} 1-deg cells; present in shipped field: {len(present)}; MISSING: {len(missing)}")
    for i, j, names, _ in missing:
        print(f"    MISSING cell (lat={i-90}, lon={j-180}): {', '.join(names)}")

    # ---- 2. fields on the 1-deg grid ----
    edgar_tot = B.load_edgar("CF4", YEAR, "TOTALS")
    edgar1 = trim(grid_to_1deg_sum(edgar_tot))
    valid_eu = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_capacity.nc"))
    valid1 = trim(grid_to_1deg_sum(valid_eu))
    prod = xr.open_dataset(os.path.join(OUT, "prior_cf4_global_production_flexinvert.nc"))["emis_prior"]
    pv = np.nan_to_num(prod.values)
    cands = [("SHIPPED-cap", sv), ("PROD-resc", pv), ("VALID-1deg", valid1), ("EDGAR-TOT", edgar1)]

    # ---- 3. per-member correlations at 1 deg ----
    files = flux_files()
    summary = {r: [] for r in REGIONS}
    for f in files:
        member = os.path.basename(f).split("_EUROPE")[0]
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        post = sel_year(ds.flux_total_posterior, YEAR).values
        post1 = post_to_1deg(post, lat, lon)
        labels = country_labels(ds)
        masks = {}
        pool = np.zeros((180, 360), bool)
        for code in COUNTRIES:
            if code not in labels:
                continue
            cf1 = cfrac_to_1deg(ds.country_fraction.isel(country=labels.index(code)).values, lat, lon)
            m = cf1 >= 0.5
            if m.sum() < MIN_CELLS_1DEG:
                continue
            pool |= m
            if code in REGIONS:
                masks[code] = m
        masks["POOL"] = pool
        for rg, m in masks.items():
            tm = post1[m]
            row = dict(member=member, n=int(m.sum()))
            for name, c in cands:
                row[name] = pearson(c[m], tm)
            # significance for SHIPPED vs EDGAR at 1 deg
            null_s = shift_null(sv, tm, m, n=500)
            row["p_shipped"] = (1 + (null_s >= row["SHIPPED-cap"]).sum()) / (1 + len(null_s))
            row["cis"] = {}
            for bs in BLOCKS_1DEG:
                (lo_, hi_), nb = block_bootstrap_dr(sv, edgar1, post1, m, bs, n=N_BOOT)
                row["cis"][bs] = (lo_, hi_, nb)
            summary[rg].append(row)
        ds.close()

    for rg in REGIONS:
        rows = summary[rg]
        if not rows:
            print(f"\n=== {rg}: no members with >= {MIN_CELLS_1DEG} 1-deg cells ===")
            continue
        print(f"\n=== {rg} at 1 deg (N={rows[0]['n']}) ===")
        hdr = "  ".join(f"{n:>11s}" for n, _ in cands)
        print(f"  {'member':16s} {hdr} {'p_shipped':>10s}  " +
              "  ".join(f"drCI(b={bs})" for bs in BLOCKS_1DEG))
        for s in rows:
            vals = "  ".join(f"{s[n]:11.3f}" for n, _ in cands)
            ci_str = "  ".join(f"[{s['cis'][bs][0]:+.3f},{s['cis'][bs][1]:+.3f}]" for bs in BLOCKS_1DEG)
            print(f"  {s['member']:16s} {vals} {s['p_shipped']:10.3f}  {ci_str}")
        mean_row = {n: np.nanmean([s[n] for s in rows]) for n, _ in cands}
        print("  MEAN: " + "  ".join(f"{n}={mean_row[n]:.3f}" for n, _ in cands))
        for bs in BLOCKS_1DEG:
            k = sum(1 for s in rows if s["cis"][bs][0] > 0)
            print(f"  -> SHIPPED dr>0 significant (95% CI excl 0, block={bs}): {k}/{len(rows)} members")


if __name__ == "__main__":
    main()
