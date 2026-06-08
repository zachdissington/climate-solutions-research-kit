"""Build the rough CF4 smelter spatial prior for the kill-test.

Reads factors/smelters_europe_killtest.csv, grids operating-2020 smelters onto a 0.1 deg Europe grid.
Two variants (robustness): capacity-weighted and presence-only (each smelter = 1). Saves both to
outputs/ as DataArrays (lat, lon) for the kill-test regridder. Run:  python src/smelter_prior.py
"""
import os
import csv

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "factors", "smelters_europe_killtest.csv")
OUT = os.path.join(ROOT, "outputs")

# 0.1 deg Europe grid covering all listed smelters (Iceland -22, Kandalaksha 67N, etc.)
LON0, LON1, LAT0, LAT1, RES = -25.0, 45.0, 34.0, 72.0, 0.1


def load_smelters(operating_only=True):
    rows = []
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            if operating_only and r["status_2020"].strip().lower() != "operating":
                continue
            rows.append((r["name"], float(r["lat"]), float(r["lon"]), float(r["capacity_ktpa"])))
    return rows


def build_grid(rows, weighted=True):
    lon = np.arange(LON0, LON1 + RES / 2, RES)
    lat = np.arange(LAT0, LAT1 + RES / 2, RES)
    g = np.zeros((lat.size, lon.size))
    for _, la, lo, cap in rows:
        i = int(round((la - LAT0) / RES))
        j = int(round((lo - LON0) / RES))
        if 0 <= i < lat.size and 0 <= j < lon.size:
            g[i, j] += cap if weighted else 1.0
    return xr.DataArray(g, coords={"lat": lat, "lon": lon}, dims=("lat", "lon"))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = load_smelters(operating_only=True)
    print(f"[smelter] operating-2020 smelters: {len(rows)}; total capacity {sum(r[3] for r in rows):,.0f} ktpa")
    for weighted, tag in ((True, "capacity"), (False, "presence")):
        da = build_grid(rows, weighted=weighted)
        nz = int((da.values > 0).sum())
        fp = os.path.join(OUT, f"prior_cf4_europe_{tag}.nc")
        da.to_netcdf(fp)
        print(f"[smelter] {tag}: {nz} non-zero cells, sum {float(da.sum()):,.0f} -> {fp}")


if __name__ == "__main__":
    main()
