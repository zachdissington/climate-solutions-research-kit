"""EDGAR HFC-134a baseline loader (the population/built-up proxy the bank prior must beat).

Reuses the EDGAR v8.0 F-gases bundle already cached for the SF6/CF4 builds (~1 GB) — HFC-134a is a
separable substance folder inside it (sectors: TOTALS, PRU_SOL). Cloned from
pfc-aluminium-prior/src/benchmarks.py: load_edgar(substance, year, sector).

Run:  python src/benchmarks.py
"""
import os
import zipfile

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Reuse the SF6 build's cached EDGAR bundle (same file, HFC-134a inside).
EDGAR_ZIP = os.path.abspath(os.path.join(ROOT, "..", "sf6-spatial-prior", "data", "benchmarks",
                                         "EDGAR_f-gases_emi_nc.zip"))
EXTRACT = os.path.join(ROOT, "data", "benchmarks", "edgar_extracted")
MEMBER = "f-gases_emi_nc/{sub}/{sector}/emi_nc/v8.0_FT2022_GHG_{sub}_{year}_{sector}_emi.nc"


def edgar_sectors(substance="HFC-134a"):
    with zipfile.ZipFile(EDGAR_ZIP) as z:
        names = z.namelist()
    pref = f"f-gases_emi_nc/{substance}/"
    secs = sorted({n[len(pref):].split("/")[0] for n in names
                   if n.startswith(pref) and n.endswith("_emi.nc")})
    return secs


def load_edgar(substance="HFC-134a", year=2020, sector="TOTALS"):
    """Return EDGAR substance/sector/year as a DataArray (tonnes substance / cell / yr)."""
    os.makedirs(EXTRACT, exist_ok=True)
    member = MEMBER.format(sub=substance, year=year, sector=sector)
    local = os.path.join(EXTRACT, os.path.basename(member))
    if not os.path.exists(local):
        with zipfile.ZipFile(EDGAR_ZIP) as z:
            with z.open(member) as src, open(local, "wb") as dst:
                dst.write(src.read())
    ds = xr.open_dataset(local)
    var = next((v for v in ds.data_vars if v.lower() not in ("spatial_ref", "crs")),
               list(ds.data_vars)[0])
    return ds[var]


def global_total(da):
    return float(np.nansum(da.values))


if __name__ == "__main__":
    print(f"[edgar] zip: {EDGAR_ZIP}  exists={os.path.exists(EDGAR_ZIP)}")
    secs = edgar_sectors("HFC-134a")
    print(f"[edgar] HFC-134a sectors: {secs}")
    for sector in ("TOTALS", "PRU_SOL"):
        if sector not in secs:
            print(f"[edgar] sector {sector} absent; skipping")
            continue
        da = load_edgar("HFC-134a", 2020, sector)
        gt = global_total(da)
        print(f"[edgar] HFC-134a {sector} 2020: global {gt:,.0f} t/yr (~{gt/1000:.2f} kt/yr) dims={dict(da.sizes)}")
