"""EDGAR CF4 baseline loader (the population/built-up proxy the smelter prior must beat).

Uses the EDGAR v8.0_FT2022_GHG F-gases bundle (EDGAR v8.0 for short; the embedded product/version
string is `v8.0_FT2022_GHG`). CF4 is a separable substance folder inside the bundle. Generalized from
sf6-spatial-prior/src/benchmarks.py: load_edgar(substance, year, sector). Run:  python src/benchmarks.py

INPUT RETRIEVAL — the EDGAR v8.0 F-gases bundle (~1 GB) is not committed (gitignored, large). The loader
resolves it in this order:
  1. EDGAR_ZIP env var, if set (absolute path to the F-gases `*_emi_nc.zip`).
  2. This artifact's own cache: data/benchmarks/EDGAR_f-gases_emi_nc.zip  (DEFAULT_EDGAR_ZIP).
  3. The SF6 build's cache (fast path, same file): ../sf6-spatial-prior/data/benchmarks/EDGAR_f-gases_emi_nc.zip.
The first existing path wins. If none exist, load_edgar() raises a FileNotFoundError that prints the
retrieval steps below.

Manual retrieval (EDGAR v8.0 F-gases, CC-BY-4.0; Crippa et al., ESSD 16:2811, 2024):
  - DOI: 10.2905/b54d8149-2864-4fb9-96b9-5fd3a020c224
    (https://data.jrc.ec.europa.eu/dataset/b54d8149-2864-4fb9-96b9-5fd3a020c224)
  - Or the EDGAR portal: https://edgar.jrc.ec.europa.eu/dataset_ghg80  -> "F-gases" -> the gridded
    NetCDF (emi_nc) bundle for v8.0_FT2022_GHG.
  - Save the downloaded archive (named like `EDGAR_f-gases_emi_nc.zip`) to one of the resolved paths
    above — simplest is data/benchmarks/EDGAR_f-gases_emi_nc.zip under this prior root.
"""
import os
import zipfile

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDGAR_DOI = "10.2905/b54d8149-2864-4fb9-96b9-5fd3a020c224"  # EDGAR v8.0 F-gases (Crippa et al. 2024)
# This artifact's own cache (preferred home for a fresh download).
DEFAULT_EDGAR_ZIP = os.path.join(ROOT, "data", "benchmarks", "EDGAR_f-gases_emi_nc.zip")
# The SF6 build's cached bundle (same file, CF4 inside) — fast path on Zach's machine.
SF6_EDGAR_ZIP = os.path.abspath(os.path.join(ROOT, "..", "sf6-spatial-prior", "data", "benchmarks",
                                             "EDGAR_f-gases_emi_nc.zip"))


def _resolve_edgar_zip():
    """Return the first existing EDGAR F-gases zip path (env override -> local cache -> SF6 cache)."""
    for cand in (os.environ.get("EDGAR_ZIP"), DEFAULT_EDGAR_ZIP, SF6_EDGAR_ZIP):
        if cand and os.path.exists(cand):
            return os.path.abspath(cand)
    raise FileNotFoundError(
        "EDGAR v8.0 F-gases bundle not found. Looked at:\n"
        f"  $EDGAR_ZIP        = {os.environ.get('EDGAR_ZIP') or '(unset)'}\n"
        f"  local cache       = {DEFAULT_EDGAR_ZIP}\n"
        f"  sf6 build cache   = {SF6_EDGAR_ZIP}\n"
        "Download the EDGAR v8.0_FT2022_GHG F-gases gridded NetCDF (emi_nc) bundle "
        f"(DOI {EDGAR_DOI}; https://edgar.jrc.ec.europa.eu/dataset_ghg80) and save the archive to "
        f"{DEFAULT_EDGAR_ZIP}, or point $EDGAR_ZIP at it.")


# Resolved on first use (keeps import side-effect-free if EDGAR is absent).
EDGAR_ZIP = SF6_EDGAR_ZIP if os.path.exists(SF6_EDGAR_ZIP) else DEFAULT_EDGAR_ZIP
EXTRACT = os.path.join(ROOT, "data", "benchmarks", "edgar_extracted")
MEMBER = "f-gases_emi_nc/{sub}/{sector}/emi_nc/v8.0_FT2022_GHG_{sub}_{year}_{sector}_emi.nc"


def edgar_sectors(substance="CF4"):
    with zipfile.ZipFile(_resolve_edgar_zip()) as z:
        names = z.namelist()
    pref = f"f-gases_emi_nc/{substance}/"
    secs = sorted({n[len(pref):].split("/")[0] for n in names
                   if n.startswith(pref) and n.endswith("_emi.nc")})
    return secs


def load_edgar(substance="CF4", year=2020, sector="TOTALS"):
    """Return EDGAR substance/sector/year as a DataArray (tonnes substance / cell / yr)."""
    os.makedirs(EXTRACT, exist_ok=True)
    member = MEMBER.format(sub=substance, year=year, sector=sector)
    local = os.path.join(EXTRACT, os.path.basename(member))
    if not os.path.exists(local):
        with zipfile.ZipFile(_resolve_edgar_zip()) as z:
            with z.open(member) as src, open(local, "wb") as dst:
                dst.write(src.read())
    ds = xr.open_dataset(local)
    var = next((v for v in ds.data_vars if v.lower() not in ("spatial_ref", "crs")),
               list(ds.data_vars)[0])
    return ds[var]


def global_total(da):
    return float(np.nansum(da.values))


if __name__ == "__main__":
    zip_path = _resolve_edgar_zip()
    print(f"[edgar] zip: {zip_path}  exists={os.path.exists(zip_path)}")
    secs = edgar_sectors("CF4")
    print(f"[edgar] CF4 sectors: {secs}")
    for sector in ("TOTALS", "NFE"):
        if sector not in secs:
            print(f"[edgar] sector {sector} absent; skipping")
            continue
        da = load_edgar("CF4", 2020, sector)
        gt = global_total(da)
        print(f"[edgar] CF4 {sector} 2020: global {gt:,.0f} t/yr (~{gt/1000:.2f} kt/yr) dims={dict(da.sizes)}")
