"""Extract OSM power substations for a region and report SF6-relevance stats.

Uses the earth-osm PYTHON API (earth_osm.eo) directly — the earth-osm CLI is broken on Windows
(`args.py` does a Unix-only `import resource`). The API path avoids that import entirely.

Guardrail #2 (see ../README.md): the SF6 universe is transmission-class substations only, not all
substations. This script reports total vs transmission-class counts and voltage-tag coverage so the
Phase-1 feasibility gate is a real number, not an assumption.

Usage:
    python src/extract_substations.py LU          # one ISO region (proof)
    python src/extract_substations.py DE           # Germany (the SW-Germany validation litmus)
"""
import sys
import os

from earth_osm import eo

# Transmission-class threshold. SF6-insulated (GIS) switchgear dominates at high voltage; sub-transmission
# and distribution substations are overwhelmingly air-insulated. 110 kV is a defensible lower bound for
# "transmission-class" (EU HV transmission starts ~110 kV). Tunable; recorded here so the choice is explicit.
TRANSMISSION_KV_MIN = 110.0

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def parse_voltage(raw):
    """OSM voltage tags are messy: '380000', '220000;110000', '380 kV', ''. Return max volts (float) or None."""
    if raw is None:
        return None
    s = str(raw).strip().lower().replace("kv", "").replace("v", "")
    if not s or s in ("nan", "none"):
        return None
    best = None
    # voltages can be ';'-separated (multi-voltage substations) — take the max
    for part in s.replace(",", ";").split(";"):
        part = part.strip()
        if not part:
            continue
        try:
            val = float(part)
        except ValueError:
            continue
        # heuristic: values < 1000 are almost certainly kV written without the 'kV' unit
        if val < 1000:
            val *= 1000.0
        best = val if best is None else max(best, val)
    return best


def main(region):
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[extract] region={region} feature=power/substation  (earth-osm API, geofabrik)")
    df = eo.get_osm_data(region, "power", "substation", data_dir=DATA_DIR, progress_bar=False)

    n_total = len(df)
    print(f"[extract] raw substation records: {n_total}")
    print(f"[extract] columns: {list(df.columns)}")
    if n_total == 0:
        print("[extract] WARNING: zero substations — bad region code or empty extract.")
        return

    # earth-osm flattens OSM tags into 'tags.<key>' columns. Voltage = 'tags.voltage'.
    volt_col = "tags.voltage" if "tags.voltage" in df.columns else (
        "voltage" if "voltage" in df.columns else None)
    if volt_col is None:
        print("[extract] WARNING: no voltage column found — inspect columns above to locate the tag.")
        return

    volts = df[volt_col].apply(parse_voltage)
    n_tagged = volts.notna().sum()
    n_transmission = (volts >= TRANSMISSION_KV_MIN * 1000.0).sum()

    print(f"[stats] voltage-tagged:      {n_tagged}/{n_total}  ({100*n_tagged/n_total:.1f}%)")
    print(f"[stats] untagged (impute):   {n_total - n_tagged}")
    print(f"[stats] transmission-class (>= {TRANSMISSION_KV_MIN:.0f} kV): {n_transmission}"
          f"  ({100*n_transmission/n_total:.1f}% of all, {100*n_transmission/max(n_tagged,1):.1f}% of tagged)")
    if n_tagged:
        kv = (volts.dropna() / 1000.0)
        print(f"[stats] voltage distribution (kV): min={kv.min():.0f} median={kv.median():.0f} max={kv.max():.0f}")

    # gas_insulated tag: the only DIRECT GIS signal in OSM. The stress test found it on just ~3,996 objects
    # worldwide — i.e. present for <1% of assets. Quantify it here; the model treats GIS status as a
    # probabilistic layer precisely because this tag is too sparse to rely on (guardrail #2).
    if "tags.gas_insulated" in df.columns:
        gi = df["tags.gas_insulated"].notna().sum()
        print(f"[stats] gas_insulated tag present: {gi}/{n_total} ({100*gi/n_total:.2f}%) "
              f"-- too sparse to use directly; model GIS probability instead")


if __name__ == "__main__":
    region = sys.argv[1] if len(sys.argv) > 1 else "LU"
    main(region)
