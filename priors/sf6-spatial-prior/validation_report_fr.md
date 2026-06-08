# Phase 2c — France (Best-Case) Behavior Check + France-vs-Germany Contrast

> Run 2026-06-03. Honest scope: the inversion posterior is not downloadable for any country, so this is
> a **directional** check, NOT a measured "beats the proxy" win. What it can show: whether the prior
> behaves sensibly and diverges from population *in the direction the inversion literature says is
> correct*, in a country where SF6 is grid-distributed.

## Why France is the best case

France's SF6 is **grid-distributed, not hotspot-dominated**: reported industrial point sources (E-PRTR)
sum to just **3.8% of the ~75 t national total** (13 small facilities, all <0.3 t) — no single dominant
industrial source like Germany's under-reported production/recycling hotspot. The bulk is spread across
the RTE transmission / nuclear-switchyard network, which in France is largely **decoupled from
population** (the grid serves nuclear plants and industry, not just cities).

## Result — divergence from the population proxies

(EDGAR's SF6 grid *is* the population proxy — verified PRU_SOL = urban population. So correlation with
EDGAR measures how population-like our prior is. Lower = more grid-driven = the right direction.)

| Region | corr(ours, EDGAR) | corr(ours, GAINS) | corr(EDGAR, GAINS) | L2 share | Layer-1 substations |
|---|---|---|---|---|---|
| **France** (grid-distributed) | **−0.03** | **−0.02** | 0.69 | 3.8% | 48,642 |
| **Germany** (hotspot) | 0.55 | 0.34 | 0.62 | 1.8% | 8,835 |

- **France: our prior is orthogonal to population** (corr ≈ 0) while the two population proxies agree
  with each other (0.69). Our French allocation is a genuinely different, grid-following spatial
  pattern — exactly the "SF6 ≠ population" signal the inversion community says is correct.
- **Spatial sanity (France):** top weighted cells are **Toulouse (#1), Lyon, Paris, Metz/Nancy
  (Lorraine), Besançon, Orléans** — real RTE grid hubs spread across the country, with Toulouse
  ranking *above* Paris. Population gridding would pile onto Paris; ours does not. Not noise — a real,
  spread, grid-following pattern.

## The France-vs-Germany contrast (the intellectual payoff)

The prior's divergence from population is **maximal in France (corr ≈ 0) and only moderate in Germany
(0.55)**. This localizes where an infrastructure prior plausibly adds value:
- **Grid-distributed countries (France):** the grid is decoupled from population, so a grid-based prior
  produces a substantially different — and directionally-correct — allocation. This is the regime where
  the artifact could matter.
- **Hotspot-dominated countries (Germany):** the dominant source is an under-reported industrial site
  that neither grid nor population captures, and the grid happens to track population anyway — so the
  prior has little to offer.

## Honest verdict

This is **consistent with the thesis in its best case** — in France the prior behaves exactly as the
"infrastructure beats population" argument predicts (population-orthogonal, grid-following, sensible
hubs). It is **NOT proof of "beats the proxy"**: without the inversion posterior we cannot measure
whether ours is *closer to truth*, only that it is *different from population in the right direction*.

Caveats (do not over-read the positive): France's OSM tags far more sub-transmission as "transmission"
(48,642 vs Germany's 8,835), so the French layer is finer-grained and more spread — part of the low
correlation is granularity, not just decoupling. And corr ≈ 0 means "unrelated to population," which is
necessary but not sufficient for "correct."

## Where this leaves the project

The Germany null and the France directional-positive together say: **the prior's value is
country-conditional** — promising where SF6 is grid-distributed, absent where a hidden industrial
hotspot dominates. A real metric verdict still requires an inversion posterior (author collaboration).
The artifact is a defensible *conditional* methods contribution, not a proven universal improvement.
