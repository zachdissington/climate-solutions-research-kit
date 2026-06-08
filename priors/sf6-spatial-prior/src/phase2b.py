"""Phase 2b/2c: combine Layer 1 + Layer 2 -> calibrated SF6 prior, and test vs the population proxies.
Region-parameterized:  python src/phase2b.py DE   |   python src/phase2b.py FR

TRUTH-DATA NOTE (verified 2026-06-03): the inversion POSTERIOR is figures-only for every country (no
downloadable gridded array). So we cannot compute a metric "beats the proxy" skill score. We do NOT
fabricate a posterior. Tests:
  - DE (hotspot case): focus-region mass fraction vs the inversion's published ~1/3 figure.
  - FR (grid-distributed best case): no single published hotspot, so the test is DIRECTIONAL —
    population-divergence (corr with EDGAR/GAINS; EDGAR's SF6 grid IS the population proxy, so low corr
    = grid-driven not population-driven, the direction the inversion literature says is right) + spatial
    sanity. Compared against DE to localize where the prior plausibly adds value.
"""
import os
import sys
import csv
import glob

import numpy as np
import xarray as xr

import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
PS_CSV = os.path.join(ROOT, "factors", "point_sources.csv")
GRID_RES = 0.1

REGION_CFG = {
    "DE": {"bbox": (5.8, 15.1, 47.2, 55.1), "national_t": 100.0, "codes": ("DE", "Germany"),
           "focus": (7.0, 10.5, 47.5, 50.0)},   # SW/focus region; inversion truth ~0.33
    "FR": {"bbox": (-5.2, 9.6, 41.3, 51.1), "national_t": 75.0, "codes": ("FR", "France"),
           "focus": None},                       # grid-distributed; no single published hotspot
}


def _coords(da):
    latn = "lat" if "lat" in da.coords else "latitude"
    lonn = "lon" if "lon" in da.coords else "longitude"
    return latn, lonn


def _box_fraction(da, box, bbox):
    latn, lonn = _coords(da)
    de = da.where((da[lonn] >= bbox[0]) & (da[lonn] <= bbox[1]) &
                  (da[latn] >= bbox[2]) & (da[latn] <= bbox[3]))
    lo0, lo1, la0, la1 = box
    foc = de.where((de[lonn] >= lo0) & (de[lonn] <= lo1) & (de[latn] >= la0) & (de[latn] <= la1))
    ds, fs = float(np.nansum(de.values)), float(np.nansum(foc.values))
    return (fs / ds) if ds else float("nan")


def _hist05(da, bbox):
    """Coarse-bin a field to 0.5 deg over bbox -> flat array (for correlation)."""
    latn, lonn = _coords(da)
    la, lo = da[latn].values, da[lonn].values
    LA, LO = np.meshgrid(la, lo, indexing="ij")
    v = np.nan_to_num(da.values)
    m = (LO >= bbox[0]) & (LO <= bbox[1]) & (LA >= bbox[2]) & (LA <= bbox[3])
    latb = np.arange(bbox[2], bbox[3] + 0.5, 0.5)
    lonb = np.arange(bbox[0], bbox[1] + 0.5, 0.5)
    H, _, _ = np.histogram2d(LA[m], LO[m], bins=[latb, lonb], weights=v[m])
    return H.ravel()


def _corr(a, b):
    return float("nan") if a.std() == 0 or b.std() == 0 else float(np.corrcoef(a, b)[0, 1])


def load_layer1(region):
    nc = sorted(glob.glob(os.path.join(OUT, f"layer1_{region.lower()}_*.nc")))[-1]
    return xr.open_dataarray(nc)


def load_point_sources(codes):
    rows = []
    with open(PS_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader((ln for ln in fh if not ln.startswith("#"))):
            if r["country"] in codes and r["lat"] and r["lon"]:
                rows.append((float(r["lat"]), float(r["lon"]),
                             float(r["sf6_tonnes_yr"]) if r["sf6_tonnes_yr"] else 0.0))
    return rows


def main(region="DE"):
    cfg = REGION_CFG[region]
    bbox, national_t = cfg["bbox"], cfg["national_t"]
    l1 = load_layer1(region)
    lats, lons = l1["lat"].values, l1["lon"].values

    pts = load_point_sources(cfg["codes"])
    l2 = np.zeros_like(l1.values)
    placed = 0
    for lat, lon, t in pts:
        i = int(round((lat - lats[0]) / GRID_RES)); j = int(round((lon - lons[0]) / GRID_RES))
        if 0 <= i < len(lats) and 0 <= j < len(lons):
            l2[i, j] += t; placed += 1
    l2_sum = l2.sum()

    l1n = l1.values / l1.values.sum() if l1.values.sum() else l1.values
    combined = l2 + l1n * max(national_t - l2_sum, 0.0)
    ours = xr.DataArray(combined, coords={"lat": lats, "lon": lons}, dims=["lat", "lon"])

    edgar = B.load_edgar_sf6(2020, "TOTALS")
    gains = B.load_gains_sf6(2020)

    ov, ev, gv = _hist05(ours, bbox), _hist05(edgar, bbox), _hist05(gains, bbox)
    c_oe, c_og, c_eg = _corr(ov, ev), _corr(ov, gv), _corr(ev, gv)

    print(f"\n=== {region} VALIDATION ===")
    v1 = "PASS" if abs(combined.sum() - national_t) < 1.0 else "FAIL"
    print(f"  [{v1}] V1 conservation: combined {combined.sum():.1f} t == target {national_t} t")
    print(f"  [{'PASS' if placed == len(pts) else 'WARN'}] V2 placement: {placed}/{len(pts)} point sources "
          f"gridded (L2 sum {l2_sum:.2f} t = {100*l2_sum/national_t:.1f}% of national)")
    print(f"  [{'PASS' if np.isfinite(c_oe) else 'FAIL'}] V4 integrity: {len(ov)} common 0.5deg cells")

    if cfg["focus"]:
        of = _box_fraction(ours, cfg["focus"], bbox)
        ef = _box_fraction(edgar, cfg["focus"], bbox)
        gf = _box_fraction(gains, cfg["focus"], bbox)
        print(f"\n=== {region} TEST A: focus-region fraction vs inversion ~0.33 ===")
        for nm, f in [("OURS", of), ("EDGAR", ef), ("GAINS", gf)]:
            print(f"  {nm:8s} {f:.3f}  (|dev| {abs(f-0.33):.3f})")

    print(f"\n=== {region} divergence from population proxies (lower = more grid-driven) ===")
    print(f"  corr(ours,EDGAR)={c_oe:.2f}  corr(ours,GAINS)={c_og:.2f}  [corr(EDGAR,GAINS)={c_eg:.2f}]")
    print(f"  L2 share of national: {100*l2_sum/national_t:.1f}%  (low => grid-distributed, not hotspot)")

    from datetime import date
    ours.to_netcdf(os.path.join(OUT, f"prior_{region.lower()}_{date.today().isoformat()}.nc"))
    return dict(region=region, c_oe=c_oe, c_og=c_og, c_eg=c_eg, l2_share=l2_sum / national_t)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "DE")
