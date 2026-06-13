"""C2F6 (PFC-116) kill-test: does the aluminium-smelter prior beat EDGAR at predicting where the C2F6
inversion posterior puts emissions? The PFC artifact's second leg (CF4 = leg 1, GO).

Truth = ICOS PARIS C2F6 (pfc218) posterior, 2020, Europe, 6-member ensemble (ELRIS/InTEM/RHIME x
NAME/FLEXPART), FLAT prior. Candidates = the SAME smelter prior built for CF4 (capacity + presence
variants, gas-agnostic smelter locations) and EDGAR C2F6 (TOTALS + NFE/aluminium). Spatial correlation
per smelter country + pooled. Caveat: aluminium is the DOMINANT CF4 source but a MINORITY C2F6 source,
so expect weaker skill than CF4's 4x. Adapted from cf4_killtest.py.
Run:  python src/c2f6_killtest.py
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
COUNTRIES = ["NOR", "ISL", "FRA", "ESP", "DEU", "SWE", "ROU", "GRC", "GBR", "ITA"]
MIN_CELLS = 8


def flux_files():
    return sorted(glob.glob(os.path.join(ICOS, "*pfc218_yearly_flux.nc")))


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
    print(f"[c2f6] ICOS C2F6 ensemble members: {len(files)}")
    edgar_tot = B.load_edgar("C2F6", YEAR, "TOTALS")
    secs = B.edgar_sectors("C2F6")
    edgar_nfe = B.load_edgar("C2F6", YEAR, "NFE") if "NFE" in secs else None
    # Reuse the SAME smelter prior grids built for CF4 (smelter LOCATIONS are gas-agnostic).
    ours_cap = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_capacity.nc"))
    ours_pres = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_presence.nc"))

    cand = [("OURS-cap", ours_cap), ("OURS-pres", ours_pres), ("EDGAR-TOT", edgar_tot)]
    if edgar_nfe is not None:
        cand.append(("EDGAR-NFE", edgar_nfe))
    keys = [k for k, _ in cand]
    regions = COUNTRIES + ["POOL"]
    res = {r: {k: [] for k in keys} for r in regions}
    ncells = {}

    for f in files:
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        from cf4_killtest import sel_year
        post = sel_year(ds.flux_total_posterior, YEAR).values
        cfrac = ds.country_fraction
        labels = [c.decode() if isinstance(c, bytes) else str(c) for c in ds["country"].values]
        rg = {k: regrid(da, lat_e, lon_e) for k, da in cand}
        pool = np.zeros_like(post, bool)
        for code in COUNTRIES:
            if code not in labels:
                continue
            mask = cfrac.isel(country=labels.index(code)).values >= 0.5
            if mask.sum() < MIN_CELLS:
                continue
            ncells[code] = int(mask.sum()); pool |= mask
            t = post[mask]
            for k in keys:
                res[code][k].append(corr(rg[k][mask], t))
        ncells["POOL"] = int(pool.sum())
        tp = post[pool]
        for k in keys:
            res["POOL"][k].append(corr(rg[k][pool], tp))
        ds.close()

    def ms(a):
        a = np.array(a, float); return f"{np.nanmean(a):.3f}±{np.nanstd(a):.2f}"
    print(f"\n=== C2F6 kill-test — spatial corr vs ICOS 2020 posterior (ensemble mean +/- sd) ===")
    print(f"  {'region':8s} " + "  ".join(f"{k:>10s}" for k in keys) + "   (N cells)")
    verdict = []
    for r in regions:
        if not any(res[r][k] for k in keys):
            continue
        print(f"  {r:8s} " + "  ".join(f"{ms(res[r][k]):>10s}" for k in keys) + f"   (N={ncells.get(r,'?')})")
        bo = np.nanmax([np.nanmean(res[r]["OURS-cap"]), np.nanmean(res[r]["OURS-pres"])])
        et = np.nanmean(res[r]["EDGAR-TOT"])
        verdict.append((r, bo, et, bo > et))
    print("\n=== VERDICT (smelter prior beats EDGAR population/built-up proxy?) ===")
    for r, bo, et, w in verdict:
        print(f"  {r}: ours(best {bo:.3f}) vs EDGAR-TOT {et:.3f} -> beats pop: {w}")
    wins = sum(1 for v in verdict if v[3])
    print(f"\n  {wins}/{len(verdict)} regions: smelter prior beats EDGAR. Truth = ICOS C2F6 2020, "
          f"FLAT-prior, {len(files)}-member ensemble, Europe. (Caveat: Al = minority C2F6 source.)")


if __name__ == "__main__":
    main()
