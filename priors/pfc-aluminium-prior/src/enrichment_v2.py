"""Enrichment metric v2 — referee-proofed recomputation for the ESSD manuscript (Rev 2).

Fixes the three methodological objections to cf4_enrichment() in holistic_significance.py:
1. COMMON BASIS: all fields compared as relative per-cell MASS on the posterior grid.
   Posterior/flat-prior densities (per m2) are multiplied by cell area (prop. to cos lat);
   EDGAR per-cell tonnes are aggregated CONSERVATIVELY (binned sum) onto the posterior grid,
   not nearest-neighbour sampled.
2. MIDRANK TIES: percentile = 100 * (n_below + 0.5 * n_equal) / n, so EDGAR's zero-inflated
   field is not artificially floored at the 0th percentile.
3. THE FLAT-PRIOR COLUMN IS REPORTED, plus the metric that isolates what observations did:
   the percentile of the posterior-minus-prior INCREMENT at smelter cells (positive increment
   above median = observations added mass at smelters relative to the flat start).

Also reports: count of smelter cells with positive increment, EDGAR exact-zero count on this
(conservative) grid, and a 3x3-neighbourhood-max sensitivity variant (inversions smear point
mass into adjacent cells; exact-cell matching is conservative against the smelter prior).

numpy-only. Deterministic. Run:  <sf6 venv python> src/enrichment_v2.py
"""
import csv
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")

import benchmarks as B
from cf4_killtest import COUNTRIES, YEAR, country_labels, edges, flux_files, sel_year

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EU_CSV = os.path.join(ROOT, "factors", "smelters_europe_killtest.csv")


def midrank_pct(field, mask, i, j):
    vals = field[mask]
    v = field[i, j]
    n = vals.size
    return 100.0 * ((vals < v).sum() + 0.5 * (vals == v).sum()) / max(1, n)


def nb_max(field, i, j):
    """3x3 neighbourhood max."""
    H, W = field.shape
    sl = field[max(0, i - 1):min(H, i + 2), max(0, j - 1):min(W, j + 2)]
    return float(sl.max())


def midrank_pct_value(value, vals):
    n = vals.size
    return 100.0 * ((vals < value).sum() + 0.5 * (vals == value).sum()) / max(1, n)


def main():
    smelters = []
    with open(EU_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["status_2020"].strip().lower() == "operating":
                smelters.append((r["name"], float(r["lat"]), float(r["lon"])))

    e = B.load_edgar("CF4", YEAR, "TOTALS")
    eln = "lat" if "lat" in e.coords else "latitude"
    elo = "lon" if "lon" in e.coords else "longitude"
    ev = np.nan_to_num(e.values)
    ELA, ELO = np.meshgrid(e[eln].values, e[elo].values, indexing="ij")

    files = flux_files()
    print(f"[enrichment v2] members: {len(files)}; common basis = per-cell mass on posterior grid;"
          f" midrank ties; EDGAR conservatively binned")

    rows = {n: {"post": [], "prior": [], "edgar": [], "incr": [], "post_nb": [], "incr_pos": [],
                "ratio": []}
            for n, _, _ in smelters}
    edgar_zero_members = {n: [] for n, _, _ in smelters}

    for f in files:
        ds = xr.open_dataset(f)
        plat, plon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(plat), edges(plon)
        area = np.cos(np.deg2rad(plat))[:, None] * np.ones((1, plon.size))

        post_d = np.clip(np.nan_to_num(sel_year(ds.flux_total_posterior, YEAR).values), 0, None)
        prior_d = np.clip(np.nan_to_num(sel_year(ds.flux_total_prior, YEAR).values), 0, None)
        post = post_d * area            # relative mass per cell
        prior = prior_d * area
        incr = (post_d - prior_d) * area  # signed increment mass
        with np.errstate(invalid="ignore", divide="ignore"):
            ratio = np.where(prior_d > 0, post_d / np.where(prior_d > 0, prior_d, 1.0), 0.0)
        # posterior/prior fold change: prior-level-independent measure of what observations did

        # conservative EDGAR aggregation: bin EDGAR cell masses into posterior cells
        eg, _, _ = np.histogram2d(ELA.ravel(), ELO.ravel(), bins=[lat_e, lon_e], weights=ev.ravel())

        labels = country_labels(ds)
        pool = np.zeros_like(post, bool)
        for cc in COUNTRIES:
            if cc in labels:
                pool |= ds.country_fraction.isel(country=labels.index(cc)).values >= 0.5

        pool_post = post[pool]
        pool_incr = incr[pool]

        for n, la, lo in smelters:
            i, j = int(np.abs(plat - la).argmin()), int(np.abs(plon - lo).argmin())
            if not pool[i, j]:
                continue
            rows[n]["post"].append(midrank_pct(post, pool, i, j))
            rows[n]["prior"].append(midrank_pct(prior, pool, i, j))
            rows[n]["edgar"].append(midrank_pct(eg, pool, i, j))
            rows[n]["incr"].append(midrank_pct(incr, pool, i, j))
            rows[n]["incr_pos"].append(1.0 if incr[i, j] > 0 else 0.0)
            rows[n]["ratio"].append(midrank_pct(ratio, pool, i, j))
            rows[n]["post_nb"].append(midrank_pct_value(nb_max(post, i, j), pool_post))
            edgar_zero_members[n].append(eg[i, j] == 0)
        ds.close()

    print(f"\n=== v2: smelter-cell midrank percentile, pooled smelter-country domain"
          f" (mean over covering members) ===")
    print(f"  {'smelter':32s} {'POST':>6s} {'FLAT':>6s} {'EDGAR':>6s} {'INCR':>6s} {'RATIO':>6s}"
          f" {'POSTnb':>7s} {'incr>0':>7s} {'EDGAR=0':>8s}")
    agg = {k: [] for k in ("post", "prior", "edgar", "incr", "ratio", "post_nb", "incr_pos")}
    nz = 0
    for n, _, _ in smelters:
        if not rows[n]["post"]:
            continue
        m = {k: np.mean(rows[n][k]) for k in agg}
        for k in agg:
            agg[k].append(m[k])
        ez = all(edgar_zero_members[n])
        nz += int(ez)
        print(f"  {n[:32]:32s} {m['post']:6.1f} {m['prior']:6.1f} {m['edgar']:6.1f}"
              f" {m['incr']:6.1f} {m['ratio']:6.1f} {m['post_nb']:7.1f} {m['incr_pos']:7.2f}"
              f" {str(ez):>8s}")
    print(f"\n  MEAN (n={len(agg['post'])} in-domain smelters):"
          f" POST {np.mean(agg['post']):.1f} | FLATPRIOR {np.mean(agg['prior']):.1f}"
          f" | EDGAR {np.mean(agg['edgar']):.1f} | INCREMENT {np.mean(agg['incr']):.1f}"
          f" | RATIO {np.mean(agg['ratio']):.1f} | POST-3x3 {np.mean(agg['post_nb']):.1f}")
    print(f"  smelter cells with positive posterior-minus-prior increment (mean share):"
          f" {np.mean(agg['incr_pos']):.2f}")
    print(f"  EDGAR exactly zero at smelter cell in ALL covering members (conservative binning):"
          f" {nz}/{len(agg['post'])}")


if __name__ == "__main__":
    main()
