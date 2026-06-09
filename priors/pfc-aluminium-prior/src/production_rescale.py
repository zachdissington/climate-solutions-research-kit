"""Build the production-rescaled global CF4 smelter prior (the recommended global variant).

Problem it fixes (holistic validation 2026-06-09): the raw capacity-weighted registry under-represents
China (registry coverage ~12 of ~120 smelters, 28% of registry weight) while China produced 56.7% of
world primary aluminium in 2020 (USGS MCS 2021). For a GLOBAL inversion ingest, country-share error is
the first-order error. Fix: rescale so each country's total weight equals its 2020 primary-aluminium
PRODUCTION share (USGS), distributed within the country across registered smelters by capacity share.
Within-country placement still relies on the registry (disclosed: China carries its 12 major clusters).

Source: USGS Mineral Commodity Summaries, January 2021, "Aluminum" — World Smelter Production 2020e
(thousand metric tons): listed countries below; "Other countries" 9,000; World 65,200. The unlisted
registry countries share the 9,000 kt "Other" pool proportional to registry capacity.

Run:  <sf6 venv python> src/production_rescale.py
"""
import csv
import os

import numpy as np
import xarray as xr

from global_prior import GLOBAL_CSV, LAT, LON

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")


def _read_rows_with_country(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("status_2020") or "operating").strip().lower() != "operating":
                continue
            try:
                rows.append((r["country_iso3"], float(r["lat"]), float(r["lon"]),
                             float(r.get("capacity_ktpa") or 0)))
            except (ValueError, KeyError):
                continue
    return rows

USGS_2020_PROD_KT = {  # USGS MCS Jan 2021, 2020e smelter production
    "USA": 1000, "AUS": 1600, "BHR": 1500, "CAN": 3100, "CHN": 37000, "ISL": 840,
    "IND": 3600, "NOR": 1400, "RUS": 3600, "ARE": 2600,
}
USGS_OTHER_KT = 9000
USGS_WORLD_KT = 65200


def main():
    rows = _read_rows_with_country(GLOBAL_CSV)
    cap_by_c = {}
    for c, la, lo, cap in rows:
        cap_by_c[c] = cap_by_c.get(c, 0.0) + cap
    other_cap = sum(v for c, v in cap_by_c.items() if c not in USGS_2020_PROD_KT)

    target = {}
    for c in cap_by_c:
        if c in USGS_2020_PROD_KT:
            target[c] = float(USGS_2020_PROD_KT[c])
        else:
            target[c] = USGS_OTHER_KT * cap_by_c[c] / other_cap
    tt = sum(target.values())
    print(f"[rescale] registry countries: {len(cap_by_c)}; targeted production total {tt:,.0f} kt"
          f" (USGS world {USGS_WORLD_KT:,} kt; gap = producers absent from registry)")
    for c in sorted(target, key=target.get, reverse=True)[:12]:
        print(f"  {c}: target {target[c]:8,.0f} kt ({100*target[c]/tt:5.1f}%)  registry cap {cap_by_c[c]:8,.0f}")

    g = np.zeros((LAT.size, LON.size))
    for c, la, lo, cap in rows:
        w = target[c] * (cap / cap_by_c[c]) if cap_by_c[c] > 0 else 0.0
        i = int(round(la + 90)); j = int(round(lo + 180))
        if 0 <= i < LAT.size and 0 <= j < LON.size:
            g[i, j] += w
    da = xr.DataArray(g, coords={"lat": LAT, "lon": LON}, dims=("lat", "lon"), name="prior_weight")
    da.attrs = {
        "long_name": "Smelter-resolved CF4 spatial prior (production-rescaled, relative)",
        "units": "1",
        "comment": ("Relative spatial weight (NOT absolute flux). Country totals rescaled to USGS MCS "
                    "2021 national primary-aluminium production 2020e; distributed within each country "
                    "by registered smelter capacity. Rescale to the inversion total before use."),
    }
    fp = os.path.join(OUT, "prior_cf4_global_production.nc")
    da.to_netcdf(fp)
    chn_share = target.get("CHN", 0) / tt
    print(f"[rescale] wrote {fp}: {int((g > 0).sum())} non-zero cells; CHN share of field weight"
          f" {100*chn_share:.1f}% (field sum {float(g.sum()):,.0f} kt-equivalent)")


if __name__ == "__main__":
    main()
