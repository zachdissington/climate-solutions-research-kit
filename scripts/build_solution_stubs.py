"""Build/refresh Drawdown solution stub notes from the Explorer CSV.

Reads data/explorer-solutions-<date>.csv and writes one markdown note per
solution row into solutions/, with all CSV attributes as YAML frontmatter.
Also regenerates solutions/_index.md (one line per solution, sorted by GHG
impact).

Idempotent: re-running refreshes CSV-derived frontmatter but NEVER overwrites
the body or enrichment fields of a note whose frontmatter says
`enrichment: enriched`.

Usage:
    python build_solution_stubs.py            # uses newest CSV in data/
    python build_solution_stubs.py --csv path/to/file.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import frontmatter
import yaml

SUST_ROOT = Path(__file__).resolve().parent.parent  # Sustainability/
DATA_DIR = SUST_ROOT / "data"
SOLUTIONS_DIR = SUST_ROOT / "solutions"

# CSV column indexes (header has unicode hyphens; index access is robust)
COL_ACTION = 0
COL_SOLUTION = 1
COL_CLASSIFICATION = 2
COL_MODE = 3
COL_SECTOR = 4
COL_CLUSTER = 5
COL_ADOPTION_UNIT = 6
COL_EFFECTIVENESS = 7
COL_ADOPTION_CURRENT = 8
COL_ADOPTION_ACHIEVABLE = 9
COL_GHG_IMPACT = 10
COL_COST = 11
COL_POLLUTANTS = 12
COL_SPEED = 13
COL_ADAPTATION_BENEFITS = 14
COL_ENVIRONMENT_BENEFITS = 15
COL_WELLBEING_BENEFITS = 16

# Fields (and the body) preserved across rebuilds for any note that has been
# checked against the live page: enrichment is "enriched" (page had content)
# or "page_pending" (page exists but Drawdown hasn't written it yet).
ENRICHED_PRESERVED_FIELDS = ("url", "enrichment", "enriched_date", "page_status")


def clean(value: str) -> str:
    """Collapse embedded newlines/whitespace in a CSV cell."""
    return re.sub(r"\s+", " ", (value or "").strip())


def slugify(action: str, solution: str) -> str:
    """Kebab-case slug matching the Drawdown Explorer URL pattern.

    e.g. ('Deploy', 'Distributed Solar PV') -> 'deploy-distributed-solar-pv'
    """
    text = f"{action} {solution}".lower()
    text = re.sub(r"[&:/,().]", " ", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return re.sub(r"-+", "-", text)


def parse_range(value: str) -> tuple[float | None, float | None]:
    """Parse '0.05 to 0.12' -> (0.05, 0.12). Returns (None, None) if not numeric."""
    value = clean(value)
    m = re.match(r"^(-?[\d,.]+)\s+to\s+(-?[\d,.]+)$", value)
    if not m:
        return None, None
    try:
        return (
            float(m.group(1).replace(",", "")),
            float(m.group(2).replace(",", "")),
        )
    except ValueError:
        return None, None


def parse_float(value: str) -> float | None:
    value = clean(value).replace(",", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_list(value: str) -> list[str]:
    """Split a comma-separated cell into a clean list."""
    return [clean(p) for p in (value or "").split(",") if clean(p)]


def newest_csv() -> Path:
    candidates = sorted(DATA_DIR.glob("explorer-solutions-*.csv"))
    if not candidates:
        sys.exit(f"ERROR: no explorer-solutions-*.csv found in {DATA_DIR}")
    return candidates[-1]


def row_to_metadata(row: list[str], csv_date: str) -> dict:
    action = clean(row[COL_ACTION])
    solution = clean(row[COL_SOLUTION])
    slug = slugify(action, solution)
    ghg_min, ghg_max = parse_range(row[COL_GHG_IMPACT])
    adoption_unit = clean(row[COL_ADOPTION_UNIT])

    return {
        "slug": slug,
        "url": f"https://drawdown.org/explorer/{slug}",
        "action": action,
        "solution": solution,
        "classification": clean(row[COL_CLASSIFICATION]),
        "mode": clean(row[COL_MODE]) or None,
        "sector": clean(row[COL_SECTOR]),
        "cluster": clean(row[COL_CLUSTER]) or None,
        "speed_of_action": clean(row[COL_SPEED]) or None,
        "ghg_impact_gt_min": ghg_min,
        "ghg_impact_gt_max": ghg_max,
        "cost_usd_per_t_co2": parse_float(row[COL_COST]),
        "adoption_unit": adoption_unit or None,
        "adoption_current": clean(row[COL_ADOPTION_CURRENT]) or None,
        "adoption_achievable": clean(row[COL_ADOPTION_ACHIEVABLE]) or None,
        "effectiveness_per_unit": clean(row[COL_EFFECTIVENESS]) or None,
        "pollutants": parse_list(row[COL_POLLUTANTS]),
        "adaptation_benefits": parse_list(row[COL_ADAPTATION_BENEFITS]),
        "environment_benefits": parse_list(row[COL_ENVIRONMENT_BENEFITS]),
        "wellbeing_benefits": parse_list(row[COL_WELLBEING_BENEFITS]),
        "data_published": ghg_max is not None,  # False = "Coming Soon" on Drawdown
        "csv_date": csv_date,
        "enrichment": "stub",
        "enriched_date": None,
    }


def stub_body(meta: dict) -> str:
    impact = (
        f"{meta['ghg_impact_gt_min']} to {meta['ghg_impact_gt_max']} Gt CO₂-eq/yr"
        if meta["data_published"]
        else "data not yet published by Drawdown (Coming Soon)"
    )
    return (
        f"# {meta['action']}: {meta['solution']}\n"
        f"\n"
        f"> **Stub** — frontmatter populated from the Drawdown Explorer CSV "
        f"({meta['csv_date']}). Body not yet enriched from the solution page.\n"
        f"\n"
        f"- Classification: {meta['classification']}\n"
        f"- Sector: {meta['sector']}\n"
        f"- Speed of action: {meta['speed_of_action'] or '—'}\n"
        f"- GHG impact: {impact}\n"
        f"- Source: {meta['url']}\n"
    )


def dump_note(meta: dict, body: str) -> str:
    fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n{body}"


def write_note(path: Path, meta: dict, body: str) -> None:
    path.write_text(dump_note(meta, body), encoding="utf-8")


def build_index(all_meta: list[dict]) -> str:
    """Generate _index.md: published-data solutions sorted by impact desc, then the rest."""

    def sort_key(m):
        return (
            0 if m["data_published"] else 1,
            -(m["ghg_impact_gt_max"] or 0),
            m["solution"],
        )

    rows = []
    for m in sorted(all_meta, key=sort_key):
        impact = (
            f"{m['ghg_impact_gt_min']}–{m['ghg_impact_gt_max']}"
            if m["data_published"]
            else "—"
        )
        cost = m["cost_usd_per_t_co2"]
        cost_s = f"{cost:g}" if cost is not None else "—"
        enriched = {"enriched": "yes", "page_pending": "pending"}.get(m["enrichment"], "")
        rows.append(
            f"| [{m['action']}: {m['solution']}]({m['slug']}.md) "
            f"| {m['classification']} | {m['sector']} | {impact} "
            f"| {m['speed_of_action'] or '—'} | {cost_s} | {enriched} |"
        )

    n_published = sum(1 for m in all_meta if m["data_published"])
    n_enriched = sum(1 for m in all_meta if m["enrichment"] == "enriched")
    n_pending = sum(1 for m in all_meta if m["enrichment"] == "page_pending")
    header = (
        "# Drawdown Solutions Index\n"
        "\n"
        f"Generated by `scripts/build_solution_stubs.py` — do not edit by hand.\n"
        f"{len(all_meta)} solutions | {n_published} with published data | "
        f"{n_enriched} enriched | {n_pending} page-pending (Drawdown hasn't written these pages yet).\n"
        "\n"
        "Query this database with `scripts/query_solutions.py` "
        "(filter by classification, sector, speed, impact, enrichment).\n"
        "\n"
        "| Solution | Classification | Sector | GHG Gt CO₂-eq/yr | Speed | Cost $/t | Enriched |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    return header + "\n".join(rows) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=None, help="Path to Explorer CSV")
    args = parser.parse_args()

    csv_path = args.csv or newest_csv()
    m = re.search(r"(\d{4}-\d{2}-\d{2})", csv_path.name)
    csv_date = m.group(1) if m else "unknown"

    SOLUTIONS_DIR.mkdir(exist_ok=True)

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if len(r) >= 17 and clean(r[COL_SOLUTION])]

    # Build metadata for every row; fail loudly on slug collisions
    seen: dict[str, str] = {}
    all_meta: list[dict] = []
    for row in rows:
        meta = row_to_metadata(row, csv_date)
        if meta["slug"] in seen:
            sys.exit(
                f"ERROR: slug collision: {meta['slug']!r} from "
                f"{meta['action']}/{meta['solution']} and {seen[meta['slug']]}"
            )
        seen[meta["slug"]] = f"{meta['action']}/{meta['solution']}"
        all_meta.append(meta)

    created, refreshed, preserved, pending = 0, 0, 0, 0
    for meta in all_meta:
        path = SOLUTIONS_DIR / f"{meta['slug']}.md"
        if path.exists():
            existing = frontmatter.load(path)
            state = existing.metadata.get("enrichment", "stub")
            if state != "stub":
                # Preserve checked body + enrichment fields; refresh CSV-derived fields
                for field in ENRICHED_PRESERVED_FIELDS:
                    if field in existing.metadata:
                        meta[field] = existing.metadata[field]
                write_note(path, meta, existing.content)
                if state == "page_pending":
                    pending += 1
                else:
                    preserved += 1
                continue
            refreshed += 1
        else:
            created += 1
        write_note(path, meta, stub_body(meta))

    (SOLUTIONS_DIR / "_index.md").write_text(build_index(all_meta), encoding="utf-8")

    n_published = sum(1 for m in all_meta if m["data_published"])
    print(f"CSV: {csv_path.name} ({len(rows)} solution rows)")
    print(
        f"Notes: {created} created, {refreshed} stub-refreshed, "
        f"{preserved} enriched-preserved, {pending} pending-preserved"
    )
    print(f"Published data: {n_published} | Coming Soon: {len(rows) - n_published}")
    print(f"Index: {SOLUTIONS_DIR / '_index.md'}")


if __name__ == "__main__":
    main()
