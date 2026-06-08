"""Diagnostic to interpret the HFC-23 kill-test negative: is the plant prior genuinely wrong, or is
the European HFC-23 posterior too weakly constrained to test (EDGAR wins by smoothness artifact)?
Also runs the deferred premise check: is EDGAR HFC-23 Europe a population proxy or already plant-located?
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

# 1. Is the posterior CONSTRAINED (moved off its FLAT prior)?
print("=== posterior vs FLAT prior, 2020, per ensemble member ===")
for f in files:
    ds = xr.open_dataset(f)
    post = ds.flux_total_posterior.sel(time="2020", method="nearest").values
    prior = ds.flux_total_prior.sel(time="2020", method="nearest").values
    p = np.nan_to_num(post).ravel(); q = np.nan_to_num(prior).ravel()
    c = np.corrcoef(p, q)[0, 1] if p.std() and q.std() else float("nan")
    ratio = np.nansum(np.abs(post - prior)) / (np.nansum(np.abs(prior)) + 1e-30)
    prior_cv = q.std() / (q.mean() + 1e-30)
    name = os.path.basename(f).split("_EUROPE")[0]
    print(f"  {name:18s} corr(post,prior)={c:.3f}  L1(post-prior)/L1(prior)={ratio:.2f}  prior_CV={prior_cv:.3f} (flat if ~0)")
    ds.close()

# 2. Is EDGAR HFC-23 Europe SMOOTH (population) or SPIKY (plant)?
print("\n=== EDGAR HFC-23 2020 spatial nature over Europe ===")
e = B.load_edgar("HFC-23", 2020, "TOTALS")
latn = "lat" if "lat" in e.coords else "latitude"
lonn = "lon" if "lon" in e.coords else "longitude"
asc = e[latn].values[0] < e[latn].values[-1]
sub = e.sel({latn: slice(34, 72) if asc else slice(72, 34), lonn: slice(-25, 45)})
v = np.nan_to_num(sub.values); nz = v.ravel()[v.ravel() > 0]
print(f"  Europe cells>0: {nz.size}; top-10 cells = {np.sort(nz)[-10:].sum()/nz.sum()*100:.1f}% of European total")
print(f"  max/mean cell = {nz.max()/nz.mean():.0f}x  (smooth/population ~ low 10s; plant-spiky ~ 100s-1000s)")
la = sub[latn].values; lo = sub[lonn].values
idx = np.dstack(np.unravel_index(np.argsort(v.ravel())[-6:], v.shape))[0]
print("  EDGAR top-6 European HFC-23 cells (lat,lon,val):")
for i, j in idx[::-1]:
    print(f"    ({la[i]:.2f},{lo[j]:.2f})  {v[i, j]:.3f}")

# 3. Where does the POSTERIOR put mass vs the plants?
print("\n=== posterior (ensemble-mean 2020) top-6 European cells vs plant coords ===")
acc = None
for f in files:
    ds = xr.open_dataset(f)
    p = np.nan_to_num(ds.flux_total_posterior.sel(time="2020", method="nearest").values)
    acc = p if acc is None else acc + p
    plat, plon = ds.latitude.values, ds.longitude.values
    ds.close()
acc /= len(files)
idx = np.dstack(np.unravel_index(np.argsort(acc.ravel())[-6:], acc.shape))[0]
print("  posterior top-6 cells (lat,lon,val):")
for i, j in idx[::-1]:
    print(f"    ({plat[i]:.2f},{plon[j]:.2f})  {acc[i, j]:.2e}")
plants = [("Dordrecht", 51.82, 4.73), ("PierreBenite", 45.71, 4.83), ("Spinetta", 44.89, 8.68),
          ("AGC-UK", 53.88, -3.00), ("Gendorf", 48.16, 12.66)]
print("  plant cells (lat,lon):")
for n, la_, lo_ in plants:
    print(f"    {n:14s} ({la_:.2f},{lo_:.2f})")
