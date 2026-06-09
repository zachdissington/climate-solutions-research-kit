"""Render the CF4 smelter-prior method note to a one-page PDF (reportlab Platypus).
Faithful to outreach/2026-06-06-method-note.md (Rev 2, 2026-06-09 — recalibrated claims).
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
                    spaceBefore=6, spaceAfter=2, textColor=colors.HexColor("#1a3a5a"))
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=8.4, leading=10.8, spaceAfter=3)
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
    "Open, non-commercial research note for the F-gas atmospheric-inversion and inventory community. "
    "Rev 2 (June 2026): validation claims recalibrated after a spatial-significance re-test; "
    "production-rescaled global variant added.", sub))

flow.append(Paragraph("What it is", h2))
flow.append(Paragraph(
    "An open spatial prior for CF4 (PFC-14) emissions, gridded by primary-aluminium smelter location, as a "
    "physically-grounded input for atmospheric inversions. It targets the gap that EDGAR and GAINS grid F-gas "
    "emissions by a population / built-up proxy, which misplaces a gas that is actually emitted at a finite, "
    "mappable set of smelters (anode-effect PFCs). The smelter registry also serves as a documented "
    "aluminium-location layer for attribution cross-checks (e.g. it carries no primary smelters in South Korea "
    "or Taiwan, where ratio-based sectoral attribution is known to struggle).", body))

flow.append(Paragraph("Method (deliberately simple, fully reproducible)", h2))
flow.append(bullets([
    "<b>Registry:</b> operating (2020 status) primary-aluminium smelters with location + nameplate capacity, "
    "from public sources (GEM gem.wiki, IAI, USGS MCS, Wikipedia “List of aluminium smelters”). 94 smelters; "
    "Europe-complete; China carries its 12 major clusters out of ~120 plants (disclosed).",
    "<b>Weighting, three variants:</b> capacity-weighted; presence-only (each smelter = 1, robustness); and "
    "<b>production-rescaled</b> (country totals matched to USGS 2020 national primary-aluminium production, "
    "distributed within country by capacity) — the recommended variant for global use, since the raw registry "
    "under-weights China (~28% of weight vs ~57% of world production).",
    "<b>Grid + normalize:</b> rasterize to the target grid; the output is a <i>relative</i> (normalized) "
    "spatial weight, to be rescaled to the inversion’s total flux before use — it must never be read as "
    "absolute emissions.",
    "<b>Validation metric:</b> per-region spatial correlation against an observation-driven inversion "
    "<b>posterior</b> (flat-prior, so no circularity), vs the EDGAR population/built-up baseline, with "
    "block-bootstrap and spatial-permutation significance tests.",
]))

flow.append(Paragraph("Validation: Europe (ICOS PARIS CF4 posterior, 2020, 6-member flat-prior ensemble)", h2))
data = [
    [Paragraph("<b>Region</b>", hcell), Paragraph("<b>smelter prior</b>", hcell),
     Paragraph("<b>EDGAR</b>", hcell), Paragraph("<b>status</b>", hcell)],
    [Paragraph("Iceland", cell), Paragraph("<b>0.25</b>", cell), Paragraph("~0", cell),
     Paragraph("significant (bootstrap + shift-null); RHIME members only", cell)],
    [Paragraph("Pooled (smelter countries)", cell), Paragraph("<b>0.057</b>", cell), Paragraph("0.015", cell),
     Paragraph("direction consistent in 6/6 members; not significant per member vs spatial autocorrelation", cell)],
    [Paragraph("Germany", cell), Paragraph("<b>0.05</b>", cell), Paragraph("0.005", cell),
     Paragraph("consistent direction 6/6; not significant", cell)],
    [Paragraph("Norway, Spain, UK", cell), Paragraph("~0", cell), Paragraph("0.03–0.09", cell),
     Paragraph("EDGAR ahead (weakly-constrained domains)", cell)],
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
    "A second, assumption-light metric: the observation-driven posterior places the 22 in-domain smelter cells "
    "at a mean <b>60th percentile</b> of the pooled domain, while EDGAR places them at the <b>26th</b> (zero CF4 "
    "at 14 of the 22 smelter cells). At the 1-degree grid of the distributed files the pooled correlations are "
    "0.14 (smelter prior) vs 0.07 (EDGAR); Iceland 0.55 vs ~0.", body))
flow.append(Paragraph(
    "Honest reading: the prior is informative where observations resolve point sources, and the direction is "
    "consistent with Kim et al. 2021 (East-Asia smelter-prior inversion). The win is <i>relative</i> and "
    "concentrated in well-constrained theatres; absolute fine-scale skill is low for all priors, and EDGAR’s "
    "smooth field still tracks the low-emission background better (rank correlation). France is system-dependent "
    "(wins in InTEM/ELRIS members, loses in RHIME) and is not claimed.", body))

flow.append(Paragraph("The open question (why an OSSE would help)", h2))
flow.append(Paragraph(
    "~56% of global CF4 is China, where the signal is largest, but no clean China-resolved gridded CF4 posterior "
    "is public, and the one global deposit (Püschel et al. 2025) uses an EDGAR-based prior, so it cannot cleanly "
    "adjudicate the smelter-vs-proxy question. A prior-sensitivity test / OSSE in FLEXINVERT+ on recent years "
    "would settle whether the smelter prior improves the posterior where observations constrain it (China, the "
    "Gulf, Russia, India).", body))

flow.append(Paragraph("What we can provide", h2))
flow.append(bullets([
    "The gridded prior (NetCDF; 1-degree global drop-in files matching the Püschel deposited grid, or any "
    "grid/resolution you specify).",
    "The open smelter registry (CSV, per-row provenance) and the method code.",
    "All three variants (capacity, presence-only, production-rescaled) and, if useful, a Tier-2 "
    "technology-weighted variant.",
]))

flow.append(Paragraph("Honest scope", h2))
flow.append(Paragraph(
    "A <i>relative</i> spatial prior (“where is CF4 likely concentrated”) rather than a per-asset emissions "
    "estimate; it covers the aluminium sector only (~60–80% of global CF4) and should be combined with a separate "
    "field for electronics/other sources rather than used as a total-CF4 prior. Within-China placement rests on "
    "12 registered major clusters. The method is not novel (Kim et al. 2021 demonstrated it regionally); the "
    "value is an open, global, maintained prior + registry the community can reuse. License: open (CC-BY); cite "
    "or acknowledge as preferred.", body))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                        topMargin=1.3 * cm, bottomMargin=1.3 * cm,
                        title="Smelter-resolved CF4 spatial prior: a one-page method note",
                        author="Zach Dissington")
doc.build(flow)
print("WROTE", OUT)
