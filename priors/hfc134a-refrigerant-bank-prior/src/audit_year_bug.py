"""Audit (2026-06-12): independently verify the year-selection bug and quantify it.

1. Print each member's time axis and what sel(time="2020", method="nearest") returns.
2. Recompute the pooled + per-country correlations under (a) the shipped selection and
   (b) exact-2020 selection, and diff against the published numbers.
3. Confirm the regenerated outputs/*.nc match the shipped (deposited) copies.
"""
import glob
import os
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")

from hfc134a_killtest import COUNTRIES, MIN_CELLS, YEAR, corr, country_labels, edges, regrid
import benchmarks as B

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
ICOS = os.path.join(ROOT, "data", "posteriors", "icos")


def main():
    # --- 3. output regeneration check ---
    for new, old in (("prior_hfc134a_europe_bank.nc", "_shipped_bank.nc"),
                     ("prior_hfc134a_europe_population.nc", "_shipped_population.nc"),
                     ("cdd_europe.nc", "_shipped_cdd.nc")):
        a = xr.open_dataarray(os.path.join(OUT, new)).values
        b = xr.open_dataarray(os.path.join(OUT, old)).values
        same = np.array_equal(np.nan_to_num(a), np.nan_to_num(b))
        print(f"[regen] {new}: identical to shipped = {same}"
              f" (max|diff| {np.nanmax(np.abs(np.nan_to_num(a)-np.nan_to_num(b))):.3g})")

    files = sorted(glob.glob(os.path.join(ICOS, "*hfc134a_yearly_flux.nc")))
    print(f"\n[time-axis audit] {len(files)} members")
    for f in files:
        ds = xr.open_dataset(f)
        times = [str(t)[:10] for t in ds.time.values]
        picked = str(ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").time.values)[:10]
        in2020 = [t for t in times if t.startswith("2020")]
        print(f"  {os.path.basename(f).split('_EUROPE')[0]:16s} picked={picked}"
              f"  (2020 stamp present: {in2020[0] if in2020 else 'NONE'})"
              f"  axis[0..3]={times[:3]}...")
        ds.close()

    # --- 2. shipped-selection vs exact-2020 correlations ---
    edgar_tot = B.load_edgar("HFC-134a", YEAR, "TOTALS")
    bank = xr.open_dataarray(os.path.join(OUT, "prior_hfc134a_europe_bank.nc"))
    pop = xr.open_dataarray(os.path.join(OUT, "prior_hfc134a_europe_population.nc"))

    for mode in ("shipped-nearest", "exact-2020"):
        res = {r: {k: [] for k in ("BANK", "POP", "EDGAR")} for r in COUNTRIES + ["POOL"]}
        for f in files:
            ds = xr.open_dataset(f)
            lat, lon = ds.latitude.values, ds.longitude.values
            lat_e, lon_e = edges(lat), edges(lon)
            if mode == "shipped-nearest":
                post = ds.flux_total_posterior.sel(time=str(YEAR), method="nearest").values
            else:
                sel = ds.flux_total_posterior.sel(time=slice("2020-01-01", "2020-12-31"))
                assert sel.time.size == 1, (f, sel.time.values)
                post = sel.isel(time=0).values
            labels = country_labels(ds)
            rg = {"BANK": regrid(bank, lat_e, lon_e), "POP": regrid(pop, lat_e, lon_e),
                  "EDGAR": regrid(edgar_tot, lat_e, lon_e)}
            pool = np.zeros_like(post, bool)
            for code in COUNTRIES:
                if code not in labels:
                    continue
                m = ds.country_fraction.isel(country=labels.index(code)).values >= 0.5
                if m.sum() < MIN_CELLS:
                    continue
                pool |= m
                for k in rg:
                    res[code][k].append(corr(rg[k][m], post[m]))
            for k in rg:
                res["POOL"][k].append(corr(rg[k][pool], post[pool]))
            ds.close()
        print(f"\n[{mode}]")
        for r in COUNTRIES + ["POOL"]:
            if not res[r]["BANK"]:
                continue
            vals = "  ".join(f"{k} {np.nanmean(res[r][k]):.3f}" for k in ("BANK", "POP", "EDGAR"))
            print(f"  {r:5s} {vals}")


if __name__ == "__main__":
    main()
