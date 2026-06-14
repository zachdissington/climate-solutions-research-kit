# C2F6 (PFC-116) — Low-Confidence Companion to the CF4 Smelter Prior

**What this is:** the honest, ship-ready caveat for the C2F6 leg of the PFC smelter-prior artifact. C2F6 travels *with* the CF4 deposit as a low-confidence companion. It is **never** presented as a peer to the CF4 layer.

**What this is NOT:** a standalone C2F6 data product. There is **no separate C2F6 deep registry, no standalone C2F6 Zenodo deposit, and no new C2F6 prior field** — by decision, not by omission (see below).

Canonical decision: [`../decisions/2026-06-07-c2f6-killtest.md`](../decisions/2026-06-07-c2f6-killtest.md) (2026-06-13 exact-2020 correction). Status: **WEAK / QUALIFIED**, parked-by-gate.

---

## The honest scope (ship this beside CF4)

The same primary-aluminium smelter prior that resolves CF4 can be applied to C2F6, because the two PFCs share the same point sources (smelter anode effects co-emit CF4 and C2F6). On the premise side this is sound: per EDGAR, aluminium (the NFE/non-ferrous category) is **~58% of global C2F6** (450 of 778 t/yr) — the *majority* source, better than the pre-run "minority source" worry.

But the European kill-test against the flat-prior ICOS PARIS posterior comes back **weak**, and the primary metric governs:

- **Correlation (the primary metric, exact-2020):** the smelter prior wins decisively where CF4 also won — Iceland 0.252 vs ~0, Germany 0.120 vs 0.099, Spain 0.056 vs 0.016 — but **pooled Europe slightly favours EDGAR** (ours best 0.013 vs EDGAR 0.023, both ≈ 0). Only 4 of 11 regions beat EDGAR, far weaker than CF4's decisive pooled win.
- **Enrichment (secondary metric, exact-2020):** smelter-cell percentile POST **70.2%** vs EDGAR **59.8%** vs the inversion's own PRIOR 68.3% (22 in-domain smelters) — i.e. the posterior *does* rank smelter cells modestly above the population proxy. This sub-claim is positive, but it does not govern.

**Why weak:** C2F6's global flux is tiny (~778 t/yr), so the European signal is even lower-SNR than CF4's; the flat-prior inversion barely constrains it, and ~42% of C2F6 is population-coincident non-aluminium (electronics/fab). The two metrics disagree at the margin; the correlation governs, so C2F6 stays low-confidence.

**One-paragraph version, for a README/deposit note:**
> C2F6 shares the CF4 smelters and aluminium is its majority source (~58% per EDGAR), so the same smelter prior applies. Against the European ICOS PARIS posterior it is decisive only in remote, well-constrained theatres (Iceland); pooled Europe is at best a tie with EDGAR's population proxy. C2F6 therefore ships as a **low-confidence companion to CF4, not a standalone product**, and should not be used as a peer to the CF4 layer.

## The gate (when this could upgrade)

The leg is **parked**, not abandoned. It upgrades only if a **returned East-Asia / China PFC posterior** flips it — the same posterior that would validate CF4. Europe's free-ICOS engine is exhausted of clean C2F6 wins, so no further Europe-domain spend is warranted ahead of that.

This is why C2F6 **folds into the CF4 outreach** rather than running its own track: a single returned East-Asia posterior validates CF4 *and* re-tests C2F6 at once (and cheaply re-tests HFC-23/NF3). See the adoption tracker's Phase-2 trigger: [`outreach/adoption-tracker.md`](outreach/adoption-tracker.md) and the long-term plan [`../plans/2026-06-10-cf4-academic-contribution-longterm.md`](../plans/2026-06-10-cf4-academic-contribution-longterm.md).

## Why no build (the explicit non-action)

The 2026-06-07 decision (corrected 2026-06-13) is explicit: *"Do not build a separate C2F6 deep registry."* Building one now would (a) contradict the canonical decision and (b) repeat the SF6 pre-build mistake — spending a full production pipeline ahead of the one cheap decisive test that governs the value claim. The decisive C2F6 test is already run (WEAK); the next decisive input is gated on outreach, not on more European building.

---

*Provenance:* numbers above are quoted verbatim from `../decisions/2026-06-07-c2f6-killtest.md` (2026-06-13 exact-2020 re-run) and `validation_report_killtest.md` (C2F6 section). No fresh computation was performed for this companion doc. Authored 2026-06-14 (Wave-3 Session E).
