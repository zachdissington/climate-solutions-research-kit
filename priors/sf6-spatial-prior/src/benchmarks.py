"""Load the existing gridded SF6 emission products that use the population/nightlights proxy --
the baselines this artifact's spatial prior must beat (Phase 3) and calibrate to (Phase 2).

Two products:
- GAINS/IIASA  : SF6-specific, global, 0.5 deg, 2005-2020, kt/cell/yr. CC-BY-4.0. ~6 MB. (PRIMARY)
- EDGAR v8.0   : F-gases are BUNDLED (no standalone SF6 grid); the gridded product is a single
                 1.04 GB zip covering all F-gases. Whether SF6 is a separable variable inside is
                 verified only on demand (--edgar). GAINS is the working SF6 baseline until then.

earth-osm's CLI is broken on Windows but is unused here. Run:  python src/benchmarks.py [--edgar]
"""
import os
import sys
import zipfile
import urllib.request

import numpy as np
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "benchmarks")
OUT = os.path.join(ROOT, "outputs")

GAINS_URL = "https://zenodo.org/records/12708771/files/MOD_SF6_FLUX_GAINS_IIASA_ALL_GBL_YEAR_V1_20231031.nc"
GAINS_FILE = os.path.join(DATA, "gains_sf6_global_0p5deg_2005-2020.nc")

# EDGAR v8.0 GHG: F-gases are bundled (all F-gases together), 1.04 GB.
EDGAR_FGAS_URL = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/v80_FT2022_GHG/EDGAR_f-gases_emi_nc.zip"
EDGAR_FILE = os.path.join(DATA, "EDGAR_f-gases_emi_nc.zip")

# Coarse regional boxes (lon_min, lon_max, lat_min, lat_max) for a no-dependency spatial sanity check.
# SF6 is dominated by East Asia (China ~57% of global) and other industrialized grids -- so the
# regional split is itself a sanity test: if "East Asia" doesn't lead, something loaded wrong.
REGIONS = {
    "Europe":        (-12, 40, 35, 72),
    "North America": (-170, -52, 24, 72),
    "East Asia":     (100, 150, 18, 54),
    "South Asia":    (60, 100, 5, 38),
}


def _download(url, dest, label):
    os.makedirs(DATA, exist_ok=True)
    if os.path.exists(dest):
        print(f"[{label}] cached: {dest} ({os.path.getsize(dest)/1e6:.1f} MB)")
        return dest
    print(f"[{label}] downloading {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"[{label}] saved {dest} ({os.path.getsize(dest)/1e6:.1f} MB)")
    return dest


def _find_latlon(da):
    """Return (lat_name, lon_name) handling common naming."""
    names = {n.lower(): n for n in da.coords}
    lat = next((names[k] for k in ("lat", "latitude", "y") if k in names), None)
    lon = next((names[k] for k in ("lon", "longitude", "x") if k in names), None)
    return lat, lon


def load_gains_sf6(year=2020):
    """GAINS SF6 -> xarray.DataArray for `year`, in tonnes SF6 / cell / yr (kt -> t)."""
    _download(GAINS_URL, GAINS_FILE, "GAINS")
    ds = xr.open_dataset(GAINS_FILE)
    print(f"[GAINS] variables: {list(ds.data_vars)}")
    print(f"[GAINS] coords: {list(ds.coords)}  dims: {dict(ds.sizes)}")
    # pick the SF6 emission variable (the single data var, or one matching 'sf6'/'flux'/'emi')
    var = next((v for v in ds.data_vars if any(k in v.lower() for k in ("sf6", "flux", "emi"))),
               list(ds.data_vars)[0])
    da = ds[var]
    if "time" in da.dims or "year" in da.dims:
        tdim = "time" if "time" in da.dims else "year"
        try:
            da = da.sel({tdim: year})
        except Exception:
            yrs = da[tdim].values
            print(f"[GAINS] year {year} not found in {yrs[:3]}..{yrs[-3:]}; using last")
            da = da.isel({tdim: -1})
    return da * 1000.0  # kt -> t


def global_total(da):
    return float(np.nansum(da.values))


def regional_totals(da):
    """Boolean-mask sums (no coord-order assumptions; handles descending lat & 0-360 lon)."""
    lat, lon = _find_latlon(da)
    latv, lonv = da[lat], da[lon]
    out = {}
    for name, (lo0, lo1, la0, la1) in REGIONS.items():
        # express boxes in the file's own longitude convention
        if float(lonv.max()) > 180:
            lo0 %= 360
            lo1 %= 360
        lon_ok = (lonv >= lo0) & (lonv <= lo1) if lo0 <= lo1 else (lonv >= lo0) | (lonv <= lo1)
        lat_ok = (latv >= la0) & (latv <= la1)
        out[name] = float(np.nansum(da.where(lat_ok & lon_ok).values))
    return out


EDGAR_EXTRACT = os.path.join(DATA, "edgar_extracted")
EDGAR_MEMBER = "f-gases_emi_nc/SF6/{sector}/emi_nc/v8.0_FT2022_GHG_SF6_{year}_{sector}_emi.nc"


def load_edgar_sf6(year=2020, sector="TOTALS"):
    """Extract one EDGAR SF6 sector/year .nc from the bundle and return tonnes SF6 / cell / yr.
    sector in {TOTALS, PRU_SOL (product use - the population-proxy switchgear sector), NFE (non-ferrous/Mg)}.
    """
    os.makedirs(EDGAR_EXTRACT, exist_ok=True)
    member = EDGAR_MEMBER.format(year=year, sector=sector)
    local = os.path.join(EDGAR_EXTRACT, os.path.basename(member))
    if not os.path.exists(local):
        with zipfile.ZipFile(EDGAR_FILE) as z:
            with z.open(member) as src, open(local, "wb") as dst:
                dst.write(src.read())
    ds = xr.open_dataset(local)
    var = next((v for v in ds.data_vars if v.lower() not in ("spatial_ref", "crs")), list(ds.data_vars)[0])
    da = ds[var]
    units = str(da.attrs.get("units", "")).lower()
    # EDGAR emi_nc are documented as "ton substance / 0.1deg / yr" -> already tonnes/cell. Flag if flux.
    if "m-2" in units or "m2" in units or "/s" in units:
        print(f"[EDGAR] WARNING: {sector} units look like flux ({units}); expected per-cell tonnes.")
    print(f"[EDGAR] {sector} {year}: var={var} units={units or 'unspecified'} dims={dict(da.sizes)}")
    return da


def inspect_edgar():
    """Download the EDGAR F-gas bundle (1 GB) and report whether SF6 is a separable variable/file."""
    _download(EDGAR_FGAS_URL, EDGAR_FILE, "EDGAR")
    with zipfile.ZipFile(EDGAR_FILE) as z:
        names = z.namelist()
    sf6 = [n for n in names if "sf6" in n.lower()]
    print(f"[EDGAR] {len(names)} files in bundle; first few: {names[:5]}")
    print(f"[EDGAR] SF6-specific files: {sf6 if sf6 else 'NONE -- F-gases only as aggregate'}")
    return sf6


def main(do_edgar=False):
    os.makedirs(OUT, exist_ok=True)
    print("=== GAINS SF6 (primary baseline) ===")
    g = load_gains_sf6(2020)
    gt = global_total(g)
    print(f"[GAINS] global SF6 total 2020: {gt:,.0f} t/yr  (~{gt/1000:,.1f} kt/yr; sanity range ~7-9 kt/yr)")
    print("[GAINS] regional split (t/yr):")
    for k, v in sorted(regional_totals(g).items(), key=lambda kv: -kv[1]):
        print(f"    {k:14s} {v:12,.0f}")
    if do_edgar:
        print("\n=== EDGAR SF6 (cross-check; population-proxy baseline) ===")
        for sector in ("TOTALS", "PRU_SOL"):
            e = load_edgar_sf6(2020, sector)
            et = global_total(e)
            print(f"[EDGAR] {sector} global SF6 2020: {et:,.0f} t/yr  (~{et/1000:,.1f} kt/yr)")
            for k, v in sorted(regional_totals(e).items(), key=lambda kv: -kv[1]):
                print(f"    {k:14s} {v:12,.0f}")
        print("\n[compare] GAINS grids only the power sector; EDGAR TOTALS = all SF6 sectors, so EDGAR"
              "\n[compare] TOTALS > GAINS is expected. The shared test: both must be East-Asia-dominant"
              "\n[compare] and ~8-10 kt/yr order. EDGAR PRU_SOL is the pure population-gridded sector.")
    else:
        print("\n[EDGAR] skipped (1.04 GB bundle). Re-run with --edgar to download + check SF6 separability.")


if __name__ == "__main__":
    main(do_edgar="--edgar" in sys.argv)
