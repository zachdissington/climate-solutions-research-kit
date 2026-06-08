"""Phase 2e: the REAL metric test vs the ICOS PARIS 2017-2024 SF6 posterior (year 2020).

Score ours / EDGAR / GAINS / ICOS-own-prior against flux_total_posterior, for FRA + DEU, across the
SF6 ensemble (InTEM & ELRIS x FLEXPART & NAME = 4 members), using the dataset's own country_fraction
masks. Recent (2020 matches our priors), fine grid (293x391 ~0.23x0.35deg), well-constrained,
multi-system. This supersedes the InGOS-2011 test. Spatial-allocation only (normalized per country).

Run:  python src/icos_metric.py
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
COUNTRIES = {"FRA": "fr", "DEU": "de"}   # ICOS country code -> our prior-grid suffix


def sf6_flux_files():
    fs = glob.glob(os.path.join(ICOS, "**", "*sf6_yearly_flux.nc"), recursive=True)
    fs += glob.glob(os.path.join(ICOS, "*sf6_yearly_flux.nc"))
    return sorted(set(fs))


def edges(centers):
    c = np.asarray(centers, float)
    mid = (c[1:] + c[:-1]) / 2
    return np.concatenate([[c[0] - (mid[0] - c[0])], mid, [c[-1] + (c[-1] - mid[-1])]])


def regrid_to_icos(da, lat_e, lon_e):
    """Sum a per-cell candidate grid (lat,lon) onto the ICOS bins -> (nlat,nlon) array."""
    latn = "lat" if "lat" in da.coords else "latitude"
    lonn = "lon" if "lon" in da.coords else "longitude"
    LA, LO = np.meshgrid(da[latn].values, da[lonn].values, indexing="ij")
    w = np.nan_to_num(da.values).ravel()
    H, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[lat_e, lon_e], weights=w)
    return H


def norm(v):
    v = np.clip(np.nan_to_num(v), 0, None); s = v.sum()
    return v / s if s else v


def skill(cand, truth):
    cn, tn = norm(cand), norm(truth)
    corr = float("nan") if cn.std() == 0 or tn.std() == 0 else float(np.corrcoef(cn, tn)[0, 1])
    return corr, float(np.sqrt(np.mean((cn - tn) ** 2)))


def main():
    files = sf6_flux_files()
    print(f"[icos] SF6 ensemble members: {len(files)}")
    edgar = B.load_edgar_sf6(2020, "TOTALS")
    gains = B.load_gains_sf6(2020)
    ours = {c: xr.open_dataarray(sorted(glob.glob(os.path.join(OUT, f"prior_{s}_*.nc")))[-1])
            for c, s in COUNTRIES.items()}

    results = {c: {k: [] for k in ("OURS", "EDGAR", "GAINS", "ICOS-prior")} for c in COUNTRIES}
    ncells = {}
    for f in files:
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        area = (np.abs(np.gradient(lat)) * 111320)[:, None] * \
               (np.abs(np.gradient(lon)) * 111320 * np.cos(np.radians(lat))[:, None])
        post = ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values * area
        iprior = ds.flux_total_prior.sel(time=str(YEAR), method="nearest").values * area
        edg = regrid_to_icos(edgar, lat_e, lon_e)
        gns = regrid_to_icos(gains, lat_e, lon_e)
        cfrac = ds.country_fraction
        for code, suf in COUNTRIES.items():
            mask = (cfrac.sel(country=code).values >= 0.5)
            if mask.sum() == 0:
                continue
            ncells[code] = int(mask.sum())
            oursg = regrid_to_icos(ours[code], lat_e, lon_e)
            t = post[mask]
            for k, arr in (("OURS", oursg), ("EDGAR", edg), ("GAINS", gns), ("ICOS-prior", iprior)):
                results[code][k].append(skill(arr[mask], t)[0])
        ds.close()

    print(f"\n=== Phase 2e VERDICT — corr vs ICOS 2020 SF6 posterior (ensemble of {len(files)}; mean +/- sd) ===")
    print(f"  {'country':9s} {'OURS(infra)':>14s} {'EDGAR(pop)':>14s} {'GAINS(pop)':>14s} {'ICOS-prior':>14s}  (N cells)")
    verdict = []
    for code in COUNTRIES:
        r = results[code]
        def ms(k): a = np.array(r[k], float); return f"{np.nanmean(a):.3f}+/-{np.nanstd(a):.2f}"
        print(f"  {code:9s} {ms('OURS'):>14s} {ms('EDGAR'):>14s} {ms('GAINS'):>14s} {ms('ICOS-prior'):>14s}  (N={ncells.get(code,'?')})")
        om, em, gm = np.nanmean(r['OURS']), np.nanmean(r['EDGAR']), np.nanmean(r['GAINS'])
        verdict.append(f"{code}: ours {om:.3f} vs EDGAR {em:.3f}/GAINS {gm:.3f} -> beats population: {om > max(em, gm)}")
    print("\n=== VERDICT ===")
    for v in verdict:
        print("  " + v)
    print("\n  Truth: ICOS PARIS 2020 SF6 posterior (recent, fine, well-constrained, multi-system). "
          "Caveat: our OSM is current vs 2020 truth (minor; grid is stable). This supersedes InGOS 2011.")


if __name__ == "__main__":
    main()
