"""PFC-CF4 kill-test: does a smelter prior beat EDGAR (population/built-up) at predicting where the
CF4 inversion posterior puts emissions?

Truth = ICOS PARIS CF4 posterior, 2020, Europe, 6-member ensemble (RHIME/InTEM/ELRIS x NAME/FLEXPART),
FLAT prior (so observation-driven). Candidates = our smelter prior (capacity + presence variants) and
EDGAR CF4 (TOTALS + NFE). Spatial correlation per country (and pooled across smelter countries),
normalized per region. Adapted from sf6-spatial-prior/src/icos_metric.py.

Run:  python src/cf4_killtest.py
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
# Smelter countries to score individually (skipped automatically if absent / too few cells).
COUNTRIES = ["NOR", "ISL", "FRA", "ESP", "DEU", "SWE", "ROU", "GRC", "GBR", "ITA"]
MIN_CELLS = 8


def flux_files():
    return sorted(glob.glob(os.path.join(ICOS, "*cf4_yearly_flux.nc")))


def edges(c):
    c = np.asarray(c, float)
    mid = (c[1:] + c[:-1]) / 2
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


def country_labels(ds):
    raw = ds["country"].values
    return [c.decode() if isinstance(c, bytes) else str(c) for c in raw]


def main():
    files = flux_files()
    print(f"[cf4] ICOS CF4 ensemble members: {len(files)}")
    edgar_tot = B.load_edgar("CF4", YEAR, "TOTALS")
    secs = B.edgar_sectors("CF4")
    edgar_nfe = B.load_edgar("CF4", YEAR, "NFE") if "NFE" in secs else None
    ours_cap = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_capacity.nc"))
    ours_pres = xr.open_dataarray(os.path.join(OUT, "prior_cf4_europe_presence.nc"))

    cand_static = [("OURS-cap", ours_cap), ("OURS-pres", ours_pres), ("EDGAR-TOT", edgar_tot)]
    if edgar_nfe is not None:
        cand_static.append(("EDGAR-NFE", edgar_nfe))
    keys = [k for k, _ in cand_static]

    regions = COUNTRIES + ["POOL"]
    res = {r: {k: [] for k in keys} for r in regions}
    ncells = {}

    for f in files:
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        post = ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values  # mol m-2 s-1; rel only
        cfrac = ds.country_fraction
        labels = country_labels(ds)
        rg = {k: regrid(da, lat_e, lon_e) for k, da in cand_static}

        # per-country
        pool_mask = np.zeros_like(post, dtype=bool)
        avail = []
        for code in COUNTRIES:
            if code not in labels:
                continue
            ci = labels.index(code)
            mask = cfrac.isel(country=ci).values >= 0.5
            if mask.sum() < MIN_CELLS:
                continue
            avail.append(code)
            ncells[code] = int(mask.sum())
            pool_mask |= mask
            t = post[mask]
            for k in keys:
                res[code][k].append(corr(rg[k][mask], t))
        ncells["POOL"] = int(pool_mask.sum())
        tp = post[pool_mask]
        for k in keys:
            res["POOL"][k].append(corr(rg[k][pool_mask], tp))
        ds.close()

    # report
    hdr = "  ".join(f"{k:>10s}" for k in keys)
    print(f"\n=== CF4 kill-test — spatial corr vs ICOS 2020 posterior (ensemble mean +/- sd) ===")
    print(f"  {'region':8s} {hdr}   (N cells)")
    def ms(a):
        a = np.array(a, float)
        return f"{np.nanmean(a):.3f}±{np.nanstd(a):.2f}"
    verdict = []
    for r in regions:
        if not any(res[r][k] for k in keys):
            continue
        line = "  ".join(f"{ms(res[r][k]):>10s}" for k in keys)
        print(f"  {r:8s} {line}   (N={ncells.get(r,'?')})")
        ocap = np.nanmean(res[r]["OURS-cap"]); opres = np.nanmean(res[r]["OURS-pres"])
        etot = np.nanmean(res[r]["EDGAR-TOT"])
        best_ours = np.nanmax([ocap, opres])
        verdict.append(f"{r}: ours(best {best_ours:.3f}) vs EDGAR-TOT {etot:.3f} -> beats pop: {best_ours > etot}")

    print("\n=== VERDICT (ours beats EDGAR population/built-up proxy?) ===")
    for v in verdict:
        print("  " + v)
    wins = sum("True" in v for v in verdict)
    print(f"\n  {wins}/{len(verdict)} regions: smelter prior beats EDGAR. "
          f"Truth = ICOS CF4 2020, FLAT-prior (observation-driven), {len(files)}-member ensemble, Europe.")


if __name__ == "__main__":
    main()
