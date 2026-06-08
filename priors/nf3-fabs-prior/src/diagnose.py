"""Interpret the NF3 kill-test: (1) is the European NF3 posterior CONSTRAINED, or is the signal ~zero so
the FLAT prior barely moves (then Europe is untestable, not a refutation)? (2) premise: is EDGAR NF3
population/built-up shaped? (3) enrichment + anti-circularity: percentile rank of POSTERIOR vs PRIOR vs
EDGAR at each fab cell (the right metric for a clustered point prior).
"""
import glob
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")
import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
files = sorted(glob.glob(os.path.join(ROOT, "data", "posteriors", "icos", "*nf3_yearly_flux.nc")))
FABS = [("Infineon-DD", 51.10, 13.77), ("GF-DD", 51.13, 13.74), ("Bosch-Reut", 48.49, 9.20),
        ("XFAB-Erfurt", 50.93, 11.05), ("ST-Crolles", 45.28, 5.88), ("ST-Rousset", 43.49, 5.61),
        ("ST-Agrate", 45.58, 9.36), ("ST-Catania", 37.50, 15.07), ("Intel-Leixlip", 53.376, -6.521),
        ("Infineon-Vil", 46.61, 13.85), ("NXP-Nijm", 51.85, 5.86)]
FAB_CC = ["DEU", "FRA", "ITA", "IRL", "AUT", "NLD"]


def ni(arr, v):
    return int(np.abs(arr - v).argmin())


def pct(field, mask, i, j):
    vals = field[mask]
    return 100.0 * (vals < field[i, j]).sum() / max(1, vals.size)


def main():
    print("=== posterior vs FLAT prior, 2020, per member (is Europe constrained or signal~0?) ===")
    for f in files:
        ds = xr.open_dataset(f)
        post = np.nan_to_num(ds.flux_total_posterior.sel(time="2020", method="nearest").values)
        prior = np.nan_to_num(ds.flux_total_prior.sel(time="2020", method="nearest").values)
        c = np.corrcoef(post.ravel(), prior.ravel())[0, 1] if post.std() and prior.std() else float("nan")
        ratio = np.nansum(np.abs(post - prior)) / (np.nansum(np.abs(prior)) + 1e-30)
        print(f"  {os.path.basename(f).split('_EUROPE')[0]:18s} corr(post,prior)={c:.3f}  L1(post-prior)/L1(prior)={ratio:.2f}")
        ds.close()

    print("\n=== EDGAR NF3 2020 spatial nature over Europe ===")
    e = B.load_edgar("NF3", 2020, "TOTALS")
    eln = "lat" if "lat" in e.coords else "latitude"
    elo = "lon" if "lon" in e.coords else "longitude"
    asc = e[eln].values[0] < e[eln].values[-1]
    sub = e.sel({eln: slice(34, 72) if asc else slice(72, 34), elo: slice(-25, 45)})
    v = np.nan_to_num(sub.values); nz = v.ravel()[v.ravel() > 0]
    print(f"  Europe cells>0: {nz.size}; top-10 = {np.sort(nz)[-10:].sum()/nz.sum()*100:.1f}% of total; max/mean={nz.max()/nz.mean():.0f}x")
    la, lo = sub[eln].values, sub[elo].values
    idx = np.dstack(np.unravel_index(np.argsort(v.ravel())[-6:], v.shape))[0]
    print("  EDGAR top-6 European NF3 cells (lat,lon):")
    for i, j in idx[::-1]:
        print(f"    ({la[i]:.2f},{lo[j]:.2f})  {v[i,j]:.4f}")

    print("\n=== enrichment: fab-cell percentile within pooled fab-country domain (mean of 6 members) ===")
    ev = np.nan_to_num(e.values); ela, elo2 = e[eln].values, e[elo].values
    rows = {n: {"post": [], "prior": [], "edgar": []} for n, _, _ in FABS}
    for f in files:
        ds = xr.open_dataset(f)
        plat, plon = ds.latitude.values, ds.longitude.values
        post = np.nan_to_num(ds.flux_total_posterior.sel(time="2020", method="nearest").values)
        prior = np.nan_to_num(ds.flux_total_prior.sel(time="2020", method="nearest").values)
        labels = [c.decode() if isinstance(c, bytes) else str(c) for c in ds["country"].values]
        pool = np.zeros_like(post, bool)
        for cc in FAB_CC:
            if cc in labels:
                pool |= ds.country_fraction.isel(country=labels.index(cc)).values >= 0.5
        ia = np.abs(ela[None, :] - plat[:, None]).argmin(axis=1)
        jo = np.abs(elo2[None, :] - plon[:, None]).argmin(axis=1)
        eg = ev[np.ix_(ia, jo)]
        for n, la_, lo_ in FABS:
            i, j = ni(plat, la_), ni(plon, lo_)
            rows[n]["post"].append(pct(post, pool, i, j))
            rows[n]["prior"].append(pct(prior, pool, i, j))
            rows[n]["edgar"].append(pct(eg, pool, i, j))
        ds.close()
    print(f"  {'fab':14s} {'POST':>7s} {'PRIOR':>7s} {'EDGAR':>7s}")
    mp, mpr, me = [], [], []
    for n, _, _ in FABS:
        p, pr, ed = np.mean(rows[n]["post"]), np.mean(rows[n]["prior"]), np.mean(rows[n]["edgar"])
        mp.append(p); mpr.append(pr); me.append(ed)
        print(f"  {n:14s} {p:6.1f}% {pr:6.1f}% {ed:6.1f}%")
    print(f"\n  MEAN: POST {np.mean(mp):.1f}%  PRIOR {np.mean(mpr):.1f}%  EDGAR {np.mean(me):.1f}%")


if __name__ == "__main__":
    main()
