"""Layer 2: industrial SF6 point sources (the hotspots a substation map misses).

US  : EPA GHGRP via the Envirofacts REST service. SF6 = gas_id 6. Facilities are pulled by the
      SF6-relevant subparts -- SS (SF6 equipment MANUFACTURE), I (electronics/semiconductor),
      T (magnesium production) = true industrial point sources; DD (T&D equipment USE) = grid, which
      overlaps Layer 1 and is tagged separately. SF6 is reported in CO2e -> divided by the SF6 GWP
      (factors/SOURCES.md) to recover tonnes.
EU  : E-PRTR / EU Industrial Emissions Portal. The portal is JS-rendered, so there is no scriptable
      download URL; load_eprtr_sf6() reads a MANUALLY downloaded CSV and prints instructions if absent.
      (Same no-fabrication fallback used for any awkward source.)

Coverage: EU + US only. China (~57% of global SF6) has no facility-level reporting -> a labeled gap,
consistent with the geography-honesty guardrail. Written to factors/point_sources.csv (committed).

Run:  python src/point_sources.py
"""
import os
import csv
import json
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "point_sources")
FACTORS = os.path.join(ROOT, "factors")
OUT_CSV = os.path.join(FACTORS, "point_sources.csv")

SF6_GWP100 = 25200.0          # AR6 GWP100 for SF6 (see factors/SOURCES.md); co2e -> mass
EF = "https://data.epa.gov/efservice"
SF6_GAS_ID = 6

# SF6-relevant GHGRP subparts and whether they are industrial point sources (Layer 2) or grid use.
SUBPARTS = {"SS": "industrial", "I": "industrial", "T": "industrial", "DD": "grid_use"}

# EU E-PRTR via the EEA discodata public SQL API (no manual download).
DISCODATA = "https://discodata.eea.europa.eu/sql"
SNAP = os.path.join(FACTORS, "snapshots")  # committed, dated provenance copies (small)
EPRTR_CSV = os.path.join(DATA, "eprtr_sf6_releases.csv")  # optional offline override only

# SF6 air releases joined to facility coordinates. Join key resolved + verified 2026-06-03:
# PollutantRelease.facilityReportId -> ProductionFacilityReport.Id; then FacilitiesPerSite on
# localId + namespace + reportingYear (=480 records, 100% geocoded, 84 facilities). LEFT join so
# any non-geocoded rows are visible (counted as 'dropped'), never silently inner-joined away.
EPRTR_SQL = (
    "SELECT r.totalPollutantQuantityKg AS kg, pfr.localId AS local_id, pfr.namespace AS ns, "
    "pfr.countryCode AS country, pfr.reportingYear AS year, f.facilityName AS name, "
    "f.x_4326 AS lon, f.y_4326 AS lat, f.facilityEPRTRAnnexIMainActivity AS activity "
    "FROM [IED].[latest].[PollutantRelease] r "
    "JOIN [IED].[latest].[ProductionFacilityReport] pfr ON pfr.Id = r.facilityReportId "
    "LEFT JOIN [IED].[latest].[FacilitiesPerSite] f ON f.facilityLocalId = pfr.localId "
    "AND f.facilityNamespace = pfr.namespace AND f.facilityReportingYear = pfr.reportingYear "
    "WHERE r.pollutant = 'SF6' AND r.mediumCode = 'AIR'"
)
EPRTR_RAW_COUNT_SQL = ("SELECT COUNT(*) AS n, SUM(totalPollutantQuantityKg) AS kg "
                       "FROM [IED].[latest].[PollutantRelease] WHERE pollutant='SF6' AND mediumCode='AIR'")


def _ef_json(path, page=10000):
    """Fetch an Envirofacts efservice path with ROWS pagination; return list of dict rows."""
    rows, start = [], 0
    while True:
        url = f"{EF}/{path}/ROWS/{start}:{start+page}/JSON"
        with urllib.request.urlopen(url, timeout=90) as r:
            chunk = json.loads(r.read().decode("utf-8", "replace"))
        if not chunk:
            break
        rows.extend(chunk)
        if len(chunk) < page:
            break
        start += page
    return rows


def _discodata_json(query, page=100000):
    """Query the EEA discodata SQL API; return list of dict rows (paginated)."""
    import urllib.parse
    rows, p = [], 1
    while True:
        url = f"{DISCODATA}?{urllib.parse.urlencode({'query': query, 'p': p, 'nrOfHits': page})}"
        with urllib.request.urlopen(url, timeout=120) as r:
            payload = json.loads(r.read().decode("utf-8", "replace"))
        chunk = payload.get("results", payload if isinstance(payload, list) else [])
        if "errors" in payload:
            raise RuntimeError(f"discodata error: {payload['errors']}")
        rows.extend(chunk)
        if len(chunk) < page:
            break
        p += 1
    return rows


def load_ghgrp_sf6():
    """Return list of US SF6 point-source dicts with lat/lon, latest-year SF6 tonnes, and sector tag."""
    # 1) SF6 emissions facts (co2e) -> latest year per facility, converted to tonnes SF6.
    facts = _ef_json(f"PUB_FACTS_SECTOR_GHG_EMISSION/gas_id/{SF6_GAS_ID}")
    latest = {}  # facility_id -> (year, co2e_sum)
    for f in facts:
        fid, yr = f.get("facility_id"), f.get("year")
        co2e = f.get("co2e_emission") or 0
        if fid is None or yr is None:
            continue
        if fid not in latest or yr > latest[fid][0]:
            latest[fid] = (yr, 0.0)
        if yr == latest[fid][0]:
            latest[fid] = (yr, latest[fid][1] + float(co2e))
    print(f"[GHGRP] SF6-emitting facilities (any subpart): {len(latest)}")

    # 2) facility metadata (lat/lon/name/subparts) for the SF6-relevant subparts.
    facs = {}
    for sp in SUBPARTS:
        recs = _ef_json(f"PUB_DIM_FACILITY/reported_subparts/CONTAINING/{sp}")
        for r in recs:
            fid = r.get("facility_id")
            if fid is None or fid in facs:
                continue
            facs[fid] = r
    print(f"[GHGRP] facilities in SF6-relevant subparts {list(SUBPARTS)}: {len(facs)}")

    out = []
    for fid, rec in facs.items():
        lat, lon = rec.get("latitude"), rec.get("longitude")
        if lat is None or lon is None:
            continue
        yr, co2e = latest.get(fid, (None, 0.0))
        tonnes = round(co2e / SF6_GWP100, 3) if co2e else None
        subs = (rec.get("reported_subparts") or "")
        tag = "industrial" if any(s in subs for s in ("SS", "I", "T")) else "grid_use"
        out.append({
            "facility_name": rec.get("facility_name"),
            "country": "US",
            "lat": lat, "lon": lon,
            "sf6_tonnes_yr": tonnes,
            "year": yr,
            "source_dataset": "EPA GHGRP (Envirofacts)",
            "sector": tag,
            "notes": f"subparts={subs}",
        })
    return out


def load_eprtr_sf6(pull_date):
    """Query EU SF6 air releases + facility coords via discodata. Return (rows, eu_stats).
    rows = one row per facility (latest reporting year); eu_stats feeds the T1/T2 validation gates.
    Writes a dated, committed snapshot of the raw join for reproducible provenance.
    """
    raw = _discodata_json(EPRTR_RAW_COUNT_SQL)[0]
    raw_n, raw_kg = int(raw["n"]), float(raw["kg"] or 0)
    joined = _discodata_json(EPRTR_SQL)
    print(f"[E-PRTR] raw SF6-air records: {raw_n} ({raw_kg:,.0f} kg); joined rows: {len(joined)}")

    # dated snapshot of the raw join (provenance; small) -> committed
    os.makedirs(SNAP, exist_ok=True)
    snap = os.path.join(SNAP, f"eprtr_sf6_{pull_date}.csv")
    if joined:
        with open(snap, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(joined[0].keys()))
            w.writeheader(); w.writerows(joined)
        print(f"[E-PRTR] snapshot -> {snap}")

    geocoded = [r for r in joined if r.get("lat") is not None and r.get("lon") is not None]
    dropped = [r for r in joined if r.get("lat") is None or r.get("lon") is None]
    dropped_kg = sum(float(r.get("kg") or 0) for r in dropped)

    # collapse facility (local_id+ns) -> latest reporting year
    latest = {}
    for r in geocoded:
        key = (r.get("local_id"), r.get("ns"))
        yr = r.get("year") or 0
        if key not in latest or yr > (latest[key].get("year") or 0):
            latest[key] = r
    rows = [{
        "facility_name": r.get("name"),
        "country": r.get("country") or "EU",
        "lat": float(r["lat"]), "lon": float(r["lon"]),
        "sf6_tonnes_yr": round(float(r["kg"]) / 1000.0, 3) if r.get("kg") is not None else None,
        "year": r.get("year"),
        "source_dataset": "E-PRTR (EEA discodata [IED].[latest])",
        "sector": "industrial",
        "notes": f"activity={r.get('activity')}",
    } for r in latest.values()]
    eu_stats = {
        "raw": raw_n, "raw_kg": raw_kg,
        "joined": len(geocoded), "dropped": len(dropped),
        "joined_kg": sum(float(r.get("kg") or 0) for r in geocoded), "dropped_kg": dropped_kg,
    }
    print(f"[E-PRTR] EU facilities (latest-year): {len(rows)}")
    return rows, eu_stats


def _snapshot(rows, name, pull_date):
    """Write a dated, committed provenance snapshot of a source pull."""
    if not rows:
        return
    os.makedirs(SNAP, exist_ok=True)
    path = os.path.join(SNAP, f"{name}_{pull_date}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"[snapshot] {name} -> {path} ({len(rows)} rows)")


def main():
    from datetime import date
    import validate_point_sources as V
    os.makedirs(DATA, exist_ok=True)
    pull_date = date.today().isoformat()

    us = load_ghgrp_sf6()
    _snapshot(us, "ghgrp_sf6", pull_date)
    eu, eu_stats = load_eprtr_sf6(pull_date)

    rows = [r for r in (us + eu) if r.get("lat") is not None and r.get("lon") is not None]

    # ---- validation gates (build refuses to write output on any FAIL) ----
    ok, results = V.run_all(rows, eu_stats)
    print("\n=== VALIDATION ===")
    for lvl, msg in results:
        print(f"  [{lvl}] {msg}")
    if not ok:
        print("\n[point_sources] HARD GATE FAILED -- not writing point_sources.csv. Fix above and re-run.")
        raise SystemExit(1)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        fh.write(f"# Layer-2 SF6 industrial point sources. Pull date {pull_date}.\n")
        fh.write("# US = EPA GHGRP (Envirofacts); EU = E-PRTR via EEA discodata [IED].[latest], SF6/AIR.\n")
        fh.write("# GAP: China (~57% of global SF6) and most of Asia have no facility-level reporting.\n")
        w = csv.DictWriter(fh, fieldnames=["facility_name", "country", "lat", "lon",
                                           "sf6_tonnes_yr", "year", "source_dataset", "sector", "notes"])
        w.writeheader()
        w.writerows(rows)
    ind = [r for r in rows if r["sector"] == "industrial"]
    print(f"\n[point_sources] wrote {len(rows)} rows ({len(ind)} industrial) -> {OUT_CSV}")
    print("[point_sources] top by SF6 t/yr:")
    for r in sorted(rows, key=lambda r: -(r["sf6_tonnes_yr"] or 0))[:10]:
        print(f"    {r['country']:3s} {str(r['facility_name'])[:42]:42s} {r['sf6_tonnes_yr']} t/yr [{r['sector']}]")


if __name__ == "__main__":
    main()
