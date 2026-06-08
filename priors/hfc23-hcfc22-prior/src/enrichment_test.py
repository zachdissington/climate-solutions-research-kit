"""The RIGHT decisive metric for a point-source prior (correlation under-scores a one-hot prior vs a
partly-diffuse posterior — the degenerate single-plant-per-country case CF4 flagged).

Enrichment test: at each plant cell, the percentile rank of the POSTERIOR value within the pooled
European plant-country domain, compared to EDGAR (population) and to the PRIOR at the same cell.
Anti-circularity guard: if the PRIOR does NOT peak at the plants but the POSTERIOR does, the
observations moved mass to the plants -> independent confirmation the plant locations are right.
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
files = sorted(glob.glob(os.path.join(ROOT, "data", "posteriors", "icos", "*hfc23_yearly_flux.nc")))
PLANTS = [("Dordrecht", 51.82, 4.73), ("PierreBenite", 45.71, 4.83), ("Spinetta", 44.89, 8.68),
          ("AGC-UK", 53.88, -3.00), ("Gendorf", 48.16, 12.66)]
PLANT_CC = ["NLD", "FRA", "ITA", "GBR", "DEU"]


def nearest_idx(arr, val):
    return int(np.abs(arr - val).argmin())


def pct_rank(field2d, mask, i, j):
    """Percentile rank (0-100) of cell (i,j)'s value among masked cells."""
    vals = field2d[mask]
    v = field2d[i, j]
    return 100.0 * (vals < v).sum() / max(1, vals.size)


def main():
    # build EDGAR on the posterior grid once (regrid via nearest sampling at plant cells is enough;
    # for percentile we need EDGAR sampled on the same mask -> regrid by interp to posterior grid)
    e = B.load_edgar("HFC-23", 2020, "TOTALS")
    elatn = "lat" if "lat" in e.coords else "latitude"
    elonn = "lon" if "lon" in e.coords else "longitude"

    rows = {name: {"post_pct": [], "prior_pct": [], "edgar_pct": []} for name, _, _ in PLANTS}
    pool_summary = {"post": [], "edgar": [], "prior": []}

    for f in files:
        ds = xr.open_dataset(f)
        plat, plon = ds.latitude.values, ds.longitude.values
        post = np.nan_to_num(ds.flux_total_posterior.sel(time="2020", method="nearest").values)
        prior = np.nan_to_num(ds.flux_total_prior.sel(time="2020", method="nearest").values)
        labels = [c.decode() if isinstance(c, bytes) else str(c) for c in ds["country"].values]
        # pooled mask over the 5 plant countries
        pool = np.zeros_like(post, dtype=bool)
        for cc in PLANT_CC:
            if cc in labels:
                pool |= ds.country_fraction.isel(country=labels.index(cc)).values >= 0.5
        # EDGAR sampled onto the posterior grid by manual nearest-neighbour (no scipy dependency)
        ev = np.nan_to_num(e.values)
        ela, elo = e[elatn].values, e[elonn].values
        ia = np.abs(ela[None, :] - plat[:, None]).argmin(axis=1)   # posterior-lat -> EDGAR-lat idx
        jo = np.abs(elo[None, :] - plon[:, None]).argmin(axis=1)   # posterior-lon -> EDGAR-lon idx
        edgar_grid = ev[np.ix_(ia, jo)]

        for name, la, lo in PLANTS:
            i, j = nearest_idx(plat, la), nearest_idx(plon, lo)
            rows[name]["post_pct"].append(pct_rank(post, pool, i, j))
            rows[name]["prior_pct"].append(pct_rank(prior, pool, i, j))
            rows[name]["edgar_pct"].append(pct_rank(edgar_grid, pool, i, j))
        ds.close()

    print("=== Plant-cell percentile rank within pooled European plant-country domain (mean over 6 members) ===")
    print(f"  {'plant':14s} {'POSTERIOR':>10s} {'PRIOR':>8s} {'EDGAR':>8s}   (higher post + low prior = obs put mass at plant)")
    for name, _, _ in PLANTS:
        pp = np.mean(rows[name]["post_pct"]); pr = np.mean(rows[name]["prior_pct"]); ed = np.mean(rows[name]["edgar_pct"])
        pool_summary["post"].append(pp); pool_summary["prior"].append(pr); pool_summary["edgar"].append(ed)
        print(f"  {name:14s} {pp:9.1f}% {pr:7.1f}% {ed:7.1f}%")
    print(f"\n  MEAN over 5 plants: POSTERIOR {np.mean(pool_summary['post']):.1f}%  "
          f"PRIOR {np.mean(pool_summary['prior']):.1f}%  EDGAR {np.mean(pool_summary['edgar']):.1f}%")
    print("\n  Interpretation:")
    print("   - POSTERIOR pct high  => the inversion concentrates HFC-23 at the plant cells.")
    print("   - PRIOR pct low       => that concentration is NOT inherited from the prior (anti-circularity).")
    print("   - EDGAR pct < POST    => population proxy under-places mass at the plants vs the truth.")


if __name__ == "__main__":
    main()
