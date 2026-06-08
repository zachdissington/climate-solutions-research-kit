# Climate Solutions Research Kit

Open methods and tooling for climate-solution and high-GWP emissions research. The headline is a reusable method, with four worked case studies, for building point-source-resolved spatial priors for orphaned high-GWP greenhouse gases. It also ships tooling to turn a Project Drawdown Explorer export into a queryable local database.

This repo contains only original work. It does **not** redistribute Project Drawdown's data — you bring your own export (see below), in line with [Drawdown's terms](https://drawdown.org/terms-of-use).

## What's inside

- `priors/` — four worked spatial-prior case studies: SF6 (electricity grid), PFC-CF4 (aluminium smelters), HFC-23 (HCFC-22 plants), NF3 (semiconductor fabs). Each carries `src/` (the code), `factors/` (emission factors + sources), and validation reports.
- `methodology/` — the spatial-prior artifact playbook, a pre-build stress test, and a Climate TRACE coverage-gap analysis.
- `scripts/` — tooling to build and query a local solutions database from your own Drawdown Explorer export.

`data/` and `solutions/` are generated locally from your Drawdown export and are gitignored — Drawdown's content is never committed here.

## The spatial-prior method, and its honest results

The premise: national inventories spread high-GWP gas emissions across population (a weak proxy), while many of these gases come from a handful of industrial point sources. A facility-resolved prior should beat the population proxy. Four tests:

| Gas | Source | Verdict |
|-----|--------|---------|
| PFC-CF4 | aluminium smelters | **Qualified GO** — the smelter prior beats the population proxy in Europe; the decisive China test is collaboration-gated |
| SF6 | electricity grid | **Refuted** — the grid proxy is too diffuse to beat population; full post-mortem in `methodology/` |
| HFC-23 | HCFC-22 plants | **No-go** — European plants sit inside populated regions, so the prior ties the proxy |
| NF3 | semiconductor fabs | **No-go** — European NF3 is a small abated residual; the real signal is East-Asian and gated |

The reusable lesson lives in `methodology/spatial-prior-artifact-playbook.md`: run the single cheapest decisive test first (find the posterior, pull a baseline, one correlation, go/no-go in hours) before building the full pipeline. Three of four gases were killed in hours this way.

Each prior under `priors/` is self-contained: its `src/` downloads the public posteriors and inventories it needs (ICOS, AGAGE, EDGAR — see each `factors/SOURCES.md`) and runs the kill-test. These use only public atmospheric data.

## Solutions-database tooling (bring your own Drawdown export)

The `scripts/` build a queryable local database from Project Drawdown's Explorer data, which you download yourself under [Drawdown's terms](https://drawdown.org/terms-of-use):

```bash
pip install python-frontmatter pyyaml

# 1. Export the Drawdown Explorer table to CSV from drawdown.org/solutions,
#    save it as data/explorer-solutions-YYYY-MM-DD.csv
# 2. Build one queryable markdown note per solution (YAML frontmatter = the database):
python scripts/build_solution_stubs.py --csv data/explorer-solutions-YYYY-MM-DD.csv

# 3. Query it:
python scripts/query_solutions.py --classification "Highly Recommended"
python scripts/query_solutions.py --min-impact 1.0 --json
```

The tooling and the database schema (the YAML frontmatter shape) are original; the underlying solution attributes remain Project Drawdown's, fetched and stored locally on your own machine.

## License

MIT — see `LICENSE`. It covers the original code, methods, and tooling in this repo. Project Drawdown content is not included; obtain it from drawdown.org under their terms.

## Acknowledgements

Built on the open atmospheric-science community (ICOS, AGAGE, EDGAR), whose public inversion posteriors and gridded inventories make independent work like this possible. The solutions tooling targets Project Drawdown's Explorer data (drawdown.org).
