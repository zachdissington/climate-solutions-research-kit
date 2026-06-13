#!/usr/bin/env python3
"""Reformat the global smelter-resolved CF4 prior into a CF-convention, drop-in NetCDF
that mirrors the grid + coordinate naming of the Puschel et al. (egusphere-2025-5656)
deposited fields, so it can be swapped in as an a-priori with no regridding.

Honesty guardrail: our field is a RELATIVE (normalized) spatial prior, not absolute flux.
The reference 'emis_post' is kg/m2/s; ours is a relative spatial weight to be rescaled to
the inversion's total flux. We document that in the variable attrs rather than mislabel units.
Values are copied byte-identical (reformat only, no numeric change). The spatial pattern is
time-invariant (a recent smelter-capacity snapshot), so it is kept 2D with a note to broadcast.
"""
import pathlib
import numpy as np
import xarray as xr

PRIOR = pathlib.Path(__file__).resolve().parent.parent
REF = PRIOR / "data" / "posteriors" / "puschel" / "CF4" / "CF4_constrained_2020.nc"

VARIANTS = {
    "outputs/prior_cf4_global_capacity.nc": {
        "out": "outputs/prior_cf4_global_capacity_flexinvert.nc",
        "long_name": "Smelter-resolved CF4 spatial prior (capacity-weighted, relative)",
        "comment": (
            "Relative spatial prior for CF4 emissions, weighted by primary-aluminium smelter "
            "nameplate capacity. Normalized spatial weight (not absolute flux): rescale to the "
            "inversion total before use as an a-priori. Grid matches the egusphere-2025-5656 "
            "deposited emission fields (1deg global, 180x360). Time-invariant smelter snapshot; "
            "broadcast across inversion years."
        ),
    },
    "outputs/prior_cf4_global_presence.nc": {
        "out": "outputs/prior_cf4_global_presence_flexinvert.nc",
        "long_name": "Smelter-resolved CF4 spatial prior (presence-only, relative)",
        "comment": (
            "Relative spatial prior for CF4 emissions, presence-only robustness variant "
            "(each operating smelter = 1). Normalized spatial weight (not absolute flux): rescale "
            "to the inversion total before use as an a-priori. Grid matches the egusphere-2025-5656 "
            "deposited emission fields (1deg global, 180x360). Time-invariant smelter snapshot; "
            "broadcast across inversion years."
        ),
    },
    "outputs/prior_cf4_global_production.nc": {
        "out": "outputs/prior_cf4_global_production_flexinvert.nc",
        "long_name": "Smelter-resolved CF4 spatial prior (production-rescaled, relative; recommended global variant)",
        "comment": (
            "Relative spatial prior for CF4 emissions. Country totals rescaled to USGS MCS 2021 "
            "national primary-aluminium production (2020e), distributed within each country by "
            "registered smelter capacity. Recommended for GLOBAL use: it corrects the raw registry's "
            "country-share bias (registry covers ~12 of ~120 Chinese smelters, so the raw capacity "
            "field carries China at 28% vs its true ~57% production share; this variant carries 56.7%). "
            "Within-China placement still relies on the 12 registered major clusters. Normalized "
            "spatial weight (not absolute flux): rescale to the inversion total before use as an "
            "a-priori. Grid matches the egusphere-2025-5656 deposited emission fields (1deg global, "
            "180x360). Time-invariant smelter snapshot (operating-2020 status); broadcast across "
            "inversion years."
        ),
    },
}

ref = xr.open_dataset(REF, decode_times=False)
ref_lat = ref["latitude"].values.astype("float32")
ref_lon = ref["longitude"].values.astype("float32")

for src_rel, cfg in VARIANTS.items():
    src = xr.open_dataset(PRIOR / src_rel)
    var = src[list(src.data_vars)[0]]
    vals = var.values.astype("float32")

    # grid sanity: our lat/lon must equal the reference axes exactly
    assert np.array_equal(src["lat"].values.astype("float32"), ref_lat), "lat mismatch vs Puschel grid"
    assert np.array_equal(src["lon"].values.astype("float32"), ref_lon), "lon mismatch vs Puschel grid"

    da = xr.DataArray(
        vals,
        dims=("latitude", "longitude"),
        coords={"latitude": ref_lat, "longitude": ref_lon},
        name="emis_prior",
    )
    da.attrs = {
        "title": "emis_prior",
        "long_name": cfg["long_name"],
        "units": "1",
        "comment": cfg["comment"],
    }
    da["latitude"].attrs = {"title": "latitude", "standard_name": "latitude",
                            "long_name": "latitude", "units": "degrees_north"}
    da["longitude"].attrs = {"title": "longitude", "standard_name": "longitude",
                             "long_name": "longitude", "units": "degrees_east"}
    out_ds = da.to_dataset()
    out_ds.attrs = {
        "title": "Smelter-resolved CF4 spatial prior",
        "summary": ("Open smelter-resolved spatial prior for CF4 (PFC-14), on the same 1deg global "
                    "grid as the egusphere-2025-5656 deposited fields. Relative spatial weights; "
                    "rescale to total flux before use as an a-priori."),
        "source": "https://doi.org/10.5281/zenodo.20617485",
        "references": "https://github.com/zachdissington/climate-solutions-research-kit",
        "Conventions": "CF-1.8",
    }
    out_path = PRIOR / cfg["out"]
    out_ds.to_netcdf(out_path)

    # verify round-trip: values byte-identical, grid identical
    chk = xr.open_dataset(out_path)
    cv = chk["emis_prior"].values.astype("float32")
    assert np.array_equal(cv, vals), "value mismatch after reformat"
    assert np.array_equal(chk["latitude"].values.astype("float32"), ref_lat)
    assert np.array_equal(chk["longitude"].values.astype("float32"), ref_lon)
    print(f"OK {cfg['out']}: shape={cv.shape} sum={float(cv.sum()):.1f} "
          f"nonzero={int((cv>0).sum())} coords=latitude/longitude var=emis_prior")
