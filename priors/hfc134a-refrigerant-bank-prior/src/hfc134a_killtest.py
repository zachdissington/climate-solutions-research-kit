"""HFC-134a kill-test: does a refrigerant-bank prior (population x CDD) beat EDGAR (population) and a
population-only prior at predicting where the HFC-134a inversion posterior puts emissions?

Truth = ICOS PARIS HFC-134a posterior, 2020, Europe, 6-member ensemble (RHIME/InTEM/ELRIS x
NAME/FLEXPART). CAVEAT: this inversion used an EDGAR/population-weighted PRIOR (filenames carry
'EDGAR'), so the posterior is partly biased toward population. The test is therefore CONSERVATIVE:
a cooling-demand prior that still beats population here is a strong signal; a loss is partly expected.

Candidates:
  - BANK  = our population x CDD refrigerant-bank prior
  - POP   = population-only prior (isolates whether CDD adds signal beyond population)
  - EDGAR = EDGAR HFC-134a TOTALS (the inversion's own population-weighted baseline)
  - PRIOR = the inversion's own flux_total_prior (reference; ~EDGAR, shows the population floor)

Spatial correlation per country (and pooled across countries), normalized per region, masked by
country_fraction. Adapted verbatim from pfc-aluminium-prior/src/cf4_killtest.py
(edges/regrid/norm/corr/country_labels reused).

Run:  python src/hfc134a_killtest.py
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
# Score the most-populated / highest-demand European countries individually.
COUNTRIES = ["FRA", "ESP", "DEU", "ITA", "GBR", "NLD", "BEL", "POL", "GRC", "PRT", "CHE", "AUT", "ROU", "SWE", "NOR"]
MIN_CELLS = 8


def flux_files():
    return sorted(glob.glob(os.path.join(ICOS, "*hfc134a_yearly_flux.nc")))


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
    print(f"[hfc134a] ICOS posterior ensemble members: {len(files)}")
    edgar_tot = B.load_edgar("HFC-134a", YEAR, "TOTALS")
    bank = xr.open_dataarray(os.path.join(OUT, "prior_hfc134a_europe_bank.nc"))
    pop = xr.open_dataarray(os.path.join(OUT, "prior_hfc134a_europe_population.nc"))

    cand_static = [("BANK", bank), ("POP", pop), ("EDGAR", edgar_tot)]
    keys = [k for k, _ in cand_static] + ["PRIOR"]  # PRIOR is per-file (inversion's own prior)

    regions = COUNTRIES + ["POOL"]
    res = {r: {k: [] for k in keys} for r in regions}
    ncells = {}

    for f in files:
        ds = xr.open_dataset(f)
        lat, lon = ds.latitude.values, ds.longitude.values
        lat_e, lon_e = edges(lat), edges(lon)
        # Exact-year selection. sel(time="2020", method="nearest") silently returned the
        # 2019 field for 4 of 6 members (mid-year stamps are equidistant from 2020-01-01 and
        # the tie resolves to the earlier index) — found in the 2026-06-12 audit; the v1
        # deposit's numbers were computed from that 4x2019 + 2x2020 mixture.
        post_sel = ds.flux_total_posterior.sel(time=slice(f"{YEAR}-01-01", f"{YEAR}-12-31"))
        assert post_sel.time.size == 1, (f, post_sel.time.values)
        post = post_sel.isel(time=0).values
        prior_sel = ds.flux_total_prior.sel(time=slice(f"{YEAR}-01-01", f"{YEAR}-12-31"))
        prior_da = xr.DataArray(
            np.nan_to_num(prior_sel.isel(time=0).values),
            dims=("latitude", "longitude"), coords={"latitude": lat, "longitude": lon})
        cfrac = ds.country_fraction
        labels = country_labels(ds)
        rg = {k: regrid(da, lat_e, lon_e) for k, da in cand_static}
        rg["PRIOR"] = prior_da.values  # already on posterior grid

        pool_mask = np.zeros_like(post, dtype=bool)
        for code in COUNTRIES:
            if code not in labels:
                continue
            ci = labels.index(code)
            mask = cfrac.isel(country=ci).values >= 0.5
            if mask.sum() < MIN_CELLS:
                continue
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
    hdr = "  ".join(f"{k:>8s}" for k in keys)
    print(f"\n=== HFC-134a kill-test — spatial corr vs ICOS 2020 posterior (ensemble mean +/- sd) ===")
    print(f"  {'region':8s} {hdr}   (N cells)")

    def ms(a):
        a = np.array(a, float)
        return f"{np.nanmean(a):.3f}±{np.nanstd(a):.2f}"

    verdict = []
    for r in regions:
        if not any(res[r][k] for k in keys):
            continue
        line = "  ".join(f"{ms(res[r][k]):>8s}" for k in keys)
        print(f"  {r:8s} {line}   (N={ncells.get(r,'?')})")
        bank_m = np.nanmean(res[r]["BANK"]); pop_m = np.nanmean(res[r]["POP"])
        edgar_m = np.nanmean(res[r]["EDGAR"])
        beats = bank_m > max(pop_m, edgar_m)
        verdict.append(f"{r}: BANK {bank_m:.3f} vs POP {pop_m:.3f} / EDGAR {edgar_m:.3f} -> beats both: {beats}")

    print("\n=== VERDICT (bank prior beats population AND EDGAR?) ===")
    for v in verdict:
        print("  " + v)
    wins = sum("True" in v for v in verdict)
    print(f"\n  {wins}/{len(verdict)} regions: bank prior beats both population references.")
    print(f"  Truth = ICOS HFC-134a 2020, EDGAR-prior (CONSERVATIVE test), {len(files)}-member ensemble, Europe.")


if __name__ == "__main__":
    main()
