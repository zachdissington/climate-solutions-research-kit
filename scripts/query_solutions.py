"""Query the Drawdown solutions database (solutions/*.md frontmatter).

The flat solutions/ folder + YAML frontmatter IS the database; this script is
the query layer so sessions/subagents never need to load 190 files.

Usage:
    python query_solutions.py                              # all, sorted by impact
    python query_solutions.py --classification "Highly Recommended"
    python query_solutions.py --sector Electricity
    python query_solutions.py --speed "Emergency Brake"
    python query_solutions.py --min-impact 1.0
    python query_solutions.py --enrichment stub --published
    python query_solutions.py --json                       # JSON output
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import frontmatter

SOLUTIONS_DIR = Path(__file__).resolve().parent.parent / "solutions"


def load_all() -> list[dict]:
    items = []
    for path in sorted(SOLUTIONS_DIR.glob("*.md")):
        if path.name == "_index.md":
            continue
        meta = frontmatter.load(path).metadata
        meta["_file"] = path.name
        items.append(meta)
    return items


def matches(meta: dict, args: argparse.Namespace) -> bool:
    def contains(field: str, needle: str | None) -> bool:
        if needle is None:
            return True
        return needle.lower() in str(meta.get(field) or "").lower()

    if not contains("classification", args.classification):
        return False
    if not contains("sector", args.sector):
        return False
    if not contains("cluster", args.cluster):
        return False
    if not contains("speed_of_action", args.speed):
        return False
    if not contains("enrichment", args.enrichment):
        return False
    if args.action and (meta.get("action") or "").lower() != args.action.lower():
        return False
    if args.min_impact is not None:
        if meta.get("ghg_impact_gt_max") is None or meta["ghg_impact_gt_max"] < args.min_impact:
            return False
    if args.published and not meta.get("data_published"):
        return False
    return True


def main() -> None:
    # Windows consoles default to cp1252; the data contains unicode (CO₂, ×10⁶)
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classification", help="substring match, e.g. 'Highly Recommended'")
    parser.add_argument("--sector", help="substring match, e.g. 'Electricity'")
    parser.add_argument("--cluster", help="substring match, e.g. 'Shift Production'")
    parser.add_argument("--speed", help="substring match: Emergency Brake | Gradual | Delayed")
    parser.add_argument("--action", help="exact match, e.g. Deploy / Protect / Restore")
    parser.add_argument("--enrichment", help="stub | enriched")
    parser.add_argument("--min-impact", type=float, help="min ghg_impact_gt_max (Gt CO₂-eq/yr)")
    parser.add_argument("--published", action="store_true", help="only solutions with published data")
    parser.add_argument("--json", action="store_true", help="output JSON instead of table")
    args = parser.parse_args()

    if not SOLUTIONS_DIR.is_dir():
        sys.exit(f"ERROR: {SOLUTIONS_DIR} does not exist — run build_solution_stubs.py first")

    results = [m for m in load_all() if matches(m, args)]
    results.sort(key=lambda m: -(m.get("ghg_impact_gt_max") or 0))

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    print(f"{len(results)} solutions\n")
    print(f"{'Solution':<55} {'Class':<19} {'Gt/yr max':>9} {'Speed':<16} {'Enriched':<8}")
    print("-" * 110)
    for m in results:
        name = f"{m.get('action', '')}: {m.get('solution', '')}"[:54]
        impact = m.get("ghg_impact_gt_max")
        impact_s = f"{impact:.2f}" if impact is not None else "—"
        print(
            f"{name:<55} {str(m.get('classification', ''))[:18]:<19} {impact_s:>9} "
            f"{str(m.get('speed_of_action') or '—')[:15]:<16} {m.get('enrichment', ''):<8}"
        )


if __name__ == "__main__":
    main()
