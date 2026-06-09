"""Build the global CF4 smelter spatial prior on the Puschel 1deg grid.

Reads factors/smelters_global.csv (+ the European gate list as fallback/supplement), grids
operating smelters onto the Puschel posterior grid (lon -180..179, lat -90..89, 1deg). Variants:
capacity-weighted and presence-only. Run:  python src/global_prior.py
"""
import os
import csv

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
GLOBAL_CSV = os.path.join(ROOT, "factors", "smelters_global.csv")
EU_CSV = os.path.join(ROOT, "factors", "smelters_europe_killtest.csv")

# Puschel grid (1 deg global)
LON = np.arange(-180, 180, 1.0)   # 360 centers, -180..179
LAT = np.arange(-90, 90, 1.0)     # 180 centers, -90..89


def _read(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            st = (r.get("status_2020") or "operating").strip().lower()
            if st != "operating":
                continue
            try:
                rows.append((float(r["lat"]), float(r["lon"]), float(r.get("capacity_ktpa") or 0)))
            except (ValueError, KeyError):
                continue
    return rows


def load_smelters():
    rows = _read(GLOBAL_CSV)
    src = "global"
    if not rows:                       # fallback to the European gate list until the global one lands
        rows = _read(EU_CSV)
        src = "europe-only (fallback)"
    return rows, src


def build(rows, weighted=True):
    g = np.zeros((LAT.size, LON.size))
    for la, lo, cap in rows:
        i = int(round(la + 90)); j = int(round(lo + 180))
        if 0 <= i < LAT.size and 0 <= j < LON.size:
            g[i, j] += (cap if weighted else 1.0)
    return xr.DataArray(g, coords={"lat": LAT, "lon": LON}, dims=("lat", "lon"))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, src = load_smelters()
    print(f"[global_prior] {len(rows)} operating smelters from {src}; capacity {sum(r[2] for r in rows):,.0f} ktpa")
    for weighted, tag in ((True, "capacity"), (False, "presence")):
        da = build(rows, weighted)
        da.name = "prior_weight"
        da.attrs = {
            "long_name": f"Smelter-resolved CF4 spatial prior, global ({tag}, relative)",
            "units": "1",
            "comment": (("Relative spatial weight (NOT absolute flux): rescale to the inversion total "
                         "before use as an a-priori. Weight = smelter nameplate capacity (ktpa). "
                         "CAUTION for global use: the registry under-covers China (~12 of ~120 smelters), "
                         "so this raw variant carries China at ~28% of weight vs its ~57% production "
                         "share; prefer prior_cf4_global_production.nc for country-share-correct use."
                         ) if weighted else
                        ("Relative spatial weight (NOT absolute flux): rescale to the inversion total "
                         "before use as an a-priori. Presence-only robustness variant (operating "
                         "smelter = 1). Registry under-covers China (~12 of ~120 smelters).")),
            "source": "factors/smelters_global.csv (operating-2020 smelters)",
        }
        fp = os.path.join(OUT, f"prior_cf4_global_{tag}.nc")
        da.to_netcdf(fp)
        print(f"[global_prior] {tag}: {int((da.values>0).sum())} non-zero 1deg cells -> {fp}")


if __name__ == "__main__":
    main()
