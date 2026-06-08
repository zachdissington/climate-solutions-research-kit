"""NF3 kill-test: does a semiconductor-fab prior beat EDGAR (population/built-up proxy) at predicting
where the NF3 inversion posterior puts emissions?

Truth = ICOS PARIS NF3 posterior, 2020, Europe, 6-member ensemble (ELRIS/InTEM/RHIME x NAME/FLEXPART),
FLAT prior. Candidate = presence-only fab prior (11 European fabs). Baseline = EDGAR NF3 (TOTALS).
Adapted from pfc-aluminium-prior/src/cf4_killtest.py / hfc23-hcfc22-prior/src/hfc23_killtest.py.
Run:  python src/nf3_killtest.py
"""
import os
import glob

import numpy as np
import xarray as xr

import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
ICOS = os.path.join(ROOT, "data", "posteriors", "icos")
YEAR = 2020
COUNTRIES = ["DEU", "FRA", "ITA", "IRL", "AUT", "NLD"]   # fab countries
CONTROLS = ["ESP", "POL", "SWE", "DNK"]                   # no major NF3 fab -> ours should not help
MIN_CELLS = 8


def flux_files():
    return sorted(glob.glob(os.path.join(ICOS, "*nf3_yearly_flux.nc")))


def edges(c):
    c = np.asarray(c, float); mid = (c[1:] + c[:-1]) / 2
    return np.concatenate([[c[0] - (mid[0] - c[0])], mid, [c[-1] + (c[-1] - mid[-1])]])


def regrid(da, lat_e, lon_e):
    latn = "lat" if "lat" in da.coords else "latitude"
    lonn = "lon" if "lon" in da.coords else "longitude"
    LA, LO = np.meshgrid(da[latn].values, da[lonn].values, indexing="ij")
    w = np.nan_to_num(da.values).ravel()
    H, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[lat_e, lon_e], weights=w)
    return H


def norm(v):
    v = np.clip(np.nan_to_num(v), 0, None); s = v.sum()
    return v / s if s else v


def corr(cand, truth):
    cn, tn = norm(cand), norm(truth)
    if cn.std() == 0 or tn.std() == 0:
        return float("nan")
    return float(np.corrcoef(cn, tn)[0, 1])


def main():
    files = flux_files()
    print(f"[nf3] ICOS NF3 ensemble members: {len(files)}")
    edgar_tot = B.load_edgar("NF3", YEAR, "TOTALS")
    ours = xr.open_dataarray(os.path.join(OUT, "prior_nf3_europe_presence.nc"))
    cand = [("OURS-pres", ours), ("EDGAR-TOT", edgar_tot)]
    keys = [k for k, _ in cand]
    regions = COUNTRIES + CONTROLS + ["POOL", "POOL-CTRL"]
    res = {r: {k: [] for k in keys} for r in regions}
    ncells = {}
    for f in files:
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        post = ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values
        cfrac = ds.country_fraction
        labels = [c.decode() if isinstance(c, bytes) else str(c) for c in ds["country"].values]
        rg = {k: regrid(da, lat_e, lon_e) for k, da in cand}
        pool = np.zeros_like(post, bool); ctrl = np.zeros_like(post, bool)
        for code in COUNTRIES + CONTROLS:
            if code not in labels:
                continue
            mask = cfrac.isel(country=labels.index(code)).values >= 0.5
            if mask.sum() < MIN_CELLS:
                continue
            ncells[code] = int(mask.sum())
            (pool if code in COUNTRIES else ctrl).__ior__(mask)
            t = post[mask]
            for k in keys:
                res[code][k].append(corr(rg[k][mask], t))
        ncells["POOL"] = int(pool.sum()); ncells["POOL-CTRL"] = int(ctrl.sum())
        for rn, m in (("POOL", pool), ("POOL-CTRL", ctrl)):
            tp = post[m]
            for k in keys:
                res[rn][k].append(corr(rg[k][m], tp))
        ds.close()

    def ms(a):
        a = np.array(a, float); return f"{np.nanmean(a):.3f}±{np.nanstd(a):.2f}"
    print(f"\n=== NF3 kill-test — spatial corr vs ICOS 2020 posterior (ensemble mean +/- sd) ===")
    print(f"  {'region':10s} " + "  ".join(f"{k:>10s}" for k in keys) + "   (N cells)")
    verdict = []
    for r in regions:
        if not any(res[r][k] for k in keys):
            continue
        print(f"  {r:10s} " + "  ".join(f"{ms(res[r][k]):>10s}" for k in keys) + f"   (N={ncells.get(r,'?')})")
        o = np.nanmean(res[r]["OURS-pres"]); e = np.nanmean(res[r]["EDGAR-TOT"])
        verdict.append((r, o, e, o > e))
    print("\n=== VERDICT (fab prior beats EDGAR population/built-up proxy?) ===")
    for r, o, e, w in verdict:
        print(f"  {r}: ours {o:.3f} vs EDGAR {e:.3f} -> beats pop: {w}")
    pv = [v for v in verdict if v[0] in COUNTRIES + ["POOL"]]
    wins = sum(1 for v in pv if v[3])
    print(f"\n  {wins}/{len(pv)} fab-regions: fab prior beats EDGAR. Truth = ICOS NF3 2020, FLAT-prior, "
          f"{len(files)}-member ensemble, Europe.")


if __name__ == "__main__":
    main()
