"""Build the rough NF3 spatial prior from European semiconductor fabs (kill-test gate).

Reads factors/nf3_fabs_europe.csv, grids operating-2020 fabs onto a 0.1 deg Europe grid.
PRESENCE-ONLY (each fab = 1): per-site NF3 emissions are not publicly disclosed (UNSOURCED), and
Crolles is partly NF3-abated (on-site F2) so capacity/node weighting would mis-rank it. Presence tests
the one claim that survives: does fab LOCATION beat the population/built-up proxy?
Run:  python src/fab_prior.py
"""
import os
import csv

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "factors", "nf3_fabs_europe.csv")
OUT = os.path.join(ROOT, "outputs")
LON0, LON1, LAT0, LAT1, RES = -25.0, 45.0, 34.0, 72.0, 0.1


def load_fabs(operating_only=True):
    rows = []
    with open(CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if operating_only and r["status_2020"].strip().lower() != "operating":
                continue
            rows.append((r["name"], float(r["lat"]), float(r["lon"]), r["country"]))
    return rows


def build_grid(rows):
    lon = np.arange(LON0, LON1 + RES / 2, RES)
    lat = np.arange(LAT0, LAT1 + RES / 2, RES)
    g = np.zeros((lat.size, lon.size))
    placed = []
    for name, la, lo, cc in rows:
        i = int(round((la - LAT0) / RES)); j = int(round((lo - LON0) / RES))
        if 0 <= i < lat.size and 0 <= j < lon.size:
            g[i, j] += 1.0
            placed.append((name, cc, la, lo))
        else:
            print(f"[fab] WARN out-of-grid: {name} ({la},{lo})")
    return xr.DataArray(g, coords={"lat": lat, "lon": lon}, dims=("lat", "lon")), placed


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = load_fabs(operating_only=True)
    print(f"[fab] operating-2020 NF3 fabs: {len(rows)}")
    da, placed = build_grid(rows)
    for name, cc, la, lo in placed:
        print(f"  placed {name} [{cc}] @ ({la:.4f},{lo:.4f})")
    fp = os.path.join(OUT, "prior_nf3_europe_presence.nc")
    da.to_netcdf(fp)
    print(f"[fab] presence: {int((da.values>0).sum())} non-zero cells, sum {float(da.sum()):,.0f} -> {fp}")


if __name__ == "__main__":
    main()
