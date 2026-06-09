"""A1 — Is the CF4 Europe win statistically real against spatial nulls?

The kill-test reported ensemble-member spread, which is NOT spatial significance. This script tests,
per ensemble member and region, whether (a) each candidate's spatial correlation with the posterior
beats a toroidal-shift null that preserves the candidate's own spatial structure, and (b) whether the
OURS-cap minus EDGAR-TOT correlation difference is distinguishable from zero under a moving-block
bootstrap that respects spatial autocorrelation. Adds Spearman rank correlation as a robustness check
(Pearson on a zero-inflated point field is fragile), and a CF4 smelter-cell enrichment test
(posterior percentile at smelter cells, vs the inversion's own flat prior and EDGAR).

numpy-only (the venv has no scipy). Deterministic: rng seeded.

Run:  <sf6 venv python> src/holistic_significance.py
"""
import csv
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")

import benchmarks as B
from cf4_killtest import COUNTRIES, MIN_CELLS, YEAR, country_labels, edges, flux_files, regrid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
EU_CSV = os.path.join(ROOT, "factors", "smelters_europe_killtest.csv")

REGIONS = ["ISL", "FRA", "DEU", "NOR", "ESP", "GBR", "POOL"]  # wins, losses, pooled
N_BOOT = 1000
N_SHIFT = 1000
BLOCK_SIZES = (10, 25)  # cells; sensitivity check (posterior autocorr length is uncertain)
RNG = np.random.default_rng(42)


def clip0(a):
    return np.clip(np.nan_to_num(a), 0, None)


def pearson(x, y):
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return pearson(rx, ry)


def block_index_sets(mask, bs):
    """Partition the mask's cells into bs x bs spatial blocks; return list of flat-index arrays."""
    ii, jj = np.where(mask)
    flat = np.ravel_multi_index((ii, jj), mask.shape)
    keys = (ii // bs) * 10_000 + (jj // bs)
    sets = {}
    for k, fl in zip(keys, flat):
        sets.setdefault(k, []).append(fl)
    return [np.array(v) for v in sets.values()]


def block_bootstrap_dr(cand_a, cand_b, truth, mask, bs, n=N_BOOT):
    """95% CI of delta_r = r(cand_a,truth) - r(cand_b,truth) under moving-block bootstrap."""
    blocks = block_index_sets(mask, bs)
    nb = len(blocks)
    a, b, t = cand_a.ravel(), cand_b.ravel(), truth.ravel()
    drs = np.empty(n)
    for k in range(n):
        pick = RNG.integers(0, nb, nb)
        idx = np.concatenate([blocks[p] for p in pick])
        drs[k] = pearson(a[idx], t[idx]) - pearson(b[idx], t[idx])
    drs = drs[np.isfinite(drs)]
    if drs.size == 0:
        return (float("nan"), float("nan")), len(blocks)
    return np.percentile(drs, [2.5, 97.5]), len(blocks)


def shift_null(cand, truth_m, mask, n=N_SHIFT):
    """Toroidal-shift null: correlation of the candidate field, randomly translated, with the truth
    inside the fixed mask. Preserves the candidate's own spatial structure."""
    H, W = cand.shape
    ii, jj = np.where(mask)
    dys = RNG.integers(0, H, n)
    dxs = RNG.integers(0, W, n)
    out = np.empty(n)
    for k in range(n):
        out[k] = pearson(cand[(ii - dys[k]) % H, (jj - dxs[k]) % W], truth_m)
    return out[np.isfinite(out)]


def cf4_enrichment(files):
    """CF4 analogue of enrichment_test.py: smelter-cell percentile of posterior / inversion prior /
    EDGAR within the pooled smelter-country domain."""
    smelters = []
    with open(EU_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["status_2020"].strip().lower() == "operating":
                smelters.append((r["name"], float(r["lat"]), float(r["lon"])))
    e = B.load_edgar("CF4", YEAR, "TOTALS")
    eln = "lat" if "lat" in e.coords else "latitude"
    elo = "lon" if "lon" in e.coords else "longitude"
    ev = np.nan_to_num(e.values)
    ela, elo2 = e[eln].values, e[elo].values

    def pct(field, mask, i, j):
        vals = field[mask]
        return 100.0 * (vals < field[i, j]).sum() / max(1, vals.size)

    rows = {n: {"post": [], "prior": [], "edgar": []} for n, _, _ in smelters}
    for f in files:
        ds = xr.open_dataset(f)
        plat, plon = ds.latitude.values, ds.longitude.values
        post = np.nan_to_num(ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values)
        prior = np.nan_to_num(ds.flux_total_prior.sel(time=str(YEAR), method="nearest").values)
        labels = country_labels(ds)
        pool = np.zeros_like(post, bool)
        for cc in COUNTRIES:
            if cc in labels:
                pool |= ds.country_fraction.isel(country=labels.index(cc)).values >= 0.5
        ia = np.abs(ela[None, :] - plat[:, None]).argmin(axis=1)
        jo = np.abs(elo2[None, :] - plon[:, None]).argmin(axis=1)
        eg = ev[np.ix_(ia, jo)]
        for n, la, lo in smelters:
            i, j = int(np.abs(plat - la).argmin()), int(np.abs(plon - lo).argmin())
            if not pool[i, j]:
                continue
            rows[n]["post"].append(pct(post, pool, i, j))
            rows[n]["prior"].append(pct(prior, pool, i, j))
            rows[n]["edgar"].append(pct(eg, pool, i, j))
        ds.close()
    print("\n=== CF4 smelter-cell percentile within pooled smelter-country domain (mean of members) ===")
    print(f"  {'smelter':30s} {'POST':>7s} {'FLATPRIOR':>9s} {'EDGAR':>7s}")
    mp, mpr, me = [], [], []
    for n, _, _ in smelters:
        if not rows[n]["post"]:
            continue
        p, pr, ed = np.mean(rows[n]["post"]), np.mean(rows[n]["prior"]), np.mean(rows[n]["edgar"])
        mp.append(p); mpr.append(pr); me.append(ed)
        print(f"  {n[:30]:30s} {p:6.1f}% {pr:8.1f}% {ed:6.1f}%")
    print(f"  MEAN: POST {np.mean(mp):.1f}%  FLATPRIOR {np.mean(mpr):.1f}%  EDGAR {np.mean(me):.1f}%"
          f"  (n={len(mp)} in-domain smelters)")


def main():
    files = flux_files()
    print(f"[A1] members: {len(files)}; N_BOOT={N_BOOT} N_SHIFT={N_SHIFT} blocks={BLOCK_SIZES}")
    edgar_tot = B.load_edgar("CF4", YEAR, "TOTALS")
    ours_cap = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_capacity.nc"))

    # grid resolution check (settles the 0.1-degree-vs-0.23-degree record question)
    ds0 = xr.open_dataset(files[0])
    dlat = float(np.diff(ds0.latitude.values).mean())
    dlon = float(np.diff(ds0.longitude.values).mean())
    print(f"[A1] ICOS grid: {ds0.latitude.size}x{ds0.longitude.size}, dlat={dlat:.4f} deg, dlon={dlon:.4f} deg")
    ds0.close()

    # member -> region -> stats
    summary = {r: [] for r in REGIONS}
    for f in files:
        member = os.path.basename(f).split("_EUROPE")[0]
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        post = clip0(ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values)
        post_raw = np.nan_to_num(ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values)
        cfrac = ds.country_fraction
        labels = country_labels(ds)
        ours = clip0(regrid(ours_cap, lat_e, lon_e))
        edgar = clip0(regrid(edgar_tot, lat_e, lon_e))

        masks = {}
        pool = np.zeros_like(post, bool)
        for code in COUNTRIES:
            if code not in labels:
                continue
            m = cfrac.isel(country=labels.index(code)).values >= 0.5
            if m.sum() < MIN_CELLS:
                continue
            pool |= m
            if code in REGIONS:
                masks[code] = m
        masks["POOL"] = pool

        for rg, m in masks.items():
            tm = post[m]
            r_ours = pearson(ours[m], tm)
            r_edgar = pearson(edgar[m], tm)
            sp_ours = spearman(ours[m], post_raw[m])
            sp_edgar = spearman(edgar[m], post_raw[m])
            null_o = shift_null(ours, tm, m)
            null_e = shift_null(edgar, tm, m)
            p_ours = (1 + (null_o >= r_ours).sum()) / (1 + len(null_o))
            p_edgar = (1 + (null_e >= r_edgar).sum()) / (1 + len(null_e))
            cis = {}
            for bs in BLOCK_SIZES:
                (lo, hi), nb = block_bootstrap_dr(ours, edgar, post, m, bs)
                cis[bs] = (lo, hi, nb)
            summary[rg].append(dict(member=member, n=int(m.sum()), r_ours=r_ours, r_edgar=r_edgar,
                                    dr=r_ours - r_edgar, sp_ours=sp_ours, sp_edgar=sp_edgar,
                                    p_ours=p_ours, p_edgar=p_edgar, cis=cis))
        ds.close()

    for rg in REGIONS:
        rows = summary[rg]
        if not rows:
            continue
        print(f"\n=== {rg} (N={rows[0]['n']}) ===")
        print(f"  {'member':16s} {'r_ours':>7s} {'r_edgr':>7s} {'dr':>7s} {'p_ours':>7s} {'p_edgr':>7s}"
              f" {'sp_ours':>8s} {'sp_edgr':>8s}  " +
              "  ".join(f"dr95CI(b={bs})" for bs in BLOCK_SIZES))
        for s in rows:
            ci_str = "  ".join(f"[{s['cis'][bs][0]:+.3f},{s['cis'][bs][1]:+.3f}]" for bs in BLOCK_SIZES)
            print(f"  {s['member']:16s} {s['r_ours']:7.3f} {s['r_edgar']:7.3f} {s['dr']:+7.3f}"
                  f" {s['p_ours']:7.3f} {s['p_edgar']:7.3f} {s['sp_ours']:8.3f} {s['sp_edgar']:8.3f}  {ci_str}")
        for bs in BLOCK_SIZES:
            k = sum(1 for s in rows if s["cis"][bs][0] > 0)
            print(f"  -> dr>0 significant (95% CI excl. 0, block={bs}): {k}/{len(rows)} members"
                  f"  (n_blocks={rows[0]['cis'][bs][2]})")
        k_shift = sum(1 for s in rows if s["p_ours"] < 0.05)
        ke_shift = sum(1 for s in rows if s["p_edgar"] < 0.05)
        print(f"  -> shift-null p<0.05: ours {k_shift}/{len(rows)} members, EDGAR {ke_shift}/{len(rows)}")

    cf4_enrichment(files)


if __name__ == "__main__":
    main()
