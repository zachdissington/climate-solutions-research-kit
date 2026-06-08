"""Decisive CF4 test: does the smelter prior beat EDGAR vs the Puschel global posterior (China-resolved)?

Truth = Puschel et al. 2025 global CF4 posterior (emis_post, 1deg, 2006-2023; deposit phaidra.751,
CC-BY-NC). Its prior was EDGAR F-gases v2024, so a plain "ours vs EDGAR vs posterior" test is partly
circular (EDGAR is the truth's own prior). Two metrics:
  (A) spatial correlation ours/EDGAR vs posterior, per region (China is the point);
  (B) circularity-robust: correlation of ours vs the inversion's CORRECTION to EDGAR (post_norm -
      edgar_norm) -- does the smelter prior explain where the observations pulled the posterior away
      from EDGAR? Immune to the shared-prior confound.
Run:  python src/puschel_killtest.py
"""
import os
import glob

import numpy as np
import xarray as xr

import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
POST = os.path.join(ROOT, "data", "posteriors", "puschel", "CF4")
YEARS = list(range(2018, 2024))   # recent, better-constrained; 2020 also reported alone

# region bboxes: lon0, lon1, lat0, lat1
REGIONS = {
    "CHINA":   (73, 135, 18, 54),
    "INDIA":   (68, 90, 8, 30),
    "GULF":    (44, 60, 22, 31),
    "CANADA":  (-140, -52, 42, 62),
    "EUROPE":  (-25, 45, 35, 72),
    "RUSSIA":  (28, 180, 48, 78),
    "GLOBAL":  (-180, 180, -60, 84),
}

LON = np.arange(-180, 180, 1.0)
LAT = np.arange(-90, 90, 1.0)
LON_E = np.arange(-180.5, 180.5, 1.0)
LAT_E = np.arange(-90.5, 90.5, 1.0)


def regrid_to_1deg(da):
    latn = "lat" if "lat" in da.coords else "latitude"
    lonn = "lon" if "lon" in da.coords else "longitude"
    LA, LO = np.meshgrid(da[latn].values, da[lonn].values, indexing="ij")
    w = np.nan_to_num(da.values).ravel()
    H, _, _ = np.histogram2d(LA.ravel(), LO.ravel(), bins=[LAT_E, LON_E], weights=w)
    return H  # (180, 360) aligned to LAT, LON


def load_post(year):
    ds = xr.open_dataset(os.path.join(POST, f"CF4_constrained_{year}.nc"))
    a = np.asarray(ds.emis_post.squeeze().values, float)
    ds.close()
    return a  # (180,360), lat -90..89, lon -180..179


def norm(v):
    v = np.clip(np.nan_to_num(v), 0, None); s = v.sum()
    return v / s if s else v


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def region_mask(lo0, lo1, la0, la1, landref):
    LO, LA = np.meshgrid(LON, LAT)
    box = (LO >= lo0) & (LO <= lo1) & (LA >= la0) & (LA <= la1)
    land = np.isfinite(landref) & (landref != 0)   # Puschel sets ocean to 0
    return box & land


def main():
    edgar = regrid_to_1deg(B.load_edgar("CF4", 2020, "TOTALS"))
    ours_cap = regrid_to_1deg(xr.open_dataarray(os.path.join(OUT, "prior_cf4_global_capacity.nc")))
    ours_pres = regrid_to_1deg(xr.open_dataarray(os.path.join(OUT, "prior_cf4_global_presence.nc")))

    rows = {r: {"OURS-cap": [], "OURS-pres": [], "EDGAR": [], "CORR-cap": []} for r in REGIONS}
    ncells = {}
    for y in YEARS:
        post = load_post(y)
        for r, (lo0, lo1, la0, la1) in REGIONS.items():
            m = region_mask(lo0, lo1, la0, la1, post)
            if m.sum() < 8:
                continue
            ncells[r] = int(m.sum())
            t = post[m]
            rows[r]["OURS-cap"].append(corr(norm(ours_cap[m]), norm(t)))
            rows[r]["OURS-pres"].append(corr(norm(ours_pres[m]), norm(t)))
            rows[r]["EDGAR"].append(corr(norm(edgar[m]), norm(t)))
            # circularity-robust: ours vs (posterior - EDGAR) correction, normalized in-region
            corr_field = norm(t) - norm(edgar[m])
            rows[r]["CORR-cap"].append(corr(norm(ours_cap[m]), corr_field))

    def ms(a):
        a = np.array(a, float)
        return f"{np.nanmean(a):.3f}" + (f"±{np.nanstd(a):.2f}" if a.size > 1 else "")

    print(f"\n=== CF4 decisive test vs Puschel posterior (years {YEARS[0]}-{YEARS[-1]} mean±sd) ===")
    print(f"  {'region':8s} {'OURS-cap':>11s} {'OURS-pres':>11s} {'EDGAR':>9s} {'ours-vs-CORRECTION':>20s}  (N)")
    verdict = []
    for r in REGIONS:
        if not rows[r]["EDGAR"]:
            continue
        oc, op, e = ms(rows[r]["OURS-cap"]), ms(rows[r]["OURS-pres"]), ms(rows[r]["EDGAR"])
        cc = ms(rows[r]["CORR-cap"])
        print(f"  {r:8s} {oc:>11s} {op:>11s} {e:>9s} {cc:>20s}  (N={ncells.get(r,'?')})")
        om = max(np.nanmean(rows[r]["OURS-cap"]), np.nanmean(rows[r]["OURS-pres"]))
        em = np.nanmean(rows[r]["EDGAR"]); corrm = np.nanmean(rows[r]["CORR-cap"])
        verdict.append((r, om, em, corrm))

    print("\n=== VERDICT ===")
    for r, om, em, corrm in verdict:
        print(f"  {r:8s} ours {om:.3f} vs EDGAR {em:.3f} -> beats: {om>em};  "
              f"explains EDGAR-correction: {corrm:.3f} ({'yes' if corrm>0.05 else 'weak/no'})")
    ch = next((v for v in verdict if v[0] == "CHINA"), None)
    if ch:
        print(f"\n  HEADLINE (China): smelter prior {'BEATS' if ch[1]>ch[2] else 'does NOT beat'} EDGAR; "
              f"correction-direction {ch[3]:+.3f}. Truth=Puschel CF4 (EDGAR-prior; preprint).")


if __name__ == "__main__":
    main()
