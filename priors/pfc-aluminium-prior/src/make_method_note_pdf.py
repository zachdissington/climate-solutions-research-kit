"""Render the CF4 smelter-prior method note to a one-page PDF (reportlab Platypus).
Faithful to outreach/2026-06-06-method-note.md (Rev 3, 2026-06-12 — adversarially audited claims).
Moved from .tmp into src/ because the PDF is a deposited artifact (reproducibility)."""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "outreach", "Smelter-resolved_CF4_prior_method_note.pdf")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=14.5, leading=17, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Italic"], fontSize=8, leading=10,
                     textColor=colors.HexColor("#555555"), spaceAfter=8)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=10, leading=12,
                    spaceBefore=5, spaceAfter=2, textColor=colors.HexColor("#1a3a5a"))
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=8.0, leading=10.2, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, spaceAfter=0)
hcell = ParagraphStyle("hcell", parent=cell, textColor=colors.white)


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(t, body), leftIndent=10) for t in items],
        bulletType="bullet", start="•", leftIndent=12, bulletFontSize=7,
    )


flow = []
flow.append(Paragraph("Smelter-resolved CF4 spatial prior: a one-page method note", h1))
flow.append(Paragraph(
    "Open research note for the F-gas atmospheric-inversion and inventory community. "
    "Rev 3 (June 2026): adversarially audited — every number re-derived from code+data; a year-selection "
    "bug fixed (four ELRIS/InTEM members were silently scored against 2019; all ensemble-wide numbers now "
    "from exact-2020 fields; Iceland, RHIME-only, unaffected); enrichment metric rebuilt on a consistent "
    "mass basis with midrank ties; claims recalibrated.", sub))

flow.append(Paragraph("What it is", h2))
flow.append(Paragraph(
    "An open spatial prior for CF4 (PFC-14) emissions, gridded by primary-aluminium smelter location, as a "
    "physically-grounded input for atmospheric inversions. It targets the gap that EDGAR and GAINS grid F-gas "
    "emissions by a population / built-up proxy, which misplaces a gas that is actually emitted at a finite, "
    "mappable set of smelters (anode-effect PFCs). The smelter registry also serves as a documented "
    "aluminium-location layer for attribution cross-checks — e.g. it documents that South Korea and Taiwan host "
    "no primary smelters: a citable source for an attribution step that otherwise rests on informal co-location.",
    body))

flow.append(Paragraph("Method (deliberately simple, fully reproducible)", h2))
flow.append(bullets([
    "<b>Registry:</b> operating (2020 status) primary-aluminium smelters with location + nameplate capacity, "
    "compiled from the public Wikipedia smelter list cross-checked against operator pages, with GEM wiki "
    "coordinates where available and USGS MCS production as the country-level anchor. 94 smelters; "
    "Europe-complete; China carries 12 cluster-anchor plants of ~120 (disclosed). A technology column is in "
    "the schema but unpopulated in this release.",
    "<b>Weighting, three variants:</b> capacity-weighted; presence-only (each smelter = 1, robustness); and "
    "<b>production-rescaled</b> (country totals matched to USGS 2020 national primary-aluminium production, "
    "distributed within country by capacity), the recommended variant for global use, since the raw registry "
    "under-weights China (27.5% of registry capacity vs 56.7% of 2020 world production).",
    "<b>Grid + scale convention:</b> rasterize to the target grid; the output is a <i>relative</i> spatial "
    "weight (units “1”, kt-equivalent magnitudes): renormalize to unit sum and rescale to your sectoral "
    "total before use; never read as absolute emissions. The fields are exactly zero outside smelter cells — "
    "do not use as a standalone total-CF4 prior (blend with a smooth background / floor).",
    "<b>Validation metric:</b> per-region spatial correlation against an observation-driven inversion "
    "<b>posterior</b> (flat-prior, so no candidate circularity), vs the EDGAR population/built-up baseline, "
    "with fixed-tile spatial block-bootstrap and toroidal-shift permutation significance tests; exact-year "
    "field selection asserted. Correlations are insensitive to the density-vs-mass basis choice (checked "
    "both ways; src/audit_basis.py).",
]))

flow.append(Paragraph("Validation: Europe (ICOS PARIS CF4 posterior, 2020, 6-member flat-prior ensemble)", h2))
data = [
    [Paragraph("<b>Region</b>", hcell), Paragraph("<b>smelter prior</b>", hcell),
     Paragraph("<b>EDGAR</b>", hcell), Paragraph("<b>status</b>", hcell)],
    [Paragraph("Iceland", cell), Paragraph("<b>0.25</b>", cell), Paragraph("~0", cell),
     Paragraph("significant (bootstrap + shift-null) in the two covering members — both RHIME, one inversion "
               "system; effectively a single-region, single-system result", cell)],
    [Paragraph("Pooled (smelter countries)", cell), Paragraph("<b>0.051</b>", cell), Paragraph("0.022", cell),
     Paragraph("direction favours the smelter prior in 5/6 members (3 systems × 2 transport models, not 6 "
               "independent results); no member individually significant", cell)],
    [Paragraph("Germany", cell), Paragraph("<b>0.06</b>", cell), Paragraph("0.015", cell),
     Paragraph("direction favours the smelter prior in 5/6 members; not significant", cell)],
    [Paragraph("Norway, Spain, UK", cell), Paragraph("~0", cell), Paragraph("0.01–0.09", cell),
     Paragraph("EDGAR ahead. Norway is the honest counterexample: remote smelters EDGAR zeroes, yet EDGAR "
               "wins the correlation; no mechanism demonstrated", cell)],
    [Paragraph("France", cell), Paragraph("—", cell), Paragraph("—", cell),
     Paragraph("reported symmetrically: the only individually significant French results favour EDGAR (both "
               "RHIME members, and one InTEM member at the larger tile size); the other InTEM member favours "
               "the smelter prior strongly (+0.37) but not significantly — system-dependent disagreement",
               cell)],
]
tbl = Table(data, colWidths=[3.9 * cm, 2.3 * cm, 1.8 * cm, 9.3 * cm])
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a5a")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f8")]),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]))
flow.append(Spacer(1, 2))
flow.append(tbl)
flow.append(Spacer(1, 3))
flow.append(Paragraph(
    "A second, distribution-free metric (common per-cell-mass basis, midrank ties): the observation-driven "
    "posterior places the 22 in-domain smelter cells at a mean <b>72nd percentile</b> of the pooled domain, "
    "EDGAR at the <b>59th</b> — and EDGAR assigns exactly zero CF4 to <b>15 of the 22</b>, including all three "
    "Icelandic smelter cells (its zeros rank at the midrank of the zero block). The inversion's own flat prior "
    "scores 77 on the same metric, so percentile values partly reflect field construction; the "
    "construction-independent posterior/prior ratio places the smelter cells at the <b>70th percentile</b>, "
    "Fjarðaál at the 99th. At the 1-degree grid of the distributed files the pooled correlations are 0.20 "
    "(smelter prior) vs 0.11 (EDGAR); Iceland 0.55 vs ~0.", body))
flow.append(Paragraph(
    "Honest reading: the prior is informative where observations resolve point sources, consistent in "
    "direction with the facility-located prior precedent of Kim et al. 2021 (one member of a regional prior "
    "ensemble). The win is <i>relative</i> and concentrated in well-constrained theatres; absolute fine-scale "
    "skill is low for all priors, and EDGAR's smooth field tracks the low-emission background ordering far "
    "better (midrank rank correlation: pooled 0.35 vs 0.03) — expected by construction for a point-source "
    "field.", body))

flow.append(Paragraph("The open question (why an OSSE would help)", h2))
flow.append(Paragraph(
    "~56% of global CF4 is China (2018–2023; Püschel et al. 2025), where the signal is largest, but no clean "
    "China-resolved gridded CF4 posterior is public, and the one global deposit uses an EDGAR-based prior, so "
    "it cannot cleanly adjudicate the smelter-vs-proxy question. A prior-sensitivity test / OSSE on recent "
    "years would settle whether the smelter prior improves the posterior where observations constrain it "
    "(China, the Gulf, Russia, India).", body))

flow.append(Paragraph("What we can provide", h2))
flow.append(bullets([
    "The gridded prior (NetCDF; 1-degree global files on the grid of the Püschel et al. deposited fields — "
    "their inversion runs a variable-resolution internal grid; the match is to the deposited product — or any "
    "grid/resolution you specify).",
    "The open smelter registry (CSV, per-row provenance) and the method code.",
    "All three variants (capacity, presence-only, production-rescaled). A technology-weighted variant is "
    "planned once a documented per-facility technology source is secured.",
]))

flow.append(Paragraph("Honest scope", h2))
flow.append(Paragraph(
    "A <i>relative</i> spatial prior (“where is CF4 likely concentrated”) rather than a per-asset "
    "emissions estimate; it covers the aluminium sector only (~60–80% of global CF4) and must be combined with "
    "a separate field for electronics/other sources rather than used as a total-CF4 prior. Within-China "
    "placement rests on 12 registered cluster anchors. The method has precedent rather than novelty: Kim et "
    "al. (2021) used hand-assembled smelter locations as the point-source member of a regional three-prior "
    "ensemble, with an explicit caution about inaccurate prior locations; the value here is an open, global, "
    "documented, maintained version of that input the community can reuse. License: open (CC-BY); cite or "
    "acknowledge as preferred.", body))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                        topMargin=1.3 * cm, bottomMargin=1.3 * cm,
                        title="Smelter-resolved CF4 spatial prior: a one-page method note",
                        author="Zach Dissington")
doc.build(flow)
print("WROTE", OUT)
