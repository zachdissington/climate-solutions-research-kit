"""HFC-23 kill-test: does an HCFC-22-plant prior beat EDGAR (population proxy) at predicting where the
HFC-23 inversion posterior puts emissions?

Truth = ICOS PARIS HFC-23 posterior, 2020, Europe, 6-member ensemble (ELRIS/InTEM/RHIME x NAME/FLEXPART),
FLAT prior (observation-driven). Candidate = our presence-only plant prior (5 permit-confirmed European
HCFC-22 producers). Baseline = EDGAR HFC-23 (TOTALS; EDGAR's only HFC-23 sector PRU_SOL == TOTALS).
Spatial correlation per plant-country and pooled across them, normalized per region.
Adapted from pfc-aluminium-prior/src/cf4_killtest.py.

Run:  python src/hfc23_killtest.py
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
# The 5 European HCFC-22-plant countries (scored individually + pooled). Neighbours added as controls.
COUNTRIES = ["NLD", "FRA", "ITA", "GBR", "DEU"]
CONTROLS = ["BEL", "ESP", "POL", "AUT"]  # no documented HCFC-22 plant -> expect ours to NOT help
MIN_CELLS = 8


def flux_files():
    return sorted(glob.glob(os.path.join(ICOS, "*hfc23_yearly_flux.nc")))


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
    print(f"[hfc23] ICOS HFC-23 ensemble members: {len(files)}")
    edgar_tot = B.load_edgar("HFC-23", YEAR, "TOTALS")
    ours_pres = xr.open_dataarray(os.path.join(OUT, "prior_hfc23_europe_presence.nc"))

    cand_static = [("OURS-pres", ours_pres), ("EDGAR-TOT", edgar_tot)]
    keys = [k for k, _ in cand_static]

    regions = COUNTRIES + CONTROLS + ["POOL", "POOL-CTRL"]
    res = {r: {k: [] for k in keys} for r in regions}
    ncells = {}

    for f in files:
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        post = ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values  # rel only
        cfrac = ds.country_fraction
        labels = country_labels(ds)
        rg = {k: regrid(da, lat_e, lon_e) for k, da in cand_static}

        pool_mask = np.zeros_like(post, dtype=bool)
        ctrl_mask = np.zeros_like(post, dtype=bool)
        for code in COUNTRIES + CONTROLS:
            if code not in labels:
                continue
            ci = labels.index(code)
            mask = cfrac.isel(country=ci).values >= 0.5
            if mask.sum() < MIN_CELLS:
                continue
            ncells[code] = int(mask.sum())
            if code in COUNTRIES:
                pool_mask |= mask
            else:
                ctrl_mask |= mask
            t = post[mask]
            for k in keys:
                res[code][k].append(corr(rg[k][mask], t))
        ncells["POOL"] = int(pool_mask.sum())
        ncells["POOL-CTRL"] = int(ctrl_mask.sum())
        for rname, m in (("POOL", pool_mask), ("POOL-CTRL", ctrl_mask)):
            tp = post[m]
            for k in keys:
                res[rname][k].append(corr(rg[k][m], tp))
        ds.close()

    hdr = "  ".join(f"{k:>10s}" for k in keys)
    print(f"\n=== HFC-23 kill-test — spatial corr vs ICOS 2020 posterior (ensemble mean +/- sd) ===")
    print(f"  {'region':10s} {hdr}   (N cells)")

    def ms(a):
        a = np.array(a, float)
        return f"{np.nanmean(a):.3f}±{np.nanstd(a):.2f}"

    verdict = []
    for r in regions:
        if not any(res[r][k] for k in keys):
            continue
        line = "  ".join(f"{ms(res[r][k]):>10s}" for k in keys)
        print(f"  {r:10s} {line}   (N={ncells.get(r,'?')})")
        opres = np.nanmean(res[r]["OURS-pres"]); etot = np.nanmean(res[r]["EDGAR-TOT"])
        verdict.append(f"{r}: ours-pres {opres:.3f} vs EDGAR-TOT {etot:.3f} -> beats pop: {opres > etot}")

    print("\n=== VERDICT (plant prior beats EDGAR population proxy?) ===")
    for v in verdict:
        print("  " + v)
    plant_v = [v for v in verdict if v.split(":")[0] in COUNTRIES + ["POOL"]]
    wins = sum("True" in v for v in plant_v)
    print(f"\n  {wins}/{len(plant_v)} plant-regions: HCFC-22-plant prior beats EDGAR. "
          f"Truth = ICOS HFC-23 2020, FLAT-prior, {len(files)}-member ensemble, Europe.")
    print("  (POOL-CTRL / control countries have no documented HCFC-22 plant -> ours should NOT win there.)")


if __name__ == "__main__":
    main()
