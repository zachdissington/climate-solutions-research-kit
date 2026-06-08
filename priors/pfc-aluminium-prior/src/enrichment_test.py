"""C2F6 enrichment cross-check (companion to c2f6_killtest.py's correlation metric, which is the primary
metric here since there are 27 smelters — non-degenerate, unlike HFC-23/NF3's one-point-per-country).

Percentile rank of the POSTERIOR vs PRIOR vs EDGAR at each operating-2020 smelter cell, within the
pooled smelter-country domain. Anti-circularity: prior low + posterior high => observations put C2F6 at
the smelters. Mirrors hfc23-hcfc22-prior/src/enrichment_test.py.
"""
import csv
import glob
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")
import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSVF = os.path.join(ROOT, "factors", "smelters_europe_killtest.csv")
files = sorted(glob.glob(os.path.join(ROOT, "data", "posteriors", "icos", "*pfc218_yearly_flux.nc")))
SMELTER_CC = ["NOR", "ISL", "FRA", "ESP", "DEU", "SWE", "ROU", "GRC", "GBR", "ITA"]


def load_smelters():
    rows = []
    with open(CSVF, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["status_2020"].strip().lower() == "operating":
                rows.append((r["name"], float(r["lat"]), float(r["lon"])))
    return rows


def ni(a, v):
    return int(np.abs(a - v).argmin())


def pct(field, mask, i, j):
    vals = field[mask]
    return 100.0 * (vals < field[i, j]).sum() / max(1, vals.size)


def main():
    smelters = load_smelters()
    e = B.load_edgar("C2F6", 2020, "TOTALS")
    eln = "lat" if "lat" in e.coords else "latitude"
    elo = "lon" if "lon" in e.coords else "longitude"
    ev = np.nan_to_num(e.values); ela, elo2 = e[eln].values, e[elo].values
    rows = {n: {"post": [], "prior": [], "edgar": []} for n, _, _ in smelters}
    for f in files:
        ds = xr.open_dataset(f)
        plat, plon = ds.latitude.values, ds.longitude.values
        post = np.nan_to_num(ds.flux_total_posterior.sel(time="2020", method="nearest").values)
        prior = np.nan_to_num(ds.flux_total_prior.sel(time="2020", method="nearest").values)
        labels = [c.decode() if isinstance(c, bytes) else str(c) for c in ds["country"].values]
        pool = np.zeros_like(post, bool)
        for cc in SMELTER_CC:
            if cc in labels:
                pool |= ds.country_fraction.isel(country=labels.index(cc)).values >= 0.5
        ia = np.abs(ela[None, :] - plat[:, None]).argmin(axis=1)
        jo = np.abs(elo2[None, :] - plon[:, None]).argmin(axis=1)
        eg = ev[np.ix_(ia, jo)]
        for n, la, lo in smelters:
            i, j = ni(plat, la), ni(plon, lo)
            if not pool[i, j]:
                continue
            rows[n]["post"].append(pct(post, pool, i, j))
            rows[n]["prior"].append(pct(prior, pool, i, j))
            rows[n]["edgar"].append(pct(eg, pool, i, j))
        ds.close()
    print("=== C2F6 smelter-cell percentile within pooled smelter-country domain (mean of members) ===")
    print(f"  {'smelter':22s} {'POST':>7s} {'PRIOR':>7s} {'EDGAR':>7s}")
    mp, mpr, me = [], [], []
    for n, _, _ in smelters:
        if not rows[n]["post"]:
            continue
        p, pr, ed = np.mean(rows[n]["post"]), np.mean(rows[n]["prior"]), np.mean(rows[n]["edgar"])
        mp.append(p); mpr.append(pr); me.append(ed)
        print(f"  {n[:22]:22s} {p:6.1f}% {pr:6.1f}% {ed:6.1f}%")
    print(f"\n  MEAN: POST {np.mean(mp):.1f}%  PRIOR {np.mean(mpr):.1f}%  EDGAR {np.mean(me):.1f}%  (n={len(mp)} in-domain smelters)")


if __name__ == "__main__":
    main()
