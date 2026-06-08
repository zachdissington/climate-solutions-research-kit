"""Build the rough HFC-23 spatial prior from European HCFC-22 production plants (kill-test gate).

Reads factors/hcfc22_plants_europe.csv (5 permit-confirmed HCFC-22 producers, Rudel et al. 2024 RSC),
grids operating-2020 plants onto a 0.1 deg Europe grid.

Weighting choice (HFC-23-specific, differs from CF4): the PRIMARY prior is PRESENCE-ONLY (each
operating plant = 1). Capacity-weighting is deliberately NOT used here:
  - per-site HCFC-22 production capacity is not publicly documented (unsourced -> do not use);
  - fluoropolymer-output as a proxy would mis-rank the plant flagged as the likely-dominant emitter
    (Solvay Spinetta Marengo, whose FP output is unquantified) toward zero;
  - mandated HFC-23 incineration under the EU F-gas Regulation decouples emitted HFC-23 from
    throughput, so location-weight-by-size is not defensible for this gas.
A presence-only prior tests the one claim that survives: does plant LOCATION beat the population proxy?

Saves to outputs/ as a DataArray (lat, lon) for the kill-test regridder.
Run:  python src/plant_prior.py
"""
import os
import csv

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "factors", "hcfc22_plants_europe.csv")
OUT = os.path.join(ROOT, "outputs")

# 0.1 deg Europe grid (same extent as the CF4 build; comfortably covers all 5 plants).
LON0, LON1, LAT0, LAT1, RES = -25.0, 45.0, 34.0, 72.0, 0.1


def load_plants(operating_only=True):
    rows = []
    with open(CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if operating_only and r["status_2020"].strip().lower() != "operating":
                continue
            rows.append((r["name"], float(r["lat"]), float(r["lon"]), r["country"]))
    return rows


def build_grid(rows):
    """Presence-only: each operating plant contributes weight 1 to its cell."""
    lon = np.arange(LON0, LON1 + RES / 2, RES)
    lat = np.arange(LAT0, LAT1 + RES / 2, RES)
    g = np.zeros((lat.size, lon.size))
    placed = []
    for name, la, lo, cc in rows:
        i = int(round((la - LAT0) / RES))
        j = int(round((lo - LON0) / RES))
        if 0 <= i < lat.size and 0 <= j < lon.size:
            g[i, j] += 1.0
            placed.append((name, cc, la, lo))
        else:
            print(f"[plant] WARN out-of-grid: {name} ({la},{lo})")
    return xr.DataArray(g, coords={"lat": lat, "lon": lon}, dims=("lat", "lon")), placed


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = load_plants(operating_only=True)
    print(f"[plant] operating-2020 HCFC-22 plants: {len(rows)}")
    da, placed = build_grid(rows)
    for name, cc, la, lo in placed:
        print(f"  placed {name} [{cc}] @ ({la:.4f},{lo:.4f})")
    nz = int((da.values > 0).sum())
    fp = os.path.join(OUT, "prior_hfc23_europe_presence.nc")
    da.to_netcdf(fp)
    print(f"[plant] presence: {nz} non-zero cells, sum {float(da.sum()):,.0f} -> {fp}")


if __name__ == "__main__":
    main()
