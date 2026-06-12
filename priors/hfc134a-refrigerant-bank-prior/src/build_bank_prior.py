"""Build a deliberately CRUDE HFC-134a refrigerant-bank spatial prior over Europe.

Hypothesis: the in-use HFC-134a refrigerant bank (the dominant emission source — leakage from the
installed stock of mobile A/C, commercial/domestic refrigeration) is proportional to
population x cooling demand. So:

    bank(cell) ~ population(cell) x CDD(cell)

where CDD = annual cooling-degree-days = sum over months of max(0, T_month - 18 degC) x days_in_month.
This is a STOCK proxy, no calibration, Europe domain only. Crude is correct (playbook rule 3).

Inputs (public, no-auth, downloaded by fetch in this script's data/inputs/):
  - WorldClim 2.1 10-arcmin monthly mean temperature climatology (1970-2000), EPSG:4326.
    https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_tavg.zip
  - GHSL GHS-POP 2020, 30-arcsec WGS84 (coarsened here to the WorldClim 0.1667deg grid).
    JRC R2023A.

Outputs (DataArrays on the WorldClim 0.1667deg grid; the kill-test histograms them onto the
posterior grid):
  - outputs/prior_hfc134a_europe_bank.nc       (population x CDD)
  - outputs/prior_hfc134a_europe_population.nc  (population only — isolates whether CDD adds signal)
  - outputs/cdd_europe.nc                       (the CDD field, for inspection)

Europe crop box matches the posterior footprint (lat 10.7..79.1, lon -97.9..39.4) but we restrict to
the populated European land mass (lon -25..40) since the posterior's western extent is open ocean.

Run:  python src/build_bank_prior.py
"""
import os
import io
import zipfile

import numpy as np
import xarray as xr
import rasterio
from rasterio.enums import Resampling

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INP = os.path.join(ROOT, "data", "inputs")
OUT = os.path.join(ROOT, "outputs")

WC_ZIP = os.path.join(INP, "wc2.1_10m_tavg.zip")
POP_ZIP = os.path.join(INP, "GHS_POP_2020_4326_30ss.zip")

# Crop to the European land domain (the posterior's data sit here; west of -25 is Atlantic).
LON_MIN, LON_MAX = -25.0, 40.0
LAT_MIN, LAT_MAX = 30.0, 75.0
DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dtype=float)
TBASE = 18.0  # degC cooling base


def load_worldclim_tavg():
    """Return (months[12] x lat x lon) tavg on the WorldClim grid, cropped to Europe, + lat/lon."""
    z = zipfile.ZipFile(WC_ZIP)
    names = sorted(n for n in z.namelist() if n.endswith(".tif"))
    assert len(names) == 12, names
    stack = []
    lat = lon = None
    for n in names:
        with rasterio.open(io.BytesIO(z.read(n))) as r:
            arr = r.read(1).astype("float32")
            arr[arr == r.nodata] = np.nan
            # build lat/lon centers from transform
            if lat is None:
                T = r.transform
                cols = np.arange(r.width)
                rows = np.arange(r.height)
                lon_full = T.c + (cols + 0.5) * T.a
                lat_full = T.f + (rows + 0.5) * T.e  # T.e negative
        stack.append(arr)
    arr = np.stack(stack)  # (12, H, W)
    # crop to Europe
    lon_m = (lon_full >= LON_MIN) & (lon_full <= LON_MAX)
    lat_m = (lat_full >= LAT_MIN) & (lat_full <= LAT_MAX)
    arr = arr[:, lat_m][:, :, lon_m]
    return arr, lat_full[lat_m], lon_full[lon_m]


def compute_cdd(tavg, lat, lon):
    """CDD = sum_m max(0, T_m - 18) * days_m. tavg shape (12, H, W)."""
    dd = np.clip(tavg - TBASE, 0, None) * DAYS[:, None, None]
    cdd = np.nansum(dd, axis=0)
    cdd[np.all(np.isnan(tavg), axis=0)] = np.nan  # keep ocean as nan
    return cdd


def load_population_on_grid(lat, lon):
    """Read GHSL 30ss population, sum-aggregate onto the WorldClim (lat,lon) target grid."""
    z = zipfile.ZipFile(POP_ZIP)
    tif = [n for n in z.namelist() if n.endswith(".tif")]
    assert len(tif) == 1, tif
    # extract to disk (rasterio windowed read needs a real path / vsizip)
    local = os.path.join(INP, os.path.basename(tif[0]))
    if not os.path.exists(local):
        with z.open(tif[0]) as src, open(local, "wb") as dst:
            dst.write(src.read())

    # target grid edges (ascending lat/lon, regular spacing)
    dlat = abs(lat[1] - lat[0]); dlon = abs(lon[1] - lon[0])
    lat_sorted = np.sort(lat)
    lon_sorted = np.sort(lon)
    lat_edges = np.concatenate([[lat_sorted[0] - dlat / 2], lat_sorted + dlat / 2])
    lon_edges = np.concatenate([[lon_sorted[0] - dlon / 2], lon_sorted + dlon / 2])

    with rasterio.open(local) as r:
        # window covering our Europe box
        from rasterio.windows import from_bounds
        win = from_bounds(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX, transform=r.transform)
        data = r.read(1, window=win).astype("float64")
        T = r.window_transform(win)
        nod = r.nodata
        if nod is not None:
            data[data == nod] = 0.0
        data[data < 0] = 0.0
        H, W = data.shape
        cols = np.arange(W); rows = np.arange(H)
        plon = T.c + (cols + 0.5) * T.a
        plat = T.f + (rows + 0.5) * T.e

    # histogram population counts into target grid cells
    PLO, PLA = np.meshgrid(plon, plat)
    Hgrid, _, _ = np.histogram2d(PLA.ravel(), PLO.ravel(),
                                 bins=[lat_edges, lon_edges], weights=data.ravel())
    # histogram2d returns rows in ascending lat; map back to target lat orientation
    pop = Hgrid  # indexed [lat_sorted, lon_sorted]
    return pop, lat_sorted, lon_sorted


def as_da(arr, lat, lon, name):
    return xr.DataArray(arr, dims=("latitude", "longitude"),
                        coords={"latitude": lat, "longitude": lon}, name=name)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("[wc] loading WorldClim tavg ...")
    tavg, lat, lon = load_worldclim_tavg()
    print(f"  tavg {tavg.shape} lat {lat.min():.2f}..{lat.max():.2f} lon {lon.min():.2f}..{lon.max():.2f}")
    cdd = compute_cdd(tavg, lat, lon)
    print(f"  CDD range {np.nanmin(cdd):.0f}..{np.nanmax(cdd):.0f} mean {np.nanmean(cdd):.0f}")

    print("[pop] loading GHSL population onto WorldClim grid ...")
    pop, plat, plon = load_population_on_grid(lat, lon)
    print(f"  pop grid {pop.shape} total {np.nansum(pop):,.0f} people  (Europe box)")

    # align CDD to the population's sorted lat/lon orientation
    # rebuild CDD on sorted axes
    lat_order = np.argsort(lat); lon_order = np.argsort(lon)
    cdd_s = cdd[np.ix_(lat_order, lon_order)]
    assert np.allclose(np.sort(lat), plat) and np.allclose(np.sort(lon), plon)

    cdd_s = np.nan_to_num(cdd_s, nan=0.0)
    bank = pop * cdd_s

    da_bank = as_da(bank, plat, plon, "bank_prior")
    da_pop = as_da(pop, plat, plon, "population_prior")
    da_cdd = as_da(cdd_s, plat, plon, "cdd")
    da_bank.to_netcdf(os.path.join(OUT, "prior_hfc134a_europe_bank.nc"))
    da_pop.to_netcdf(os.path.join(OUT, "prior_hfc134a_europe_population.nc"))
    da_cdd.to_netcdf(os.path.join(OUT, "cdd_europe.nc"))
    print(f"[out] wrote bank/population/cdd priors to {OUT}")
    print(f"  bank total weight {bank.sum():.3e}; pop total {pop.sum():,.0f}; "
          f"corr(pop,bank) cells -> built")


if __name__ == "__main__":
    main()
