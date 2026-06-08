"""Phase 2d: the REAL metric test. Score ours / EDGAR / GAINS (and the InGOS own prior) against the
InGOS 2011 SF6 POSTERIOR, on the InGOS grid, for France and Germany. First non-directional verdict.

Truth = InGOS posterior_flux (kg/yr/m2) -> per-cell total = flux * cell_area. Primary system = EMPA2
(405 variable cells, carries prior_flux + posterior_flux); NILU regular 0.5deg grid = ensemble check.
All fields normalized per-region (sum=1) so the test is purely SPATIAL ALLOCATION.

CAVEAT (stated, not hidden): truth is 2011; our OSM is current, EDGAR/GAINS are 2020. Grid topology +
population change slowly, so spatial comparison is meaningful, but the year gap is a real limitation.

Run:  python src/metric_test.py
"""
import os
import re
import glob
import zipfile

import numpy as np
import xarray as xr

import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
ZIP_FP = os.path.join(ROOT, "data", "posteriors", "ingos_halocarbon_inversions.zip")

REGIONS = {"DE": (5.8, 15.1, 47.2, 55.1), "FR": (-5.2, 9.6, 41.3, 51.1)}
EMPA2 = "results_empa2/H13v4/GRID_MEAN_INGOS_EMPA2_ASIM_H13v4_FLEXPART.nc"


def cell_area_m2(lat, dlon, dlat):
    m_per_deg = 111320.0
    return (dlat * m_per_deg) * (dlon * m_per_deg * np.cos(np.radians(lat)))


def load_ingos_empa2():
    if not os.path.exists(os.path.join(ROOT, "data", "posteriors", EMPA2)):
        zipfile.ZipFile(ZIP_FP).extract(EMPA2, os.path.join(ROOT, "data", "posteriors"))
    return xr.open_dataset(os.path.join(ROOT, "data", "posteriors", EMPA2))


def candidate_sum_in_box(da, lo0, lo1, la0, la1):
    """Sum a per-cell-total candidate grid (lat,lon) over a lon/lat box (cell centers inside)."""
    latn = "lat" if "lat" in da.coords else "latitude"
    lonn = "lon" if "lon" in da.coords else "longitude"
    sub = da.where((da[lonn] >= lo0) & (da[lonn] < lo1) & (da[latn] >= la0) & (da[latn] < la1))
    return float(np.nansum(sub.values))


def norm(v):
    v = np.clip(np.nan_to_num(v), 0, None)
    s = v.sum()
    return v / s if s else v


def skill(cand, truth):
    cn, tn = norm(cand), norm(truth)
    if cn.std() == 0 or tn.std() == 0:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(cn, tn)[0, 1])
    rmse = float(np.sqrt(np.mean((cn - tn) ** 2)))
    return corr, rmse


def main():
    ds = load_ingos_empa2()
    lon, lat = ds.lon.values, ds.lat.values
    dlon, dlat = ds.dlon.values, ds.dlat.values
    area = cell_area_m2(lat, dlon, dlat)
    post = np.clip(ds.posterior_flux.values, 0, None) * area      # truth, per-cell total
    iprior = np.clip(ds.prior_flux.values, 0, None) * area        # InGOS own prior

    edgar = B.load_edgar_sf6(2020, "TOTALS")
    gains = B.load_gains_sf6(2020)

    lines = []
    for region, (lo0, lo1, la0, la1) in REGIONS.items():
        # InGOS cells whose CENTER is in this country's bbox
        idx = np.where((lon >= lo0) & (lon <= lo1) & (lat >= la0) & (lat <= la1))[0]
        if idx.size == 0:
            print(f"[{region}] no InGOS cells in bbox"); continue
        ours_da = xr.open_dataarray(sorted(glob.glob(os.path.join(OUT, f"prior_{region.lower()}_*.nc")))[-1])

        truth_v = post[idx]
        cand = {"OURS (infra)": [], "EDGAR (pop)": [], "GAINS (pop+night)": [], "InGOS-prior": iprior[idx]}
        for k in idx:
            bl0, bl1 = lon[k] - dlon[k] / 2, lon[k] + dlon[k] / 2
            ba0, ba1 = lat[k] - dlat[k] / 2, lat[k] + dlat[k] / 2
            cand["OURS (infra)"].append(candidate_sum_in_box(ours_da, bl0, bl1, ba0, ba1))
            cand["EDGAR (pop)"].append(candidate_sum_in_box(edgar, bl0, bl1, ba0, ba1))
            cand["GAINS (pop+night)"].append(candidate_sum_in_box(gains, bl0, bl1, ba0, ba1))
        cand = {k: np.asarray(v, float) for k, v in cand.items()}

        print(f"\n=== {region}: skill vs InGOS-2011 posterior  (N={idx.size} InGOS cells) ===")
        print(f"  {'candidate':20s} {'corr':>7s} {'RMSE':>9s}")
        rows = {}
        for name, v in cand.items():
            c, r = skill(v, truth_v)
            rows[name] = (c, r)
            print(f"  {name:20s} {c:7.3f} {r:9.4f}")
        winner = max((k for k in rows if k != "InGOS-prior"), key=lambda k: (rows[k][0] if np.isfinite(rows[k][0]) else -9))
        beats_pop = rows["OURS (infra)"][0] > max(rows["EDGAR (pop)"][0], rows["GAINS (pop+night)"][0])
        lines.append(f"{region}: ours corr={rows['OURS (infra)'][0]:.3f} vs EDGAR {rows['EDGAR (pop)'][0]:.3f} / "
                     f"GAINS {rows['GAINS (pop+night)'][0]:.3f} (InGOS-prior {rows['InGOS-prior'][0]:.3f}); "
                     f"beats population: {beats_pop}; best={winner}")

    print("\n=== VERDICT (corr vs 2011 posterior; higher=better; spatial-allocation only) ===")
    for ln in lines:
        print("  " + ln)
    print("\n  Caveats: truth=2011 vs our current/2020 priors; coarse variable grid; EMPA2 only (NILU "
          "cross-check pending); small N per country. A win here justifies recent-year validation via outreach.")


if __name__ == "__main__":
    main()
