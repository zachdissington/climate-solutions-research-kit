"""Phase 2a, Layer 1: OSM transmission substations -> gridded SF6 emission weights (Germany).

Per-substation SF6 emission weight (RELATIVE; the absolute level is set later by national-total
calibration in 2b):
    weight = charge_proxy(voltage_class) x P(GIS | voltage) x leak_rate
- charge_proxy: GIS per-breaker SF6 charge by voltage class (factors/nameplate_charge_by_voltage.csv).
- P(GIS): probability gas-insulated (factors/gis_probability.csv; MODELLED monotonic-in-voltage prior).
- leak_rate: 0.5 %/yr (factors/leak_emission_factors.csv central value; a scalar).

Extraction: DIRECT Overpass query, NOT earth-osm. earth-osm's geofabrik index is stale (it requested a
dated DE pbf that 404s) on top of its Windows CLI bug -- so for DE we query Overpass directly (lighter,
controllable, no 4 GB download). Filter to transmission-class: substation type in {transmission,
subtransmission} OR parsed voltage >= 110 kV.

Run:  python src/layer1_model.py
"""
import os
import csv
import json
import urllib.request

import numpy as np
import xarray as xr

from extract_substations import parse_voltage  # reuse the messy-voltage parser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACTORS = os.path.join(ROOT, "factors")
OUT = os.path.join(ROOT, "outputs")
DATA = os.path.join(ROOT, "data", "osm")

LEAK_RATE = 0.005           # 0.5 %/yr central (factors/leak_emission_factors.csv)
TRANSMISSION_KV_MIN = 110.0
GRID_RES = 0.1

# region configs (ISO3166-1 code + mainland bbox lon0,lon1,lat0,lat1)
REGIONS = {
    "DE": (5.8, 15.1, 47.2, 55.1),
    "FR": (-5.2, 9.6, 41.3, 51.1),     # mainland France
}

OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "sf6-spatial-prior/1.0 (research; +https://github.com/zachdissington)"
QUERY_TMPL = """
[out:json][timeout:300];
area["ISO3166-1"="{iso}"][admin_level=2]->.reg;
(
  way["power"="substation"]["substation"~"^(transmission|subtransmission)$"](area.reg);
  node["power"="substation"]["substation"~"^(transmission|subtransmission)$"](area.reg);
  way["power"="substation"]["voltage"](area.reg);
  node["power"="substation"]["voltage"](area.reg);
);
out center tags;
"""

# voltage(kV) -> class representative used to key the factor tables
VCLASS = [(180, 145), (300, 245), (460, 420), (600, 525), (1e9, 765)]


def _load_factor(path, key_col, val_cols):
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader((ln for ln in fh if not ln.startswith("#"))):
            out[int(round(float(r[key_col])))] = {c: r.get(c) for c in val_cols}
    return out


def vclass_rep(kv):
    for thresh, rep in VCLASS:
        if kv < thresh:
            return rep
    return 765


def fetch_substations(iso):
    os.makedirs(DATA, exist_ok=True)
    cache = os.path.join(DATA, f"overpass_{iso.lower()}_substations.json")
    if os.path.exists(cache):
        print(f"[overpass] cached: {cache}")
        payload = json.load(open(cache, encoding="utf-8"))
    else:
        print(f"[overpass] querying {iso} transmission substations...")
        req = urllib.request.Request(OVERPASS, data=QUERY_TMPL.format(iso=iso).encode("utf-8"),
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            payload = json.loads(r.read().decode("utf-8", "replace"))
        json.dump(payload, open(cache, "w", encoding="utf-8"))
        print(f"[overpass] cached -> {cache}")
    return payload.get("elements", [])


def main(region="DE"):
    os.makedirs(OUT, exist_ok=True)
    charge_t = _load_factor(os.path.join(FACTORS, "nameplate_charge_by_voltage.csv"),
                            "representative_kv", ["gis_charge_kg_per_breaker"])
    gis_t = _load_factor(os.path.join(FACTORS, "gis_probability.csv"),
                         "representative_kv", ["p_gis"])

    elements = fetch_substations(region)
    print(f"[overpass] raw elements: {len(elements)}")

    subs, imputed = [], 0
    for e in elements:
        tags = e.get("tags", {})
        lat = e.get("lat") or (e.get("center") or {}).get("lat")
        lon = e.get("lon") or (e.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        kv_raw = parse_voltage(tags.get("voltage"))
        kv = (kv_raw / 1000.0) if kv_raw else None     # parse_voltage returns volts
        stype = (tags.get("substation") or "").lower()
        # transmission-class filter
        is_tx = stype in ("transmission", "subtransmission") or (kv is not None and kv >= TRANSMISSION_KV_MIN)
        if not is_tx:
            continue
        if kv is None:               # transmission type but no voltage -> impute baseline class
            kv = 145.0
            imputed += 1
        subs.append({"lat": float(lat), "lon": float(lon), "kv": kv,
                     "rep": vclass_rep(kv), "type": stype or "untyped"})

    n = len(subs)
    print(f"[layer1] transmission-class substations: {n}  (voltage imputed: {imputed} = {100*imputed/max(n,1):.0f}%)")

    # per-substation weight = charge_proxy x P(GIS) x leak
    for s in subs:
        charge = float(charge_t[s["rep"]]["gis_charge_kg_per_breaker"])
        pgis = float(gis_t[s["rep"]]["p_gis"])
        s["pgis"] = pgis
        s["weight"] = charge * pgis * LEAK_RATE

    # grid to 0.1 deg over region bbox
    lo0, lo1, la0, la1 = REGIONS[region]
    lons = np.arange(lo0, lo1, GRID_RES)
    lats = np.arange(la0, la1, GRID_RES)
    grid = np.zeros((len(lats), len(lons)))
    gridded = 0
    for s in subs:
        j = int((s["lon"] - lo0) / GRID_RES)
        i = int((s["lat"] - la0) / GRID_RES)
        if 0 <= i < len(lats) and 0 <= j < len(lons):
            grid[i, j] += s["weight"]
            gridded += 1

    # ---- validation gates ----
    print("\n=== VALIDATION ===")
    oob = n - gridded   # valid-coord substations outside the mainland bbox (overseas territories/border)
    g1 = "PASS" if oob / max(n, 1) < 0.02 else "WARN"
    print(f"  [{g1}] G1 coverage: extracted={n}, gridded(in-bbox)={gridded}, "
          f"out-of-bbox={oob} (overseas/border — reported, not silently lost)")
    bad_p = [s for s in subs if not (0 <= s["pgis"] <= 1)]
    bad_w = [s for s in subs if not np.isfinite(s["weight"]) or s["weight"] < 0]
    g2 = "PASS" if not bad_p and not bad_w else "FAIL"
    print(f"  [{g2}] G2 valid-model: P(GIS) out-of-range={len(bad_p)}, bad weights={len(bad_w)}")
    flat = grid[grid > 0]
    ratio = (flat.max() / np.median(flat)) if flat.size else 0
    g3 = "PASS" if ratio > 3 else "WARN"
    print(f"  [{g3}] G3 spatial-sanity: top-cell/median weight ratio = {ratio:.1f} (want >> 1, i.e. non-uniform)")
    top_idx = np.dstack(np.unravel_index(np.argsort(grid.ravel())[::-1][:10], grid.shape))[0]
    for i, j in top_idx:
        print(f"        cell ({lats[i]:.1f}N,{lons[j]:.1f}E) weight={grid[i,j]:.3f}")
    g4 = "INFO"
    print(f"  [{g4}] G4 imputation: {100*imputed/max(n,1):.0f}% of substations used imputed voltage (145 kV baseline)")

    if g1 == "FAIL" or g2 == "FAIL":
        print("\n[layer1] HARD GATE FAILED -- not writing grid.")
        raise SystemExit(1)

    # write NetCDF + committed summary
    from datetime import date
    da = xr.DataArray(grid, coords={"lat": lats, "lon": lons}, dims=["lat", "lon"],
                      name="sf6_layer1_weight",
                      attrs={"description": "Layer-1 relative SF6 emission weight (uncalibrated)",
                             "units": "relative", "leak_rate_pct_yr": 0.5})
    nc = os.path.join(OUT, f"layer1_{region.lower()}_{date.today().isoformat()}.nc")
    da.to_netcdf(nc)
    print(f"\n[layer1] wrote grid -> {nc}  (total weight {grid.sum():.2f}, {n} substations)")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "DE")
