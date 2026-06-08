"""Deterministic validation gates for the Layer-2 point-source collection.

Proves no expected data was silently dropped by the collection/filter steps (the user's requirement).
Pure asserts + reconciliation, no test framework dependency. Each check returns (level, message)
where level in {PASS, WARN, FAIL}. The build refuses to write output unless all hard gates pass
(T5 may WARN). See plans/2026-06-03-eprtr-discodata-ingest-with-tests.md.
"""

# SW-Germany box for the inversion-identified production/recycling hotspot (lon, lon, lat, lat).
SW_DE_BOX = (7.0, 10.5, 47.5, 50.0)


def t1_no_silent_drops(eu_stats):
    """Collection: raw SF6-air records == joined-kept + dropped, with dropped reported (not hidden)."""
    raw, joined, dropped = eu_stats["raw"], eu_stats["joined"], eu_stats["dropped"]
    if raw != joined + dropped:
        return ("FAIL", f"T1 row accounting broken: raw {raw} != kept {joined} + dropped {dropped}")
    pct = (dropped / raw * 100) if raw else 0
    lvl = "FAIL" if pct > 5 else "PASS"
    return (lvl, f"T1 collection: raw={raw}, geocoded-kept={joined}, dropped(no-coord)={dropped} "
                 f"({pct:.1f}% — {eu_stats['dropped_kg']:.0f} kg); accounting reconciles")


def t2_mass_conservation(eu_stats):
    """Filter/join preserved mass: sum(joined kg) == raw SF6-air kg within rounding."""
    raw_kg, joined_kg = eu_stats["raw_kg"], eu_stats["joined_kg"] + eu_stats["dropped_kg"]
    diff = abs(raw_kg - joined_kg)
    lvl = "PASS" if diff <= max(1.0, raw_kg * 1e-4) else "FAIL"
    return (lvl, f"T2 mass conservation: raw={raw_kg:,.0f} kg vs accounted={joined_kg:,.0f} kg "
                 f"(diff {diff:,.1f} kg)")


def t3_geocoding(rows):
    """Every output row has valid, non-null coordinates."""
    bad = [r for r in rows if r.get("lat") is None or r.get("lon") is None
           or not (-90 <= float(r["lat"]) <= 90) or not (-180 <= float(r["lon"]) <= 180)]
    lvl = "FAIL" if bad else "PASS"
    return (lvl, f"T3 geocoding: {len(rows)-len(bad)}/{len(rows)} valid coords"
                 + (f"; BAD: {[r['facility_name'] for r in bad[:5]]}" if bad else ""))


def t4_dedup(rows):
    """No duplicate facility identity after latest-year collapse."""
    keys = [(r.get("source_dataset"), r.get("facility_name"), round(float(r["lat"]), 4),
             round(float(r["lon"]), 4)) for r in rows]
    dupes = len(keys) - len(set(keys))
    lvl = "FAIL" if dupes else "PASS"
    return (lvl, f"T4 dedup: {dupes} duplicate facility rows" if dupes else
                 f"T4 dedup: {len(rows)} unique facility rows")


def t5_known_answer_sw_germany(rows):
    """Known-answer: a German SF6 facility should sit in SW Germany (inversion hotspot). WARN if absent."""
    lo0, lo1, la0, la1 = SW_DE_BOX
    hits = [r for r in rows if str(r.get("country")) in ("DE", "Germany")
            and lo0 <= float(r["lon"]) <= lo1 and la0 <= float(r["lat"]) <= la1]
    if hits:
        top = max(hits, key=lambda r: r.get("sf6_tonnes_yr") or 0)
        return ("PASS", f"T5 SW-Germany known-answer: {len(hits)} facility(ies); top "
                        f"'{top['facility_name']}' {top.get('sf6_tonnes_yr')} t/yr")
    return ("WARN", "T5 SW-Germany: no facility in box — may be below E-PRTR threshold (not forced)")


def t6_cross_source(rows):
    """Combined output: every row geocoded + sourced; report per-source counts."""
    by_src = {}
    for r in rows:
        by_src[r.get("source_dataset", "?")] = by_src.get(r.get("source_dataset", "?"), 0) + 1
    missing_src = [r for r in rows if not r.get("source_dataset")]
    lvl = "FAIL" if missing_src else "PASS"
    return (lvl, f"T6 cross-source: {dict(by_src)}; total {len(rows)}"
                 + (f"; {len(missing_src)} missing source!" if missing_src else ""))


def run_all(rows, eu_stats):
    """Run every gate. Return (ok, results) where ok is False if any hard gate FAILs (T5 WARN ok)."""
    results = [
        t1_no_silent_drops(eu_stats),
        t2_mass_conservation(eu_stats),
        t3_geocoding(rows),
        t4_dedup(rows),
        t5_known_answer_sw_germany(rows),
        t6_cross_source(rows),
    ]
    ok = all(lvl != "FAIL" for lvl, _ in results)
    return ok, results
