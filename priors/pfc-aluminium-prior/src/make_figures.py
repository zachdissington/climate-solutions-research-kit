"""Generate the three manuscript figures for the ESSD data descriptor (Rev 2).

Fig 1: global registry map (points sized by capacity; China cluster anchors flagged).
Fig 2: production-rescaled 1-degree global weight field (log scale).
Fig 3: European 0.1-degree capacity field with the evaluation smelter cells.

Land outline: Natural Earth 110m land GeoJSON (downloaded once into paper/figures/).
Run:  <sf6 venv python> src/make_figures.py
"""
import csv
import json
import os
import urllib.request

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, "paper", "figures")
os.makedirs(FIG, exist_ok=True)
NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
          "geojson/ne_110m_land.geojson")
NE_PATH = os.path.join(FIG, "ne_110m_land.geojson")


def land_polys():
    if not os.path.exists(NE_PATH):
        urllib.request.urlretrieve(NE_URL, NE_PATH)
    gj = json.load(open(NE_PATH, encoding="utf-8"))
    polys = []
    for feat in gj["features"]:
        g = feat["geometry"]
        if g["type"] == "Polygon":
            polys.extend(g["coordinates"])
        elif g["type"] == "MultiPolygon":
            for p in g["coordinates"]:
                polys.extend(p)
    return polys


def draw_land(ax, polys, lw=0.4):
    for ring in polys:
        xy = np.asarray(ring)
        ax.plot(xy[:, 0], xy[:, 1], color="0.55", lw=lw, zorder=1)


def registry():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "factors", "smelters_global.csv"),
                                    encoding="utf-8")))
    return [r for r in rows if r["status_2020"].strip().lower() == "operating"]


def fig1(polys):
    op = registry()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    draw_land(ax, polys)
    for grp, color, marker, label in (
            ("CHN", "#d95f02", "^", "China cluster anchors (12; see Sect. 2.3)"),
            ("other", "#1f6fb4", "o", "registered smelters (82)")):
        sel = [r for r in op if (r["country_iso3"] == "CHN") == (grp == "CHN")]
        lons = [float(r["lon"]) for r in sel]
        lats = [float(r["lat"]) for r in sel]
        caps = np.array([float(r["capacity_ktpa"] or 50) for r in sel])
        ax.scatter(lons, lats, s=6 + caps * 0.06, c=color, marker=marker,
                   alpha=0.8, edgecolors="white", linewidths=0.4, zorder=3, label=label)
    ax.set_xlim(-180, 180); ax.set_ylim(-60, 80)
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.set_title("Primary-aluminium smelters operating in 2020 (point area ∝ nameplate capacity)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig1_registry.png"), dpi=300)
    plt.close(fig)


def fig2(polys):
    da = xr.open_dataset(os.path.join(ROOT, "outputs", "prior_cf4_global_production.nc"))
    name = [v for v in da.data_vars][0]
    f = da[name]
    latn = "lat" if "lat" in f.coords else "latitude"
    lonn = "lon" if "lon" in f.coords else "longitude"
    v = np.nan_to_num(f.values)
    v = np.where(v > 0, v, np.nan)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    draw_land(ax, polys)
    LA, LO = np.meshgrid(f[latn].values, f[lonn].values, indexing="ij")
    nz = ~np.isnan(v)
    pm = ax.scatter(LO[nz], LA[nz], c=v[nz], s=14, marker="s",
                    norm=LogNorm(vmin=np.nanmin(v), vmax=np.nanmax(v)),
                    cmap="viridis", zorder=2)
    fig.colorbar(pm, ax=ax, shrink=0.75,
                 label="relative weight (kt-equivalent, rescale before use; log scale)")
    ax.set_xlim(-180, 180); ax.set_ylim(-60, 80)
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.set_title("Production-rescaled global CF$_4$ smelter weight field (1°, recommended variant)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_production_field.png"), dpi=300)
    plt.close(fig)


def fig3(polys):
    f = xr.open_dataarray(os.path.join(ROOT, "outputs", "prior_cf4_europe_capacity.nc"))
    latn = "lat" if "lat" in f.coords else "latitude"
    lonn = "lon" if "lon" in f.coords else "longitude"
    v = np.nan_to_num(f.values)
    v = np.where(v > 0, v, np.nan)
    eu = [r for r in csv.DictReader(open(os.path.join(ROOT, "factors",
                                                      "smelters_europe_killtest.csv"),
                                         encoding="utf-8"))
          if r["status_2020"].strip().lower() == "operating"]
    fig, ax = plt.subplots(figsize=(7.5, 7))
    draw_land(ax, polys, lw=0.5)
    LA, LO = np.meshgrid(f[latn].values, f[lonn].values, indexing="ij")
    nz = ~np.isnan(v)
    pm = ax.scatter(LO[nz], LA[nz], c=v[nz], s=22, marker="s",
                    norm=LogNorm(vmin=np.nanmin(v), vmax=np.nanmax(v)),
                    cmap="viridis", zorder=2)
    ax.scatter([float(r["lon"]) for r in eu], [float(r["lat"]) for r in eu],
               s=70, facecolors="none", edgecolors="#d62728", linewidths=1.0, zorder=4,
               label="operating European smelters (27)")
    fig.colorbar(pm, ax=ax, shrink=0.7,
                 label="capacity weight (kt yr$^{-1}$, relative; log scale)")
    ax.set_xlim(-26, 32); ax.set_ylim(34, 72)
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.set_title("European 0.1° capacity-weighted CF$_4$ field and the registry smelters",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_europe_field.png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    polys = land_polys()
    fig1(polys)
    fig2(polys)
    fig3(polys)
    print("wrote:", os.listdir(FIG))
