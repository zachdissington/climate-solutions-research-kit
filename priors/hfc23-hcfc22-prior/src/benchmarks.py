"""EDGAR HFC-23 baseline loader (the population proxy the plant prior must beat).

Reuses the EDGAR v8.0 F-gases bundle already cached for the SF6/CF4 builds (HFC-23 is a separable
substance folder inside it). Generalized from pfc-aluminium-prior/src/benchmarks.py.
Run:  python src/benchmarks.py
"""
import os
import zipfile

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Reuse the SF6 build's cached EDGAR F-gas bundle (HFC-23 inside).
EDGAR_ZIP = os.path.abspath(os.path.join(ROOT, "..", "sf6-spatial-prior", "data", "benchmarks",
                                         "EDGAR_f-gases_emi_nc.zip"))
EXTRACT = os.path.join(ROOT, "data", "benchmarks", "edgar_extracted")
MEMBER = "f-gases_emi_nc/{sub}/{sector}/emi_nc/v8.0_FT2022_GHG_{sub}_{year}_{sector}_emi.nc"
SUB = "HFC-23"


def edgar_sectors(substance=SUB):
    with zipfile.ZipFile(EDGAR_ZIP) as z:
        names = z.namelist()
    pref = f"f-gases_emi_nc/{substance}/"
    secs = sorted({n[len(pref):].split("/")[0] for n in names
                   if n.startswith(pref) and n.endswith("_emi.nc")})
    return secs


def load_edgar(substance=SUB, year=2020, sector="TOTALS"):
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
    secs = edgar_sectors(SUB)
    print(f"[edgar] {SUB} sectors: {secs}")
    for sector in (["TOTALS"] + [s for s in secs if s != "TOTALS"]):
        if sector not in secs:
            continue
        da = load_edgar(SUB, 2020, sector)
        gt = global_total(da)
        print(f"[edgar] {SUB} {sector} 2020: global {gt:,.1f} t/yr (~{gt/1000:.3f} kt/yr) dims={dict(da.sizes)}")
