"""EDGAR NF3 baseline loader (the population/built-up proxy the fab prior must beat).
Reuses the cached EDGAR v8.0 F-gas bundle. NF3 single sector PRU_SOL == TOTALS.
Run:  python src/benchmarks.py
"""
import os
import zipfile

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDGAR_ZIP = os.path.abspath(os.path.join(ROOT, "..", "sf6-spatial-prior", "data", "benchmarks",
                                         "EDGAR_f-gases_emi_nc.zip"))
EXTRACT = os.path.join(ROOT, "data", "benchmarks", "edgar_extracted")
MEMBER = "f-gases_emi_nc/{sub}/{sector}/emi_nc/v8.0_FT2022_GHG_{sub}_{year}_{sector}_emi.nc"
SUB = "NF3"


def edgar_sectors(substance=SUB):
    with zipfile.ZipFile(EDGAR_ZIP) as z:
        names = z.namelist()
    pref = f"f-gases_emi_nc/{substance}/"
    return sorted({n[len(pref):].split("/")[0] for n in names
                   if n.startswith(pref) and n.endswith("_emi.nc")})


def load_edgar(substance=SUB, year=2020, sector="TOTALS"):
    os.makedirs(EXTRACT, exist_ok=True)
    member = MEMBER.format(sub=substance, year=year, sector=sector)
    local = os.path.join(EXTRACT, os.path.basename(member))
    if not os.path.exists(local):
        with zipfile.ZipFile(EDGAR_ZIP) as z:
            with z.open(member) as src, open(local, "wb") as dst:
                dst.write(src.read())
    ds = xr.open_dataset(local)
    var = next((v for v in ds.data_vars if v.lower() not in ("spatial_ref", "crs")), list(ds.data_vars)[0])
    return ds[var]


def global_total(da):
    return float(np.nansum(da.values))


if __name__ == "__main__":
    print(f"[edgar] zip exists={os.path.exists(EDGAR_ZIP)}; {SUB} sectors: {edgar_sectors(SUB)}")
    for sector in ["TOTALS"]:
        da = load_edgar(SUB, 2020, sector)
        print(f"[edgar] {SUB} {sector} 2020: global {global_total(da):,.1f} t/yr dims={dict(da.sizes)}")
